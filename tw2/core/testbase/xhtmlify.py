#!/usr/bin/env python
"""An HTML to XHTML converter.


This code is from Tom Lynn
http://www.fish.cx/pytest/wsgi/xhtmlify.py

MIT Licensed
"""
from __future__ import print_function
import re
from six.moves import html_entities as htmlentitydefs

NAME_RE = r'[_a-zA-Z\-][:_a-zA-Z0-9\-]*'
BAD_ATTR_RE = r'''[^<>\s"'][^<>\s]*'''
ATTR_RE = r'''%s\s*(?:=\s*(?:".*?"|'.*?'|%s))?''' % (NAME_RE, BAD_ATTR_RE)
CDATA_RE = r'<!\[CDATA\[.*?\]\]>'
COMMENT_RE = r'<!--.*?-->|<!\s*%s.*?>' % NAME_RE  # comment or doctype-alike
TAG_RE = r'%s|%s|<([^<>]*?)>|<' % (COMMENT_RE, CDATA_RE)
INNARDS_RE = r'(%s\s*(?:%s\s*)*(/?)\Z)|(/%s\s*\Z)|(\?.*)|(.*)' % (
                 NAME_RE, ATTR_RE, NAME_RE)

SELF_CLOSING_TAGS = ['br', 'hr', 'input', 'img', 'meta',
                     'spacer', 'link', 'frame', 'base']  # from BeautifulSoup
CDATA_TAGS = ['script']
STRUCTURAL_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'blockquote', 'div', 'td',
                   'ul', 'ol', 'li', 'body']  # deliberately excluding <p>


class ValidationError(Exception):
    def __init__(self, message, line, offset):
        message = message + ' at line %d, column %d' % (line, offset)
        self.line = line
        self.offset = offset
        super(ValidationError, self).__init__(message)


def ampfix(value):
    """Replaces ampersands in value that aren't part of an HTML entity.
    Adapted from <http://effbot.org/zone/re-sub.htm#unescape-html>."""
    def fixup(m):
        text = m.group(0)
        if text == '&':
            pass
        elif text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    unichr(int(text[3:-1], 16))
                else:
                    unichr(int(text[2:-1], 10))
            except ValueError:
                pass
            else:
                return text  # it's well-formed
        else:
            # named entity
            try:
                return '&#%d;' % htmlentitydefs.name2codepoint[text[1:-1]]
            except KeyError:
                pass
        return '&#38;' + text[1:]
    return re.sub("&#?\w+;|&", fixup, value)


def fix_attrs(attrs):
    if not attrs:
        return ''  # most tags have no attrs, quick exit in that case
    lastpos = 0
    result = []
    output = result.append
    for m in re.compile(ATTR_RE, re.DOTALL).finditer(attrs):
        output(attrs[lastpos:m.start()])
        lastpos = m.end()
        attr = m.group()
        if '=' not in attr:
            assert re.compile(NAME_RE + r'\s*\Z').match(attr), repr(attr)
            output(re.sub('(%s)' % NAME_RE, r'\1="\1"', attr))
        else:
            name, value = attr.split('=', 1)
            if len(value) > 1 and value[0] + value[-1] in ("''", '""'):
                if value[0] not in value[1:-1]:  # preserve their quoting
                    output('%s=%s' % (name, ampfix(value)))
                    continue
                value = value[1:-1]
            output('%s="%s"' % (name, ampfix(value.replace('"', '&quot;'))))
    output(attrs[lastpos:])
    return ''.join(result)


