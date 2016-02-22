#!/usr/bin/env python3
# Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
# Time-stamp: <2016-02-21 22:33:39 (jmiller)>

# imports
import sys
import re
from copy import copy
from functools import reduce
from bs4 import BeautifulSoup

# String patterns
CAPTION_START=r'\[caption id='
CAPTION_END=r'\[/caption\]'
CAPTION_RE = re.compile(CAPTION_START+r'.+?'+CAPTION_END)
BEGIN_BOLD_RE=re.compile(r'\S<strong>')
END_BOLD_RE=re.compile(r'</strong>\S')
BEGIN_ITALICS_RE=re.compile(r'\S<em>')
END_ITALICS_RE=re.compile(r'</em>\S')

LIST_RE=re.compile(r'<ul>[\S\s]+?</ul>')

CAPTION_OPEN_RE=re.compile(r'\[caption id=.+?\[/caption\]')

SEPARATOR="\n==================================================\n"

def get_post_string(filename):
    "Imports post contained in file with filename"
    with open(filename,'r') as f:
        post_string = f.read()
    return post_string
    
def get_figures(post_string):
    """
    Takes post_string and extracts figures.

    Returns [figures], post_string2

    where post_string2 no longer contains figures.
    """
    figures = CAPTION_RE.findall(post_string)
    post_string2 = copy(post_string)
    for figure in figures:
        post_string2=post_string2.replace(figure,'')

    return figures,post_string2.lstrip().rstrip()

def sanitize_paragraphs(post_string):
    post_string = post_string.replace('\n\n\n','\n\n')
    return post_string

def sanitize_string_whitespace(post_string):
    "Removes extraneous whitespace"
    post_string = post_string.replace(' </em>','</em>')
    post_string = post_string.replace('<em> ','<em>')
    post_string = post_string.replace('<strong> ','<strong>')
    post_string = post_string.replace(' </strong>','</strong>')
    post_string = post_string.replace('\n\n<h2>','\n<h2>')
    post_string = post_string.replace('</h2>\n\n','</h2>\n')
    post_string = post_string.replace('</em>.','.</em>')
    post_string = post_string.replace('</em>,',',</em>')
    post_string = post_string.replace('</strong>.','.</strong>')
    post_string = post_string.replace('</strong>,',',</strong>')
    post_string = post_string.replace('\n\n<h2>','\n<h2>')
    post_string = post_string.replace('</h2>\n\n','</h2>\n')
    return post_string

def fix_bold_italics_ambiguity(post_string):
    """Google plus can't handle any non whitespace
    characters near formatting markers. So we remove them.
    """
    for match in BEGIN_BOLD_RE.findall(post_string):
        post_string = post_string.replace(match,
                                          '{} <strong>'.format(match[0]))
    for match in END_BOLD_RE.findall(post_string):
        post_string = post_string.replace(match,
                                          '</strong> {}'.format(match[-1]))
    for match in BEGIN_ITALICS_RE.findall(post_string):
        post_string = post_string.replace(match,
                                          '{} <em>'.format(match[0]))
    for match in END_ITALICS_RE.findall(post_string):
        post_string = post_string.replace(match,
                                          '</em> {}'.format(match[-1]))
    return post_string

def convert_headers(post_string):
    "Converts headers to G+ readable"
    post_string = post_string.replace('<h2>','\n*')
    post_string = post_string.replace('</h2>','*\n')
    return post_string

def convert_formatting(post_string):
    "Converts italics and bold"
    post_string = post_string.replace('<em>','_')
    post_string = post_string.replace('</em>','_')
    post_string = post_string.replace('<strong>','*')
    post_string = post_string.replace('</strong>','*')
    return post_string

def convert_lists(post_string):
    list_containers = LIST_RE.findall(post_string)
    for container in list_containers:
        temp = "\n"
        list_items = BeautifulSoup(container).findAll('li')
        for item in list_items:
            temp +='* {}\n'.format(item.text)
            soup = BeautifulSoup('{}'.format(item))
            a = soup.find('a')
            temp = temp.replace('{}'.format(a),
                                a.text)
            temp += '{}\n\n'.format(a['href'])
        post_string = post_string.replace(container,
                                          temp)
    return post_string

def convert_links(post_string):
    post_string += '\n*References*\n\n'
    soup = BeautifulSoup(post_string)
    links = soup.findAll('a')
    for i,a in enumerate(links):
        post_string = post_string.replace('{}'.format(a),
                                          '{} [{}]'.format(a.text,i))
        post_string += '[{}] {}\n'.format(i, a['href'])
    post_string += '\n'
    return post_string

def parse_post_string(post_string):
    figures,post_string = get_figures(post_string)
    post_string = sanitize_paragraphs(post_string)
    post_string = sanitize_string_whitespace(post_string)
    post_string = fix_bold_italics_ambiguity(post_string)
    post_string = convert_headers(post_string)
    post_string = convert_formatting(post_string)
    post_string = convert_lists(post_string)
    post_string = convert_links(post_string)
    return figures,post_string

def parse_figure(figure_string):
    figure_string=sanitize_string_whitespace(figure_string)
    figure_string=fix_bold_italics_ambiguity(figure_string)
    figure_string=convert_formatting(figure_string)
    open_index = figure_string.find(']')
    figure_string = figure_string[open_index+1:]
    figure_string = figure_string.rstrip('[/caption]')
    links = BeautifulSoup(figure_string)
    avals =[a for a in links.findAll('a')]
    open_index = figure_string.find('</a>')
    figure_string = figure_string[open_index+4:]
    figure_string.lstrip().rstrip()
    figure_string = figure_string.replace('{}'.format(avals[1]),
                                          '{}'.format(avals[1].text))
    figure_string += ' {}'.format(avals[1]['href'])
    return figure_string

if __name__ == "__main__":
    post_string = get_post_string(sys.argv[1])
    figures,post_string = parse_post_string(post_string)
    for figure in figures:
        t = '{}'.format(figure)
        t = parse_figure(t)
        print('{}\n'.format(t))
        print(SEPARATOR)
        print('\n')
    print(post_string)
        
    
