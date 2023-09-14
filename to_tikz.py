from solver import *
from knapsack import *
from tikz import *

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

    instance = KnapsackInstance(5, 15, [4, 6, 4, 2, 5], [2, 3, 6, 6, 1], [1, 1, 2, 2, 1])

    model = KnapsackModel(instance)
    dominance_rule = KnapsackDominance()

    state_fmt = lambda x: str(x.capa)

    Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings())), state_fmt=state_fmt, show_thresholds=False).convert("root_exact")

    all_dds = []

    for i in range(len(settings)):
        setting = settings[i]

        solver = Solver(model, dominance_rule, None)
        solver.solve(setting, [0])

        all_dds.append(solver.dds)

    setting = settings[0]

    solver = Solver(model, dominance_rule, None)
    solver.solve(setting, [0, 1])

    all_dds.append(solver.dds)
        
    Tikz(all_dds[0][0], state_fmt=state_fmt).convert("root_restricted")
    Tikz(all_dds[0][1], state_fmt=state_fmt, show_thresholds=False, node_labels={
        KnapsackState(15, 1): "a_1",
        KnapsackState(11, 1): "a_2",
    }).convert("root_relaxed")

    Tikz(all_dds[0][2], state_fmt=state_fmt, node_labels={
        KnapsackState(11, 1): "a_2",
        KnapsackState(1, 3): "c_3",
    }).convert("cutset_relaxed_1")
    Tikz(all_dds[0][3], state_fmt=state_fmt, node_labels={
        KnapsackState(15, 1): "a_1",
        KnapsackState(1, 3): "c_4",
    }).convert("cutset_relaxed_2")

    Tikz(all_dds[1][2], state_fmt=state_fmt, node_labels={
        KnapsackState(11, 1): "a_2",
        KnapsackState(11, 3): "c_1",
    }).convert("cutset_relaxed_1_pruning")
    Tikz(all_dds[1][3], state_fmt=state_fmt, node_labels={
        KnapsackState(15, 1): "a_1",
        KnapsackState(11, 3): "c_2",
    }).convert("cutset_relaxed_2_pruning")

    Tikz(all_dds[2][2], state_fmt=state_fmt, node_labels={
        KnapsackState(11, 1): "a_2",
    }).convert("cutset_relaxed_1_dominance")
    Tikz(all_dds[2][3], state_fmt=state_fmt, node_labels={
        KnapsackState(15, 1): "a_1",
    }).convert("cutset_relaxed_2_dominance")

    Tikz(all_dds[3][2], state_fmt=state_fmt, node_vertical_spacing=1.5, node_labels={
        KnapsackState(11, 1): "a_2",
    }).convert("cutset_restricted_1_bab")
    Tikz(all_dds[3][3], state_fmt=state_fmt, node_vertical_spacing=1.5, show_thresholds=False, node_labels={
        KnapsackState(11, 1): "a_2",
    }).convert("cutset_relaxed_1_bab")

if __name__ == "__main__":
    main() 