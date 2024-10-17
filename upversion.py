"""
该模块基于霞鹜文楷更新

"""

import os
import subprocess

from fontTools.ttLib import TTFont

WORK_PATH = os.getcwd()
# 设置字体转换工具到环境变量
FONT_MERGER_PATH = os.path.join(os.getcwd(), "Warcraft-Font-Merger")
os.environ["PATH"] = f"{FONT_MERGER_PATH}:" + os.environ["PATH"]
# 安装命令：https://formulae.brew.sh/formula/fontforge
FONTFORGE_PATH = os.path.join("/opt/homebrew/bin")
os.environ["PATH"] = f"{FONTFORGE_PATH}:" + os.environ["PATH"]


def convert_font(ttf_font_path: str, convert_font_path):
    """将合并后生成的 ttf 格式的字体转为其他格式

    Args:
        ttf_font_path: 合并后生成的ttf格式的字体所在路径
        convert_font_path: 其他格式的保存路径
    """
    convert_command = f'Open("{ttf_font_path}"); Generate("{convert_font_path}");'
    subprocess.run(
        [
            "fontforge",
            "-lang=ff",
            "-c",
            convert_command,
        ],
        check=True,
    )


def delete_font_info(font_path):
    """
    删除合并后的字体的所有信息。
    Args:
        font_path: 待删除信息的字体的路径。
    """
    font = TTFont(font_path)
    name_table = font["name"]
    name_table.names = []
    font.save(font_path)


FONT_NAME = "QiushuiShotai"
BRIGHT_NAME = "QiushuiShotaiBright"

UPDATE_VERSION = "1.501"
# pylint: disable=line-too-long
COPY_RIGHT = r"Copyright 2020 The Klee Project Authors (https://github.com/fontworks-fonts/Klee)\nCopyright 2021-2024 LXGW (https://github.com/lxgw/LxgwWenKai)\nCopyright 2022-now NoHeartPen (https://github.com/NoHeartPen/QiushuiShotai)"


def edit_font_info(old_font_path, new_font_path):
    """编辑合并生成的字体的相关信息

    Args:
        old_font_path: 合并生成的字体所在的路径，应为脚本当前所在的路径+字体名。
        new_font_path: 修改相关信息后保存的路径。
    """
    delete_font_info(old_font_path)
    font_name = FONT_NAME
    if BRIGHT_NAME in old_font_path:
        font_name = BRIGHT_NAME

    fontforge_command = f'Open("{old_font_path}"); SetFontNames("{font_name}", "{font_name}", "{font_name}","Regular","{COPY_RIGHT}","{UPDATE_VERSION}"); Save("{new_font_path}");'
    subprocess.run(
        [
            "fontforge",
            "-lang=ff",
            "-c",
            fontforge_command,
        ],
        check=True,
    )


def create_font(base_font_path, cjk_font, save_font):
    """基于基础字体生成对应的字体

    Args:
        base_font_path: 基础字体，也是优先显示字形的字体。
        cjk_font: 补充显示字体，当 base_font 不存在该字时，采用该字体的字形补全。
        save_font: 合并后的字体。
    """
    subprocess.run(["otfccdump", f"{base_font_path}", "-o", "base.otd"], check=True)
    subprocess.run(
        ["otfccdump", f"{cjk_font}", "-o", "cjk.otd"],
        check=True,
    )
    subprocess.run(
        [
            "merge-otd",
            "base.otd",
            "cjk.otd",
        ],
        check=True,
    )
    # 合并完的的文件先保存在当前工作路径，修改完相关信息后再保存到对应的路径下
    # 由于使用 FontForge 修改相关信息后，保存的字体文件大小会异常，所以之后会用 woff 格式重新生成 ttf
    font_name = FONT_NAME
    if BRIGHT_NAME in save_font:
        font_name = BRIGHT_NAME
    subprocess.run(
        ["otfccbuild", "base.otd", "-O2", "-o", f"{font_name}.{TTF_TYPE}"],
        check=True,
    )
    # 删除中间文件
    subprocess.run("rm *.otd", shell=True, check=True)
    # 修改合并后的字体的信息
    edit_font_info(f"{font_name}.{TTF_TYPE}", save_font)
    # 删除合并后的未修改信息的文件
    subprocess.run("rm *.ttf", shell=True, check=True)


def build_font_path(font_dir: str, font_name: str, font_type: str):
    """构造字体路径

    Args:
        font_dir: 字体所在的文件夹
        font_name: 字体名
        font_type: 字体类型

    Returns:
        字体路径
    """
    return os.path.join(font_dir, f"{font_name}.{font_type}")


def convert_ttf_to_other(ttf_font_path, font_dir, converted_font_name):
    """
    利用 ttf 格式生成其他格式的字体
    Args:
        ttf_font_path:
        font_dir: 生成的其他格式字体的保存路径
        converted_font_name: 生成的其他格式字体的名称。
    """
    woff2_font_path = build_font_path(font_dir, converted_font_name, "woff2")
    convert_font(ttf_font_path, woff2_font_path)

    woff_font_path = build_font_path(font_dir, converted_font_name, "woff")
    convert_font(ttf_font_path, woff_font_path)
    # 利用生成的 woff 格式字体重新生成 ttf 格式字体
    convert_font(woff_font_path, ttf_font_path)


# 基础字体所在的文件夹
BASE_FONT_DIR = os.path.join(WORK_PATH, "basefont")
KLEE_FILENAME = "KleeOne-SemiBold.ttf"
BASE_KLEE_PATH = os.path.join(BASE_FONT_DIR, KLEE_FILENAME)
# Bright 的基础字体
BRIGHT_KLEE_NAME = "KleeOne-SemiBold-Ysabeau-Regular.ttf"
BASE_BRIGHT_KLEE_PATH = os.path.join(BASE_FONT_DIR, KLEE_FILENAME)
# 补全中文字形的字体
LXGW_FILE_NAME = "LXGWWenKai-Regular.ttf"
BASE_LXGW_PATH = os.path.join(BASE_FONT_DIR, LXGW_FILE_NAME)

TTF_TYPE = "ttf"

FONT_DIR = os.path.join(WORK_PATH, "QiushuiShotai")
BRIGHT_DIR = os.path.join(WORK_PATH, "QiushuiShotai Bright")

FONT_PATH = os.path.join(
    FONT_DIR,
    f"{FONT_NAME}.{TTF_TYPE}",
)

BRIGHT_PATH = os.path.join(
    BRIGHT_DIR,
    f"{BRIGHT_NAME}.{TTF_TYPE}",
)
# 生成 QiushuiShotai
create_font(BASE_KLEE_PATH, BASE_LXGW_PATH, FONT_PATH)
# 生成 QiushuiShotaiBright
create_font(BASE_BRIGHT_KLEE_PATH, BASE_LXGW_PATH, BRIGHT_PATH)
# 生成 ttf 以外的其他格式
convert_ttf_to_other(FONT_PATH, FONT_DIR, FONT_NAME)
convert_ttf_to_other(BRIGHT_PATH, BRIGHT_DIR, BRIGHT_NAME)
