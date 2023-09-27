import math
from bitarray import bitarray

class TalentSchedInstance:
    def __init__(self, n, d, c, r):
        self.n = n
        self.d = d
        self.c = c
        self.r = r
    
    def __str__(self):
        return "instance<n=" + str(self.n) + ",d=" + str(self.d) + ",c=" + str(self.c) + ",r=" + str(self.r) + ">"

class TalentSchedState:
    def __init__(self, scenes, maybe_scenes=bitarray()):
        self.scenes = scenes
        self.maybe_scenes = maybe_scenes

    def clone(self):
        return TalentSchedState(self.scenes, self.maybe_scenes)
    
    def __lt__(self, other): # used only for tikz output
        return (self.scenes, self.maybe_scenes) > (other.scenes, other.maybe_scenes)

    def __hash__(self):
        return hash((self.scenes, self.maybe_scenes))

    def __eq__(self, other):
        return (self.scenes, self.maybe_scenes) == (other.scenes, other.maybe_scenes)
    
    def __str__(self):
        return "state<scenes=" + str(self.scenes) + \
            (str(self.maybe_scenes) if self.maybe_scenes.count() > 0 else "") + \
            ">"

class TalentSchedModel:
    def __init__(self, instance):
        self.instance = instance
    
    def nb_variables(self):
        return self.instance.n

    def root(self):
        return TalentSchedState(bitarray('1' * self.instance.n))

    def domain(self, state, variable):
        return range(self.instance.n)
    
    def successor(self, state, decision):
        if not state.scenes[decision] and not state.maybe_scenes[decision]:
            return None
        successor = state.clone()
        successor.scenes[decision] = False
        successor.maybe_scenes[decision] = False
        return successor
    
    def reward(self, state, decision):
        
    
    def merge(self, a, b):
        a.maybe_scenes |= a.scenes
        a.maybe_scenes |= b.scenes
        a.maybe_scenes |= b.maybe_scenes
        a.scenes &= a.scenes
    
    def rough_upper_bound(self, state):
        return 0
