CFG_CONF = {
    # 1=1, 1 = 1, 2.6 = 2.6, -3.7 = -3.7, 1 = 1.0 '1'='1' 'foo'='foo'
    'T_Comparison': ['F_tautology_number', 'F_tautology_complex','F_tautology_string','True_Query'],

    # Logical expression

    'and': ['F_And'],
    
    'or': ['F_Pipe'],

    '=':['space like space'],

    # Generate one or more spaces

    'space':['F_Space','space F_Space'],
    # 'space':['F_Space'],


    # Directly use ' ' is the way of string matching,'T_Whitespace' is the form of sql parsing and matching

    # ' ': ['F_Whitespace_Alternatives', 'Left_Inline_Comment Inline_Comment Right_Inline_Comment'],
    'T_Whitespace': ['F_Whitespace_Alternatives', 'Left_Inline_Comment Inline_Comment Right_Inline_Comment'],
    
    # Comment
    'Left_Inline_Comment': ['Inline_Comment_Slash Left_Inline_Comment_Asterisk'],
    'Left_Inline_Comment_Asterisk': ['Left_Inline_Comment_Asterisk *', '*'],
    'Right_Inline_Comment': ['Right_Inline_Comment_Asterisk Inline_Comment_Slash'],
    'Right_Inline_Comment_Asterisk': ['Right_Inline_Comment_Asterisk *', '*'],
    'Inline_Comment_Slash': ['/'],
    'Inline_Comment': ['F_Inline_Comment_Random', 'F_Inline_Comment_Benign', 'F_Inline_Comment_Random_Sentense'],

    # rewirte recomment
    'T_Comment':['Left_Inline_Comment Inline_Comment Right_Inline_Comment'],

    # swap case
    'T_Any_But_Whitespace':['A_Swap_Cases','A_Inline_Comment'],

    # where
    'where':['F_The_where False_Query or','F_The_where True_Query and'],
    'Bool_Query':['True_Query','False_Query'],
    'True_Query':['F_True_Query','True_Query space and space F_True_Query'],
    'False_Query':['F_False_Query','False_Query space or space F_False_Query'],

    # swap integer base
    'T_Number':['A_Swap_Integer_Base'],
    

}

CFG_CONF_ENTRY = {
    # Comparsion or Tautology
    'S_Comparsion':['T_Comparison',CFG_CONF['T_Comparison']],
    # and
    'S_Logical_and':['and',CFG_CONF['and']],
    # or
    'S_Logical_or':['or',CFG_CONF['or']],
    # =
    'S_Equal':['=',CFG_CONF['=']],
    # space 
    'S_Whitespace':['T_Whitespace',CFG_CONF['T_Whitespace']],
    # anything except space
    'S_Any_But_Whitespace':['T_Any_But_Whitespace',CFG_CONF['T_Any_But_Whitespace']],
    # where
    'S_where':['where',CFG_CONF['where']],
    # number
    'S_Number':['T_Number',CFG_CONF['T_Number']],
    # comment
    'S_Comment':['T_Comment',CFG_CONF['T_Comment']]
}