def xhtmlify(html, self_closing_tags=SELF_CLOSING_TAGS,
                   cdata_tags=CDATA_TAGS):
    """
    Parses HTML and converts it to XHTML-style tags.
    Throws a ValidationError if the tags are badly nested or malformed.
    It is slightly stricter than normal HTML in some places and more lenient
    in others, but it generally behaves in a human-friendly way.
    It is intended to be idempotent, i.e. it should make no changes if fed its
    own output. This implies that it accepts XHTML-style self-closing tags.
    """
    for tag in cdata_tags:
        assert tag not in self_closing_tags
    tags = []
    result = []
    output = result.append
    lastpos = 0
    tag_re = re.compile(TAG_RE, re.DOTALL | re.IGNORECASE)
    cdata_re = re.compile('(%s)' % CDATA_RE, re.DOTALL)
    for tag_match in tag_re.finditer(html):
        pos = tag_match.start()
        line = html.count('\n', 0, pos) + 1
        offset = pos - html.rfind('\n', 0, pos)
        prevtag = tags and tags[-1][0].lower() or None
        innards = tag_match.group(1)
        if innards is None:
            if tag_match.group().startswith('<!'):
                continue  # CDATA, treat it as text
            assert tag_match.group() == '<'
            if prevtag in cdata_tags:
                continue  # ignore until we have all the text
            else:
                raise ValidationError('Unescaped "<" or unfinished tag',
                                      line, offset)
        elif not innards:
            raise ValidationError("Empty tag", line, offset)
        text = html[lastpos:pos]
        if prevtag in cdata_tags:
            for i, match in enumerate(cdata_re.split(text)):
                if i % 2 == 1 or not re.search('[<>&]', match):
                    output(match)  # already <![CDATA[...]]> or safe
                else:
                    output('<![CDATA[%s]]>' % match)
        else:
            output(ampfix(text))
        m = re.compile(INNARDS_RE, re.DOTALL).match(innards)
        if prevtag in cdata_tags and (not m.group(3) or
            re.match(r'/(\w+)', innards).group(1).lower() != prevtag):
            # not the closing tag, output it as CDATA
            output('<![CDATA[%s]]>' % tag_match.group())
        elif m.group(1):  # opening tag
            endslash = m.group(2)
            m = re.match(r'\w+', innards)
            TagName, attrs = m.group(), innards[m.end():]
            attrs = fix_attrs(attrs)
            tagname = TagName.lower()
            if prevtag in self_closing_tags:
                tags.pop()
                prevtag = tags and tags[-1][0].lower() or None
            if ((
                prevtag == 'p' and (
                    tagname == 'p' or tagname in STRUCTURAL_TAGS
                )) or
                (prevtag == 'li' and tagname == 'li')
            ):
                tags.pop()
                output('</%s>' % prevtag)
                #prevtag = tags and tags[-1][0].lower() or None
            if endslash:
                output('<%s%s>' % (tagname, attrs))
            elif tagname in self_closing_tags:
                output('<%s%s/>' % (tagname, attrs))  # preempt any closing tag
                tags.append((TagName, attrs, line, offset))
            else:
                output('<%s%s>' % (tagname, attrs))
                tags.append((TagName, attrs, line, offset))
        elif m.group(3):  # closing tag
            TagName = re.match(r'/(\w+)', innards).group(1)
            tagname = TagName.lower()
            if prevtag in self_closing_tags:
                # The tag has already been output in self-closed form.
                if prevtag == tagname:  # explicit close
                    # Minor hack: discard any whitespace we just output
                    if result[-1].strip():
                        raise ValidationError(
                            ("Self-closing tag <%s/> is not empty" %
                             tags[-1][0]), tags[-1][2], tags[-1][3])
                    else:
                        result.pop()
                else:
                    tags.pop()
                    prevtag = tags and tags[-1][0].lower() or None
                    assert prevtag not in self_closing_tags
            if (prevtag == 'p' and tagname in STRUCTURAL_TAGS) or (
                prevtag == 'li' and tagname in ('ol', 'ul')):
                output('</%s>' % prevtag)
                tags.pop()
                prevtag = tags and tags[-1][0].lower() or None
            if prevtag == tagname:
                if tagname not in self_closing_tags:
                    output(tag_match.group().lower())
                    tags.pop()
            else:
                raise ValidationError(
                    "Unexpected closing tag </%s>" % TagName, line, offset)
        elif m.group(5):  # mismatch
            raise ValidationError("Malformed tag", line, offset)
        else:
            # We don't do any validation on pre-processing tags (<? ... >).
            output(ampfix(tag_match.group()))
        lastpos = tag_match.end()
    while tags:
        tagname = tags[-1][0].lower()
        if tagname in self_closing_tags:
            tags.pop()
        else:
            raise ValidationError("Unclosed tag <%s>" % tagname, line, offset)
    output(ampfix(html[lastpos:]))
    return ''.join(result)


def test(html=None):
    from xml.etree import ElementTree as ET
    if html is None:
        import sys
        if len(sys.argv) == 2:
            html = open(sys.argv[1]).read()
        else:
            sys.exit('usage: %s HTMLFILE' % sys.argv[0])
    xhtml = xhtmlify(html)
    try:
        assert xhtml == xhtmlify(xhtml)
    except ValidationError:
        print(xhtml)
        raise
    # parse it as XML with ElementTree/expat
    xml = ET.fromstring(re.sub(r'(?si)<!--.*?-->|<!doctype\b.*?>', '', xhtml))
    if len(sys.argv) == 2:
        print(xhtml)
    return xhtml

if __name__ == '__main__':
    test()
