import sys
import re
import math
import random
import copy
import Levenshtein


class Auxiliary():
    """
    Class used to store things
    """

    def __init__(self, tree, operational_locations, attacker, clsf, max_steps, computation_budget):
        self.tree = tree
        self._tree = copy.copy(self.tree)
        self.operational_locations = operational_locations
        self.attacker = attacker
        self.clsf = clsf
        self.max_steps = max_steps
        self.computation_budget = computation_budget

    def reset_tree(self):
        self._tree = copy.copy(self.tree)


class MCTS_Node(object):
    """
    MCTS_Node, contains information such as parent node and child node, as well as the number of traversals and quality values used to calculate UCB, and MCTS_State.
    """

    def __init__(self):
        self.parent = None
        self.children = []

        self.visit_times = 0
        self.quality_value = 0.0

        self.state = None

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def get_parent(self):
        return self.parent

    def set_parent(self, parent):
        self.parent = parent

    def get_children(self):
        return self.children

    def get_visit_times(self):
        return self.visit_times

    def set_visit_times(self, times):
        self.visit_times = times

    def visit_times_add_one(self):
        self.visit_times += 1

    def get_quality_value(self):
        return self.quality_value

    def set_quality_value(self, value):
        self.quality_value = value

    def quality_value_add_n(self, n):
        self.quality_value += n

    def is_all_expand(self):
        return len(self.children) == self.state.get_len_of_available_choices()

    def add_child(self, sub_node):
        sub_node.set_parent(self)
        self.children.append(sub_node)

    def get_payload_distance_change(self):
        return self.state.get_payload_distance_change()

    def __repr__(self):
        return "{}".format(self.state)
        # return "Q/N: {}/{}, {}".format(self.quality_value, self.visit_times, self.state)


def tree_policy(node, mode):
    """
In the Selection and Expansion stages of Monte Carlo tree search, the node that needs to be searched (such as the root node) is passed in, and the best node that needs to be expended is returned according to the exploration/exploitation algorithm. Note that if the node is a leaf node, it is returned directly.
     The basic strategy is to find the currently unselected child node first, if there are more than one, select randomly. If you have chosen all of them, find the largest UCB value that has been weighed against exploration/exploitation. If the UCB values are equal, choose randomly.
    """

    # Check if the current node is the leaf node
    while node.get_state().is_terminal() == False:

        if node.is_all_expand():
            node, _ = best_child(node, mode, is_exploration=True)
        else:
            # Return the new sub node
            sub_node = expand(node)
            return sub_node

    # Return the leaf node
    return node


def default_policy(node):
    """
    In the simulation stage of Monte Carlo tree search, enter a node that needs to be expanded, create a new node after random operation, 
    and return the reward of the newly added node. Note that the input node should not be a child node, and there are unexecuted Actions that can be expended.
    The basic strategy is to randomly select Action.
    """
    bypassed_payload = ''
    bypassed = False
    # Get the state of the game
    current_state = node.get_state()
    # Run until the game over
    while current_state.is_terminal() == False:
        # Pick one random action to play and get next state
        current_state = current_state.get_next_state()
        if current_state.get_bypassed():
            # print('default policy 提前结束')
            bypassed_payload = current_state.current_payload
            bypassed = True

    final_state_reward = current_state.compute_reward()
    return final_state_reward, bypassed, bypassed_payload


def expand(node):
    """
    Enter a node, expand a new node on the node, use the random method to execute the Action, and return the newly added node.
    """
    new_state = node.get_state().get_next_state()

    sub_node = MCTS_Node()
    sub_node.set_state(new_state)
    node.add_child(sub_node)

    return sub_node


def best_child(node, mode, is_exploration):
    """
    Using the UCB algorithm, select the child node with the highest score after weighing the exploration and exploitation. Note that if it is the exploitation in the prediction stage, directly select the current Q-score.
    """

    # TODO: Use the min float value
    best_score = -sys.maxsize
    best_sub_node = None

    # Travel all sub nodes to find the best one
    for sub_node in node.get_children():
        if sub_node.get_state().get_bypassed():
            # print('best_child end early')
            return sub_node, True
        # Ignore exploration for inference
        if is_exploration:
            C1 = 1 / math.sqrt(2.0)
        else:
            C1 = 0.0
        """
        ORI UCB = quality / times + C1 * sqrt(2 * ln(total_times) / times)
        NEW UCB = quality / times + C1 * sqrt(2 * ln(total_times) / times) + C2 * sqrt((current_length - origin_length) / origin_length)
        """
        _left = sub_node.get_quality_value() / sub_node.get_visit_times()
        _middle = 2.0 * math.log(node.get_visit_times()) / \
            sub_node.get_visit_times()
        left = _left
        middle = C1 * math.sqrt(_middle)
        if mode == 'mctscfg':
            score = left + middle
        elif mode == 'mctsfix':
            if is_exploration:
                distance_ratio = sub_node.get_payload_distance_change()
                # distance_ratio = 1.0
            else:
                distance_ratio = 1.0
            score = (left + middle) * distance_ratio
            # print('distance', distance_ratio,'ucb','l:',left ,'m:', middle,'s:',score)
        if score > best_score:
            best_sub_node = sub_node
            best_score = score

    return best_sub_node, False


def backup(node, reward):
    """
    Backpropagation
    """

    # Update util the root node
    while node != None:
        # Update the visit times
        node.visit_times_add_one()

        # Update the quality value
        node.quality_value_add_n(reward)

        # Change the node to the parent node
        node = node.parent


