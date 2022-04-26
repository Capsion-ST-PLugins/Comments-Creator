# -*- coding: utf-8 -*-
#
# @Author: CPS
# @email: 373704015@qq.com
# @Date: 2021-08-06 11:19:08.939442
# @Last Modified by: CPS
# @Last Modified time: 2021-08-06 11:16:54.145176
# @file_path "Z:\CPS\IDE\SublimeText\sublime_text_4113.21_win64_test\Data\Packages\testt_comments_creater\core"
# @Filename "settings.py"
# @Description: 功能描述
#

if ( __name__ == "__main__"):
    pass


import sublime
import sublime_plugin

PLUGIN_NAME = "testt_comments_creater"
SETTING_FILE = "testt.sublime-settings"


def get_floder_list() -> dict:
    print('执行： get_floder_list()')
    return {
        'user_path':os.path.join(sublime.packages_path(),'User'),
        'default_settings':os.path.join(sublime.packages_path(), PLUGIN_NAME, '.sublime', SETTING_FILE),
        'user_settings':os.path.join(sublime.packages_path(),'User', SETTING_FILE),
    }

