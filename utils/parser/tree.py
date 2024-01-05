import sqlparse
import sys
from sqlparse import sql
from global_vars import input_args
from utils.misc.misc_utils import is_number
from utils.parser.semantic_type import TOKEN_TYPE_DICT
from utils.cfg.cfg_conf import CFG_CONF_ENTRY


class Tree:
    def __init__(self, level=0, parent=0):
        self.level = level
        self.parent = parent
        self.max_idx = 0
        self.leaves = {}
        self.out_buffer = ''

    def parse_tokens(self, tokens):
        for token in tokens:
            self.add(Node(token))

    def add(self, node):
        node.set_level(self.level)
        node.set_parent(self.parent)
        node.set_index(self.max_idx)
        res = node.parse_child(self.parent, node.token)
        self.leaves[self.max_idx] = node
        self.max_idx = self.max_idx + 1
        if res:
            self.add(Node(sqlparse.parse('select ')[0][1]))

    def output_line(self):
        """
        Output from the root node
        """
        res = ''
        for i in self.leaves:
            res += str(self.parse_idx(self.leaves[i])
                       )+str(self.leaves[i].token)+"|"
        print(res)

    def output_simple(self, *partial_tree):
        """
        Output from the leaf node (not printing)
        Variable parameters, adapt to recursive and non-recursive situations
        Only add a newline at the outermost layer
        Simple mode without special symbols
        """
        if not partial_tree:
            t = self
            self.out_buffer = ''
        else:
            t = partial_tree[0]
        for i in t.leaves:
            if not t.leaves[i].has_child:
                # if t.leaves[i].token.value == "\\n":
                #     self.out_buffer += "\\"
                #     self.out_buffer += "n"
                # elif t.leaves[i].token.value == "\\t":
                #     self.out_buffer += "\\"
                #     self.out_buffer += "t"
                if input_args.request_method in ['GET','GET(JSON)','POST'] and t.leaves[i].token.value == "&&":
                    self.out_buffer += "%26"
                    self.out_buffer += "%26"
                else:
                    self.out_buffer += str(t.leaves[i].token)
            else:
                self.output_simple(t.leaves[i].child)
        return self.out_buffer.replace('\\t','\t').replace('\\n','\n')

    def output_detail(self, *partial_tree):
        """
        Output from the leaf node
        Variable parameters, adapt to recursive and non-recursive situations
        Only add a newline at the outermost layer
        """
        t = self if not partial_tree else partial_tree[0]
        for i in t.leaves:
            if not t.leaves[i].has_child:
                print("(l{}f{}i{})".format(
                    t.leaves[i].level, t.leaves[i].parent, t.leaves[i].index), end="")
                print(str(t.leaves[i].token), end="|")
            else:
                print("(l{}f{}i{})".format(
                    t.leaves[i].level, t.leaves[i].parent, t.leaves[i].index), end="<")
                self.output_detail(t.leaves[i].child)
                print(end=">")
        if not partial_tree:
            print()
    def output_detail_detail(self, *partial_tree):
        """
        Output from the leaf node
        Variable parameters, adapt to recursive and non-recursive situations
        Only add a newline at the outermost layer
        """
        t = self if not partial_tree else partial_tree[0]
        for i in t.leaves:
            if not t.leaves[i].has_child:
                print("(l{}f{}i{})".format(
                    t.leaves[i].level, t.leaves[i].parent, t.leaves[i].index), end="")
                print(str(t.leaves[i].token),'!!!',t.leaves[i].ttype, end="|")
            else:
                print("(l{}f{}i{})".format(
                    t.leaves[i].level, t.leaves[i].parent, t.leaves[i].index), end="<")
                self.output_detail_detail(t.leaves[i].child)
                print(end=">")
        if not partial_tree:
            print()
    def verify_conditions(self, type, token):
        if type == 'Comparison':
            """
            1=1
            1 = 1
            2.6 = 2.6
            -3.7 = -3.7
            1 = 1.0
            '1' = '1'
            """
            try:
                res = is_number(token.value.split('=')[0].strip()) and is_number(token.value.split('=')[1].strip()) and float(token.value.split('=')[0].strip()) == float(token.value.split('=')[1].strip())
                if res:
                    return True
                res = token.value.split('=')[0].strip() == token.value.split('=')[1].strip()
                if res:
                    return True
                return False
            except:
                return False
        if type == 'Comment':
            return True
        return False

    def search_locations_could_be_manipulated(self,entry, *partial_tree):
        """
        Recursively find all positions, return the position index and the prod of CFG
        """
        if not partial_tree:
            t = self
            self.search_res = []
        else:
            t = partial_tree[0]
        stmt = CFG_CONF_ENTRY[entry][0]
        for i in t.leaves:
            if not t.leaves[i].has_child:
                if stmt.startswith('T_'):
                    token_name = stmt.split('T_')[1]
                    if TOKEN_TYPE_DICT[token_name][1] == None:
                        if type(t.leaves[i].token) == TOKEN_TYPE_DICT[token_name][0] and self.verify_conditions(token_name, t.leaves[i].token):
                            self.search_res.append(
                                (t.leaves[i].level, t.leaves[i].parent, t.leaves[i].index, t.leaves[i].value, entry))
                            # print((t.leaves[i].level, t.leaves[i].parent, t.leaves[i].index, t.leaves[i].value, entry))
                    else:
                        for _type in TOKEN_TYPE_DICT[token_name][1]:
                            if str(t.leaves[i].ttype) == _type:
                                self.search_res.append(
                                    (t.leaves[i].level, t.leaves[i].parent, t.leaves[i].index, t.leaves[i].value, entry))
                                # print((t.leaves[i].level, t.leaves[i].parent, t.leaves[i].index, t.leaves[i].value, entry))    
                # and
                elif t.leaves[i].value == stmt:
                    self.search_res.append(
                        (t.leaves[i].level, t.leaves[i].parent, t.leaves[i].index, t.leaves[i].value, entry))
                    # print((t.leaves[i].level, t.leaves[i].parent, t.leaves[i].index, t.leaves[i].value, entry))
            else:
                self.search_locations_could_be_manipulated(entry,t.leaves[i].child)
        return self.search_res

    def search(self, stmt, *partial_tree):
        """
        Search recursively according to stmt, and return the index of the found node: (level, parent, index, value)
        """
        if not partial_tree:
            t = self
            self.search_res = []
        else:
            t = partial_tree[0]
        for i in t.leaves:
            if not t.leaves[i].has_child:
                if stmt.startswith('T_'):
                    token_name = stmt.split('T_')[1]

                    # "Comparison": [sqlparse.sql.Comparison, None]
                    if TOKEN_TYPE_DICT[token_name][1] == None:
                        # print(t.leaves[i].token, type(t.leaves[i].token) , TOKEN_TYPE_DICT[token_name][0])
                        if type(t.leaves[i].token) == TOKEN_TYPE_DICT[token_name][0] and self.verify_conditions(token_name, t.leaves[i].token):
                            self.search_res.append(
                                (t.leaves[i].level, t.leaves[i].parent, t.leaves[i].index, t.leaves[i].value))
                    # "Whitespace": [sqlparse.sql.Token, 'Token.Text.Whitespace']
                    else:
                        for _type in TOKEN_TYPE_DICT[token_name][1]:
                            if str(t.leaves[i].ttype) == _type:
                                self.search_res.append(
                                    (t.leaves[i].level, t.leaves[i].parent, t.leaves[i].index, t.leaves[i].value))
                # and
                elif t.leaves[i].value == stmt:
                    self.search_res.append(
                        (t.leaves[i].level, t.leaves[i].parent, t.leaves[i].index, t.leaves[i].value))
            else:
                self.search(stmt, t.leaves[i].child)
        return self.search_res

    def replace_node(self, stmt, target_stmt, target_node, idx_tuple, *partial_tree):
        """
        idx_tuple: (level,parent,index,value)
        """
        t = self if not partial_tree else partial_tree[0]
        for idx, i in enumerate(t.leaves):
            if not t.leaves[i].has_child:
                if self.compare_idx(t.leaves[i], idx_tuple):
                    # print('修改调试信息',idx_tuple, self.parse_idx(t.leaves[i]), str.encode(stmt), str.encode(t.leaves[i].value))
                    target_node.set_level(idx_tuple[0])
                    target_node.set_parent(idx_tuple[1])
                    target_node.set_index(idx_tuple[2])
                    target_node.parse_child(idx_tuple[1], target_node.token)
                    t.leaves[i] = target_node
            else:
                self.replace_node(stmt, target_stmt, target_node,
                                  idx_tuple, t.leaves[i].child)

    def parse_idx(self, node):
        return (node.level, node.parent, node.index)

    def compare_idx(self, node, idx_tuple):
        return node.level == idx_tuple[0] and node.parent == idx_tuple[1] and node.index == idx_tuple[2]

    # def delete_node(self,)

