# -*- coding: utf-8 -*-
#
# @Author: CPS
# @email: 373704015@qq.com
# @Date:
# @Last Modified by: CPS
# @Last Modified time: 2021-04-12 03:25:48.660601
# @file_path "D:\CPS\IDE\JS_SublmieText\Data\Packages\CPS"
# @Filename "main.py"
# @Description: 功能描述
#

from typing import Optional, Tuple, Union, NewType
import sublime
import sublime_plugin
import os

from imp import reload

if int(sublime.version()) < 3176:
    raise ImportWarning("本插件不支持当前版本，请使用大于等于3176的sublime Text")

from .core import utils
from .core import comments_creator
from .core import helper

DEBUG = 0
PLUGIN_NAME = "cps_comments_creator"
DEFAULT_SETTINGS = "cps.sublime-settings"
SETTINGS = {}
FOLDER_LIST = None

resLineTuple = NewType("tuple(currt_line:Region, currt_contents:str)", tuple)


def log(*args):
    global DEBUG
    if DEBUG:
        print(*args)


def get_floder_list() -> dict:
    return {
        "user_path": os.path.join(sublime.packages_path(), "User"),
        "default_settings": os.path.join(
            sublime.packages_path(), __package__, ".sublime", DEFAULT_SETTINGS
        ),
        "user_settings": os.path.join(
            sublime.packages_path(), "User", DEFAULT_SETTINGS
        ),
    }


def plugin_loaded():
    global FOLDER_LIST
    FOLDER_LIST = get_floder_list()
    reload(comments_creator)

    print(f"{PLUGIN_NAME} on loaded")

    def plugin_loaded_async():
        """
        @Description 监听用户配置文件
        """
        global SETTINGS, FOLDER_LIST
        if not FOLDER_LIST:
            return

        with open(FOLDER_LIST["default_settings"], "r", encoding="utf8") as f:
            SETTINGS = sublime.decode_value(f.read()).get(PLUGIN_NAME, {})
            if len(list(SETTINGS.keys())) == 0:
                raise Exception(
                    "读取配置失败 ~~~ 请确保一下文件真实存在： ", FOLDER_LIST["default_settings"]
                )
            # log('读取settings: ', SETTINGS.keys())

        user_settings = sublime.load_settings(DEFAULT_SETTINGS)
        utils.recursive_update(SETTINGS, user_settings.to_dict()[PLUGIN_NAME])
        user_settings.add_on_change(DEFAULT_SETTINGS, _on_settings_change)

    def _on_settings_change() -> None:
        global SETTINGS

        tmp = sublime.load_settings(DEFAULT_SETTINGS).get(PLUGIN_NAME, False)

        if not tmp or not isinstance(tmp, dict):
            return

        utils.recursive_update(SETTINGS, tmp)

        log(f"{DEFAULT_SETTINGS} 触发更新。")
        return

    # 在另一个进程执行该函数( 这样不会阻塞窗口的初始化，造成载入文件卡顿 )
    sublime.set_timeout_async(plugin_loaded_async)


class CpsCommentsCreatorReloadCommand(sublime_plugin.TextCommand):
    def run(self, edit) -> None:
        reload(comments_creator)
        print(f"comments_creator reloaded")


class CpsCommentsCreatorEditSettingCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit):
        global FOLDER_LIST

        if not FOLDER_LIST:
            return

        sublime.active_window().run_command(
            "edit_settings",
            {
                "base_file": f'{FOLDER_LIST["default_settings"]}',
                "default": '{\n  "comments_creater_options":{\n    /*请在插件名称内选项内添加自定义配置*/\n    \n  }\n}',
            },
        )


class CpsCommentsCreatorCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit):
        view = self.view

        # 获取配置
        global SETTINGS
        options = SETTINGS

        # 根据文件后缀名，配置对应的解析函数
        # 为了处理带多个.的文件名，使用切片反方向获取
        name, syntax = os.path.basename(view.file_name()).split(".")[-2:]
        if not syntax or not syntax in comments_creator.PARSER:
            return log("{}:: >>> 不支持的语法{}".format(PLUGIN_NAME, syntax))

        # 默认模板兜底，使用用户模版更新
        syntax_tmpl = options["default_tmpl"]
        if syntax in options:
            utils.recursive_update(syntax_tmpl, options[syntax])

        # 需要查找的字符串，整行进行匹配
        currt_region, currt_line_contents = self.get_currt_line_str()

        # 定义新注释的插入方向
        # py 是下方
        # js之类的是上方
        insert_direction: str = syntax_tmpl.get(
            "comments_direction", None
        ) or options.get("comments_direction")

        if insert_direction == "down":
            insert_position = currt_region
            indent_offset = 1
        else:
            insert_position = self.get_pre_line_region(currt_region)
            indent_offset = 0

        # 查找是否有旧的注释块块
        comments_begin: str = syntax_tmpl["comments_header"][0]  # 注释块的头部标识
        comments_end: str = syntax_tmpl["comments_header"][-1]  # 注释快的尾部标识

        old_comments = self.search_old_comments(
            currt_region,
            comments_begin,
            comments_end,
            search_direction=insert_direction,
        )

        # log("old_comments: ", old_comments)

        # 匹配当前行
        # 实例化解释对象
        parser = comments_creator.PARSER[syntax]()
        if parser.match_line(currt_line_contents):
            # 如果存在旧的注释，尝试提取旧注释（旧注释内不能带空格，空格之后会被忽略）
            if old_comments:
                parser.set_old_comments(view.substr(old_comments))

            # 更新数据到注释模版内
            parser.format(syntax_tmpl)

            if old_comments:
                view.replace(edit, old_comments, parser.output_str)
            else:
                view.insert(edit, insert_position.b, parser.output_str)
        else:

            # 获取当前缩进类型
            currt_str = currt_line_contents
            indent = " " if view.settings().get("tab_size", None) else "\t"
            indent = (len(currt_str) - len(currt_str.lstrip())) * indent
            comments_str = "".join(
                [f"{indent}{line}\n" for line in syntax_tmpl["comments_header"]]
            )

            view.insert(edit, currt_region.a, comments_str.replace("\n\n", "\n"))

    def get_currt_line_str(self) -> resLineTuple:
        """
        返回要查找的行的具体信息

        @returns `{currt_region:Region}` 查找行的选区
        @returns `{currt_contents:str}` 要查找行的文本内容（完整）

        """
        view = self.view
        if helper.has_selection(view):
            currt_region = helper.get_currt_region_full_lines(view)
            currt_region_content = view.substr(currt_region)

            # 根据最下方的坐标，获取注释最终插入的位置
            # 选择多行的情况下，无法正确的识别最后一行的位置
            # -1 确保多行中，最后一行位置的正确识别
            currt_cursor = (
                currt_region.a
                if currt_region.a > currt_region.b
                else currt_region.b - 1
            )
            currt_region = view.full_line(currt_cursor)
            currt_contents = helper.merge_line(currt_region_content)
        else:
            currt_cursor = view.sel()[0].a
            currt_region = view.full_line(currt_cursor)
            currt_contents = view.substr(currt_region)

        return (currt_region, currt_contents)

    # 获取现有注释模块的内容
    def search_old_comments(
        self,
        line_region: sublime.Region,
        comment_begin: str,
        comment_end: str,
        search_direction: str = "up",
    ) -> sublime.Region:
        """
        给定一行范围，从该行，向下或者向上开始查找是否存在旧的注释块

        - param line_region         :{sublime.Region} 开始查找的行
        - param comment_begin       :{str}            注释块的开始标识，（py：三个"或者三个'）|（js：/**）等
        - param comment_end         :{str}            注释块的结束标识，（py：三个"或者三个'）|（js：*/）等
        - param search_direction=up :{str}            'down'|'up'查找的方向

        @returns `{ sublime.Region}` (start:int，end:int1)

        """

        begin = comment_begin.strip()
        end = comment_end.strip()

        # 根据查找方向，给定开始查找的行
        if search_direction == "down":
            # 获取下一行的位置
            find_region = self.get_next_line_region(line_region)
        else:
            # 获取前一行的位置
            find_region = self.get_pre_line_region(line_region)

        # 查找注释头标识： begin
        find_begin = self.find_str_by_line_region(
            find_region, begin, max_search_count=1, direction=search_direction
        )

        if not find_begin:
            return False

        # 查找注释尾标识： end
        find_region = self.get_next_line_region(find_begin)
        find_end = self.find_str_by_line_region(
            find_region, end, max_search_count=30, direction="down"
        )
        # log("find_end: ", find_end)
        if not find_end:
            return False

        return sublime.Region(find_begin.a, find_end.b)

    def find_str_by_line_region(
        self,
        line_region: sublime.Region,
        find_str: str,
        max_search_count: int = 1,
        direction: str = "up",
    ) -> Optional[str]:
        """
        @Description 查找一个字符串，并返回其所在的位置1

        - param line_region        :{sublime.Region} 查找开始的位置
        - param find_str           :{str}            要查找的字符串
        - param max_search_count=1 :{int}            查找多少行，默认1
        - param direction=up       :{str}            查找的方向，一般js，ts往上，py往下等等


        """
        view = self.view
        search_count = 1
        while search_count <= max_search_count:
            currt_str = view.substr(line_region).strip()
            log("查找： ", currt_str)

            if currt_str.find(find_str) == 0:
                # log('找到： ', find_str, '>>>>> 返回 ', line_region)
                # 返回当前行尾
                return line_region
            else:
                if direction == "up":
                    # 向上查找
                    line_region = view.full_line(line_region.a - 1)
                else:
                    # 向下查找
                    line_region = view.full_line(line_region.b + 1)

            search_count += 1
        return False

    def get_next_line_region(self, line_region: sublime.Region) -> sublime.Region:
        """
        @Description 获取下一行Region

        - param line_region :{sublime.Region} sublime.Region是一个一维二元数组

        """
        return self.view.full_line(line_region.b + 1)

    def get_pre_line_region(self, line_region: sublime.Region) -> sublime.Region:
        """
        @Description 获取上一行Region

        - param line_region :{sublime.Region} sublime.Region是一个一维二元数组

        """
        return self.view.full_line(line_region.a - 1)
