import h5py
import json

def inspect_nodes(filepath):
    print(f"Opening {filepath}")
    with h5py.File(filepath, 'r') as f:
        model_config_raw = f.attrs.get('model_config')
        if isinstance(model_config_raw, bytes):
            config_str = model_config_raw.decode('utf-8')
        else:
            config_str = model_config_raw
        
        config = json.loads(config_str)
        layers = config.get('config', {}).get('layers', [])
        for layer in layers:
            inbound_nodes = layer.get('inbound_nodes', [])
            if not isinstance(inbound_nodes, list):
                print(f"Layer {layer['name']} inbound_nodes is not a list: {type(inbound_nodes)}")
            else:
                for idx, node in enumerate(inbound_nodes):
                    # node should be a list like:
                    # [ [inbound_node_name, node_index, tensor_index, kwargs] ]
                    if not isinstance(node, list):
                        print(f"Layer {layer['name']} node {idx} is not a list: {type(node)} -> {node}")
                        # In some older Keras formats, node is a list of lists.
                        # Wait, the error is inside input_data = input_data.as_list(), which is likely during the node construction.

if __name__ == "__main__":
    inspect_nodes("leaf_model_backup.h5")
