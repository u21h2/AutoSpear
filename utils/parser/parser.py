import re
import sys
import sqlparse
from utils.parser.tree import Tree
from global_vars import input_args
# from sql_metadata import Parser

class SQLTree():
    def __init__(self, raw_statement):
        self.raw_statement = raw_statement

        self.raw_left_boundary_statement = None
        self.raw_query_statement = None
        self.raw_right_boundary_statement = None

        self.left_boundary_tree = Tree()
        self.query_tree = Tree()
        self.right_boundary_tree = Tree()

        self.variable_corpus = []

        self.parse_mode = 0  # 0->query 1->left_boundary&query 2->left_boundary&query&right_boundary

        self.parse_raw_statement()

    def get_parse_mode(self):
        return self.parse_mode

    def get_variable_corpus(self):
        return self.variable_corpus

    def parse_tables_and_columns(self, stmt):
        # 
        # try:
        #     return Parser(stmt).tables + Parser(stmt).columns
        # except:
        #     return []
        #
        return []

    def parse_raw_statement(self):
        parsed = sqlparse.parse(self.raw_statement)
        """
        simple demo
        """
        if len(parsed) == 1:
            idx = self.raw_statement.find("'")
            idx_space = self.raw_statement.find(" ")
            if not 0 < idx < 10:
                idx = self.raw_statement.find("‘")
            if not 0 < idx < 10:
                idx = self.raw_statement.find('"')
            if not 0 < idx < 10:
                idx = self.raw_statement.find(";")
            if 0 < idx < 10 and (idx_space == 0 or idx < idx_space):
                """
                1' or xxxxxxx
                """
                self.raw_left_boundary_statement = self.raw_statement[:idx+1]
                self.left_boundary_tree.parse_tokens(sqlparse.parse(self.raw_left_boundary_statement))
                self.raw_query_statement = self.raw_statement[idx+1:]
                self.query_tree.parse_tokens(sqlparse.parse(self.raw_query_statement))
                self.variable_corpus += self.parse_tables_and_columns(self.raw_left_boundary_statement)
                self.variable_corpus += self.parse_tables_and_columns(self.raw_query_statement)
                self.parse_mode = 1
            else:
                self.raw_query_statement = self.raw_statement
                self.query_tree.parse_tokens(parsed[0])
                self.variable_corpus += self.parse_tables_and_columns(self.raw_query_statement)
                self.parse_mode = 0
        elif len(parsed) > 1:
            self.raw_left_boundary_statement = str(parsed[0])
            self.left_boundary_tree.parse_tokens(parsed[0])
            self.raw_query_statement = str(parsed[1])
            self.query_tree.parse_tokens(parsed[1])
            self.variable_corpus += self.parse_tables_and_columns(self.raw_query_statement)
            self.parse_mode = 1
            if len(parsed) == 3:
                self.raw_right_boundary_statement = str(parsed[2])
                self.right_boundary_tree.parse_tokens(parsed[2])
                self.parse_mode = 2
        if len(parsed) > 3:
            print('***parse error***',self.raw_statement)
            raise Exception

    def output(self):
        res = self.left_boundary_tree.output_simple() + self.query_tree.output_simple() + self.right_boundary_tree.output_simple()
        if input_args.request_method in ['GET','GET(JSON)','POST']:
           res = res.replace('&&',' %26%26 ')
        return res

    def output_query(self):
        return self.query_tree.output_simple()

    def dev_output(self):
        self.query_tree.output_detail()