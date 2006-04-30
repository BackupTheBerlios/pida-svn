#! /bin/sh

# don't accept errors
set -e

# detect the real location of the working copy
if type -p readlink > /dev/null; then
	ME=$( readlink -f "$0" )
else
	ME="$0"
fi
PIDADIR=$( cd "${ME%/*}"; pwd )
unset ME

if [ "$1" == "--update" ]; then
	echo "Updating $PIDADIR..."
	shift;
	svn up "$PIDADIR"
fi

(
	echo "Building pida..."

	rm -rf "$PIDADIR/run"
	mkdir -p "$PIDADIR/run"

	PYTHONPATH="$PIDADIR/run:$PYTHONPATH"
	cat <<-EOT > "$PIDADIR/setup.cfg"
	[egg_info]
	tag_svn_revision = true
	EOT

	cd "$PIDADIR"
	python setup.py develop --install-dir=run --script-dir=run 2>&1>run/buildlog.log
	rm setup.cfg
	grep '^Version:' pida.egg-info/PKG-INFO | cut -d' ' -f2- > pida/data/version
)

echo "Starting..."
python2.4 "$PIDADIR/run/pida" $*
