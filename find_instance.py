import random

from knapsack import *
from solver import *

def main():

    width = 3
    cutset = Cutset.FRONTIER

    settings = [
        [
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=False, use_dominance=False),
            Settings(width, cutset, use_rub=False, use_locb=False, use_cache=True, use_dominance=False),
        ],
        [
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=False, use_dominance=False),
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=True, use_dominance=False),
        ],
        [
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=False, use_dominance=False),
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=True, use_dominance=True),
        ]
    ]

    rand = random.Random(0)

    while True:
        found = True
        instance = KnapsackInstance.random(5, rand)
        all_dds = []

        model = KnapsackModel(instance)
        dominance_rule = KnapsackDominance()

        for i in range(len(settings)):
            setting = settings[i]

            solver = Solver(model, dominance_rule, None)
            solver.solve(setting)

            if len(solver.dds) < 4:
                found = False
                break
            if i == 0 and len(solver.dds) > 5:
                found = False
                break
            if i > 0 and len(solver.dds) > 4:
                found = False
                break
            if setting[0].use_rub:
                if not solver.dds[1].used_rub:
                    found = False
                    break
            if setting[0].use_locb:
                if not solver.dds[1].used_locb:
                    found = False
                    break
            if any(s.use_cache for s in setting):
                if not any(dd.used_cache for dd in solver.dds):
                    found = False
                    break
                if i < 2 and not solver.dds[3].used_cache_larger: # pruning happens with larger value than the one used to compute the threshold
                    found = False
                    break
                if i == 0 and solver.dds[2].is_exact(): # first cutset dd is relaxed
                    found = False
                    break
                if i == 1 and solver.dds[2].is_exact() and solver.dds[2].get_best_value() is not None: # with pruning enabled, first cutset dd is fully pruned
                    found = False
                    break
                if i == 1 and not solver.dds[2].is_exact() and len(solver.dds[2].get_cutset()) > 0: # with pruning enabled, first cutset dd is fully pruned
                    found = False
                    break
                if i == 1 and not solver.dds[3].used_cache_pruning: # with pruning enabled, second cutset dd uses a pruning threshold
                    found = False
                    break
            if any(s.use_dominance for s in setting):
                if not any(dd.used_dominance for dd in solver.dds):
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