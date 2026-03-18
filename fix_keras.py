import h5py
import json

def fix_h5_model(filepath, output_filepath):
    print(f"Opening {filepath}...")
    with h5py.File(filepath, 'r') as f_in:
        print("Reading model config...")
        model_config_raw = f_in.attrs.get('model_config')
        if isinstance(model_config_raw, bytes):
            model_config_str = model_config_raw.decode('utf-8')
        else:
            model_config_str = model_config_raw
        model_config = json.loads(model_config_str)
        
        def clean_config(config_dict):
            if isinstance(config_dict, dict):
                # Fix DTypePolicy
                if 'dtype' in config_dict and isinstance(config_dict['dtype'], dict):
                    dtype_dict = config_dict['dtype']
                    if dtype_dict.get('class_name') == 'DTypePolicy':
                        # Replace complex dict with simple string ('float32')
                        new_dtype = dtype_dict.get('config', {}).get('name', 'float32')
                        print(f"    Replacing DTypePolicy dict with '{new_dtype}'")
                        config_dict['dtype'] = new_dtype

                # Fix inbound_nodes
                if 'inbound_nodes' in config_dict and isinstance(config_dict['inbound_nodes'], list):
                    new_inbound_nodes = []
                    for node in config_dict['inbound_nodes']:
                        if isinstance(node, dict) and 'args' in node:
                            new_node = []
                            kwargs = node.get('kwargs', {})
                            for arg in node['args']:
                                if isinstance(arg, dict) and arg.get('class_name') == '__keras_tensor__':
                                    history = arg.get('config', {}).get('keras_history')
                                    if history:
                                        conn = list(history)
                                        conn.append(kwargs)
                                        kwargs = {}
                                        new_node.append(conn)
                            new_inbound_nodes.append(new_node)
                        else:
                            new_inbound_nodes.append(node)
                    if config_dict['inbound_nodes'] != new_inbound_nodes:
                        print(f"    Fixed inbound_nodes in a layer config")
                    config_dict['inbound_nodes'] = new_inbound_nodes

                if config_dict.get('class_name') == 'InputLayer':
                    config = config_dict.get('config', {})
                    if 'batch_shape' in config:
                        print(f"    Removing batch_shape: {config['batch_shape']}")
                        config['batch_input_shape'] = config['batch_shape']
                        del config['batch_shape']
                    if 'optional' in config:
                        print(f"    Removing optional: {config['optional']}")
                        del config['optional']
                
                if config_dict.get('class_name') == 'Dense':
                    config = config_dict.get('config', {})
                    if 'quantization_config' in config:
                        print(f"    Removing quantization_config in {config.get('name')}")
                        del config['quantization_config']
                
                for k, v in list(config_dict.items()):
                    clean_config(v)
            elif isinstance(config_dict, list):
                for item in config_dict:
                    clean_config(item)

        print("Fixing configs recursively...")
        clean_config(model_config)
                
        # Write modified config back to a new file
        print(f"Writing to {output_filepath}...")
        with h5py.File(output_filepath, 'w') as f_out:
            # Copy all groups/datasets from the original file
            for key in f_in.keys():
                f_in.copy(key, f_out)
            
            # Copy all attributes
            for attr_name, attr_value in f_in.attrs.items():
                if attr_name == 'model_config':
                    # Save the new fixed config
                    fixed_config_bytes = json.dumps(model_config).encode('utf-8')
                    f_out.attrs.create('model_config', fixed_config_bytes)
                else:
                    f_out.attrs[attr_name] = attr_value
    print("Done!")

if __name__ == "__main__":
    fix_h5_model("leaf_model_backup.h5", "leaf_model.h5")
