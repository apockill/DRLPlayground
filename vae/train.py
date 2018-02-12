import argparse
from pathlib import Path

from vae.model import VariationalAutoencoder
from vae.dataset import Dataset

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script will train an autoencoder and save the trained encoder"
                                                 "and decoder to a specified directory.")
    parser.add_argument('-i', '--image_dir', type=str, required=True,
                        help='The directory where the images for training are saved')
    parser.add_argument('-d', '--output_dir', type=str, default="./models/",
                        help='The directory where the trained encoder and decoder files will be saved')
    parser.add_argument('--resolution', type=int, nargs=2, required=True,
                        help='The image width, height, and channels that the network will accept as input')
    parser.add_argument('--latent_dim', type=int, default=2,
                        help='The size of the bottleneck vector in the autonecoder')
    parser.add_argument('--epochs', type=int, default=1000,
                        help='How long you want the training to go on for. Usually > 1000')
    args = parser.parse_args()

    # Load the dataset
    dataset = Dataset(args.image_dir, 0.2, load_resolution=args.resolution)
    x_train, x_test = dataset.load()

    # Train the model
    vae = VariationalAutoencoder(args.resolution, 3, args.epochs)
    vae.latent_dim = args.latent_dim
    encoder, decoder = vae.train(x_train, x_test)

    # Save the encoder and decoder
    Path(args.output_dir).mkdir(exist_ok=True)
    name = "_ld_{}_e_{}.h5".format(vae.latent_dim, vae.epochs)
    encoder.save(str(Path(args.output_dir) / ("Encoder" + name)))
    decoder.save(str(Path(args.output_dir) / ("Decoder" + name)))
