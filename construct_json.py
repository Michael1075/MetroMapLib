from maplib.tools.json_file_tools import create_input_json_transcript
from maplib.tools.json_file_tools import create_tex_json_transcript
from maplib.tools.json_file_tools import format_input_json
from maplib.tools.json_file_tools import format_tex_json
from maplib.tools.json_file_tools import modify_tex_json


if __name__ == "__main__":
    format_input_json()
    create_input_json_transcript("_copy")
    format_tex_json()
    modify_tex_json()
    create_tex_json_transcript("_copy")
