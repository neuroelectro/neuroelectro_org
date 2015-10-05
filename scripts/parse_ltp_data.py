"""
Collect the curated LTP annotations from the specified directory (recursively) and 
write the control data values with the corresponding standard errors and 
number of trials to a csv file.

Created by: Dmitry Tebaykin
"""
import neuroelectro.models as m
from db_functions.author_search import get_article_last_author
import os, errno, re, numpy as np
import csv
from neuroelectro_org.article_text_mining.assign_metadata import get_num

# List of existing curators (input and output file paths)
# TODO: collect metadata for the articles once, not once per curator
curators = [
#             ("/Users/dtebaykin/Documents/Curated brat files/LTP_All_Kris", "/Users/dtebaykin/Documents/Neuroelectro documents/Spreadsheets/ltp_controls_kris.csv"),
            ("/Users/dtebaykin/Documents/Curated brat files/LTP_All_Brenna", "/Users/dtebaykin/Documents/Neuroelectro documents/Spreadsheets/ltp_controls_brenna.csv")
#             ("/Users/dtebaykin/Documents/Curated brat files/LTP_All_Thanos", "/Users/dtebaykin/Documents/Neuroelectro documents/Spreadsheets/ltp_controls_thanos.csv"),
#             ("/Users/dtebaykin/Documents/Curated brat files/LTP_All_Ryan", "/Users/dtebaykin/Documents/Neuroelectro documents/Spreadsheets/ltp_controls_ryan.csv")
            ]

# Header and metadata setup
nom_vars = ['Species', 'Strain', 'ElectrodeType', 'PrepType', 'JxnPotential']
cont_vars  = ['JxnOffset', 'RecTemp', 'AnimalAge', 'AnimalWeight', 'FlagSoln']
cont_var_headers = ['JxnOffset', 'Temp', 'Age', 'Weight', 'FlagSoln']
for i in range(0, 5):
    cont_vars.extend(['external_%s_Mg' % i, 'external_%s_Ca' % i, 'external_%s_Na' % i, 'external_%s_Cl' % i, 'external_%s_K' % i, 'external_%s_pH' % i, 'internal_%s_Mg' % i, 'internal_%s_Ca' % i, 'internal_%s_Na' % i, 'internal_%s_Cl' % i, 'internal_%s_K' % i, 'internal_%s_pH' % i])
    cont_var_headers.extend(['External_%s_Mg' % i, 'External_%s_Ca' % i, 'External_%s_Na' % i, 'External_%s_Cl' % i, 'External_%s_K' % i, 'External_%s_pH' % i, 'Internal_%s_Mg' % i, 'Internal_%s_Ca' % i, 'Internal_%s_Na' % i, 'Internal_%s_Cl' % i, 'Internal_%s_K' % i, 'Internal_%s_pH' % i])
num_nom_vars = len(nom_vars)

other_headers = ['ExtractedLTPValue', 'AdjustedLTPValue', 'Confidence', 'StandardError', 'NumOfTrials', 'PubmedLink', 'Title', 'Journal', 'PubYear', 'ArticleDataLink', 'LastAuthor']
all_headers = other_headers
all_headers.extend(nom_vars + cont_var_headers)

pubmed_base_link_str = 'http://www.ncbi.nlm.nih.gov/pubmed/%d/'
table_base_link_str = 'http://neuroelectro.org/data_table/%d/'
article_base_link_str = 'http://neuroelectro.org/article/%d/'

# Delete the specified file, maintenance since the parsing process involves appending to an already existing output file
def fileRemove(path):
    if os.path.exists(path) and os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

