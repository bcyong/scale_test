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

[Full report](sample/report.json)

# Reflections and Future Quality Checks

# Conclusion
