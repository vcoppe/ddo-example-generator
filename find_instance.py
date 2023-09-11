import random

from knapsack import *
from dd import *

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
            input = CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, width, Cutset.LAYER, use_rub, use_locb, use_cache, use_dominance)
            dds = []

            dds.append(Diagram(input))
            dds[-1].compile()

            if dds[-1].get_best_value() is not None:
                input.best = dds[-1].get_best_value()

            input.relaxed = True

            dds.append(Diagram(input))
            dds[-1].compile()

            cutset = dds[-1].get_cutset()

            if len(cutset) == 0:
                found = False
                break

            for node in sorted(cutset, key=lambda n: n.ub, reverse=True):
                if node.ub <= input.best:
                    continue

                input.root = node
                dds.append(Diagram(input))
                dds[-1].compile()

                if dds[-1].get_best_value() is not None and dds[-1].get_best_value() > input.best:
                    input.best = dds[-1].get_best_value()

            if use_dominance:
                if not (dds[0].used_dominance or dds[1].used_dominance):
                    found = False
                    break
            elif use_cache:
                if not any(dd.used_cache for dd in dds):
                    found = False
                    break
            elif use_locb:
                if not dds[1].used_locb:
                    found = False
                    break
            elif use_rub:
                if not dds[1].used_rub:
                    found = False
                    break

            all_dds.append(dds)
            
        if found:
            print(instance)
            for dds in all_dds:
                print("=========== dds for next config ===========")
                for dd in dds:
                    print(dd)

if __name__ == "__main__":
    main() 