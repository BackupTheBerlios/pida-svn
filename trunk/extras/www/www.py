
import sys
from nevow import rend, stan, loaders, tags as T

from ConfigParser import ConfigParser
import os
from string import Template

import subprocess

class Config(ConfigParser):

    def __init__(self):
        ConfigParser.__init__(self)
        self.load_config()
    

    def load_config(self, fn='www.ini'):
        self.read(fn)
    
    

CONF = Config()
from docutils.core import publish_parts

COMMON_RST = """
.. |imagedir| replace:: %s 
""" % CONF.get('resources', 'imagedir')

import urlparse

class Page(rend.Page):

    docFactory = loaders.stan(
                    T.html[
                        T.head[
                            T.link(rel='stylesheet',
                                href=urlparse.urljoin(
                                    CONF.get('target', 'baseurl'),
                                    CONF.get('stylesheet', 'filename')),    
                               type='text/css'),
                            T.title[
                                T.directive('title')
                            ]
                        ],
                        T.body[
                            T.div(id='main')[
                                T.directive('main')
                            ]
                        ]
                    ]
                 )

    def render_stylesheet(self, context, data):
        return open('main.css').read()

    def render_title(self, context, data):
        if data.title:
            tit = data.title
        else:
            tit = data.name
        return '%s - %s' % (tit, CONF.get('project', 'name'))
        
    def render_bottom(self, context, data):
        
        yield 'Copyright 2006 %s' % CONF.get('copyright', 'holder')        
     
        
    def render_main(self, context, data):
        for part in 'top', 'middle', 'bottom':
            yield T.div(id=part)[T.directive(part)]

    def render_middle(self, context, data):
        yield T.div(render=T.directive('trail'), data=data.get_ancestry())
        yield T.h1(class_='main-heading')[data.title]

        yield T.div(render=T.directive('items'), data=data.get_subdirs())

        yield T.div(render=T.directive('rst'))      

        yield T.div(render=T.directive('items'), data=data.get_items())
                
    def render_items(self, context, items):
        return self.render_menu(context, items)
        
    def render_main_menu(self, context, items):
        return self.render_menu(context, items, class_='main-menu')
    
    def render_subdirs(self, context, items):
        return self.render_menu(context, items)
    
    def render_rst(self, context, data):
        if data.body:
            return loaders.htmlstr(data.body)
        else:
            return ''
            

    def render_top(self, context, data):
        
        yield T.div(
                id='banner',
                )[CONF.get('project', 'name')]
        yield T.div(
                id='logo',
                )['"%s"' % CONF.get('project', 'motto')]
        def _menuitems():
            yield data.home
            for i in data.home.get_items():
                yield i
        yield T.div(
                render=T.directive('main_menu'),
                data=_menuitems()
                )
        

   
    def render_trail(self, context, items):
        trail = []
        for item in items:
            trail.append(
                T.span(class_='trail')[
                    T.a(href=item.get_url())[item.title]
                    ]
                )
            trail.append('>')
        if len(trail) <= 2:
            return ''
        else:
            trail.pop()
            return T.div(class_='trail')['You are:', trail]    
        
                
    def render_menu(self, context, items, class_='menu'):
        def _menu(items, class_):
            for item in items:
                yield T.li(class_=class_)[T.a(href=item.get_url(),
                                              class_=class_)[item.title]]
        return T.ul(class_=class_)[_menu(items, class_)]


        