class Node:
    def __init__(self, token: sqlparse.sql.Token) -> None:
        self.parent = ''
        self.level = 0
        self.index = None
        self.token = token
        self.value = str(token)
        self.type = type(token)
        self.ttype = token.ttype
        self.has_child = False
        self.child = None

    def set_level(self, level):
        self.level = level

    def set_index(self, index):
        self.index = index

    def set_parent(self, parent):
        self.parent = parent

    def replace_token(self, token):
        self.token = token
        self.value = str(token)
        self.ttype = token.ttype

    def parse_child(self, parent, token):
        """
        In some cases, the subtree of node needs to be extracted
        Determine whether recursive solution is needed
        """
        if isinstance(token, sqlparse.sql.IdentifierList) or isinstance(token, sqlparse.sql.Where):
            self.has_child = True
            self.child = Tree(level=self.level+1,
                              parent=str(parent)+'-'+str(self.index))
            for t in token:
                self.child.add(Node(t))
        elif not (isinstance(token, sqlparse.sql.Identifier)  or isinstance(token, sqlparse.sql.Function) or isinstance(token, sqlparse.sql.Comment)):
            try:
                if len(self.token.tokens) > 1:
                    self.has_child = True
                    self.child = Tree(level=self.level+1,
                                      parent=str(parent)+'-'+str(self.index))
                    for t in token:
                        self.child.add(Node(t))
            except:
                pass
        elif isinstance(token, sqlparse.sql.Comparison):
            try:
                if len(self.token.tokens) > 1:
                    self.has_child = True
                    self.child = Tree(level=self.level+1,
                                      parent=str(parent)+'-'+str(self.index))
                    for t in token:
                        self.child.add(Node(t))
            except:
                pass