from maplib.tools.tex_json_file_tools import create_transcript
from maplib.tools.tex_json_file_tools import init_json
from maplib.tools.tex_json_file_tools import modify_tex


if __name__ == "__main__":
    init_json()
    modify_tex()
    create_transcript("_copy")
