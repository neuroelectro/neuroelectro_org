from django.conf import settings
import neuroelectro.models as m
import article_text_mining.assign_metadata as meta
from article_text_mining.html_process_tools import getMethodsTag
from django.db.models import Q
import os, re, nltk, sys
import fuzzywuzzy.fuzz as fuzz
import pycrfsuite
from itertools import chain
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import sklearn
from random import randint


# Modified From: http://nbviewer.jupyter.org/github/tpeng/python-crfsuite/blob/master/examples/CoNLL%202002.ipynb
def word2features(sent, i):
    word = sent[i]
    
    features = [
        'word.lower=' + word.lower(),
        'word[-3:]=' + word[-3:],
        'word[-2:]=' + word[-2:],
        'word.isupper=%s' % word.isupper(),
        'word.istitle=%s' % word.istitle(),
        'word.isdigit=%s' % word.isdigit(),
        'word.isna=%s' % meta.na_re.search(word),
        'word.ismm=%s' % meta.conc_re.search(word),
        'word.isca=%s' % meta.ca_re.search(word),
        'word:isk=%s' % meta.k_re.search(word),
        'word.iscl=%s' % meta.cl_re.search(word),
        'word.isMg=%s' % meta.mg_re.search(word)
    ]
    if i > 0:
        word1 = sent[i-1]
        features.extend([
            '-1:word.lower=' + word1.lower(),
            '-1:word.istitle=%s' % word1.istitle(),
            '-1:word.isupper=%s' % word1.isupper(),
            '-1:word.isdigit=%s' % word1.isdigit(),
            '-1:word.isna=%s' % meta.na_re.search(word1),
            '-1:word.ismm=%s' % meta.conc_re.search(word1),
            '-1:word.isca=%s' % meta.ca_re.search(word1),
            '-1:word:isk=%s' % meta.k_re.search(word1),
            '-1:word.iscl=%s' % meta.cl_re.search(word1),
            '-1:word.isMg=%s' % meta.mg_re.search(word1)
        ])
        
    if i < len(sent)-1:
        word1 = sent[i+1]
        features.extend([
            '+1:word.lower=' + word1.lower(),
            '+1:word.istitle=%s' % word1.istitle(),
            '+1:word.isupper=%s' % word1.isupper(),
            '+1:word.isdigit=%s' % word1.isdigit(),
            '+1:word.isna=%s' % meta.na_re.search(word1),
            '+1:word.ismm=%s' % meta.conc_re.search(word1),
            '+1:word.isca=%s' % meta.ca_re.search(word1),
            '+1:word:isk=%s' % meta.k_re.search(word1),
            '+1:word.iscl=%s' % meta.cl_re.search(word1),
            '+1:word.isMg=%s' % meta.mg_re.search(word1)
        ])
                
    return features

# Adapted From: http://nbviewer.jupyter.org/github/tpeng/python-crfsuite/blob/master/examples/CoNLL%202002.ipynb
def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

path = os.getcwd()
    
reload(sys)  
sys.setdefaultencoding('utf8')
os.chdir(settings.FULL_TEXTS_DIRECTORY)
    
#articles = m.Article.objects.all()
articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1,
                                        datatable__datasource__neuronephysdatamap__isnull = False) | 
                                        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1,
                                          usersubmission__datasource__neuronephysdatamap__isnull = False)).distinct()

corpus = []

