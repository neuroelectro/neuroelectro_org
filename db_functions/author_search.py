from neuroelectro import models as m

__author__ = 'stripathy'


def get_article_last_author(article):
    """
    Gets the last author object from NeuroElectro DB given an article
    """
    return get_article_author(article, author_position = -1)


def get_article_author(article, author_position = -1):
    """
    Gets the author object from NeuroElectro DB given an article and requested author_position (0 index)
    """
    author_list_str = article.author_list_str
    if author_list_str is None:
        return None
    author_list = author_list_str.split(';')
    last_author_str = author_list[author_position]

    last_author_split_str = last_author_str.split()
    last_author_last_name = last_author_split_str[:-1]
    last_author_last_name = ' '.join(last_author_last_name)

    try:
        if len(last_author_split_str) > 1:
            last_author_initials = last_author_split_str[-1]
            author_ob = m.Author.objects.filter(last = last_author_last_name,
                                                initials = last_author_initials,
                                                article = article)[0]
        else:
            last_author_initials = None
            author_ob = m.Author.objects.filter(last = last_author_last_name,
                                                article = article)[0]
        return author_ob
    except IndexError:
        #print 'Cant find author %s' % last_author_str
        #cant_find_count += 1
        #last_author_node_list.append(None)
        return None
