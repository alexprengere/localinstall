#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Expose function to install and import locally.

This piece of code is used to install on the fly
a package locally. It can be useful to use third party
modules on environment where you can deploy code but do
have direct ssh access to install stuff. For example to
run streaming jobs in Python on a Hadoop cluster::

    >>> from local_install import install
    >>> pytz = install('pytz')

Test it::

    >>> NO_PYTZ = pytz is None

This requires *pip*.
"""

import sys
import os
import pip
from tempfile import mkdtemp

CWD = os.getcwd()


def install(package, url=None, build_dir=None, target_dir=None, verbose=True):
    """Install package and import it locally.

    The package is returned if successful, None if failure.
    """
    if url is None:
        url = package

    if build_dir is None:
        build_dir = os.path.abspath(mkdtemp(dir=CWD))

    if target_dir is None:
        target_dir = os.path.abspath(mkdtemp(dir=CWD))

    # Add non existent directories to sys.path may lead
    # to unexpected behavior
    # mkdtemp() calls will create the directory, but the check is still
    # useful for user-given target directories
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    if target_dir not in sys.path:
        sys.path.insert(0, target_dir)

    try:
        p = __import__(package)

    except ImportError:
        print >> sys.stderr, "Could not import at first. Installing %s in %s..." % \
            (package, target_dir)

        # This will create an egg in local site-packages
        # We could have used setuptools.command.main instead of pip.main,
        # but some versions of easy_install are too old to support the
        # different options.
        # We do not use the --user option of pip, because we may not have
        # writing rights on the user sitepackage
        # stdout is temporarily redirect to stderr to avoid polluting stdout
        # (useful for Hadoop jobs)
        if verbose:
            sys.stdout = sys.__stderr__
        else:
            sys.stdout = open(os.devnull, 'w')

        pip.main(['install', url,
                  '--build', build_dir,
                  '--target', target_dir])

        sys.stdout = sys.__stdout__

        # Testing now
        try:
            p = __import__(package)

        except ImportError:
            p = None
            print >> sys.stderr, "Could not import %s!" % package
        else:
            print >> sys.stderr, "%s successfully imported after installation." % package

    else:
        print >> sys.stderr, "%s successfully imported without doing anything." % package

    # Cleaning
    del sys.path[0]
    return p


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description="Local installer of packages.")

    parser.add_argument("package_name", help="Package name")

    parser.add_argument("-b", "--build",
                        help="""
                        Build directory. Default is a temporary directory.
                        """,
                        default=None)

    parser.add_argument("-t", "--target",
                        help="""
                        Target directory. Default is a temporary directory.
                        """,
                        default=None)

    parser.add_argument("-u", "--url",
                        help="""
                        Url. Installer will use the package name unless this
                        argument is given.
                        """,
                        default=None)

    parser.add_argument("-q", "--quiet",
                        help="""
                        Hide installation messages.
                        """,
                        action='store_true')

    args = parser.parse_args()

    install(package=args.package_name,
            url=args.url,
            build_dir=args.build,
            target_dir=args.target,
            verbose=not args.quiet)
