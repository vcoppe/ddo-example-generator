import math
import random

class Instance:
    def __init__(self, n, c, w, v):
        self.n = n
        self.c = c

        r = [(v[i] / w[i], v[i], w[i]) for i in range(n)]
        r.sort(reverse=True)

        self.v = [r[i][1] for i in range(n)]
        self.w = [r[i][2] for i in range(n)]
    
    def __str__(self):
        return "instance<n=" + str(self.n) + ",c=" + str(self.c) + ",v=" + str(self.v) + ",w=" + str(self.w) + ">"

class Arc:
    def __init__(self, parent, reward):
        self.parent = parent
        self.reward = reward

class State:
    def __init__(self, capa, depth):
        self.capa = capa
        self.depth = depth

    def __hash__(self):
        return hash((self.capa, self.depth))

    def __eq__(self, other):
        return (self.capa, self.depth) == (other.capa, other.depth)
    
    def successor(self, instance, decision):
        capa = self.capa - decision * instance.w[self.depth]
        if capa < 0:
            return None
        return State(capa, self.depth + 1)
    
    def reward(self, instance, decision):
        return decision * instance.v[self.depth]
    
    def rough_upper_bound(self, instance):
        capa = self.capa
        rub = 0
        for depth in range(self.depth, instance.n):
            if instance.w[depth] <= capa:
                capa -= instance.w[depth]
                rub += instance.v[depth]
            else:
                rub += int(math.floor(capa * instance.v[depth] / instance.w[depth]))
                break
        return rub
    
    def __str__(self):
        return "state<capa=" + str(self.capa) + ">"
        
class Node:
    def __init__(self, state, value_top=0, arc=None, relaxed=False):
        self.state = state
        self.value_top = value_top
        self.value_bot = -math.inf
        self.theta = math.inf
        self.rub = -math.inf
        self.ub = 0
        self.arcs = []
        if arc is not None:
            self.arcs.append(arc)
        self.relaxed = relaxed

    def successor(self, instance, decision):
        state = self.state.successor(instance, decision)
        if state is None:
            return None
        reward = self.state.reward(instance, decision)
        return Node(state, self.value_top + reward, Arc(self, reward), self.relaxed)
    
    def rough_upper_bound(self, instance):
        return self.value_top + self.state.rough_upper_bound(instance)
    
    def __str__(self):
        return "node<state=" + str(self.state) + ",value_top=" + str(self.value_top) \
            + ((",value_bot=" + str(self.value_bot)) if self.value_bot != -math.inf else "") \
            + ((",rub=" + str(self.rub - self.value_top)) if self.rub != -math.inf else "") \
            + ((",theta=" + str(self.theta)) if self.theta != math.inf else "") \
            + (",relaxed" if self.relaxed else "") + ">"

