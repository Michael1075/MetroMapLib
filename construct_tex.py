from maplib.tools.tex_file_tools import add_chn_tex
from maplib.tools.tex_file_tools import add_eng_tex
from maplib.tools.tex_file_tools import remove_chn_tex
from maplib.tools.tex_file_tools import remove_eng_tex


if __name__ == "__main__":
    remove_eng_tex("Morth Sichuan Road")
    #add_eng_tex("North Sichuan Road")
    remove_eng_tex("Guiyuanwu Road")
    #add_eng_tex("Jinyuanwu Road")
    remove_eng_tex("Yuansheng Stadium")
    add_eng_tex("Yuanshen Stadium")
