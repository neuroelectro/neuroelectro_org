'''
Extract concentrations from the existing InternalSolution and ExternalSolution entities
'''
__author__ = 'dtebaykin'
import neuroelectro.models as m
from django.db.models import Q
from article_text_mining.assign_metadata import record_compounds
from scripts.dbrestore import prog

def record_solution_concs():
#     articles = m.Article.objects.all()
    
    articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1,
                                            datatable__datasource__neuronephysdatamap__isnull = False) | 
                                            Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1,
                                              usersubmission__datasource__neuronephysdatamap__isnull = False)).distinct()
    
    robot_user = m.get_robot_user()
    
    solution_names = {"external": 'ExternalSolution', 
                      "internal": 'InternalSolution'}
    
    len_articles = articles.count()
    
    for i, article in enumerate(articles):
        prog(i, len_articles)
        for soln, soln_name in solution_names.iteritems():
            solution_ob = m.ArticleMetaDataMap.objects.filter(article = article, metadata__name = soln_name)
            if solution_ob and solution_ob[0].ref_text:
                record_compounds(article, None, solution_ob[0].ref_text.text, ["", "", "", ""], "%s_0" % soln, robot_user)
        
def run():
    print "Running record_solution_concs.py"
    record_solution_concs()
    print "\n\nFinished record_solution_concs.py"