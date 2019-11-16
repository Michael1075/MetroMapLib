MetroMapLib is a tool to config a metro map in format SVG.


## Requirements

MetroMapLib runs on python 3.6. System requirements are just LaTeX. Other packages required are `numpy` and `openpyxl`. PDF file can also be made if packages `reportlab` and `svglib` are installed.

```sh
# Default packages required
copy, hashlib, inspect, multiprocessing, os, re, treading, time, xml
# Install python requirements
python -m pip install -r requirements.txt
```


## Using MetroMapLib

Run `python main.py` under the root file.
Note, it takes about 7 sec to write a tex file to an svg file, so if some tex are added, please wait patiently. There're 492 stations altogeter(up to now), so if the tex commands of the labels are changed, every 492 files take about 3500 sec.
However, if all tex are settled, the main process only takes about 10 sec.


## View SVG

SVG is a short for Scalable Vector Graphics, which can be viewed simply in a chrome. Google Chrome is recommended.