# Repairing CAZY database
# Problem : all proteins from CAZy.GH.GT.CE.PL.AA-2013-05-10 , clas AA 
# have same CAZY family annotation
# Therefore the scoring dictionary is wrong and need to be updated using
# a more recente dictionary
# list of not found exported to not.found.txt
# 91 entries, 86 are Not classiffied AA0
# The rest I will assume as NC
# AFZ53998.1
# AFS83208.1
# CCO11889.1
# AFV76103.1






#usage python correct_cazy_dictionary.py <bad.dict> <helping.dict> <out.file.base>
#        	0		1		2		3	4


import pickle
import sys

file_bad_dictionary = open(sys.argv[1], 'rb')
file_helping_dictionary = open(sys.argv[2], 'r')
file_good_dictionary = open(sys.argv[3], 'w')

bad_dictionary = pickle.load(file_bad_dictionary)
helping_dictionary = pickle.load(file_helping_dictionary)
good_dictionary={}

print len(bad_dictionary.keys())

AA_NC = ['AFZ53998.1','AFS83208.1','CCO11889.1','AFV76103.1']

counterAA = 0
counterAA0 = 0
counterAA_NN = 0
for key in bad_dictionary.keys():
    # Get dictionary entry
    dict_entry = bad_dictionary.get(key,0)
    # Test if we are modifying AA
    if dict_entry[2] == 'AA':
        counterAA = counterAA + 1
        print 'Found  AA enzyme'
        whole_name = dict_entry[0]
        cazy_class = dict_entry[2]
        cazy_organism = dict_entry[3]
        # Get good value from helping dictionary
        helping_entry = helping_dictionary.get(key)
        if helping_entry == None:
            print ' No AA class found'
            split_key = key.split('|')
            if split_key[3] in AA_NC:
                print ' CAZy family set to AA_NN'
                cazy_family = 'AA_NN'
                counterAA_NN = counterAA_NN + 1
#                print cazy_family
                new_dict_entry = [whole_name, cazy_family, cazy_class, cazy_organism]
                good_dictionary[key] = new_dict_entry
#                print new_dict_entry
            else:
                print '  CAZy family set to AA0'
                cazy_family = 'AA0'
                counterAA0 = counterAA0 + 1
#                print cazy_family
                new_dict_entry = [whole_name, cazy_family, cazy_class, cazy_organism]
                good_dictionary[key] = new_dict_entry
#                print new_dict_entry
        else:
            cazy_family = helping_entry[1]
            print ' CAZy family set to %s' %cazy_family
            new_dict_entry = [whole_name, cazy_family, cazy_class, cazy_organism]
            good_dictionary[key] = new_dict_entry
#            print new_dict_entry
#        print new_dict_entry
#        bad_dictionary[key] = new_dict_entry
        print len(new_dict_entry)       
    else:
        print 'Not an AA family'
        good_dictionary[key] = dict_entry
        print len(dict_entry)
#print counterAA
print counterAA0
print counterAA_NN
print len(good_dictionary.keys())

#print bad_dictionary
pickle.dump(good_dictionary,file_good_dictionary)


file_bad_dictionary.close()
file_helping_dictionary.close()
file_good_dictionary.close()




