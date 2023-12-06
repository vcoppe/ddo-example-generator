from solver import *
from knapsack import *
from tikz import *

def main():

    instance = KnapsackInstance(5, 15, [4, 6, 4, 2, 5], [2, 3, 6, 6, 1], [1, 1, 2, 2, 1])

    model = KnapsackModel(instance)
    dominance_rule = KnapsackDominance()

    state_fmt = lambda x: str(x.capa)

    #Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings())), state_fmt=state_fmt, show_thresholds=False, max_nodes=15, node_horizontal_spacing=3.5).diagram(), "exact_dd")

    Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings())), state_fmt=state_fmt, show_thresholds=False, max_nodes=8, arcs_sep_angle=120).diagram(), "exact_dd")

if __name__ == "__main__":
    main() 