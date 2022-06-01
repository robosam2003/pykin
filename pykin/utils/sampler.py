import numpy as np
from pykin.search.node_data import NodeData

def find_best_idx_from_random(tree, children, value):
    # eps = self._config["eps"]
    # if eps > np.random.uniform():
    best_node_idx = np.random.choice(len([tree.nodes[child][value] for child in children]))
    return best_node_idx

def find_idx_from_greedy(tree, children):
    best_node_idx = np.argmax([tree.nodes[child][NodeData.Q] for child in children])
    return best_node_idx

def find_idx_from_ucb1(tree, children):
    ucbs = []
    for child in children:
        action_values = tree.nodes[child][NodeData.Q_HISTORY]
        u = np.mean(action_values)
        n = [tree.nodes[child][NodeData.VISITS]]
        total_n = tree.nodes[0][NodeData.VISITS]

        if n == 0:
            ucb = float('inf')
        else:
            exploitation = u
            exploration = np.sqrt(1.5 * np.log(total_n) / n)
            ucb = exploitation + exploration
        ucbs.append(ucb)

    best_node_idx = np.argmax(ucb)
    return best_node_idx

def find_idx_from_uct(tree, children, c):
    ucts = []
    for child in children:
        action_values = tree.nodes[child][NodeData.Q_HISTORY]
        u = np.mean(action_values)
        n = np.mean(tree.nodes[child][NodeData.VISITS])
        total_n = tree.nodes[0][NodeData.VISITS]

        if n == 0:
            uct = float('inf')
        else:
            exploitation = u
            exploration = np.sqrt(np.log(total_n) / n)
            uct = exploitation + c * exploration
        ucts.append(uct)

    best_node_idx = np.argmax(ucts)
    return best_node_idx

# TODO
def find_idx_from_bai_ucb(self, children):
    pass

# TODO
def find_idx_from_bai_perturb(self, children):
    pass