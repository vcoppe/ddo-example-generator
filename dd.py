import math
from enum import Enum

class Cutset(Enum):
    LAYER = 0
    FRONTIER = 1

class CompilationInput:
    def __init__(self, model, dominance_rule, root, best, cache, dominance, relaxed, settings):
        self.model = model
        self.dominance_rule = dominance_rule
        self.root = root
        self.best = best
        self.cache = cache
        self.dominance = dominance
        self.relaxed = relaxed
        self.settings = settings

class Arc:
    def __init__(self, parent, reward, decision):
        self.parent = parent
        self.reward = reward
        self.decision = decision
        self.opt = False
        
class Node:
    def __init__(self, state, depth=0, value_top=0, score=0, arc=None, relaxed=False, merged=False, ub=math.inf):
        self.state = state
        self.depth = depth
        self.value_top = value_top
        self.value_bot = -math.inf
        self.score = score
        self.theta = math.inf
        self.rub = math.inf
        self.ub = ub
        self.arcs = []
        if arc is not None:
            self.arcs.append(arc)
        self.relaxed = relaxed
        self.merged = merged
        self.cutset = False
        self.above_cutset = False
        self.deleted_by_rub = False
        self.deleted_by_local_bounds = False
        self.deleted_by_cache = False
        self.deleted_by_dominance = False
        self.deleted_by_hint = None

    def __lt__(self, other):
        return self.ub > other.ub
    
    def __str__(self):
        return "node<state=" + str(self.state) + ",value_top=" + str(self.value_top) \
            + ((",value_bot=" + str(self.value_bot)) if self.value_bot != -math.inf else "") \
            + ((",rub=" + str(self.rub)) if self.rub != math.inf else "") \
            + ((",theta=" + str(self.theta)) if self.theta != math.inf else "") \
            + (",relaxed" if self.relaxed else "") + ">"

