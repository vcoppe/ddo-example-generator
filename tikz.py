from dd import Layer
from knapsack import CompilationMode
import sane_tikz.core as stz
import sane_tikz.formatting as fmt

import math

class Label:
    def __init__(self, content, position="right"):
        self.content = content
        self.position = position

class Tikz:
    def __init__(self, dd, show_locbs=True, show_thresholds=True, text_style="", opt_style=fmt.line_width(4 * fmt.standard_line_width), node_style=fmt.combine_tikz_strs([fmt.fill_color("nodecolor"), "draw=none", fmt.text_color("white")]), cutset_style=fmt.line_width(1.5 * fmt.standard_line_width), relaxed_style=fmt.combine_tikz_strs([fmt.fill_color("FireBrick"), "draw=none"]), ub_style=fmt.text_color("black!50"), arc_style=r"", node_radius=0.3, annotation_horizontal_spacing=0.2, annotation_vertical_spacing=0.25, pruning_info_vertical_spacing=0.5, node_horizontal_spacing=1.8, node_vertical_spacing=1.5, max_nodes=5, state_fmt=lambda x: x, node_labels=dict(), node_label_style=r"font=\large", legend=None, arcs_sep_angle=75, arc_positions=dict(), show_layer_label=False, show_variable_label=False, show_empty_layer=True, show_prev_layer=True, theta=r"\theta", theta_color="DarkTurquoise", value_unit=r"", max_layer=math.inf, show_deleted=False, show_merged=True, show_cross=True):
        self.dd = dd
        self.nodes = [dict() for _ in range(dd.input.model.nb_variables() + 1)]
        self.others = []

        self.theta = theta

        self.show_merged = show_merged
        self.show_deleted = show_deleted
        self.show_cross = show_cross
        self.show_locbs = show_locbs
        self.show_thresholds = show_thresholds
        self.show_layer_label = show_layer_label
        self.show_variable_label = show_variable_label
        self.show_empty_layer = show_empty_layer
        self.show_prev_layer = show_prev_layer

        self.max_layer = max_layer

        self.text_style = text_style
        self.opt_style = opt_style
        self.node_style = node_style
        self.cutset_style = cutset_style
        self.relaxed_style = relaxed_style
        self.ub_style = ub_style
        self.arc_style = arc_style
        self.node_label_style = node_label_style
        self.value_unit = value_unit

        self.theta_color = theta_color

        self.node_radius = node_radius
        self.annotation_horizontal_spacing = annotation_horizontal_spacing
        self.annotation_vertical_spacing = annotation_vertical_spacing
        self.pruning_info_vertical_spacing = pruning_info_vertical_spacing
        self.node_horizontal_spacing = node_horizontal_spacing
        self.node_vertical_spacing = node_vertical_spacing
        self.max_nodes = max_nodes
        self.arcs_sep_angle = arcs_sep_angle

        self.state_fmt = state_fmt

        self.node_labels = node_labels
        self.arc_positions = arc_positions
        self.legend = legend

    def node(self, node):
        node_elems = dict()

        # create circle with different formatting depending on flags
        style = self.node_style
        if node.cutset and node.depth < self.dd.input.model.nb_variables():
            style = fmt.combine_tikz_strs([style, self.cutset_style])
        if node.relaxed:
            style = self.relaxed_style
        node_elems["circle"] = stz.circle([0, 0], self.node_radius, style)

        # state text
        node_elems["state"] = stz.latex([0, 0], self.state_fmt(node.state), fmt.combine_tikz_strs([self.text_style, self.node_style, "fill=none"]))
        if node.depth == self.dd.input.model.nb_variables() and self.dd.input.model.mode == CompilationMode.DD:
            node_elems["goal"] = stz.circle([0, 0], self.node_radius, "draw=none,pattern=mypattern, pattern color=white")

        # record elements in hashmap
        self.nodes[node.depth][node.state] = node_elems

        return list(node_elems.values())
    
    def node_annotations(self, node):
        node_elems = self.nodes[node.depth][node.state]

        if node.depth == self.dd.input.model.nb_variables() and self.dd.input.model.mode == CompilationMode.TREE:
            node_elems["value_top"] = stz.latex(
                stz.translate_coords_vertically(node_elems["state"]["cs"], - self.annotation_vertical_spacing),
                "{value_top}".format(value_top=node.value_top) + self.value_unit,
                fmt.combine_tikz_strs([self.text_style, fmt.anchor("top_center")])
            )
        else:
            node_elems["value_top"] = stz.latex(
                stz.translate_coords_horizontally(node_elems["state"]["cs"], - self.annotation_horizontal_spacing),
                "{value_top}".format(value_top=node.value_top) + self.value_unit,
                fmt.combine_tikz_strs([self.text_style, fmt.anchor("right_center")])
            )

        # add local bounds for relaxed dds
        if self.dd.relaxed and self.show_locbs and self.dd.input.settings.use_locb:
            node_elems["value_bot"] = stz.latex(
                stz.translate_coords_horizontally(node_elems["state"]["cs"], - self.annotation_horizontal_spacing),
                "{value_bot}".format(value_bot=(r"$-\infty$" if node.value_bot == -math.inf else node.value_bot)),
                fmt.combine_tikz_strs([self.text_style, self.ub_style, fmt.anchor("right_center")])
            )
            stz.distribute_vertically_with_spacing([node_elems["value_bot"], node_elems["value_top"]], self.annotation_vertical_spacing)
            stz.align_centers_vertically([[node_elems["value_bot"], node_elems["value_top"]]], node_elems["state"]["cs"][1])

        # add thresholds for relaxed dds
        if (self.dd.relaxed or self.dd.is_exact()) and self.show_thresholds and \
            (not node.relaxed or node.theta < math.inf):
            node_elems["theta"] = stz.latex(
                stz.translate_coords_horizontally(node_elems["state"]["cs"], - self.annotation_horizontal_spacing),
                "{theta}".format(theta=(r"{\color{" + self.theta_color + "}" + (r"∞" if node.theta == math.inf else str(node.theta)) + r"}")),
                fmt.combine_tikz_strs([self.text_style, fmt.anchor("right_center")])
            )
            e_lst = [node_elems["value_top"]]
            if "value_bot" in node_elems:
                e_lst.insert(0, node_elems["value_bot"])
            e_lst.insert(0, node_elems["theta"])
            stz.distribute_vertically_with_spacing(e_lst, self.annotation_vertical_spacing)
            stz.align_centers_vertically([e_lst], node_elems["state"]["cs"][1])

        # pruning info
        if node.deleted_by_rub or node.deleted_by_local_bounds or node.deleted_by_cache or node.deleted_by_dominance or (node.deleted_by_shrink and self.show_cross):
            bbox = stz.bbox(node_elems["circle"])
            node_elems["cross1"] = stz.line_segment(bbox[0], bbox[1], fmt.combine_tikz_strs(["dash pattern=on 2pt off 1pt", fmt.line_width(4 * fmt.standard_line_width), fmt.line_color("Gold")]))
            node_elems["cross2"] = stz.line_segment([bbox[0][0], bbox[1][1]], [bbox[1][0], bbox[0][1]], fmt.combine_tikz_strs(["dash pattern=on 2pt off 1pt", fmt.line_width(4 * fmt.standard_line_width), fmt.line_color("Gold")]))

            text = ""
            if node.deleted_by_rub:
                text = "{value_top}".format(value_top=node.value_top) + r" + " + \
                        r"{\color{black!50}" + "{rub}".format(rub=node.rub) + r"} ≤ " + \
                        "{best}".format(best=node.deleted_by_hint)
            if node.deleted_by_local_bounds:
                text = "{value_top}".format(value_top=node.value_top) + r" + " + \
                        r"{\color{black!50}" + "{value_bot}".format(value_bot=node.value_bot) + r"} ≤ " + \
                        "{best}".format(best=node.deleted_by_hint)
            if node.deleted_by_cache:
                text = "{value_top}".format(value_top=node.value_top) + r" ≤ " + \
                        "{theta}".format(theta=node.deleted_by_hint)
            if node.deleted_by_dominance:
                if self.dd.input.dominance_rule.use_value():
                    text = "(" + "{value_top}".format(value_top=node.value_top) + self.value_unit + r"," + \
                            "{state}".format(state=self.state_fmt(node.state)) + r") ≤ " + \
                            "(" + "{value_top}".format(value_top=node.deleted_by_hint.value_top) + self.value_unit + r"," + \
                            "{state}".format(state=self.state_fmt(node.deleted_by_hint.state)) + r")"
                else:
                    text = "{state}".format(state=self.state_fmt(node.state)) + r" ≤ " + \
                            "{state}".format(state=self.state_fmt(node.deleted_by_hint.state))
                    
            if len(text) > 0:
                node_elems["pruning"] = stz.latex(
                    stz.translate_coords_vertically(node_elems["state"]["cs"], - self.pruning_info_vertical_spacing),
                    text,
                    fmt.combine_tikz_strs([r"font=\scriptsize", "draw", "inner sep=1pt", fmt.fill_color("white")])
                )
        
        if node.state in self.node_labels:
            bbox = stz.bbox(list(filter(lambda e: e["type"] == "latex", node_elems.values())))
            label = self.node_labels[node.state]
            if isinstance(label, str):
                label = Label(label)
            if label.position == "right":
                node_elems["label"] = stz.latex(
                    stz.translate_coords_horizontally([bbox[1][0], node_elems["state"]["cs"][1]], self.annotation_horizontal_spacing),
                    r"$" + "{label}".format(label=label.content) + r"$",
                    fmt.combine_tikz_strs([self.node_label_style, fmt.anchor("left_center")])
                )
            elif label.position == "left":
                node_elems["label"] = stz.latex(
                    stz.translate_coords_horizontally([bbox[0][0], node_elems["state"]["cs"][1]], - self.annotation_horizontal_spacing),
                    r"$" + "{label}".format(label=label.content) + r"$",
                    fmt.combine_tikz_strs([self.node_label_style, fmt.anchor("right_center")])
                )
            elif label.position == "top":
                node_elems["label"] = stz.latex(
                    stz.translate_coords_vertically([node_elems["state"]["cs"][0], bbox[0][1]], self.annotation_horizontal_spacing),
                    r"$" + "{label}".format(label=label.content) + r"$",
                    fmt.combine_tikz_strs([self.node_label_style, fmt.anchor("bottom_center")])
                )
            elif label.position == "bottom":
                node_elems["label"] = stz.latex(
                    stz.translate_coords_vertically([node_elems["state"]["cs"][0], bbox[1][1]], - self.annotation_horizontal_spacing),
                    r"$" + "{label}".format(label=label.content) + r"$",
                    fmt.combine_tikz_strs([self.node_label_style, fmt.anchor("top_center")])
                )
    
    def node_arcs(self, node):
        to_elems = self.nodes[node.depth][node.state]
        to_circle = to_elems["circle2"] if "circle2" in to_elems else to_elems["circle"]

        # group arcs by parent to hande multi-arcs
        arcs_by_parent = dict()
        for arc in node.arcs:
            if arc.parent.state not in arcs_by_parent:
                arcs_by_parent[arc.parent.state] = []
            arcs_by_parent[arc.parent.state].append(arc)

        cnt = 0
        for arcs in arcs_by_parent.values():
            parent = arcs[0].parent

            from_elems = self.nodes[parent.depth][parent.state]
            from_circle = from_elems["circle2"] if "circle2" in from_elems else from_elems["circle"]

            from_cs = stz.center_coords(from_circle)
            to_cs = stz.center_coords(to_circle)

            out_angle = stz.normalize_angle_to_standard_interval(stz.vector_to_angle([from_cs, to_cs]))
            in_angle = stz.normalize_angle_to_standard_interval(out_angle + 180.0)

            alpha = 0
            delta = 0

            #if len(arcs) > 1:
            delta = self.arcs_sep_angle * math.pow(math.sin(stz.degrees_to_radians(out_angle)), 2) / len(arcs)
            alpha = - (out_angle - 270) * math.fabs(math.cos(stz.degrees_to_radians(out_angle))) * 0.2 #- (out_angle - 270) * 0.1
            alpha -= delta * (len(arcs) - 1) / 2

            for arc in sorted(arcs, key=lambda x: x.decision):
                out_angle = stz.normalize_angle_to_standard_interval(stz.vector_to_angle([from_cs, to_cs]) + alpha)
                in_angle = stz.normalize_angle_to_standard_interval(out_angle + 180.0 - alpha)

                from_cs_bezier = stz.coords_on_circle(from_cs, from_circle["radius"], out_angle)
                to_cs_bezier = stz.coords_on_circle(to_cs, to_circle["radius"], in_angle)

                position = .35
                if (parent.state, node.state) in self.arc_positions:
                    position = self.arc_positions[(parent.state, node.state)]

                decoration = r"postaction={decorate, decoration={" \
                    + r"markings, mark=at position " + str(position) + r" with { \node[" \
                    + fmt.combine_tikz_strs([r"font=\scriptsize", "circle", fmt.fill_color("white"), "inner sep=0.5pt"]) \
                    + r"]{" \
                    + str(arc.reward) \
                    + r"}; }}}"

                line_style = [self.arc_style, decoration]
                if arc.opt and self.max_layer + 1 >= len(self.dd.layers):
                    line_style.append(self.opt_style)
                to_elems["arcs" + str(cnt)] = stz.bezier_with_symmetric_relative_angle_midway_controls(
                    from_cs_bezier, to_cs_bezier, alpha, 
                    fmt.combine_tikz_strs(list(reversed(line_style)))
                )

                alpha += delta
                cnt += 1

    def layer(self, layer):
        nodes = self.get_layer_nodes(layer)

        # order nodes according to state comparison
        nodes.sort(key=lambda node: node.state)

        # create tikz nodes
        e_lst = []
        for node in nodes:
            e_lst.append(self.node(node))
        
        # distribute nodes horizontally (adapt spacing when more than self.max_nodes)
        spacing = self.node_horizontal_spacing
        if len(e_lst) > self.max_nodes:
            spacing = (self.max_nodes - 1) * self.node_horizontal_spacing / (len(e_lst) - 1)
        stz.distribute_centers_horizontally_with_spacing(e_lst, spacing)

        if len(e_lst) == 0 and self.show_empty_layer:
            dummy_node = stz.circle([0, 0], self.node_radius, fmt.line_color("white"))
            self.others.append(dummy_node)
            e_lst.append(dummy_node)
        
        bbox = stz.bbox(e_lst)
        if len(e_lst) < 10:
            rectangle = stz.rectangle(stz.translate_coords_horizontally(bbox[0], -2*self.annotation_horizontal_spacing), stz.translate_coords_horizontally(bbox[1], 2*self.annotation_horizontal_spacing), "opacity=0")
        else:
            rectangle = stz.rectangle(stz.translate_coords_horizontally(bbox[0], -1.7*self.annotation_horizontal_spacing), stz.translate_coords_horizontally(bbox[1], 1.7*self.annotation_horizontal_spacing), "opacity=0")
        self.others.append(rectangle)
        e_lst.append(rectangle)

        return e_lst
    
    def layer_annotations(self, layer):
        # add annotations once nodes they are correctly placed
        for node in self.get_layer_nodes(layer):
            self.node_annotations(node)
    
    def layer_arcs(self, layer):
        # add annotations once nodes they are correctly placed
        for node in self.get_layer_nodes(layer):
            self.node_arcs(node)
    
    def get_layer_nodes(self, layer):
        # get all nodes, even the pruned ones
        groups = [list(layer.nodes.values()), layer.deleted_by_dominance, layer.deleted_by_cache, layer.deleted_by_rub, layer.deleted_by_local_bounds]
        if self.show_deleted and self.max_layer == layer.depth and layer.depth < self.dd.input.model.nb_variables():
            groups.append(layer.deleted_by_shrink)
        if self.max_layer == layer.depth and not self.show_merged:
            groups[0] = list(filter(lambda n: False if n.merged else True, groups[0]))
        return [node for group in groups for node in group]
    
    def layers(self):
        e_lst = []

        # create nodes of each layer
        if self.show_prev_layer:
            for i in range(self.dd.layers[0].depth):
                nodes = self.layer(Layer(self.dd.input, i))
                if len(nodes) > 0:
                    e_lst.insert(0, nodes)
        for i, layer in enumerate(self.dd.layers):
            if i > self.max_layer:
                break
            nodes = self.layer(layer)
            if len(nodes) > 0:
                e_lst.insert(0, nodes)
        
        # align layers horizontally
        stz.distribute_centers_vertically_with_spacing(e_lst, self.node_vertical_spacing)
        stz.align_centers_horizontally(e_lst, 0)
    
    def layer_and_variable_labels(self):
        bbox = stz.bbox(self.get_e_lst())
        if self.show_layer_label:
            for l in range(len(self.dd.layers)):
                if l > self.max_layer:
                    break
                self.others.append(stz.latex([bbox[1][0] + self.node_horizontal_spacing / 2, (len(self.dd.layers) - 1 - l) * self.node_vertical_spacing], r"$L_" + str(self.dd.layers[l].depth) + r"$", self.text_style))
        
        if self.show_variable_label:
            for l in range(len(self.dd.layers) - 1):
                if l == self.max_layer:
                    break
                self.others.append(stz.latex([bbox[1][0] + self.node_horizontal_spacing / 2, (len(self.dd.layers) - 1.5 - l) * self.node_vertical_spacing], r"$x_" + str(self.dd.layers[l].depth) + r"$", self.text_style))


    def bottom_legend(self):
        if self.legend is not None:
            l = stz.latex([0, 0], self.legend)
            stz.place_below_and_align_to_the_center(l, self.get_e_lst(), self.node_vertical_spacing / 3)
            self.others.append(l)

    def get_e_lst(self):
        e_lst = [e for layer in self.nodes for node_elems in layer.values() for e in node_elems.values()]
        e_lst.extend(self.others)
        e_lst.sort(key=lambda e: e["type"])
        return e_lst

    def diagram(self):
        # create all layers and distribute them correcly
        self.layers()

        # add arcs once nodes are correctly placed
        for i, layer in enumerate(self.dd.layers):
            if i > self.max_layer:
                break
            self.layer_arcs(layer)

        # add node annotations
        for i, layer in enumerate(self.dd.layers):
            if i > self.max_layer:
                break
            self.layer_annotations(layer)

        # add legend
        self.bottom_legend()
        
        # add layer/variable labels
        self.layer_and_variable_labels()

        return self.get_e_lst()
    
    def combine(e_lst, spacing=1.5):
        stz.distribute_horizontally_with_spacing(e_lst, spacing)
        return e_lst

    def to_file(e_lst, name):
        # create tex file
        file =  "out/{}.tex".format(name)
        stz.draw_to_tikz_standalone(e_lst, file)

        # add needed tikzlibrary
        match_str = [r"\usepackage{tikz}", r"\usetikzlibrary{arrows.meta}", r"\begin{tikzpicture}", r"\end{tikzpicture}"]
        insert_str = [r"\usepackage[paperwidth=128ex, paperheight=72ex, bottom=0ex, right=0ex, left=0ex, top=12ex]{geometry}\usepackage[usenames, svgnames]{xcolor}\pagenumbering{gobble}", r"""
\usetikzlibrary{patterns}
\usetikzlibrary{decorations.markings}
\usepackage{fontspec}
\setmainfont{PinkChicken}[Path=/Users/vcoppe/Downloads/,Extension=.ttf]
\pgfdeclarepatternformonly[\size]{mypattern}
{\pgfpoint{ -\size}{-\size}}
{\pgfpoint{  \size}{ \size}}
{\pgfpoint{2*\size}{2*\size}}
{
  \pgfpathrectangle{\pgfpoint{-\size}{-\size}}{\pgfpoint{\size}{\size}}
  \pgfpathrectangle{\pgfpoint{0}{0}}{\pgfpoint{\size}{\size}}
  \pgfusepath{fill}
}
\definecolor{nodecolor}{RGB}{7,77,125}
\tikzset{
  size/.store in=\size, size=3pt,
}""", r"\begin{center}", r"\end{center}"]
        before = [True, False, True, False]
        with open(file, 'r+') as fd:
            contents = fd.readlines()
            contents[0] = "\documentclass[crop=false]{standalone}"
            for i in range(len(match_str)):
                for index, line in enumerate(contents):
                    if match_str[i] in line:
                        if before[i]:
                            contents.insert(index, insert_str[i])
                        else:
                            contents.insert(index + 1, insert_str[i])
                        break
            fd.seek(0)
            fd.writelines(contents)