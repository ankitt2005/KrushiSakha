import tensorflow as tf
from tensorflow import keras
import sys

def convert_h5_to_saved_model(h5_path, pb_dir):
    try:
        print(f"Loading {h5_path} with compile=False...")
        model = keras.models.load_model(h5_path, compile=False)
        print(f"Saving to {pb_dir} as SavedModel...")
        model.export(pb_dir)
        print("Success!")
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    convert_h5_to_saved_model("leaf_model_backup.h5", "leaf_model_saved")
