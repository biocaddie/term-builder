#!/usr/bin/env python
# -*- coding: utf-8
"""
    Database stored UMLS terminology management utilities.

    UMLS classes to process UMLS terms

    Created on   : 2015-04-30 ( esoysal@gmail.com )
    Last modified: Aug 07, 2015, Fri 20:35:04 -0500
"""

from sqlalchemy import select, and_
from sqlalchemy import distinct
from .term import TermTable


class UMLS(TermTable):
    def _attrs(self, attr, c):
        """Build where condition based on attributes provided"""
        ret = []
        for fld in attr:
            if fld == 'sab':
                sab = self._list(attr['sab'], c.SAB)
                ret.append(sab)
            elif fld == 'ispref':
                ret.append(attr['ispref'] == c.ISPREF)
            elif fld == 'code':
                ret.append(attr['code'] == c.CODE)
            elif fld == 'suppress':
                suppress = self._list(attr['suppress'], c.SUPPRESS)
                ret.append(suppress)
            elif fld == 'lat':
                lat = self._list(attr['lat'], c.LAT)
                ret.append(lat)
            else:
                raise AttributeError('Unknown table field: %s' % fld)

        return ret

    def relations(self, cui, **attr):
        table = self.getTable('MRREL')
        where = [table.c.CUI2 == cui]

        if 'sab' in attr:
            sab = self._list(attr['sab'], table.c.SAB)
            where.append(sab)

        if 'rel' in attr:
            rel = self._list(attr['rel'], table.c.REL)
            where.append(rel)

        if 'rela' in attr:
            rela = self._list(attr['rela'], table.c.RELA)
            where.append(rela)

        s = select([table]).where(and_(*where))

        if 'sabOrder' in attr:
            sabOrder = self._valCase(attr['sabOrder'], table.c.SAB)
            s = s.order_by(sabOrder)

        return self._exec(s)

    def relcuis(self, cui, **attr):
        table = self.getTable('MRREL')
        where = [table.c.CUI2 == cui]

        if 'sab' in attr:
            sab = self._list(attr['sab'], table.c.SAB)
            where.append(sab)

        if 'rel' in attr:
            rel = self._list(attr['rel'], table.c.REL)
            where.append(rel)

        if 'rela' in attr:
            rela = self._list(attr['rela'], table.c.RELA)
            where.append(rela)

        if 'suppress' in attr:
            suppress = self._list(attr['suppress'], table.c.SUPPRESS)
            where.append(suppress)

        if 'stype1' in attr:
            stype1 = attr['stype1']
            where.append(table.c.STYPE1 == stype1)

        # s = select([distinct(table.c.CUI1) ]).where(and_(*where))
        s = select([table]).where(and_(*where))

        if 'sabOrder' in attr:
            sabOrder = self._valCase(attr['sabOrder'], table.c.SAB)
            s = s.order_by(sabOrder)

        return self._execDict(s)

    def concept(self, cui, **attr):
        table = self.getTable('MRCONSO')
        where = [table.c.CUI == cui]

        awh = self._attrs(attr, table.c)
        where.extend(awh)

        s = select([table]).where(and_(*where))

        if 'sabOrder' in attr:
            sabOrder = self._valCase(attr['sabOrder'], table.c.SAB)
            s = s.order_by(sabOrder)

        return self._execDict(s)

    def aui(self, aui, **attr):
        table = self.getTable('MRCONSO')
        where = [table.c.AUI == aui]

        awh = self._attrs(attr, table.c)
        where.extend(awh)

        s = select([table]).where(and_(*where))

        res = self._execDict(s)
        if len(res) == 0:
            return None
        else:
            return res[0]

    def concepts(self, offset=0, limit=100, **attr):
        table = self.getTable('MRCONSO')
        # where = [ table.c.LAT == 'ENG' ]
        where = []

        awh = self._attrs(attr, table.c)
        where.extend(awh)

        s = select([table]).where(and_(*where))  \
            .limit(limit).offset(offset)         \
            .order_by(table.c.AUI)

        if 'sabOrder' in attr:
            sabOrder = self._valCase(attr['sabOrder'], table.c.SAB)
            s = s.order_by(sabOrder)

        return self._execDict(s)

    def cuis(self, offset=0, limit=100, **attr):
        table = self.getTable('MRCONSO')
        # where = [ table.c.LAT == 'ENG' ]
        where = []

        awh = self._attrs(attr, table.c)
        where.extend(awh)

        s = select([distinct(table.c.CUI)]).where(and_(*where)) \
            .limit(limit).offset(offset).order_by(table.c.AUI)

        if 'sabOrder' in attr:
            sabOrder = self._valCase(attr['sabOrder'], table.c.SAB)
            s = s.order_by(sabOrder)

        return self._exec1(s)

    def semTypes(self, cui):
        table = self.getTable('MRSTY')
        where = [table.c.CUI == cui]

        s = select([table.c.STY]).where(and_(*where))

        return self._exec1(s)

    def tuis(self, cui):
        table = self.getTable('MRSTY')
        where = [table.c.CUI == cui]

        s = select([table.c.TUI]).where(and_(*where))

        return self._exec1(s)

    def terms(self, cui, **attr):
        """returns distinct terms for the given cui"""
        table = self.getTable('MRCONSO')
        where = [table.c.CUI == cui]

        awh = self._attrs(attr, table.c)
        where.extend(awh)

        s = select([distinct(table.c.STR)]).where(and_(*where))

        if 'sabOrder' in attr:
            sabOrder = self._valCase(attr['sabOrder'], table.c.SAB)
            s = s.order_by(sabOrder)

        return self._exec1(s)

    def synonyms(self, cui, **attr):
        table = self.getTable('MRREL')
        where = [table.c.REL == 'SY']
        where.append(table.c.CUI2 == cui)
        where.append(table.c.CUI1 != cui)

        if 'sab' in attr:
            sab = self._list(attr['sab'], table.c.SAB)
            where.append(sab)

        s = select([table]).where(and_(*where))

        if 'sabOrder' in attr:
            sabOrder = self._valCase(attr['sabOrder'], table.c.SAB)
            s = s.order_by(sabOrder)

        return self._exec(s)

    def defn(self, cui, **attr):
        table = self.getTable('MRDEF')
        where = [table.c.CUI == cui]

        s = select([table]).where(and_(*where))

        if 'sabOrder' in attr:
            sabOrder = self._valCase(attr['sabOrder'], table.c.SAB)
            s = s.order_by(sabOrder)

        res = self._execDict(s)
        if len(res) == 0:
            return None
        else:
            return res[0]
