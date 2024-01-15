from solver import *
from knapsack import *
from tikz import *

def main():

    width = 2
    cutset = Cutset.LAYER

    settings = [
        Settings(width, cutset, use_rub=False, use_locb=False, use_cache=False, use_dominance=False),
        Settings(width, cutset, use_rub=False, use_locb=False, use_cache=False, use_dominance=True),
    ]

    instance = KnapsackInstance(4, 12, [6, 5, 6, 6], [5, 6, 1, 6], [1, 1, 1, 1])

    model = KnapsackModel(instance)
    dominance_rule = KnapsackDominance()

    state_fmt = lambda x: str(x.capa)

    solver = Solver(model, dominance_rule, None)
    solver.solve(settings)
    
    Tikz.to_file(
        Tikz.combine([
            Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings())), state_fmt=state_fmt, legend="(a) Exact", show_thresholds=False, show_layer_label=True, show_variable_label=True).diagram(),
            Tikz(solver.dds[0], state_fmt=state_fmt, legend="(b) Restricted").diagram(),
            Tikz(solver.dds[1], state_fmt=state_fmt, legend="(c) Relaxed", show_locbs=False, show_thresholds=False, node_labels={
                KnapsackState(12, 1): "a_1",
                KnapsackState(6, 1): "a_2",
            }).diagram(),
        ], spacing=0.8), 
        "root_dds"
    )

    Tikz.to_file(
        Tikz.combine([
            Tikz(solver.dds[2], state_fmt=state_fmt, legend=r"(a) Exact DD from $a_2$", show_thresholds=False, node_labels={
                KnapsackState(6, 1): "a_2",
                KnapsackState(6, 3): "c_1",
                KnapsackState(1, 3): "c_2",
                KnapsackState(0, 3): "c_3",
            }).diagram(),
            Tikz(solver.dds[3], state_fmt=state_fmt, legend=r"(b) Exact DD from $a_1$", node_horizontal_spacing=1.7, show_locbs=False, show_thresholds=False, node_labels={
                KnapsackState(12, 1): "a_1",
                KnapsackState(12, 3): "c_4",
                KnapsackState(7, 3): "c_5",
                KnapsackState(6, 3): "c_6",
                KnapsackState(1, 3): "c_7",
            }).diagram(),
        ]), 
        "next_dds"
    )

if __name__ == "__main__":
    main() 