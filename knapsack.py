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
        return "instance<n=" + str(self.n) + ",c=" + str(self.c) + ",v=" + str(self.v) + ",w=" + str(self.w) + ",q=" + str(self.q) + ">"
    
    def random(n, rand):
        alpha = 6
        beta = 2

        c = n * alpha // beta
        v = []
        w = []
        q = [1 + i % 2 for i in range(n)]
        q[-1] = rand.randint(1, 2)

        rand.shuffle(q)

        for _ in range(n):
            v.append(rand.randint(1, alpha))
            w.append(rand.randint(1, alpha))
        
        return KnapsackInstance(n, c, w, v, q)

class KnapsackState:
    def __init__(self, capa, depth):
        self.capa = capa
        self.depth = depth

    def clone(self):
        return KnapsackState(self.capa, self.depth)

    def __hash__(self):
        return hash((self.capa, self.depth))

    def __eq__(self, other):
        return (self.capa, self.depth) == (other.capa, other.depth)
    
    def __str__(self):
        return "state<capa=" + str(self.capa) + ">"

class KnapsackModel:
    def __init__(self, instance):
        self.instance = instance
    
    def nb_variables(self):
        return self.instance.n

    def root(self):
        return KnapsackState(self.instance.c, 0)

    def domain(self, state, variable):
        return range(self.instance.q[variable] + 1)
    
    def successor(self, state, decision):
        capa = state.capa - decision * self.instance.w[state.depth]
        if capa < 0:
            return None
        return KnapsackState(capa, state.depth + 1)
    
    def reward(self, state, decision):
        return decision * self.instance.v[state.depth]
    
    def merge(self, a, b):
        a.capa = max(a.capa, b.capa)
        a.depth = max(a.depth, b.depth)
    
    def rough_upper_bound(self, state):
        if USE_LP_BOUND:
            return self.lp_bound(state)
        else:
            return self.simple_bound(state)
    
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
