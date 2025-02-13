from pydantic import BaseModel
from typing import List, Optional
import networkx as nx


class DataField(BaseModel):
    symbol: str
    name: str
    type: str

class DataModel(BaseModel):
    symbol: str
    name: str
    type: str
    complex_data_type: Optional[str] = None
    fields: List[dict] = []
    call_by: Optional[str] = None

def process_fields_to_graph(fields):
    graph = nx.DiGraph()

    def add_node_and_edges(parent_symbol, field, parent_symbols=None):
        if parent_symbols is None:
            parent_symbols = []

        adjusted_parent_symbol = parent_symbol + "[]" if field.get("complexDataType") == "Table" else parent_symbol
        full_lineage = parent_symbols + [adjusted_parent_symbol]
        call_by_value = ".".join(full_lineage)

        if not graph.has_node(parent_symbol):
            data_model = DataModel(
                symbol=parent_symbol,
                name=field["name"],
                type=field["dataType"],
                complex_data_type=field.get('complexDataType'),
                call_by=call_by_value
            )
            graph.add_node(data_model.symbol, label=data_model.symbol, **data_model.model_dump())

        if not field['dataTypeComponents']:
            data_model = DataModel(
                symbol=field['symbol'],
                name=field["name"],
                type=field["dataType"],
                complex_data_type=field.get('complexDataType'),
                call_by=call_by_value
            )
            graph.add_node(data_model.symbol, label=data_model.symbol, **data_model.model_dump())

        else:
            subfields = field['dataTypeComponents']
            for subfield in subfields:
                if 'complexDataType' not in subfield:

                    data_field = DataField(
                        symbol=subfield['symbol'],
                        name=subfield['name'],
                        type=subfield['type']
                    )

                    if 'fields' not in graph.nodes[parent_symbol]:
                        graph.nodes[parent_symbol]['fields'] = []
                    graph.nodes[parent_symbol]['fields'].append(data_field.model_dump())
                else:

                    nested_model_symbol = subfield['symbol']
                    adjusted_nested_model_symbol = nested_model_symbol + "[]" if subfield.get("complexDataType") == "Table" else nested_model_symbol
                    sub_data_model = DataModel(
                        symbol=nested_model_symbol,
                        name=subfield["name"],
                        type=subfield["type"],
                        complex_data_type=subfield.get('complexDataType'),
                        call_by=".".join(full_lineage + [adjusted_nested_model_symbol])
                    )
                    graph.add_node(sub_data_model.symbol, label=sub_data_model.symbol, **sub_data_model.model_dump())

                    graph.add_edge(parent_symbol, nested_model_symbol)

                    add_node_and_edges(nested_model_symbol, subfield, full_lineage)

    for field in fields:
        add_node_and_edges(field['symbol'], field)

    return graph


def parse_nodes_to_prompt(nodes):
    prompt = []
    for node in nodes:
        print(node)
        if "complex_data_type" in node and node["complex_data_type"]:
            for field in node["fields"]:
                prompt.append(f"PF.{node['call_by']}.{field['symbol']}: {field['type']}\n")
        else:
            prompt.append(f"PF.{node['call_by']}: {node['type']}\n")
    prompt = "".join(prompt)

    return prompt



