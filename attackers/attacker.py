import re
import sqlparse
import random
import global_vars
import traceback
from collections import defaultdict
from utils.parser.tree import Node
from utils.cfg.cfg_func import *
from utils.cfg.cfg_conf import CFG_CONF_ENTRY
from utils.parser.parser import SQLTree
from attackers.mcts.mcts import Auxiliary, MCTS_Node, MCTS_ENTRY, MCTS


class Attacker:
    def __init__(self):
        self.cfg_prods = defaultdict(list)
        self.payload = None
        self.processed_payload = None

    def add_cfg(self, lhs, rhs):
        prods = rhs.split('|')
        for prod in prods:
            self.cfg_prods[lhs].append(tuple(prod.split()))

    def load_cfgs(self, cfgs):
        for key in cfgs:
            for value in cfgs[key]:
                self.add_cfg(key, value)

    def load_benign_payloads(self, path):
        with open(path) as f:
            while True:
                line = f.readline().strip()
                if line:
                    global_vars.benign_payloads.append(line)
                if not line:
                    break

    def weighted_choice(self, weights):
        rnd = random.random() * sum(weights)
        for i, w in enumerate(weights):
            rnd -= w
            if rnd < 0:
                return i

    def gen_random_convergent(self, symbol, arg='', cfactor=0.25, pcount=defaultdict(int)):
        sentence = ''
        weights = []
        for prod in self.cfg_prods[symbol]:
            if prod in pcount:
                weights.append(cfactor ** (pcount[prod]))
            else:
                weights.append(1.0)

        rand_prod = self.cfg_prods[symbol][self.weighted_choice(weights)]

        pcount[rand_prod] += 1

        for sym in rand_prod:
            if sym in self.cfg_prods:
                sentence += self.gen_random_convergent(
                    sym, cfactor=cfactor, pcount=pcount)
            else:
                if sym.startswith('F_'):
                    sym = eval(sym)()
                    sentence += sym
                elif sym.startswith('A_'):
                    sym = eval(sym)(arg)
                    sentence += sym
                else:
                    sentence += sym

        pcount[rand_prod] -= 1
        return sentence

    def search_before_attack(self, tree,tree_mutate_pattern):
        """
        Search out all the nodes that can be modified, return the index of the tree and the modifiable nodes and the modification method
        [(0,left_boundary_tree,[]),(1,query_tree,[]),(2,right_boundary_tree,[])]
        """
        operational_locations = []
        trees = [tree.left_boundary_tree, tree.query_tree, tree.right_boundary_tree]
        for i, p_t in enumerate(trees):
            search_res = []
            if tree_mutate_pattern == 'query' and not i == 1:
                operational_locations.append((i, p_t, search_res))
            else:
                for entry in CFG_CONF_ENTRY:
                    search_res += p_t.search_locations_could_be_manipulated(entry)
                operational_locations.append((i, p_t, search_res))
        return operational_locations

    def gen_before_attack(self, operational_locations, t=10):
        """
        Use CFG to generate a large number of replacement nodes
        t is the number of replacement nodes for each node 
        """
        operational_locations_and_nodes = []
        for (i, p_t, search_res) in operational_locations:
            _search_res = []
            for idx_tuple in search_res:
                prod = CFG_CONF_ENTRY[idx_tuple[4]][0]
                stmts = []
                for _ in range(t):
                    stmt = self.gen_random_convergent(prod, idx_tuple[3])
                    if stmt not in stmts:
                        stmts.append(stmt)
                    # print(prod,stmts)
                stmts_and_nodes = []
                for stmt in stmts:
                    if stmt in [' ', "\\t", "\\n"]:  # , "\\f", "\\v"]:
                        node = Node(sqlparse.parse('select'+stmt)[0][1])
                    else:
                        node = Node(sqlparse.parse(stmt)[0])
                    stmts_and_nodes.append((stmt, node))
                _search_res.append(idx_tuple+(stmts_and_nodes,))
            operational_locations_and_nodes.append((i, p_t, _search_res))
        """
        idx_tuple (0, 0, 5, '1 = 1', 'S_Comparsion', [(,),(,),(,)])
        """
        return operational_locations_and_nodes

    def sum_operational_locations(self, operational_locations):
        sum = 0
        for (_, _, search_res) in operational_locations:
            sum += len(search_res)
        return sum

    def __attack(self, attacker, tree, p_t, idx_tuple, verify_corpus=False, just_replace=False, node_idx=0):
        """
        the most basic attack i.e., do replace
        """
        if just_replace:
            p_t.replace_node(stmt=idx_tuple[3], target_stmt=idx_tuple[5][node_idx][0],
                             target_node=idx_tuple[5][node_idx][1], idx_tuple=idx_tuple)
        elif (not verify_corpus) or (not idx_tuple[3] in tree.variable_corpus):  # Skip table name and variable name
            prod = CFG_CONF_ENTRY[idx_tuple[4]][0]
            stmt = attacker.gen_random_convergent(prod, idx_tuple[3])
            if stmt in [' ', "\\t", "\\n"]:  # , "\\f", "\\v"]:
                node = Node(sqlparse.parse('select'+stmt)[0][1])
            else:
                node = Node(sqlparse.parse(stmt)[0])
            p_t.replace_node(stmt=prod, target_stmt=stmt,
                             target_node=node, idx_tuple=idx_tuple)

    def _attack(self, attacker, tree, idx_tuple, mode, verify_corpus=False, just_replace=False, node_idx=0):
        """
        Encapsulate specific attacks
        mode:
            0 partial_tree : No need to care which tree it is
            1 left_boundary
            2 query_boundary
            3 right_boundary
            4 all : all trees
        verify_corpus:
            False : No need to verify that the content to be modified is the database table name or field name, skip this step
            True
        """
        if mode == 0:
            self.__attack(attacker, tree, tree, idx_tuple, verify_corpus, just_replace, node_idx)
        elif mode == 1:
            self.__attack(attacker, tree, tree.left_boundary_tree,
                          idx_tuple, verify_corpus, just_replace, node_idx)
        elif mode == 2:
            self.__attack(attacker, tree, tree.query_tree,
                          idx_tuple, verify_corpus, just_replace, node_idx)
        elif mode == 3:
            self.__attack(attacker, tree, tree.right_boundary_tree,
                          idx_tuple, verify_corpus, just_replace, node_idx)
        elif mode == 4:
            self.__attack(attacker, tree, tree.left_boundary_tree,
                          idx_tuple, verify_corpus, just_replace, node_idx)
            self.__attack(attacker, tree, tree.query_tree,
                          idx_tuple, verify_corpus, just_replace, node_idx)
            self.__attack(attacker, tree, tree.right_boyndary_tree,
                          idx_tuple, verify_corpus, just_replace, node_idx)

    def random_attack(self, idx, attempt, max_attempts, fdetail, fsuccess, tree, clsf, max_steps=6, tree_mutate_pattern='all'):
        """
        random attack
        """
        min_score = 1
        min_score_payload = ''
        origin_output = tree.output()
        try:
            operational_locations = self.search_before_attack(tree,tree_mutate_pattern)
            if not self.sum_operational_locations(operational_locations):
                print('idx:{} [{}] can not parsed to a valid tree'.format(
                    idx, tree.output()))
                print('idx:{} [{}] can not parsed to a valid tree'.format(
                    idx, tree.output()), file=fdetail, flush=True)
                return {'success': False, 'except': 'can not parsed to a valid tree'}
            all_choices = []
            for (_, p_t, search_res) in operational_locations:  # No need to care which tree it is
                for idx_tuple in search_res:
                    all_choices.append((p_t, idx_tuple))
            astep = min(max_steps, len(all_choices))
            for stp in range(astep):
                p_t, idx_tuple = random.choice(all_choices)
                all_choices.remove((p_t, idx_tuple))
                self._attack(attacker=self, tree=p_t, idx_tuple=idx_tuple,
                             mode=0, verify_corpus=False)
                output = tree.output()
                score = clsf.get_score(output)
                # print("idx:{} attempt:{}/{}  {} {}".format(idx,attempt, max_attempts, score, output))
                print("idx:{} attempt:{}/{} step:{}/{}  {} {}".format(idx, attempt,
                      max_attempts, stp, astep, score, (output+" ").encode()), file=fdetail, flush=True)
                if score < min_score:
                    min_score = score
                    min_score_payload = output
                if score <= clsf.get_thresh():
                    # print(origin_output, file=fsuccess, flush=True)
                    print(idx, '\t', (origin_output+" ").encode(), file=fsuccess, flush=True)
                    print(idx, '\t', (output+" ").encode(), file=fsuccess, flush=True)
                    return {'success': True, 'except': None, 'benign': False, 'min_score': min_score, 'min_score_payload': min_score_payload, 'success_step': stp+1, 'max_step': astep}
        except Exception as e:
            print('EXCEPT', e)
            print('EXCEPT', e, file=fdetail, flush=True)
            traceback.print_exc()
            return {'success': False, 'except': 'attack except'}
        return {'success': False, 'except': None, 'benign': False, 'min_score': min_score, 'min_score_payload': min_score_payload, 'success_step': None, 'max_step': astep}

    def mcts_attack(self, idx, attempt, max_attempts, fdetail, fsuccess, tree, clsf, init_score, max_steps=6, computation_budget=10, blackbox=False, tree_mutate_pattern='all'):
        """
        attack guided by Monte-Carlo-Tree-Search 
        """
        origin_output = tree.output()
        min_score = 1
        min_score_payload = ''
        try:
            operational_locations = self.search_before_attack(tree,tree_mutate_pattern)
            operational_locations_and_nodes = self.gen_before_attack(operational_locations, t=20)
            if not self.sum_operational_locations(operational_locations):
                print('idx:{} [{}] can not parsed to a valid tree'.format(
                    idx, tree.output()))
                print('idx:{} [{}] can not parsed to a valid tree'.format(
                    idx, tree.output()), file=fdetail, flush=True)
                return {'success': False, 'except': 'can not parsed to a valid tree'}
            max_steps = min(max_steps, self.sum_operational_locations(operational_locations))

            auxiliary = Auxiliary(tree=tree, operational_locations=operational_locations_and_nodes, attacker=self, clsf=clsf,
                                    max_steps=max_steps, computation_budget=computation_budget)
            """
            init_score / 0
            """
            init_state = MCTS(auxiliary=auxiliary, init_score=init_score,
                                origin_payload=tree.output(), blackbox=blackbox)
            init_node = MCTS_Node()
            init_node.set_state(init_state)
            current_node = init_node

            for stp in range(max_steps):
                current_node, bypassed, bypassed_payload, stage = MCTS_ENTRY(current_node, auxiliary, mode='mctsfix')
                if bypassed:
                    print('The game ends during the exploration', idx, stage, bypassed_payload, file=fdetail, flush=True)
                    print(idx, '\t', origin_output.encode(), file=fsuccess, flush=True)
                    print(idx, '\t', bypassed_payload.encode(), file=fsuccess, flush=True)
                    return {'success': True, 'except': None, 'benign': False, 'min_score': clsf.get_score(bypassed_payload), 'min_score_payload': bypassed_payload, 'success_step': stp+1, 'max_step': max_steps}
                current_choice = current_node.get_state().get_integral_cumulative_choices()[-1]  # Return the optimal node, get the action,
                idx_tuple = operational_locations_and_nodes[current_choice[0]][2][current_choice[1]]

                self._attack(attacker=self, tree=tree, idx_tuple=idx_tuple,mode=current_choice[0]+1, verify_corpus=False, just_replace=True, node_idx=current_choice[2])

                output = tree.output()
                score = clsf.get_score(output)
                # print("idx:{} outer:{}/{} inner:{}/{} {} {}".format(idx, attempt, max_attempts, stp+1, max_steps, score, (output+" ").encode()))
                print("idx:{} outer:{}/{} inner:{}/{} {} {}".format(idx, attempt, max_attempts, stp+1, max_steps, score, (output+" ").encode()), file=fdetail, flush=True)
                if score < min_score:
                    min_score = score
                    min_score_payload = output
                if score <= clsf.get_thresh():
                    print(idx, '\t', (origin_output+" ").encode(), file=fsuccess, flush=True)
                    print(idx, '\t', (output+" ").encode(), file=fsuccess, flush=True)
                    return {'success': True, 'except': None, 'benign': False, 'min_score': min_score, 'min_score_payload': min_score_payload, 'success_step': stp+1, 'max_step': max_steps}
        except Exception as e:
            print('EXCEPT', e)
            print('EXCEPT', e, file=fdetail, flush=True)
            traceback.print_exc()
            return {'success': False, 'except': 'something except'}
        return {'success': False, 'except': None, 'benign': False, 'min_score': min_score, 'min_score_payload': min_score_payload, 'success_step': None, 'max_step': max_steps}
