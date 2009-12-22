"""
This was whole-sale stolen from turbogears2  (gotta love MIT)

a reimplementation of the mako template loader
that supports dotted names
"""
import os
import stat

from mako.template import Template
from pkg_resources import ResourceManager
import core
from mako import exceptions

rm = ResourceManager()
try:
    import threading
except ImportError:
    import dummy_threading as threading


class DottedTemplateLookup(object):
    """Mako template lookup emulation that supports
    zipped applications and dotted filenames.

    This is an emulation of the Mako template lookup that will handle
    get_template and support dotted names in Python path notation
    to support zipped eggs.

    This is necessary because Mako asserts that your project will always
    be installed in a zip-unsafe manner with all files somewhere on the
    hard drive.
    
    This is not the case when you want your application to be deployed
    in a single zip file (zip-safe). If you want to deploy in a zip
    file _and_ use the dotted template name notation then this class
    is necessary because it emulates files on the filesystem for the
    underlying Mako engine while they are in fact in your zip file.

    """

    def __init__(self, input_encoding, output_encoding,
            imports, default_filters):

        self.input_encoding = input_encoding
        self.output_encoding = output_encoding
        self.imports = imports
        self.default_filters = default_filters
        # implement a cache for the loaded templates
        self.template_cache = dict()
        # implement a cache for the filename lookups
        self.template_filenames_cache = dict()

        # a mutex to ensure thread safeness during template loading
        self._mutex = threading.Lock()

    def __check(self, template):
        """private method used to verify if a template has changed
        since the last time it has been put in cache...

        This method being based on the mtime of a real file this should
        never be called on a zipped deployed application.

        This method is a ~copy/paste of the original caching system from
        the Mako lookup loader.

        """
        if template.filename is None:
            return template

        if not os.path.exists(template.filename):
            # remove from cache.
            self.template_cache.pop(template.filename, None)
            raise exceptions.TemplateLookupException(
                    "Cant locate template '%s'" % template.filename)

        elif template.module._modified_time < os.stat(
                template.filename)[stat.ST_MTIME]:

            # cache is too old, remove old template
            # from cache and reload.
            self.template_cache.pop(template.filename, None)
            return self.__load(template.filename)

        else:
            # cache is correct, use it.
            return template

    def __load(self, filename):
        """real loader function. copy paste from the mako template
        loader.

        """
        # make sure the template loading from filesystem is only done
        # one thread at a time to avoid bad clashes...
        self._mutex.acquire()
        template_name = filename
        try:
            if not template_name.endswith('.mak'):
                split = template_name.rsplit('.', 1)
                filename = rm.resource_filename(split[0], split[1]+'.mak')

            self.template_cache[template_name] = Template(open(filename).read(),
                filename=filename,
                input_encoding=self.input_encoding,
                output_encoding=self.output_encoding,
                default_filters=self.default_filters,
                imports=self.imports,
                lookup=self)

            return self.template_cache[template_name]
        finally:
            # _always_ release the lock once done to avoid
            # "thread lock" effect
            self._mutex.release()
            pass

    def adjust_uri(self, uri, relativeto):
        return os.path.join(os.path.dirname(relativeto), uri)

    def get_template(self, template_name):
        """this is the emulated method that must return a template
        instance based on a given template name
        """

        if not self.template_cache.has_key(template_name):
            # the template string is not yet loaded into the cache.
            # Do so now
            self.__load(template_name)

        try:
            # AUTO RELOADING will be activated only if user has
            # explicitly asked for it in the configuration
            # return the template, but first make sure it's not outdated
            # and if outdated, refresh the cache.
            if getattr(core.request_local()['middleware'].config, 'auto_reload_templates', False):
                return self.__check(self.template_cache[template_name])
        except (AttributeError, KeyError):
            pass

        return self.template_cache[template_name]
    
    load_template = get_template
    
