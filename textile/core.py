#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__copyright__ = """
Copyright (c) 2009, Jason Samsa, http://jsamsa.com/
Copyright (c) 2010, Kurt Raschke <kurt@kurtraschke.com>
Copyright (c) 2004, Roberto A. F. De Almeida, http://dealmeida.net/
Copyright (c) 2003, Mark Pilgrim, http://diveintomark.org/

Original PHP Version:
Copyright (c) 2003-2004, Dean Allen <dean@textism.com>
All rights reserved.

Thanks to Carlo Zottmann <carlo@g-blog.net> for refactoring
Textile's procedural code into a class framework

Additions and fixes Copyright (c) 2006 Alex Shiels http://thresholdstate.com/

"""

import uuid
from xml.etree import ElementTree

from textile.tools import sanitizer, imagesize
from textile.regex_strings import (align_re_s, cls_re_s, halign_re_s,
        pnct_re_s, regex_snippets, syms_re_s, table_span_re_s, valign_re_s)
from textile.utils import (encode_high, encode_html, decode_high, has_raw_text,
        is_rel_url, is_valid_url, list_type, normalize_newlines, pba,
        parse_attributes)


try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


try:
    # Python 3
    from urllib.parse import urlparse, urlsplit, urlunsplit, quote, unquote
    xrange = range
    unichr = chr
    unicode = str
except (ImportError):
    # Python 2
    from urllib import quote, unquote
    from urlparse import urlparse, urlsplit, urlunsplit


try:
    import regex as re
except ImportError:
    import re


class Textile(object):
    restricted_url_schemes = ('http', 'https', 'ftp', 'mailto')
    unrestricted_url_schemes = restricted_url_schemes + ('file', 'tel',
            'callto', 'sftp', 'data')

    btag = ('bq', 'bc', 'notextile', 'pre', 'h[1-6]', 'fn\d+', 'p', '###')
    btag_lite = ('bq', 'bc', 'p')

    note_index = 1

    doctype_whitelist = ['xhtml', 'html5']

    glyph_definitions = {
        'quote_single_open':  '&#8216;',
        'quote_single_close': '&#8217;',
        'quote_double_open':  '&#8220;',
        'quote_double_close': '&#8221;',
        'apostrophe':         '&#8217;',
        'prime':              '&#8242;',
        'prime_double':       '&#8243;',
        'ellipsis':           '&#8230;',
        'ampersand':          '&amp;',
        'emdash':             '&#8212;',
        'endash':             '&#8211;',
        'dimension':          '&#215;',
        'trademark':          '&#8482;',
        'registered':         '&#174;',
        'copyright':          '&#169;',
        'half':               '&#189;',
        'quarter':            '&#188;',
        'threequarters':      '&#190;',
        'degrees':            '&#176;',
        'plusminus':          '&#177;',
        'fn_ref_pattern':     '<sup{atts}>{marker}</sup>',
        'fn_foot_pattern':    '<sup{atts}>{marker}</sup>',
        'nl_ref_pattern':     '<sup{atts}>{marker}</sup>',
    }

    def __init__(self, restricted=False, lite=False, noimage=False,
            get_sizes=False, html_type='xhtml', rel='', block_tags=True):
        """Textile properties that are common to regular textile and
        textile_restricted"""
        self.restricted = restricted
        self.lite = lite
        self.noimage = noimage
        self.get_sizes = get_sizes
        self.fn = {}
        self.urlrefs = {}
        self.shelf = {}
        self.rel = rel
        self.html_type = html_type
        self.max_span_depth = 5
        self.span_depth = 0
        uid = uuid.uuid4().hex
        self.uid = 'textileRef:{0}:'.format(uid)
        self.linkPrefix = '{0}-'.format(uid)
        self.linkIndex = 0
        self.refCache = {}
        self.refIndex = 0
        self.block_tags = block_tags

        # We'll be searching for characters that need to be HTML-encoded to
        # produce properly valid html.  These are the defaults that work in
        # most cases.  Below, we'll copy this and modify the necessary pieces
        # to make it work for characters at the beginning of the string.
        self.glyph_search = [
            # apostrophe's
            re.compile(r"(^|\w)'(\w)", re.U),
            # back in '88
            re.compile(r"(\s)'(\d+\w?)\b(?!')", re.U),
            # single closing
            re.compile(r"(^|\S)'(?=\s|{0}|$)".format(pnct_re_s, re.U)),
            # single opening
            re.compile(r"'", re.U),
            # double closing
            re.compile(r'(^|\S)"(?=\s|{0}|$)'.format(pnct_re_s, re.U)),
            # double opening
            re.compile(r'"'),
            # ellipsis
            re.compile(r'([^.]?)\.{3}', re.U),
            # ampersand
            re.compile(r'(\s)&(\s)', re.U),
            # em dash
            re.compile(r'(\s?)--(\s?)', re.U),
            # en dash
            re.compile(r'\s-(?:\s|$)', re.U),
            # dimension sign
            re.compile(r'(\d+)( ?)x( ?)(?=\d+)', re.U),
            # trademark
            re.compile(r'\b ?[([]TM[])]', re.I | re.U),
            # registered
            re.compile(r'\b ?[([]R[])]', re.I | re.U),
            # copyright
            re.compile(r'\b ?[([]C[])]', re.I | re.U),
            # 1/2
            re.compile(r'[([]1\/2[])]', re.I | re.U),
            # 1/4
            re.compile(r'[([]1\/4[])]', re.I | re.U),
            # 3/4
            re.compile(r'[([]3\/4[])]', re.I | re.U),
            # degrees
            re.compile(r'[([]o[])]', re.I | re.U),
            # plus/minus
            re.compile(r'[([]\+\/-[])]', re.I | re.U),
            # 3+ uppercase acronym
            re.compile(r'\b([{0}][{1}]{{2,}})\b(?:[(]([^)]*)[)])'.format(
                regex_snippets['abr'], regex_snippets['acr']),
                flags=regex_snippets['mod']),
            # 3+ uppercase
            re.compile(r'({space}|^|[>(;-])([{abr}]{{3,}})([{nab}]*)'
                '(?={space}|{pnct}|<|$)(?=[^">]*?(<|$))'.format(**{ 'space':
                    regex_snippets['space'], 'abr': regex_snippets['abr'],
                    'nab': regex_snippets['nab'], 'pnct': pnct_re_s}),
                flags=regex_snippets['mod']),
        ]

        # These are the changes that need to be made for characters that occur
        # at the beginning of the string.
        self.glyph_search_initial = list(self.glyph_search)
        # apostrophe's
        self.glyph_search_initial[0] = re.compile(r"(\w)'(\w)", re.U)
        # single closing
        self.glyph_search_initial[2] = re.compile(r"(\S)'(?=\s|{0}|$)".format(
                pnct_re_s, re.U))
        # double closing
        self.glyph_search_initial[4] = re.compile(r'(\S)"(?=\s|{0}|$)'.format(
                pnct_re_s, re.U))

        self.glyph_replace = [x.format(**self.glyph_definitions) for x in (
            r'\1{apostrophe}\2',                  # apostrophe's
            r'\1{apostrophe}\2',                  # back in '88
            r'\1{quote_single_close}',            # single closing
            r'{quote_single_open}',               # single opening
            r'\1{quote_double_close}',            # double closing
            r'{quote_double_open}',               # double opening
            r'\1{ellipsis}',                      # ellipsis
            r'\1{ampersand}\2',                   # ampersand
            r'\1{emdash}\2',                      # em dash
            r' {endash} ',                        # en dash
            r'\1\2{dimension}\3',                 # dimension sign
            r'{trademark}',                       # trademark
            r'{registered}',                      # registered
            r'{copyright}',                       # copyright
            r'{half}',                            # 1/2
            r'{quarter}',                         # 1/4
            r'{threequarters}',                   # 3/4
            r'{degrees}',                         # degrees
            r'{plusminus}',                       # plus/minus
            r'<acronym title="\2">\1</acronym>',  # 3+ uppercase acronym
            r'\1<span class="caps">{0}:glyph:\2'  # 3+ uppercase
              r'</span>\3'.format(self.uid),
        )]

        if self.html_type == 'html5':
            self.glyph_replace[19] = r'<abbr title="\2">\1</abbr>'

        if self.restricted is True:
            self.url_schemes = self.restricted_url_schemes
        else:
            self.url_schemes = self.unrestricted_url_schemes

    def parse(self, text, rel=None, sanitize=False):
        """Parse the input text as textile and return html output."""
        self.notes = OrderedDict()
        self.unreferencedNotes = OrderedDict()
        self.notelist_cache = OrderedDict()


        if self.restricted:
            text = encode_html(text, quotes=False)

        text = normalize_newlines(text)
        text = text.replace(self.uid, '')

        if self.block_tags:
            if self.lite:
                self.blocktag_whitelist = ['bq', 'p']
                text = self.block(text)
            else:
                self.blocktag_whitelist = [ 'bq', 'p', 'bc', 'notextile',
                        'pre', 'h[1-6]',
                        'fn{0}+'.format(regex_snippets['digit']), '###']
                text = self.block(text)
                text = self.placeNoteLists(text)
        else:
            # Inline markup (em, strong, sup, sub, del etc).
            text = self.span(text)

            # Glyph level substitutions (mainly typographic -- " & ' => curly
            # quotes, -- => em-dash etc.
            text = self.glyphs(text)

        if rel:
            self.rel = ' rel="{0}"'.format(rel)

        text = self.getRefs(text)

        if not self.lite:
            text = self.placeNoteLists(text)

        text = self.retrieve(text)
        text = text.replace('{0}:glyph:'.format(self.uid), '')

        if sanitize:
            text = sanitizer.sanitize(text)

        text = self.retrieveURLs(text)

        # if the text contains a break tag (<br> or <br />) not followed by
        # a newline, replace it with a new style break tag and a newline.
        text = re.sub(r'<br( /)?>(?!\n)', '<br />\n', text)

        return text

    def table(self, text):
        text = "{0}\n\n".format(text)
        pattern = re.compile(r'^(?:table(?P<tatts>_?{s}{a}{c})\.'
                r'(?P<summary>.*?)\n)?^(?P<rows>{a}{c}\.? ?\|.*\|)'
                r'[\s]*\n\n'.format(**{'s': table_span_re_s, 'a': align_re_s,
                    'c': cls_re_s}),
                flags=re.S | re.M | re.U)
        return pattern.sub(self.fTable, text)

    def fTable(self, match):
        tatts = pba(match.group('tatts'), 'table')

        summary = ''
        if match.group('summary'):
            summary = ' summary="{0}"'.format(match.group('summary').strip())
        cap = ''
        colgrp, last_rgrp = '', ''
        c_row = 1
        rows = []
        split = re.split(r'\|\s*?$', match.group('rows'), flags=re.M)
        for row in [x for x in split if x]:
            row = row.lstrip()

            # Caption -- only occurs on row 1, otherwise treat '|=. foo |...'
            # as a normal center-aligned cell.
            captionpattern = (r"^\|\=(?P<capts>{s}{a}{c})\. (?P<cap>[^\n]*)"
                    r"(?P<row>.*)".format(**{'s': table_span_re_s, 'a':
                        align_re_s, 'c': cls_re_s}))
            caption_re = re.compile(captionpattern, re.S)
            cmtch = caption_re.match(row)
            if c_row == 1 and cmtch:
                capatts = pba(cmtch.group('capts'))
                cap = "\t<caption{0}>{1}</caption>\n".format(capatts,
                        cmtch.group('cap').strip())
                row = cmtch.group('row').lstrip()
                if row == '':
                    continue

            c_row = c_row + 1

            # Colgroup
            grppattern = r"^\|:(?P<cols>{s}{a}{c}\. .*)".format(**{'s':
                table_span_re_s, 'a': align_re_s, 'c': cls_re_s})
            grp_re = re.compile(grppattern, re.M)
            gmtch = grp_re.match(row.lstrip())
            if gmtch:
                has_newline = "\n" in row
                idx = 0
                for col in gmtch.group('cols').replace('.', '').split("|"):
                    gatts = pba(col.strip(), 'col')
                    if idx == 0:
                        gatts = "group{0}>".format(gatts)
                    else:
                        gatts = "{0} />".format(gatts)
                    colgrp = "{0}\t<col{1}\n".format(colgrp, gatts)
                    idx = idx + 1
                colgrp = "{0}\t</colgroup>\n".format(colgrp)

                # If the row has a newline in it, account for the missing
                # closing pipe and process the rest of the line
                if not has_newline:
                    continue
                else:
                    row = row[row.index('\n'):].lstrip()

            grpmatchpattern = (r"(:?^\|(?P<part>{v})(?P<rgrpatts>{s}{a}{c})"
                    r"\.\s*$\n)?^(?P<row>.*)").format(**{'v': valign_re_s, 's':
                        table_span_re_s, 'a': align_re_s, 'c': cls_re_s})
            grpmatch_re = re.compile(grpmatchpattern, re.S | re.M)
            grpmatch = grpmatch_re.match(row.lstrip())

            # Row group
            rgrp = ''
            rgrptypes = {'^': 'head', '~': 'foot', '-': 'body'}
            if grpmatch.group('part'):
                rgrp = rgrptypes[grpmatch.group('part')]
            rgrpatts = pba(grpmatch.group('rgrpatts'))
            row = grpmatch.group('row')

            rmtch = re.search(r'^(?P<ratts>{0}{1}\. )(?P<row>.*)'.format(
                align_re_s, cls_re_s), row.lstrip())
            if rmtch:
                ratts = pba(rmtch.group('ratts'), 'tr')
                row = rmtch.group('row')
            else:
                ratts = ''

            cells = []
            for cellctr, cell in enumerate(row.split('|')):
                ctyp = 'd'
                if cell.startswith('_'):
                    ctyp = "h"
                cmtch = re.search(r'^(?P<catts>_?{0}{1}{2}\. )(?P<cell>.*)'.format(
                    table_span_re_s, align_re_s, cls_re_s), cell, flags=re.S)
                if cmtch:
                    catts = pba(cmtch.group('catts'), 'td')
                    cell = cmtch.group('cell')
                else:
                    catts = ''

                if not self.lite:
                    a_pattern = r'(?P<space>{0}*)(?P<cell>.*)'.format(
                            regex_snippets['space'])
                    a = re.search(a_pattern, cell, flags=re.S)
                    if a:
                        cell = self.redcloth_list(a.group('cell'))
                        cell = self.textileLists(cell)
                        cell = '{0}{1}'.format(a.group('space'), cell)

                # row.split() gives us ['', 'cell 1 contents', '...']
                # so we ignore the first cell.
                if cellctr > 0:
                    ctag = "t{0}".format(ctyp)
                    cline = "\t\t\t<{ctag}{catts}>{cell}</{ctag}>".format(**{
                        'ctag': ctag, 'catts': catts, 'cell': cell})
                    cells.append(self.doTagBr(ctag, cline))

            grp = ''

            if rgrp and last_rgrp:
                grp = "\t</t{0}>\n".format(last_rgrp)

            if rgrp:
                grp = "{0}\t<t{1}{2}>\n".format(grp, rgrp, rgrpatts)

            last_rgrp = rgrp if rgrp else last_rgrp

            trailing_newline = '\n' if cells else ''
            rows.append("{0}\t\t<tr{1}>\n{2}{3}\t\t</tr>".format(grp, ratts,
                '\n'.join(cells), trailing_newline))
            cells = []
            catts = None

        rows = '{0}\n'.format('\n'.join(rows))
        close = ''

        if last_rgrp:
            close = '\t</t{0}>\n'.format(last_rgrp)
        tbl = ("\t<table{tatts}{summary}>\n{cap}{colgrp}{rows}{close}\t"
            "</table>\n\n".format(**{'tatts': tatts, 'summary': summary, 'cap':
            cap, 'colgrp': colgrp, 'close': close, 'rows': rows}))
        return tbl

    def textileLists(self, text):
        pattern = re.compile(r'^((?:[*;:]+|[*;:#]*#(?:_|\d+)?){0}[ .].*)$'
                r'(?![^#*;:])'.format(cls_re_s), re.U | re.M | re.S)
        return pattern.sub(self.fTextileList, text)

    def fTextileList(self, match):
        text = re.split(r'\n(?=[*#;:])', match.group(), flags=re.M)
        pt = ''
        result = []
        ls = OrderedDict()
        for i, line in enumerate(text):
            try:
                nextline = text[i + 1]
            except IndexError:
                nextline = ''

            m = re.search(r"^([#*;:]+)(_|\d+)?({0})[ .](.*)$".format(cls_re_s),
                    line, re.S)
            if m:
                tl, start, atts, content = m.groups()
                content = content.strip()
                nl = ''
                ltype = list_type(tl)
                if ';' in tl:
                    litem = 'dt'
                elif ':' in tl:
                    litem = 'dd'
                else:
                    litem = 'li'

                showitem = len(content) > 0

                # handle list continuation/start attribute on ordered lists
                if ltype == 'o':
                    if not hasattr(self, 'olstarts'):
                        self.olstarts = {tl: 1}

                    # does the first line of this ol have a start attribute
                    if len(tl) > len(pt):
                        # no, set it to 1
                        if start is None:
                            self.olstarts[tl] = 1
                        # yes, set it to the given number
                        elif start != '_':
                            self.olstarts[tl] = int(start)
                        # we won't need to handle the '_' case, we'll just
                        # print out the number when it's needed

                    # put together the start attribute if needed
                    if len(tl) > len(pt) and start is not None:
                        start = ' start="{0}"'.format(self.olstarts[tl])

                    # This will only increment the count for list items, not
                    # definition items
                    if showitem:
                        self.olstarts[tl] = self.olstarts[tl] + 1

                nm = re.match("^([#\*;:]+)(_|[\d]+)?{0}[ .].*".format(
                    cls_re_s), nextline)
                if nm:
                    nl = nm.group(1)

                # We need to handle nested definition lists differently.  If
                # the next tag is a dt (';') of a lower nested level than the
                # current dd (':'),
                if ';' in pt and ':' in tl:
                    ls[tl] = 2

                atts = pba(atts)
                # If start is still None, set it to '', else leave the value
                # that we've already formatted.
                start = start or ''

                # if this item tag isn't in the list, create a new list and
                # item, else just create the item
                if tl not in ls:
                    ls[tl] = 1
                    itemtag = ("\n\t\t<{0}>{1}".format(litem, content) if
                               showitem else '')
                    line = "\t<{0}l{1}{2}>{3}".format(ltype, atts, start,
                            itemtag)
                else:
                    line = ("\t\t<{0}{1}>{2}".format(litem, atts, content) if
                            showitem else '')

                if len(nl) <= len(tl):
                    if showitem:
                        line = "{0}</{1}>".format(line, litem)
                # work backward through the list closing nested lists/items
                for k, v in reversed(list(ls.items())):
                    if len(k) > len(nl):
                        if v != 2:
                            line = "{0}\n\t</{1}l>".format(line, list_type(k))
                        if len(k) > 1 and v != 2:
                            line = "{0}</{1}>".format(line, litem)
                        del ls[k]

                # Remember the current Textile tag
                pt = tl

            # This else exists in the original php version.  I'm not sure how
            # to come up with a case where the line would not match.  I think
            # it may have been necessary due to the way php returns matches.
            #else:
                #line = "{0}\n".format(line)
            result.append(line)
        return self.doTagBr(litem, "\n".join(result))

    def doTagBr(self, tag, input):
        return re.compile(r'<({0})([^>]*?)>(.*)(</\1>)'.format(re.escape(tag)),
                          re.S).sub(self.doBr, input)

    def doPBr(self, in_):
        return re.compile(r'<(p)([^>]*?)>(.*)(</\1>)', re.S).sub(self.doBr,
                                                                 in_)

    def doBr(self, match):
        content = re.sub(r'(.+)(?:(?<!<br>)|(?<!<br />))\n(?![#*;:\s|])',
                         r'\1<br />', match.group(3))
        return '<{0}{1}>{2}{3}'.format(match.group(1), match.group(2), content,
                match.group(4))

    def block(self, text):
        if not self.lite:
            tre = '|'.join(self.btag)
        else:
            tre = '|'.join(self.btag_lite)
        text = text.split('\n\n')

        tag = 'p'
        atts = cite = graf = ext = ''
        c1 = ''
        eat = False

        out = []

        anon = False
        for line in text:
            pattern = (r'^(?P<tag>{0})(?P<atts>{1}{2})\.(?P<ext>\.?)'
                    r'(?::(?P<cite>\S+))? (?P<content>.*)$'.format(tre,
                        align_re_s, cls_re_s))
            match = re.search(pattern, line, flags=re.S | regex_snippets['mod'])
            if match:
                if ext:
                    out.append('{0}{1}'.format(out.pop(), c1))

                tag, atts, ext, cite, content = match.groups()
                o1, o2, content, c2, c1, eat = self.fBlock(**match.groupdict())
                # leave off c1 if this block is extended,
                # we'll close it at the start of the next block
                if ext:
                    line = "{0}{1}{2}{3}".format(o1, o2, content, c2)
                else:
                    line = "{0}{1}{2}{3}{4}".format(o1, o2, content, c2, c1)

            else:
                anon = True
                if ext or not re.search(r'^\s', line):
                    o1, o2, content, c2, c1, eat = self.fBlock(tag, atts, ext,
                                                               cite, line)
                    # skip $o1/$c1 because this is part of a continuing
                    # extended block
                    if tag == 'p' and not has_raw_text(content):
                        line = content
                    else:
                        line = "{0}{1}{2}".format(o2, content, c2)
                else:
                    line = self.graf(line)

            line = self.doPBr(line)
            line = re.sub(r'<br>', '<br />', line)

            if ext and anon:
                out.append("{0}\n{1}".format(out.pop(), line))
            elif not eat and line:
                out.append(line)

            if not ext:
                tag = 'p'
                atts = ''
                cite = ''
                graf = ''

        if ext:
            out.append('{0}{1}'.format(out.pop(), c1))
        return '\n\n'.join(out)

    def fBlock(self, tag, atts, ext, cite, content):
        att = atts
        atts = pba(atts, include_id=not self.restricted)
        o1 = o2 = c2 = c1 = ''
        eat = False

        if tag == 'p':
            # is this an anonymous block with a note definition?
            notedef_re = re.compile(r"""
            ^note\#                               # start of note def marker
            (?P<label>[^%<*!@\#^([{{ {space}.]+)  # label
            (?P<link>[*!^]?)                      # link
            (?P<att>{cls})                        # att
            \.?                                   # optional period.
            [{space}]+                            # whitespace ends def marker
            (?P<content>.*)$                      # content""".format(
                space=regex_snippets['space'], cls=cls_re_s),
            flags=re.X | regex_snippets['mod'])
            notedef = notedef_re.sub(self.fParseNoteDefs, content)

            # It will be empty if the regex matched and ate it.
            if '' == notedef:
                return o1, o2, notedef, c2, c1, True

        fns = re.search(r'fn(?P<fnid>{0}+)'.format(regex_snippets['digit']),
                tag, flags=regex_snippets['mod'])
        if fns:
            tag = 'p'
            fnid = self.fn.get(fns.group('fnid'), None)
            if fnid is None:
                fnid = '{0}{1}'.format(self.linkPrefix,
                        self._increment_link_index())

            # If there is an author-specified ID goes on the wrapper & the
            # auto-id gets pushed to the <sup>
            supp_id = ''

            # if class has not been previously specified, set it to "footnote"
            if atts.find('class=') < 0:
                atts = '{0} class="footnote"'.format(atts)

            # if there's no specified id, use the generated one.
            if atts.find('id=') < 0:
                atts = '{0} id="fn{1}"'.format(atts, fnid)
            else:
                supp_id = ' id="fn{0}"'.format(fnid)

            if att.find('^') < 0:
                sup = self.formatFootnote(fns.group('fnid'), supp_id)
            else:
                fnrev = '<a href="#fnrev{0}">{1}</a>'.format(fnid,
                        fns.group('fnid'))
                sup = self.formatFootnote(fnrev, supp_id)

            content = '{0} {1}'.format(sup, content)

        if tag == 'bq':
            if cite:
                cite = self.shelveURL(cite)
                cite = ' cite="{0}"'.format(cite)
            else:
                cite = ''
            o1 = "\t<blockquote{0}{1}>\n".format(cite, atts)
            o2 = "\t\t<p{0}>".format(atts)
            c2 = "</p>"
            c1 = "\n\t</blockquote>"

        elif tag == 'bc' or tag == 'pre':
            o1 = "<pre{0}>".format(atts)
            o2 = c2 = ''
            if tag == 'bc':
                o2 = "<code{0}>".format(atts)
                c2 = "</code>"
            c1 = "</pre>"
            content = self.shelve(encode_html('{0}\n'.format(
                content.rstrip("\n"))))

        elif tag == 'notextile':
            content = self.shelve(content)
            o1 = o2 = ''
            c1 = c2 = ''

        elif tag == '###':
            eat = True

        else:
            o2 = "\t<{0}{1}>".format(tag, atts)
            c2 = "</{0}>".format(tag)

        if not eat:
            content = self.graf(content)
        else:
            content = ''
        return o1, o2, content, c2, c1, eat

    def formatFootnote(self, marker, atts='', anchor=True):
        if anchor:
            pattern = self.glyph_definitions['fn_foot_pattern']
        else:
            pattern = self.glyph_definitions['fn_ref_pattern']
        return pattern.format(**{'atts': atts, 'marker': marker})

    def footnoteRef(self, text):
        # somehow php-textile gets away with not capturing the space.
        return re.compile(r'(?<=\S)\[(?P<id>{0}+)(?P<nolink>!?)\]'
                r'(?P<space>{1}?)'.format(regex_snippets['digit'],
                    regex_snippets['space']), flags=regex_snippets['mod']).sub(
                            self.footnoteID, text)

    def footnoteID(self, m):
        backref = ' class="footnote"'
        if m.group('id') not in self.fn:
            self.fn[m.group('id')] = '{0}{1}'.format(self.linkPrefix,
                    self._increment_link_index())
            fnid = self.fn[m.group('id')]
            backref = '{0} id="fnrev{1}"'.format(backref, fnid)
        fnid = self.fn[m.group('id')]
        footref = '<a href="#fn{0}">{1}</a>'.format(fnid, m.group('id'))
        if '!' == m.group('nolink'):
            footref = m.group('id')
        footref = self.formatFootnote(footref, backref, False)
        return '{0}{1}'.format(footref, m.group('space'))

    def glyphs(self, text):
        """
        Because of the split command, the regular expressions are different for
        when the text at the beginning and the rest of the text.
        for example:
        let's say the raw text provided is "*Here*'s some textile"
        before it gets to this glyphs method, the text has been converted to
        "<strong>Here</strong>'s some textile"
        When run through the split, we end up with ["<strong>", "Here",
        "</strong>", "'s some textile"].  The re.search that follows tells it
        not to ignore html tags.
        If the single quote is the first character on the line, it's an open
        single quote.  If it's the first character of one of those splits, it's
        an apostrophe or closed single quote, but the regex will bear that out.
        A similar situation occurs for double quotes as well.
        So, for the first pass, we use the glyph_search_initial set of
        regexes.  For all remaining passes, we use glyph_search
        """
        # fix: hackish
        if text.endswith('"'):
            text = '{0} '.format(text)

        text = text.rstrip('\n')
        result = []
        searchlist = self.glyph_search_initial
        # split the text by any angle-bracketed tags
        for i, line in enumerate(re.compile(r'(<[\w\/!?].*?>)',
                                            re.U).split(text)):
            if not i % 2:
                for s, r in zip(searchlist, self.glyph_replace):
                    line = s.sub(r, line)
            result.append(line)
            if i == 0:
                searchlist = self.glyph_search
        return ''.join(result)

    def getRefs(self, text):
        """Capture and store URL references in self.urlrefs."""
        pattern = re.compile(r'(?:(?<=^)|(?<=\s))\[(.+)\]((?:http(?:s?):\/\/|\/)\S+)(?=\s|$)',
                             re.U)
        text = pattern.sub(self.refs, text)
        return text

    def refs(self, match):
        flag, url = match.groups()
        self.urlrefs[flag] = url
        return ''

    def relURL(self, url):
        scheme = urlparse(url)[0]
        if scheme and scheme not in self.url_schemes:
            return '#'
        return url

    def shelve(self, text):
        self.refIndex = self.refIndex + 1
        itemID = '{0}{1}:shelve'.format(self.uid, self.refIndex)
        self.shelf[itemID] = text
        return itemID

    def retrieve(self, text):
        while True:
            old = text
            for k, v in self.shelf.items():
                text = text.replace(k, v)
            if text == old:
                break
        return text

    def graf(self, text):
        if not self.lite:
            text = self.noTextile(text)
            text = self.code(text)

        text = self.getHTMLComments(text)

        text = self.getRefs(text)
        text = self.links(text)

        if not self.noimage:
            text = self.image(text)

        if not self.lite:
            text = self.table(text)
            text = self.redcloth_list(text)
            text = self.textileLists(text)

        text = self.span(text)
        text = self.footnoteRef(text)
        text = self.noteRef(text)
        text = self.glyphs(text)

        return text.rstrip('\n')

    def links(self, text):
        """For some reason, the part of the regex below that matches the url
        does not match a trailing parenthesis.  It gets caught by tail, and
        we check later to see if it should be included as part of the url."""
        text = self.markStartOfLinks(text)

        return self.replaceLinks(text)

    def markStartOfLinks(self, text):
        """Finds and marks the start of well formed links in the input text."""
        # Slice text on '":<not space>' boundaries. These always occur in
        # inline links between the link text and the url part and are much more
        # infrequent than '"' characters so we have less possible links to
        # process.
        mod = regex_snippets['mod']
        slices = text.split('":')
        output = []

        if len(slices) > 1:
            # There are never any start of links in the last slice, so pop it
            # off (we'll glue it back later).
            last_slice = slices.pop()

            for s in slices:
                # Cut this slice into possible starting points wherever we find
                # a '"' character. Any of these parts could represent the start
                # of the link text - we have to find which one.
                possible_start_quotes = s.split('"')

                # Start our search for the start of the link with the closest
                # prior quote mark.
                possibility = possible_start_quotes.pop()

                # Init the balanced count. If this is still zero at the end of
                # our do loop we'll mark the " that caused it to balance as the
                # start of the link and move on to the next slice.
                balanced = 0
                linkparts = []
                i = 0

                while balanced is not 0 or i is 0:
                    # Starting at the end, pop off the previous part of the
                    # slice's fragments.

                    # Add this part to those parts that make up the link text.
                    linkparts.append(possibility)

                    if len(possibility) > 0:
                        # did this part inc or dec the balanced count?
                        if re.search(r'^\S|=$', possibility, flags=mod):
                            balanced = balanced - 1
                        if re.search(r'\S$', possibility, flags=mod):
                            balanced = balanced + 1
                        possibility = possible_start_quotes.pop()
                    else:
                        # If quotes occur next to each other, we get zero
                        # length strings.  eg. ...""Open the door,
                        # HAL!"":url...  In this case we count a zero length in
                        # the last position as a closing quote and others as
                        # opening quotes.
                        if i is 0:
                            balanced = balanced + 1
                        else:
                            balanced = balanced - 1
                        i = i + 1

                        try:
                            possibility = possible_start_quotes.pop()
                        except IndexError:
                            # If out of possible starting segments we back the
                            # last one from the linkparts array
                            linkparts.pop()
                            break
                        # If the next possibility is empty or ends in a space
                        # we have a closing ".
                        if (possibility is '' or possibility.endswith(' ')):
                            # force search exit
                            balanced = 0;

                    if balanced <= 0:
                        possible_start_quotes.append(possibility)
                        break

                # Rebuild the link's text by reversing the parts and sticking
                # them back together with quotes.
                linkparts.reverse()
                link_content = '"'.join(linkparts)
                # Rebuild the remaining stuff that goes before the link but
                # that's already in order.
                pre_link = '"'.join(possible_start_quotes)
                # Re-assemble the link starts with a specific marker for the
                # next regex.
                o = '{0}{1}linkStartMarker:"{2}'.format(pre_link, self.uid,
                        link_content)
                output.append(o)

            # Add the last part back
            output.append(last_slice)
            # Re-assemble the full text with the start and end markers
            text = '":'.join(output)

        return text

    def replaceLinks(self, text):
        """Replaces links with tokens and stores them on the shelf."""
        stopchars = r"\s|^'\"*"
        pattern = r"""
            (?P<pre>\[)?           # Optionally open with a square bracket eg. Look ["here":url]
            {0}linkStartMarker:"   # marks start of the link
            (?P<inner>(?:.|\n)*?)  # grab the content of the inner "..." part of the link, can be anything but
                                   # do not worry about matching class, id, lang or title yet
            ":                     # literal ": marks end of atts + text + title block
            (?P<urlx>[^{1}]*)      # url upto a stopchar
        """.format(self.uid, stopchars)
        text = re.compile(pattern, flags=re.X | regex_snippets['mod']).sub(
                self.fLink, text)
        return text

    def fLink(self, m):
        in_ = m.group()
        pre, inner, url = m.groups()
        pre = pre or ''

        if inner == '':
            return '{0}"{1}":{2}'.format(pre, inner, url)

        m = re.search(r'''^
            (?P<atts>{0})                # $atts (if any)
            {1}*                         # any optional spaces
            (?P<text>                    # $text is...
                (!.+!)                   #     an image
            |                            #   else...
                .+?                      #     link text
            )                            # end of $text
            (?:\((?P<title>[^)]+?)\))?   # $title (if any)
            $'''.format(cls_re_s, regex_snippets['space']), inner,
                flags=re.X | regex_snippets['mod'])

        atts = m.group('atts') or ''
        text = m.group('text') or '' or inner
        title = m.group('title') or ''

        pop, tight = '', ''
        counts = { '[': None, ']': url.count(']'), '(': None, ')': None }

        # Look for footnotes or other square-bracket delimited stuff at the end
        # of the url...
        #
        # eg. "text":url][otherstuff... will have "[otherstuff" popped back
        # out.
        #
        # "text":url?q[]=x][123]    will have "[123]" popped off the back, the
        # remaining closing square brackets will later be tested for balance
        if (counts[']']):
            m = re.search('(?P<url>^.*\])(?P<tight>\[.*?)$', url,
                flags=regex_snippets['mod'])
            if m:
                url, tight = m.groups()

        # Split off any trailing text that isn't part of an array assignment.
        # eg. "text":...?q[]=value1&q[]=value2 ... is ok
        # "text":...?q[]=value1]following  ... would have "following" popped
        # back out and the remaining square bracket will later be tested for
        # balance
        if (counts[']']):
            m = re.search(r'(?P<url>^.*\])(?!=)(?P<end>.*?)$', url,
                    flags=regex_snippets['mod'])
            if m:
                url = m.group('url')
                tight = '{0}{1}'.format(m.group('end'), tight)

        # Now we have the array of all the multi-byte chars in the url we will
        # parse the  uri backwards and pop off  any chars that don't belong
        # there (like . or , or unmatched brackets of various kinds).
        first = True
        popped = True

        counts[']'] = url.count(']')
        url_chars = list(url)

        def _endchar(c, pop, popped, url_chars, counts, pre):
            """Textile URL shouldn't end in these characters, we pop them off
            the end and push them out the back of the url again."""
            pop = '{0}{1}'.format(c, pop)
            url_chars.pop()
            popped = True
            return pop, popped, url_chars, counts, pre

        def _rightanglebracket(c, pop, popped, url_chars, counts, pre):
            url_chars.pop()
            urlLeft = ''.join(url_chars)

            m = re.search(r'(?P<url_chars>.*)(?P<tag><\/[a-z]+)$', urlLeft)
            if m:
                url_chars = m.group('url_chars')
                pop = '{0}{1}{2}'.format(m.group('tag'), c, pop)
                popped = True
            return pop, popped, url_chars, counts, pre

        def _closingsquarebracket(c, pop, popped, url_chars, counts, pre):
            """If we find a closing square bracket we are going to see if it is
            balanced.  If it is balanced with matching opening bracket then it
            is part of the URL else we spit it back out of the URL."""
            if counts['['] is None:
                counts['['] = url.count('[')

            if counts['['] == counts[']']:
                # It is balanced, so keep it
                url_chars.append(c)
            else:
                # In the case of un-matched closing square brackets we just eat
                # it
                popped = True
                url_chars.pop()
                counts[']'] = counts[']'] - 1;
                if first:
                    pre = ''
            return pop, popped, url_chars, counts, pre

        def _closingparenthesis(c, pop, popped, url_chars, counts, pre):
            if counts[')'] is None:
                counts['('] = url.count('(')
                counts[')'] = url.count(')')

            if counts['('] != counts[')']:
                # Unbalanced so spit it out the back end
                popped = True
                pop = '{0}{1}'.format(url_chars.pop(), pop)
                counts[')'] = counts[')'] - 1
            return pop, popped, url_chars, counts, pre

        def _casesdefault(c, pop, popped, url_chars, counts, pre):
            return pop, popped, url_chars, counts, pre

        cases = {
                '!': _endchar,
                '?': _endchar,
                ':': _endchar,
                ';': _endchar,
                '.': _endchar,
                ',': _endchar,
                '>': _rightanglebracket,
                ']': _closingsquarebracket,
                ')': _closingparenthesis,
                }
        for c in url_chars[-1::-1]:
            popped = False
            pop, popped, url_chars, counts, pre = cases.get(c,
                    _casesdefault)(c, pop, popped, url_chars, counts, pre)
            first = False
            if popped is False:
                break

        url = ''.join(url_chars)
        uri_parts = urlsplit(url)

        scheme_in_list = uri_parts.scheme in self.url_schemes
        valid_scheme = (uri_parts.scheme and scheme_in_list)
        if not is_valid_url(url) and not valid_scheme:
            return in_.replace('{0}linkStartMarker:'.format(self.uid), '')

        if text == '$':
            text = url
            if "://" in text:
                text = text.split("://")[1]
            else:
                text = text.split(":")[1]

        text = text.strip()
        title = encode_html(title)

        if not self.noimage:
            text = self.image(text)
        text = self.span(text)
        text = self.glyphs(text)
        url = self.shelveURL(self.encode_url(urlunsplit(uri_parts)))
        attributes = parse_attributes(atts)
        if title:
            attributes['title'] = title
        attributes['href'] = url
        if self.rel:
            attributes['rel'] = self.rel
        a = ElementTree.Element('a', attrib=attributes)
        a_tag = ElementTree.tostring(a)
        # FIXME: Kind of an ugly hack.  There *must* be a cleaner way.  I tried
        # adding text by assigning it to a.text.  That results in non-ascii
        # text being html-entity encoded.  Not bad, but not entirely matching
        # php-textile either.
        #
        # I thought I had found a fancy solution, using
        # ElementTree.tostringlist, but it fails differently on different
        # platforms.
        a_tag = a_tag.decode('utf-8').rstrip(' />')
        a_text = '{0}>{1}</a>'.format(a_tag, text)
        a_shelf_id = self.shelve(a_text)

        out = '{0}{1}{2}{3}'.format(pre, a_shelf_id, pop, tight)

        return out

    def encode_url(self, url):
        """
        Converts a (unicode) URL to an ASCII URL, with the domain part
        IDNA-encoded and the path part %-encoded (as per RFC 3986).

        Fixed version of the following code fragment from Stack Overflow:
            http://stackoverflow.com/a/804380/72656
        """
        # turn string into unicode
        if not isinstance(url, unicode):
            url = url.decode('utf8')

        # parse it
        parsed = urlsplit(url)

        if parsed.netloc:
            # divide the netloc further
            netloc_pattern = re.compile(r"""
                (?:(?P<user>[^:@]+)(?::(?P<password>[^:@]+))?@)?
                (?P<host>[^:]+)
                (?::(?P<port>[0-9]+))?
            """, re.X | re.U)
            netloc_parsed = netloc_pattern.match(parsed.netloc).groupdict()
        else:
            netloc_parsed = {'user': '', 'password': '', 'host': '', 'port':
                    ''}

        # encode each component
        scheme = parsed.scheme
        user = netloc_parsed['user'] and quote(netloc_parsed['user'])
        password = (netloc_parsed['password'] and
                    quote(netloc_parsed['password']))
        host = netloc_parsed['host']
        port = netloc_parsed['port'] and netloc_parsed['port']
        path = '/'.join(  # could be encoded slashes!
            quote(unquote(pce).encode('utf8'), b'')
            for pce in parsed.path.split('/')
        )
        query = quote(unquote(parsed.query), b'=&?/')
        fragment = quote(unquote(parsed.fragment))

        # put it back together
        netloc = ''
        if user:
            netloc = '{0}{1}'.format(netloc, user)
            if password:
                netloc = '{0}:{1}'.format(netloc, password)
            netloc = '{0}@'.format(netloc)
        netloc = '{0}{1}'.format(netloc, host)
        if port:
            netloc = '{0}:{1}'.format(netloc, port)
        return urlunsplit((scheme, netloc, path, query, fragment))

    def span(self, text):
        qtags = (r'\*\*', r'\*', r'\?\?', r'\-', r'__',
                 r'_', r'%', r'\+', r'~', r'\^')
        pnct = r""".,"'?!;:‹›«»„“”‚‘’"""
        self.span_depth = self.span_depth + 1

        if self.span_depth <= self.max_span_depth:
            for tag in qtags:
                pattern = re.compile(r"""
                    (?P<pre>^|(?<=[\s>{pnct}\(])|[{{[])
                    (?P<tag>{tag})(?!{tag})
                    (?P<atts>{cls})
                    (?!{tag})
                    (?::(?P<cite>\S+[^{tag}]{space}))?
                    (?P<content>[^{space}{tag}]+|\S.*?[^\s{tag}\n])
                    (?P<end>[{pnct}]*)
                    {tag}
                    (?P<tail>$|[\[\]}}<]|(?=[{pnct}]{{1,2}}[^0-9]|\s|\)))
                """.format(**{'tag': tag, 'cls': cls_re_s, 'pnct': pnct,
                    'space': regex_snippets['space']}),
                flags=re.X | regex_snippets['mod'])
                text = pattern.sub(self.fSpan, text)
        self.span_depth = self.span_depth - 1
        return text

    def fSpan(self, match):
        pre, tag, atts, cite, content, end, tail = match.groups()

        qtags = {
            '*':  'strong',
            '**': 'b',
            '??': 'cite',
            '_':  'em',
            '__': 'i',
            '-':  'del',
            '%':  'span',
            '+':  'ins',
            '~':  'sub',
            '^':  'sup'
        }

        tag = qtags[tag]
        atts = pba(atts)
        if cite:
            atts = '{0} cite="{1}"'.format(atts, cite.rstrip())

        content = self.span(content)

        out = "<{0}{1}>{2}{3}</{4}>".format(tag, atts, content, end, tag)
        if pre and not tail or tail and not pre:
            out = '{0}{1}{2}'.format(pre, out, tail)
        return out

    def image(self, text):
        pattern = re.compile(r"""
            (?:[\[{{])?         # pre
            \!                  # opening !
            (\<|\=|\>)?         # optional alignment atts
            ({0})               # optional style,class atts
            (?:\. )?            # optional dot-space
            ([^\s(!]+)          # presume this is the src
            \s?                 # optional space
            (?:\(([^\)]+)\))?   # optional title
            \!                  # closing
            (?::(\S+))?         # optional href
            (?:[\]}}]|(?=\s|$)) # lookahead: space or end of string
        """.format(cls_re_s), re.U | re.X)
        return pattern.sub(self.fImage, text)

    def fImage(self, match):
        # (None, '', '/imgs/myphoto.jpg', None, None)
        align, atts, url, title, href = match.groups()
        atts = pba(atts)
        size = None

        alignments = {'<': 'left', '=': 'center', '>': 'right'}

        if not title:
            title = ''

        if not is_rel_url(url) and self.get_sizes:
            size = imagesize.getimagesize(url)

        if href:
            href = self.shelveURL(href)

        url = self.shelveURL(url)

        out = []
        if href:
            out.append('<a href="{0}" class="img">'.format(href))
        out.append('<img')
        if align:
            out.append(' align="{0}"'.format(alignments[align]))
        out.append(' alt="{0}"'.format(title))
        if size:
            out.append(' height="{0}"'.format(size[1]))
        out.append(' src="{0}"'.format(url))
        if atts:
            out.append(atts)
        if title:
            out.append(' title="{0}"'.format(title))
        if size:
            out.append(' width="{0}"'.format(size[0]))
        out.append(' />')
        if href:
            out.append('</a>')

        return ''.join(out)

    def code(self, text):
        text = self.doSpecial(text, '<code>', '</code>', self.fCode)
        text = self.doSpecial(text, '@', '@', self.fCode)
        text = self.doSpecial(text, '<pre>', '</pre>', self.fPre)
        return text

    def fCode(self, match):
        before, text, after = match.groups()
        if after is None:
            after = ''
        # text needs to be escaped
        if not self.restricted:
            text = encode_html(text, quotes=False)
        return ''.join([before, self.shelve('<code>{0}</code>'.format(text)), after])

    def fPre(self, match):
        before, text, after = match.groups()
        if after is None:
            after = ''
        # text needs to be escaped
        if not self.restricted:
            text = encode_html(text)
        return ''.join([before, '<pre>', self.shelve(text), '</pre>', after])

    def doSpecial(self, text, start, end, method):
        pattern = re.compile(r'(^|\s|[\[({{>|]){0}(.*?){1}($|[\])}}])?'.format(
            re.escape(start), re.escape(end)), re.M | re.S)
        return pattern.sub(method, text)

    def noTextile(self, text):
        text = self.doSpecial(text, '<notextile>', '</notextile>',
                              self.fTextile)
        return self.doSpecial(text, '==', '==', self.fTextile)

    def fTextile(self, match):
        before, notextile, after = match.groups()
        if after is None:
            after = ''
        return ''.join([before, self.shelve(notextile), after])

    def getHTMLComments(self, text):
        """Search the string for HTML comments, e.g. <!-- comment text -->.  We
        send the text that matches this to fParseHTMLComments."""
        return self.doSpecial(text, '<!--', '-->', self.fParseHTMLComments)

    def fParseHTMLComments(self, match):
        """If self.restricted is True, clean the matched contents of the HTML
        comment.  Otherwise, return the comments unchanged.
        The original php had an if statement in here regarding restricted mode.
        nose reported that this line wasn't covered.  It's correct.  In
        restricted mode, the html comment tags have already been converted to
        &lt;!*#8212; and &#8212;&gt; so they don't match in getHTMLComments,
        and never arrive here.
        """
        before, commenttext, after = match.groups()
        commenttext = self.shelve(commenttext)
        return '{0}<!--{1}-->'.format(before, commenttext)

    def redcloth_list(self, text):
        """Parse the text for definition lists and send them to be
        formatted."""
        pattern = re.compile(r"^([-]+{0}[ .].*:=.*)$(?![^-])".format(cls_re_s),
                re.M | re.U | re.S)
        return pattern.sub(self.fRCList, text)

    def fRCList(self, match):
        """Format a definition list."""
        out = []
        text = re.split(r'\n(?=[-])', match.group(), flags=re.M)
        for line in text:
            # parse the attributes and content
            m = re.match(r'^[-]+({0})[ .](.*)$'.format(cls_re_s), line,
                    flags=re.M | re.S)

            atts, content = m.groups()
            # cleanup
            content = content.strip()
            atts = pba(atts)

            # split the content into the term and definition
            xm = re.match(r'^(.*?)[\s]*:=(.*?)[\s]*(=:|:=)?[\s]*$', content,
                          re.S)
            term, definition, ending = xm.groups()
            # cleanup
            term = term.strip()
            definition = definition.strip(' ')

            # if this is the first time through, out as a bool is False
            if not out:
                if definition == '':
                    dltag = "<dl{0}>".format(atts)
                else:
                    dltag = "<dl>"
                out.append(dltag)

            if definition != '' and term != '':
                if definition.startswith('\n'):
                    definition = '<p>{0}</p>'.format(definition.lstrip())
                definition = definition.replace('\n', '<br />').strip()

                term = self.graf(term)
                definition = self.graf(definition)

                out.extend(['\t<dt{0}>{1}</dt>'.format(atts, term),
                    '\t<dd>{0}</dd>'.format(definition)])

        out.append('</dl>')
        out = '\n'.join(out)
        return out

    def placeNoteLists(self, text):
        """Parse the text for endnotes."""
        if self.notes:
            o = OrderedDict()
            for label, info in self.notes.items():
                if 'seq' in info:
                    i = info['seq']
                    info['seq'] = label
                    o[i] = info
                else:
                    self.unreferencedNotes[label] = info

            if o:
                # sort o by key
                o = OrderedDict(sorted(o.items(), key=lambda t: t[0]))
            self.notes = o
        text_re = re.compile('<p>notelist({0})(?:\:([\w|{1}]))?([\^!]?)(\+?)'
                '\.?[\s]*</p>'.format(cls_re_s, syms_re_s), re.U)
        text = text_re.sub(self.fNoteLists, text)
        return text

    def fNoteLists(self, match):
        """Given the text that matches as a note, format it into HTML."""
        att, start_char, g_links, extras = match.groups()
        start_char = start_char or 'a'
        index = '{0}{1}{2}'.format(g_links, extras, start_char)
        result = ''

        if index not in self.notelist_cache:
            o = []
            if self.notes:
                for seq, info in self.notes.items():
                    links = self.makeBackrefLink(info, g_links, start_char)
                    atts = ''
                    if 'def' in info:
                        infoid = info['id']
                        atts = info['def']['atts']
                        content = info['def']['content']
                        li = ('\t\t<li{0}>{1}<span id="note{2}"> '
                                '</span>{3}</li>').format(atts, links, infoid,
                                        content)
                    else:
                        li = ('\t\t<li{0}>{1} Undefined Note [#{2}].<li>'
                                ).format(atts, links, info['seq'])
                    o.append(li)
            if '+' == extras and self.unreferencedNotes:
                for seq, info in self.unreferencedNotes.items():
                    if info['def']:
                        atts = info['def']['atts']
                        content = info['def']['content']
                        li = '\t\t<li{0}>{1}</li>'.format(atts, content)
                    o.append(li)
            self.notelist_cache[index] = "\n".join(o)
            result = self.notelist_cache[index]
        if result:
            list_atts = pba(att)
            result = '<ol{0}>\n{1}\n\t</ol>'.format(list_atts, result)
        return result

    def makeBackrefLink(self, info, g_links, i):
        """Given the pieces of a back reference link, create an <a> tag."""
        atts, content, infoid, link = '', '', '', ''
        if 'def' in info:
            link = info['def']['link']
        backlink_type = link or g_links
        i_ = encode_high(i)
        allow_inc = i not in syms_re_s
        i_ = int(i_)

        if backlink_type == "!":
            return ''
        elif backlink_type == '^':
            return """<sup><a href="#noteref{0}">{1}</a></sup>""".format(
                info['refids'][0], i)
        else:
            result = []
            for refid in info['refids']:
                i_entity = decode_high(i_)
                sup = """<sup><a href="#noteref{0}">{1}</a></sup>""".format(
                        refid, i_entity)
                if allow_inc:
                    i_ = i_ + 1
                result.append(sup)
            result = ' '.join(result)
            return result

    def fParseNoteDefs(self, m):
        """Parse the note definitions and format them as HTML"""
        label = m.group('label')
        link = m.group('link')
        att = m.group('att')
        content = m.group('content')

        # Assign an id if the note reference parse hasn't found the label yet.
        if label not in self.notes:
            self.notes[label] = {'id': '{0}{1}'.format(self.linkPrefix,
                self._increment_link_index())}

        # Ignores subsequent defs using the same label
        if 'def' not in self.notes[label]:
            self.notes[label]['def'] = {'atts': pba(att), 'content':
                    self.graf(content), 'link': link}
        return ''

    def noteRef(self, text):
        """Search the text looking for note references."""
        text_re = re.compile(r"""
        \[          # start
        ({0})       # !atts
        \#
        ([^\]!]+)   # !label
        ([!]?)      # !nolink
        \]""".format(cls_re_s), re.X)
        text = text_re.sub(self.fParseNoteRefs, text)
        return text

    def fParseNoteRefs(self, match):
        """Parse and format the matched text into note references.
        By the time this function is called, all the defs will have been
        processed into the notes array. So now we can resolve the link numbers
        in the order we process the refs..."""
        atts, label, nolink = match.groups()
        atts = pba(atts)
        nolink = nolink == '!'

        # Assign a sequence number to this reference if there isn't one already
        if label in self.notes:
            num = self.notes[label]['seq']
        else:
            self.notes[label] = {
                'seq': self.note_index, 'refids': [], 'id': ''
            }
            num = self.note_index
            self.note_index = self.note_index + 1

        # Make our anchor point and stash it for possible use in backlinks when
        # the note list is generated later...
        refid = '{0}{1}'.format(self.linkPrefix, self._increment_link_index())
        self.notes[label]['refids'].append(refid)

        # If we are referencing a note that hasn't had the definition parsed
        # yet, then assign it an ID...
        if not self.notes[label]['id']:
            self.notes[label]['id'] = '{0}{1}'.format(self.linkPrefix,
                    self._increment_link_index())
        labelid = self.notes[label]['id']

        # Build the link (if any)...
        result = '<span id="noteref{0}">{1}</span>'.format(refid, num)
        if not nolink:
            result = """<a href="#note{0}">{1}</a>""".format(labelid, result)

        # Build the reference...
        result = '<sup{0}>{1}</sup>'.format(atts, result)
        return result

    def shelveURL(self, text):
        if text == '':
            return ''
        self.refIndex = self.refIndex + 1
        self.refCache[self.refIndex] = text
        output = '{0}{1}{2}'.format(self.uid, self.refIndex, ':url')
        return output

    def retrieveURLs(self, text):
        return re.sub(r'{0}(?P<token>[0-9]+):url'.format(self.uid), self.retrieveURL, text)

    def retrieveURL(self, match):
        url = self.refCache.get(int(match.group('token')), '')
        if url is '':
            return url

        if url in self.urlrefs:
            url = self.urlrefs[url]

        return url

    def _increment_link_index(self):
        """The self.linkIndex property needs to be incremented in various
        places.  Don't Repeat Yourself."""
        self.linkIndex = self.linkIndex + 1
        return self.linkIndex


def textile(text, html_type='xhtml', encoding=None, output=None):
    """
    Apply Textile to a block of text.

    This function takes the following additional parameters:

    html_type - 'xhtml' or 'html5' style tags (default: 'xhtml')

    """
    return Textile(html_type=html_type).parse(text)


def textile_restricted(text, lite=True, noimage=True, html_type='xhtml'):
    """
    Apply Textile to a block of text, with restrictions designed for weblog
    comments and other untrusted input.  Raw HTML is escaped, style attributes
    are disabled, and rel='nofollow' is added to external links.

    This function takes the following additional parameters:

    html_type - 'xhtml' or 'html5' style tags (default: 'xhtml')
    lite - restrict block tags to p, bq, and bc, disable tables (default: True)
    noimage - disable image tags (default: True)

    """
    return Textile(restricted=True, lite=lite, noimage=noimage,
            html_type=html_type, rel='nofollow').parse(
                    text)