class Model(object):

    def __init__(self, parent, path, home):
        self.parent = parent
        self.path = os.path.abspath(path)
        self.home = home
        self.name = os.path.basename(path)
        self.output_root = None
        self.rst = None
        self.items = []
        self.subdirs = []
        self.rst = ''
        self.title = None
        self.body = ''

    def get_items(self):
        for i in self.items:
            yield i

    def get_subdirs(self):
        for i in self.subdirs:
            yield i

    def get_ancestry(self):
        path = []
        parent = self
        while parent:
            path.insert(0, parent)
            parent = parent.parent
        return path


    def get_path(self):
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return path

    def get_output_root(self):
        if self.output_root is not None:
            return self.output_root
        else:
            return self.parent.get_output_root()
        
    def get_output_path(self):
        root = self.get_output_root()
        return os.path.join(root, *self.get_path()[1:])
    
    def get_upload_path(self):
        root = ':'.join([CONF.get('target', 'host'),
                         CONF.get('target', 'upload')])
        return '/'.join([root.strip('/')] + list(self.get_path()[1:]))

    def get_url(self):
        url = urlparse.urljoin(self.home.get_url(),
                               '/'.join(self.get_path()[1:]))
        if not os.path.isdir(self.get_output_path()):
            url = '%s.html' % url
        return url    
            
    def render(self):
        page = Page(self)
        return page.renderSynchronously()
        
    def write(self):
        op = self.get_output_path()
        if op.endswith('.html'):
            output_path = op
        else:
            output_path = os.path.join(op, 'index.html')
            if not os.path.exists(op):
                os.mkdir(op)
        f = open(output_path, 'w')
        #f = sys.stdout
        f.write(self.render())
        f.close()
        for item in self.get_items():
            item.write()
        for item in self.get_subdirs():
            item.write()
        self.upload()
    
    def upload(self):
        def _popen(args):
            return subprocess.Popen(args, stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT)
        def _rmkdir(dirname):
            dirargs = ['ssh', CONF.get('target', 'host'),
                       'mkdir %s' % dirname]
            return _popen(dirargs).stdout.read().strip()
        def _rcp(src, dst):
            fileargs = ['scp', src, dst]
            return _popen(fileargs).stdout.read().strip()
        outputpath = self.get_output_path()
        uploadpath = self.get_upload_path()
        if os.path.isdir(outputpath):
            _rmkdir(uploadpath.split(':')[-1])
            outputpath = '%s/index.html' % outputpath
            uploadpath = '%s/index.html' % uploadpath
        print outputpath, uploadpath
        _rcp(outputpath, uploadpath)
            
    def load_rst(self):
        if self.path.endswith('.rst'):
            path = self.path
        else:
            path = os.path.join(self.path, 'index.rst')
        try:
            f = open(path)
            rst = f.read()
            f.close()
        except:
            rst = ''
        template = Template(rst)
        self.rst = template.substitute(
            imagedir=CONF.get('resources', 'imagedir'))
        parts = publish_parts(source=self.rst,
                              writer_name='html')
        self.title = parts['title']
        if not self.title:
            self.title = self.name.capitalize()
        self.body = parts['body']
        
        
   
   
class Directory(Model):

    def __init__(self, parent, path, home):
        Model.__init__(self, parent, path, home)
        l = os.listdir(self.path)
        l.sort()
        self.items = [i for i in self._load_items(l)]
        self.subdirs = [i for i in self._load_subdirs(l)]
        self.load_rst()
        
    def _load_items(self, l):
        for p in l:
            if p.endswith('.rst') and p != 'index.rst':
                path = os.path.join(self.path, p)
                yield Item(self, path, self.home)
    
    def _load_subdirs(self, l):
        for p in l:
            if p.startswith('.'):
                continue
            path = os.path.join(self.path, p)
            if os.path.isdir(path):
                yield Directory(self, path, self.home)


class Item(Model):

    def __init__(self, parent, path, home):
        Model.__init__(self, parent, path, home)
        self.name = os.path.basename(path).replace('.rst', '')
        self.load_rst()
        
        
    def get_output_path(self):
        return '%s.html' % super(Item, self).get_output_path()
        
    def get_upload_path(self):
        return '%s.html' % super(Item, self).get_upload_path()

        
class Home(Directory):

    def __init__(self):
        self.parent = None
        self.home = self
        self.name = 'home'
        self.path = 'index.rst'
        self.output_root = CONF.get('target', 'directory')
        self.url_root = CONF.get('target', 'baseurl')
        if not os.path.exists(self.output_root):
            os.mkdir(self.output_root)
        self.config = True
        self.items = [i for i in self._load_items()]
        self.subdirs = []
        self.load_rst()
    
        
   
    def get_url(self):
        return self.url_root
    
    def _load_items(self):
        for module in CONF.get('modules', 'dirs').split(','):
            yield Directory(self, module, self)
        yield Link('https://launchpad.net/products/pida/+bugs', 'bugs')
        
    #def get_output_path(self):
    #    return os.path.join(self.output_root, 'index.html')
        



def render_page(page):
    return page.renderSynchronously()
    

def write_page(page, fd=sys.stdout):
    fd.write(render_page(page))
    fd.flush()

class Link(object):

    def __init__(self, url, text):
        self.url = url
        self.title = text
        
    def get_url(self):
        return self.url
        
    def write(self):
        pass
        
    

home = Home()
home.write()
#print [i for i in home.news.get_items()]
#print [i for i in home.news.get_items()]










