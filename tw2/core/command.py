from __future__ import print_function

import errno
import re
import operator
import shutil
import sys
import os
import stat
import tempfile
import subprocess
import mimetypes
from functools import reduce
import six
from six.moves import map
from six.moves import zip

try:
    from hashlib import md5
except ImportError:
    import md5

try:
    from cStringIO import StringIO
except ImportError:
    from six import StringIO

import pkg_resources
from setuptools import Command
from distutils import log

from tw2.core import core
from tw2.core import widgets
from tw2.core import middleware


def request_local_fake():
    global _request_local, _request_id
    if _request_local == None:
        _request_local = {}
    try:
        return _request_local[_request_id]
    except KeyError:
        rl_data = {}
        _request_local[_request_id] = rl_data
        return rl_data

core.request_local = request_local_fake
_request_local = {}
_request_id = 'whatever'


class archive_tw2_resources(Command):
    """
    Setuptools command to copy and optionally compress all static resources
    from a series of distributions and their dependencies into a directory
    where they can be served by a fast web server.

    To enable compression of CSS and JS files you will need to have installed a
    Java Runtime Environment and YUICompressor
    (http://www.julienlecomte.net/yuicompressor)

    In order for resources from widget eggs to be properly collected these
    need to have a 'tw2.widgets' 'widgets' entry-point which points
    to a module which, when imported, instantiates all needed JS and CSS Links.

    The result is laid out in the output directory in such a way that when
    a web server such as Apache or Nginx is configured to map URLS that
    begin with /resources to that directory static files will be served
    from there bypassing python completely.


    To integrate this command into your build process you can add these lines
    to ``setup.cfg``::

        [archive_tw2_resources]
        output = /home/someuser/public_html/resources/
        compresslevel = 2
        distributions = MyProject
        yuicompressor = /home/someuser/bin/yuicompressor.jar
        onepass = true

        [aliases]
        deploy = archive_tw2_resources --force install

    This way you can run::

        $ python setup.py deploy

    To install a new version of your app and copy/compress resources.
    """
    description = "Copies ToscaWidgets static resources into a directory "\
                  "where a fast web-server can serve them."
    user_options = [
        ("output=", "o",
         "Output directory. If it doesn't exist it will be created."),
        ("force", "f", "If output dir exists, it will be ovewritten"),
        ("onepass", None, "If given, yuicompressor will only be called once "\
                          "for each kind of file with a all files "\
                          "together and then separated back into smaller "\
                          "files"),
        ("compresslevel=", "c",
         "Compression level: 0) for no compression (default). "\
                            "1) for js-minification. "\
                            "2) for js & css compression"),
        ("yuicompressor=", None, "Name of the yuicompressor jar."),
        ("distributions=", "d",
         "List of widget dists. to include resources from "
         "(dependencies will be handled recursively). Note that "
         "these distributions need to define a 'tw2.widgets' "
         "'widgets' entrypoint pointing to a a module where "
         "resources are located."),
        ]

    IGNORED_NAMES = [".svn", ".git", ".hg"]
    """
    A list of names to ignore, used to prevent collecting
    subversion control data.
    """

    def initialize_options(self):
        self.output = ''
        self.force = False
        self.onepass = False
        self.compresslevel = 0
        self.distributions = []
        self.yuicompressor = 'yuicompressor.jar'

    def finalize_options(self):
        self.ensure_string("output")
        self.ensure_string("yuicompressor")
        self.ensure_string_list("distributions")
        self.compresslevel = int(self.compresslevel)
        self.yuicompressor = os.path.abspath(self.yuicompressor)

    def run(self):
        if not self.output:
            print("Need to specify an output directory", file=sys.stderr)
            return
        if not self.distributions:
            print("Need to specify at least one distribution", file=sys.stderr)
            return
        if os.path.exists(self.output) and not self.force:
            print((
                "Destination dir %s exists. " % self.output) + \
               "Use -f to overwrite.", file=sys.stderr)
            return
        if self.compresslevel > 0 and not os.path.exists(self.yuicompressor):
            print("Could not find YUICompressor at " + \
                                 self.yuicompressor, file=sys.stderr)
            return

        self.tempdir = tempdir = tempfile.mktemp()
        self.execute(os.makedirs, (tempdir,), "Creating temp dir %s" % tempdir)

        if self.compresslevel > 0:
            if self.onepass:
                self.writer = OnePassCompressingWriter(self, tempdir)
            else:
                self.writer = CompressingWriter(self, tempdir)
        else:
            self.writer = FileWriter(self, tempdir)

        self.execute(self._copy_resources, tuple(), "Extracting resources")
        self.writer.finalize()
        if os.path.exists(self.output):
            self.execute(shutil.rmtree, (self.output,),
                         "Deleting old output dir %s" % self.output)
        self.execute(os.makedirs, (self.output,), "Creating output dir")

        prefix = '/resources'   # TODO -- get this from config.

        final_dest = os.path.join(self.output, prefix.strip('/'))
        self.execute(shutil.move, (tempdir, final_dest),
                     "Moving build to %s" % final_dest)

    def _load_widgets(self, mod):
        """ Register the widgets' resources with the middleware. """
        print("Doing", mod.__name__)
        for key, value in six.iteritems(mod.__dict__):
            if isinstance(value, widgets.WidgetMeta):
                try:
                    value(id='fake').req().prepare()
                except Exception:
                    self.announce("Failed to register %s" % key)

                for res in value.resources:
                    try:
                        res.req().prepare()
                    except Exception:
                        self.announce("Failed to register %s" % key)

    def _load_widget_entry_points(self, distribution):
        try:
            dist = pkg_resources.get_distribution(distribution)
            requires = [r.project_name for r in dist.requires()]

            map(self._load_widget_entry_points, requires)

            #Here we only look for a [tw2.widgets] entry point listing and we
            #don't care what data is listed in it.  We do this, because many of
            #the existing tw2 libraries do not conform to a standard, e.g.:
            #
            #    ## Doing it wrong:
            #    [tw2.widgets]
            #    tw2.core = tw2.core
            #
            #    ## Doing it right:
            #    [tw2.widgets]
            #    widgets = tw2.jquery
            #
            #For now, anything with a [tw2.widgets] listing at all is loaded.
            #TODO -- this should be resolved and standardized in the future.

            for ep in pkg_resources.iter_entry_points('tw2.widgets'):
                if ep.dist == dist:
                    mod = ep.load()
                    self._load_widgets(mod)
                    self.announce("Loaded %s" % mod.__name__)

        except ImportError as e:
            self.announce("%s has no widgets entrypoint" % distribution)

    def _copy_resources(self):

        # Set up fake middleware with which widgets can register their
        # resources
        core.request_local = request_local_fake
        core.request_local()['middleware'] = middleware.make_middleware()

        # Load widgets and have them prepare their resources
        map(self._load_widget_entry_points, self.distributions)

        rl_resources = core.request_local().setdefault('resources', [])

        for resource in rl_resources:
            try:
                modname = resource.modname
                fbase = resource.filename.split('/')[0]
                self.execute(self._copy_resource_tree, (modname, fbase),
                             "Copying %s recursively into %s" %
                             (modname, self.writer.base))
            except AttributeError as e:
                pass

    def _copy_resource_tree(self, modname, fname):
        try:
            for name in pkg_resources.resource_listdir(modname, fname):
                if name in self.IGNORED_NAMES:
                    continue
                name = '/'.join((fname, name))
                rel_name = '/'.join((modname, name))
                if pkg_resources.resource_isdir(modname, name):
                    self.execute(self._copy_resource_tree, (modname, name),
                                 "Recursing into " + rel_name)
                else:
                    full_name = pkg_resources.resource_filename(modname, name)
                    ct, _ = mimetypes.guess_type(full_name)
                    stream = pkg_resources.resource_stream(modname, name)
                    filename = '/'.join((modname, name))
                    self.execute(self.writer.write_file, (stream, filename),
                                 "Processing " + filename)
                    stream.close()
        except OSError as e:
            if e.errno == errno.ENOENT:
                self.warn("Could not copy %s" % repr((modname, fname, e)))


