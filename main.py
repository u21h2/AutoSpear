import os
import time
import copy
import numpy as np
from attackers.mcts.mcts import Auxiliary
import global_vars
from global_vars import input_args
from classifiers.clients.ml_client import MLClient
from classifiers.clients.wafaas_client import WAFaasClient
from attackers.attacker import Attacker
from utils.parser.parser import SQLTree
from utils.cfg.cfg_conf import CFG_CONF
from utils.misc.misc_utils import read_payloads


def main():

    np.random.seed(0)

    if input_args.pattern == 'ML':
        assert(not input_args.ML_url == 'default')
        blackbox = True if input_args.ML_box == 'blackbox_without_score' else False
        clsf = MLClient(base_url=input_args.ML_url, thresh=input_args.ML_thresh, blackbox=blackbox)
        request_method = 'ML'
        
    elif input_args.pattern == 'WAFaas':
        assert(not input_args.WAFaas_url == 'default')
        blackbox = True
        clsf = WAFaasClient(base_url=input_args.WAFaas_url, sleep_time=0.001, cookie=input_args.cookie)
        request_method = input_args.request_method

    BENIGN_PAYLOADS_PATH = 'payload_benign.txt'
    attacker = Attacker()
    attacker.load_cfgs(CFG_CONF)
    attacker.load_benign_payloads(BENIGN_PAYLOADS_PATH)

    payload_path = 'payload_single.txt' if input_args.payload_number == 'single' else 'payload_multiple.txt'
    payloads = read_payloads(payload_path)
    begin_time = time.time()
    begin_time_str = time.strftime("%m-%d#%H-%M-%S", time.localtime())

    log_path = 'logs/{}'.format(begin_time_str)
    os.mkdir(log_path)

    guide = input_args.guide
    max_attempts = input_args.max_attempts
    max_steps = input_args.max_steps
    pattern = input_args.pattern
    tree_mutate_pattern = input_args.tree_mutate_pattern

    fbenign = open('{}/{}-{}-{}#benign.log'.format(log_path, pattern, request_method, guide), 'a+')
    fexcept = open('{}/{}-{}-{}#except.log'.format(log_path, pattern, request_method, guide), 'a+')
    fsummary = open('{}/{}-{}-{}#summary.log'.format(log_path,
                    pattern, request_method, guide), 'a+')

    counter = {'total': len(payloads), 'success': 0, 'benign': 0, 'except': 0, 'failure': 0}

    for idx, payload in enumerate(payloads):
        run_res = _run(idx, attacker, payload, log_path, clsf=clsf, guide=guide, max_attempts=max_attempts,
                       max_steps=max_steps, pattern=pattern, request_method=request_method,blackbox=blackbox, tree_mutate_pattern=tree_mutate_pattern)
        if run_res['benign']:
            print(idx, payload, file=fbenign, flush=True)
            counter['benign'] = counter['benign'] + 1
        elif run_res['except']:
            print(idx, payload, run_res['except'], file=fexcept, flush=True)
            counter['except'] = counter['except'] + 1
        elif run_res['success']:
            print(idx, 'success', run_res['min_score_payload'].encode())
            counter['success'] = counter['success'] + 1
        else:
            counter['failure'] = counter['failure'] + 1

    end_time = time.time()
    time_consume = end_time - begin_time

    print("================Summary================")
    if input_args.pattern == 'ML':
        print("Guide: {}, Model url: {}, Model thresh: {}, Blackbox: {}".format(
            guide, input_args.ML_url, input_args.ML_thresh, input_args.ML_box))
        print("Guide: {}, Model url: {}, Model thresh: {}, Blackbox: {}".format(
            guide, input_args.ML_url, input_args.ML_thresh, input_args.ML_box), file=fsummary, flush=True)
    elif input_args.pattern == 'WAFaas':
        print("WAFaas url: {}, Request method:{}, Cookie:{}".format(
            input_args.WAFaas_url, input_args.request_method, input_args.cookie))
        print("WAFaas url: {}, Request method:{}, Cookie:{}".format(input_args.WAFaas_url,
              input_args.request_method, input_args.cookie), file=fsummary, flush=True)
    print("Total payloads: {}, Success: {}, Failure: {}, Benign: {}, Except: {}".format(
        counter['total'], counter['success'], counter['failure'], counter['benign'], counter['except']))
    print("Total payloads: {}, Success: {}, Failure: {}, Benign: {}, Except: {}".format(
        counter['total'], counter['success'], counter['failure'], counter['benign'], counter['except']), file=fsummary, flush=True)
    print("Total time consuming: {}h/{}m/{}s".format(round(time_consume/3600, 4),
                                                     round(time_consume/60, 4), round(time_consume, 4)))
    print("Total time consuming: {}h/{}m/{}s".format(round(time_consume/3600, 4),
                                                     round(time_consume/60, 4), round(time_consume, 4)), file=fsummary, flush=True)
    print("For detauil log, please see {}/".format(log_path))


