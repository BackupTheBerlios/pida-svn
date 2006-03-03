#! /bin/sh

rm -rf run
mkdir run
PYTHONPATH="run:$PYTHONPATH"
python setup.py develop --install-dir=run --script-dir=run 2>&1>run/buildlog.log
run/pida $*
