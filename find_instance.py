import random

from knapsack import *
from solver import *

def main():

    rand = random.Random(0)

    found = set()

    while True:
        instance = KnapsackInstance.random(5, rand)

        if hash((instance.c, tuple(instance.w), tuple(instance.v))) in found:
            continue

        model = KnapsackModel(instance)
        dominance_rule = KnapsackDominance()
        
        # check if dominance is used for the exact DD
        dd = Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings(use_dominance=True)))
        best = dd.get_best_value()
        if best == 27 or dd.used_dominance == 0:
            continue

        for order in range(2):
            # check if cache-based pruning is used
            solver = Solver(model, dominance_rule, None, order)
            solver.solve([
                Settings(width=3, cutset=Cutset.LAYER, use_dominance=True),
                Settings(width=3, cutset=Cutset.FRONTIER, use_cache=True, use_dominance=True),
            ], [0])
            if len(solver.dds) != 4 or \
                solver.dds[0].get_best_value() == best or \
                solver.dds[2].input.root.depth != 1 or \
                solver.dds[3].input.root.depth != 1 or \
                solver.dds[3].used_cache_larger == 0:
                continue

            if solver.dds[3].used_cache > 1 and dd.used_dominance > 1:  
                print(instance, solver.dds[3].used_cache, dd.used_dominance)
                found.add(hash((instance.c, tuple(instance.w), tuple(instance.v))))

if __name__ == "__main__":
    main() 