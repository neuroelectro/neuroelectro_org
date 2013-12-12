"""
A list of functions to operate on the NeuroTree database
including loading of data and performing shortest path operations 
between node pairs and network visualization
"""

import models as m
import sys,csv,codecs,cStringIO,copy
from django.db import transaction

#row_ = None

# ---------- WARNING ----------
# Before loading anything from the .php files, 
# make sure every field in the neurotree model tables is utf-8 encoded.  
# For example, do something like this to every VARCHAR column:  
# ALTER TABLE neurotree_node MODIFY COLUMN lastname VARCHAR(75) CHARACTER SET utf8 COLLATE utf8_general_ci;
# Except pick a VARCHAR(x) value where x is the max_length value in the model field.  
# You will have to do this after every migration as well since it will switch the encoding
# back to the database default.  

def prog(num,denom):
    fract = float(num)/denom
    hyphens = int(round(50*fract))
    spaces = int(round(50*(1-fract)))
    sys.stdout.write('\r%.2f%% [%s%s]' % (100*fract,'-'*hyphens,' '*spaces))
    sys.stdout.flush()  

def loadDB():
	loadNodes()
	loadEdges()

def loadNodes():
	with open('neurotree/data/dumpnodes.php','rU') as f:
		reader = csv.reader(f)
		junk = reader.next() # Skip leading blank line.  
		junk = reader.next() # Skip header.  
		rows = list(reader)
		n_rows = len(rows)
		with transaction.commit_on_success():
			for i,row in enumerate(rows):
				#if float(i)/n_rows < 0.6:
				#	continue
				prog(i,n_rows)
				if len(row)<7: # Probably the last line (blank).
					continue
				trees = []
				tree_names = row[6].split('+')
				for tree_name in tree_names:
					tree,created = m.Tree.objects.get_or_create(name=tree_name)
					trees.append(tree)

				firstname = row[1].decode('latin1')
				middlename = row[2].decode('latin1')
				lastname = row[3].decode('latin1')
				location = row[4].decode('latin1')
				altpubmed = row[5].decode('latin1')
				#global row_
				#row_ = row
				#print firstname,middlename,lastname,location
				node,created = m.Node.objects.get_or_create(id=row[0],
											 defaults={'firstname':firstname,
										   			   'middlename':middlename,
										   			   'lastname':lastname,
										   			   'location':location,
										   			   'altpubmed':altpubmed})
				for tree in trees: 
					node.tree.add(tree)

def loadEdges():
	with open('neurotree/data/dumpedges.php','rU') as f:
		reader = csv.reader(f)
		junk = reader.next() # Skip headers . 
		junk = reader.next() # Skip headers . 
		rows = list(reader)
		n_rows = len(rows)
		with transaction.commit_on_success():
			for i,row in enumerate(rows):
				prog(i,n_rows)
				try:
					node1 = m.Node.objects.get(id=int(row[0]))
					node2 = m.Node.objects.get(id=int(row[2]))
				except:
					print "One of these nodes not found: %d,%d" % (int(row[0]),int(row[2]))
					pass 
					# Nodes probably did not exist.  
					# There are some edges in the file with node id's
					# that are not in the dumpnodes.php file.  
				else:
					edge,created = m.Edge.objects.get_or_create(
									node1=node1,
									node2=node2,
									defaults={'relationcode':row[1],
											  'relationstring':row[3],
											  'stopyear':int(row[4])})

def shortest_path(node1,node2,relationcodes=[1,2],directions=['up','down'],max_path_length=5,chain=[]):
	"""
	Finds the shortest path between any two pair of NeuroTree nodes
	"""
	chain_ = copy.copy(chain)
	chain_.append(node1)
	if node1 == node2:
		return chain_
	elif len(chain_) >= max_path_length:
		return None
	if 'up' in directions:
		parents = [x.node2 for x in node1.parents.filter(relationcode__in=relationcodes)]
	else:
		parents = []
	if 'down' in directions:
		children = [x.node1 for x in node1.children.filter(relationcode__in=relationcodes)]
	else:
		children = []
	kwargs = {'relationcodes':relationcodes,
			  'directions':directions,
			  'max_path_length':max_path_length,
			  'chain':chain_}
	possible_chains = []
	for parent in parents:
		possible_chain = shortest_path(parent,node2,**kwargs)
		if(possible_chain and possible_chain[-1] == node2): # Found a path.
			kwargs['max_path_length'] = len(possible_chain)  
		possible_chains.append(possible_chain)
	for child in children:
		possible_chain = shortest_path(child,node2,**kwargs)
		if(possible_chain and possible_chain[-1] == node2): # Found a path.
			kwargs['max_path_length'] = len(possible_chain)  
		possible_chains.append(possible_chain)
	possible_chains = [x for x in possible_chains if x is not None]
	chains = sorted(possible_chains,key=lambda x:len(x),reverse=False)
	return chains[0] if len(chains) else None

def author_path_length_matrix(authors):
	import neurotree.neurotree_author_search as search
	import numpy as np
	#authors = search.get_neurotree_authors()[0]
	matrix = np.zeros((len(authors),len(authors)))
	for i in range(len(authors)):
		prog(i,len(authors))
		for j in range(len(authors)):
			path = shortest_path(authors[i],authors[j],directions=['up'],max_path_length=3)
			matrix[i,j] = len(path) if path is not None else None
	return matrix

def graphviz_dot(authors,max_path_length=2):
	"""After running this, run: 
	dot -Tpdf -Gcharset=latin1 authors.dot -o authors.pdf
	on the command line."""
	f = open('authors.dot','w')
	f.write('digraph G {\r\n')
	for i,author1 in enumerate(authors):
		prog(i,len(authors))
		f.write('\t%s\r\n' % clean(author1.lastname))
		for author2 in authors:
			if author1 == author2:
				continue
			path = shortest_path(author1,
            					 author2,
            					 directions=['up'],
            					 max_path_length=max_path_length)
			if path is not None:
				#f.write('\t%s->%s\r\n' % (clean(author1.lastname),clean(author2.lastname)))
				for j in range(len(path)-1):
					f.write('\t%s->%s\r\n' % (clean(path[j].lastname),clean(path[j+1].lastname)))
				print path
	f.write('}')
	f.close()    

def graphviz_dot_plus_grandparents(author_list_full, authors, max_path_length=2):
	"""After running this, run: 
	dot -Tpdf -Gcharset=latin1 authors.dot -o authors.pdf
	on the command line."""
	f = open('authors.dot','w')
	f.write('digraph G {\r\n')
	for i,author1 in enumerate(author_list_full):
		prog(i,len(author_list_full))
		f.write('\t%s\r\n' % clean(author1.lastname))
		if author1 in authors:
			f.write('\t%s\r[fillcolor = red]\r\n' % clean(author1.lastname))
		for author2 in author_list_full:
			if author1 == author2:
				continue
			path = shortest_path(author1,
            					 author2,
            					 directions=['up'],
            					 max_path_length=max_path_length)
			if path is not None:
				#f.write('\t%s->%s\r\n' % (clean(author1.lastname),clean(author2.lastname)))
				for j in range(len(path)-1):
					f.write('\t%s->%s\r\n' % (clean(path[j].lastname),clean(path[j+1].lastname)))
				print path
	f.write('}')
	f.close()    

def clean(string):
	x = string.replace('@','').replace(' ','_').replace('-','_').replace('(','').replace(')','').replace(',','_').replace('.','_').replace('&','_').replace("'",'_')
	return x.encode('latin1')

