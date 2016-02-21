#!/usr/bin/env python3
# Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
# Time-stamp: <2016-02-21 17:57:03 (jmiller)>

# imports
import sys
import re
from copy import copy
from bs4 import BeautifulSoup

# String patterns
CAPTION_START=r'\[caption id='
CAPTION_END=r'\[/caption\]'
CAPTION_RE = re.compile(CAPTION_START+r'.+?'+CAPTION_END)
BEGIN_BOLD_RE=re.compile(r'\S<strong>')
END_BOLD_RE=re.compile(r'</strong>\S')
BEGIN_ITALICS_RE=re.compile(r'\S<em>')
END_ITALICS_RE=re.compile(r'</em>\S')


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

    print(post_string2)
    return figures,post_string2.lstrip().rstrip()

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

if __name__ == "__main__":
    post_string = get_post_string(sys.argv[1])
    figures,post_string = get_figures(post_string)
    post_string = sanitize_string_whitespace(post_string)
    post_string = fix_bold_italics_ambiguity(post_string)
    post_string = convert_headers(post_string)
    post_string = convert_formatting(post_string)

    soup = BeautifulSoup(post_string)

    for a in soup.findAll('a'):
        print (a.text,a['href'])

    for li in soup.findAll('li'):
        for a in li.findAll('a'):
            print(li)

    print(post_string)

