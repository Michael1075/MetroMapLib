![figure](figure.png)

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://choosealicense.com/licenses/mit/)

# MetroMapLib

MetroMapLib is a tool to config a metro map in format svg.

## Requirements

MetroMapLib runs on python 3.7. To install python requirements, run the following:
```sh
python -m pip install -r requirements.txt
```

**Default package requirements**
> `concurrent`
> `functools`
> `hashlib`
> `inspect`
> `json`
> `operator`
> `os`
> `re`
> `time`
> `xml`

**Other package requirements** (Also listed in `requirements.txt`)
> `numpy` (1.17.4)
> `openpyxl` (3.0.2)

**System requirements**
> LaTeX
> Google Chrome

## Using MetroMapLib

Before using, you may default the open mode of svg files to Google Chrome.

Try running the following:
```sh
python main.py
```

Note, new tex files requires your GPU to run close to its full capacity by multithreading. However, if all tex are settled, the main process does not take long.

The file `maplib/parameters.py` keeps all parameters of the project. You can modify some to change the style whatever you like.

The file `json_tool.py` is a tool to config json files, which store path data of tex.

You can also create your own map by creating 2 excel files in the format required.

