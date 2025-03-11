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
1. A set of completed tasks associated with a `project_name` are downloaded utilizing the Scale API
2. Data from each Task is used to create a Task object, with associated Annotations created as well
3. The source image related to the Task is downloaded
4. A set of quality checks are performed on each Task, both analyzing individual Annotations as well as the full set of Annotations for a Task
5. A JSON report is saved to disk listing Annotations for each Task that have been flagged with `WARNING`s or `ERROR`s, along with the associated error messages

# Quality Checks Implemented

The quality checks implemented fall under a few broad categories which are detailed here

## Basic Annotation Validity

These are a basic sanity check on the data present in each Annotation. These checks ensure that the data is well-formed and valid. They may be a bit overkill because the data is being pulled from Scale's servers, but it never hurts to check again. Failing any of these checks results in the Annotation being tagged as an `ERROR`.

1. All mandatory data exists for an Annotation (`left`, `top`, `width`, `height`, `label`, `occlusion`, `truncation`, `background_color`)
2. All Annotation enumerized data is marked with available values
3. Annotation bounding boxes do not exceed image canvas
4. Annotations labeled `non_visible_face` must have a `background_color` of `non_applicable`
   
## Size Heuristics

These checks identify potential errors related to the size of the Annotation as well as truncation. The size of an annotation itself or when compared to the source iamge can provide powerful indications of potential problems.

1. Annotations with any dimension of `0 ` are disallowed despite being allowed in the Task parameters (`ERROR`)
2. Annotations with a `truncation` of `100%` are disallowed as they would be fully invisible (`ERROR`)
3. Annotations that are very small (< `SIZE_MIN_SIZE_WARNING`) with no truncation (`0%`) that are not labeled `non_visible_face` are flagged, as it's unlikely the labeler would be able to dtermine the type of sign (`WARNING`)
4. Annotations that are very small (<`SIZE_MIN_SIZE_WARNING`) and not mostly truncated (`75%`) are flagged (`ERRROR`)
5. Annotations that are too large relative to the source iamge size (`SIZE_RATIO_WARNING_THRESHOLD`) in either dimension are flagged, as it's unlikely a sign would dominate the view from within a vehicle (`ERROR`)
6. Annotations with very extreme aspect ratios (`ASPECT_RATIO_WARNING_THRESHOLD`) without very high truncation are flagged, as they are unlikely to exist (`WARNING`)

## Position Heuristics

This check makes a prior assumption that no sign will extend into the bottom section of the image, as this would be directly in front of the vehicle. This also covers some instances of painted streets being annotated, as that is explictly disallowed in the specifications.

1. If the lower position of the Annotation extends within `POSITION_LOWER_WARNING_THRESHOLD`% of the source image, this annotation is flagged (`WARNING`)

## Color Heuristics

These checks attempt to look at the colors within the cropped iamge of the Annotation to flag potential illegible signs, as well as sanity check colors for certain labels.

1. If the average color of the Annotation is too dim or too bright to likely be legible, it is flagged (`WARNING`)
2. If the Annotation is labeled as a `construction_sign` and the dominant color is not some shade of orange, it is flagged (`WARNING`)

## Bounding Box Heuristics

These checks look at bounding box interactions between Annotations within a Task to determine if there is any duplication.

1. If intersection over union is very high (`BOUNDING_BOX_IOU_DUPLICATE_WARNING_THRESHOLD`) between two Annotations, both Annotations are flagged (`ERROR`)
2. If intersection over union is moderate (`BOUNDING_BOX_IOU_OVERLAP_WARNING_THRESHOLD`) between two Annotations, both Annotations are flagged (`WARNING`)

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

The quality checks identify 7 annotations that very small and are probably too small to be legible to label correctly. They also identify 1 annotation that appears to be too bright.

Upon visual inspection, `2705` is a false positive for being identified as too bright. The annotation actually has an incorrectly large bounding box, but the extra area is actually dimmer than the sign itself, which is white. This may indicate that the brightness threshold needs to be increased for determining bright annotation warnings. The 7 annotations identified as too small are indeed too small to discern if any sign exists, and look to either be user misclicks or deliberate attempts to add extra annotations. The rest of the annotations appear correct.

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

# Improvements and Future Quality Checks

This project was implemented in a timeboxed environment so the implemented heuristics strongly favored effectiveness achievable with a limited implementation time. Given more time for thought and implementation, a numbner of imrprovements and new quality checks could be added to greatly increase the effectiveness in identifying potentially problematic Annotations.

## Improvements

1. Fix the implementation for the bounding box checks to optimize for runtime efficiency. The current check runs in O(n^2) time which will bog down in production environments. Switching to a quad tree algorithm should decrease the average runtime to O(n log n).
2. Expand the use of color-based heuristics. The current checks are simplistic and a deeper exploration into using all of the dominant colors as well as their percentages to validate Annotation label types seems likely to increase effectiveness. More sophisticated calculations to determine brightness rather than simply summing up the RGB values will likely increase effectiveness as well. `background_color` could also be verified programmatically.
3. Reccomment that **ObserveSign** modify their specification to either add a new label for illegible signs, or modify the criteria for `non_visible_face` to include illegible signs. Currently it appears some labelers are using a sign is too illegible to determine a label, even though the sign may not necessarily be presenting a `non_visible_face` as defined in the current specifications.
4. Increase the flexibilty and modularity of the existing script. Allow users to select which checks they'd like to run, and override constants if desired. Move potentially unneeded calculations to when the particular test requiring the calcuations are run so they're not running unnecessarily if the test is disabled by the user.

## Future Quality Checks

1. Add overlapping bounding box checks in addition to intersection over union checks. Annotations with a high percentage of overlap are likely either occluding or being occluded by another sign, so a higher `occlusion` should be checked in these cases.
2. Perform simplistic shape detection within the image crop of an Annotation. Some labels (especially `traffic_control_sign`) correlate strongly to particular sign shapes so this potentially could add a lot of signal to checking Annotation correctness.
   - Using shape detection seems like a likely candidate to identify traffic lights due to their unique shape arrangement, which would allow checks to ensure `background_color` is properly labeled as `other` when a sign is likely a traffic light.
   - Box detection resulting from shape detection could allow Annotations to be checked for potentially grouped signs, which is another edge case excplitly disallowed in the specifications.
3. Perform OCR on the image crops of Annotations. Many signs have a very standardized set of possible text (`STOP`, `YIELD`, `SPEED LIMIT`, etc) and identifying the words present in an Annotation would give a very strong signal in determining if the label is correct.
4. There may be some correlation between some sign types existing in a scene and the prescence or absence of other sign types. Exploring existing datasets may allow some predictability when evaluating the set of Annotations of a Task.
5. Explore ML-based approaches to either pre-labeling or verifying annotated images. Scale has a very large dataset of labeled, reliable autonomous vehicle image data which could be used to quickly build a classifier that conforms to the labels that **ObserveSign** is trying to label. Leveraging that dataset should provide a very quick way to efficiently provide automated quality checks on annotated images.

# Conclusion
