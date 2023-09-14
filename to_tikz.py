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

    Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings())), state_fmt=state_fmt, show_thresholds=False, arcs_sep_angle=80, arc_positions={
        (KnapsackState(11, 2),KnapsackState(3,3)): .5,
        (KnapsackState(9, 2),KnapsackState(9,3)): .2,
    }).diagram(), "exact_dd")
    
    dds = [
        Tikz(all_dds[0][0], state_fmt=state_fmt, legend="(a) Restricted DD", arc_positions={
            (KnapsackState(9, 2),KnapsackState(1,3)): .2,
            (KnapsackState(5, 2),KnapsackState(5,3)): .5,
        }).diagram(),
        Tikz(all_dds[0][1], state_fmt=state_fmt, legend="(b) Relaxed DD", show_thresholds=False, node_labels={
            KnapsackState(15, 1): "a_1",
            KnapsackState(11, 1): "a_2",
        }, arc_positions={
            (KnapsackState(5, 3),KnapsackState(3,4)): .45,
            (KnapsackState(5, 3),KnapsackState(1,4)): .5,
        }).diagram()
    ]
    Tikz.to_file(Tikz.combine(dds), "root_dds")

    dds = [
        Tikz(all_dds[0][2], state_fmt=state_fmt, legend="(a) Relaxed DD rooted at $a_2$", node_labels={
            KnapsackState(11, 1): "a_2",
            KnapsackState(1, 3): "c_3",
        }).diagram(),
        Tikz(all_dds[0][3], state_fmt=state_fmt, legend="(b) Relaxed DD rooted at $a_1$", node_labels={
            KnapsackState(15, 1): "a_1",
            KnapsackState(1, 3): "c_4",
        }).diagram()
    ]
    Tikz.to_file(Tikz.combine(dds), "cutset_dds")

    dds = [
        Tikz(all_dds[1][2], state_fmt=state_fmt, legend="(a) Relaxed DD rooted at $a_2$", node_labels={
            KnapsackState(11, 1): "a_2",
            KnapsackState(11, 3): "c_1",
        }).diagram(),
        Tikz(all_dds[1][3], state_fmt=state_fmt, legend="(b) Relaxed DD rooted at $a_1$", node_labels={
            KnapsackState(15, 1): "a_1",
            KnapsackState(11, 3): "c_2",
        }).diagram()
    ]
    Tikz.to_file(Tikz.combine(dds), "cutset_dds_pruning")

    dds = [
        Tikz(all_dds[2][2], state_fmt=state_fmt, legend="(a) Relaxed DD rooted at $a_2$", node_labels={
            KnapsackState(11, 1): "a_2",
        }).diagram(),
        Tikz(all_dds[2][3], state_fmt=state_fmt, legend="(b) Relaxed DD rooted at $a_1$", node_labels={
            KnapsackState(15, 1): "a_1",
        }).diagram()
    ]
    Tikz.to_file(Tikz.combine(dds), "cutset_dds_dominance")

    Tikz.to_file(Tikz(all_dds[3][2], state_fmt=state_fmt, node_vertical_spacing=1.2, arcs_sep_angle=120, node_label_style=r"font=\normalsize", node_labels={
        KnapsackState(11, 1): "a_2",
    }).diagram(), "cutset_restricted_1_bab")
    Tikz.to_file(Tikz(all_dds[3][3], state_fmt=state_fmt, node_vertical_spacing=1.2, arcs_sep_angle=120, node_label_style=r"font=\normalsize", show_thresholds=False, node_labels={
        KnapsackState(11, 1): "a_2",
        KnapsackState(11, 2): "b_1",
        KnapsackState(5, 2): "b_2",
        KnapsackState(3, 3): "c_1",
        KnapsackState(1, 4): "d_3",
    }).diagram(), "cutset_relaxed_1_bab")

if __name__ == "__main__":
    main() 