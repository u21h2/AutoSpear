import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--pattern', '-p', required=True, default='ML', choices=[
                    'ML', 'WAFaas'], help='attack pattern: ML or WAFaas; ML means local ML SQLi detector and WAFaas means real-world WAF-as-a-service; you need to specify request method when WAFaas')
parser.add_argument('--guide', '-g', required=False, default='random', choices=[
                    'random', 'mcts'], help='guide mothod: mcts or random (default); mcts means Monte-Carlo Tree Search')
parser.add_argument('--request_method', '-r', required=False, default='GET(JSON)', choices=[
                    'GET', 'GET(JSON)', 'POST', 'POST(JSON)'], help='request method: GET / GET(JSON) / POST / POST(JSON)')
parser.add_argument('--max_attempts', '-mat', required=False, default=10,
                    type=int, help='maximum number of attempts, default is 10; This parameter is for the entire attack process, no matter what attack method is used, the attack process is repeated *mat* times')
parser.add_argument('--max_steps', '-mst', required=False, default=10, type=int,
                    help='this parameter plays a role in the attack process, a payload can be mutated at most *mst* times.')
parser.add_argument('--tree_mutate_pattern', '-tp', required=False, default='all', choices=[
                    'all', 'query'], help='tree muatte pattern: only modify query_tree or modify both boundary and query trees')
parser.add_argument('--payload_number', '-pn', required=False, default='single', choices=[
                    'single', 'multiple'], help='payload pattern: single payloads or multi paylaods, you need to write your payload(s) to the corresponding files (payload_xxx.txt)')
parser.add_argument('--ML_url', '-MLu', required=False, default='default',
                    help='the local ML SQLi detector url (the ML model needs to be deployed as a *service* in advance)')
parser.add_argument('--ML_thresh', '-MLt', required=False, default=0.5,
                    type=float, help='threshold of the local ML SQLi detector')
parser.add_argument('--ML_box', '-MLb', required=False, default='blackbox_with_score',
                    choices=['blackbox_with_score', 'blackbox_without_score'], help='blackbox with score?')
parser.add_argument('--WAFaas_url', '-WAFu', required=False,
                    default='default', help='the url of your target WAFaas')
parser.add_argument('--cookie', '-c', required=False, default='', help='cookie')
input_args = parser.parse_args()


benign_payloads = []
