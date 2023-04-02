import os
import importlib.util
import imp
import inspect
from collections import deque

import typing
from typing_extensions import final
import yaml
from yamlinclude import YamlIncludeConstructor
import numpy as np

from yeagerai.core.abstract_component import AbstractComponent
from yeagerai.core.abstract_context import AbstractContext


class AbstractWorkflow(AbstractComponent):
    @classmethod
    @final
    def workflow_exc_flow_path(cls) -> str:
        return os.path.join(cls.module_path(), "exec_flow.yml")

    @classmethod
    @final
    def check_exc_flow_path(cls) -> None:
        if not os.path.isfile(cls.workflow_exc_flow_path()):
            raise FileNotFoundError(
                "exc_flow.yml not found on ",
                cls.component_dockerfile_path(),
            )

    @classmethod
    @final
    def components_folder_path(cls) -> str:
        return os.path.join(cls.module_path(), "components/")

    @classmethod
    @final
    def check_components_folder_path(cls) -> None:
        if not os.path.isfile(cls.components_folder_path()):
            raise FileNotFoundError(
                "components/ not found on ",
                cls.components_folder_path(),
            )

    @classmethod
    @final
    def check_components_folder_contains_components(cls) -> None:
        components_path = cls.components_folder_path()
        for file in os.listdir(components_path):
            if os.path.isdir(os.path.join(components_path, file)):
                module = importlib.import_module(file)
                classes = inspect.getmembers(module, inspect.isclass)
                for _, component_class in classes:
                    if issubclass(component_class, AbstractComponent):
                        component_class.test_cls()

    @classmethod
    def test_workflow_cls(cls) -> None:
        cls.test_cls()
        cls.check_exc_flow_path()
        cls.check_components_folder_path()
        cls.check_components_folder_contains_components()

    async def execute(self, args: typing.Any, context: AbstractContext) -> typing.Any:
        """
        It loads the exc-flow.yml which is a configuration of every workflow, and
        executes the flow in the order of the adjacency matrix, transforming the data and
        sending it to the next nodes
        """

        print(f"Executing the {type(self).__name__} workflow...")

        exc_flow = self._load_exc_flow()
        adj_list = self._build_adj_list(exc_flow)
        sorted_nodes = self._topological_sort(adj_list)

        results_dict: dict = {}
        for node_idx in sorted_nodes:
            node_data = self._get_node_data(exc_flow, node_idx)
            input_dict = self._build_input_dict(
                args, exc_flow, node_idx, node_data, results_dict
            )
            component_instance = self._create_component_instance(
                exc_flow, node_data, node_idx
            )
            output_dict = await component_instance.execute(input_dict, context)
            results_dict[node_idx] = output_dict

        print(f"The workflow {type(self).__name__} has finished its execution !")
        return results_dict

    def _load_exc_flow(self) -> dict:
        """
        Load the exc_flow.yml configuration file and return its contents as a dictionary.
        """
        YamlIncludeConstructor.add_to_loader_class(
            loader_class=yaml.FullLoader,
            base_dir=self.module_path(),
        )
        with open(
            self.workflow_exc_flow_path(), "r", encoding="utf-8"
        ) as exc_flow_file:
            return yaml.load(exc_flow_file, Loader=yaml.FullLoader)

    def _build_adj_list(self, yaml_data: dict) -> dict:
        """
        Build an adjacency list representation of the workflow's dependency graph, given the
        workflow configuration YAML data as a dictionary.

        Returns:
        - adj_list (dict): The adjacency list representation of the workflow's dependency graph,
                           where each key represents a node ID and the corresponding value is a list
                           of its immediate children node IDs.
        """
        adj_matrix = np.array(yaml_data["flow-matrix"])
        adj_list: dict = {i: [] for i in range(len(yaml_data["components"]))}
        for from_idx, row in enumerate(adj_matrix):
            adj_list[from_idx] = list(np.where(row > 0)[0])
        return adj_list

    def _topological_sort(self, adj_list: dict) -> list:
        """
        Perform topological sort on the given adjacency list, which represents a
        directed acyclic graph (DAG).
        """
        sorted_nodes = []
        incoming_edge_count = {node: 0 for node in adj_list}
        for edges in adj_list.values():
            for node in edges:
                incoming_edge_count[node] += 1
        no_incoming_edges = deque(
            node for node in incoming_edge_count if incoming_edge_count[node] == 0
        )
        while no_incoming_edges:
            node = no_incoming_edges.popleft()
            sorted_nodes.append(node)
            for neighbor in adj_list.get(node, []):
                incoming_edge_count[neighbor] -= 1
                if incoming_edge_count[neighbor] == 0:
                    no_incoming_edges.append(neighbor)
        if len(sorted_nodes) != len(adj_list):
            cycle_nodes = set(adj_list.keys()) - set(sorted_nodes)
            raise ValueError(f"The graph contains at least one cycle: {cycle_nodes}")
        return sorted_nodes

    def _get_node_data(self, yaml_data: dict, node_idx: int) -> dict:
        """
        Retrieve the node data (i.e., name, class, parameters, etc.) for the node
        with the given index in the workflow adjacency matrix.
        """
        for node_info in yaml_data["components"]:
            if int(node_info.split("-")[1]) == node_idx:
                return yaml_data["components"][node_info]
        raise ValueError(f"Node with ID '{node_idx}' not found")

    def _build_input_dict(
        self,
        args: typing.Any,
        yaml_data: dict,
        node_idx: int,
        node_data: dict,
        results_dict: dict,
    ) -> typing.Any:
        """
        Build the input dictionary for the component with the given node data, based on
        the results of the components that are incoming edges of the node.
        """

        mapper = yaml_data.get("mapper", {})
        incoming_edges = [
            (k, v) for k, v in mapper.items() if k.split(".")[0] == f"node-{node_idx}"
        ]

        # Specify the full path and name of the module
        module_path = os.path.join(
            self.module_path(),
            yaml_data["components"][f"node-{node_idx}"]["module-path"],
        )
        module_name = (
            yaml_data["components"][f"node-{node_idx}"]["module-path"]
            .split("/")[-1]
            .split(".")[0]
        )

        # Load the module from the specified path
        node_module = imp.load_source(module_name, module_path)

        # Load and instantiate the input class
        input_dict_cls = getattr(node_module, node_data["configuration"]["input-class"])

        # Replace the types with instances of the given data_type
        def create_instance(data_type: typing.Any) -> typing.Any:
            if type(None) in typing.get_args(data_type):
                return None
            return data_type()

        def replace_types_with_instances(cls_annotations: dict) -> dict:
            return {
                key: create_instance(value) for key, value in cls_annotations.items()
            }

        annotations_with_instances = replace_types_with_instances(
            input_dict_cls.__annotations__
        )
        input_dict = input_dict_cls(**annotations_with_instances)

        for current_input, previous_output in incoming_edges:
            input_param = current_input.split(".")[-1]
            if "args" in previous_output:
                setattr(
                    input_dict,
                    input_param,
                    getattr(args, previous_output.split(".")[-1]),
                )
                continue
            else:
                previous_output_node = previous_output.split(".")[0]
                # previous_output_class = previous_output.split(".")[1]
                previous_output_param = previous_output.split(".")[2]
                previous_output_node_id = int(previous_output_node.split("-")[1])
                setattr(
                    input_dict,
                    input_param,
                    getattr(
                        results_dict[previous_output_node_id],
                        previous_output_param,
                    ),
                )
        return input_dict

    def _create_component_instance(
        self, yaml_data: dict, node_data: dict, node_idx: int
    ) -> AbstractComponent:
        # Specify the full path and name of the module
        module_path = os.path.join(
            self.module_path(),
            yaml_data["components"][f"node-{node_idx}"]["module-path"],
        )
        module_name = (
            yaml_data["components"][f"node-{node_idx}"]["module-path"]
            .split("/")[-1]
            .split(".")[0]
        )

        # Loading the module and the class
        node_module = imp.load_source(module_name, module_path)
        component_cls = getattr(node_module, node_data["configuration"]["name"])

        if not issubclass(component_cls, AbstractComponent):
            raise ValueError(
                f"Class {node_data['class']} is not a subclass of AbstractComponent"
            )
        return component_cls()

    def _validate_nodes_processed(
        self, node_idx: int, adj_list: dict, results_dict: dict
    ) -> None:
        for in_node_idx in adj_list[node_idx]:
            if in_node_idx not in results_dict:
                raise ValueError(f"Node with ID '{node_idx}' cannot be processed yet")

    def _check_results_dict(self, results_dict: dict, node_idx: int) -> None:
        if node_idx not in results_dict:
            raise ValueError(f"Node with ID '{node_idx}' cannot be processed yet")
