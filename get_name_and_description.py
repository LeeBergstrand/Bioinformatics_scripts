import sys

filein=open(sys.argv[1])
fp=open(sys.argv[2], 'w')
for line in filein:
    if line.startswith('>'):
        line=line.split(" ",1)
        name=line[0]
        desc=line[1]
        fp.write('%s\t%s' %(name,desc))
    else:
        continue
fp.close()
