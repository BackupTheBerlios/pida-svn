import os
import urllib2
import urllib

from nevow import flat, tags as T


TRAC = 'http://pseudoscience.co.uk/projects/pida'
BASE = 'PidaDocumentation'

import re
VRE = re.compile(r'name\="version"\ value\="([0-9]+)')

def makeurl(part):
    return '%s/wiki/%s' % (TRAC, part)

def edit_wiki(page, data):
    url = '%s' % makeurl(page)
    geturl = '%s?action=edit' % url
    u = urllib2.urlopen(geturl)
    html = u.read()
    version = VRE.search(html).groups()[0]
    data = ('%s\n\n%s' % (data, create_advert()))
    formdata = {'action':'edit',
                'text': data,
                'version':version,
                'user':'Ali'}
    fdata = urllib.urlencode(formdata)
    try:
        u = urllib2.urlopen(url, data=fdata)
        u.read()
        print page, 'done'
    except urllib2.HTTPError:
        print page, 'no update needed/ update failed'

def render_list(ctx, (base, data)):
    for d in data:
        href = '%s/%s' % (base, d)
        yield T.li[T.a(href=href)[d]]

def create_l(base, iterable, ltype=T.ol):
    return flat.flatten(T.div[
                        T.h1[base],
                        T.h2['Table Of Contents'],
                        ltype(data=(base, iterable))[render_list]
                        ])

def create_advert():
    s = ('This page was automatically generated and '
         'uploaded using ')
    return trac_html(flat.flatten(
        T.div(class_='last-modified')[
        s,
        T.a(href='/projects/pida/wiki/TracDumbUpload')[
            'TracDumbUpload'],
        T.br, T.br
        ]))


def trac_html(html):
    return '{{{\n#!html\n%s\n}}}' % html

def trac_rst(rst):
    return '{{{\n#!rst\n%s\n}}}' % rst
    
manuals = ['UserManual', 'DeveloperDocumentation', 'FAQ']

base_page_text = trac_html(create_l(BASE, manuals, ltype=T.ul))
edit_wiki(BASE, base_page_text)

for manual in manuals:
    page = '/'.join([BASE, manual])
    sections = []
    contentspath = os.path.join(manual, 'contents.ini')
    f = open(contentspath)
    for line in f:
        fname = line.strip()
        if not fname.endswith('.rst'):
            continue
        wname = fname.rsplit('.', 1)[0].capitalize()
        fpath = os.path.join(manual, fname)
        f = open(fpath)
        text = f.read()
        f.close()
        trac_text = trac_rst(text)
        sections.append((wname, trac_text))
    manual_base = '/'.join([BASE, manual])
    single_page = '/'.join([manual_base, 'SinglePage'])
    single_link = '/'.join([manual, 'SinglePage'])
    manual_page_text = trac_html(create_l(manual,
                       [s[0] for s in sections]))
    contents_text = manual_page_text
    single_text = ''
    backlinks = 'up: %s' % BASE
    manual_page_text = '\n'.join([backlinks,
                                  manual_page_text,
                                 '[wiki:%s Entire Manual on a single page]'
                                 % single_page])
    edit_wiki(manual_base, manual_page_text)
    contentspath = os.path.join(manual, 'contents.ini')
    f = open(contentspath)
    backlinks = ('up: %s | %s' % (BASE, manual_base))
    for section, text in sections:
        single_text = '\n'.join([single_text, text])
        sect_url = '/'.join([manual_base, section])
        edit_wiki(sect_url, '\n'.join([backlinks, text]))
    edit_wiki(single_page, single_text)
    

    

    
