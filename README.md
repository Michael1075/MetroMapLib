# MetroMapLib

MetroMapLib is a tool to config a metro map in format SVG.


## Requirements

MetroMapLib runs on python 3.6. System requirements are just LaTeX. Other packages required are `numpy` and `openpyxl`. PDF file can also be made if packages `reportlab` and `svglib` are installed.

```sh
# Default packages required
concurrent
functools
hashlib
inspect
json
operator
os
re
time
xml

# Install python requirements
python -m pip install -r requirements.txt

# Run the following in case that the network is poor
python -m pip --default-timeout=1000 install -U -r requirements.txt
```


## Using MetroMapLib

Run `python main.py` under the root file.
Note, new tex files requires your GPU to run close to its full capacity by multithreading. However, if all tex are settled, the main process does not take long.
The file `json_tool.py` is a tool to config json files, which store path data of tex.


## View SVG

SVG is a short for Scalable Vector Graphics, which can be viewed simply in a chrome. Google Chrome is recommended.

