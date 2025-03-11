import json
import base64
import argparse
import scaleapi
from scaleapi.tasks import TaskStatus
import torchvision.ops.boxes as bops
import cv2
import numpy as np
from task import Task, ErrorLevel

API_KEY = "live_b1c5a645ea7e418a969b42b134e2d2d6"
PROJECT_NAME = "Traffic Sign Detection"

ANNOTATION_OBJECTS = ["traffic_control_sign", "construction_sign", "information_sign", "policy_sign", "non_visible_face"]
OCCLUSION_CHOICES = ["0%", "25%", "50%", "75%", "100%"]
TRUNCATION_CHOICES = ["0%", "25%", "50%", "75%", "100%"]
BACKGROUND_COLORS = ["white", "red", "orange", "yellow", "green", "blue", "other", "not_applicable"]

SIZE_MIN_SIZE_WARNING = 4
SIZE_RATIO_WARNING_THRESHOLD = 0.6
ASPECT_RATIO_WARNING_THRESHOLD = 6

POSITION_LOWER_WARNING_THRESHOLD = 0.15

COLOR_TOO_DARK_THRESHOLD = 90
COLOR_TOO_BRIGHT_THRESHOLD = 650

BOUNDING_BOX_IOU_DUPLICATE_WARNING_THRESHOLD = 0.9
BOUNDING_BOX_IOU_OVERLAP_WARNING_THRESHOLD = 0.5

# Error Messages
ERROR_MSG_NO_SIZE = "No size"
ERROR_MSG_INVALID_SIZE = "Invalid size"
ERROR_MSG_OUT_OF_BOUNDS = "Out of bounds"
ERROR_MSG_INVALID_LABEL = "Invalid label"
ERROR_MSG_INVALID_ATTRIBUTES = "Invalid attributes"
ERROR_MSG_LABEL_BGCOLOR_MISMATCH = "Label and background color mismatch"
ERROR_MSG_ZERO_SIZE = "Zero size"
ERROR_MSG_100_TRUNCATED = "100% truncated"
ERROR_MSG_PROBABLY_NOT_LEGIBLE = "Probably not legible Label: {} Size: {}, {}"
ERROR_MSG_SIZE_TOO_SMALL = "Size too small {}, {}"
ERROR_MSG_SIZE_TO_IMAGE_TOO_LARGE = "Size too large relative to image {}"
ERROR_MSG_ASPECT_RATIO_TOO_EXTREME = "Aspect ratio too extreme {}"
ERROR_MSG_POSITION_TOO_LOW = "Position too low Label max: {} Image threshold: {}"
ERROR_MSG_COLOR_TOO_DARK = "Color too dark Brightness: {}"
ERROR_MSG_COLOR_TOO_BRIGHT = "Color too bright Brightness: {}"
ERROR_MSG_LABEL_COLOR_MISMATCH = "Label and color mismatch Label: {} Color: {}"
ERROR_MSG_DUPLICATE_BOXES = "Duplicate boxes between {} and {} (Overlap: {})"
ERROR_MSG_OVERLAPPING_BOXES = "Overlapping boxes between {} and {} (Overlap: {})"

def get_tasks(client, project_name, created_after, created_before):
    # Define optional filters (adjust as necessary)
    filters = {
        "project_name": project_name,  # Replace with your project name
        "status": TaskStatus.Completed,  # Filter by task status (optional)
        "created_after": created_after,  # Filter by start time (optional)
        "created_before": created_before,  # Filter by end time (optional)
    }

    # Retrieve the list of tasks with optional filters
    tasks = client.get_tasks(**filters)

    return tasks

# Checks if the annotation has all the required data
def check_basic_annotation_data(annotation, image):
    image_width, image_height = image.size

    if annotation.left is None or annotation.top is None or annotation.width is None or annotation.height is None:
        annotation.set_error_level(ErrorLevel.ERROR)
        annotation.add_error_message(ERROR_MSG_NO_SIZE)

    if annotation.left < 0 or annotation.top < 0 or annotation.width < 0 or annotation.height < 0:
        annotation.set_error_level(ErrorLevel.ERROR)
        annotation.add_error_message(ERROR_MSG_INVALID_SIZE)

    if annotation.left + annotation.width > image_width or annotation.top + annotation.height > image_height:
        annotation.set_error_level(ErrorLevel.ERROR)
        annotation.add_error_message(ERROR_MSG_OUT_OF_BOUNDS)

    if annotation.label not in ANNOTATION_OBJECTS:
        annotation.set_error_level(ErrorLevel.ERROR)
        annotation.add_error_message(ERROR_MSG_INVALID_LABEL)

    if annotation.occlusion not in OCCLUSION_CHOICES or annotation.truncation not in TRUNCATION_CHOICES or annotation.background_color not in BACKGROUND_COLORS:
        annotation.set_error_level(ErrorLevel.ERROR)
        annotation.add_error_message(ERROR_MSG_INVALID_ATTRIBUTES)

    if annotation.label == "non_visible_face" and annotation.background_color != "not_applicable":
        annotation.set_error_level(ErrorLevel.ERROR)
        annotation.add_error_message(ERROR_MSG_LABEL_BGCOLOR_MISMATCH)

