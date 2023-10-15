from solver import *
from csrflp import *
from tikz import *

def main():

    def state_fmt(state):
        out = []
        dist = 0.1
        for i in range(4):
            out.append(stz.circle([dist * (-1 if i % 2 == 0 else 1), dist * (1 if i // 2 == 0 else -1)], 0.08, fmt.fill_color("white" if i in state.must else "black")))
            out.append(stz.latex([dist * (-1 if i % 2 == 0 else 1), dist * (1 if i // 2 == 0 else -1)], str(i), fmt.combine_tikz_strs([fmt.text_color("black" if i in state.must else "white"), r"font=\tiny"])))
        return out
    
    instance = CsrflpInstance(
        4,
        [5, 3, 2, 6], 
        [
            [0, 8, 3, 5],
            [8, 0, 1, 4],
            [3, 1, 0, 6],
            [5, 4, 6, 0]
        ],
    )
    model = CsrflpModel(instance)

    Tikz.to_file(Tikz(Diagram(CompilationInput(model, None, Node(model.root(), value_top=model.root_value()), -math.inf, dict(), dict(), False, Settings())), state_fmt=state_fmt, show_thresholds=False, minimize=True, arc_positions={
        (CsrflpState(frozenset([1,2,3])), CsrflpState(frozenset([1,2]))): 0.3,
        (CsrflpState(frozenset([0,2,3])), CsrflpState(frozenset([2,3]))): 0.2,
        (CsrflpState(frozenset([0,2,3])), CsrflpState(frozenset([0,2]))): 0.45,
        (CsrflpState(frozenset([0,1,3])), CsrflpState(frozenset([1,3]))): 0.2,
        (CsrflpState(frozenset([0,1,3])), CsrflpState(frozenset([0,1]))): 0.2,
        (CsrflpState(frozenset([0,1,2])), CsrflpState(frozenset([1,2]))): 0.45,
        (CsrflpState(frozenset([1,2])), CsrflpState(frozenset([1]))): 0.2,
        (CsrflpState(frozenset([0,3])), CsrflpState(frozenset([0]))): 0.5,
        (CsrflpState(frozenset([0,2])), CsrflpState(frozenset([2]))): 0.45,
    }).diagram(), "exact_dd")

    dds = []
    
    instance = CsrflpInstance(
        4,
        [5, 3, 2, 6], 
        [
            [0, 8, 3, 5],
            [8, 0, 1, 4],
            [3, 1, 0, 6],
            [5, 4, 6, 0]
        ],
        [(2, 2)],
    )
    model = CsrflpModel(instance)

    dds.append(Tikz(Diagram(CompilationInput(model, None, Node(model.root(), value_top=model.root_value()), -math.inf, dict(), dict(), False, Settings())), state_fmt=state_fmt, show_thresholds=False, minimize=True, legend="(a)").diagram())
    
    instance = CsrflpInstance(
        4,
        [5, 3, 2, 6], 
        [
            [0, 8, 3, 5],
            [8, 0, 1, 4],
            [3, 1, 0, 6],
            [5, 4, 6, 0]
        ],
        [(2, 2)],
        [(0, 3)],
    )
    model = CsrflpModel(instance)

    dds.append(Tikz(Diagram(CompilationInput(model, None, Node(model.root(), value_top=model.root_value()), -math.inf, dict(), dict(), False, Settings())), state_fmt=state_fmt, show_thresholds=False, minimize=True, legend="(b)").diagram())

    Tikz.to_file(Tikz.combine(dds), "exact_dd_constr")

if __name__ == "__main__":
    main() 