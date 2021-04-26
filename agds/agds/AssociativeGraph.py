import pandas as pd
import pygraphviz as pgv
from IPython.display import Image, display


class AssociativeGraph(pgv.AGraph):

    def __init__(self, data_frame, *args):
        """
        Crates Associative Graph from dataframe table
        """
        super(AssociativeGraph, self).__init__(
            strict=False, directed=False, *args)
        self.graph_attr['rankdir'] = 'LR'
        self.node_attr['shape'] = 'Mrecord'

    def associative_transformation(data_frame):
        """
        Transformates the data_frame into the AGDS
        """
        pass

    def render_graph(self):
        self.draw('tmp.png', prog='dot')
        display(Image('tmp.png'))


if __name__ == "__main__":
    data = {'id': ['O1', 'O2', 'O3', 'O4', 'O5', 'O6', 'O7', 'O8', 'O9'],
            'Sepal length': [5.4, 6.3, 6.0, 6.7, 6.0, 5.9, 6.0, 6.7, 6.5],
            'Sepal width': [3.0, 3.3, 2.7, 3.0, 2.2, 3.2, 3.0, 2.5, 3.2],
            'Petal length': [4.5, 4.7, 5.1, 5.0, 5.0, 4.8, 4.8, 5.0, 5.1],
            'Petal width': [1.5, 1.6, 1.6, 1.7, 1.5, 1.8, 1.8, 2.0, 2.0],
            'Class': ['Versicolor', 'Versicolor', 'Versicolor', 'Versicolor', "Viriginica", 'Versicolor', "Viriginica", "Viriginica", "Viriginica"]}
    input_table = pd.DataFrame(data)
    graph = AssociativeGraph(input_table)
    input_table.head()
