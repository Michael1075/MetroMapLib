MetroMapLib is a tool to config a metro map in format SVG.

## Requirements
MetroMapLib runs on python 3.*. System requirements are just LaTeX. Default packages required are `copy, hashlib, inspect, openpyxl, os, re, time, xml`(`treadings` and `multiprocessing` may be required in the future). Other packages required are `numpy`.
PDF file can also be made if packages `reportlab` and `svglib` are installed.

## Using MetroMapLib
Run `python main.py` under the root file.
Note, it takes about 10 sec to write a tex file to an svg file, so if some tex are added, please wait patiently. There're 476 stations altogeter(up to now), so if the tex commands of the labels are changed, every 476 files take about 4000-5000 sec.
However, if all tex are settled, the main process only takes about 10 sec.

## View SVG
SVG is a short for Scalable Vector Graphics, which can be viewed simply in a chrome. Google Chrome is recommended.