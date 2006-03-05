#! /bin/sh

rm -rf run
mkdir run
PYTHONPATH="run:$PYTHONPATH"
echo "[egg_info]" > setup.cfg
echo "tag_svn_revision = true" >> setup.cfg
python setup.py develop --install-dir=run --script-dir=run 2>&1>run/buildlog.log
rm setup.cfg
grep '^Version:' pida.egg-info/PKG-INFO | cut -d' ' -f2- > pida/data/version
run/pida $*
