#!/usr/bin/python
# File created on 13 Feb 2014.
from __future__ import division

__author__ = "Erick Cardenas Poire"
__copyright__ = "Copyright 2014"
__credits__ = [""]
__version__ = "1.0"
__maintainer__ = "Erick Cardenas Poire"
__status__ = "Release"

#import glob
#import fileinput

from Bio import SeqIO
import sys
import os
import re 
import inspect
from commands import getstatusoutput
from optparse import OptionParser
import shutil 


#config = load_config()
script_info={}
script_info['brief_description'] = """Filters sequence according to a minimum size parameter"""
script_info['script_description'] = """HMMER parser. Runs hmmscan, filters results and extract hits
	     REQUIRED: Model, input proteins
	     REQUIRED Modules: Biopython
	     OPTIONAL: Contigs"""

script_info['script_usage'] = []

usage = '''
Usage:  
./dbCAN_HMM_Genomes.py -c <directory_containing_dbCAN_files> [required] -e <specify_file_extension> [required] -f <input_format> [optional] -d <directory_containing_fasta_input> [optional]

Example:
./dbCAN_HMM_Genomes.py -c ~/CAZy/ -e .gbk -d ~/Genomes/Assembled/Fasta/ -f genbank

DEPENDENCIES: 	
		ii) dbCAN files: dbCAN-fam-HMMs.txt, hmmscan-parser.sh & all.hmm.ps.len. (Note: one must have run \"hmmpress dbCAN-fam-HMMs.txt\" to format db in advance of this script)
		iii) HMMR v.3.0 - Must be in PATH

'''

parser = OptionParser(usage)
parser.add_option("-m", "--model", dest="input_model",
                  help='The input HMM database (prepared with hmmpress) [REQUIRED]')
parser.add_option("-i", "--input_proteins", dest="input_fp",
                  help='The input protein file [REQUIRED]')
parser.add_option("-o", "--output_dir", dest="output_dir",
                  help='The output directory [REQUIRED]')
parser.add_option("-L", "--models_length", dest="model_len",default='none',
                  help='Lengths of HMM models in HMM database [OPTIONAL]')
parser.add_option("-e", "--evalue", dest="evalue_threshold",default=10,
                  help='Maximum evalue threshold  [OPTIONAL]')
parser.add_option("-a", "--assembly", dest="assembly_file",default='none',
                  help='Assembly files, source of proteins [OPTIONAL, default: none]')
parser.add_option("-c", "--converage", dest="hmm_coverage",default=0,
                  help='Minimum HMM coverage (%) [OPTIONAL, default: 0]')
parser.add_option('-x','--extract_mode', dest="extract_mode", default='none',
                   choices=['none', 'proteins', 'contigs','all'], 
                   help='\n(a) \'none\' -- Do not extract anything (Default)\n'+
                        '\n(b) \'proteins\' -- Extract hits\n' +
                        '\n(c) \'contigs\' -- Extract contigs that contains hits, requires assebly file using -a\n' +
                        '\n(d) \'all\' -- Extract hits, contigs, and all proteins from hits\n')


def update_progress(progress):
    barLength = 30 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done.....\r\n"
    block = int(round(barLength*progress))
    text = "\r   Percent: [{0}] {1}% {2}".format( "="*block + " "*(barLength-block), progress*100, status)
    sys.stderr.write(text)
    sys.stderr.flush()

#Get HMM length function
def get_hmm_len(input_model):
   hmmshortname = re.sub('[.](hmm)','',input_model, re.I)  #removes extension, case insensitive search
   hmm_leng_file=hmmshortname+".length.txt"
   hmm_fileout=open(hmm_leng_file,'w')
   hmm_filein=open(input_model,'r')
   for line in hmm_filein:
      if line.startswith('NAME'):
         line=line.strip('\n')
         line=line.split(' ')
         name=line[2]
         hmm_fileout.write('%s\t' %name)
      else:
         if line.startswith('LENG'):
            line=line.strip('\n')
            line=line.split(' ')
            len=line[2]
            hmm_fileout.write('%s\n' %len)
         else:
            continue
   hmm_fileout.close()
   hmm_filein.close()
   os.system(' '.join(['cp',hmm_leng_file,'all.hmm.ps.len']))


#Function to run hmmscan and parse
def run_hmm_scan (model,query,output):
   hmmshortname = re.sub('[.](hmm)','',model, re.I)  #removes extension, case insensitive search
   shortname=re.sub('[.](fasta$|fas$|faa$|fsa$|fa$)','',query, re.I)  #finds file format removes extension, case insensitive search
   output_file=output+"/"+shortname+"_"+hmmshortname+'.hmm.out'
   output_file2=output+"/"+shortname+"_"+hmmshortname+'.txt'
   print 'Running hmmscan...'
   os.system(' '.join(['hmmscan',model,query,">",output_file]))
   print 'Parsing results...'
   os.system(' '.join(['sh','hmmscan-parser.sh',output_file,'>',output_file2]))

