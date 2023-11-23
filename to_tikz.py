from solver import *
from knapsack import *
from tikz import *

def main():

    state_fmt = lambda x: str(x.capa)

    dominance_rule = KnapsackDominance()

    instance = KnapsackInstance(5, 15, [4, 4, 4, 2, 4], [2, 3, 6, 6, 1], [1, 1, 2, 2, 1])
    model = KnapsackModel(instance)

    Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), True, Settings())), state_fmt=state_fmt, show_thresholds=False, arcs_sep_angle=80).diagram(), "exact_dd_agg")

    aggregated = Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), True, Settings()))

    instance = KnapsackInstance(5, 15, [4, 6, 4, 2, 5], [2, 3, 6, 6, 1], [1, 1, 2, 2, 1])
    model = KnapsackModel(instance, KnapsackAggregationA(aggregated))

    solver = Solver(model, dominance_rule, None)
    solver.solve([Settings(3, cutset=Cutset.FRONTIER, use_rub=True, use_locb=True, use_cache=True, use_dominance=True, use_aggb=True)])

    Tikz.to_file(Tikz(solver.dds[1], state_fmt=state_fmt, show_thresholds=False, show_locbs=False).diagram(), "relaxed_dd_aggb")
    
    solver = Solver(model, dominance_rule, None)
    solver.solve([Settings(3, cutset=Cutset.FRONTIER, use_rub=True, use_locb=True, use_cache=True, use_dominance=False, use_aggh=True)])

    Tikz.to_file(Tikz(solver.dds[0], state_fmt=state_fmt).diagram(), "restricted_dd_aggh")

if __name__ == "__main__":
    main() 