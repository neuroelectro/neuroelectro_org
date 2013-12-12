# -*- coding: utf-8 -*-
"""
Bayes rule for PubMed/NeuroTree/NeuroElectro

{m}: the set of individuals in pubmed.
{t}: the set of individuals (nodes) in neurotree.
{e}: the set of individuals (authors) in neuroelectro.

N = N(A,B) = # of papers in which A is first author and B is last author.  
A and B are drawn from the members of {t}, which are assumed to be a subset of the members of {m}.  

(1) p( B advised A | N) = p(N | B advised A) * p(B advised A)/p(N) 
						= x1 * y1 / z1

(2) p( B advised A | N, A in e) = p(N | A in e, B advised A) * p(A in e | B advised A) * p(B advised A) / (p(N | A in e) * p(A in e))
								= x2 * x3 * y1 / (z2 * z3)

x1 = p(N | B advised A)
x2 = p(N | A in e, B advised A)
x3 = p(A in e | B advised A)
y1 = p(B advised A)
z1 = p(N) # This is probably intractable because there are too many nodes.  
z2 = p(N | A in e)
z3 = p(A in e)
"""



from neurotree.models import Node
from pubmed_integration import compute_neurotree_coauthorship_distro
from author_search import get_neurotree_authors
from numpy import hist
RELATION_CODES = [1,2]

def X1():
	A_list = Node.objects.all()
	# These are the unconditional A, who are just every individual in NeuroTree.   

	distro = compute_neurotree_coauthorship_histo_uncond(A_list):
	# This should be the distribution of (N | B advised A).
	# It looks up the B (advisor) corresponding to A.    

	density, bin_edges = hist(distro, bins=range(10), density=True)
	# This should be the probability density of (N | B advised A). 

	return density

def X2():
	A_list = get_neurotree_authors()[0] 
	# These are the A in e, or more specifically the A who are last authors in e.  
	# I think this restriction requires a modification to the calculation.  

	distro = compute_neurotree_coauthorship_histo_uncond(A_list):
	# This should be the distribution of (N | A (are last authors) in e, B advised A).
	# That function looks up the B (advisor) corresponding to A.    

	density, bin_edges = hist(distro, bins=range(10), density=True)
	# This should be the probability density of (N | A are last authors in e). 

	return density

def X3():
	relationships = Edge.objects.filter(relationcode__in=RELATION_CODES)
	A_list = [x.node2 for x in relationships]
	# Here I am selecting, over all cases for which B advised A is meaningful.  
	# I think that this is equivalent to iterating over all A and all B in two loops
	# and selecting those cases where B advised A.  
	# I expect some individuals to appear here multiple times.  

	authors = get_neurotree_authors()[0]
	# All NeuroTree (last) authors, as NeuroTree Nodes.  

	intersection = list(set(A_list) & set(authors))
	# This should be the intersection of these two lists, i.e. A in e and B advised A.  
	# The count n(A in e | B advised A) should be the length of this list.  
	
	proportion = float(len(intersection)) / len(A_list)
	# p(A in e | B advised A) = p(A in e, B advised A) / p(B advised A)
	# 						  = n(A in e, B advised A) / n(B advised A)

	return proportion

def Y1():
	relationships = Edge.objects.filter(relationcode__in=RELATION_CODES)
	nodes = Node.objects.all()

	proportion = float(relationships.count()) / nodes.count()*(nodes.count()-1)
	# p(B advised A) = n(advisory relationships) / n(possible relationships)
	# 				 = n(advisory relationships) / (num_nodes * (num_nodes-1))

	return proportion

def Z1():
	"""This will be intractable because it would require |t|^2 pubmed searches."""  
	pass

def Z2():
	A_list = get_neurotree_authors()[0] 
	# These are the A in e, or more specifically the A who are last authors in e.  
	# I think this restriction requires a modification to the calculation.  

	B_list = Node.objects.all()
	# These are the unconditional B, who, like the unconditional A, are just
	# every individual in NeuroTree.   

	distro = compute_neurotree_coauthorship_histo_uncond(A_list, 
                                                		 B_list):
	# This should be the distribution of (N | A (are last authors) in e, B advised A).
	# That function looks up the B (advisor) corresponding to A.    

	density, bin_edges = hist(distro, bins=range(10), density=True)
	# This should be the probability density of (N | A (are last authors) in e, ). 

	return density


def Z3():
	nodes = get_neurotree_authors()[0] 
	# These are the A in e, or more specifically the A who are last authors in e.  
	# I think this restriction requires a modification to the calculation.  

	proportion = float(len(nodes)) / Nodes.objects.all().count()
	# The number of A in {e} divided by the total number of A.  
	# Recall that A are drawn from {t}.  

	return proportion

x1 = X1()
x2 = X2()
x3 = X3()
y1 = Y1()
z1 = Z1()
z2 = Z2()
z3 = Z3()

result = x2 * x3 * y1 / (z2 * z3)

print result

