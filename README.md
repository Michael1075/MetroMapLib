![figure](figure.png)

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://choosealicense.com/licenses/mit/)

# MetroMapLib

MetroMapLib is a tool to config a metro map in format svg.

## Requirements

MetroMapLib runs on python 3.7. To install python requirements, run the following:
```sh
python -m pip install -r requirements.txt
```

**Standard libraries required**

> `argparse`  
> `concurrent`  
> `functools`  
> `importlib`  
> `json`  
> `operator`  
> `os`  
> `re`  
> `time`  
> `xml`

**Site-packages required** (Also listed in `requirements.txt`)

> `numpy` (1.18.0)

**Systems required**

> LaTeX  
> Google Chrome

## Using MetroMapLib

Before using, you may default the open mode of svg files to Google Chrome.

Try running the following:
```sh
python main.py
```
or the equivalent command:
```sh
python main.py -p Shanghai -s default_style
```

The darcula style is also available:
```sh
python main.py -s darcula_style
```

The metro map of Shanghai is a project that has been momentarily finished. It's also a good example to teach you how to use MetroMapLib.

## Create your own map

You can create your own map by creating a transcript of `template_file` folder. You may rename the transcript folder with its project name. If you've finished configuring `input.json` in the format required, run the following:
```sh
python main.py -p [your_project_name]
```

You can also create the metro logo in `metro_logo.svg` under the corresponding project file.

The file `default_style.py` under the project file keeps all parameters of the corresponding project. You can make a transcript and modify some parameters to change its style by running the following:
```sh
python main.py -p [your_project_name] -s [your_style_file_name]
```

The file `construct_json.py` is a tool to config json files, including `input.json` and `tex.json`. Among them `tex.json` stores the path data of tex. If you want to modify the json files under a specific project file, you can run the following:
```sh
python construct_json.py -p [your_project_name]
```

You may keep a transcript of your project file if necessary.

## License

Copyright (c) 2019-present Michael W, released under the MIT license.

## Thanks

Great thanks to those who have inspired me more or less during the production of this repository.

[@3b1b](https://github.com/3b1b)  
[@chinhoyoo](https://www.zhihu.com/people/liang-ren-you-shi-jie)
