import random

from knapsack import *
from solver import *

def main():

    width = 2
    cutset = Cutset.LAYER

    settings = [
        Settings(width, cutset, use_rub=False, use_locb=False, use_cache=False, use_dominance=False),
        Settings(width, cutset, use_rub=False, use_locb=False, use_cache=False, use_dominance=True)
    ]

    rand = random.Random(0)
    cnt = 0

    while cnt < 10:
        instance = KnapsackInstance.random(4, rand)

        model = KnapsackModel(instance)
        dominance_rule = KnapsackDominance()

        solver = Solver(model, dominance_rule, None)
        solver.solve(settings)

        if len(solver.dds) != 4:
            continue
        if solver.dds[0].used_dominance or solver.dds[1].used_dominance:
            continue
        if not solver.dds[2].used_dominance_real:# or not solver.dds[3].used_dominance:
            continue

        print(instance)
        cnt += 1

if __name__ == "__main__":
    main() 