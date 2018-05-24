# Transient-Classifier
Contextual classification of transients

Folders:
- create_catalog: For scripts used to gather + process our data
- data: Processed data, intended for use to train the classifiers
- exploratory: I created this to store files that are just experiments or that I don't know how to classify
- raw_data: Data downloaded off the internet (no pre-processing done)

## Setting up Anaconda Environment

Step 1: Install (Anaconda)[https://www.anaconda.com/download/] for your operating system.  You want the python 3.6 version.

Step 2: Clone this repo.

Step 3: Navigate to the cloned repo and create the environment by running:
```bash
conda env create -f environment.yaml
```

Step 4: Activate the environment:
```bash
source activate TransClass
```
