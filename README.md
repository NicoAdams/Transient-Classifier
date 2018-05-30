# Transient-Classifier
Contextual classification of transients

Structure:
- data: Files related to training data
    - raw_data: Data that is NOT ready for training
    - process_data: Code for processing data in raw_data
    - training: Data files that are ready to be used for training
- Exploratory: If you don't know where to put something, put it here for now

## Setting up Anaconda Environment

Step 1: Install [Anaconda](https://www.anaconda.com/download/) for your operating system.  You want the python 3.6 version.

Step 2: Clone this repo.

Step 3: Navigate to the cloned repo and create the environment by running:
```bash
conda env create -f environment.yaml
```

Step 4: Activate the environment:
```bash
source activate TransClass
```
