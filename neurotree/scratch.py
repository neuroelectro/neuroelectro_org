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