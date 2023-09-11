import random

from knapsack import *
from solver import *

def main():
    configs = [(True, False, False, False), (True, True, False, False), (True, True, True, False), (True, True, True, True), (False, False, False, False)]

    rand = random.Random(0)

    while True:
        found = True
        instance = KnapsackInstance.random(5, rand)
        all_dds = []

        model = KnapsackModel(instance)
        dominance_rule = KnapsackDominance()

        width = 3

        for (use_rub, use_locb, use_cache, use_dominance) in configs:
            solver = Solver(model, dominance_rule, Settings(width, Cutset.LAYER, use_rub, use_locb, use_cache, use_dominance))
            solver.solve()

            if len(solver.dds) < 2:
                found = False
                break

            if use_dominance:
                if not (solver.dds[0].used_dominance or solver.dds[1].used_dominance):
                    found = False
                    break
            elif use_cache:
                if not any(dd.used_cache for dd in solver.dds):
                    found = False
                    break
            elif use_locb:
                if not solver.dds[1].used_locb:
                    found = False
                    break
            elif use_rub:
                if not solver.dds[1].used_rub:
                    found = False
                    break

            all_dds.append(solver.dds)
            
        if found:
            print(instance)
            for dds in all_dds:
                print("=========== dds for next config ===========")
                for dd in dds:
                    print(dd)

if __name__ == "__main__":
    main() 