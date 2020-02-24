import re
import string
import sys
import unicodedata
import functools
from threading import Thread

from ln2sql.parsingException import ParsingException
from ln2sql.query import *

class OrderByParser(Thread):
    def __init__(self, phrases, tables_of_from, asc_keywords, desc_keywords, database_dico, database_object):
        Thread.__init__(self)
        self.order_by_objects = []
        self.phrases = phrases
        self.tables_of_from = tables_of_from
        self.asc_keywords = asc_keywords
        self.desc_keywords = desc_keywords
        self.database_dico = database_dico
        self.database_object = database_object

    def get_tables_of_column(self, column):
        tmp_table = []
        for table in self.database_dico:
            if column in self.database_dico[table]:
                tmp_table.append(table)
        return tmp_table

    def get_column_name_with_alias_table(self, column, table_of_from):
        one_table_of_column = self.get_tables_of_column(column)[0]
        tables_of_column = self.get_tables_of_column(column)
        if table_of_from in tables_of_column:
            return str(table_of_from) + '.' + str(column)
        else:
            return str(one_table_of_column) + '.' + str(column)

    def intersect(self, a, b):
        return list(set(a) & set(b))

    def predict_order(self, phrase):
        if (len(self.intersect(phrase, self.desc_keywords)) >= 1):
            return 'DESC'
        else:
            return 'ASC'

    def run(self):
        for table_of_from in self.tables_of_from:
            order_by_object = OrderBy()
            for phrase in self.phrases:
                for i in range(0, len(phrase)):
                    for table_name in self.database_dico:
                        columns = self.database_object.get_table_by_name(table_name).get_columns()
                        for column in columns:
                            if (phrase[i] == column.name) or (phrase[i] in column.equivalences):
                                column_with_alias = self.get_column_name_with_alias_table(column.name, table_of_from)
                                order_by_object.add_column(column_with_alias, self.predict_order(phrase))
            self.order_by_objects.append(order_by_object)

    def join(self):
        Thread.join(self)
        return self.order_by_objects