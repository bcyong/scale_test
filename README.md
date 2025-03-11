# Introduction

## Objective

The objective of this project is to programmatically perform quality checks on human labeled data for **ObserveSign**, a tech startup in the autonomous vehicle industry attempting to detect and understand traffic signals.

## Scope of Work

This project attempts to perform automated quality checks on already human labeled iamges according to specifications created by **ObserveSign**. To do this, the completed tasks are downloaded from Scale using the Scale API, as well as the associated original image being annotated, and a set of heuristics are applied to flag annotations that may contain errors or irregularites, which are then compiled into a JSON report.

# Codebase

## Files

This project consists of two files, `main.py` and `task.py`. 
`main.py` implements the actual quality checks performed on the Scale Tasks, as well as runtime logic to determine which project and tasks are evaluated.
`task.py` implements classes for Task and Annotation to organize data, as well as do some initial calculations used by the various quality checks.

## Dataflow

The data in this project proceeds as follows:
1. A set of completed tasks associated with a `project_name` are pulled down utilizing the Scale API
2. Data from each Task is used to create a Task object, with associated Annotations created as well
3. The source image related to the Task is pulled down
4. A set of quality checks are performed on each Task, both analyzing individual Annotations as well as the full set of Annotations for a Task
5. A JSON report is saved to disk listing Annotations for each Task that have been flagged with warnings or errors, along with the associated error messages

# Quality Checks Implemented

# Run Instructions 
Usage:

`> python main.py`

Full Usage:
```
> python main.py --help

usage: main.py [-h] [--project_name PROJECT_NAME] [--output_file OUTPUT_FILE] [--created_after CREATED_AFTER] [--created_before CREATED_BEFORE]`

options:
  -h, --help            show this help message and exit
  --project_name PROJECT_NAME
  --output_file OUTPUT_FILE
  --created_after CREATED_AFTER
  --created_before CREATED_BEFORE
