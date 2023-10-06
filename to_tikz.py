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
            Settings(width, cutset, use_rub=True, use_locb=True, use_cache=False, use_dominance=True),
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

    solver = Solver(model, dominance_rule, None)
    solver.solve([Settings(width, cutset=Cutset.LAYER, use_rub=False, use_locb=False, use_cache=False, use_dominance=False)])

    all_dds.append(solver.dds)

    solver = Solver(model, dominance_rule, None)
    solver.solve([Settings(width, cutset=Cutset.FRONTIER, use_rub=True, use_locb=True, use_cache=False, use_dominance=True)])

    all_dds.append(solver.dds)

    Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings())), state_fmt=state_fmt, show_thresholds=False, show_layer_label=True, show_variable_label=True, arcs_sep_angle=80, arc_positions={
        (KnapsackState(11, 2),KnapsackState(3,3)): .5,
        (KnapsackState(9, 2),KnapsackState(9,3)): .2,
    }).diagram(), "exact_dd")

    Tikz.to_file(Tikz(Diagram(CompilationInput(model, dominance_rule, Node(model.root()), 0, dict(), dict(), False, Settings(use_dominance=True))), state_fmt=state_fmt, show_thresholds=False, arcs_sep_angle=80, arc_positions={
        (KnapsackState(11, 2),KnapsackState(3,3)): .5,
        (KnapsackState(9, 2),KnapsackState(9,3)): .2,
        (KnapsackState(11, 4),KnapsackState(15,5)): .45,
        (KnapsackState(7, 4),KnapsackState(15,5)): .45,
    }).diagram(), "exact_dd_dominance")
    
    Tikz.to_file(Tikz(all_dds[0][1], state_fmt=state_fmt, show_thresholds=False, node_horizontal_spacing=2.2, node_labels={
        KnapsackState(15, 1): "a_1",
        KnapsackState(11, 1): "a_2",
        KnapsackState(15, 3): "c_1",
        KnapsackState(11, 3): "c_2",
        KnapsackState(9, 3): "c_3",
        KnapsackState(5, 3): "c_4",
        KnapsackState(7, 4): "d_1",
        KnapsackState(5, 4): "d_2",
        KnapsackState(1, 4): "d_3",
    }, arc_positions={
        (KnapsackState(5, 3),KnapsackState(3,4)): .45,
        (KnapsackState(5, 3),KnapsackState(1,4)): .5,
    }).diagram(), "root_dds_pruning")

    dds = [
        Tikz(all_dds[0][2], state_fmt=state_fmt, node_horizontal_spacing=2.5, show_locbs=False, theta=r"\theta_d", legend="(a) Relaxed DD rooted at $a_2$", node_labels={
            KnapsackState(11, 1): "a_2",
            KnapsackState(11, 2): "b_1",
            KnapsackState(5, 2): "b_2",
            KnapsackState(3, 3): "c_1",
            KnapsackState(1, 3): "c_2",
            KnapsackState(1, 4): "d_1",
        }).diagram(),
        Tikz(all_dds[0][3], state_fmt=state_fmt, show_locbs=False, show_thresholds=False, legend="(b) Relaxed DD rooted at $a_1$", node_labels={
            KnapsackState(15, 1): "a_1",
            KnapsackState(1, 3): "c_2'",
            KnapsackState(1, 4): "d_1'",
        }).diagram()
    ]
    Tikz.to_file(Tikz.combine(dds), "cutset_dds")

    dds = [
        Tikz(all_dds[1][2], state_fmt=state_fmt, show_locbs=False, theta=r"\theta_p", node_horizontal_spacing=1.7, legend="(a) Relaxed DD rooted at $a_2$", node_labels={
            KnapsackState(11, 1): "a_2",
            KnapsackState(11, 3): Label("c_1", "bottom"),
            KnapsackState(1, 3): Label("c_2", "bottom"),
            KnapsackState(3, 4): Label("d_1", "bottom"),
            KnapsackState(1, 4): Label("d_2", "bottom"),
        }).diagram(),
        Tikz(all_dds[1][3], state_fmt=state_fmt, show_locbs=False, node_horizontal_spacing=1.7, show_thresholds=False, legend="(b) Relaxed DD rooted at $a_1$", node_labels={
            KnapsackState(15, 1): "a_1",
            KnapsackState(11, 3): Label("c_1'", "bottom"),
            KnapsackState(1, 3): Label("c_2'", "bottom"),
            KnapsackState(3, 4): Label("d_1'", "bottom"),
            KnapsackState(1, 4): Label("d_2'", "bottom"),
        }).diagram()
    ]
    Tikz.to_file(Tikz.combine(dds, spacing=0.7), "cutset_dds_pruning")

    dds = [
        Tikz(all_dds[2][2], state_fmt=state_fmt, legend="(a) Relaxed DD rooted at $a_2$", show_locbs=False, node_labels={
            KnapsackState(11, 1): "a_2",
        }).diagram(),
        Tikz(all_dds[2][3], state_fmt=state_fmt, legend="(b) Relaxed DD rooted at $a_1$", show_locbs=False, node_labels={
            KnapsackState(15, 1): "a_1",
        }).diagram()
    ]
    Tikz.to_file(Tikz.combine(dds), "cutset_dds_dominance")
    
    dds = [
        Tikz(all_dds[3][0], state_fmt=state_fmt, legend=r"(a) Restricted DD $\rst{B}$", arc_positions={
            (KnapsackState(9, 2),KnapsackState(1,3)): .2,
            (KnapsackState(5, 2),KnapsackState(5,3)): .5,
        }).diagram(),
        Tikz(all_dds[3][1], state_fmt=state_fmt, legend="(b) Relaxed DD", show_locbs=False, show_thresholds=False, arc_positions={
            (KnapsackState(9, 2),KnapsackState(1,3)): .2,
            (KnapsackState(5, 2),KnapsackState(15,3)): .5,
            (KnapsackState(7, 3),KnapsackState(3,4)): .2,
            (KnapsackState(1, 3),KnapsackState(15,4)): .5,
        }).diagram()
    ]
    Tikz.to_file(Tikz.combine(dds, spacing=2), "root_dds")

    Tikz.to_file(Tikz(all_dds[3][4], state_fmt=state_fmt, node_vertical_spacing=1.2, arcs_sep_angle=120, node_label_style=r"font=\normalsize", node_labels={
        KnapsackState(11, 1): "a_2",
    }).diagram(), "cutset_restricted_1_bab")
    Tikz.to_file(Tikz(all_dds[3][5], state_fmt=state_fmt, node_vertical_spacing=1.2, arcs_sep_angle=120, node_label_style=r"font=\normalsize", cutset_style=fmt.line_width(fmt.standard_line_width), show_locbs=False, show_thresholds=False, node_labels={
        KnapsackState(11, 1): "a_2",
        #KnapsackState(11, 2): "b_1",
        #KnapsackState(5, 2): "b_2",
        #KnapsackState(3, 3): "c_1",
        #KnapsackState(1, 4): "d_3",
    }).diagram(), "cutset_relaxed_1_bab")
    
    Tikz.to_file(Tikz(all_dds[4][3], state_fmt=state_fmt, show_thresholds=False, show_layer_label=True, node_labels={
        KnapsackState(15, 1): "a_1",
        KnapsackState(15, 3): "c_1",
        KnapsackState(11, 3): "c_2",
        KnapsackState(9, 3): "c_3",
        KnapsackState(7, 3): "c_4",
        KnapsackState(5, 3): "c_5",
        KnapsackState(1, 3): "c_6",
    }).diagram(), "cutset_dd_dominance")

if __name__ == "__main__":
    main() 