# Checks various heuristics about the size of the sign
def check_annotation_size(annotation, image):
    image_width, image_height = image.size

    # Signs that are 0x0 are probably not visible despite the specifcation allowing it
    if annotation.width == 0 or annotation.height == 0:
        annotation.set_error_level(ErrorLevel.ERROR)
        annotation.add_error_message(ERROR_MSG_ZERO_SIZE)

    # Signs that are 100% truncated are probably not visible despite the specifcation allowing it
    if annotation.truncation == "100%":
        annotation.set_error_level(ErrorLevel.ERROR)
        annotation.add_error_message(ERROR_MSG_100_TRUNCATED)

    width = float(annotation.width)
    height = float(annotation.height)

    # Handle cases with very small signs
    if (width < SIZE_MIN_SIZE_WARNING or height < SIZE_MIN_SIZE_WARNING) and annotation.truncation == "0%":
        # It's unlikely that a sign is legible if it's very small
        if annotation.label != "non_visible_face":
            annotation.set_error_level(ErrorLevel.WARNING)
            annotation.add_error_message(ERROR_MSG_PROBABLY_NOT_LEGIBLE.format(annotation.label, width, height))

        # Allow for ery truncated signs causing small sizes
        if annotation.truncation != "75%":
            annotation.set_error_level(ErrorLevel.ERROR)
            annotation.add_error_message(ERROR_MSG_SIZE_TOO_SMALL.format(width, height))

    # Check if sign is too large relative to image
    if width / image_width > SIZE_RATIO_WARNING_THRESHOLD or height / image_height > SIZE_RATIO_WARNING_THRESHOLD:
        annotation.set_error_level(ErrorLevel.ERROR)
        annotation.add_error_message(ERROR_MSG_SIZE_TO_IMAGE_TOO_LARGE.format(max(width / image_width, height / image_height)))

    # Check if sign has extreme aspect ratio
    if (width / annotation.height > ASPECT_RATIO_WARNING_THRESHOLD or height / annotation.width > ASPECT_RATIO_WARNING_THRESHOLD):

        # Allow for very truncated signs causing extreme aspect ratios
        if annotation.truncation != "75%":
            annotation.set_error_level(ErrorLevel.WARNING)
            annotation.add_error_message(ERROR_MSG_ASPECT_RATIO_TOO_EXTREME.format(max(width / height, height / width)))

# Checks if the sign is too low on the image, with the assumption that the camera is looking out from a vehicle
def check_annotation_position(annotation, image):
    image_width, image_height = image.size

    if annotation.top + annotation.height >= image_height - (image_height * POSITION_LOWER_WARNING_THRESHOLD):
        annotation.set_error_level(ErrorLevel.WARNING)
        annotation.add_error_message(ERROR_MSG_POSITION_TOO_LOW.format(annotation.top + annotation.height, image_height - (image_height * POSITION_LOWER_WARNING_THRESHOLD)))

# Checks heuristics related to the color of the sign
def check_annotation_color(annotation):
    brightness = sum(annotation.average_color)

    if brightness < COLOR_TOO_DARK_THRESHOLD:
        annotation.set_error_level(ErrorLevel.WARNING)
        annotation.add_error_message(ERROR_MSG_COLOR_TOO_DARK.format(brightness))
    elif brightness > COLOR_TOO_BRIGHT_THRESHOLD:
        annotation.set_error_level(ErrorLevel.WARNING)
        annotation.add_error_message(ERROR_MSG_COLOR_TOO_BRIGHT.format(brightness))
    elif annotation.label == "construction_sign":
        if annotation.dominant_color is not None:
            r, g, b = annotation.dominant_color
            # Check if color is in orange range (high red, medium green, low blue)
            if not (r > 150 and 50 < g < 140 and b < 50):
                annotation.set_error_level(ErrorLevel.WARNING)
                annotation.add_error_message(ERROR_MSG_LABEL_COLOR_MISMATCH.format(annotation.label, annotation.dominant_color))

# Adapted from https://www.geeksforgeeks.org/shape-detection-using-opencv-in-python/
# def check_annotation_shape(annotation):
#     # converting image into grayscale image
#     gray = cv2.cvtColor(np.array(annotation.image_crop.convert('RGB')), cv2.COLOR_BGR2GRAY)

