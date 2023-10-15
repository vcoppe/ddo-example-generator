from solver import *
from knapsack import *
from tikz import *

def main():

    state_fmt = lambda x: str(x.capa)

    dominance_rule = KnapsackDominance()

    dds = []

    instance = KnapsackInstance(5, 15, [4, 4, 4, 2, 4], [2, 3, 6, 6, 1], [1, 1, 2, 2, 1])
    model = KnapsackModel(instance)

    dds.append(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), True, Settings())), state_fmt=state_fmt, show_thresholds=False, arcs_sep_angle=80, legend="(a) Exact DD for aggregation (A)", node_labels={
        KnapsackState(11, 1): "a_2'",
        KnapsackState(11, 2): "b_2'",
    }).diagram())

    aggregated_a = Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), True, Settings()))

    instance = KnapsackInstance(3, 15, [4, 2, 5], [3, 6, 1], [2, 4, 1])
    model = KnapsackModel(instance)

    dds.append(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), True, Settings())), state_fmt=state_fmt, show_thresholds=False, arcs_sep_angle=80, legend="(b) Exact DD for aggregation (B)", node_labels={
        KnapsackState(1, 2): "d_4'",
    }).diagram())

    aggregated_b = Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), True, Settings()))

    Tikz.to_file(Tikz.combine(dds), "exact_dds_agg")

    relaxed_dds = []

    instance = KnapsackInstance(5, 15, [4, 6, 4, 2, 5], [2, 3, 6, 6, 1], [1, 1, 2, 2, 1])
    model = KnapsackModel(instance, KnapsackAggregationA(aggregated_a))

    solver = Solver(model, dominance_rule, None)
    solver.solve([Settings(3, cutset=Cutset.FRONTIER, use_rub=True, use_locb=True, use_cache=True, use_dominance=True, use_aggb=True)])

    relaxed_dds.append(Tikz(solver.dds[1], state_fmt=state_fmt, show_thresholds=False, show_locbs=False, legend="(a) Relaxed DD with AggB (A)", node_labels={
        KnapsackState(11, 1): "a_2",
        KnapsackState(9, 2): "b_2",
        KnapsackState(15, 3): "c_1",
        KnapsackState(11, 3): "c_2",
        KnapsackState(7, 4): "d_1",
        KnapsackState(5, 4): "d_2",
    }).diagram())

    model = KnapsackModel(instance, KnapsackAggregationB(aggregated_b, instance))

    solver = Solver(model, dominance_rule, None)
    solver.solve([Settings(3, cutset=Cutset.FRONTIER, use_rub=True, use_locb=True, use_cache=True, use_dominance=True, use_aggb=True)])

    relaxed_dds.append(Tikz(solver.dds[1], state_fmt=state_fmt, show_thresholds=False, legend="(b) Relaxed DD with AggB (B)", node_labels={
        KnapsackState(1, 4): "d_4",
    }).diagram())

    Tikz.to_file(Tikz.combine(relaxed_dds), "relaxed_dd_aggb")

    restricted_dds = []

    instance = KnapsackInstance(5, 15, [4, 6, 4, 2, 5], [2, 3, 6, 6, 1], [1, 1, 2, 2, 1])
    model = KnapsackModel(instance, KnapsackAggregationA(aggregated_a))

    solver = Solver(model, dominance_rule, None)
    solver.solve([Settings(3, cutset=Cutset.FRONTIER, use_rub=True, use_locb=True, use_cache=True, use_dominance=False, use_aggh=True)])

    restricted_dds.append(Tikz(solver.dds[0], state_fmt=state_fmt, legend="(a) Restricted DD with AggH (A)").diagram())

    model = KnapsackModel(instance, KnapsackAggregationB(aggregated_b, instance))

    solver = Solver(model, dominance_rule, None)
    solver.solve([Settings(3, cutset=Cutset.FRONTIER, use_rub=True, use_locb=True, use_cache=True, use_dominance=False, use_aggh=True)])

    restricted_dds.append(Tikz(solver.dds[0], state_fmt=state_fmt, show_thresholds=False, legend="(b) Restricted DD with AggH (B)").diagram())

    Tikz.to_file(Tikz.combine(restricted_dds), "restricted_dd_aggh")

if __name__ == "__main__":
    main() 