# Get all the existing metadata on the article from NeuroElectro database
def collectMeta(a):
    amdms = m.ArticleMetaDataMap.objects.filter(article = a)
    curr_metadata_list = ['']*(len(nom_vars) + len(cont_vars))
    
    # Process metadata for nominal vars
    for i,v in enumerate(nom_vars):
        valid_vars = amdms.filter(metadata__name = v)
        temp_metadata_list = [vv.metadata.value for vv in valid_vars]
        if 'in vitro' in temp_metadata_list and 'cell culture' in temp_metadata_list:
            curr_metadata_list[i] = 'cell culture'
        elif v == 'Strain' and amdms.filter(metadata__value = 'Mice').count() > 0:
            temp_metadata_list = 'C57BL'
            curr_metadata_list[i] = 'C57BL'
        elif v == 'Strain' and amdms.filter(metadata__value = 'Guinea Pigs').count() > 0:
            temp_metadata_list = 'Guinea Pigs'
            curr_metadata_list[i] = 'Guinea Pigs'
        elif len(temp_metadata_list) == 0 and v == 'Strain':
            if amdms.filter(metadata__value = 'Rats').count() > 0:
                if np.random.randn(1)[0] > 0:
                    curr_metadata_list[i] = 'Sprague-Dawley'
                else:
                    curr_metadata_list[i] = 'Wistar'
        elif len(temp_metadata_list) > 1: 
            temp_metadata_list = temp_metadata_list[0]
            curr_metadata_list[i] = temp_metadata_list
        else:
            curr_metadata_list[i] = u'; '.join(temp_metadata_list)
            
    # Process metadata for continuous vars
    for i,v in enumerate(cont_vars):
        valid_vars = amdms.filter(metadata__name = v)
        if valid_vars.count() > 0:
            cont_value_ob = valid_vars[0].metadata.cont_value.mean
            curr_metadata_list[i+num_nom_vars] = cont_value_ob
        else:
            # check if 
            if v == 'RecTemp' and amdms.filter(metadata__value = 'in vivo').count() > 0:
                curr_metadata_list[i+num_nom_vars] = 37.0
       
    pubmed_link_str = pubmed_base_link_str % a.pmid
    article_link_str = article_base_link_str % a.pk
    
    last_author = get_article_last_author(a)
    if last_author is not None:
        last_author_name = '%s %s' % (last_author.last, last_author.initials)
        last_author_name = last_author_name.encode("utf8", "replace")
    else:
        last_author_name = ''
            
    curr_meta_list = []
    
    curr_meta_list.append(pubmed_link_str)
    curr_meta_list.append((a.title).encode("utf8", "replace"))
    curr_meta_list.append(a.journal)
    curr_meta_list.append(a.pub_year)
    curr_meta_list.append(article_link_str)
    curr_meta_list.append(last_author_name)
    curr_meta_list.extend(curr_metadata_list)

    return curr_meta_list

# Get the value of the related entity given the relation line
def extractRelatedEntity(all_lines, check_line):
    entity_id = re.findall('T\d+', check_line)[-1]
    for line in all_lines:
        if entity_id in line:
            return re.findall(r'-?\d*\.\d+|\d+', line)[-1]

# Main method for parsing an LTP annotation file
def parseLtpFile(src, dest):
    ltp_lines = src.readlines()
    
    if not ltp_lines or not ltp_lines[0].startswith("T1\tArticleTitle"):
        return
    
    if "Not_Curated" in ltp_lines[1]:
        return
    
    if "Complicated_LTP" in ltp_lines[2] or "Not_LTP" in ltp_lines[2]:
        return
    
    pmid = re.search("\d+\.ann", src.name).group(0).split('.')[0]
    
    if not m.Article.objects.filter(pmid = float(pmid)):
        return
    
    a = m.Article.objects.filter(pmid = float(pmid))[0]
    metadata = collectMeta(a)
    if not metadata:
        metadata = []

    print "Processing metadata for article: %s" % a.pmid

    for line in ltp_lines:
        if "LTPControlValue" in line:
            entity_num = (re.search("T\d+", line)).group(0)
            entity_score = 0
            conf = 0
            sterr = float('NaN')
            n = float('NaN')
            fixError = False
            
            try:
                ltpVal = float(line.split("\t")[2].strip())
            except Exception:
                # This will extract mean of all numbers in line[2], all numbers will be treated as positive
                # TODO: the issue will arise when encountering a range of negative numbers
                ltpVal = get_num(line.split("\t")[2].strip())
                
            adj_ltpVal = ltpVal
            
            for check_line in ltp_lines:
                # Find the lines of .ann file that contain the curated LTP control value reference number, Example: T51
                if re.search(entity_num + '\s', check_line):
                    if 'HasError' in check_line:
                        sterr = extractRelatedEntity(ltp_lines, check_line)
                        # If the standard error relates to a fold-change value - adjust it
                        if fixError:
                            sterr = float(sterr) * 100
                    if 'NumTrials' in check_line:
                        n = extractRelatedEntity(ltp_lines, check_line)
                    if 'Confidence' in check_line:
                        if 'Certain' in check_line:
                            conf = 3
                        elif 'Probable' in check_line:
                            conf = 2
                        else:
                            conf = 1
                    if 'Curation %s Curated' % entity_num in check_line:
                        entity_score += 1
                    if 'LTPValueType' in check_line:
                        if 'Additive' in check_line:
                            adj_ltpVal += 100
                        if 'Fold-change' in check_line:
                            adj_ltpVal *= 100
                            fixError = True
                            # if sterr value has been found and saved before fold-change attribute - adjust it
                            if sterr:
                                sterr = float(sterr) * 100
                        
            if entity_score == 1:
                dest.writerow([ltpVal, adj_ltpVal, conf, sterr, n] + metadata)

# Driver portion of the script - iterates over all files and subfolders of the specified list of folders (curators)
# and parses each .ann file it finds for control LTP values                              
for input_root, output_path in curators:
    # cleanup any previously created output files
    fileRemove(output_path)
    
    dest = csv.writer(open(output_path, "w+b"), delimiter = '\t')
    dest.writerow(all_headers)
    for folder, subs, files in os.walk(input_root):
        for filename in files:
            with open(os.path.join(folder, filename), 'r') as src:
                parseLtpFile(src, dest)

print "done"