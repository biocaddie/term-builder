#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BioCADDIE Terminology Utilities
OBO file reader

Typical usage:
     with OBOReader('filename.obo') as obo:
         for term in obo:
             print term.name

Created on   : 2015-06-29 ( Ergin Soysal )
Last modified: Aug 07, 2015, Fri 20:38:23 -0500
"""

import codecs
import re


class OBOTerm(object):
    """Simple class to model a concept from an OBO file"""
    def __init__(self, termId='', name=''):
        self.id = termId
        self.name = name
        self.defn = None
        self.is_a = []
        self.alt_id = []
        self.synonym = []
        self.xref = []
        self.relationship = []
        self.intersection_of = []
        self.union_of = []
        self.subset = []
        self.property_value = []

    def __str__(self):
        return '%s [%s]' % (self.name, self.id)


class EntryParser(object):
    XREF = re.compile(ur'(\S+)(?:\s+(.*))?')
    SYN = re.compile(ur'"((?:\"|[^""])+)"(?:\s([^\s\[]+(?:\s[^\s\[]+)*))?'
                     ur'(?:\s\[([^\])]*)\])?')
    IS_A = re.compile(ur'(\S+)(?:\s+!\s*(.*))?')
    REL = re.compile(ur'(\S+)\s+(\S+)(?:\s+!\s*(.*))?')
    DEF = re.compile(ur'"((?:\"|[^""])+)"\s*(?:\[([^\])]*)\])?')

    def xref(self, line):
        """Process xref line

        :line: line to process
        :returns: an array containing xref string, and any source
        """
        m = EntryParser.XREF.match(line)
        # if m is None: print line; exit()
        return {
            'code': m.group(1),
            'src': m.group(2),
        }

    def defn(self, line):
        """Process definition line

        :line: line to process
        :returns: an array containing definition string, and any code
        """
        m = EntryParser.DEF.match(line)
        # if m is None: print line; exit()
        return {
            'name': m.group(1),
            'code': m.group(2),
        }

    def syn(self, line):
        """Process synonym line

        :line: line to process
        :returns: an array containing synonym string, synonym type (if any),
                and any code
        """
        m = EntryParser.SYN.match(line)
        # if m is None: print line; exit()
        return {
            'name': m.group(1),
            'type': m.group(2),
            'code': m.group(3),
        }

    def rel(self, line):
        m = EntryParser.REL.match(line)
        return {
            'type': m.group(1),
            'code': m.group(2),
            'name': m.group(3),
        }

    def is_a(self, line):
        m = EntryParser.IS_A.match(line)
        return {
            'code': m.group(1),
            'name': m.group(2),
        }


class OBOReader(object):
    """OBO file reader."""
    def __init__(self, filename):
        self.fb = None
        self.eof = True
        self.curTerm = None
        self.isTerm = False
        self.fmt = EntryParser()
        self.open(filename)

    def __enter__(self):
        return self

    def __exit__(self, e_type, e_value, traceback):
        self.close()
        if e_type is not None:
            print e_type, e_value, traceback
            # return False

        return self

    def __iter__(self):
        return self

    def next(self):
        if self.eof:
            raise StopIteration

        if self.isTerm:
            self.curTerm = OBOTerm()

        for line in self.fb:
            row = [l.strip() for l in line.split(':', 1)]
            if row[0] == '[Term]':
                if self.isTerm:
                    return self.curTerm
                else:
                    self.isTerm = True
                    self.curTerm = OBOTerm()
            elif row[0] == '[Typedef]':
                if self.isTerm:
                    self.isTerm = False
                    return self.curTerm
                self.isTerm = False
            elif self.isTerm:
                if row[0] == 'id':
                    self.curTerm.id = row[1]
                elif row[0] == 'name':
                    self.curTerm.name = row[1]
                elif row[0] == 'def':
                    fmt = self.fmt.defn(row[1])
                    self.curTerm.defn = fmt
                elif row[0] == 'synonym':
                    fmt = self.fmt.syn(row[1])
                    self.curTerm.synonym.append(fmt)
                elif row[0] == 'relationship':
                    fmt = self.fmt.rel(row[1])
                    self.curTerm.relationship.append(fmt)
                elif row[0] == 'xref':
                    fmt = self.fmt.xref(row[1])
                    self.curTerm.xref.append(fmt)
                elif row[0] == 'is_a':
                    fmt = self.fmt.is_a(row[1])
                    self.curTerm.is_a.append(fmt)
                elif row[0] == 'intersection_of':
                    self.curTerm.intersection_of.append(row[1])
                elif row[0] == 'alt_id':
                    self.curTerm.alt_id.append(row[1])
                elif row[0] == 'subset':
                    self.curTerm.subset.append(row[1])
                elif row[0] == 'property_value':
                    self.curTerm.property_value.append(row[1])
                elif row[0] == 'union_of':
                    self.curTerm.union_of.append(row[1])

        self.eof = True
        if self.isTerm:
            return self.curTerm
        else:
            raise StopIteration

    def open(self, filename):
        self.filename = filename
        self.fb = codecs.open(filename, 'r', 'utf-8')
        self.eof = False

    def close(self):
        if self.fb is not None:
            self.fb.close()
            self.fb = None
