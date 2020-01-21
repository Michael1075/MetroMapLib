from maplib.tools.json_file_tools import JsonTools


if __name__ == "__main__":
    tool = JsonTools()
    tool.format_input_json()
    tool.create_input_json_transcript("_copy")
    tool.modify_tex_json()
    tool.format_tex_json()
    tool.create_tex_json_transcript("_copy")