class Layer:
    def __init__(self, node=None):
        self.nodes = dict()
        self.deleted_by_dominance = []
        self.deleted_by_cache = []
        self.deleted_by_rub = []
        self.deleted_by_shrink = []
        self.deleted_by_local_bounds = []
        if node is not None:
            self.nodes[node.state] = node
    
    def next(self, instance):
        next = Layer()
        for node in self.nodes.values():
            for decision in [0, 1]:
                successor = node.successor(instance, decision)
                if successor is not None:
                    next.insert(successor)
        return next

    def insert(self, node):
        current = self.nodes.get(node.state)
        if current is None:
            current = node
        else:
            current.arcs.append(node.arcs[0])
            current.value_top = max(current.value_top, node.value_top)
            current.relaxed |= node.relaxed
        self.nodes[current.state] = current

    def shrink(self, width, relaxed, terminal=False):
        order = sorted(self.nodes.values(), key=lambda n: n.value_top, reverse=True)
        if relaxed:
            self.relax(width, order, terminal)
        else:
            self.restrict(width, order)
    
    def restrict(self, width, order):
        for node in order[width:]:
            self.deleted_by_shrink.append(node)
            del self.nodes[node.state]
    
    def relax(self, width, order, terminal):
        if len(order) <= 1:
            return
        merged = Node(State(0, 0), relaxed=not terminal)
        for node in order[(width - 1):]:
            merged.state.capa = max(merged.state.capa, node.state.capa)
            merged.state.depth = max(merged.state.depth, node.state.depth)
            merged.value_top = max(merged.value_top, node.value_top)
            merged.arcs.extend(node.arcs)
            merged.relaxed |= node.relaxed
            self.deleted_by_shrink.append(node)
            del self.nodes[node.state]
        self.insert(merged)
    
    def filter_with_dominance(self, dominance):
        if not use_dominance:
            return False
        used = False
        order = sorted(self.nodes.values(), key=lambda n: n.state.capa, reverse=True)
        for i in range(len(order)):
            node = order[i]
            if node.relaxed:
                continue

            dominated = False
            dominated_by_capa = False
            others = dominance[node.state.depth]

            j = 0
            while j < len(others):
                if node.state.capa >= others[j].state.capa and node.value_top >= others[j].value_top:
                    del others[j]
                elif node.state.capa <= others[j].state.capa and node.value_top <= others[j].value_top:
                    node.theta = others[j].value_top if node.state.capa == others[j].state.capa else others[j].value_top + 1
                    self.deleted_by_dominance.append(node)
                    del self.nodes[node.state]
                    dominated = True
                    dominated_by_capa = node.state.capa != others[j].state.capa
                    break
                else:
                    j += 1
            
            if dominated and dominated_by_capa:
                used = True
            else:
                others.append(node)
        return used
    
    def filter_with_cache(self, cache):
        if not use_cache:
            return False
        used = False
        for node in list(self.nodes.values()):
            theta = cache.get(node.state)
            if theta is not None and node.value_bot <= theta:
                node.theta = theta
                self.deleted_by_cache.append(node)
                del self.nodes[node.state]
                used = True
        return used
    
    def filter_with_rub(self, instance, best):
        if not use_rub:
            return False
        used = False
        for node in list(self.nodes.values()):
            node.rub = node.rough_upper_bound(instance)
            if node.rub <= best:
                node.theta = node.value_top + best - node.rub
                self.deleted_by_rub.append(node)
                del self.nodes[node.state]
                used = True
        return used
    
    def filter_with_local_bounds(self, best):
        if not use_locb:
            return False
        used = False
        for node in list(self.nodes.values()):
            if node.value_top + node.value_bot <= best:
                node.theta = best - node.value_bot
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
    
    def thresholds(self, cache, cmp_lel):
        for nodes in [self.deleted_by_dominance, self.deleted_by_cache, self.deleted_by_rub, self.deleted_by_local_bounds]:
            for node in nodes:
                for arc in node.arcs:
                    arc.parent.theta = min(arc.parent.theta, node.theta + arc.reward)
        for node in self.nodes.values():
            if cmp_lel == 0:
                node.theta = node.value_top
            if cmp_lel <= 0:
                cache[node.state] = node.theta
            for arc in node.arcs:
                arc.parent.theta = min(arc.parent.theta, node.theta + arc.reward)
    
    def __str__(self):
        ret = "layer<"
        first = True
        for node in self.nodes.values():
            if first:
                first = False
            else:
                ret += ","
            ret += str(node)
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
    def __init__(self, instance, root, width, relaxed):
        self.instance = instance
        self.root = root
        self.width = width
        self.relaxed = relaxed
        self.layers = [Layer() for _ in range(self.root.state.depth)]
        self.layers.append(Layer(root))
        self.lel = self.root.state.depth

        self.used_dominance = False
        self.used_cache = False
        self.used_rub = False
        self.used_locb = False
        
    def compile(self, dominance, cache, best):
        depth = self.root.state.depth
        while depth < self.instance.n:
            self.layers.append(self.layers[-1].next(self.instance))

            if depth + 1 < self.instance.n:
                self.used_dominance |= self.layers[-1].filter_with_dominance(dominance)
                self.used_cache |= self.layers[-1].filter_with_cache(cache)
                self.used_rub |= self.layers[-1].filter_with_rub(self.instance, best)

            if depth > self.root.state.depth and depth + 1 < self.instance.n and self.layers[-1].width() > self.width:
                self.layers[-1].shrink(self.width, self.relaxed)
            elif self.lel == depth:
                self.lel = depth + 1

            depth += 1
        self.layers[-1].shrink(1, True, terminal=True)

        if self.relaxed or self.lel == self.instance.n:
            self.local_bounds(best)
            self.thresholds(cache)
    
    def local_bounds(self, best):
        for node in self.layers[-1].nodes.values():
            node.value_bot = 0
        for layer in reversed(self.layers):
            layer.local_bounds()
        self.used_locb |= self.layers[self.lel].filter_with_local_bounds(best)

        best_value = -math.inf
        if self.best_value() is not None:
            best_value = self.best_value()
        for node in self.layers[self.lel].nodes.values():
            node.ub = best_value
            if use_rub:
                node.ub = min(node.ub, node.rub)
            if use_locb:
                node.ub = min(node.ub, node.value_top + node.value_bot)
    
    def thresholds(self, cache):
        depth = self.instance.n
        for layer in reversed(self.layers):
            layer.thresholds(cache, depth - self.lel)
            depth -= 1

    def best_value(self):
        if self.layers[-1].width() > 0:
            return next(iter(self.layers[-1].nodes.values())).value_top
        return None

    def cutset(self):
        return self.layers[self.lel]
    
    def __str__(self):
        ret = "diagram<lel=" + str(self.lel) + ",layers=<\n"
        for depth, layer in enumerate(self.layers):
            if depth < self.root.state.depth:
                continue
            ret += str(depth) + ": " + str(layer) + "\n"
        ret += ">>"
        return ret
    
