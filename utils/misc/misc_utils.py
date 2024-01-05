import random


def is_number(s):
    """
    chech number in str
    """
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def shuffle_dic(dicts):
    """
    shuffle dic
    """
    dict_key_ls = list(dicts.keys())
    random.shuffle(dict_key_ls)
    new_dic = {}
    for key in dict_key_ls:
        new_dic[key] = dicts.get(key)
    return new_dic


def read_payloads(path):
    payloads = []
    with open(path) as f:
        while True:
            line = f.readline().strip()
            if line:
                payloads.append(line+' ')
            else:
                break
    return payloads
