"""本地 MySQL 独立隔离库验证；不读取/修改业务库，不输出临时凭据。"""
import importlib.util
import json
import secrets
import subprocess
from pathlib import Path

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.exc import DBAPIError

ROOT = Path('/home/wang/work/rosbag-catalog')
CONTAINER = 'rosbag-catalog-local-mysql-1'
SCHEMA = 'r2_review_20261010_' + secrets.token_hex(4)
USER = 'r2rev_' + secrets.token_hex(4)
PASSWORD = secrets.token_hex(24)
cli = ['docker', 'exec', '-i', CONTAINER, 'sh', '-c', 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N']


def sql(statement):
    return subprocess.run(cli, input=statement, text=True, capture_output=True)


try:
    setup = sql(f"CREATE DATABASE {SCHEMA}; CREATE USER '{USER}'@'%' IDENTIFIED BY '{PASSWORD}'; GRANT ALL ON {SCHEMA}.* TO '{USER}'@'%';")
    print('setup_rc=', setup.returncode)
    if setup.returncode:
        raise RuntimeError('隔离库准备失败；不输出包含临时凭据的 SQL')
    net = json.loads(subprocess.check_output(['docker', 'inspect', '--format', '{{json .NetworkSettings.Networks}}', CONTAINER]))
    host = net['rosbag-catalog-local_default']['IPAddress']
    engine = sa.create_engine(sa.URL.create('mysql+pymysql', username=USER, password=PASSWORD, host=host, database=SCHEMA))
    with engine.begin() as connection:
        print('version/sql_mode=', connection.execute(sa.text('SELECT @@version, @@sql_mode')).one())
        projection = connection.execute(sa.text('SELECT "source_id", "source_generation", "event_id" FROM (SELECT "actual-bag" AS source_id, 1 AS source_generation, "actual-event" AS event_id) e')).one()
        print('quoted_projection=', projection)
        assert tuple(projection) == ('source_id', 'source_generation', 'event_id')
        connection.execute(sa.text('CREATE TABLE scene_analysis_version (id BIGINT PRIMARY KEY, parent_bag_uid VARCHAR(26), scene_code VARCHAR(32), current BOOLEAN)'))
        connection.execute(sa.text("INSERT INTO scene_analysis_version VALUES(1, 'p', 'slope', 0)"))
        from app.models import SceneAnalysisVersion as V
        other = sa.select(V.id).where(V.parent_bag_uid == 'p', V.scene_code == 'slope', V.current.is_(True), V.id != 1).exists()
        stmt = sa.update(V).where(V.id == 1, ~other).values(current=True)
        print('actual_SQLAlchemy_update=', stmt.compile(dialect=engine.dialect))
        try:
            connection.execute(stmt)
            raise AssertionError('预期 MySQL 1093 未出现')
        except DBAPIError as exc:
            print('switch_current_errno=', exc.orig.args[0], 'message=', exc.orig.args[1])
            assert exc.orig.args[0] == 1093
    from app.models import PurposeScheduleEvent
    from app.services.scene_schedule_consumer import poll_outbox_events, consume_purpose_events
    from sqlalchemy.orm import Session
    PurposeScheduleEvent.__table__.create(engine)
    with Session(engine) as db:
        db.add(PurposeScheduleEvent(event_id='actual-event', submission_id='actual-sub',
                                  source_id='actual-bag', parent_bag_uid='actual-bag',
                                  purpose='self_built', profile_id='profile', profile_version=1))
        db.commit()
        projected = poll_outbox_events(db)
        print('actual_poll=', projected)
        stats = consume_purpose_events(db, projected)
        print('actual_consumer_stats=', stats)
        status = db.execute(sa.text("SELECT status FROM purpose_schedule_event WHERE event_id='actual-event'")).scalar()
        print('actual_outbox_status_after_consume=', status)
        assert stats['dropped'] == 1 and status == 'PENDING'
    migration_file = ROOT / 'alembic/versions/20261008_02_ingest_config.py'
    spec = importlib.util.spec_from_file_location('actual_ingest_migration', migration_file)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    @sa.event.listens_for(engine, 'before_cursor_execute')
    def capture(conn, cursor, statement, params, context, many):
        if statement.lstrip().startswith('CREATE TABLE ingest_profile'):
            print('actual_alembic_DDL=', statement)

    with engine.begin() as connection:
        assert 'ingest_profile' not in sa.inspect(connection).get_table_names()
        try:
            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()
            raise AssertionError('预期真实 incremental migration 1101 未出现')
        except DBAPIError as exc:
            print('incremental_migration_errno=', exc.orig.args[0], 'message=', exc.orig.args[1])
            assert exc.orig.args[0] == 1101
    engine.dispose()
finally:
    cleanup = sql(f"DROP DATABASE IF EXISTS {SCHEMA}; DROP USER IF EXISTS '{USER}'@'%';")
    print('cleanup_rc=', cleanup.returncode)
    assert cleanup.returncode == 0
