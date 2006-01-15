#! /usr/bin/python

import os

rst_dir = 'rst'
html_dir = 'html'

rst2html_command = 'rst2html'

def chdir():
    os.chdir('docs')

def main():
    chdir()
    for name in os.listdir(rst_dir):
        if name.endswith('.rst'):
            in_path = os.path.join(rst_dir, name)
            out_path = os.path.join(html_dir,
                                    name.replace('.rst', '.html'))
            os.system('%s %s > %s' % (rst2html_command,
                                      in_path, out_path))


if __name__ == '__main__':
    main()

#cd ../../docs
#rst2latex rst/pida-manual.rst > html/pida-manual.html
