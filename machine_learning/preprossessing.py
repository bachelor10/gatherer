from PIL import Image
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
"""



"""


from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img

def generate_dataset():
    print("Generating dataset")
    train_generator = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=False
    )
    print("Generating validation")

    validation_generator = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=False
    )
    print("Getting train data")

    train_generator = train_generator.flow_from_directory(
        'train',
        target_size=(26, 26),
        batch_size=32,
        class_mode='categorical')

    print("Getting validation data")

    validation_generator = validation_generator.flow_from_directory(
        'validation',
        target_size=(26, 26),
        batch_size=32,
        class_mode='categorical')

    return train_generator, validation_generator


train_generator, validation_generator = generate_dataset()

print("Creating model")

model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),
                 activation='relu',
                 input_shape=(26, 26, 3)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(66, activation='softmax'))

print("Compiling model")

model.compile(loss=keras.losses.mean_squared_error,
              optimizer=keras.optimizers.Adadelta(),
              metrics=['accuracy'])
print("Fitting model")

model.fit_generator(
        train_generator,
        steps_per_epoch=2000,
        epochs=10,
        validation_data=validation_generator,
        validation_steps=800)

print("Done!")
model.save('my_model.h5')  # creates a HDF5 file 'my_model.h5'
#score = model.evaluate(x_test, y_test, verbose=0)
#print('Test loss:', score[0])
#print('Test accuracy:', score[1])




#img = load_img('../bitmap_data/1516694853600.png')  # this is a PIL image

#transform_image(img)



