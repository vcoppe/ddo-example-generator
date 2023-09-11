import random

from knapsack import *
from solver import *

def main():

    width = 3
    cutset = Cutset.FRONTIER

    settings = [
        [
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=False, use_dominance=False),
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=False, use_dominance=False),
            Settings(width, cutset, use_rub=False, use_locb=False, use_cache=True, use_dominance=False),
            Settings(width, cutset, use_rub=False, use_locb=False, use_cache=True, use_dominance=False),
        ],
        [
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=False, use_dominance=False),
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=False, use_dominance=False),
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=True, use_dominance=False),
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=True, use_dominance=False),
        ],
        [
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=False, use_dominance=True),
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=False, use_dominance=True),
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=True, use_dominance=True),
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

            if any(s.use_dominance for s in setting):
                if not any(dd.used_dominance for dd in solver.dds):
                    found = False
                    break
            if any(s.use_cache for s in setting):
                if not any(dd.used_cache for dd in solver.dds):
                    found = False
                    break
                cnt = 0
                for dd in solver.dds:
                    if dd.relaxed or dd.is_exact():
                        cnt += 1
                        if cnt == 3 and ((i == 0 and not dd.used_cache_larger) or (i > 0 and not dd.used_cache)):
                            found = False
                            break
            if setting[1].use_locb:
                if not solver.dds[1].used_locb:
                    found = False
                    break
            if setting[1].use_rub:
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