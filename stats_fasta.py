#!/usr/bin/python

#usage
#python fasta.stats.py <filein>

import sys

counter=0
total_len=0

filein=open(sys.argv[1],'r')
for line in filein:
#   print line
   if line.startswith('>'):
      counter=counter+1
      continue
   else:
      length=int(len(line))
      total_len=total_len+length
average_len=total_len/float(counter)

print 'Reads found: %s' %counter
print 'Total bases: %s' % total_len
print 'Average read length: %s' %average_len

