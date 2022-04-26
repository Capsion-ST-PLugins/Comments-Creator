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


from typing import Pattern
import sublime
import sublime_plugin
import re, os
from imp import reload


if int(sublime.version()) < 3176:
    raise ImportWarning("本插件不支持当前版本，请使用大于等于3176的sublime Text")

from .core import utils
from .core import comments_creator

PLUGIN_NAME = __package__
SETTING_FILE = "testt.sublime-settings"
SETTINGS = {}

DEBUG = 1
def log(*args):
    global DEBUG
    if DEBUG:print(*args)

def get_floder_list() -> dict:
    return {
        'user_path':os.path.join(sublime.packages_path(),'User'),
        'default_settings':os.path.join(sublime.packages_path(), PLUGIN_NAME, '.sublime', SETTING_FILE),
        'user_settings':os.path.join(sublime.packages_path(),'User', SETTING_FILE),
    }

def plugin_loaded():
    global FOLDER_LIST
    FOLDER_LIST = get_floder_list()

    def plugin_loaded_async():
        global SETTINGS
        with open(FOLDER_LIST['default_settings'], 'r', encoding='utf8') as f:
            SETTINGS = sublime.decode_value(f.read()).get(PLUGIN_NAME, {})
            if len(list(SETTINGS.keys())) == 0:
                raise Exception('读取配置失败 ~~~ 请确保一下文件真实存在： ', FOLDER_LIST['default_settings'])
            # log('读取settings 1: ', SETTINGS.keys())

        user_settings = sublime.load_settings(SETTING_FILE)
        utils.recursive_update(SETTINGS, user_settings.to_dict()[PLUGIN_NAME])
        user_settings.add_on_change(SETTING_FILE, _on_settings_change)

    def _on_settings_change() -> None:
        global SETTINGS
        
        tmp = sublime.load_settings(SETTING_FILE).get(PLUGIN_NAME, False)

        if not tmp or not isinstance(tmp, dict): return

        utils.recursive_update(SETTINGS, tmp)

        log(f'{SETTING_FILE} 触发更新。')
        return
    
    # 在另一个进程执行该函数( 这样不会阻塞窗口的初始化，造成载入文件卡顿 )
    sublime.set_timeout_async(plugin_loaded_async)

def get_currt_line_str(line):
    log('get_currt_line_str: >>> ')
    return sublime.View.substr(line).strip()


class TesttCommentsCreatorReloadCommand(sublime_plugin.TextCommand):
    def run(self, edit) -> None:
        log(f'重新加载 {__package__}')
        reload(comments_creator)





class TesttCommentsCreatorCommand(sublime_plugin.TextCommand):
    def run(self, edit:sublime.Edit):
        view = self.view

        # 获取配置
        global SETTINGS
        options = SETTINGS

        # 根据文件后缀名，配置对应的解析函数
        # 为了处理带多个.的文件名，使用切片反方向获取
        name, syntax = os.path.basename(view.file_name()).split('.')[-2:]
        if not syntax or not syntax in comments_creator.PARSER:
            return log('TesttCommentsCreatorCommand:: >>> 不支持的语法{}'.format(syntax))

        # 实例化解释对象
        parser = comments_creator.PARSER[syntax]()

        # 默认模板兜底，使用用户模版更新
        syntax_tmpl = options['default_tmpl']
        if syntax in options: 
            utils.recursive_update(syntax_tmpl, options[syntax])

        # 获取当前光标位置
        currt_cursor = view.sel()[0].a
        curt_line:sublime.Region = view.full_line(currt_cursor) # 获取当前所在行的内容
        log("curt_line: ", curt_line)
        log('currt_str: ', view.substr(curt_line))

        # 定义新注释的插入位置
        insert_offset:int = syntax_tmpl.get('insert_offset', 0) or options.get('insert_offset',-1)
        if insert_offset > 0:
            # 正数 在目标下一行插入
            insert_position = curt_line
        else:
            # 负数 在目标前一行插入
            insert_position = self.get_pre_line_region(curt_line)
        log('插入位置： ', insert_position)

        # 查找是否有旧的注释块块
        comments_begin:str = syntax_tmpl["comments_header"][0] # 注释块的头部标识
        comments_end:str = syntax_tmpl["comments_header"][-1]  # 注释快的尾部标识
        old_comments = self.search_old_comments(curt_line, comments_begin, comments_end, search_direction=insert_offset)

        # 需要查找的字符串，整行进行匹配
        match_str:str = view.substr(curt_line)
        log("match_str: ", match_str)

        # 匹配当前行
        if parser.match_line(match_str):
            # 如果存在旧的注释，尝试提取旧注释（旧注释内不能带空格，空格之后会被忽略）
            if old_comments:
                parser.set_old_comments(view.substr(old_comments))

            # 更新数据到注释模版内
            # parser.format_by_tmpl(syntax_tmpl)
            parser.format(syntax_tmpl)

            if old_comments:
                view.replace(edit, old_comments, parser.output_str)
            else:
                view.insert(edit, insert_position.b, parser.output_str)

    # 获取现有注释模块的内容
    def search_old_comments(self, line_region:sublime.Region, comment_begin:str, comment_end:str, search_direction:int=1) -> sublime.Region:
        view = self.view
        begin = comment_begin.strip()
        end = comment_end.strip()

        # 根据查找方向，给定开始查找的行
        if search_direction > 0:
            # 向下
            direction = "down"
            find_region = self.get_next_line_region(line_region)
        else:
            direction = 'up'
            find_region = self.get_pre_line_region(line_region)


        # 查找注释头标识： begin
        find_begin = self.find_str_by_line_region(find_region, begin, max_search_count=1, direction=direction)
        if not find_begin:return False

        # 查找注释尾标识： end
        find_region = self.get_next_line_region(find_begin)
        find_end = self.find_str_by_line_region(find_region, end, max_search_count=1, direction='down')
        if not find_end:return False

        # 返回返回
        return sublime.Region(find_begin.a, find_end.b)

    def find_str_by_line_region(self, line_region:sublime.Region, find_str:str, max_search_count:int=1, direction:str='up'):
        view = self.view
        search_count = 1
        while search_count <= max_search_count:
            currt_str = view.substr(line_region).strip()
            log('查找： ', currt_str)

            if currt_str.find(find_str) == 0:
                log('找到： ', find_str, '>>>>> 返回 ', line_region)
                # 返回当前行尾
                return line_region
            else:
                if direction =='up':
                    # 向上查找
                    line_region = view.full_line(line_region.a - 1)
                else:
                    # 向下查找
                    line_region = view.full_line(line_region.b + 1)

            search_count +=1
        return False

    # 获取下一行 region
    def get_next_line_region(self, line_region:sublime.Region) -> sublime.Region:
        return self.view.full_line(line_region.b + 1)

    # 获取上一行 region
    def get_pre_line_region(self, line_region:sublime.Region) -> sublime.Region:
        return self.view.full_line(line_region.a - 1)
