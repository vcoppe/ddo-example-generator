import random

from solver import *
from knapsack import *
from tikz import *

def main():
    
    # instance = KnapsackInstance(5, 11, [5, 2, 3, 5, 2], [9, 7, 2, 10, 8], [1, 1, 1, 1, 1])
    instance = KnapsackInstance(5, 8, [2, 4, 2, 3, 2], [2, 8, 10, 9, 7], [1, 1, 1, 1, 1])
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
    solver = Solver(model, dominance_rule, Settings(width=3, cutset=Cutset.LAYER), order=1)
    solver.solve()
    Tikz.to_file(Tikz.combine([
        Tikz(solver.dds[0], state_fmt=state_fmt).diagram(),
        Tikz(solver.dds[1], state_fmt=state_fmt, show_thresholds=False).diagram(),
    ], spacing=8), "first_approximate")
    Tikz.to_file(Tikz.combine([
        Tikz.combine([
            Tikz(solver.dds[2], state_fmt=state_fmt, show_thresholds=False, node_horizontal_spacing=1.4).diagram(),
            Tikz(solver.dds[3], state_fmt=state_fmt, show_thresholds=False, node_horizontal_spacing=1.4).diagram(),
        ], spacing=-0.2),
        Tikz.combine([
            Tikz(solver.dds[4], state_fmt=state_fmt, show_thresholds=False, node_horizontal_spacing=1.4).diagram(),
            Tikz(solver.dds[5], state_fmt=state_fmt, show_thresholds=False, node_horizontal_spacing=1.4).diagram(),
        ], spacing=-0.2)
    ], spacing=1.5), "cutset")

    for i in range(instance.n + 1):
        Tikz.to_file(Tikz(solver.dds[0], state_fmt=state_fmt, show_deleted=True, show_cross=False, max_layer=i).diagram(), "rst_" + str(i) + "_a")
        Tikz.to_file(Tikz(solver.dds[0], state_fmt=state_fmt, show_deleted=True, max_layer=i).diagram(), "rst_" + str(i) + "_b")
        Tikz.to_file(Tikz(solver.dds[0], state_fmt=state_fmt, max_layer=i).diagram(), "rst_" + str(i) + "_c")
    
    for i in range(instance.n + 1):
        Tikz.to_file(Tikz(solver.dds[1], state_fmt=state_fmt, show_thresholds=False, show_deleted=True, show_cross=False, show_merged=False, max_layer=i).diagram(), "rlx_" + str(i) + "_a")
        Tikz.to_file(Tikz(solver.dds[1], state_fmt=state_fmt, show_thresholds=False, show_deleted=True, show_merged=False, max_layer=i).diagram(), "rlx_" + str(i) + "_b")
        Tikz.to_file(Tikz(solver.dds[1], state_fmt=state_fmt, show_thresholds=False, max_layer=i).diagram(), "rlx_" + str(i) + "_c")

    # show cutset exact DDs
    solver = Solver(model, dominance_rule, None, order=1)
    solver.solve([Settings(width=3, cutset=Cutset.LAYER), Settings()])
    Tikz.to_file(Tikz.combine([
        Tikz(solver.dds[3], state_fmt=state_fmt, show_thresholds=False).diagram(),
        Tikz(solver.dds[2], state_fmt=state_fmt, show_thresholds=False).diagram(),
    ], spacing=1.6), "cutset_exact")

    # show dominance used for the exact DD
    Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings(use_dominance=True))), state_fmt=state_fmt, show_thresholds=False, max_nodes=6).diagram(), "exact_dominance")

    # show cache-based pruning is used
    solver = Solver(model, dominance_rule, None, order=0)
    solver.solve([
        Settings(width=3, cutset=Cutset.LAYER, use_dominance=False),
        Settings(width=3, cutset=Cutset.FRONTIER, use_cache=True, use_dominance=True),
    ], [0])
    Tikz.to_file(Tikz.combine([
        Tikz(solver.dds[0], state_fmt=state_fmt).diagram(),
        Tikz(solver.dds[1], state_fmt=state_fmt, show_thresholds=False).diagram(),
    ]), "cache_1")
    Tikz.to_file(Tikz.combine([
        Tikz(solver.dds[2], state_fmt=state_fmt).diagram(),
        Tikz(solver.dds[3], state_fmt=state_fmt, show_thresholds=False).diagram(),
    ]), "cache_2")

    # show exact aggregate
    instance = KnapsackInstance(5, 8, [2, 2, 2, 2, 2], [2, 8, 10, 9, 7], [1, 1, 1, 1, 1])
    model = KnapsackModel(instance)
    Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), True, Settings(use_locb=True))), state_fmt=state_fmt, show_thresholds=False, show_locbs=True, max_nodes=6).diagram(), "aggregate")

    # show large exact DD
    # instance = KnapsackInstance.random(20, random.Random(0))
    # model = KnapsackModel(instance)
    # Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings())), state_fmt=state_fmt, show_thresholds=False, max_nodes=30).diagram(), "exact_large")

if __name__ == "__main__":
    main() 