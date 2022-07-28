# -*- coding: utf-8 -*-
#
# @Author: CPS
# @email: 373704015@qq.com
# @Date: 2022-07-28 22:39:59.807307
# @Last Modified by: CPS
# @Last Modified time: 2022-07-28 22:39:59.807307
# @file_path "D:\CPS\IDE\JS_SublmieText\Data\Packages\testt"
# @Filename "helper.py"
# @Description: 功能描述
#

import sublime


def get_currt_coords(view: sublime.View) -> str:
    currt_cursor = view.sel()[0].a
    curt_line: sublime.Region = view.full_line(currt_cursor)
    line_content: str = view.substr(curt_line)
    return line_content


def has_selection(view: sublime.View) -> bool:
    """
    判断当前是否存在选区
    """
    if view.sel()[0].empty():
        return False
    return True


def get_currt_region_full_lines(view: sublime.View) -> sublime.Region:
    """
    获取所选区域内，每行的完整内容

    - param view :{sublime.View} {description}

    @returns `{ str}` {description}

    """
    if not has_selection(view):
        return ""

    region = view.sel()[0]
    full_lines_region = view.full_line(region)
    return full_lines_region

    # region_str = view.substr(full_lines_region)
    # return merge_line(region_str)


def merge_line(region_str: str) -> str:
    """
    将多行文本拼接成一行，首行的缩进保留，其他缩进替换成一个空格

    - param region_str :{str} {description}

    @returns `{ str}` {description}

    """

    region_list = region_str.split("\n")
    line_list = [region_list[0]] + [each_line.strip() for each_line in region_list[1:]]

    return "\n".join(line_list).replace("\n", " ")
