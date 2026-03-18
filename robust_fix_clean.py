import h5py
import json

def fix_dict(d):
    if isinstance(d, dict):
        if 'batch_shape' in d:
            d['batch_input_shape'] = d['batch_shape']
            del d['batch_shape']
        if 'optional' in d:
            del d['optional']
        if 'quantization_config' in d:
            del d['quantization_config']
            
        # Fix DTypePolicy kwargs recursively just in case
        if 'dtype' in d and isinstance(d['dtype'], dict):
            dtype_dict = d['dtype']
            if dtype_dict.get('class_name') == 'DTypePolicy':
                d['dtype'] = dtype_dict.get('config', {}).get('name', 'float32')
            
        for k, v in list(d.items()):
            fix_dict(v)
    elif isinstance(d, list):
        for item in d:
            fix_dict(item)

def main():
    filepath = 'leaf_model_original.h5'
    output_filepath = 'leaf_model_fixed.h5'
    print(f"Reading from {filepath}...")
    with h5py.File(filepath, 'r') as f_in:
        model_config_raw = f_in.attrs.get('model_config')
        if isinstance(model_config_raw, bytes):
            model_config_str = model_config_raw.decode('utf-8')
        else:
            model_config_str = model_config_raw
            
        config = json.loads(model_config_str)
        fix_dict(config)
        
        print("Writing patched config...")
        with h5py.File(output_filepath, 'w') as f_out:
            for key in f_in.keys():
                f_in.copy(key, f_out)
            for attr_name, attr_value in f_in.attrs.items():
                if attr_name == 'model_config':
                    fixed_config_bytes = json.dumps(config).encode('utf-8')
                    f_out.attrs.create('model_config', fixed_config_bytes)
                else:
                    f_out.attrs[attr_name] = attr_value
    print("Fixed model saved to", output_filepath)

if __name__ == '__main__':
    main()
