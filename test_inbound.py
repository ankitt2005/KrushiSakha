import tensorflow as tf
from tensorflow import keras
import json

inp1 = keras.layers.Input(shape=(10,), name='input1')
inp2 = keras.layers.Input(shape=(10,), name='input2')

x1 = keras.layers.Dense(10, name='dense1')(inp1)
x2 = keras.layers.Dense(10, name='dense2')(inp2)

added = keras.layers.Add(name='add1')([x1, x2])

model = keras.models.Model(inputs=[inp1, inp2], outputs=added)

config = model.get_config()
print(json.dumps(config['layers'], indent=2))
