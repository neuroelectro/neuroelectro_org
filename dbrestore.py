
# Methods to restore the database after the migration. applied by Rick.  
import sys
import pickle
import neuroelectro.models as m
import xlrd
import re

sys.path.append('code')

def main():
	update_concept_maps()
	update_ephys_defs()
	assign_robot()
	# update_articles() # this one will take a while and prob fail

def update_concept_maps():
	ncm_fields, ecm_fields, nedm_fields = load()
	
	datatables = m.DataTable.objects.all()
	for x in datatables:
	    m.DataSource.objects.get_or_create(data_table=x)
    
	anon_user = m.get_anon_user()
	robot_user = m.get_robot_user()
	for nedm_field in nedm_fields:
	    nedm=m.NeuronEphysDataMap.objects.get(pk=nedm_field['pk'])
	    data_source = m.DataSource.objects.get(data_table=nedm_field['fields']['data_table'])
	    nedm.source = data_source
	    if nedm.added_by_old == 'human':
	    	nedm.added_by = anon_user
	    else:
	    	nedm.added_by = robot_user
	    nedm.save()
	    
	for ncm_field in ncm_fields:
	    ncm=m.NeuronConceptMap.objects.get(pk=ncm_field['pk'])
	    data_source = m.DataSource.objects.get(data_table=ncm_field['fields']['data_table'])
	    ncm.source = data_source
	    if nedm.added_by_old == 'human':
	    	nedm.added_by = anon_user
	    else:
	    	nedm.added_by = robot_user
	    nedm.save()
	    
	for ecm_field in ecm_fields:
	    ecm=m.EphysConceptMap.objects.get(pk=ecm_field['pk'])
	    data_source = m.DataSource.objects.get(data_table=ecm_field['fields']['data_table'])
	    ecm.source = data_source
	    if nedm.added_by_old == 'human':
	    	nedm.added_by = anon_user
	    else:
	    	nedm.added_by = robot_user
	    nedm.save()
	    
def update_ephys_defs():
	table, nrows, ncols = load_ephys_defs()
	for i in range(1,nrows):
		ephysProp = table[i][0]
		rawSyns = table[i][2]
		ephysDef = table[i][1]
		unit = table[i][3]
		unit_main = table[i][4]
		unit_sub = table[i][5]
		ephysOb = m.EphysProp.objects.get_or_create(name = ephysProp)[0]
		if unit_main != '':
			u = m.Unit.objects.get_or_create(name = '%s' % unit_main, prefix = '%s' % unit_sub)[0]
			ephysOb.units = u
		if ephysDef != '':
			ephysOb.definition = ephysDef
		print u.pk,ephysDef
		ephysOb.save()

def assign_robot():
    nams = m.NeuronArticleMap.objects.all()
    u = m.get_robot_user()
    for nam in nams:
        nam.added_by = u
        nam.save()
        
def update_articles():
	all_arts = Article.objects.all()
	pmid_list = [a.pmid for a in all_arts]
	for pmid in pmid_list:
	    add_single_article_full(pmid)

def load():
	pkl_file = open('user_contrib_data', 'rb')
	myData = pickle.load(pkl_file)
	pkl_file.close()
	ncm_fields, ecm_fields, nedm_fields = myData
	return (ncm_fields, ecm_fields, nedm_fields)
	
def load_ephys_defs():
	book = xlrd.open_workbook("data/Ephys_prop_definitions_3.xlsx")
	#os.chdir('C:\Python27\Scripts\Biophys')
	sheet = book.sheet_by_index(0)
	ncols = sheet.ncols
	nrows = sheet.nrows

	table= [ [ 0 for i in range(ncols) ] for j in range(nrows ) ]
	for i in range(nrows):
		for j in range(ncols):
			table[i][j] = sheet.cell(i,j).value
	return table, nrows, ncols
