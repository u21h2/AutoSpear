import sqlparse
TOKEN_TYPE_DICT = {
    "Comparison": [sqlparse.sql.Comparison, None],
    "Whitespace": [sqlparse.sql.Token, ['Token.Text.Whitespace']],
    "Any_But_Whitespace": [sqlparse.sql.Token, ['Token.Keyword', 'Token.Keyword.DML']],
    "Number": [sqlparse.sql.Token, ['Token.Literal.Number.Integer']],
    'Comment': [sqlparse.sql.Comment, None],
    # 'DMLInlineComment':[sqlparse.sql.Token,['oken.Comment.Multiline']]
}
