#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

    BIOCADDIE Terminology server utilities
    Index terms to elasticsearch

    Created on   : 2015-05-25 ( esoysal@gmail.com )
    Last modified: Aug 05, 2015, Wed 12:03:37 -0500
"""
import argparse
# from utils.snomedct import SNOMEDCT
# from utils.umls import UMLS
from sqlalchemy import create_engine
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError

from utils.semTypes import INV_SEM_TYPES

# Global vars
es = None
conn = None

#
# LNC, RXNORM
# NCI: is removed b/o false entries like: TP53, prostate carcinoma
#
#  CREATE TABLE indexdata AS
#     SELECT LUI , STR, GROUP_CONCAT(DISTINCT CUI) AS CUIS,
#               GROUP_CONCAT(DISTINCT CONCAT( SAB, ':', CODE )) AS CODES
#     FROM MRCONSO
#     WHERE LAT = 'ENG'
#       AND SAB IN ('MSH', 'SNOMEDCT_US', 'NCBI', 'GO', 'HGNC', 'FMA')
#       AND SUPPRESS IN ('N')
#     GROUP BY LUI
#     ORDER BY LUI;
#
#  ALTER TABLE indexdata ADD PRIMARY KEY(LUI);
#
#  CREATE TABLE temp_strs AS SELECT str FROM indexdata;
#
SEM_TYPE_NAMEs = [
    '(foundation metadata concept)',
    '(context-dependent category)',
    '(morphologic abnormality)',
    '(administrative concept)',
    '(navigational concept)',
    '(contextual qualifier)',
    '(geographic location)',
    '(religion/philosophy)',
    '(biological function)',
    '(separate procedure)',
    '(namespace concept)',
    '(observable entity)',
    '(assessment scale)',
    '(record artifact)',
    '(allelic variant)',
    '(qualifier value)',
    '(living organism)',
    '(physical object)',
    '(cell structure)',
    '(surface region)',
    '(physical force)',
    '(regime/therapy)',
    '(body structure)',
    '(tumor staging)',
    '(clinical exam)',
    '(staging scale)',
    '(combined site)',
    '(manifestation)',
    '(invertebrate)',
    '(ethnic group)',
    '(environment)',
    '(Drosophila)',    #
    '(medication)',
    '(occupation)',
    '(attribute)',
    '(procedure)',
    '(substance)',
    '(diagnosis)',
    '(treatment)',
    '(situation)',
    '(eukaryote)',
    '(diagnosis)',
    '(superior)',
    '(inferior)',
    '(obsolete)',
    '(bacteria)',
    '(lab test)',
    '(disorder)',
    '(specimen)',
    '(organism)',
    '(Medicine)',
    '(etiology)',
    '(function)',
    '(property)',
    '(disease)',
    '(finding)',
    '(product)',
    '(symptom)',
    '(degrees)',
    '(history)',
    '(lateral)',
    '(person)',
    '(fungus)',
    '(medial)',
    '(device)',
    '(action)',
    '(event)',
    '(yeast)',    #
    '(human)',
    '(PLANT)',    #
    '(cell)',
]

SQL = "SELECT LUI , STR, CUIS, CODES, TUIS FROM indexdata LIMIT %d, %d"

# NCBI Taxonomy, 2014_04_01
# NCI Thesaurus, 2014_03E


def query(offset, count=100):
    """Run the same sql from a given offset for a given count"""
    sql = SQL % (offset, count)
    result = conn.execute(sql)
    res = []
    for row in result:
        res.append(row)

    return res


def addIndex(concept, index, doctype):
    """Indexes a given umls concept to index with doc_type"""
    tuis = concept[4].split(',')
    sset = [INV_SEM_TYPES[tui] for tui in tuis]
    body = {
        'lui': concept[0],
        'term': concept[1],
        'cui': concept[2].split(','),
        'sab': concept[3].split(','),
        'tui': tuis,
        'sset': sset,  # subset
    }

    es.index(index=index, doc_type=doctype, body=body)


def processAll(index, doctype):
    """process all concepts in smaller chunks"""
    offset = 0
    count = 100
    hasMore = True
    while hasMore:
        concepts = query(offset, count)
        for concept in concepts:
            addIndex(concept, index, doctype)

        # check the number of results
        numResults = len(concepts)
        offset += numResults
        # is the result count equals to expected number of items?
        hasMore = numResults == count


def parseArgs():
    parser = argparse.ArgumentParser(description='Creates ElasticSearch index '
                                     'using UMLS concept descriptions',
                                     fromfile_prefix_chars='@')
    parser.add_argument('-d', '--delete', action='store_true', required=False,
                        help='Delete the previous index and restart')
    parser.add_argument('-H', '--host', default='localhost', required=False,
                        help='Host for ElasticSearch server')
    parser.add_argument('-p', '--port', type=int, default=9200, required=False,
                        help='Port for ElasticSearch server')
    parser.add_argument('-i', '--index', required=True,
                        help='Name of the ElasticSearch index to create')
    parser.add_argument('-t', '--doctype', required=True,
                        help='Document type of the ElasticSearch index '
                        'to create')
    parser.add_argument('-s', '--constr', required=True,
                        help='Connection string for sqlalchemy')

    return parser.parse_args()


def main(args):
    global conn
    global es

    try:
        es = Elasticsearch([
            {u'host': args.host, u'port': args.port},
        ], sniff_on_start=True)
    except TransportError:
        print 'Unable to sniff host %s:%s' % (args.host, args.port)
        exit(1)

    if args.delete:
        print 'deleting index'
        es.indices.delete(index=args.index, ignore=[400, 404])

    engine = create_engine(args.constr)
    conn = engine.connect()
    try:
        processAll(args.index, args.doctype)
    finally:
        conn.close()

if __name__ == '__main__':
    main(parseArgs())
