#!/usr/bin/python
# File created on 31 Jan 2014.

__author__ = "Erick Cardenas Poire"
__copyright__ = "Copyright 2014"
__credits__ = [""]
__version__ = "1.0"
__maintainer__ = "Erick Cardenas Poire"
__status__ = "Release"

from Bio import SeqIO
import sys
from os import makedirs, sys, listdir, environ, path
import re 
import inspect
from commands import getstatusoutput
from optparse import OptionParser
import shutil 

#config = load_config()
script_info = {}
script_info['brief_description'] = """Adds coverage information from one file and modifies fasta header"""
script_info['script_description'] = """Adds coverage information from one file and modifies fasta header
             REQUIRED: You must have a fasta and coverage file with same base name"""
script_info['script_usage'] = []

usage= """
Need to run it like this:
./add.coverage.to.fasta.py  -i input_file
For more options:  ./add.coverage.to.fasta.py -h"""

parser = OptionParser(usage)
parser.add_option("-i", "--input_file", dest = "input_fp",
                  help = 'the input fasta file/input dir [REQUIRED]')


#creates an input output pair if input is just an input file
def create_an_inputs_and_output(input_file):
   input_output = []
   shortname = re.sub('[.](fasta$|fas$|fna$|faa$|fsa$|fa$)','',input_file, re.I)  #finds file format removes extension, case insensitive search
   coverage_input_file = shortname+".cov"
   output_file = shortname + ".new.fasta"
   input_output.append(input_file)
   input_output.append(coverage_input_file)
   input_output.append(output_file)
   return input_output

# checks if the supplied arguments are adequate
def valid_arguments(opts, args):
   if opts.input_fp == None:
      return True
   else:
      return False

def main(argv):
   (opts, args) = parser.parse_args()
   if valid_arguments(opts, args):
      print usage
      sys.exit(0)

   # initialize the input directory or file
   input_fp = opts.input_fp 
   list_of_files = create_an_inputs_and_output(input_fp)
 
   # Creates coverage dictionary
   coverage_dictionary = {}
   coverage_file_in = open(list_of_files[1],'r')
   for line in coverage_file_in:
      line = line.split('\t')
      seq_ID = line[0]
      seq_coverage = line[1]
      coverage_dictionary[seq_ID] = seq_coverage
   coverage_file_in.close()   

   fileout = open(list_of_files[2], 'w')
   for seq_record in SeqIO.parse(list_of_files[0], format = "fasta"):
      seq_name = seq_record.id
      coverage = coverage_dictionary.get(seq_name,0)
      description = "coverage=" + coverage
      fileout.write('>%s %s\n%s\n' %(seq_record.id, description, seq_record.seq))
   fileout.close()

# the main function 
main(sys.argv[1:])    