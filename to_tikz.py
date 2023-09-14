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
        solver.solve(setting)

        all_dds.append(solver.dds)
        
    Tikz(all_dds[0][0], state_fmt=state_fmt).convert("root_restricted")
    Tikz(all_dds[0][1], state_fmt=state_fmt, show_thresholds=False).convert("root_relaxed")

    Tikz(all_dds[0][2], state_fmt=state_fmt).convert("cutset_relaxed_1")
    Tikz(all_dds[0][3], state_fmt=state_fmt).convert("cutset_relaxed_2")

    Tikz(all_dds[1][2], state_fmt=state_fmt).convert("cutset_relaxed_1_pruning")
    Tikz(all_dds[1][3], state_fmt=state_fmt).convert("cutset_relaxed_2_pruning")

    Tikz(all_dds[2][2], state_fmt=state_fmt).convert("cutset_relaxed_1_dominance")
    Tikz(all_dds[2][3], state_fmt=state_fmt).convert("cutset_relaxed_2_dominance")

if __name__ == "__main__":
    main() 