#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from utils.obo import OBOReader, EntryParser


class TestOBOReader(unittest.TestCase):
    def setUp(self):
        # self.obo = OBOReader('test.obo')
        pass

    def tearDown(self):
        # self.obo = None
        pass

    def test_oboreader(self):
        """OBOReader test."""
        with OBOReader('test/test.obo') as terms:
            i = 1
            for term in terms:
                self.assertNotEqual(term, None, "Term %d returns None" % i)


class TestEntryParser(unittest.TestCase):
    def setUp(self):
        self.fmt = EntryParser()

    def tearDown(self):
        self.fmt = None

    def test_syn_1(self):
        syn = self.fmt.syn('"\"Down\" syndrome" EXACT [UMLS:000000]')
        self.assertEqual(syn['name'], '\"Down\" syndrome')
        self.assertEqual(syn['type'], 'EXACT')
        self.assertEqual(syn['code'], 'UMLS:000000')

    def test_syn_2(self):
        syn = self.fmt.syn('"\"Down\" syndrome" [UMLS:000000]')
        self.assertEqual(syn['name'], '\"Down\" syndrome')
        self.assertEqual(syn['type'], None)
        self.assertEqual(syn['code'], 'UMLS:000000')

    def test_syn_3(self):
        syn = self.fmt.syn('"\"Down\" syndrome" EXACT []')
        self.assertEqual(syn['name'], '\"Down\" syndrome')
        self.assertEqual(syn['type'], 'EXACT')
        self.assertEqual(syn['code'], '')

    def test_syn_4(self):
        syn = self.fmt.syn('"\"Down\" syndrome" []')
        self.assertEqual(syn['name'], '\"Down\" syndrome')
        self.assertEqual(syn['type'], None)
        self.assertEqual(syn['code'], '')

    def test_rel_1(self):
        """Test relationship extraction."""
        rel = self.fmt.rel('has_part UBERON:0001003 ! skin epidermis')
        self.assertEqual(rel['type'], 'has_part')
        self.assertEqual(rel['code'], 'UBERON:0001003')
        self.assertEqual(rel['name'], 'skin epidermis')

    def test_rel_2(self):
        rel = self.fmt.rel('has_part UBERON:0001003')
        self.assertEqual(rel['type'], 'has_part')
        self.assertEqual(rel['code'], 'UBERON:0001003')
        self.assertEqual(rel['name'], None)

    def test_xref_1(self):
        """Test xref"""
        xref = self.fmt.xref('UMLS:C1280202 {source="NIFSTD:birnlex_1169"}')
        self.assertEqual(xref['code'], 'UMLS:C1280202')
        self.assertEqual(xref['src'], '{source="NIFSTD:birnlex_1169"}')

    def test_xref_2(self):
        """Test xref"""
        xref = self.fmt.xref('UMLS:C1280202')
        self.assertEqual(xref['code'], 'UMLS:C1280202')
        self.assertEqual(xref['src'], None)

    def test_defn_1(self):
        defn = self.fmt.defn('"A \"wide\" transducer." [UMLS:000022]')
        self.assertEqual(defn['name'], 'A \"wide\" transducer.')
        self.assertEqual(defn['code'], 'UMLS:000022')

    def test_defn_2(self):
        defn = self.fmt.defn('"An 2\" organ that is capable of transducing '
                             'sensory stimulus to the nervous system." '
                             '[https://github.com/obophenotype/uberon/issues'
                             '/549, https://orcid.org/0000-0002-6601-2165]')
        self.assertEqual(defn['name'],
                         'An 2\" organ that is capable of transducing '
                         'sensory stimulus to the nervous system.')
        self.assertEqual(defn['code'],
                         'https://github.com/obophenotype/uberon/issues/549, '
                         'https://orcid.org/0000-0002-6601-2165')

    def test_defn_3(self):
        defn = self.fmt.defn('"A \"wide\" transducer." []')
        self.assertEqual(defn['name'], 'A \"wide\" transducer.')
        self.assertEqual(defn['code'], '')

    def test_defn_4(self):
        defn = self.fmt.defn('"A \"wide\" transducer."')
        self.assertEqual(defn['name'], 'A \"wide\" transducer.')
        self.assertEqual(defn['code'], None)

    def test_is_a_1(self):
        """Test is_a"""
        is_a = self.fmt.is_a('UMLS:C0832830 ! Bony part of zone of phalanx')
        self.assertEqual(is_a['code'], 'UMLS:C0832830')
        self.assertEqual(is_a['name'], 'Bony part of zone of phalanx')

    def test_is_a_2(self):
        """Test is_a"""
        is_a = self.fmt.is_a('UMLS:C0832830 !')
        self.assertEqual(is_a['code'], 'UMLS:C0832830')
        self.assertEqual(is_a['name'], '')

    def test_is_a_3(self):
        """Test is_a"""
        is_a = self.fmt.is_a('UMLS:C0832830')
        self.assertEqual(is_a['code'], 'UMLS:C0832830')
        self.assertEqual(is_a['name'], None)

if __name__ == '__main__':
    unittest.main()
