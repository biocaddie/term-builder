#!/usr/bin/env python
# -*- coding: utf-8
"""
    Database stored terminology management utilities.

    Base terminology table to access classes to process
    a generic terminology

    Created on   : 2014-05-28 ( esoysal@gmail.com )
    Last modified: Aug 07, 2015, Fri 14:37:31 -0500

"""

from sqlalchemy import MetaData, Table
from sqlalchemy import select, and_, or_
from sqlalchemy import join, distinct, case
from sqlalchemy.orm import sessionmaker

class TermTable(object):
    def __init__(self, engine, prefix =''):
        self.engine = engine

        ## Session
        #Session = sessionmaker(bind=engine)
        #self.session = Session()

        self.conn = None
        self.result = None
        self.prefix = prefix
        self.metadata = MetaData()
        #self.metadata.bind = engine
        self.tables = dict()
        self._open()

    def __del__(self):
        self._close()

    def __enter__(self):
        return(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()

    def _open(self):
        self.conn = self.engine.connect()
        self.conn.execution_options(stream_results=True)

    def _close(self):
        if not self.result is None:
            self.result.close()
            self.result = None

        if not self.conn is None:
            self.conn.close()
            self.conn = None

    def _exec(self, sql):
        if not self.result is None:
            self.result.close()

        self.result = self.conn.execute(sql)
        return self.result.fetchall()

    def _exec1(self, sql):
        """returns a list of first column for the resultset.
        Use carefully on large resultsets"""
        result = self._exec(sql)
        return [row[0] for row in result]

    def _execDict(self, sql):
        if not self.result is None:
            self.result.close()

        self.result = self.conn.execute(sql)
        res = []
        for row in self.result:
            res.append({c[0]: c[1] for c in row.items()})

        return res

    def _list(self, val, fld):
        """allow val to be an list, tupple or a primitive"""
        if isinstance(val, (list, tuple)):
            if len(val) == 1:
                return fld == val[0]
            else:
                return fld.in_(val)
        else:
            return fld == val

    def _valCase(self, vals, fld, defVal=999999):
        res = {}
        i = 1
        for v in vals:
            res[v] = i
            i += 1

        return case(res, value=fld, else_ = defVal)

    def getTable(self, tablename):
        """Generate a table object using schema definition.
        Maintain a single instance using a dict object."""
        tablename = self.prefix + tablename
        if not tablename in self.tables:
            self.tables[tablename] = Table( tablename, self.metadata, \
                    autoload=True, autoload_with=self.conn )

        return self.tables[tablename]