def MCTS_ENTRY(node, auxiliary, mode):
    """
    Monte Carlo tree search algorithm, pass in a root node, expand new nodes and update data according to the tree structure that has been explored before within a limited budget, and then return as long as the child node with the highest exploitation.
    Monte Carlo tree search includes four steps, Selection, Expansion, Simulation, Backpropagation.
    The first two steps use tree policy to find nodes worth exploring.
    The third step is to use the default policy, which is to randomly select a child node on the selected node and calculate the reward.
    The last step to use backup is to update the reward to all the nodes of the selected nodes that have passed.
    When making predictions, only need to select the node with the largest exploitation based on the Q value, and find the next optimal node.
    """
    bypassed = False
    bypassed_payload = ''
    # Run as much as possible under the computation budget
    for _ in range(auxiliary.computation_budget):

        # 1. Find the best node to expand
        expand_node = tree_policy(node, mode)
        # 2. Random run to add node and get reward
        reward, bypassed, bypassed_payload = default_policy(expand_node)
        if bypassed:
            return node, bypassed, bypassed_payload, 'default_policy'
        # 3. Update all passing nodes with reward
        backup(expand_node, reward)

    # N. Get the best next node
    best_next_node, bypassed = best_child(node, mode, is_exploration=False,)
    if bypassed:
        bypassed_payload = best_next_node.get_state().get_current_payload()
    return best_next_node, bypassed, bypassed_payload, 'best_child'


class MCTS(object):
    """
    The game state of the Monte Carlo tree search, including the current game score, the current game round number, and the record from the beginning to the current.
    """

    def __init__(self, auxiliary, init_score=1.0, origin_payload='', blackbox=False):
        self.init_score = init_score
        self.current_value = 1 - init_score
        self.origin_payload = origin_payload
        self.current_payload = ''
        self.current_round_index = 0
        self.cumulative_choices = []
        self.integral_cumulative_choices = []
        self.auxiliary = auxiliary
        self.all_choices = self.get_all_choices()
        self.clsf_thresh = self.auxiliary.clsf.get_thresh()
        self.blackbox = blackbox
        self.bypassed = False

    def get_current_value(self):
        return self.current_value

    def set_current_value(self, value):
        self.current_value = value

    def get_current_round_index(self):
        return self.current_round_index

    def set_current_round_index(self, turn):
        self.current_round_index = turn

    def get_cumulative_choices(self):
        return self.cumulative_choices

    def set_cumulative_choices(self, choices):
        self.cumulative_choices = choices

    def get_integral_cumulative_choices(self):
        return self.integral_cumulative_choices

    def set_integral_cumulative_choices(self, choices):
        self.integral_cumulative_choices = choices

    def is_terminal(self):
        # The round index starts from 1 to max round number
        return self.current_round_index == self.auxiliary.max_steps

    def is_going_to_terminal(self):
        return self.current_round_index == self.auxiliary.max_steps - 1

    def compute_reward(self):
        return self.current_value * 10
        # if self.blackbox:
        #     return self.current_value * 10
        # else:
        #     return self.current_value / (self.init_score - self.clsf_thresh) * 10

    def get_all_choices(self):
        choices = []
        for (i, _, search_res) in self.auxiliary.operational_locations:
            for j, idx_tuple in enumerate(search_res):
                for k, _ in enumerate(idx_tuple[5]):
                    choices.append((i, j, k))
        return choices

    def get_available_choices(self):
        # Get the unused choice
        return [choice for choice in self.all_choices if (choice[0], choice[1]) not in self.cumulative_choices]

    def get_len_of_available_choices(self):
        # Get the number of unused choice
        return len(self.get_available_choices())

    def perform_one_attack(self, random_choice):
        self.auxiliary.attacker._attack(attacker=self.auxiliary.attacker, tree=self.auxiliary._tree,  idx_tuple=self.auxiliary.operational_locations[
                                        random_choice[0]][2][random_choice[1]], mode=random_choice[0]+1, verify_corpus=True, just_replace=True, node_idx=random_choice[2])

        output = self.auxiliary._tree.output()
        score = self.auxiliary.clsf.get_score(output)
        self.auxiliary.reset_tree()
        return score, output

    def get_next_state(self):
        random_choice = random.choice(self.get_available_choices())
        next_state = MCTS(auxiliary=self.auxiliary, origin_payload=self.origin_payload,
                          init_score=self.init_score, blackbox=self.blackbox)
        score, output = self.perform_one_attack(random_choice)
        value = self.init_score - score
        if score < self.auxiliary.clsf.get_thresh():
            next_state.set_bypassed()
        next_state.set_current_value(value)
        next_state.set_current_round_index(self.current_round_index + 1)
        next_state.set_cumulative_choices(
            self.cumulative_choices + [(random_choice[0], random_choice[1])])
        next_state.set_integral_cumulative_choices(
            self.integral_cumulative_choices + [(random_choice[0], random_choice[1], random_choice[2])])
        next_state.set_current_payload(output)
        return next_state

    def set_current_payload(self, p):
        self.current_payload = p

    def get_current_payload(self):
        return self.current_payload

    def get_payload_distance_change(self):
        return Levenshtein.ratio(self.origin_payload, self.current_payload)

    def set_bypassed(self):
        self.bypassed = True

    def get_bypassed(self):
        return self.bypassed

    def __repr__(self):
        return "round: {}, value: {}, choices: {}".format(self.current_round_index, self.current_value, self.cumulative_choices)
