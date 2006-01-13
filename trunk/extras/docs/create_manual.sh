rm -rf ../../docs/manual-html
latex2html pidamanual.tex -local_icons -verbosity 0 -ascii_mode
mv pidamanual ../../docs/manual-html
cp pidamanual.css ../../docs/manual-html