class Layer:
    def __init__(self, input, depth, root=None):
        self.input = input
        self.nodes = dict()
        if root is not None:
            self.nodes[root.state] = root
        self.depth = depth

        self.deleted_by_dominance = []
        self.deleted_by_cache = []
        self.deleted_by_rub = []
        self.deleted_by_shrink = []
        self.deleted_by_local_bounds = []
    
    def next(self):
        next = Layer(self.input, self.depth + 1)
        for node in self.nodes.values():
            for decision in self.input.model.domain(node.state, self.depth):
                state = self.input.model.successor(node.state, decision)
                if state is None:
                    continue
                reward = self.input.model.reward(node.state, decision)
                score = self.input.model.score(node.state, decision)
                next.insert(Node(state, next.depth, node.value_top + reward, node.score + score, Arc(node, reward, decision), node.relaxed))
        return next

    def insert(self, node):
        current = self.nodes.get(node.state)
        if current is None:
            current = node
            self.nodes[current.state] = current
        else:
            current.arcs.append(node.arcs[0])
            current.value_top = max(current.value_top, node.value_top)
            current.score = max(current.score, node.score)
            current.relaxed |= node.relaxed

    def shrink(self):
        if self.input.relaxed:
            order = sorted(self.nodes.values(), key=lambda n: n.value_top, reverse=True)
            self.relax(order)
        else:
            if self.input.settings.use_aggh:
                order = sorted(self.nodes.values(), key=lambda n: (n.score, n.value_top), reverse=True)
            else:
                order = sorted(self.nodes.values(), key=lambda n: n.value_top, reverse=True)
            self.restrict(order)
    
    def restrict(self, order):
        for node in order[self.input.settings.width:]:
            self.deleted_by_shrink.append(node)
            del self.nodes[node.state]
    
    def relax(self, order):
        relax_start = self.input.settings.width - 1
        self.relax_helper(order[relax_start:], Node(order[relax_start].state.clone(), order[relax_start].depth, relaxed=True, merged=True))
    
    def finalize(self):
        nodes = list(self.nodes.values())
        if self.width() > 0:
            self.relax_helper(nodes, Node(nodes[0].state.clone(), nodes[0].depth, relaxed=False))
        
            current = next(iter(self.nodes.values()))
            while len(current.arcs) > 0:
                for arc in current.arcs:
                    if arc.parent.value_top + arc.reward == current.value_top:
                        arc.opt = True
                        current = arc.parent
                        break
    
    def relax_helper(self, to_merge, merged):
        for node in to_merge:
            self.input.model.merge(merged.state, node.state)
            merged.value_top = max(merged.value_top, node.value_top)
            merged.score = max(merged.score, node.score)
            merged.arcs.extend(node.arcs)
            merged.relaxed |= node.relaxed
            self.deleted_by_shrink.append(node)
            del self.nodes[node.state]
        self.insert(merged)
    
    def filter_with_dominance(self):
        if not self.input.settings.use_dominance:
            return False
        if self.input.dominance_rule is None:
            return False
        used = False
        order = sorted(self.nodes.values(), key=lambda n: (self.input.dominance_rule.value(n.state), n.value_top), reverse=True)
        for i in range(len(order)):
            node = order[i]
            if node.relaxed:
                continue

            dominated = False
            others = self.input.dominance.get(self.input.dominance_rule.key(node.state))
            if others is None:
                others = []
                self.input.dominance[self.input.dominance_rule.key(node.state)] = others

            j = 0
            while j < len(others):
                cmp = self.input.dominance_rule.check(node.state, others[j].state)
                if cmp == 0:
                    if self.input.dominance_rule.use_value():
                        if node.value_top >= others[j].value_top:
                            del others[j]
                        else:
                            node.theta = others[j].value_top - 1
                            node.deleted_by_dominance = True
                            node.deleted_by_hint = others[j]
                            self.deleted_by_dominance.append(node)
                            del self.nodes[node.state]
                            dominated = True
                            break
                    else:
                        del others[j]
                elif cmp > 0:
                    if self.input.dominance_rule.use_value():
                        if node.value_top >= others[j].value_top:
                            del others[j]
                        else:
                            j += 1
                    else:
                        del others[j]
                elif cmp < 0:
                    if self.input.dominance_rule.use_value():
                        if node.value_top <= others[j].value_top:
                            node.theta = others[j].value_top
                            node.deleted_by_dominance = True
                            node.deleted_by_hint = others[j]
                            self.deleted_by_dominance.append(node)
                            del self.nodes[node.state]
                            dominated = True
                            break
                        else:
                            j += 1
                    else:
                        node.theta = math.inf
                        node.deleted_by_dominance = True
                        node.deleted_by_hint = others[j]
                        self.deleted_by_dominance.append(node)
                        del self.nodes[node.state]
                        dominated = True
                        break
            
            if dominated:
                used = True
            else:
                others.append(node)
        return used
    
    def filter_with_cache(self):
        if not self.input.settings.use_cache:
            return (False, False, False)
        used = False
        used_larger = False
        used_pruning = False
        for node in list(self.nodes.values()):
            threshold = self.input.cache.get(node.state)
            if threshold is not None and node.value_top <= threshold.theta:
                node.theta = threshold.theta
                node.deleted_by_cache = True
                node.deleted_by_hint = threshold.theta
                self.deleted_by_cache.append(node)
                del self.nodes[node.state]
                used = True
                used_larger |= node.value_top > threshold.value_top
                used_pruning |= threshold.pruning
        return (used, used_larger, used_pruning)
    
    def filter_with_rub(self):
        if not self.input.settings.use_rub:
            return False
        used = False
        for node in list(self.nodes.values()):
            node.rub = self.input.model.rough_upper_bound(node.state)
            if self.input.settings.use_aggb:
                node.rub = min(node.rub, self.input.model.aggregate_bound(node.state))
            if node.value_top + node.rub <= self.input.best:
                node.theta = self.input.best - node.rub
                node.deleted_by_rub = True
                node.deleted_by_hint = self.input.best
                self.deleted_by_rub.append(node)
                del self.nodes[node.state]
                used = True
        return used
    
    def frontier(self, cutset_nodes):
        for node in self.nodes.values():
            if node.cutset:
                cutset_nodes.append(node)
            for arc in node.arcs:
                if node.relaxed and not arc.parent.relaxed:
                    arc.parent.cutset = True
                    arc.parent.above_cutset = True
                arc.parent.above_cutset |= node.above_cutset
    
    def filter_with_local_bounds(self):
        if not self.input.settings.use_locb:
            return False
        used = False
        for node in list(self.nodes.values()):
            if node.cutset and node.value_top + node.value_bot <= self.input.best:
                node.theta = self.input.best - node.value_bot
                node.deleted_by_local_bounds = True
                node.deleted_by_hint = self.input.best
                self.deleted_by_local_bounds.append(node)
                del self.nodes[node.state]
                used = True
        return used

    def width(self):
        return len(self.nodes)
    
    def local_bounds(self):
        for node in self.nodes.values():
            for arc in node.arcs:
                arc.parent.value_bot = max(arc.parent.value_bot, node.value_bot + arc.reward)
    
    def thresholds(self, lel):
        for nodes in [self.deleted_by_dominance, self.deleted_by_cache, self.deleted_by_rub, self.deleted_by_local_bounds]:
            for node in nodes:
                if (self.input.settings.cutset == Cutset.FRONTIER or (self.input.settings.cutset == Cutset.LAYER and node.depth <= lel)) and not node.relaxed:
                    self.input.cache[node.state] = Threshold(node.theta, node.value_top, True)
                for arc in node.arcs:
                    arc.parent.theta = min(arc.parent.theta, node.theta - arc.reward)
        for node in self.nodes.values():
            if node.cutset:
                node.theta = min(node.theta, node.value_top)
            if node.above_cutset:
                self.input.cache[node.state] = Threshold(node.theta, node.value_top)
            for arc in node.arcs:
                arc.parent.theta = min(arc.parent.theta, node.theta - arc.reward)
    
    def __str__(self):
        ret = "layer<depth=" + str(self.depth) + ",nodes=<"
        first = True
        for node in self.nodes.values():
            if first:
                first = False
            else:
                ret += ","
            ret += str(node)
        ret += ">"
        for name, nodes in ({
            "deleted_by_dominance": self.deleted_by_dominance,
            "deleted_by_cache": self.deleted_by_cache,
            "deleted_by_rub": self.deleted_by_rub,
            "deleted_by_shrink": self.deleted_by_shrink,
            "deleted_by_local_bounds": self.deleted_by_local_bounds,
        }).items():
            if len(nodes) > 0:
                ret += "," + name + "=<"
                first = True
                for node in nodes:
                    if first:
                        first = False
                    else:
                        ret += ","
                    ret += str(node)
                ret += ">"
        ret += ">"
        return ret
    
