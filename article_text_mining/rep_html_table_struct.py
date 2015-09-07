from bs4 import BeautifulSoup
from article_text_mining.text_mining_util_fxns import get_tag_text

__author__ = 'shreejoy'


def rep_html_table_struct(html_table_tag):
    """Returns a 2D table row-column representation of an input html data table

    Args:
        html_table_tag: the html table tag of a data table object,
                            something that can be beautiful soupified
    Returns:
        data_table_rep: a 2D python table representation of the table text
        num_header_rows: number of rows in the table header
        id_table_rep: a 2D python table representation of the table where each cell element
                        is the 'id' tag of the table cell

    Comments:
        function is lightly tested but should be robust to most ugly html tables provided by publishers

    """

    soup = BeautifulSoup(''.join(html_table_tag), 'lxml')

    html_table = soup.find('table')
    row_tags = html_table.findAll('tr')

    # line of code could be more robust - ideally it'd be the max number of columns in any row
    n_cols = len(row_tags[-1].findAll('td'))

    # initialize representation of data table as 2D python table
    data_table_rep = [[0 for i in range(n_cols)] for j in range(len(row_tags))]

    # initialize representation of data table as 2D python table composed of html id elements
    id_table_rep = [[0 for i in range(n_cols)] for j in range(len(row_tags))]

    row_cnt = 0
    num_header_rows = 0

    # iterate through all table rows
    for tr_html_tag in row_tags:
        header_tags = tr_html_tag.findAll('th')
        if len(header_tags) > 0:
            num_header_rows += 1

        # counts the number of columns - I think??
        # set colCnt by finding first non-zero element in table
        try:
            col_cnt = data_table_rep[row_cnt].index(0)
        except ValueError:
            print 'Table is likely fucked up!!!'
            data_table_rep = None
            id_table_rep = None
            return data_table_rep, 0, id_table_rep

        for th_html_tag in header_tags:

            cell_text = get_tag_text(th_html_tag)
            try:
                column_width = int(th_html_tag['colspan'])
            except KeyError:
                column_width = 1
            try:
                row_width = int(th_html_tag['rowspan'])
            except KeyError:
                row_width = 1

            for i in range(row_cnt, row_cnt + row_width):
                while data_table_rep[i][col_cnt] != 0:
                    col_cnt += 1
                for j in range(col_cnt, col_cnt + column_width):
                    try:
                        data_table_rep[i][j] = cell_text
                        id_table_rep[i][j] = th_html_tag['id']
                    except IndexError:
                        continue
            col_cnt += column_width
        col_tags = tr_html_tag.findAll('td')
        try:
            for td_html_tag in col_tags:
                cell_text = get_tag_text(td_html_tag)
                try:
                    column_width = int(td_html_tag['colspan'])
                except KeyError:
                    column_width = 1
                try:
                    row_width = int(td_html_tag['rowspan'])
                except KeyError:
                    row_width = 1

                for i in range(row_cnt, row_cnt + row_width):
                    # need to check if current row and col already has an element
                    while data_table_rep[i][col_cnt] != 0:
                        col_cnt += 1
                    for j in range(col_cnt, col_cnt + column_width):
                        data_table_rep[i][j] = cell_text
                        id_table_rep[i][j] = td_html_tag['id']
                col_cnt += column_width
        except IndexError:
            pass

        row_cnt += 1
    return data_table_rep, num_header_rows, id_table_rep
