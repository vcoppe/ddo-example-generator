class CsrflpInstance:
    def __init__(self, n, l, c, p=None, o=None, r=None):
        self.n = n
        self.l = l
        self.c = c
        self.position = dict()
        self.department = dict()
        self.predecessors = [frozenset() for i in range(n)]
        self.previous = dict()

        if p is not None:
            for (dep, pos) in p:
                self.position[dep] = pos
                self.department[pos] = dep

        if o is not None:
            for (dep1, dep2) in o:
                self.predecessors[dep2] |= frozenset([dep1])

        if r is not None:
            for (dep1, dep2) in r:
                self.previous[dep2] = dep1
    
    def __str__(self):
        return "instance<n=" + str(self.n) + ",l=" + str(self.l) + ",c=" + str(self.c) + ",p=" + str(self.p) + ",o=" + str(self.o) + ",r=" + str(self.r) + ">"

class CsrflpState:
    def __init__(self, must):
        self.must = must

    def clone(self):
        return CsrflpState(self.must.copy())
    
    def __lt__(self, other): # used only for tikz output
        return self.must < other.must

    def __hash__(self):
        return hash(self.must)

    def __eq__(self, other):
        return self.must == other.must
    
    def __str__(self):
        return "state<must=" + str(self.must) + ">"

class CsrflpModel:
    def __init__(self, instance):
        self.instance = instance
    
    def nb_variables(self):
        return self.instance.n

    def root(self):
        return CsrflpState(frozenset(range(self.instance.n)))
    
    def root_value(self):
        val = 0
        for i in range(self.instance.n):
            for j in range(i+1, self.instance.n):
                val += self.instance.c[i][j] * (self.instance.l[i] + self.instance.l[j])/ 2
        return - val

    def domain(self, state, position):
        placed = frozenset(range(self.instance.n)) - state.must

        must_place_pos = None
        if position in self.instance.department:
            must_place_pos = self.instance.department[position]
            if not self.instance.predecessors[must_place_pos] <= placed:
                return []
            if must_place_pos in self.instance.previous and self.instance.previous[must_place_pos] not in placed:
                return []
            
        must_place_rel = None
        for i in state.must:
            if i in self.instance.previous and self.instance.previous[i] in placed:
                must_place_rel = i
                if not self.instance.predecessors[must_place_rel] <= placed:
                    return []
                if must_place_rel in self.instance.position and self.instance.position[must_place_rel] != position:
                    return []
                
        if must_place_pos is not None or must_place_rel is not None:
            if must_place_pos is not None and must_place_rel is not None:
                if must_place_pos == must_place_rel:
                    return [must_place_pos]
                else:
                    return []
            elif must_place_pos is not None:
                return [must_place_pos]
            else:
                return [must_place_rel]
        
        dom = []
        for i in state.must:
            if i not in self.instance.position and i not in self.instance.previous and self.instance.predecessors[i] <= placed:
                dom.append(i)

        return dom
    
    def successor(self, state, decision):
        must = state.must - frozenset([decision])
        return CsrflpState(must)
    
    def reward(self, state, decision):
        cost = 0
        left = frozenset(range(self.instance.n)) - state.must
        right = state.must - frozenset([decision])
        for i in left:
            for j in right:
                cost += self.instance.c[i][j] * self.instance.l[decision]
        return - cost
    
    def merge(self, a, b):
        a.must -= b.must
    
    def rough_upper_bound(self, state):
        return 0