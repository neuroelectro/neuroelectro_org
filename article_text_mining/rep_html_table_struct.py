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

    # need to count column tags
    row_tags = html_table.findAll('tr')
    n_rows = 0
    for tag in row_tags:
        temp_num_rows, temp_num_cols = get_row_col_width(tag)
        n_rows += temp_num_rows

    # finds maximum number of columns in any row
    n_cols = 0
    for row_tag in row_tags:
        curr_col_tags = row_tag.findAll('td')
        curr_col_width = 0
        for tag in curr_col_tags:
            temp_num_rows, temp_num_cols = get_row_col_width(tag)
            curr_col_width += temp_num_cols
        if curr_col_width > n_cols:
            n_cols = curr_col_width

    # initialize representation of data table as 2D python table
    data_table_rep = [[0 for i in range(n_cols)] for j in range(n_rows)]

    # initialize representation of data table as 2D python table composed of html id elements
    id_table_rep = [[0 for i in range(n_cols)] for j in range(n_rows)]

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
        try:
            for th_html_tag in header_tags:

                cell_text = get_tag_text(th_html_tag)
                row_width, column_width = get_row_col_width(th_html_tag)

                for i in range(row_cnt, row_cnt + row_width):
                    while data_table_rep[i][col_cnt] != 0:
                        col_cnt += 1
                    for j in range(col_cnt, col_cnt + column_width):

                            data_table_rep[i][j] = cell_text
                            id_table_rep[i][j] = th_html_tag['id']

                col_cnt += column_width
        except IndexError:
            continue
        col_tags = tr_html_tag.findAll('td')
        try:
            for td_html_tag in col_tags:
                cell_text = get_tag_text(td_html_tag)
                row_width, column_width = get_row_col_width(td_html_tag)

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


def printHtmlTable(tableTag):
    """Convenience function for printing a stringified html data table"""
    soup = BeautifulSoup(''.join(tableTag))
    tableStr = u''
    try:
        # print title
        #title = dt.article.title
        #tableStr += title + u'\n'
        # print 'Title: ' + title.encode('utf-8')

        table = soup.find('table')
        captionTag = soup.find('div', {'class':'table-caption'})
        if captionTag is None:
            captionTag = soup.find('div', {'class':'auto-clean'})
        if captionTag is not None:
            caption = get_tag_text(captionTag)
    #        caption = ''.join(captionTag.findAll(text=True))
            tableStr += caption + u'\n'
        rows = table.findAll('tr')
        for tr in rows:
            headers = tr.findAll('th')
            for th in headers:
                currText = get_tag_text(th)
    #            currText = ''.join(th.findAll(text=True))
    #            if currText is None:
    #                currText = '\t'
                text = u''.join(currText)
                tableStr += text +"|"
            cols = tr.findAll('td')
            for td in cols:
                currText = get_tag_text(td)
    #            currText = ''.join(td.findAll(text=True))
    #            if currText is None:
    #                currText = '\t'
                text = u''.join(currText)
                tableStr += text +"|"
            tableStr += u'\n'
        footnotesTag = soup.find('div', {'class':'table-foot'})
        footnotes = get_tag_text(footnotesTag)
        tableStr += footnotes

        print tableStr.encode("iso-8859-15", "replace")
        return tableStr
    except (UnicodeDecodeError, UnicodeEncodeError):
        print 'Unicode printing failed!'
        return


def get_row_col_width(tag):
    """Gets the row and column width of a data table cell tag
    Args:
        tag: a beautiful soup tag of a data table cell

    Returns:
        num_rows: integer of the number of rows the cell spans
        num_cols: integer of the number of columns the cell spans
    """

    try:
        num_rows = int(tag['rowspan'])
    except KeyError:
        num_rows = 1
    try:
        num_cols = int(tag['colspan'])
    except KeyError:
        num_cols = 1
    return num_rows, num_cols
