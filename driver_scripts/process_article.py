import sys
import article_text_mining.assign_metadata as meta
import neuroelectro.models as m

def process_article(article_id):
    article = m.Article.objects.get(id = int(article_id))
    processed = meta.assign_solution_concs(article)  
    if processed == 1:
        meta.assign_species(article)
        meta.assign_electrode_type(article)
        meta.assign_strain(article)
        meta.assign_prep_type(article)
        meta.assign_rec_temp(article)
        meta.assign_animal_age(article)
        meta.assign_jxn_potential(article)
    print processed

def main():
    process_article(int(sys.argv[1]))
    
if __name__ == '__main__':
    main()