#     # setting threshold of gray image 
#     _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

#     # using a findContours() function
#     contours, _ = cv2.findContours(
#         threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

#     i = 0

#     print(annotation.uuid)
#     # list for storing names of shapes
#     for contour in contours:

#         # here we are ignoring first counter because
#         # findcontour function detects whole image as shape
#         if i == 0:
#             i = 1
#             continue

#         # cv2.approxPloyDP() function to approximate the shape
#         approx = cv2.approxPolyDP(
#             contour, 0.01 * cv2.arcLength(contour, True), True)

#         if len(approx) == 3:
#             print("  Triangle")
#         elif len(approx) == 4:
#             print("  Quadrilateral")
#         elif len(approx) == 5:
#             print("  Pentagon")
#         elif len(approx) == 6:
#             print("  Hexagon")

def validate_annotation(annotation, image):
    check_basic_annotation_data(annotation, image)
    check_annotation_size(annotation, image)
    check_annotation_position(annotation, image)
    check_annotation_color(annotation)
    # check_annotation_shape(annotation)

# Checks hueristics about the bounding boxes of the signs
def check_bounding_boxes(task):
    # Adapted from https://stackoverflow.com/a/65988061

    # This is n^2, and should be optimized
    for i in range(len(task.annotations)):
        i_box = task.annotations[i].bounding_box

        for j in range(i + 1, len(task.annotations)):
            j_box = task.annotations[j].bounding_box

            iou = bops.box_iou(i_box, j_box).item()
            if iou > BOUNDING_BOX_IOU_DUPLICATE_WARNING_THRESHOLD:
                task.annotations[i].set_error_level(ErrorLevel.ERROR)
                task.annotations[i].add_error_message(ERROR_MSG_DUPLICATE_BOXES.format(task.annotations[i].uuid, task.annotations[j].uuid, iou))

                task.annotations[j].set_error_level(ErrorLevel.ERROR)
                task.annotations[j].add_error_message(ERROR_MSG_DUPLICATE_BOXES.format(task.annotations[j].uuid, task.annotations[i].uuid, iou))
            elif iou > BOUNDING_BOX_IOU_OVERLAP_WARNING_THRESHOLD:
                task.annotations[i].set_error_level(ErrorLevel.WARNING)
                task.annotations[i].add_error_message(ERROR_MSG_OVERLAPPING_BOXES.format(task.annotations[i].uuid, task.annotations[j].uuid, iou))

                task.annotations[j].set_error_level(ErrorLevel.WARNING)
                task.annotations[j].add_error_message(ERROR_MSG_OVERLAPPING_BOXES.format(task.annotations[j].uuid, task.annotations[i].uuid, iou))

def generate_task_report(task):
    task_report = {}
    task_report["task_id"] = task.task_id
    task_report["annotations"] = []

    for annotation in task.annotations:
        if annotation.error_level != ErrorLevel.NORMAL:
            annotation_report = {}
            annotation_report["uuid"] = annotation.uuid
            annotation_report["label"] = annotation.label
            annotation_report["error_level"] = annotation.error_level
            annotation_report["error_messages"] = annotation.error_messages
            #annotation_report["image"] = base64.b64encode(annotation.image_crop.tobytes()).decode('utf-8')
            task_report["annotations"].append(annotation_report)

    return task_report

def main(project_name, output_file, created_after, created_before):
    # Initialize the ScaleClient with your API key
    client = scaleapi.ScaleClient(API_KEY)

    report = {}
    report["project_name"] = project_name
    report["tasks"] = []

    # Retrieve the list of tasks with optional filters
    tasks = get_tasks(client, project_name, created_after, created_before)

    # Print the details of each task
    for task in tasks:
        task_dict = task.as_dict()
        if task_dict is None:
            print("no task dict")
            continue

        task = Task(task_dict)
        if task.task_id is None:
            print("no task id")
            continue

        print(task.task_id)

        if task.status != "completed":
            print("not completed")
            continue

        if task.image is None:
            print("no image")
            continue

        if task.annotations is None:
            print("no annotations")
            continue

        for annotation in task.annotations:
            validate_annotation(annotation, task.image)

        check_bounding_boxes(task)

        task_report = generate_task_report(task)
        report["tasks"].append(task_report)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_name", type=str, default=PROJECT_NAME)
    parser.add_argument("--output_file", type=str, default="report.json")
    parser.add_argument("--created_after", type=str, default="1960-01-01")
    parser.add_argument("--created_before", type=str, default="2100-01-01")
    args = parser.parse_args()

    main(args.project_name, args.output_file, args.created_after, args.created_before)
