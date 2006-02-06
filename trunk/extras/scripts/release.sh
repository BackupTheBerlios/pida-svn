#! /bin/sh

# bail if we have no arguments
if [ $# -eq 0 ]; then
    echo "need to pass release string"
    exit 1
else
    VERSION=$1
fi

echo "Releasing PIDA! Spread the love."

# Tag the thing
REPOURI="svn+ssh://aafshar@svn.berlios.de/svnroot/repos/pida"
SRCURI="$REPOURI/trunk"
DSTURI="$REPOURI/tags/release-$VERSION"
TAGMESSAGE="Tagged release $VERSION"
svn cp -m"$TAGMESSAGE" $SRCURI $DSTURI

# Make the dist tarball
rm setup.cfg
rm data/version
python setup.py -q sdist
svn revert setup.cfg
SDIST_TARBALL="dist/pida-$VERSION.tar.gz"


# Upload to berlios
BERLIOS_URL="ftp.berlios.de"
BERLIOS_DIR="incoming"
ncftpput $BERLIOS_URL $BERLIOS_DIR $SDIST_TARBALL

#upload to pypy
python setup.py bdist_egg sdist upload


