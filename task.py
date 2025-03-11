from enum import IntEnum
import requests
from PIL import Image
import cv2
import numpy as np
import torch

TASK_ID_KEY = "task_id"
STATUS_KEY = "status"
PARAMS_KEY = "params"
ATTACHMENT_KEY = "attachment"

UUID_KEY = "uuid"
LABEL_KEY = "label"
ATTRIBUTES_KEY = "attributes"
OCCLUSION_KEY = "occlusion"
TRUNCATION_KEY = "truncation"
BACKGROUND_COLOR_KEY = "background_color"

LEFT_KEY = "left"
TOP_KEY = "top"
WIDTH_KEY = "width"
HEIGHT_KEY = "height"

class ErrorLevel(IntEnum):
    NORMAL = 0
    WARNING = 1
    ERROR = 2

class Task:
    def __init__(self, task_dict):
        self.__dict__ = task_dict

        self.task_id = self.__dict__.get(TASK_ID_KEY)
        self.status = self.__dict__.get(STATUS_KEY)

        self.get_image()
        self.build_annotations()

    def get_image(self):
        self.image = None

        params = self.__dict__.get(PARAMS_KEY)
        if params is None:
            return
        attachment = params.get(ATTACHMENT_KEY)
        if attachment is None or not isinstance(attachment, str):
            return

        try:
            # Download the image
            response = requests.get(attachment, stream=True)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            self.image = Image.open(response.raw)
        except (requests.RequestException, IOError) as e:
            print(f"Error downloading/opening image: {e}")
            return

    def build_annotations(self):
        self.annotations = []

        response = self.__dict__.get("response")
        if response is None:
            return

        annotations = response.get("annotations")
        if annotations is None:
            return

        for annotation in annotations:
            annotation = Annotation(annotation)
            annotation.set_image(self.image)

            self.annotations.append(annotation)

class Annotation:
    def __init__(self, annotation_dict):
        self.__dict__ = annotation_dict

        self.uuid = self.__dict__.get(UUID_KEY)
        self.label = self.__dict__.get(LABEL_KEY)

        attributes = self.__dict__.get(ATTRIBUTES_KEY)
        self.occlusion = attributes.get(OCCLUSION_KEY)
        self.truncation = attributes.get(TRUNCATION_KEY)
        self.background_color = attributes.get(BACKGROUND_COLOR_KEY)

        self.left = self.__dict__.get(LEFT_KEY)
        self.top = self.__dict__.get(TOP_KEY)
        self.width = self.__dict__.get(WIDTH_KEY)
        self.height = self.__dict__.get(HEIGHT_KEY)

        self.image_crop = None
        self.dominant_color = None
        self.dominant_colors = []
        self.average_color = None

        self.bounding_box = torch.tensor([[self.left, self.top, self.left + self.width, self.top + self.height]], dtype=torch.float)

        self.error_level = ErrorLevel.NORMAL
        self.error_messages = []

    def set_image(self, image):
        self.image_crop = None

        if image is not None:
            self.image_crop = image.crop((self.left, self.top, self.left + self.width, self.top + self.height))
            self.set_dominant_colors()

    # Adapted from https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv
    def set_dominant_colors(self):

        if self.image_crop is None:
            return

        # Convert PIL Image to numpy array and ensure it's RGB
        img_array = np.array(self.image_crop.convert('RGB'))

        average = img_array.mean(axis=0).mean(axis=0)
        self.average_color = average.tolist()

        # Reshape the array to 2D (pixels x RGB)
        pixels = img_array.reshape(-1, 3)

        # Convert to float32 for k-means
        pixels = np.float32(pixels)

        # Get number of pixels and set n_colors accordingly
        n_pixels = pixels.shape[0]
        n_colors = min(5, n_pixels)  # Use minimum of 5 or number of pixels

        if n_pixels == 0:  # Handle empty image case
            self.dominant_color = None
            self.dominant_colors = []
            return

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
        flags = cv2.KMEANS_RANDOM_CENTERS

        # Perform k-means clustering
        _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
        _, counts = np.unique(labels, return_counts=True)

        # Store both dominant color and full palette with percentages
        self.dominant_color = palette[np.argmax(counts)]
        self.dominant_colors = []
        for i in range(len(counts)):
            color = palette[i].astype(int)
            percentage = counts[i] / np.sum(counts)
            self.dominant_colors.append({
                'color': color.tolist(),
                'percentage': percentage
            })

    def set_error_level(self, error_level):
        self.error_level = max(self.error_level, error_level)

    def add_error_message(self, error_message):
        self.error_messages.append(error_message)