for a in articles:
    if a.pk > 80000:
        break
    try: 
        if a.articlefulltext_set.all().count() == 0:
            print "No full text associated with article: %s" % a.pk
            continue
        
        full_text_list = m.ArticleFullText.objects.filter(article = a.pk)
        
        if not full_text_list:
            print "Full text file does not exist for article: %s" % a.pk
            continue
        
        try:
            full_text = full_text_list[0].get_content()
        except:
            print "File not found for article: %s" % a.pk
            continue
        
        methods_tag = getMethodsTag(full_text, a)
        
        if methods_tag is None:
            print "No methods tag found article id: %s, pmid: %s" % (a.pk, a.pmid)
            continue
        
        article_text = re.sub('\s+', ' ', methods_tag.text)
        
        if len(article_text) <= 100:
            print "Methods section is too small. Article id: %s, pmid: %s" % (a.pk, a.pmid)
            continue
        
        amdm = m.ArticleMetaDataMap.objects.filter(article = a, metadata__name = "ExternalSolution")[0]
        ref_text = amdm.ref_text
        solns = ref_text.text
        
        amdm = m.ArticleMetaDataMap.objects.filter(article = a, metadata__name = "InternalSolution")[0]
        ref_text = amdm.ref_text
        solns = solns + " " + ref_text.text
                
        sentences = nltk.sent_tokenize(article_text)
        
        for sent in sentences:
            sent = sent.decode('utf-8').strip()
            words = nltk.word_tokenize(sent)
            
            if fuzz.partial_ratio(sent, solns) >= 80:
                corpus.append([words, ["soln"] * len(words)])
            elif randint(0, 100) == 100:
                corpus.append([words, ["other"] * len(words)])
                
        print "Processed: %s" % a.pk
        
    except Exception, e:
        print "Exception occurred for article %s: %s" % (a.pk, str(e))

split = int(len(corpus)*0.9)
x_train = [sent2features(s[0]) for s in corpus[:split]]
y_train = [s[1] for s in corpus[:split]]

x_test = [sent2features(s[0]) for s in corpus[split + 1:]]
y_test = [s[1] for s in corpus[split + 1:]]

trainer = pycrfsuite.Trainer(verbose=False)

for xseq, yseq in zip(x_train, y_train):
    trainer.append(xseq, yseq)
    
trainer.set_params({
    'c1': 1.0,   # coefficient for L1 penalty
    'c2': 1e-3,  # coefficient for L2 penalty
    'max_iterations': 50,  # stop earlier

    # include transitions that are possible, but not observed
    'feature.possible_transitions': True
})

def my_classification_report(test, pred):
    lb = LabelBinarizer()
    y_true_combined = lb.fit_transform(list(chain.from_iterable(test)))
    y_pred_combined = lb.transform(list(chain.from_iterable(pred)))
    
    return classification_report(y_true_combined, y_pred_combined, digits = 2)

trainer.train('crf-model.crfsuite')

print "done training"

tagger = pycrfsuite.Tagger()
tagger.open('crf-model.crfsuite')

y_pred = [tagger.tag(xseq) for xseq in x_test]
print(my_classification_report(y_test, y_pred))

from collections import Counter
info = tagger.info()

def print_transitions(trans_features):
    for (label_from, label_to), weight in trans_features:
        print("%-6s -> %-7s %0.6f" % (label_from, label_to, weight))

print("\nTop likely transitions:")
print_transitions(Counter(info.transitions).most_common(15))

print("\nTop unlikely transitions:")
print_transitions(Counter(info.transitions).most_common()[-15:])

def print_state_features(state_features):
    for (attr, label), weight in state_features:
        print("%0.6f %-6s %s" % (weight, label, attr))    

print("\nTop positive:")
print_state_features(Counter(info.state_features).most_common(20))

print("\nTop negative:")
print_state_features(Counter(info.state_features).most_common()[-20:])

print "\nRandomForest\n"
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators = 100)
rf = rf.fit(x_train, y_train)

y_pred = [rf.predict(xseq) for xseq in x_test]
print(my_classification_report(y_test, y_pred))

print "\nDecisionTree\n"
from sklearn.tree import DecisionTreeClassifier
clf = DecisionTreeClassifier(max_depth=None, min_samples_split=1,random_state=0)
clf = clf.fit(x_train, y_train)

y_pred = [clf.predict(xseq) for xseq in x_test]
print(my_classification_report(y_test, y_pred))

os.chdir(path)
print "\ndone"