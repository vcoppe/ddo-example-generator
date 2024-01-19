import random

from solver import *
from knapsack import *
from tikz import *

def main():

    # instance<5, 15, [3, 6, 5, 3, 5], [7, 8, 9, 2, 10], [1, 1, 1, 1, 1]>
    # instance<5, 15, [5, 6, 5, 5, 6], [8, 9, 2, 7, 10], [1, 1, 1, 1, 1]>
    # instance<5, 15, [5, 6, 5, 5, 5], [9, 10, 8, 2, 7], [1, 1, 1, 1, 1]>
    # instance<5, 15, [3, 6, 5, 3, 6], [7, 8, 9, 2, 10], [1, 1, 1, 1, 1]>
    # instance<5, 15, [3, 5, 6, 3, 6], [7, 9, 8, 2, 10], [1, 1, 1, 1, 1]>
    # instance<5, 15, [3, 6, 5, 3, 6], [7, 8, 10, 2, 9], [1, 1, 1, 1, 1]>
    # instance<5, 15, [5, 6, 5, 5, 6], [9, 10, 7, 2, 8], [1, 1, 1, 1, 1]>
    # instance<5, 15, [3, 4, 6, 3, 6], [7, 10, 8, 2, 9], [1, 1, 1, 1, 1]>
    # instance<5, 15, [3, 5, 6, 3, 5], [7, 10, 8, 2, 9], [1, 1, 1, 1, 1]>
    # instance<5, 15, [3, 5, 6, 3, 6], [7, 10, 8, 2, 9], [1, 1, 1, 1, 1]>
    # instance<5, 15, [5, 6, 5, 5, 5], [9, 10, 2, 8, 7], [1, 1, 1, 1, 1]>
    # instance<5, 15, [3, 6, 4, 3, 6], [7, 8, 10, 2, 9], [1, 1, 1, 1, 1]>
    # instance<5, 15, [4, 6, 4, 4, 6], [8, 10, 2, 7, 9], [1, 1, 1, 1, 1]>
    # instance<5, 15, [5, 6, 5, 5, 6], [8, 10, 7, 2, 9], [1, 1, 1, 1, 1]>

    instance = KnapsackInstance(5, 12, [4, 5, 4, 4, 4], [9, 10, 2, 7, 8], [1, 1, 1, 1, 1])

    state_fmt = lambda x: "" if x.depth == instance.n and x.mode == CompilationMode.DD else str(x.capa) + "€"

    model = KnapsackModel(instance, CompilationMode.TREE)
    dominance_rule = KnapsackDominance()

    # show tree
    for i in range(instance.n + 1):
        Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings())), state_fmt=state_fmt, show_thresholds=False, max_nodes=11, max_layer=i).diagram(), "tree_" + str(i))

    model = KnapsackModel(instance, CompilationMode.DP)

    # show DP
    Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings())), state_fmt=state_fmt, show_thresholds=False, max_nodes=6).diagram(), "dp")

    model = KnapsackModel(instance)

    # show exact DD
    Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings())), state_fmt=state_fmt, show_thresholds=False, max_nodes=6).diagram(), "exact")

    # show first approximate DD
    solver = Solver(model, dominance_rule, Settings(width=3, cutset=Cutset.LAYER))
    solver.solve()
    Tikz.to_file(Tikz.combine([
        Tikz(solver.dds[0], state_fmt=state_fmt).diagram(),
        Tikz(solver.dds[1], state_fmt=state_fmt, show_thresholds=False).diagram(),
    ]), "first_approximate")

    for i in range(instance.n + 1):
        Tikz.to_file(Tikz(solver.dds[0], state_fmt=state_fmt, show_deleted=True, max_layer=i).diagram(), "rst_" + str(i) + "_a")
        Tikz.to_file(Tikz(solver.dds[0], state_fmt=state_fmt, max_layer=i).diagram(), "rst_" + str(i) + "_b")

    # show dominance used for the exact DD
    Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings(use_dominance=True))), state_fmt=state_fmt, show_thresholds=False, max_nodes=6).diagram(), "exact_dominance")

    # show cache-based pruning is used
    solver = Solver(model, dominance_rule, None)
    solver.solve([
        Settings(width=3, cutset=Cutset.LAYER, use_dominance=True),
        Settings(width=3, cutset=Cutset.FRONTIER, use_cache=True, use_dominance=True),
    ], [0])
    Tikz.to_file(Tikz.combine([
        Tikz(solver.dds[0], state_fmt=state_fmt).diagram(),
        Tikz(solver.dds[1], state_fmt=state_fmt, show_thresholds=False).diagram(),
        Tikz(solver.dds[2], state_fmt=state_fmt).diagram(),
        Tikz(solver.dds[3], state_fmt=state_fmt).diagram(),
    ]), "cache")

    # show large exact DD
    # instance = KnapsackInstance.random(20, random.Random(0))
    # model = KnapsackModel(instance)
    # Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings())), state_fmt=state_fmt, show_thresholds=False, max_nodes=30).diagram(), "exact_large")

if __name__ == "__main__":
    main() 