class Diagram:
    def __init__(self, input):
        self.input = input
        self.layers = [Layer(input, input.root.depth, input.root)]
        self.lel = input.root.depth
        self.relaxed = input.relaxed
        self.cutset_nodes = []

        self.used_dominance = False
        self.used_cache = False
        self.used_cache_larger = False
        self.used_cache_pruning = False
        self.used_rub = False
        self.used_locb = False

        self.compile()
        
    def compile(self):
        depth = self.layers[-1].depth
        while depth < self.input.model.nb_variables():
            self.layers.append(self.layers[-1].next())

            if depth + 1 < self.input.model.nb_variables():
                (used_cache, used_cache_larger, used_cache_pruning) = self.layers[-1].filter_with_cache()
                self.used_cache |= used_cache
                self.used_cache_larger |= used_cache_larger
                self.used_cache_pruning |= used_cache_pruning
                self.used_dominance |= self.layers[-1].filter_with_dominance()
                self.used_rub |= self.layers[-1].filter_with_rub()

            if depth > self.input.root.depth and depth + 1 < self.input.model.nb_variables() and self.layers[-1].width() > self.input.settings.width:
                self.layers[-1].shrink()
            elif self.lel == depth:
                self.lel = depth + 1

            depth += 1
        self.layers[-1].finalize()

        if self.input.relaxed or self.is_exact():
            self.cutset()
            self.local_bounds()
            self.thresholds()

    def cutset(self):
        if self.input.settings.cutset == Cutset.LAYER or self.is_exact():
            for node in self.layers[self.lel - self.input.root.depth].nodes.values():
                node.cutset = True
                self.cutset_nodes.append(node)
            for layer in self.layers[(self.lel - self.input.root.depth)::-1]:
                for node in layer.nodes.values():
                    node.above_cutset = True
        elif self.input.settings.cutset == Cutset.FRONTIER:
            for layer in reversed(self.layers):
                layer.frontier(self.cutset_nodes)
    
    def local_bounds(self):
        if self.layers[-1].depth == self.input.model.nb_variables():
            for node in self.layers[-1].nodes.values():
                node.value_bot = 0
        for layer in reversed(self.layers):
            layer.local_bounds()
            self.used_locb |= layer.filter_with_local_bounds()

        best_value = -math.inf
        if self.get_best_value() is not None:
            best_value = self.get_best_value()
        for node in self.cutset_nodes:
            node.ub = best_value
            if self.input.settings.use_rub:
                node.ub = min(node.ub, node.value_top + node.rub)
            if self.input.settings.use_locb:
                node.ub = min(node.ub, node.value_top + node.value_bot)
    
    def thresholds(self):
        if not self.input.settings.use_cache:
            return
        for layer in reversed(self.layers):
            layer.thresholds(self.lel)

    def get_terminal(self):
        if self.layers[-1].depth == self.input.model.nb_variables() and self.layers[-1].width() > 0:
            return next(iter(self.layers[-1].nodes.values()))
        return None

    def get_best_value(self):
        terminal = self.get_terminal()
        if terminal is None:
            return None
        return terminal.value_top

    def get_best_solution(self):
        current = self.get_terminal()
        if current is None:
            return None
        solution = []
        while len(current.arcs) > 0:
            for arc in current.arcs:
                if arc.opt:
                    solution.insert(0, arc.decision)
                    current = arc.parent
        return solution

    def get_cutset(self):
        return self.cutset_nodes
    
    def is_exact(self):
        return self.lel == self.input.model.nb_variables()
    
    def __str__(self):
        ret = "diagram<" + ("exact" if self.is_exact() else ("relaxed" if self.relaxed else "restricted")) +  ",lel=" + str(self.lel) + ",layers=<\n"
        for layer in self.layers:
            ret += str(layer) + "\n"
        ret += ">>"
        return ret
    
class Threshold:
    def __init__(self, theta, value_top, pruning=False):
        self.theta = theta
        self.value_top = value_top
        self.pruning = pruning