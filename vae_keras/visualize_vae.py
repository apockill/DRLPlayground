import keras

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


def visualize_grid(generator, output_shape, num_cols=15, batch_size=32):
    # display a 2D manifold of the digits
    figure = np.zeros((output_shape[0] * num_cols,
                       output_shape[1] * num_cols,
                       output_shape[2]))

    # linearly spaced coordinates on the unit square were transformed through the inverse CDF (ppf) of the Gaussian
    # to produce values of the latent variables z, since the prior of the latent space is Gaussian
    grid_x = norm.ppf(np.linspace(0.05, 0.95, num_cols))
    grid_y = norm.ppf(np.linspace(0.05, 0.95, num_cols))

    for i, yi in enumerate(grid_x):
        for j, xi in enumerate(grid_y):
            z_sample = np.array([[xi, yi]])
            z_sample = np.tile(z_sample, batch_size).reshape(batch_size, 2)
            x_decoded = generator.predict(z_sample, batch_size=batch_size)

            # Reshape the image and convert it from BGR to RGB
            img = x_decoded[0].reshape(output_shape)
            img = img[..., ::-1]

            figure[i * output_shape[0]: (i + 1) * output_shape[0],
                   j * output_shape[1]: (j + 1) * output_shape[1]] = img

    plt.figure(figsize=(10, 10))
    plt.imshow(figure, cmap='Greys_r')
    plt.show()


if __name__ == "__main__":
    model = keras.models.load_model("./models/Decoder_ld_2_conv_3_id_128_e_1000.h5")
    visualize_grid(model, (32, 32, 3))