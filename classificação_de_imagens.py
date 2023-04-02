# -*- coding: utf-8 -*-
"""Classificação de Imagens

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16kT8VbnmAOZVeovvSq8OFT59IK5ggyKd
"""

!echo "deb [arch=amd64] http://storage.googleapis.com/tensorflow-serving-apt stable tensorflow-model-server tensorflow-model-server-universal" | sudo tee /etc/apt/sources.list.d/tensorflow-serving.list && \
curl https://storage.googleapis.com/tensorflow-serving-apt/tensorflow-serving.release.pub.gpg | sudo apt-key add -

!apt-get update && apt-get install tensorflow-model-server

!wget 'http://storage.googleapis.com/tensorflow-serving-apt/pool/tensorflow-model-server-universal-2.8.0/t/tensorflow-model-server-universal/tensorflow-model-server-universal_2.8.0_all.deb'
!dpkg -i tensorflow-model-server-universal_2.8.0_all.deb.2

!pip install requests

# Commented out IPython magic to ensure Python compatibility.
import os
import json
import requests
import subprocess
import numpy as np
import random
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import matplotlib.pyplot as plt

from tensorflow.keras.datasets import cifar10
# %matplotlib inline

(X_train,y_train),(X_test,y_test) = cifar10.load_data()

X_train = X_train/255.0
X_test = X_test/255.0

class_names = ['airplane','automobile','bird','cat','deer','dog','frog','horse','ship','truck']

X_train.shape

X_test.shape

np.unique(y_train)

model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Conv2D(filters=32,kernel_size=3,padding='same',activation='relu',input_shape=(32,32,3)))
model.add(tf.keras.layers.Conv2D(filters=32,kernel_size=3,padding='same',activation='relu'))
model.add(tf.keras.layers.MaxPool2D(pool_size=2,strides=2,padding='valid'))
model.add(tf.keras.layers.Conv2D(filters=64,kernel_size=3,padding='same',activation='relu'))
model.add(tf.keras.layers.Conv2D(filters=64,kernel_size=3,padding='same',activation='relu'))
model.add(tf.keras.layers.MaxPool2D(pool_size=2,strides=2,padding='valid'))
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(128,activation='relu'))
model.add(tf.keras.layers.Dense(10,activation='softmax'))
model.compile(optimizer='adam',loss='sparse_categorical_crossentropy',metrics=['accuracy'])
# model.summary()

model.fit(X_train,y_train,batch_size=128,epochs=10)

test_loss, test_acc = model.evaluate(X_test,y_test)

print(f'Test accuracy: {test_acc}')
print(f'Test loss: {test_loss}')

# salvando o modelo para produção

#criando o diretório para  modelo
model_dir = 'model/'
version = 1

export_path = os.path.join(model_dir,str(version))
export_path

if os.path.isdir(export_path):
  !rm -r {export_path}

#salvando o modelo para o tensorflow serving
tf.saved_model.simple_save(tf.keras.backend.get_session(),export_dir=export_path,
                           inputs={'input_image':model.input},
                           outputs={t.name: t for t in model.outputs})

# configuração do ambiente de produção
os.environ['model_dir'] = os.path.abspath(model_dir)

# Commented out IPython magic to ensure Python compatibility.
# %%bash --bg
# nohup tensorflow_model_server --rest_api_port=8501 --model_name=cifar10 --model_base_path="${model_dir}" >sever.log 2>&1

!tail server.log

random_image = np.random.randint(0,len(X_test))
random_image

#criando o objeto json
data = json.dumps({'signature_name':'serving_default','instances':[X_test[random_image].tolist()]})
data

# enviando a primeira requisição POST
headers = {'content_type':'application/json'}
json_response = requests.post(url='http://localhost:8501/v1/models/cifar10:predict',data=data,headers=headers)

json_response

predictions = json.loads(json_response.text)['predictions']
predictions

plt.imshow(X_test[random_image])

class_names[np.argmax(predictions[0])]

#enviando a requisição post para um modelo especifico
specific_json_response = requests.post(url="http://localhost:8501/v1/models/cifar10/versions/1:predict", data = data, headers = headers)

specific_json_response