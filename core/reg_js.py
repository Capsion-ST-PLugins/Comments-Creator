# -*- coding: utf-8 -*-
#
# @Author: CPS
# @email: 373704015@qq.com
# @Date: 2021-08-18 01:03:11.867012
# @Last Modified by: CPS
# @Last Modified time: 2021-08-18 01:03:11.867012
# @file_path "D:\CPS\IDE\sublime Text\sublime_text_4113.21_win64_patched\sublime_text\Data\Packages\testt_comments_creater\core"
# @Filename "reg_js.py"
# @Description: 功能描述
#


import re
def create_reg_obj(reg, res_len:int, name:int, type:int=-1, context:int=-1 ) -> dict:
    """
    @Description 创建一个匹配模板，内含各个匹配结果后的含义

    - param reg     :{params} 正则表达式
    - param res_len :{int}    匹配成功后的正确长度
    - param name    :{int}    函数名|参数名
    - param type    :{int}    函数类型|参数类型
    - param context :{int}    默认参数

    returns `{dict}` 返回对应信息的索引位置
    ```python
    {
        "res_len":7,
        "name":3, # 函数名
        "return_type":6, # 返回的类型
        "params":5, # 参数的数量
        "indent":0  # 缩进数量
    }
    ```
    """
    if res_len <= 1:
        raise Exception("res_len 参数必须大于1，返回的结果需要二元tuple进行处理")

    res = {
        "reg":re.compile(reg),
        "name":name,
        "res_len":res_len
    }

    if context != -1:res['context'] = context
    if type != -1:res['type'] = type

    return res


int_reg = [
    create_reg_obj(r'^(\w+)\s*?:\s*?(number)\s*?\=\s*?(\-?\d+|0)$', 3, 0, 1, 2),
    create_reg_obj(r'^(\w+)\s*?\=\s*?(\-?\d+|0)$', 2, 0, context=1),
    create_reg_obj(r'^(\w+)\s*?:\s*?(number)$', 2, 0, 1),
]


str_reg = [
    create_reg_obj(r'(\w+)\s*?:(string)\s*?=\s*?(\'|\")(\w+)(\'|\")$', 5, 0, 1, 3),
    create_reg_obj(r'(\w+)\s*?\s*?\=\s*?(\'|\")(\w+)?(\'|\")$', 4, 0, context=2),
    create_reg_obj(r'(\w+)\s*?:(string)', 2, 0, type=1),
]

params_reg = [
    create_reg_obj(r'^(\w+|\*\*\w+|\*\w+)\s*?\:\s*?(\w+\.\w+|\w+\[\w+\.\w+|\w+|.*\]|\w+)\s*?\=\s*?(.*)$',3,0,1,2),
    create_reg_obj(r'^(\w+|\*\*\w+|\*\w+)\s*?\:\s*?(\w+\.\w+|\w+\[\w+\.\w+|\w+|.*\]|\w+)$',2,0,type=1),
    create_reg_obj(r'^(\w+|\*\*\w+|\*\w+)(\s*?)$',2,0), # 添加 (\s*?) 为了可以返回2元格式的结果
    create_reg_obj(r'^(\w+)\s?\=\s?(\w+)$', 2, 0, context=1),
]

func_reg = [
    {   # export const ifDirExists = async (filePath="") => { 处理有括号的
        "reg":re.compile(r'^(\s+)?(export\s)?(const\s|var\s|let\s)(\w+\s?)\=\s?(async\s?)?\((.*)\)\s?\:?(.*)?\s?\=>\s?\{?'),
        "res_len":7,
        "name":3, # 函数名
        "return_type":6, # 返回的类型
        "params":5,
        "indent":0
    },

    {   # export const ifDirExists = async filePath => { 处理无括号的
        "reg":re.compile(r'^(\s+)?(export\s)?(const\s|var\s|let\s)(\w+\s?)\=\s?(async\s?)?(.*)\s?\:?(.*)?\s?\=>\s?\{?'),
        "res_len":7,
        "name":3, # 函数名
        "return_type":6, # 返回的类型
        "params":5,
        "indent":0
    },

    {
        "reg":re.compile(r'^(\s+)?(exports\.)(\w+)\s?\=\s?(async\s)?(function)\s?\((.*)?\)\s?\:?\s?(\w+)?\s?\{'),
        "res_len":7,
        "name":2,
        "return_type":6,
        "params":5,
        "indent":0
    },
    {
        "reg":re.compile(r'^(\s+)?(export\s)?(async\s)?(function\s)?(\w+)\s?\((.*)?\)\s?\:?\s?(.*)?\s?\{'),
        "res_len":7,
        "name":4,
        "type":1,
        "return_type":6,
        "params":5,
        "indent":0
    },
    {
        "reg":re.compile(r'^(\s+|exports\.|\w+\.)(\w+\s?)\=\s?(async\s?)?\((.*)\)\s?(\:.*)?\s?\=>\s?\{?'),
        "res_len":5,
        "name":1,
        "type":1,
        "return_type":4,
        "params":3,
        "indent":0
    },
]

