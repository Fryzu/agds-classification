import pandas as pd
import pygraphviz as pgv
from IPython.display import Image, display
from .utils import previous_current_next
from functools import reduce
import statusbar
import tqdm


class AssociativeGraph(pgv.AGraph):

    # Used in order to tell apart attributes from other nodes,
    # id:class dict
    _attributes = dict()
    # class:max_value dict
    _max_values = dict()
    # class:min_value dict
    _min_values = dict()

    @classmethod
    def get_hash(cls, attribute_name, attribute_value):
        return hash("{attribute_name}_{attribute_value}".format(attribute_value=attribute_value, attribute_name=attribute_name))

    def __init__(self, data_frame, primary_key="id", *args):
        """
        Crates Associative Graph from dataframe table
        """
        super(AssociativeGraph, self).__init__(
            strict=False, directed=False, spline="curved", * args)
        self.graph_attr['rankdir'] = 'LR'
        self.node_attr['shape'] = 'Mrecord'
        self.associative_transformation(data_frame, primary_key)

    def associative_transformation(self, data_frame, pk):
        """
        Transformates the data_frame into the AGDS
        """
        column_names = [x for x in data_frame.columns if x != "id"]

        self.add_node("param")
        for column in column_names:
            self.add_node(column)
            self.add_edge("param", column)

        for column_name in column_names:
            column = list(data_frame[column_name])
            column.sort()

            self._max_values[column_name] = column[-1]
            self._min_values[column_name] = column[0]

            for prev_item, attribute, next_item in previous_current_next(column):
                prev_id = AssociativeGraph.get_hash(column_name, prev_item)
                node_id = AssociativeGraph.get_hash(column_name, attribute)
                next_id = AssociativeGraph.get_hash(column_name, next_item)

                self._attributes[str(node_id)] = column_name

                self.add_node(node_id, label=attribute)
                if not self.has_edge(column_name, node_id):
                    self.add_edge(column_name, node_id)
                if prev_item and not self.has_edge(prev_id, node_id) and prev_item != attribute:
                    weight = 2
                    self.add_edge(prev_id, node_id,
                                  weight=weight, constraint=False)
                if next_item and not self.has_edge(node_id, next_id) and next_item != attribute:
                    weight = 2
                    self.add_edge(node_id, next_id,
                                  weight=weight, constraint=False)

        rows = data_frame.to_dict(orient='records')

        for row in rows:
            entity_id = row["id"]
            self.add_node(entity_id)
            for column_name, attribute in row.items():
                if column_name != "id":
                    node_id = AssociativeGraph.get_hash(column_name, attribute)
                    self.add_edge(node_id, entity_id)

    def render_graph(self):
        self.draw('tmp.png', prog='dot')
        display(Image('tmp.png'))

    def get_attribute_weight(self, node_a, node_b):
        try:
            class_name = self._attributes[node_a]
            v_a_max = float(self._max_values[class_name])
            v_a_min = float(self._min_values[class_name])
            r = v_a_max - v_a_min
            v_a = float(self.get_node(node_a).attr["label"])
            v_b = float(self.get_node(node_b).attr["label"])
            weight = 1 - abs(v_a-v_b)/r
            return weight
        except:
            return 0.5

    def get_weight(self, node_a, node_b):
        if (node_a in self._attributes and node_b in self._attributes):
            return self.get_attribute_weight(node_a, node_b)
        else:
            neighbors = len(self.neighbors(node_b))
            return 1/neighbors

    def inference(self, strat_node):
        """
        Returns inference starting from node with id start_node
        """
        weights_dict = dict()
        weights_dict[strat_node] = 1
        bfs_queue = [strat_node]

        while bfs_queue:
            current_node = bfs_queue.pop()
            neighbors = [i for i in self.neighbors(
                current_node) if i not in weights_dict]
            for node in neighbors:
                bfs_queue.insert(0, node)
                weights_dict[node] = weights_dict[current_node] * \
                    self.get_weight(current_node, node)

        parsed_dict = dict()
        for k, v in weights_dict.items():
            if k in self._attributes:
                key = "{}:{}".format(
                    self._attributes[k], self.get_node(k).attr["label"])
                parsed_dict[key] = v
            else:
                parsed_dict[k] = v

        return parsed_dict

    def classify(self, input_nodes):
        """
        input_nodes is a dictionary of classified params {param: value}
        """
        node_keys = [self.get_hash(k, v) for k, v in input_nodes.items()]

        node_inferences = []

        for node in tqdm.tqdm(node_keys):
            node_inferences.append(self.inference(node))

        def sum_up(dict1, dict2):
            keys = set(list(dict1.keys()) + list(dict2.keys()))
            result = dict()
            for key in keys:
                if key in dict1 and key in dict2:
                    result[key] = dict1[key] + dict2[key]
                elif key in dict1:
                    result[key] = dict1[key]
                else:
                    result[key] = dict2[key]

            return result

        result = reduce(sum_up, node_inferences, dict())

        return {k: v for k, v in sorted(result.items(), key=lambda item: item[1])}


if __name__ == "__main__":
    data = {'id': ['O1', 'O2', 'O3', 'O4', 'O5', 'O6', 'O7', 'O8', 'O9'],
            'Sepal length': [5.4, 6.3, 6.0, 6.7, 6.0, 5.9, 6.0, 6.7, 6.5],
            'Sepal width': [3.0, 3.3, 2.7, 3.0, 2.2, 3.2, 3.0, 2.5, 3.2],
            'Petal length': [4.5, 4.7, 5.1, 5.0, 5.0, 4.8, 4.8, 5.0, 5.1],
            'Petal width': [1.5, 1.6, 1.6, 1.7, 1.5, 1.8, 1.8, 2.0, 2.0],
            'Class': ['Versicolor', 'Versicolor', 'Versicolor', 'Versicolor', "Viriginica", 'Versicolor', "Viriginica", "Viriginica", "Viriginica"]}
    data_frame = pd.DataFrame(data)
    graph = AssociativeGraph(data_frame)
    data_frame.head()
