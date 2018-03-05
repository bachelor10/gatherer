import functools

import keras
from keras import backend, Sequential
import tensorflow as tf
import tensorflow
from keras import backend as K
from keras import layers
from keras.callbacks import Callback
from keras.layers import LSTM, Bidirectional, BatchNormalization, Activation, Embedding
from keras.utils import Sequence
import numpy as np

from online_recog.xml_parse_rawdata import *
from online_recog.online_trainer import *


def populate_data_names(fil):
	list = []
	print("Populating data names.")
	with h5py.File(fil, "r") as f:
		for d in f:
			list.append(d)
	return list


# TODO parse data into self.x and self.y, and split them into train, validation. Testdata is avalable in another subdirectory

class InkMLSequence(Sequence): # https://gist.github.com/alxndrkalinin/6cc4228e9178ec4af7b2696a0d1ad5a1
	
	def __init__(self, batch_size=1):  # batch size is one because one matrix is several traces
		self.batch_size = batch_size
		self.file = 'raw_train.hdf5'
		self.class_file = 'raw_class.hdf5'
		self.classes, self.num_classes = find_classes('raw_data_classes.txt')
		self.x_name, self.y_name = populate_data_names(self.file), populate_data_names(self.class_file)
	
	def __len__(self):
		return np.ceil(len(self.x_name) / float(self.batch_size))
	
	def __getitem__(self, ix):
		with h5py.File(self.file) as f:
			batch_x = f[self.x_name[ix * self.batch_size:(ix + 1) * self.batch_size]]
		with h5py.File(self.class_file) as g:
			batch_y = g[self.y_name[ix * self.batch_size:(ix + 1) * self.batch_size]]
		batch_y = keras.utils.to_categorical(batch_y, self.num_classes)
		
		return np.array([batch_x, batch_y])


if __name__ == '__main__':
	epochs = 5
	verbose = 1
	
	train_generator = InkMLSequence()
	print(len(train_generator.x_name))
	model = Sequential()
	model.add(Embedding(1,None,mask_zero=True))
	model.add(LSTM(input_shape=(train_generator.batch_size, None), return_sequences=True))
	model.add(Dropout(0.2))
	model.add(LSTM(input_shape=(train_generator.batch_size, None), return_sequences=True))
	model.add(Dropout(0.2))
	model.add(Activation('softmax'))
	
	model.fit(
		train_generator,
		epochs=epochs
	)
	