def _run(idx, attacker, payload, log_path, clsf, guide, max_attempts, max_steps, pattern, request_method, blackbox, tree_mutate_pattern):
    fdetail = open('{}/{}-{}-{}#detail.log'.format(log_path, pattern, request_method, guide), 'a+')
    fsuccess = open('{}/{}-{}-{}#succes.log'.format(log_path, pattern, request_method, guide), 'a+')

    try:
        init_SQLtree = SQLTree(payload)
    except:
        run_res = {'success': False, 'except': 'Parse Fail', 'benign': False}
        return run_res

    init_score = clsf.get_score(payload)
    threshold = clsf.get_thresh()

    min_score = init_score
    min_score_payload = payload

    # benign
    if init_score <= threshold:
        run_res = {'success': False, 'except': None, 'benign': True}
        return run_res

    except_count = 0
    except_detail = ''

    for attempt in range(max_attempts):
        try:
            _SQLtree = SQLTree(payload)
            # random attack
            if guide == 'random':
                attack_res = attacker.random_attack(idx=idx, attempt=attempt+1, max_attempts=max_attempts,
                                                    fdetail=fdetail, fsuccess=fsuccess, tree=_SQLtree, clsf=clsf, max_steps=max_steps, tree_mutate_pattern=tree_mutate_pattern)
            # guided by mcts
            elif guide == 'mcts':
                attack_res = attacker.mcts_attack(idx=idx, attempt=attempt+1, max_attempts=max_attempts, fdetail=fdetail, fsuccess=fsuccess,
                                                  tree=_SQLtree,clsf=clsf, init_score=init_score, max_steps=max_steps, computation_budget=10, blackbox=blackbox, tree_mutate_pattern=tree_mutate_pattern)
            # success
            if attack_res['success']:
                run_res = {'success': True, 'except': None, 'benign': False,
                           'min_score': attack_res['min_score'], 'min_score_payload': attack_res['min_score_payload']}
                return run_res

            if min_score < attack_res['min_score']:
                min_score = attack_res['min_score']
                min_score_payload = attack_res['min_score_payload']
        except Exception as e:
            print(e)
            except_detail = str(e)
            except_count += 1
            continue

    # except when attack
    if except_count == max_attempts:
        run_res = {'success': False, 'except': 'Attack Fail:'+except_detail, 'benign': False}
        return run_res

    # failure
    run_res = {'success': False, 'except': None, 'benign': False,
               'min_score': min_score, 'min_score_payload': min_score_payload}
    return run_res


if __name__ == "__main__":
    main()


"""
python main.py -p WAFaas -WAFu http://10.15.196.135:8088/foo -pn multiple
python main.py -p WAFaas -WAFu http://10.15.196.135:8088/foo -pn multiple -g mcts
python main.py -p ML -MLu http://127.0.0.1:9001/wafbrain -MLt 0.1 -MLb blackbox_with_score -pn multiple -g mcts
python main.py -p ML -MLu http://127.0.0.1:9002/lstm -MLt 0.1 -MLb blackbox_with_score -pn multiple -g mcts
python main.py -p ML -MLu http://127.0.0.1:9003/cnn -MLt 0.1 -MLb blackbox_without_score -pn multiple -g random
"""