#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Creates OBO file from UMLS database tables.

Created on   : 2015-07-18 ( Ergin Soysal )
Last modified: Aug 11, 2015, Tue 09:19:04 -0500
"""
import sys
import argparse
from datetime import datetime
import codecs
import gc

import logging

from utils.umls import UMLS
from utils.semTypes import INV_SEM_TYPES
from sqlalchemy import create_engine

# Globals
umls = None

withAltId = False   # generate alt_id keys?

SABS = ['MSH', 'SNOMEDCT_US', 'NCBI', 'FMA', 'GO', 'HGNC']
SUPPRESS = ['N']
LAT = ['ENG']
SUBTYPES = [
    ('morg', 'Microorganism'),
    ('org', 'Any living organism'),
    ('chem', 'Chemical'),
    ('med', 'Medication'),
    ('body', 'Body structure'),
    ('cell', 'Cell structure'),
    ('proc', 'Medical procedure'),
    ('thrp', 'Therapeutic procedure'),
    ('lab', 'Laboratory procedure'),
    ('prob', 'Problem - disease, sign or symptom'),
    ('gene', 'Gene'),
    ('prot', 'Protein'),
    ('subs', 'Substance'),
    ('other', 'Not classified yet'),
]

SUBTYPES_TUI = []

TYPEDEFS = {
    'inverse_isa':
        {'name': 'inverse_isa', 'is_transitive': 'true'},
    'sibling_of':
        {'name': 'sibling_of', 'is_transitive': 'true'},
    'part_of':
        {'name': 'part_of', 'xref': 'BFO:0000050', 'is_transitive': 'true'},
    'causative_agent_of':
        {'name': 'causative agent of'},
}

IGNORE_RELA = [
    'inverse_isa',
    'inverse_was_a',
    'was_a',
    'sibling_of',
    'moved_from',
    'moved_to',
]

IGNORE_REL = [
    'PAR',
]


def addSynIfNotExists(term, type, code, sab, name=''):
    # String comparisons are case insensitive
    lname = name.lower()
    for syn in term['synonym']:
        if syn['type'] == type and    \
           syn['code'] == code and    \
           syn['sab'] == sab and      \
           syn['name'].lower() == lname:
            return

    if sab == 'UMLS' and \
       term['name'].lower() == lname and \
       term['id'] == code:
        return

    term['synonym'].append({
        'type': type,
        'code': code,
        'sab': sab,
        'name': name,
    })


def addSynonym(term, c):
    addSynIfNotExists(term, 'EXACT', c['SCUI'] or c['CODE'], c['SAB'], c['STR'])


def addSynonyms(term, name, cc):
    term['syns'] = [name.lower()]
    # select mrconso where cui=:cui and lui<>:lui
    for c in cc:
        code = makeCode(c['SAB'], c['SCUI'] or c['CODE'])
        ustr = c['STR'].lower()

        if withAltId and code not in term['alt_id']:
            term['alt_id'].append(code)

        if not ustr in term['syns']:
            addSynonym(term, c)
            term['syns'].append(ustr)

        addXref(term, c)


def addXref(term, c):
    xref = makeCode(c['SAB'], c['SCUI'] or c['CODE']) + ' ! '

    for xr in term['xref']:
        if xr.startswith(xref):
            return

    term['xref'].append(xref + c['STR'])


def addRelInNotExists(term, type, code, sab, name=''):
    for rel in term['relationship']:
        if rel['type'] == type and    \
           rel['code'] == code and    \
           rel['sab'] == sab and      \
           rel['name'] == name:
            return

    term['relationship'].append({
        'type': type,
        'code': code,
        'sab': sab,
        'name': name,
    })


def addRelationships(term, cui):
    # select cui2, rel, rela mrrel
    # where cui1=:cui and SUPPRESS IN ('N') AND SAB IN ('...')
    #
    # rela CUI:xxx
    # PAR, CHD: -> is_a
    is_as = []
    rels = umls.relcuis(cui, stype1='SCUI', sab=SABS, suppress=SUPPRESS)
    for r in rels:
        rela = r['RELA']
        rel = r['REL']
        sab = r['SAB']
        cui1 = r['CUI1']
        c = findConcept(cui1, sab)
        if c is None:
            # (no concept for cui???)
            logging.warning('No concept for CUI %s (%s) in addRelationships' %
                            (cui1, sab))
            continue
        elif c['supp']:
            logging.warning('Skipping relasionship with suppressible concept '
                            '%(name)s (%(code)s) in addRelationships' % c)
            continue
        else:
            name = c['name']
            # ccode = c['code']

        if rela in ['isa', 'is_a'] or \
                (rela is None and rel in ['CHD']):
            # check recurrence of is_a
            ctemp = 'UMLS:' + cui1
            if ctemp not in is_as:
                is_as.append(ctemp)
                temp = '%s ! %s' % (ctemp, name)
                # if not temp in term['is_a']:
                term['is_a'].append(temp)
        elif rel == 'SY':
            # UMLS CUI marked as a synonym
            addSynIfNotExists(term, 'EXACT', cui1, 'UMLS', name)
        elif rel == 'RN' and rela not in ['part_of', 'was_a']:
            # has_alternative, mapped_from, mapped_to, refers_to
            # GO, MeSH
            # this concept is narrower,
            # so, the related concept is broader!
            addSynIfNotExists(term, 'BROAD', cui1, 'UMLS', name)
        elif rel == 'RB' and rela not in [
                'has_part', 'inverse_isa', 'inverse_was_a']:
            # alternative_of, mapped_from, mapped_to, referred_to_by
            # GO, MeSH
            # reverse of previous condition 'RN'
            addSynIfNotExists(term, 'NARROW', cui1, 'UMLS', name)
        elif rel == 'RQ':
            # GO: replaced_by, ...
            # SNOMEDCT mapped_from, mapped_to
            addSynIfNotExists(term, 'RELATED', cui1, 'UMLS', name)
        elif rela is not None:
            if rela not in IGNORE_RELA:
                addRelInNotExists(term, rela, cui1, sab, name)
                # need a type definition?
                if rela not in TYPEDEFS:
                    # type definitions require manual review
                    TYPEDEFS[rela] = {'name': rela}
        elif rel == 'PAR':
            # MeSH, NCBI
            # inverse_isa should be ignored. If not being ignored:
            if 'inverse_isa' not in IGNORE_RELA:
                addRelInNotExists(term, 'inverse_isa', cui1, sab, name)
        elif rel == 'SIB':
            # FMA, GO, MeSH
            # Sibling information is included.
            # if not in ignore list
            if 'sibling_of' not in IGNORE_RELA:
                addRelInNotExists(term, 'sibling_of', cui1, sab, name)
        elif rel == 'RN':     # is a
            # GO, MeSH
            # this concept is narrower,
            # so, the related concept is broader!
            addSynIfNotExists(term, 'BROAD', cui1, 'UMLS', name)
        elif rel == 'RB':
            # GO, MeSH
            # reverse of previous condition 'RN'
            addSynIfNotExists(term, 'NARROW', cui1, 'UMLS', name)
        elif rel == 'RO':
            # GO, MeSH makes no sense: related some otherway
            pass
        elif rel == 'QB':
            # MeSH
            pass
        else:
            logging.error("Unhandled combination: "
                          "rel:%s rela:%s cui:%s '%s' in addRelationships" %
                          (rel, rela, cui, name))
            # exit()


def addSemTypeInNotExists(term, tui):
    ctui = 'UMLS:' + tui
    if ctui not in term['subset']:
        # term['subset'].append(ctui)
        if ctui not in SUBTYPES_TUI:
            SUBTYPES_TUI.append(ctui)
    if not INV_SEM_TYPES[tui] in term['subset']:
        term['subset'].append(INV_SEM_TYPES[tui])


def addSemTypes(term, cui):
    for tui in umls.tuis(cui):
        addSemTypeInNotExists(term, tui)


def getTerm(cui, name, cc):
    """Pack all information for the same cui into a single term"""
    term = {
        'id': 'UMLS:%s' % cui,
        'name': name,
        'alt_id': [],
        'synonym': [],
        'xref': [],
        'is_a': [],
        'relationship': [],
        'subset': [],
    }

    termDef = umls.defn(cui, suppress=SUPPRESS, sabOrder=SABS)  # SAB??
    if termDef:
        conDef = umls.aui(termDef['AUI'])
        if conDef is None:
            logging.error('AUI Not found %s - %s from MRDEF in getTerm' %
                          (termDef['AUI'], cui))
            print "NoneType for", termDef['AUI']
            conDef = {'SCUI': '', 'SAB': termDef['SAB']}

        term['def'] = {
            'def': termDef['DEF'],
            'code': conDef['SCUI'] or conDef['CODE'],
            'sab': conDef['SAB'],
        }

    addSynonyms(term, name, cc)
    addRelationships(term, cui)
    addSemTypes(term, cui)

    return term


def writeOBO(fname):
    f = codecs.open(fname, "w", "utf-8")
    f.write('format-version: 1.2\n')
    f.write('data-version: UMLS 2015AA\n')
    f.write('date: %s\n' % datetime.now().strftime('%d:%m:%Y %H:%M'))
    for stype in SUBTYPES:
        f.write('subsetdef: %s "%s"\n' % stype)

    # for stype in SUBTYPES_TUI:
    #     f.write('subsetdef: %s ""\n' % stype)

    f.write('\n')
    return f


def escapeStr(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def makeCode(sab, code):
    if ':' in code:
        return code
    else:
        return '%s:%s' % (sab, code)


def writeTerm(f, term):
    f.write('[Term]\n')
    f.write('id: %s\n' % term['id'])
    f.write('name: %s\n' % term['name'])

    for alt_id in term['alt_id']:
        f.write('alt_id: %s\n' % alt_id)

    # term definiton
    if 'def' in term:
        defn = term['def']
        f.write('def: "%s" [%s]\n' %
                (escapeStr(defn['def']), makeCode(defn['sab'], defn['code'])))

    for subset in term['subset']:
        f.write('subset: %s\n' % subset)

    for is_a in term['is_a']:
        f.write('is_a: %s\n' % is_a)

    for syn in term['synonym']:
        syn['ename'] = escapeStr(syn['name'])
        syn['ecode'] = makeCode(syn['sab'], syn['code'])
        f.write('synonym: "%(ename)s" %(type)s [%(ecode)s]\n' % syn)

    for xref in term['xref']:
        f.write('xref: %s\n' % xref)

    for rel in term['relationship']:
        rel['ename'] = escapeStr(rel['name'])
        f.write('relationship: %(type)s UMLS:%(code)s ! %(ename)s\n' % rel)

    f.write('\n')


def writeTypes(f):
    for t in TYPEDEFS:
        tdef = TYPEDEFS[t]
        tdef['id'] = t
        f.write('[Typedef]\nid: %(id)s\nname: %(name)s\n' % tdef)

        for td in ['xref', 'is_transitive']:
            if td in tdef:
                f.write('%s: %s\n' % (td, tdef[td]))

        f.write('\n')


def selectRootConcept(c):
    """Logic to select root concept goes here"""
    for c1 in c:
        if c1['TS'] == 'P' and c1['STT'] == 'PF' and c1['ISPREF'] == 'Y':
            return c1

    return c[0]


def findConcept(cui, sab):
    c = umls.concept(cui, sab=sab)
    if len(c) < 1:
        c = umls.concept(cui, lat=LAT, sab=SABS, suppress=SUPPRESS)
        if len(c) < 1:
            logging.warning('CUI Not found %s - %s in findConcept' % (cui, sab))
            return None
        else:
            logging.warning('CUI for SAB not found %s - %s in findConcept' %
                            (cui, sab))

    c = c[0]

    return {'sab': c['SAB'], 'code': c['SCUI'] or c['CODE'], 'name': c['STR'],
            'supp': c['SUPPRESS'] not in SUPPRESS}


def processConcept(cui):
    c = umls.concept(cui, lat=LAT, sab=SABS, suppress=SUPPRESS)
    if len(c) == 0:
        return None

    bc = selectRootConcept(c)

    term = getTerm(cui, bc['STR'], c)
    return term


def processConcepts(fname, offset, count):
    f = writeOBO(fname)
    hasMore = True
    while hasMore:
        res = umls.cuis(offset, count, sab=SABS, suppress=SUPPRESS, lat=LAT)
        print offset, "received", len(res)
        i = 1
        for cui in res:
            print "\r", i, "processing", cui,
            term = processConcept(cui)
            writeTerm(f, term)
            sys.stdout.flush()
            i += 1

        print
        gc.collect()

        hasMore = len(res) == count
        offset = offset + len(res)

    writeTypes(f)
    f.close()


def parseArgs():
    parser = argparse.ArgumentParser(description='Creates OBO file from '
                                     'UMLS database tables.',
                                     fromfile_prefix_chars='@')
    parser.add_argument('-f', '--filename', default="umls.obo",
                        help='OBO Output filename')
    parser.add_argument('-d', '--deploy', action='store_true', required=False,
                        help='Run in deploy mode')
    parser.add_argument('-p', '--prefix', default='',
                        help='umls tablename prefix')
    parser.add_argument('-o', '--offset', type=int, default=0,
                        help='Start number of the first CUI to be processed')
    parser.add_argument('-c', '--count', type=int, default=100,
                        help='Number of CUIS to process for each query')
    parser.add_argument('-s', '--constr', required=True,
                        help='Connection string for sqlalchemy')
    parser.add_argument('-a', '--alt-id', action='store_true', required=False,
                        default=False, help='Generate alt_id\'s')

    return parser.parse_args()


def main(args):
    global umls

    engine = create_engine(args.constr)
    with UMLS(engine, args.prefix) as umls:
        processConcepts(args.filename, args.offset, args.count)


if __name__ == '__main__':
    args = parseArgs()
    if args.deploy:
        level = logging.ERROR
    else:
        level = logging.DEBUG
        print "Logging in DEBUG mode"

    logging.basicConfig(filename='generateOBO.log',
                        format='%(levelname)s:%(message)s',
                        level=level)

    main(args)
