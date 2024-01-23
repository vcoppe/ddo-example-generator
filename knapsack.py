from enum import Enum
import math

USE_LP_BOUND = False

class KnapsackInstance:
    def __init__(self, n, c, w, v, q):
        self.n = n
        self.c = c

        r = [(v[i] / w[i], v[i], w[i], q[i]) for i in range(n)]

        if USE_LP_BOUND:
            r.sort(reverse=True)

        self.v = [r[i][1] for i in range(n)]
        self.w = [r[i][2] for i in range(n)]
        self.q = [r[i][3] for i in range(n)]
    
    def __str__(self):
        return "instance<" + str(self.n) + ", " + str(self.c) + ", " + str(self.w) + ", " + str(self.v) + ", " + str(self.q) + ">"
    
    def random(n, rand):
        alpha = 6
        beta = 2

        c = n * alpha // beta
        v = [10, 9, 8, 7, 2]
        w = []
        #q = [1 + i % 2 for i in range(n)]
        #q[-1] = rand.randint(1, 2)
        #rand.shuffle(q)
        q = [1 for _ in range(n)]

        for i in range(n - 1):
            w.append(rand.randint(2, alpha))
        w.append(rand.randint(1, min(w)))

        if w[0] + w[1] + w[2] <= c:
            c = w[0] + w[1] + w[2] - 1
        
        combined = [(v[i], w[i]) for i in range(n)]
        rand.shuffle(combined)
        v = [x[0] for x in combined]
        w = [x[1] for x in combined]

        for i in range(len(v), n):
            w.append(rand.randint(1, alpha))
            v.append(rand.randint(1, 10))
        
        return KnapsackInstance(n, c, w, v, q)
    

class CompilationMode(Enum):
    DD = 0
    DP = 1
    TREE = 2

class KnapsackState:
    ID = 0

    def __init__(self, capa, depth, mode):
        self.capa = capa
        self.depth = depth
        self.id = KnapsackState.ID
        self.mode = mode

        if mode == CompilationMode.TREE:
            KnapsackState.ID += 1

    def clone(self):
        return KnapsackState(self.capa, self.depth, self.mode)
    
    def __lt__(self, other): # used only for tikz output
        if self.mode == CompilationMode.TREE:
            return self.id < self.id
        return self.capa > other.capa

    def __hash__(self):
        return hash((self.capa, self.depth, self.id))

    def __eq__(self, other):
        return (self.capa, self.depth, self.id) == (other.capa, other.depth, self.id)
    
    def __str__(self):
        return "state<capa=" + str(self.capa) + ">"

class KnapsackModel:
    def __init__(self, instance, mode=CompilationMode.DD, aggregation=None):
        self.instance = instance
        self.mode = mode
        self.aggregation = aggregation
    
    def nb_variables(self):
        return self.instance.n

    def root(self):
        return KnapsackState(self.instance.c, 0, self.mode)

    def domain(self, state, variable):
        return range(self.instance.q[variable] + 1)
    
    def successor(self, state, decision):
        capa = state.capa - decision * self.instance.w[state.depth]
        if capa < 0:
            return None
        return KnapsackState(capa, state.depth + 1, self.mode)
    
    def reward(self, state, decision):
        return decision * self.instance.v[state.depth]
    
    def score(self, state, decision):
        if self.aggregation is None:
            return 0
        return self.aggregation.score(state, decision)
    
    def merge(self, a, b):
        a.capa = max(a.capa, b.capa)
        a.depth = max(a.depth, b.depth)
    
    def rough_upper_bound(self, state):
        return 100000
        # if USE_LP_BOUND:
        #     return self.lp_bound(state)
        # else:
        #     return self.simple_bound(state)
        
    def aggregate_bound(self, state):
        if self.aggregation is not None:
            return self.aggregation.bound(state)
        else:
            return math.inf
    
    def lp_bound(self, state): # needs the items to be sorted by decreasing v/w ratio
        capa = state.capa
        rub = 0
        for depth in range(state.depth, self.instance.n):
            if self.instance.w[depth] * self.instance.q[depth] <= capa:
                capa -= self.instance.w[depth] * self.instance.q[depth]
                rub += self.instance.v[depth] * self.instance.q[depth]
            else:
                rub += int(math.floor(capa * self.instance.v[depth] / self.instance.w[depth]))
                break
        return rub

    def simple_bound(self, state):
        rub = 0
        for depth in range(state.depth, self.instance.n):
            rub += self.instance.v[depth] * self.instance.q[depth]
        return rub

class KnapsackDominance:
    def key(self, state):
        return state.depth
    
    def value(self, state):
        return state.capa
    
    def check(self, a, b):
        return a.capa - b.capa
    
    def use_value(self):
        return True

class KnapsackAggregation:
    def __init__(self, diagram):
        self.diagram = diagram

    def bound(self, state):
        bound = math.inf
        for node in self.diagram.layers[state.depth].nodes.values():
            if node.state.capa >= state.capa:
                bound = min(bound, node.value_bot)
        return bound

    def score(self, state, decision):
        solution = self.diagram.get_best_solution()
        if decision == solution[state.depth]:
            return 1
        else:
            return 0