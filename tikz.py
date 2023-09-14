import sane_tikz.core as stz
import sane_tikz.formatting as fmt

import math

class Tikz:
    def __init__(self, dd, show_locbs=True, show_thresholds=True, text_style=r"font=\scriptsize", opt_style=fmt.line_width(2 * fmt.standard_line_width), cutset_style=fmt.line_width(2 * fmt.standard_line_width), relaxed_style=fmt.fill_color("black!10"), ub_style=fmt.text_color("black!50"), arc_style=r"-{Straight Barb[length=3pt,width=4pt]}", node_radius=0.25, annotation_horizontal_spacing=0.25, annotation_vertical_spacing=0.2, pruning_info_vertical_spacing=0.5, node_horizontal_spacing=2, node_vertical_spacing=2, max_nodes=5, state_fmt=lambda x: x):
        self.dd = dd
        self.nodes = [dict() for _ in range(dd.input.model.nb_variables() + 1)]

        self.show_locbs = show_locbs
        self.show_thresholds = show_thresholds

        self.text_style = text_style
        self.opt_style = opt_style
        self.cutset_style = cutset_style
        self.relaxed_style = relaxed_style
        self.ub_style = ub_style
        self.arc_style = arc_style

        self.node_radius = node_radius
        self.annotation_horizontal_spacing = annotation_horizontal_spacing
        self.annotation_vertical_spacing = annotation_vertical_spacing
        self.pruning_info_vertical_spacing = pruning_info_vertical_spacing
        self.node_horizontal_spacing = node_horizontal_spacing
        self.node_vertical_spacing = node_vertical_spacing
        self.max_nodes = max_nodes

        self.state_fmt = state_fmt

    def node(self, node):
        node_elems = dict()

        # create circle with different formatting depending on flags
        style = fmt.fill_color("white")
        if node.cutset and node.depth < self.dd.input.model.nb_variables():
            style = fmt.combine_tikz_strs([style, self.cutset_style])
        if node.merged:
            node_elems["circle2"] = stz.circle([0, 0], self.node_radius * 1.15, style)
        if node.relaxed:
            style = self.relaxed_style
        node_elems["circle"] = stz.circle([0, 0], self.node_radius, style)

        # state text
        if node.depth == self.dd.input.model.nb_variables():
            node_elems["state"] = stz.latex([0, 0], "$t$", self.text_style)
        else:
            node_elems["state"] = stz.latex([0, 0], self.state_fmt(node.state), self.text_style)

        # record elements in hashmap
        self.nodes[node.depth][node.state] = node_elems

        return list(node_elems.values())
    
    def node_annotations(self, node):
        node_elems = self.nodes[node.depth][node.state]

        node_elems["value_top"] = stz.latex(
            stz.translate_coords_horizontally(node_elems["state"]["cs"], - self.annotation_horizontal_spacing),
            r"$\mathbf{" + "{value_top}".format(value_top=node.value_top) + r"}$",
            fmt.combine_tikz_strs([self.text_style, fmt.anchor("right_center")])
        )

        # add local bounds for relaxed dds
        if self.dd.relaxed and self.show_locbs:
            node_elems["value_bot"] = stz.latex(
                stz.translate_coords_horizontally(node_elems["state"]["cs"], - self.annotation_horizontal_spacing),
                "{value_bot}".format(value_bot=(r"$-\infty$" if node.value_bot == -math.inf else node.value_bot)),
                fmt.combine_tikz_strs([self.text_style, self.ub_style, fmt.anchor("right_center")])
            )
            stz.distribute_vertically_with_spacing([node_elems["value_bot"], node_elems["value_top"]], self.annotation_vertical_spacing)
            stz.align_centers_vertically([[node_elems["value_bot"], node_elems["value_top"]]], node_elems["state"]["cs"][1])

        # add thresholds for relaxed dds
        if (self.dd.relaxed or self.dd.is_exact()) and self.show_thresholds:
            node_elems["theta"] = stz.latex(
                stz.translate_coords_horizontally(node_elems["state"]["cs"], - self.annotation_horizontal_spacing),
                "{theta}".format(theta=(r"$\theta=" + (r"\infty" if node.theta == math.inf else str(node.theta)) + r"$")),
                fmt.combine_tikz_strs([self.text_style, fmt.anchor("right_center")])
            )
            e_lst = [node_elems["value_top"]]
            if "value_bot" in node_elems:
                e_lst.insert(0, node_elems["value_bot"])
            e_lst.insert(0, node_elems["theta"])
            stz.distribute_vertically_with_spacing(e_lst, self.annotation_vertical_spacing)
            stz.align_centers_vertically([e_lst], node_elems["state"]["cs"][1])

        # pruning info
        if node.deleted_by_rub or node.deleted_by_local_bounds or node.deleted_by_cache or node.deleted_by_dominance:
            bbox = stz.bbox(node_elems["circle"])
            node_elems["cross"] = [
                stz.line_segment(bbox[0], bbox[1], "densely dotted"),
                stz.line_segment([bbox[0][0], bbox[1][1]], [bbox[1][0], bbox[0][1]], "densely dotted")
            ]
            text = ""
            if node.deleted_by_rub:
                text = r"$" + \
                        r"\mathbf{" + "{value_top}".format(value_top=node.value_top) + r"} + " + \
                        r"{\color{black!50}" + "{rub}".format(rub=node.rub) + r"} \le " + \
                        "{best}".format(best=node.deleted_by_hint) + \
                        "$"
            if node.deleted_by_local_bounds:
                text = r"$" + \
                        r"\mathbf{" + "{value_top}".format(value_top=node.value_top) + r"} + " + \
                        r"{\color{black!50}" + "{value_bot}".format(value_bot=node.value_bot) + r"} \le " + \
                        "{best}".format(best=node.deleted_by_hint) + \
                        "$"
            if node.deleted_by_cache:
                text = r"$" + \
                        r"\mathbf{" + "{value_top}".format(value_top=node.value_top) + r"} \le " + \
                        "{theta}".format(theta=node.deleted_by_hint) + \
                        "$"
            if node.deleted_by_dominance:
                if self.dd.input.dominance_rule.use_value():
                    text = r"$(\mathbf{" + "{value_top}".format(value_top=node.value_top) + r"}," + \
                            "{state}".format(state=self.state_fmt(node.state)) + r") \prec " + \
                            r"(\mathbf{" + "{value_top}".format(value_top=node.deleted_by_hint.value_top) + r"}," + \
                            "{state}".format(state=self.state_fmt(node.deleted_by_hint.state)) + r") " + \
                            "$"
                else:
                    text = "${state}".format(state=self.state_fmt(node.state)) + r" \prec " + \
                            "{state}$".format(state=self.state_fmt(node.deleted_by_hint.state))

            node_elems["pruning"] = stz.latex(
                stz.translate_coords_vertically(node_elems["state"]["cs"], - self.pruning_info_vertical_spacing),
                text,
                fmt.combine_tikz_strs([r"font=\tiny", "draw", "inner sep=1pt", fmt.fill_color("white")])
            )

        return list(node_elems.values())
    
    def node_arcs(self, node):
        to_elems = self.nodes[node.depth][node.state]
        to_circle = to_elems["circle2"] if "circle2" in to_elems else to_elems["circle"]

        # group arcs by parent to hande multi-arcs
        arcs_by_parent = dict()
        for arc in node.arcs:
            if arc.parent.state not in arcs_by_parent:
                arcs_by_parent[arc.parent.state] = []
            arcs_by_parent[arc.parent.state].append(arc)

        e_lst = []
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
            delta = 75 * math.pow(math.sin(stz.degrees_to_radians(out_angle)), 2) / len(arcs)
            alpha = - (out_angle - 270) * math.fabs(math.cos(stz.degrees_to_radians(out_angle))) * 0.2 #- (out_angle - 270) * 0.1
            alpha -= delta * (len(arcs) - 1) / 2

            for arc in sorted(arcs, key=lambda x: x.decision):
                out_angle = stz.normalize_angle_to_standard_interval(stz.vector_to_angle([from_cs, to_cs]) + alpha)
                in_angle = stz.normalize_angle_to_standard_interval(out_angle + 180.0 - alpha)

                from_cs_bezier = stz.coords_on_circle(from_cs, from_circle["radius"], out_angle)
                to_cs_bezier = stz.coords_on_circle(to_cs, to_circle["radius"], in_angle)

                decoration = r"postaction={decorate, decoration={" \
                    + r"markings, mark=at position .35 with { \node[" \
                    + fmt.combine_tikz_strs([self.text_style, "circle", fmt.fill_color("white"), "inner sep=0.5pt"]) \
                    + r"]{" \
                    + str(arc.reward) \
                    + r"}; }}}"

                line_style = [self.arc_style, decoration]
                if arc.opt:
                    line_style.append(self.opt_style)
                e_lst.append(stz.bezier_with_symmetric_relative_angle_midway_controls(
                    from_cs_bezier, to_cs_bezier, alpha, 
                    fmt.combine_tikz_strs(list(reversed(line_style)))
                ))

                alpha += delta

        return e_lst

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

        return e_lst
    
    def layer_annotations(self, layer):
        # add annotations once nodes they are correctly placed
        e_lst = []
        for node in self.get_layer_nodes(layer):
            e_lst.append(self.node_annotations(node))

        return e_lst
    
    def layer_arcs(self, layer):
        # add annotations once nodes they are correctly placed
        e_lst = []
        for node in self.get_layer_nodes(layer):
            arcs = self.node_arcs(node)
            if len(arcs) > 0:
                e_lst.append(arcs)

        return e_lst
    
    def get_layer_nodes(self, layer):
        # get all nodes, even the pruned ones
        groups = [list(layer.nodes.values()), layer.deleted_by_dominance, layer.deleted_by_cache, layer.deleted_by_rub, layer.deleted_by_local_bounds]
        return [node for group in groups for node in group]

    def convert(self, name):
        e_lst = []

        # create nodes of each layer
        for layer in self.dd.layers:
            nodes = self.layer(layer)
            if len(nodes) > 0:
                e_lst.insert(0, nodes)
        
        # align layers horizontally
        stz.distribute_centers_vertically_with_spacing(e_lst, self.node_vertical_spacing)
        stz.align_centers_horizontally(e_lst, 0)

        # add arcs once nodes are correctly placed
        for layer in self.dd.layers:
            arcs = self.layer_arcs(layer)
            if len(arcs) > 0:
                e_lst.append(arcs)

        # add node annotations
        for layer in self.dd.layers:
            annotations = self.layer_annotations(layer)
            if len(annotations) > 0:
                e_lst.append(annotations)

        # create tex file
        file =  "out/{}.tex".format(name)
        stz.draw_to_tikz_standalone(e_lst, file)

        # add needed tikzlibrary
        match_str = r"\usetikzlibrary{arrows.meta}"
        insert_str = r"\usetikzlibrary{decorations.markings}" + "\n"
        with open(file, 'r+') as fd:
            contents = fd.readlines()
            if match_str in contents[-1]:
                contents.append(insert_str)
            else:
                for index, line in enumerate(contents):
                    if match_str in line:
                        contents.insert(index + 1, insert_str)
                        break
            fd.seek(0)
            fd.writelines(contents)