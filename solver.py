from queue import PriorityQueue
from dd import *

class Settings:
    def __init__(self, width=math.inf, cutset=Cutset.LAYER, use_rub=False, use_locb=False, use_cache=False, use_dominance=False):
        self.width = width
        self.cutset = cutset
        self.use_rub = use_rub
        self.use_locb = use_locb
        self.use_cache = use_cache
        self.use_dominance = use_dominance

class Solver:
    def __init__(self, model, dominance_rule, settings):
        self.input = CompilationInput(model, dominance_rule, None, 0, dict(), dict(), False, settings)
        self.dds = []
        self.queue = PriorityQueue()
    
    def enqueue(self, node):
        self.queue.put((- node.ub, node))
    
    def dequeue(self):
        return self.queue.get()[1]
    
    def finished(self):
        return self.queue.empty()
    
    def update_best(self, dd):
        best = dd.get_best_value()
        if best is not None and best > self.input.best:
            self.input.best = best


    def solve(self, settings=None):
        it = 0
        self.enqueue(Node(self.input.model.root()))

        while not self.finished():
            self.input.root = self.dequeue()

            if self.input.root.ub <= self.input.best:
                continue

            if settings is not None and it < len(settings):
                self.input.settings = settings[it]
                it += 1

            self.input.relaxed = False

            if it == 1:
                restricted = Diagram(self.input)
                self.dds.append(restricted)

                self.update_best(restricted)

                if restricted.is_exact():
                    continue

            self.input.relaxed = True

            relaxed = Diagram(self.input)
            self.dds.append(relaxed)

            if relaxed.is_exact():
                self.update_best(relaxed)
            else:
                cutset = relaxed.get_cutset()
                for node in cutset:
                    self.enqueue(Node(node.state, node.depth, node.value_top, ub=node.ub))