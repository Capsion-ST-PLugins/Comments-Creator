# -*- coding: utf-8 -*-
#
# @Author: CPS
# @email: 373704015@qq.com
# @Date: 2021-08-17 11:17:54.793679
# @Last Modified by: CPS
# @Last Modified time: 2021-08-17 11:17:54.793679
# @file_path "Z:\CPS\IDE\SublimeText\sublime_text_4113.21_win64_test\Data\Packages\testt_comments_creater\core"
# @Filename "test.py"
# @Description: 功能描述
#

def extract(params_list:list, reg_obj:list) -> list:
    result:list = []
    i = 0

    for index, each_param in enumerate(params_list):
        for reg_index, each_reg in enumerate(reg_obj):
            res = each_reg["reg"].findall(each_param)
            if not res or len(res) == 0: continue
            i+=1
            print(f'{index+1} 表达式{reg_index+1}:\t{each_param}\t>>>\t{res} [{len(res[0])}]')

            params_list[index] = ""

            result.append({
                "id":index,
                 "type":res[0][each_reg['type']] if 'type' in each_reg else "",
                 "name":res[0][each_reg['name']],
                 "context":res[0][each_reg['context']] if 'context' in each_reg else ""
            })
            break
    print()
    return result
