import math

class CompilationInput:
    def __init__(self, model, dominance_rule, root, best=0, cache=dict(), dominance=dict(), relaxed=False, width=math.inf, use_rub=False, use_locb=False, use_cache=False, use_dominance=False):
        self.model = model
        self.dominance_rule = dominance_rule
        self.root = root
        self.best = best
        self.cache = cache
        self.dominance = dominance
        self.relaxed = relaxed
        self.width = width

        self.use_rub = use_rub
        self.use_locb = use_locb
        self.use_cache = use_cache
        self.use_dominance = use_dominance

class Arc:
    def __init__(self, parent, reward):
        self.parent = parent
        self.reward = reward
        
class Node:
    def __init__(self, state, depth=0, value_top=0, arc=None, relaxed=False):
        self.state = state
        self.depth = depth
        self.value_top = value_top
        self.value_bot = -math.inf
        self.theta = math.inf
        self.rub = math.inf
        self.ub = math.inf
        self.arcs = []
        if arc is not None:
            self.arcs.append(arc)
        self.relaxed = relaxed
    
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
                next.insert(Node(state, next.depth, node.value_top + reward, Arc(node, reward), node.relaxed))
        return next

    def insert(self, node):
        current = self.nodes.get(node.state)
        if current is None:
            current = node
            self.nodes[current.state] = current
        else:
            current.arcs.append(node.arcs[0])
            current.value_top = max(current.value_top, node.value_top)
            current.relaxed |= node.relaxed

    def shrink(self):
        order = sorted(self.nodes.values(), key=lambda n: n.value_top, reverse=True)
        if self.input.relaxed:
            self.relax(order)
        else:
            self.restrict(order)
    
    def restrict(self, order):
        for node in order[self.input.width:]:
            self.deleted_by_shrink.append(node)
            del self.nodes[node.state]
    
    def relax(self, order):
        relax_start = self.input.width - 1
        self.relax_helper(order[relax_start:], Node(order[relax_start].state.clone(), order[relax_start].depth, relaxed=True))
    
    def finalize(self):
        nodes = list(self.nodes.values())
        if len(nodes) > 0:
            self.relax_helper(nodes, Node(nodes[0].state.clone(), nodes[0].depth, relaxed=False))
    
    def relax_helper(self, to_merge, merged):
        for node in to_merge:
            self.input.model.merge(merged.state, node.state)
            merged.value_top = max(merged.value_top, node.value_top)
            merged.arcs.extend(node.arcs)
            merged.relaxed |= node.relaxed
            self.deleted_by_shrink.append(node)
            del self.nodes[node.state]
        self.insert(merged)
    
    def filter_with_dominance(self):
        if not self.input.use_dominance:
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
                        if node.value_top > others[j].value_top:
                            del others[j]
                        elif node.value_top < others[j].value_top:
                            node.theta = others[j].value_top
                            self.deleted_by_dominance.append(node)
                            del self.nodes[node.state]
                            dominated = True
                            break
                        else:
                            j += 1
                    else:
                        j += 1
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
                            node.theta = others[j].value_top + 1
                            self.deleted_by_dominance.append(node)
                            del self.nodes[node.state]
                            dominated = True
                            break
                        else:
                            j += 1
                    else:
                        node.theta = math.inf
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
        if not self.input.use_cache:
            return False
        used = False
        for node in list(self.nodes.values()):
            theta = self.input.cache.get(node.state)
            if theta is not None and node.value_top <= theta:
                node.theta = theta
                self.deleted_by_cache.append(node)
                del self.nodes[node.state]
                used = True
        return used
    
    def filter_with_rub(self):
        if not self.input.use_rub:
            return False
        used = False
        for node in list(self.nodes.values()):
            node.rub = self.input.model.rough_upper_bound(node.state)
            if node.value_top + node.rub <= self.input.best:
                node.theta = self.input.best - node.rub
                self.deleted_by_rub.append(node)
                del self.nodes[node.state]
                used = True
        return used
    
    def filter_with_local_bounds(self):
        if not self.input.use_locb:
            return False
        used = False
        for node in list(self.nodes.values()):
            if node.value_top + node.value_bot <= self.input.best:
                node.theta = self.input.best - node.value_bot
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
                for arc in node.arcs:
                    arc.parent.theta = min(arc.parent.theta, node.theta + arc.reward)
        for node in self.nodes.values():
            if self.depth == lel:
                node.theta = min(node.theta, node.value_top)
            if self.depth <= lel:
                self.input.cache[node.state] = node.theta
            for arc in node.arcs:
                arc.parent.theta = min(arc.parent.theta, node.theta + arc.reward)
    
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

        self.used_dominance = False
        self.used_cache = False
        self.used_rub = False
        self.used_locb = False
        
    def compile(self):
        depth = self.layers[-1].depth
        while depth < self.input.model.nb_variables():
            self.layers.append(self.layers[-1].next())

            if depth > self.input.root.depth and depth + 1 < self.input.model.nb_variables():
                self.used_dominance |= self.layers[-1].filter_with_dominance()
                self.used_cache |= self.layers[-1].filter_with_cache()
                self.used_rub |= self.layers[-1].filter_with_rub()

            if depth > self.input.root.depth and depth + 1 < self.input.model.nb_variables() and self.layers[-1].width() > self.input.width:
                self.layers[-1].shrink()
            elif self.lel == depth:
                self.lel = depth + 1

            depth += 1
        self.layers[-1].finalize()

        if self.input.relaxed or self.lel == self.input.model.nb_variables():
            self.local_bounds()
            self.thresholds()
    
    def local_bounds(self):
        for node in self.layers[-1].nodes.values():
            node.value_bot = 0
        for layer in reversed(self.layers):
            layer.local_bounds()
        self.used_locb |= self.cutset().filter_with_local_bounds()

        best_value = -math.inf
        if self.best_value() is not None:
            best_value = self.best_value()
        for node in self.cutset().nodes.values():
            node.ub = best_value
            if self.input.use_rub:
                node.ub = min(node.ub, node.value_top + node.rub)
            if self.input.use_locb:
                node.ub = min(node.ub, node.value_top + node.value_bot)
    
    def thresholds(self):
        for layer in reversed(self.layers):
            layer.thresholds(self.lel)

    def best_value(self):
        if self.layers[-1].width() > 0:
            return next(iter(self.layers[-1].nodes.values())).value_top
        return None

    def cutset(self):
        return self.layers[self.lel - self.input.root.depth]
    
    def __str__(self):
        ret = "diagram<lel=" + str(self.lel) + ",layers=<\n"
        for layer in self.layers:
            if layer.depth < self.input.root.depth:
                continue
            ret += str(layer) + "\n"
        ret += ">>"
        return ret