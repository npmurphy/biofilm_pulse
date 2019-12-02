import keras
import os
import scipy.io
import numpy as np
import skimage.io
import skimage.transform as trans
from keras import backend as K
from keras.callbacks import LearningRateScheduler, ModelCheckpoint
from keras.layers import (
    Conv2D,
    Conv2DTranspose,
    Dropout,
    Input,
    MaxPooling2D,
    UpSampling2D,
    concatenate,
    merge,
)
import keras.layers
from keras.models import Model
from keras.optimizers import Adam
from skimage.transform import resize

# this unet from https://github.com/zhixuhao/unet/blob/master/model.py
def unet(input_size=(1, 256, 256), output_dim=1):
    inputs = Input(input_size)

    conv1 = Conv2D(
        64, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(inputs)
    conv1 = Conv2D(
        64, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2), data_format="channels_first")(conv1)

    conv2 = Conv2D(
        128, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(pool1)
    conv2 = Conv2D(
        128, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2), data_format="channels_first")(conv2)

    conv3 = Conv2D(
        256, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(pool2)
    conv3 = Conv2D(
        256, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2), data_format="channels_first")(conv3)

    conv4 = Conv2D(
        512, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(pool3)
    conv4 = Conv2D(
        512, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv4)
    drop4 = Dropout(0.5)(conv4)
    pool4 = MaxPooling2D(pool_size=(2, 2), data_format="channels_first")(drop4)

    conv5 = Conv2D(
        1024, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(pool4)
    conv5 = Conv2D(
        1024, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv5)
    drop5 = Dropout(0.5)(conv5)

    up6 = Conv2D(
        512, 2, activation="relu", padding="same", kernel_initializer="he_normal"
    )(UpSampling2D(size=(2, 2))(drop5))
    merge6 = merge([drop4, up6], mode="concat", concat_axis=1)
    merge6 = keras.layers.Concatenate(axis=1)([drop4, up6])
    conv6 = Conv2D(
        512, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(merge6)
    conv6 = Conv2D(
        512, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv6)

    up7 = Conv2D(
        256, 2, activation="relu", padding="same", kernel_initializer="he_normal"
    )(UpSampling2D(size=(2, 2))(conv6))
    merge7 = merge([conv3, up7], mode="concat", concat_axis=1)
    merge7 = keras.layers.Concatenate(axis=1)([conv3, up7])
    conv7 = Conv2D(
        256, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(merge7)
    conv7 = Conv2D(
        256, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv7)

    up8 = Conv2D(
        128, 2, activation="relu", padding="same", kernel_initializer="he_normal"
    )(UpSampling2D(size=(2, 2))(conv7))
    merge8 = keras.layers.Concatenate(axis=1)([conv2, up8])
    conv8 = Conv2D(
        128, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(merge8)
    conv8 = Conv2D(
        128, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv8)

    up9 = Conv2D(
        64, 2, activation="relu", padding="same", kernel_initializer="he_normal"
    )(UpSampling2D(size=(2, 2))(conv8))
    merge9 = keras.layers.Concatenate(axis=1)([conv1, up9])
    conv9 = Conv2D(
        64, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(merge9)
    conv9 = Conv2D(
        64, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv9)
    conv9 = Conv2D(
        2, 3, activation="relu", padding="same", kernel_initializer="he_normal"
    )(conv9)
    conv10 = Conv2D(output_dim, (1, 1), activation="sigmoid")(conv9)

    model = Model(inputs=inputs, outputs=conv10)

    model.summary()

    model.compile(
        optimizer=Adam(lr=1e-4), loss="binary_crossentropy", metrics=["accuracy"]
    )

    return model


def main():
    # img_rows, img_cols = X_train.shape[2], X_train.shape[3]
    img_rows, img_cols = 64, 64
    print(img_rows, img_cols)
    input_size = (1, img_rows, img_cols)

    # try_model =  model_zoo.unet_to_ellipse_small
    try_model = unet

    dirname = try_model.__name__ + "_2d"

    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass

    data = scipy.io.loadmat("training.mat")
    X_train = data["train_X"]
    Y_train = data["train_Y"]

    model = try_model(input_size=input_size, output_dim=2)
    model_weights = os.path.join(dirname, "model_weights.h5")
    model_phase = os.path.join(dirname, "model.h5")
    filepath = os.path.join(
        dirname, "weights-improvement-{epoch:02d}-{val_acc:.2f}.hdf5"
    )
    try:
        model.load_weights(model_weights)
    except OSError:
        pass

    checkpoint = ModelCheckpoint(
        filepath, monitor="val_acc", verbose=1, save_best_only=True, mode="max"
    )
    callbacks_list = [checkpoint]

    batch_size = 32
    epochs = 15
    # time.sleep(60*60)
    history = (
        model.fit(
            x=X_train,
            y=Y_train,
            # validation_data=(X_test, Y_test),
            batch_size=batch_size,
            epochs=epochs,
            verbose=1,
            callbacks=callbacks_list,
            validation_split=0.5,
        ),
    )  # class_weight=[0.3, 0.7])
    # validation_data=(test_X, test_Y))
    model.save(model_phase)
    model.save_weights(model_weights)

