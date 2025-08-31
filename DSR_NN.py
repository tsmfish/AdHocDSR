import numpy
import tensorflow as tf
import random as rn
import os
os.environ['PYTHONHASHSEED'] = '0'
rn.seed(12345)
from keras.layers import Convolution2D, BatchNormalization, MaxPooling2D, Dense, Input, Dropout, Flatten
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.models import Model
from keras.callbacks import TensorBoard
from keras.models import Sequential
from keras.optimizers import Adam
import time
# import pandas as pd
from keras.callbacks import TensorBoard
import os
from sklearn.model_selection import train_test_split
from keras.callbacks import CSVLogger
from keras.callbacks import ModelCheckpoint
from keras.models import load_model
from scipy import signal
from scipy.io import wavfile
import random
import csv

# ---------------------------------------------------------------------------------------------------------------
#  prepare data for NN
# ----------------------------------------------------------------------------------------------------------------
def row_to_nn_input(row_data):
    adj = 5
    for x in range(2, len(row_data)):
        row_data[x] = row_data[x] / adj
    row_data[0] = row_data[0] / 15.0
    row_data[1] = row_data[1] / 2000.0
    return row_data

def load_data(file_name):
    csvfile = open(file_name, newline='\n')
    reader = csv.reader(csvfile, delimiter=',')
    data = list(reader)
    XX = []
    YY = []
    for row_index in range(1, len(data)):
        if len(data[row_index]) > 0:
            YY.append([3* float(data[row_index][0])])
            row_xx = [float(x) for x in data[row_index][1:]]

            #  norm----------------------------
            row_xx = row_to_nn_input(row_xx)
            #  end norm--------------------------

            XX.append(row_xx)
    return numpy.array(XX) , numpy.array(YY)

# ---------------------------------------------------------------------------------------------------------------
#  nn learn
# ----------------------------------------------------------------------------------------------------------------
def Learn_NN_5L_(X_Train, Y_Train,X_val1, y_val1,  RezDir, NN_Name, Epochs=30):

    # Input data is 2 dimension array

    model = Sequential([
        Dense(9, activation='relu', input_shape=(X_Train.shape[1],)),
        Dense(7, activation='relu'),
        Dense(5, activation='relu'),
        Dense(1)  # Output layer with 1 neuron and linear activation (default)
    ])
    # Create model
    # model = Sequential()
    # Normalization data
    # model.add(BatchNormalization())
    # add Feedforward part
    # model.add(Dense(15, input_shape=input_shape,activation='relu'))
    # model.add(Dense(10,activation='relu'))
    # # add Output part
    # model.add(Dense(2,activation='linear'))

    model.compile(optimizer='adam',    loss='mse',        metrics=['mae'])
    csv_logger = CSVLogger(RezDir + NN_Name + '_training__log.csv', separator=',', append=False)

    checkpoint = ModelCheckpoint(filepath=RezDir + NN_Name + '_Best.hdf5',
                                 monitor='val_loss',
                                 save_best_only=True,
                                 mode='min',
                                 verbose=1)
    model.fit(X_Train, Y_Train,
              batch_size=64,
              epochs=Epochs, shuffle=True,
              validation_data=(X_val1, y_val1),
              callbacks=[checkpoint, csv_logger])
    model.save(filepath=RezDir + NN_Name + '_Final.hdf5')
    # rr = model.predict(X_val1)
    # print('end')

# ---------------------------------------------------------------------------------------------------------------
#  Clas for load and Run NN for simulation
# ----------------------------------------------------------------------------------------------------------------
class Run_NN():
    def __init__(self, Net_file_nameme):
        self.nn = load_model(Net_file_nameme)

    def run(self, rows_data):
        input = []
        for row in rows_data:
            input.append(row_to_nn_input(row))
        pred = self.nn.predict(numpy.array(input))
        return pred


    def run_wo_preproc(self, rows_data):
        pred = self.nn.predict(rows_data)
        print(pred)

# ---------------------------------------------------------------------------------------------------------------
#  Learn NN
# ----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    X_Train, Y_Train = load_data(file_name= r'd:\Sychov\HNUPS\Projects\DSR_data\train_snr_data.csv')
    X_val1, y_val1 = load_data(file_name=r'd:\Sychov\HNUPS\Projects\DSR_data\valid_snr_data.csv')
    Learn_NN_5L_(X_Train, Y_Train, X_val1, y_val1, RezDir= r'd:\Sychov\HNUPS\Projects\DSR_data\\',
                 NN_Name='dsr_snr_net_v2', Epochs=30)

    # NN = Run_NN(r'd:\Sychov\HNUPS\Projects\DSR_data\dsr_net_Best.hdf5')
    # X_val1, y_val1 = load_data(file_name=r'd:\Sychov\HNUPS\Projects\DSR_data\test_nn_data.csv')
    # NN.run_wo_preproc(X_val1)