```

# Output and Results on Sample Images

## Tasks

<details>
<summary>5f127f6f26831d0010e985e5</summary>

The quality checks did not return any problematic annotations here. 

Upon visual inspection the annotations are pretty good. `information_sign` `d768` overlaps the bounding box for `b60b` and would benefit from a programmatic check of total overlap by other bounding boxes as opposed to the intersection over union check this project implements to ensure that either `d768` or `b60b` is marked at least partially occluded.
  
  [View Audit](https://dashboard.scale.com/audit?taskId=5f127f6f26831d0010e985e5)

  ```
        {
            "task_id": "5f127f6f26831d0010e985e5",
            "annotations": []
        },
  ```
</details>

<details>
<summary>5f127f6c3a6b1000172320ad</summary>

The quality checks did not return any problematic annotations here. 

Upon visual inspection the annotions seem solid.
  
  [View Audit](https://dashboard.scale.com/audit?taskId=5f127f6c3a6b1000172320ad)
  ```
        {
            "task_id": "5f127f6c3a6b1000172320ad",
            "annotations": []
        },
  ```
</details>

<details>
<summary>5f127f699740b80017f9b170</summary>

The quality checks identify 3 Annotations as too dim, and 1 Annotation as too bright, and marks them as warnings.

Upon visual inspection, it does appear that the majority of the Annotations are either too dim or too bright, enough so as to question if there should be Annotations there at all. `4d8c`, `5533`, and `802a` are all marked correctly marked as dim, and `da64` is correctly marked as too bright. `1000` is also probably too dim but the brightness exceeds that of the current threshold set for the quality check.

  [View Audit](https://dashboard.scale.com/audit?taskId=5f127f699740b80017f9b170)
  ```
        {
            "task_id": "5f127f699740b80017f9b170",
            "annotations": [
                {
                    "uuid": "da493933-bb23-4179-a3ce-16c2b8b14d8c",
                    "label": "traffic_control_sign",
                    "error_level": 1,
                    "error_messages": [
                        "Color too dark Brightness: 42.256518082422204"
                    ]
                },
                {
                    "uuid": "15e7ee7c-ae01-434d-a0b7-54d4403d5533",
                    "label": "traffic_control_sign",
                    "error_level": 1,
                    "error_messages": [
                        "Color too dark Brightness: 48.506578947368425"
                    ]
                },
                {
                    "uuid": "2b0b1670-30be-4573-9fa3-c1aa9b51802a",
                    "label": "traffic_control_sign",
                    "error_level": 1,
                    "error_messages": [
                        "Color too dark Brightness: 60.498005982053826"
                    ]
                },
                {
                    "uuid": "0fd6b443-d9e2-4d7d-af67-968cc78bda6f",
                    "label": "policy_sign",
                    "error_level": 1,
                    "error_messages": [
                        "Color too bright Brightness: 746.674074074074"
                    ]
                }
            ]
        },
  ```
</details>

<details>
<summary>5f127f671ab28b001762c204</summary>

The quality checks identify 6 annotations as potential duplicates with very high intersection over union values and marked them as errors.

Upon visual inspection, the 6 identified annotations are indeed duplicates of each other, all identifying the same `Montgomery Post` `information_sign`. The rest of the annotations look solid, with the exception of the ommission of a couple `traffic_control_sign`s.

  [View Audit](https://dashboard.scale.com/audit?taskId=5f127f671ab28b001762c204)
  ```
            "task_id": "5f127f671ab28b001762c204",
            "annotations": [
                {
                    "uuid": "b80eb8aa-4d3d-4a8c-b581-3f4eb6c018e3",
                    "label": "information_sign",
                    "error_level": 2,
                    "error_messages": [
                        "Duplicate boxes between b80eb8aa-4d3d-4a8c-b581-3f4eb6c018e3 and 0d5d4005-3d0e-435e-84f1-83cfae9aaeed (Overlap: 0.963302731513977)",
                        "Duplicate boxes between b80eb8aa-4d3d-4a8c-b581-3f4eb6c018e3 and c2cbfd02-b009-4990-ac7c-f01cc20f39c5 (Overlap: 0.9814814925193787)",
                        "Duplicate boxes between b80eb8aa-4d3d-4a8c-b581-3f4eb6c018e3 and 4acb81c7-5f06-4784-8a22-63a8b7800162 (Overlap: 0.9279279112815857)",
                        "Duplicate boxes between b80eb8aa-4d3d-4a8c-b581-3f4eb6c018e3 and 24962795-80a8-469b-a758-3351e5ac9a87 (Overlap: 0.9814814925193787)",
                        "Duplicate boxes between b80eb8aa-4d3d-4a8c-b581-3f4eb6c018e3 and 622c4b74-eb64-4109-8608-600b1bc079b7 (Overlap: 0.9631312489509583)"
                    ]
                },
                {
                    "uuid": "0d5d4005-3d0e-435e-84f1-83cfae9aaeed",
                    "label": "information_sign",
                    "error_level": 2,
                    "error_messages": [
                        "Duplicate boxes between 0d5d4005-3d0e-435e-84f1-83cfae9aaeed and b80eb8aa-4d3d-4a8c-b581-3f4eb6c018e3 (Overlap: 0.963302731513977)",
                        "Duplicate boxes between 0d5d4005-3d0e-435e-84f1-83cfae9aaeed and c2cbfd02-b009-4990-ac7c-f01cc20f39c5 (Overlap: 0.9814814925193787)",
                        "Duplicate boxes between 0d5d4005-3d0e-435e-84f1-83cfae9aaeed and 4acb81c7-5f06-4784-8a22-63a8b7800162 (Overlap: 0.9626168012619019)",
                        "Duplicate boxes between 0d5d4005-3d0e-435e-84f1-83cfae9aaeed and 24962795-80a8-469b-a758-3351e5ac9a87 (Overlap: 0.9814814925193787)",
                        "Duplicate boxes between 0d5d4005-3d0e-435e-84f1-83cfae9aaeed and 622c4b74-eb64-4109-8608-600b1bc079b7 (Overlap: 0.9631312489509583)"
                    ]
                },
                {
                    "uuid": "c2cbfd02-b009-4990-ac7c-f01cc20f39c5",
                    "label": "information_sign",
                    "error_level": 2,
                    "error_messages": [
                        "Duplicate boxes between c2cbfd02-b009-4990-ac7c-f01cc20f39c5 and b80eb8aa-4d3d-4a8c-b581-3f4eb6c018e3 (Overlap: 0.9814814925193787)",
                        "Duplicate boxes between c2cbfd02-b009-4990-ac7c-f01cc20f39c5 and 0d5d4005-3d0e-435e-84f1-83cfae9aaeed (Overlap: 0.9814814925193787)",
                        "Duplicate boxes between c2cbfd02-b009-4990-ac7c-f01cc20f39c5 and 4acb81c7-5f06-4784-8a22-63a8b7800162 (Overlap: 0.945117712020874)",
                        "Duplicate boxes between c2cbfd02-b009-4990-ac7c-f01cc20f39c5 and 24962795-80a8-469b-a758-3351e5ac9a87 (Overlap: 1.0)",
                        "Duplicate boxes between c2cbfd02-b009-4990-ac7c-f01cc20f39c5 and 622c4b74-eb64-4109-8608-600b1bc079b7 (Overlap: 0.9811320900917053)"
                    ]
                },
                {
                    "uuid": "4acb81c7-5f06-4784-8a22-63a8b7800162",
                    "label": "information_sign",
                    "error_level": 2,
                    "error_messages": [
                        "Duplicate boxes between 4acb81c7-5f06-4784-8a22-63a8b7800162 and b80eb8aa-4d3d-4a8c-b581-3f4eb6c018e3 (Overlap: 0.9279279112815857)",
                        "Duplicate boxes between 4acb81c7-5f06-4784-8a22-63a8b7800162 and 0d5d4005-3d0e-435e-84f1-83cfae9aaeed (Overlap: 0.9626168012619019)",
                        "Duplicate boxes between 4acb81c7-5f06-4784-8a22-63a8b7800162 and c2cbfd02-b009-4990-ac7c-f01cc20f39c5 (Overlap: 0.945117712020874)",
                        "Duplicate boxes between 4acb81c7-5f06-4784-8a22-63a8b7800162 and 24962795-80a8-469b-a758-3351e5ac9a87 (Overlap: 0.945117712020874)",
                        "Duplicate boxes between 4acb81c7-5f06-4784-8a22-63a8b7800162 and 622c4b74-eb64-4109-8608-600b1bc079b7 (Overlap: 0.9631312489509583)"
                    ]
                },
                {
                    "uuid": "24962795-80a8-469b-a758-3351e5ac9a87",
                    "label": "information_sign",
                    "error_level": 2,
                    "error_messages": [
                        "Duplicate boxes between 24962795-80a8-469b-a758-3351e5ac9a87 and b80eb8aa-4d3d-4a8c-b581-3f4eb6c018e3 (Overlap: 0.9814814925193787)",
                        "Duplicate boxes between 24962795-80a8-469b-a758-3351e5ac9a87 and 0d5d4005-3d0e-435e-84f1-83cfae9aaeed (Overlap: 0.9814814925193787)",
                        "Duplicate boxes between 24962795-80a8-469b-a758-3351e5ac9a87 and c2cbfd02-b009-4990-ac7c-f01cc20f39c5 (Overlap: 1.0)",
                        "Duplicate boxes between 24962795-80a8-469b-a758-3351e5ac9a87 and 4acb81c7-5f06-4784-8a22-63a8b7800162 (Overlap: 0.945117712020874)",
                        "Duplicate boxes between 24962795-80a8-469b-a758-3351e5ac9a87 and 622c4b74-eb64-4109-8608-600b1bc079b7 (Overlap: 0.9811320900917053)"
                    ]
                },
                {
                    "uuid": "622c4b74-eb64-4109-8608-600b1bc079b7",
                    "label": "information_sign",
                    "error_level": 2,
                    "error_messages": [
                        "Duplicate boxes between 622c4b74-eb64-4109-8608-600b1bc079b7 and b80eb8aa-4d3d-4a8c-b581-3f4eb6c018e3 (Overlap: 0.9631312489509583)",
                        "Duplicate boxes between 622c4b74-eb64-4109-8608-600b1bc079b7 and 0d5d4005-3d0e-435e-84f1-83cfae9aaeed (Overlap: 0.9631312489509583)",
                        "Duplicate boxes between 622c4b74-eb64-4109-8608-600b1bc079b7 and c2cbfd02-b009-4990-ac7c-f01cc20f39c5 (Overlap: 0.9811320900917053)",
                        "Duplicate boxes between 622c4b74-eb64-4109-8608-600b1bc079b7 and 4acb81c7-5f06-4784-8a22-63a8b7800162 (Overlap: 0.9631312489509583)",
                        "Duplicate boxes between 622c4b74-eb64-4109-8608-600b1bc079b7 and 24962795-80a8-469b-a758-3351e5ac9a87 (Overlap: 0.9811320900917053)"
                    ]
                }
            ]
        },
  ```
</details>

<details>
<summary>5f127f643a6b1000172320a5</summary>

The quality checks did not return any problematic annotations here. 

Upon visual inspection the annotions seem solid. There is a glaring omission of 2 `policy_sign` in the right foreground and a less visible sign in the right background on a light pole from the annotations.

  [View Audit](https://dashboard.scale.com/audit?taskId=5f127f643a6b1000172320a5)
  ```
        {
            "task_id": "5f127f643a6b1000172320a5",
            "annotations": []
        },
  ```
</details>

<details>
<summary>5f127f5f3a6b100017232099</summary>

The quality checks identify 1 `construction_sign` annotation with a color mismatch, and 1 annotation that's both too large relative to the full image as well as too low to the bottom of the image.

Upon visual inspection, `b54b` is correctly labeled as a `construction_sign`, but the bounding box includes the tree next to it, leading the quality check to identify the dominant color as a brown instead of an orange for a successful warning. `3687` is incorrectly labeling a street marking, which is correctly marked an error by the quality check checking lowest position of the annotation relative to the image. The rest of the annotations look solid, with the exception of a couple missed signs.

  [View Audit](https://dashboard.scale.com/audit?taskId=5f127f5f3a6b100017232099)
  ```
        {
            "task_id": "5f127f5f3a6b100017232099",
            "annotations": [
                {
                    "uuid": "478496a5-1d09-4d53-889a-ef56a561b54b",
                    "label": "construction_sign",
                    "error_level": 1,
                    "error_messages": [
                        "Label and color mismatch Label: construction_sign Color: [120.85358   93.744545  76.73831 ]"
                    ]
                },
                {
                    "uuid": "25e6e90c-7acb-4786-a0fb-ca7b10fc3687",
                    "label": "non_visible_face",
                    "error_level": 2,
                    "error_messages": [
                        "Size too large relative to image 0.7694117647058824",
                        "Position too low Label max: 850 Image threshold: 722.5"
                    ]
                }
            ]
        },
  ```
</details>

<details>
<summary>5f127f5ab1cb1300109e4ffc</summary>

The quality checks did not return any problematic annotations here. 

Upon visual inspection the annotions seem solid.

  [View Audit](https://dashboard.scale.com/audit?taskId=5f127f5ab1cb1300109e4ffc)
  ```
        {
            "task_id": "5f127f5ab1cb1300109e4ffc",
            "annotations": []
        },
  ```
</details>

<details>
<summary>5f127f55fdc4150010e37244</summary>

  [View Audit](https://dashboard.scale.com/audit?taskId=5f127f55fdc4150010e37244)
  ```
        {
            "task_id": "5f127f55fdc4150010e37244",
            "annotations": [
                {
                    "uuid": "ec8b8899-5d60-44c1-9919-fae2902d2705",
                    "label": "information_sign",
                    "error_level": 1,
                    "error_messages": [
                        "Color too bright Brightness: 681.3055555555555"
                    ]
                },
                {
                    "uuid": "97319a82-2635-4785-9589-ff7e0b67bf81",
                    "label": "traffic_control_sign",
                    "error_level": 2,
                    "error_messages": [
                        "Probably not legible Label: traffic_control_sign Size: 2.0, 2.0",
                        "Size too small 2.0, 2.0"
                    ]
                },
                {
                    "uuid": "31b6471b-0af3-4eb0-9923-57ca32972fde",
                    "label": "traffic_control_sign",
                    "error_level": 2,
                    "error_messages": [
                        "Probably not legible Label: traffic_control_sign Size: 2.0, 2.0",
                        "Size too small 2.0, 2.0"
                    ]
                },
                {
                    "uuid": "b43ba10e-0507-4eaf-ba67-c6fb49d6beca",
                    "label": "traffic_control_sign",
                    "error_level": 2,
                    "error_messages": [
                        "Probably not legible Label: traffic_control_sign Size: 2.0, 2.0",
                        "Size too small 2.0, 2.0"
                    ]
                },
                {
                    "uuid": "3d2d21c8-7c44-4c04-911b-168c22db6b48",
                    "label": "traffic_control_sign",
                    "error_level": 2,
                    "error_messages": [
                        "Probably not legible Label: traffic_control_sign Size: 2.0, 2.0",
                        "Size too small 2.0, 2.0"
                    ]
                },
                {
                    "uuid": "61f914e3-5699-4e7c-b3be-c9722b43c229",
                    "label": "traffic_control_sign",
                    "error_level": 2,
                    "error_messages": [
                        "Probably not legible Label: traffic_control_sign Size: 2.0, 2.0",
                        "Size too small 2.0, 2.0"
                    ]
                },
                {
                    "uuid": "17b437ad-168b-47c6-92de-3b308157ce0b",
                    "label": "traffic_control_sign",
                    "error_level": 2,
                    "error_messages": [
                        "Probably not legible Label: traffic_control_sign Size: 2.0, 2.0",
                        "Size too small 2.0, 2.0"
                    ]
                },
                {
                    "uuid": "5111c4d1-5f26-4860-a834-b3890ae5d362",
                    "label": "traffic_control_sign",
                    "error_level": 2,
                    "error_messages": [
                        "Probably not legible Label: traffic_control_sign Size: 2.0, 2.0",
                        "Size too small 2.0, 2.0"
                    ]
                }
            ]
        }
  ```
</details>

The full report can be found [here](sample/report.json)

# Reflections and Future Quality Checks

# Conclusion
