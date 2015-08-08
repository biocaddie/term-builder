#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Processes uberon OBO file

Created on   : 2015-07-29 ( Ergin Soysal )
Last modified: Aug 04, 2015, Tue 11:09:21 -0500
"""

import argparse
import codecs
from utils.obo import OBOReader


def saveToCvs(fb, term, delim='\t'):
    fb.write(term.id + delim + term.name + delim)
    if term.defn is not None:
        fb.write(term.defn['name'] + delim)
        if term.defn['code'] is not None:
            fb.write(term.defn['code'])
    fb.write('\n')


def saveSynToCvs(fb, term, delim='\t'):
    print 'syn'
    for synonym in term.synonym:
        if synonym['code'] is not None:
            codes = [c.strip() for c in synonym['code'].split(',')]
        else:
            codes = [None]

        for code in codes:
            fb.write(term.id + delim + synonym['name'] + delim)

            if synonym['type'] is not None:
                fb.write(synonym['type'])
            fb.write(delim)
            if code is not None:
                fb.write(code)
            fb.write('\n')

    for xref in term.xref:
        fb.write(term.id + delim)
        if xref['src'] is not None:
            fb.write(xref['src'])
        fb.write(delim + 'EXACT' + delim)

        if xref['code'] is not None:
            fb.write(xref['code'])
        fb.write('\n')


def saveRelToCvs(fb, term, delim='\t'):
    print 'rel'
    for is_a in term.is_a:
        fb.write(term.id + delim + 'is_a' + delim + is_a['code'] + delim)
        if is_a['name'] is not None:
            fb.write(is_a['name'])
        fb.write('\n')

    # intersection_of
    # union_of

    # relationship
    for rel in term.relationship:
        fb.write(term.id + delim + rel['type'] + delim + rel['code'] + delim)
        if rel['name'] is not None:
            fb.write(rel['name'])
        fb.write('\n')


def process(term):
    """Process an UBERON term

    :term: OBOTerm to process
    """
    print '[Term]'
    print 'id:', term.id
    print 'name:', term.name

    if term.defn is not None:
        print 'def: "%s"' % term.defn['name'],
        if term.defn['code'] is not None:
            print ' [%s]' % term.defn['code']

    if len(term.subset) > 0:
        for subset in term.subset:
            print 'subset:', subset

    # synonym
    if len(term.synonym) > 0:
        for synonym in term.synonym:
            print 'synonym: "%s" %s' % (synonym['name'], synonym['type']),
            if synonym['code'] is not None:
                print '[%s]' % synonym['code']
            else:
                print

    # xref
    if len(term.xref) > 0:
        for xref in term.xref:
            print 'xref:', xref['code'],
            if xref['src'] is not None:
                print xref['src']
            else:
                print

    # is_a
    if len(term.is_a) > 0:
        for is_a in term.is_a:
            print 'is_a:', is_a['code'],
            if is_a['name'] is not None:
                print '!', is_a['name']
            else:
                print

    # intersection_of
    # union_of

    # relationship
    if len(term.relationship) > 0:
        for rel in term.relationship:
            print 'relationship:', rel['type'], rel['code'],
            if rel['name'] is not None:
                print '!', rel['name']
            else:
                print

    print


def parseArgs():
    parser = argparse.ArgumentParser(description='Processes uberon OBO file')
    parser.add_argument('-f', '--filename', default='uberon.obo',
                        required=False, help='OBO filename to process')

    return parser.parse_args()


def main(args):
    with codecs.open(args.filename + '_con.tsv', 'w', 'utf-8') as conFb:
        with codecs.open(args.filename + '_syn.tsv', 'w', 'utf-8') as synFb:
            with codecs.open(args.filename + '_rel.tsv', 'w', 'utf-8') as relFb:
                with OBOReader(args.filename) as obo:
                    for term in obo:
                        process(term)
                        saveToCvs(conFb, term)
                        saveSynToCvs(synFb, term)
                        saveRelToCvs(relFb, term)

if __name__ == '__main__':
    main(parseArgs())
