import argparse
from pathlib import Path

import cv2
import dhash
from PIL import Image

from unity_server.server import UnityInterface

HASH_SIZE = 4


class ImageRecorder:
    """ This class will keep track of images that have been recoreded, the similarity of new images, and will
    automatically save images that are "novel" enough to be worthy of saving. """

    def __init__(self, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self.output_dir = Path(output_dir)
        self.existing_dhashes = self.get_existing_dhashes(output_dir)


    def get_existing_dhashes(self, img_dir):
        """ Get a list of existing dhashes from the images in that directory """
        dhashes = []
        for img_path in Path(img_dir).glob("*.png"):
            img = cv2.imread(str(img_path))
            hash = dhash.dhash_int(Image.fromarray(img), HASH_SIZE)
            dhashes.append(hash)

        return dhashes

    def record(self, new_image):
        """ This will decide whether or not to record the image, and then save it if it's novel enough"""

        hash = dhash.dhash_int(Image.fromarray(new_image), HASH_SIZE)
        if hash not in self.existing_dhashes:
            self.existing_dhashes.append(hash)
            write_to = self.output_dir / (str(hash) + ".png")
            print("Writing image to ", write_to)
            cv2.imwrite(str(write_to), new_image)


def record_images(output_dir, client):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_dir = Path(output_dir).resolve()
    recorder = ImageRecorder(output_dir)
    last_key = 0

    while True:
        is_over, image, score = client.get_state()

        if is_over:
            print("Game over!")
            client.reset_game()
            continue

        cv2.imshow('BrainServer', image)
        recorder.record(image)

        k = cv2.waitKey(1) - 48
        if k >= 0:
            last_key = k

        client.send_state(last_key)  # choice([UP, DOWN, LEFT, RIGHT]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script saves many images from the game into a given folder")

    parser.add_argument('-o', '--output_dir', type=str, default="./images/",
                        help='The directory where the output VAE training images will be saved.')
    parser.add_argument('-u', '--hostname', type=str, default="localhost",
                        help='The hostname of the running unity server')
    parser.add_argument('-p', '--port', type=int, default=1234,
                        help='The port of the running Unity server')
    args = parser.parse_args()


    interface = UnityInterface(args.hostname, args.port)
    record_images(args.output_dir, interface)