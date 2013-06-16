from django.db import models as m

# Create your models here.

#ALTER TABLE neurotree_node MODIFY COLUMN lastname VARCHAR(75) CHARACTER SET utf8 COLLATE utf8_general_ci;


class Tree(m.Model):
	"""Tree type (e.g. neuro, chemistry, phys)"""
	name = m.CharField(max_length=15)
	def __unicode__(self):
		return self.name

class Node(m.Model):
	"""A node in a tree"""
	firstname = m.CharField(max_length=50)
	middlename = m.CharField(max_length=50)
	lastname = m.CharField(max_length=75)
	location = m.CharField(max_length=200)
	altpubmed = m.CharField(max_length=400)
	tree = m.ManyToManyField(Tree)
	nodes = m.ManyToManyField('Node',through='Edge')
	def __unicode__(self):
		return '%s %s %s' % (self.firstname,self.middlename,self.lastname)

class Edge(m.Model):
	"""An edge between nodes"""
	node1 = m.ForeignKey(Node,related_name='children') # One node of the edge.  
	node2 = m.ForeignKey(Node,related_name='parents') # The other node of the edge.  
	relationcode = m.IntegerField()
	relationstring = m.CharField(max_length=25)
	stopyear = m.IntegerField()
	def __unicode__(self):
		return '%s is/was a %s %s' % (self.node1,self.relationstring,self.node2)
