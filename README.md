# CDAK

## Description

Parses through Cathepsin D Assay Kinetics csv data and filters then transposes well groups in the following format, `<ABC 0.5 ug><ABC 1 ug><ABC 2 ug>`. Output goes to an output csv or stdout.

## Usage

```
usage: cdak.py [-h] [-c CONFIG_FILE] CSV

Cathepsin D Assay Kinetics data converter

positional arguments:
  CSV                   path to input csv file to parse

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        path to config file. Defaults to ./config.ini
```

- BLANK must be in the three upper right corner wells

- config.ini must be in this format:

```
# comments ignored, newlines ignored

'stdout' # print to stdout
0, 0 # trailing comments allowed
1, 0
2, 0
0, 3
1, 3
2, 3
0, 6
1, 6
2, 6

# 'stdout2' # print to stdout without overriding the previous stdout
# required syntax below:
1,9   # A, 0.5 ug
2,9   # B, 0.5 ug
3,9   # C, 0.5 ug

4,9   # A, 1 ug
5,9   # B, 1 ug
6,9   # C, 1 ug

6,0   # A, 2 ug
6,1   # B, 2 ug
6,2   # C, 2 ug

'pep.csv' # write to a file called pep.csv
None # None is an empty well and is ignored
None
None
None
None
None
7,0
7,1
7,2

```