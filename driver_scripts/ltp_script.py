"""
Search the literature corpus for articles containing information about Long Term Potentiation experiments
in the hippocampal brain region

Created by: Dmitrii Tebaikin
"""
import neuroelectro.models as m
import article_text_mining.assign_metadata as meta
import os, errno, csv

path = os.getcwd()

os.chdir("/Users/dtebaykin/Desktop/raw_full_texts")


articles = m.Article.objects.all()
# Record which articles have LTP mention in it
# csvout = csv.writer(open("/Users/dtebaykin/Documents/Neuroelectro documents/Spreadsheets/ltp_article_pmids.csv", "w+b"))
# for article in articles:
#     if meta.check_ltp_article(article):
#         csvout.writerow([article.pmid])

# Read the pmid's of LTP articles 
ltp_article_pmids = [] 
with open("/Users/dtebaykin/Documents/Neuroelectro documents/Spreadsheets/ltp_article_pmids.csv", "rb") as csvfile:
    for row in csvfile:
        ltp_article_pmids.append(float(row))

# Good LTP example: 10559382
# article_list = [17408856, 12177213]

def fileRemove(path):
    if os.path.exists(path) and os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

n = 0
for article in articles:
    if article.pmid in ltp_article_pmids:
        fileRemove(meta.BRAT_FILE_PATH + "ltp_data_%s.ann" % article.pmid)
        fileRemove(meta.BRAT_FILE_PATH + "ltp_data_%s.txt" % article.pmid)
        meta.assign_ltp(article)
        n += 1
            
os.chdir(path)
print "LTP articles: %s" % (n)
print "done"