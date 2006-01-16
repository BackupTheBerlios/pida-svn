#! /usr/bin/python

import os

rst_dir = 'rst'
html_dir = 'html'
latex_dir = 'latex'

rst2html_command = 'rst2html --toc-top-backlinks'
rst2tex_command = 'rst2latex'

def chdir():
    os.chdir('docs')

def main():
    chdir()
    for name in os.listdir(rst_dir):
        if name.endswith('.rst'):
            in_path = os.path.join(rst_dir, name)
            out_path_html = os.path.join(html_dir,
                                name.replace('.rst', '.html'))
            out_path_tex = os.path.join(latex_dir,
                                name.replace('.rst', '.tex'))
            os.system('%s %s > %s' % (rst2html_command,
                                      in_path, out_path_html))
            os.system('%s %s > %s' % (rst2tex_command,
                                      in_path, out_path_tex))


if __name__ == '__main__':
    main()

#cd ../../docs
#rst2latex rst/pida-manual.rst > html/pida-manual.html
