import sys
cp = open(sys.argv[1], encoding='utf-8').read()
for p in sys.argv[2:]:
    d = open(p, encoding='utf-8').read()
    open(p, 'w', encoding='utf-8').write(cp + d)