def random_instance(n, rand):
    c = n * 5 // 2
    v = []
    w = []

    for _ in range(n):
        v.append(rand.randint(1, 6))
        w.append(rand.randint(1, 6))
    
    return Instance(n, c, w, v)

def main():
    global use_rub, use_locb, use_cache, use_dominance

    configs = [(True, False, False, False), (True, True, False, False), (True, True, True, False), (True, True, True, True), (False, False, False, False)]

    rand = random.Random(0)

    while True:
        found = True
        instance = random_instance(5, rand)
        all_dds = []

        for (use_rub, use_locb, use_cache, use_dominance) in configs:
            cache = dict()
            dominance = [[] for _ in range(instance.n + 1)]
            best = 0
            dds = []

            dds.append(Diagram(instance, Node(State(instance.c, 0)), 3, False))
            dds[-1].compile(dominance, cache, best)

            if dds[-1].best_value() is not None:
                best = dds[-1].best_value()

            dds.append(Diagram(instance, Node(State(instance.c, 0)), 3, True))
            dds[-1].compile(dominance, cache, best)

            lel = dds[-1].cutset()

            if len(lel.nodes) == 0:
                found = False
                break

            for node in sorted(lel.nodes.values(), key=lambda n: n.ub, reverse=True):
                if node.ub <= best:
                    continue

                dds.append(Diagram(instance, node, 100, True))
                dds[-1].compile(dominance, cache, best)

                if dds[-1].best_value() is not None and dds[-1].best_value() > best:
                    best = dds[-1].best_value()

            if use_dominance:
                #if not any(dd.used_dominance for dd in dds):
                if not (dds[0].used_dominance or dds[1].used_dominance):
                    found = False
                    break
            elif use_cache:
                if not any(dd.used_cache for dd in dds):
                    found = False
                    break
            elif use_locb:
                if not dds[1].used_locb:
                    found = False
                    break
            elif use_rub:
                if not dds[1].used_rub:
                    found = False
                    break

            all_dds.append(dds)
            
        if found:
            print(instance)
            for dds in all_dds:
                print("=========== dds for next config ===========")
                for dd in dds:
                    print(dd)

if __name__ == "__main__":
    main() 