#Filtering by evalue and coverage
def filtering_by_evalue_and_coverage(model,query,output,evalue,coverage):
   hmmshortname = re.sub('[.](hmm)','',model, re.I)  #removes extension, case insensitive search
   shortname=re.sub('[.](fasta$|fas$|faa$|fsa$|fa$)','',query, re.I)  #finds file format removes extension, case insensitive search
   output_file2=output+"/"+shortname+"_"+hmmshortname+'.txt'
   hmm_table=open(output_file2,'r')
   output_file3=output+"/"+shortname+"_"+hmmshortname+'.filtered.txt'
   hmm_filtered_table=open(output_file3,'w')
   print 'Filtering results with coverage >= %s percentage and evalue <= %s ...' %(coverage,evalue)
   for line in hmm_table:
      line2=line.strip('\n').split('\t')
      result_evalue=float(line2[2])
      result_model_coverage=float(line2[7])
      if (result_evalue<=evalue) and (result_model_coverage*100>=coverage):
         hmm_filtered_table.write('%s' %line)
      else:
         continue
   hmm_table.close()
   hmm_filtered_table.close()

#Function to extract hits from filtered results
def extract_protein_hits(query,model,output):
   hmmshortname = re.sub('[.](hmm)','',model, re.I)  #removes extension, case insensitive search
   shortname=re.sub('[.](fasta$|fas$|faa$|fsa$|fa$)','',query, re.I)  #finds file format removes extension, case insensitive search
   input_file4=output+"/"+shortname+"_"+hmmshortname+'.filtered.txt'
   hmm_filtered_table2=open(input_file4,'r')
  

   print '   Extracting proteins for file=%s and HMM database=%s' %(query,model)
   #Create dictionary with protein:[list of model it hits]
   protein_hit_dictionary={}
   all_models_hits=[]
   for line3 in hmm_filtered_table2:
      line4=line3.strip('\n').split('\t')
      protein_hit=line4[0]
      model_of_protein_hit=line4[1].rstrip(' ')
 
      #update list of proteins
      all_models_hits.append(model_of_protein_hit)

      #Get list of proteins hits, if non existent create empty list
      models=protein_hit_dictionary.get(protein_hit,[])
      #Append current model hit to list
      models.append(model_of_protein_hit)   
      #Update dictionary entry   
      protein_hit_dictionary[protein_hit]=models

   #Print message
   count_of_models=list(set(all_models_hits))
   count_of_proteins=len(protein_hit_dictionary.keys())

   print '   Extracting %s unique proteins corresponding to %s HMM models' %(count_of_proteins,len(count_of_models))      

   #open one output file per model
   #Generate list of output files 
   #for item in all_models_hits:
   files=[open(output+'/'+shortname+'_'+hmmshortname+'_'+item+'.fasta','w') for item in set(all_models_hits)]

   #Open original file, find if name is in hit list, then get models hits and write to model result files
   filein=open(query,'r')
   for record in SeqIO.parse(filein,"fasta"):
      name=record.name
      if name in protein_hit_dictionary.keys():
         what_models_list=protein_hit_dictionary.get(name)
         #Iterate this list
         for what_model in what_models_list:
            #Find index
            index=count_of_models.index(what_model)
            files[index].write('>%s\n%s\n' % (name, record.seq))
    
   #Close files
   for f in files:
      f.close()

#Function to extract contigs
def extract_contigs(query,model,output,assembly_file):
   hmmshortname = re.sub('[.](hmm)','',model, re.I)  #removes extension, case insensitive search
   shortname=re.sub('[.](fasta$|fas$|faa$|fsa$|fa$)','',query, re.I)  #finds file format removes extension, case insensitive search
   input_file4=output+"/"+shortname+"_"+hmmshortname+'.filtered.txt'
   hmm_filtered_table2=open(input_file4,'r')
  
   print '   Extracting contigs for file=%s and HMM database=%s' %(query,model)
   #Create dictionary with protein:[list of model it hits]
   protein_model_dictionary={}
   for line3 in hmm_filtered_table2:
      line4=line3.strip('\n').split('\t')
      protein_hit=line4[0]
      model_of_protein_hit=line4[1].rstrip(' ')
      #Get list of proteins hits, if non existent create empty list
      models=protein_model_dictionary.get(protein_hit,[])
      #Append current model hit to list
      models.append(model_of_protein_hit)   
      #Update dictionary entry   
      protein_model_dictionary[protein_hit]=models

   #Create protein-contig dictionary
   contigs_list=[]
   for protein in protein_model_dictionary.keys(): #parse through list and add to contigs_list
      contig=protein.rsplit('_',1)
      contigs_list.append(contig[0])
   contigs_list=list(set(contigs_list))

   #Open original file, find if name is in hit list, then get models hits and write to model result files
   assembly_in=open(assembly_file,'r')
   contigs_file=output+"/"+shortname+"_"+hmmshortname+'_contigs.fasta'
   contigs_out=open(contigs_file,'w')
   print '   Looking for %s contigs' %len(contigs_list)
   progress_counter=0
   for record in SeqIO.parse(assembly_in,"fasta"):
      name=record.name
      if name in contigs_list:
         progress_counter=progress_counter+1
         contigs_out.write('>%s\n%s\n' % (name, record.seq))
      else:
         continue
      update_progress(progress_counter/float(len(contigs_list)))
   contigs_out.close()
   if progress_counter != len(contigs_list):
      print 'Some contigs were not found'