class FileWriter(object):
    def __init__(self, cmd, base):
        self.base = base
        self.cmd = cmd

    def finalize(self):
        pass

    def write_file(self, stream, path):
        final = os.path.join(self.base, path)
        if not os.path.exists(os.path.dirname(final)):
            os.makedirs(os.path.dirname(final))
        dest = open(final, 'wb')
        self.announce("Writing %s" % path)
        shutil.copyfileobj(stream, dest)
        dest.close()

    # Delegate methods to Command
    for name in "warn announce error execute".split():
        exec("""\
def %(name)s(self, *args, **kw):
    return self.cmd.%(name)s(*args, **kw)
""" % locals())


class CompressingWriter(FileWriter):

    def __init__(self, *args, **kw):
        super(CompressingWriter, self).__init__(*args, **kw)
        self.counters = 0, 0

    def finalize(self):
        try:
            avg = reduce(operator.truediv, self.counters) * 100
            msg = "Total JS&CSS compressed size is %.2f%% of original" % avg
            self.announce(msg)
        except ZeroDivisionError:
            # No files were compressed
            pass

    def compress(self, stream, path):
        typ = path.split('.')[-1]
        if typ not in ('css', 'js'):
            return stream
        args = ['java', '-jar', self.cmd.yuicompressor, '--type', typ]
        if self.cmd.compresslevel < 2:
            args.append('--nomunge')
        args.append('--charset=utf8')
        p = subprocess.Popen(args, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.announce("Compressing %s" % path)
        buffer = StringIO()
        shutil.copyfileobj(stream, buffer)
        data = buffer.getvalue()
        if not data:
            return buffer
        stdout, stderr = p.communicate(data)
        if p.returncode != 0:
            self.warn("Failed to compress %s: %d" % (path, p.returncode))
            self.warn("File will be copied untouched")
            sys.stderr.write(stderr)
            sys.stderr.write(stdout)
            stream.seek(0)
        else:
            count = len(stdout), len(data)
            ratio = reduce(operator.truediv, count)
            self.counters = map(sum, zip(self.counters, count))
            msg = "Compressed %s (New size: %.2f%%)" % (path, ratio * 100)
            self.announce(msg)
            stream = StringIO(stdout)
        return stream

    def write_file(self, stream, path):
        stream = self.compress(stream, path)
        return super(CompressingWriter, self).write_file(stream, path)


class OnePassCompressingWriter(CompressingWriter):
    def __init__(self, *args, **kw):
        super(OnePassCompressingWriter, self).__init__(*args, **kw)
        #XXX This comment trick only works with JS as of YUICompressor 2.3.5
        self._caches = {'js': StringIO()}
        self._marker = "/*! MARKER #### %(path)s #### MARKER */"
        regexp = r"^\/\* MARKER #### (?P<path>.*?) #### MARKER \*\/$"
        self._re = re.compile(regexp)

    def _demultiplex(self, stream):
        cur_file = None
        buffer = StringIO()
        stream.seek(0)
        for line in stream:
            m = self._re.match(line)
            if m:
                if cur_file:
                    buffer.seek(0)
                    FileWriter.write_file(self, buffer, cur_file)
                    buffer.truncate(0)
                cur_file = m.group('path')
            else:
                buffer.write(line)

    def finalize(self):
        self.announce("Compressing all defered files")
        for typ, cache in six.iteritems(self._caches):
            cache.seek(0)
            # self.compress only wants to know the file extension to see
            # what kind of file it is, we pass a dummy one
            compressed = self.compress(cache, '__defered__.' + typ)
            self._demultiplex(compressed)
        super(OnePassCompressingWriter, self).finalize()

    def write_file(self, stream, path):
        typ = path.split('.')[-1]
        cache = self._caches.get(typ)
        if not cache:
            self.announce("Will not consider %s for onepass" % path)
            return CompressingWriter.write_file(self, stream, path)
        print(self._marker % locals(), file=cache)
        self.announce("Defering %s for compression in one pass" % path)
        shutil.copyfileobj(stream, cache)
