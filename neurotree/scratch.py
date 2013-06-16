import models as m
import sys,csv,codecs,cStringIO
from django.db import transaction

#row_ = None

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

def shortest_path(node1,node2,max_path_length=5):
	pass

