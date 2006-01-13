rm -rf ../../docs/html
latex2html pidamanual.tex -local_icons -verbosity 0 -ascii_mode
mv pidamanual ../../docs/html
cp pidamanual.css ../../docs/html