#End of Extract contigs function
   

#Function to extract all proteins from contig
def extract_all_proteins_from_contigs(query,model,output):
   hmmshortname = re.sub('[.](hmm)','',model, re.I)  #removes extension, case insensitive search
   shortname=re.sub('[.](fasta$|fas$|faa$|fsa$|fa$)','',query, re.I)  #finds file format removes extension, case insensitive search
   input_file4=output+"/"+shortname+"_"+hmmshortname+'.filtered.txt'
   hmm_filtered_table2=open(input_file4,'r')
  
   print '   Extracting all proteins from hit contigs of file=%s and HMM database=%s' %(query,model)
   #Create dictionary with protein:[list of model it hits]
   protein_list=[]
   for line3 in hmm_filtered_table2:
      line4=line3.strip('\n').split('\t')
      protein_hit=line4[0]
      protein_list.append(protein_hit)   

   #Create protein-contig dictionary
   contigs_list=[]
   for protein in protein_list: #parse through list and add to contigs_list
      contig=protein.rsplit('_',1)
      contigs_list.append(contig[0])
   contigs_list=list(set(contigs_list))

   print '   Looking for %s contigs' %len(contigs_list)

   #open one output file per model
   #Generate list of output files 
   files=[open(output+'/'+shortname+'_'+hmmshortname+'_'+contigs+'.fasta','w') for contigs in (contigs_list)]

   #Open original file, find if name is in hit list, then get models hits and write to model result files
   filein=open(query,'r')
   for record in SeqIO.parse(filein,"fasta"):
      name=record.name
      the_contig0=name.rsplit('_',1)
      the_contig=the_contig0[0]
      if the_contig in contigs_list:
         index=contigs_list.index(the_contig)
         files[index].write('>%s\n%s\n' % (name, record.seq))
      else:
         continue

   #Close files
   for f in files:
      f.close()
#End of Extract all proteins from contigs function
   

def main(argv):
   (opts, args) = parser.parse_args()
   print ''
   print 'Initializing...'
   # initialize the input directory or file
   input_model = opts.input_model 
   input_fp = opts.input_fp 
   output_dir = opts.output_dir 
   assembly_file = opts.assembly_file 
   model_len = opts.model_len 
   evalue_threshold=float(opts.evalue_threshold)
   hmm_coverage=float(opts.hmm_coverage)
   extract_mode = opts.extract_mode.strip()

   #check if model length exists, otherwise it creates a model length dictionary
   print 'Checking model length...'
   if model_len == 'none':
      print '   HMM length not found'
      hmmshortname = re.sub('[.](hmm)','',input_model, re.I)  #removes extension, case insensitive search
      hmm_leng_file=hmmshortname+".length.txt"
      print '   Created %s file' % hmm_leng_file
      get_hmm_len(input_model)
   else:
      print '   Model length found in :%s' %model_len 

   #Running hmm scan 
   run_hmm_scan(input_model,input_fp,output_dir)

   #Filter results with model coverage and evalue
   filtering_by_evalue_and_coverage(input_model,input_fp,output_dir,evalue_threshold,hmm_coverage)

   print 'Checking extract mode...'
   print '   Extract mode set to %s' %extract_mode

   #Checking extraction mode
   if extract_mode=='none':
      print '   No extraction performed...'
   elif extract_mode=='proteins':
      extract_protein_hits(input_fp,input_model,output_dir)
   elif extract_mode=='contigs':
      extract_contigs(input_fp,input_model,output_dir,assembly_file)
      
   elif extract_mode=='all':
      extract_protein_hits(input_fp,input_model,output_dir)
      extract_contigs(input_fp,input_model,output_dir,assembly_file)
      extract_all_proteins_from_contigs(input_fp,input_model,output_dir)
   print 'All tasks completed'
   print 'Keep calm and carry on'
   #cleanup



# the main function of metapaths
if __name__ == "__main__":
    main(sys.argv[1:])    

