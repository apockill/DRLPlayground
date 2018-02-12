import numpy as np
from keras.layers import Input, Dense, Lambda, Flatten, Reshape, Layer
from keras.layers import Conv2D, Conv2DTranspose
from keras.models import Model
from keras import backend as kb
from keras import metrics


# Custom loss layer
class CustomVariationalLossLayer(Layer):
    """
    This is specifically for calculating the loss for a variational autoencoder. No operations happen here that change
    the inputs or outputs.
    """
    def __init__(self, img_width, img_height, **kwargs):
        self.is_placeholder = True
        super(CustomVariationalLossLayer, self).__init__(**kwargs)
        self.height = img_height
        self.width = img_width

    def vae_loss(self, x, x_decoded_mean_squash, z_mean, z_log_var):
        x = kb.flatten(x)
        x_decoded_mean_squash = kb.flatten(x_decoded_mean_squash)

        xent_loss = self.height * self.width * 1metrics.binary_crossentropy(x, x_decoded_mean_squash)
        kl_loss = - 0.5 * kb.mean(1 + z_log_var - kb.square(z_mean) - kb.exp(z_log_var), axis=-1)
        return kb.mean(xent_loss + kl_loss)

    def call(self, inputs):
        x = inputs[0]
        x_decoded_mean_squash = inputs[1]
        z_mean = inputs[2]
        z_log_var = inputs[3]

        loss = self.vae_loss(x, x_decoded_mean_squash, z_mean, z_log_var)
        self.add_loss(loss, inputs=inputs)
        return x


class VariationalAutoencoder:
    def __init__(self, img_resolution, channels, epochs=1000):
        # Network Parameters
        self.height = img_resolution[1]
        self.width = img_resolution[0]
        self.channels = channels
        self.latent_dim = 2
        self.intermediate_dim = 128
        self.epsilon_std = 1.0
        self.epochs = epochs
        self.filters = 32
        self.num_conv = 3
        self.batch_size = 500


    def train(self, x_train, x_test):
        """ Trains an autoencoder on the dataset and returns a trained encoder and decoder"""
        # Build the model equation
        x = Input(shape=(self.height, self.width, self.channels))
        encoded, z_mean, z_log_var = self.encoder(x)
        decoded = self.decoder(encoded)
        y = CustomVariationalLossLayer(self.width, self.height)([x, decoded, z_mean, z_log_var])

        # Initialize the Keras model
        vae = Model(x, y)
        vae.compile(optimizer='rmsprop', loss=None)
        vae.summary()

        # Prepare the dataset
        x_train = x_train.astype('float32') / 255.
        x_train = x_train.reshape((x_train.shape[0],) + (self.height, self.width, self.channels))
        x_test = x_test.astype('float32') / 255.
        x_test = x_test.reshape((x_test.shape[0],) + (self.height, self.width, self.channels))

        # Train
        vae.fit(x_train,
                shuffle=True,
                epochs=self.epochs,
                batch_size=self.batch_size,
                validation_data=(x_test, None))

        # Create the encoder that was learned
        encoder = Model(x, z_mean)

        # Create the decoder that was learned
        decoder_input = Input(shape=(self.latent_dim, ))
        decoded = self.decoder(decoder_input)
        decoder = Model(decoder_input, decoded)

        return encoder, decoder

    def encoder(self, x):
        # Encoder architecture

        conv_1 = Conv2D(self.channels,
                        kernel_size=(2, 2),
                        padding='same', activation='relu')(x)
        conv_2 = Conv2D(self.filters,
                        kernel_size=(2, 2),
                        padding='same', activation='relu',
                        strides=(2, 2))(conv_1)
        conv_3 = Conv2D(self.filters,
                        kernel_size=self.num_conv,
                        padding='same', activation='relu',
                        strides=1)(conv_2)
        conv_4 = Conv2D(self.filters,
                        kernel_size=self.num_conv,
                        padding='same', activation='relu',
                        strides=1)(conv_3)
        flat = Flatten()(conv_4)
        hidden = Dense(self.intermediate_dim, activation='relu')(flat)

        # mean and variance for latent variables
        z_mean = Dense(self.latent_dim)(hidden)
        z_log_var = Dense(self.latent_dim)(hidden)

        z = Lambda(self._sampling, output_shape=(self.latent_dim,))([z_mean, z_log_var])
        return z, z_mean, z_log_var

    def decoder(self, z):
        # Decoder architecture
        decoder_hid = Dense(self.intermediate_dim, activation='relu')
        decoder_upsample = Dense(self.filters * int(self.height / 2 * self.width / 2), activation='relu')

        output_shape = (self.batch_size, int(self.height / 2), int(self.width / 2), self.filters)

        decoder_reshape = Reshape(output_shape[1:])
        decoder_deconv_1 = Conv2DTranspose(self.filters,
                                           kernel_size=self.num_conv,
                                           padding='same',
                                           strides=1,
                                           activation='relu')
        decoder_deconv_2 = Conv2DTranspose(self.filters,
                                           kernel_size=self.num_conv,
                                           padding='same',
                                           strides=1,
                                           activation='relu')
        decoder_deconv_3_upsamp = Conv2DTranspose(self.filters,
                                                  kernel_size=(3, 3),
                                                  strides=(2, 2),
                                                  padding='valid',
                                                  activation='relu')
        decoder_mean_squash = Conv2D(self.channels,
                                     kernel_size=2,
                                     padding='valid',
                                     activation='sigmoid')

        hid_decoded = decoder_hid(z)
        up_decoded = decoder_upsample(hid_decoded)
        reshape_decoded = decoder_reshape(up_decoded)
        deconv_1_decoded = decoder_deconv_1(reshape_decoded)
        deconv_2_decoded = decoder_deconv_2(deconv_1_decoded)
        x_decoded_relu = decoder_deconv_3_upsamp(deconv_2_decoded)
        x_decoded_mean_squash = decoder_mean_squash(x_decoded_relu)

        return x_decoded_mean_squash

    def _sampling(self, args):
        """ The sampling layer"""
        z_mean, z_log_var = args
        epsilon = kb.random_normal(shape=(kb.shape(z_mean)[0], self.latent_dim),
                                   mean=0., stddev=self.epsilon_std)
        return z_mean + kb.exp(z_log_var) * epsilon