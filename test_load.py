import keras

print(f"Keras version: {keras.__version__}")
model = keras.models.load_model('leaf_model_fixed.h5', compile=False)
print("Model loaded successfully!")
