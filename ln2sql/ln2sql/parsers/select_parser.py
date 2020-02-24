import re
import string
import sys
import unicodedata
import functools
from threading import Thread


from ln2sql.parsingException import ParsingException
from ln2sql.query import *

class SelectParser(Thread):
    def __init__(self, columns_of_select, tables_of_from, phrase, count_keywords, sum_keywords, average_keywords,
                 max_keywords, min_keywords, distinct_keywords, database_dico, database_object):
        Thread.__init__(self)
        self.select_objects = []
        self.columns_of_select = columns_of_select
        self.tables_of_from = tables_of_from
        self.phrase = phrase
        self.count_keywords = count_keywords
        self.sum_keywords = sum_keywords
        self.average_keywords = average_keywords
        self.max_keywords = max_keywords
        self.min_keywords = min_keywords
        self.distinct_keywords = distinct_keywords
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

    def uniquify(self, list):
        already = []
        for element in list:
            if element not in already:
                already.append(element)
        return already

    def run(self):
        for table_of_from in self.tables_of_from:  # for each query
            self.select_object = Select()
            is_count = False
            self.columns_of_select = self.uniquify(self.columns_of_select)
            number_of_select_column = len(self.columns_of_select)

            if number_of_select_column == 0:
                select_type = []
                for count_keyword in self.count_keywords:
                    lower_self_phrase = ' '.join(word.lower() for word in self.phrase)
                    if count_keyword in lower_self_phrase:
                        select_type.append('COUNT')

                self.select_object.add_column(None, self.uniquify(select_type))
            else:
                select_phrases = []
                previous_index = 0

                for i in range(0, len(self.phrase)):
                    for column_name in self.columns_of_select:
                        if (self.phrase[i] == column_name) or (
                                    self.phrase[i] in self.database_object.get_column_with_this_name(column_name).equivalences):
                            select_phrases.append(self.phrase[previous_index:i + 1])
                            previous_index = i + 1

                select_phrases.append(self.phrase[previous_index:])

                for i in range(0, len(select_phrases)):
                    select_type = []

                    phrase = [word.lower() for word in select_phrases[i]]

                    for keyword in self.average_keywords:
                        if keyword in phrase:
                            select_type.append('AVG')
                    for keyword in self.count_keywords:
                        if keyword in phrase:
                            select_type.append('COUNT')
                    for keyword in self.max_keywords:
                        if keyword in phrase:
                            select_type.append('MAX')
                    for keyword in self.min_keywords:
                        if keyword in phrase:
                            select_type.append('MIN')
                    for keyword in self.sum_keywords:
                        if keyword in phrase:
                            select_type.append('SUM')
                    for keyword in self.distinct_keywords:
                        if keyword in phrase:
                            select_type.append('DISTINCT')

                    if (i != len(select_phrases) - 1):
                        column = self.get_column_name_with_alias_table(self.columns_of_select[i], table_of_from)
                        self.select_object.add_column(column, self.uniquify(select_type))

            self.select_objects.append(self.select_object)

    def join(self):
        Thread.join(self)
        return self.select_objects