js_reg = {
    # 旧
    "func":func_reg,
    "string":str_reg,
    "number":int_reg,
    "params":params_reg,

    "checkType":{
        "func":func_reg,
        "param":params_reg,
        # "class":class_reg,
    },

    "paramType":{
        "string":str_reg,
        "number":int_reg,
        "params":params_reg, # 无类型参数
    },

    'except':{
        "param":[]
    }
}

def test_func(params_list:list, reg_obj:list) -> list:
    """
    @Description 测试函数

    - param params_list :{list} {description}
    - param reg_obj     :{list} {description}

    @returns `{list}` {description}

    """
    result:list = []
    i = 0

    for index, each_param in enumerate(params_list):
        for reg_index, each_reg in enumerate(reg_obj):
            res = each_reg["reg"].findall(each_param)
            if not res or len(res) == 0:
                print(f'【第{index}行】: ', each_param)
                continue
            else:
                i += 1
                params_list[index] = ""

                ret = { "id":index }
                for each in each_reg.keys():
                    if each in ['reg', 'res_len']:
                        continue
                    ret[each] = res[0][each_reg[each]]

                result.append(ret)
                print(f"【第{index}行】: ", ret)
            break

    return result

def test_params(params_list:list, reg_obj:list) -> list:

    result:list = []
    i = 0

    for index, each_param in enumerate(params_list):

        for reg_index, each_reg in enumerate(reg_obj):

            res = each_reg["reg"].findall(each_param)

            if not res or len(res) == 0: continue

            i+=1
            # print(f'{index+1} 表达式{reg_index+1}:\t{each_param}\t>>>\t{res} [{len(res[0])}]')
            # print(f'{index+1} 表达式{reg_index+1} {res[0][each_reg["name"]]}\t>>>\t 函数类型: [{res[0][each_reg["return_type"]] if "return_type" in each_reg else ""}]\t 函数参数:[{res[0][each_reg["params"]]}]')

            params_list[index] = ""
            result.append({
                "id":index,
                 "type":res[0][each_reg['type']] if 'type' in each_reg else "",
                 "name":res[0][each_reg['name']],
                 "context":res[0][each_reg['context']] if 'context' in each_reg else ""
            })


            break

    for each in result:
        print(each)

    return result


if ( __name__ == "__main__"):
    # 测试用参数字符串
    param_list = [
        # 整数
        r'int_param = 555',
        r"int_param:number",
        r"int_param:number = -5566",
        r'int_param: number=-111111',
        r'int_param : number = 0',
        r'time = 1000',

        # 字符串
        r'str_param=""',
        r"alignment=''",
        r'str_param:string=""',
        r'str_param:string',
        r'str_param="str_context"',
        r'str_param:string = "45123"',
        r'str_param:string="str_context:string"',

        # 浮点数
        # r'float_param: float',
        # r'float_param= 0.06',
        # r'float_param:float = -1.77',
        # r'float_param:float=-0.5',

        # 通用匹配带类型 - 无默认参数
        r'self',
        r'target',
        r'cc=None',
        r'isTrue:bool = True',
        r'list_str:list[str]',
        r'list_dict:list[dict]',
        r'list_custom:list[custom]',
        r'map_str:map[custom]',
        r'set_str:set[custom]=None',
        r'tuple_str:tuple[custom]=[]',
        r'object_param:subilme.Region',
        r'dict_custom:subilme.Region',
        r'dict_custom:dict[custom]',
    ]

    # 测试 函数、对象字符串
    func_str = """
exports.function_name = (ccvb, aaabbb) => cccvbbb',
exports.function_name = async ({ccvb:string, aaabbb}):void => cccvbbb',
    const function_name = ()=>{}",
    const function_name = async ({ccvb1:string="st", ccvb2:number=1}):void => {}',
    const function_name = (target: any, key: string): MetadataResult => {',

export const function_name = async (path,name):void=>{}',
export const function_name = (path: string): Function => setMetadata('all', path);',
export const function_name = (app: Application, middlewares: Function[]) => {',

exports.function_name = async function({data1, data2}) : number {}',
exports.function_name = function(data:string) {}',

export async function function_name(data,ccvb){}
    function function_name(path: string): boolen {
    async function_name(e, name) {
    function_name(e, name) {
function function_name(path):ccvb{}
tmp_img.onload = () => {
export const delay = (time = 1000) =>
"""
    func_list = [each for each in func_str.split('\n') if each !=""]

    # from test import extract
    # extract(int_test, int_reg)
    # extract(int_test, str_reg)
    # extract(int_test, float_reg)
    # extract(int_test, params_reg)
    # res = python_reg['func']['reg'].findall(func_str[0])



    test_func(func_list, func_reg)
    # test_params(param_list, int_reg)
