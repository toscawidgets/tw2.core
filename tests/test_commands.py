"""
filling in the missing gaps in test coverage
"""
from unittest import TestCase
import distutils.dist
import StringIO
import sys
import os
import shutil
import tempfile

from nose.tools import eq_

import tw2.core.core as core
import tw2.core.middleware as middleware

TMP_DIR = tempfile.mkdtemp(suffix='tmp_test_out1')
OUT_DIR = tempfile.mkdtemp(suffix='tmp_test_out2')

class StdOut(StringIO.StringIO):
     def __init__(self,stdout):
         self.__stdout = stdout
         StringIO.StringIO.__init__(self)

     def write(self,s):
         self.__stdout.write(s)
         StringIO.StringIO.write(self,s)

     def read(self):
         self.seek(0)
         stuff = StringIO.StringIO.read(self)
         self.__stdout.write(stuff)
         return stuff

class TestErrors(TestCase):
    def setUp(self):
        import tw2.core.command
        o = StdOut(sys.stdout)
        e = StdOut(sys.stderr)
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = o
        sys.stderr = e
        d = distutils.dist.Distribution()
        self.c = tw2.core.command.archive_tw2_resources(d)
        try:
            shutil.rmtree(OUT_DIR)
        except Exception, e:
            pass
        os.mkdir(OUT_DIR)

    def tearDown(self):
        sys.stdout = self._stdout
        sys.stderr = self._stderr
        shutil.rmtree(OUT_DIR)

    def test_init_options(self):
        self.c.initialize_options()
        assert(self.c.output == '')
        assert(self.c.force == False)
        assert(self.c.onepass == False)
        assert(self.c.compresslevel == 0)
        assert(self.c.distributions == [])
        assert(self.c.yuicompressor == 'yuicompressor.jar')

    def test_finalize_options(self):
        self.c.initialize_options()
        self.c.finalize_options()

    def test_finalize_options_fail(self):
        self.c.initialize_options()
        self.c.compresslevel = 'not-an-int'
        try:
            self.c.finalize_options()
            assert(False)
        except ValueError, e:
            assert(
                str(e) == "invalid literal for int() with base 10: 'not-an-int'"
            )

    def test_no_output(self):
        self.c.initialize_options()
        self.c.finalize_options()
        self.c.run()
        assert(sys.stderr.read().strip() == "Need to specify an output directory")

    def test_no_distributions(self):
        self.c.initialize_options()
        self.c.finalize_options()
        self.c.output = OUT_DIR
        self.c.run()
        assert(sys.stderr.read().strip() == "Need to specify at least one distribution")

    def test_no_compressor(self):
        self.c.initialize_options()
        self.c.finalize_options()
        self.c.output = OUT_DIR
        self.c.force = True
        self.c.distributions = ['tw2.core']
        self.c.compresslevel = 1
        self.c.run()
        output = sys.stderr.read().strip()
        target = "Could not find YUICompressor at %s" % self.c.yuicompressor
        assert(output == target)

    def test_no_force_overwrite(self):
        self.c.initialize_options()
        self.c.finalize_options()
        self.c.output = OUT_DIR
        self.c.distributions = ['tw2.core']
        self.c.run()
        output = sys.stderr.read().strip()
        target = "Destination dir %s exists. Use -f to overwrite." % \
            OUT_DIR
        assert(output == target)

class TestArchive(TestCase):
    def setUp(self):
        import tw2.core.command
        o = StdOut(sys.stdout)
        e = StdOut(sys.stderr)
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = o
        sys.stderr = e
        d = distutils.dist.Distribution()
        self.c = tw2.core.command.archive_tw2_resources(d)

        try:
            shutil.rmtree(OUT_DIR)
        except Exception, e:
            pass

        self.c.initialize_options()
        self.c.finalize_options()
        self.c.output = OUT_DIR
        self.c.force = True
        self.c.distributions = ['tw2.forms']
        os.mkdir(OUT_DIR)

        # Set up fake middleware with which widgets can register their resources
        core.request_local = tw2.core.command.request_local_fake
        core.request_local()['middleware'] = middleware.make_middleware()
        try:
            core.request_local()['resources'] = []
        except Exception, e:
            pass

    def tearDown(self):
        sys.stdout = self._stdout
        sys.stderr = self._stderr

        try:
            shutil.rmtree(OUT_DIR)
        except Exception, e:
            pass

        try:
            shutil.rmtree(TMP_DIR)
        except Exception, e:
            pass

    def test_load_widgets(self):
        import tw2.forms.widgets
        import tw2.core
        self.c._load_widgets(tw2.forms.widgets)
        rl_resources = core.request_local().setdefault('resources', [])
        target = tw2.core.CSSLink(link="/resources/tw2.forms/static/forms.css").req()
        assert(any([
            target.link == getattr(r, 'link', None) for r in rl_resources
        ]))

    def test_load_no_widgets(self):
        import tw2.core.widgets
        self.c._load_widgets(tw2.core.widgets)
        rl_resources = core.request_local().setdefault('resources', [])
        assert(len(rl_resources) == 0)

    def test_load_entry_points(self):
        self.c._load_widget_entry_points('tw2.forms')
        rl_resources = core.request_local().setdefault('resources', [])
        eq_(len(rl_resources), 4)

    def test_render_entry_points(self):
        self.c._load_widget_entry_points('tw2.forms')
        rl_resources = core.request_local().setdefault('resources', [])

        import pprint
        print pprint.pformat(rl_resources)

    def test_copy_tree(self):
        import tw2.core.command
        self.c._load_widget_entry_points('tw2.forms')
        rl_resources = core.request_local().setdefault('resources', [])
        self.c.writer = tw2.core.command.FileWriter(self.c, TMP_DIR)
        self.c._copy_resource_tree(
            rl_resources[-1].modname,
            rl_resources[-1].filename.split('/')[0],
        )
        assert(os.path.isdir(TMP_DIR))
        assert(os.path.isdir(
            '/'.join([TMP_DIR, 'tw2.forms'])
        ))
        assert(os.path.isdir(
            '/'.join([TMP_DIR, 'tw2.forms', 'static'])
        ))
        assert(os.path.isfile(
            '/'.join([TMP_DIR, 'tw2.forms', 'static', 'edit-undo.png'])
        ))

    def test_full_run(self):
        self.c.run()
        assert(not os.path.isdir(TMP_DIR))
        assert(os.path.isdir(OUT_DIR))
        assert(os.path.isfile(
            '/'.join([
                OUT_DIR, 'resources', 'tw2.forms', 'static', 'edit-undo.png'
            ])
        ))

    def test_one_pass(self):
        import yuicompressor
        self.c.yuicompressor = yuicompressor.get_jar_filename()
        self.c.compresslevel = 1
        self.c.onepass = True
        self.c.run()
        assert(not os.path.isdir(TMP_DIR))
        assert(os.path.isdir(OUT_DIR))
        assert(os.path.isfile(
            '/'.join([
                OUT_DIR, 'resources', 'tw2.forms', 'static', 'edit-undo.png'
            ])
        ))
        # TODO  Might be nice to check and see if the file is really compressed

    def test_many_pass_compress(self):
        import yuicompressor
        self.c.yuicompressor = yuicompressor.get_jar_filename()
        self.c.compresslevel = 1
        self.c.run()
        assert(not os.path.isdir(TMP_DIR))
        assert(os.path.isdir(OUT_DIR))
        assert(os.path.isfile(
            '/'.join([
                OUT_DIR, 'resources', 'tw2.forms', 'static', 'edit-undo.png'
            ])
        ))
        # TODO  Might be nice to check and see if the file is really compressed
