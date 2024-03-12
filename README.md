<div align="center"><h1>AutomatedDrugTesting&nbsp;<img src="https://img.shields.io/badge/python-v3.9+-red.svg" alt="Python">&nbsp;<img src="https://img.shields.io/badge/selenium-v4.8+-red.svg" alt="Selenium">&nbsp;<img src="https://img.shields.io/badge/pyautogui-v0.9+-red.svg" alt="Pyautogui"></h1></div> 
<div align="center">Web/App Automation techniques applied in drug design, testing and discovery</div>

## Introduction
In our modern world of Big Data, ever more, the necessity arises for "Natural Sciences" to capitalize the power of automation provided by computational technologies. These technologies encompass a range of tools designed to process large datasets, perform complex calculations, and simulate real-world phenomena. 

In drug testing, design, and discovery, these technologies enable researchers to sift through large chemical libraries, predict the interactions between molecules and biological targets, and identify potential side effects or efficacy issues early in the development process. 

The perpetual goal is to identify the processes that can be automated and exempt the human from tedious, repetitive tasks, thereby freeing up researchers to focus on the more creative and strategic aspects of their work.

## Problem
An acquaintance of mine, conducting research for her thesis, was given 911 compounds that can possibly interact with a given ligand

The above three phases (combined with the intermediate steps) require at least 10 minutes per compound if carried out by a human. So, for the total amount of the given compounds a human would need **at least** 9110 minutes (**152 hours** or 6.3 days) and antidepressant drugs -for sure-.

## Solution
The entire process described above can be automated using the scripts available in this repository. As a result, the 911 compounds can produce the desired outputs in **maximum 15 hours** without the presence of a human! Huge time saving and effort for the researcher.

### => Phase 1: Webina


## How to deploy
- `git clone` the current repository to your directory and enter it
- `pip install -r requirements.txt` to install the required packages
### => Phase 1: Webina
Write and execute the command in your (linux) terminal: `python webina.py`
>> Requirements: <br>

googlechrome driver installed at the path '/usr/local/bin/chromedriver' <br>
The folder structure must be the following: <br>
```
Project's Folder/
├── webina.py
├── 7RPZ_final.pdb
├── 7RPZ_KRAS_ligand.pdb
└── Testing_Compounds_Specs_Natural_Products/ (includes compounds with .sdf extension)
```

>> Directories made: <br>
```
Project's Folder/
├── webinaTXTOuputs: contains the output files of the webina execution with the same compound name and .txt extension
├── webinaPDBQTOuputs: contains the output files of the webina execution with the same compound name and .pdbqt extension
└── Downloads: temporary directory that holds the downloads of the website
```
                         
In order to insert the affinities to a database and extract an excel for compounds-affinities write and execute the command in your (linux) terminal: `python dataBase.py`
>> Requirements: <br>

The folder structure must be the following: <br>
```
Project's Folder/
├── dataBase.py
└── webinaTXTOutputs folder with the results of webina.py in .txt
```

>> Directories made: <br>

```
Project's Folder/
├── compounds.db file: contains database
└── affinities.xlsx: excel with compound names and best affinities
```

### => Phase 2: PyRx
Write and execute the command in your (windows) cmd: `python pyrx.py`
