# -*- coding: utf-8 -*-
#
# @Author: CPS
# @email: 373704015@qq.com
# @Date: 2021-08-17 00:33:03.068323
# @Last Modified by: CPS
# @Last Modified time: 2021-08-17 00:33:03.070420
# @file_path "D:\CPS\IDE\sublime Text\sublime_text_4113.21_win64_patched\sublime_text\Data\Packages\testt_comments_creater\core"
# @Filename "test.py"
# @Description: 功能描述
#
import re


def create_reg_obj(
    reg, res_len: int, name: int, type: int = -1, context: int = -1
) -> dict:
    """
    Description 创建一个匹配模板，记录匹配结果对应索引代表的意思

    - param reg:{params}  正则表达式
    - param res_len:{int} 匹配成功后的正确长度
    - param name:{int}    函数名|参数名
    - param type:{int}    函数类型|参数类型
    - param context:{int} 默认参数

    - returns {dict} 函数的返回类型

    """
    if res_len <= 1:
        raise Exception("res_len 参数必须大于1，返回的结果需要二元tuple进行处理")

    res = {"reg": re.compile(reg), "name": name, "res_len": res_len}

    if context != -1:
        res["context"] = context

    if type != -1:
        res["type"] = type

    return res


int_reg = [
    create_reg_obj(r"^(\w+)\s*?:\s*?(int)\s*?\=\s*?(\-?\d+|0)$", 3, 0, 1, 2),
    create_reg_obj(r"^(\w+)\s*?\=\s*?(\-?\d+|0)$", 2, 0, context=1),
    create_reg_obj(r"^(\w+)\s*?:\s*?(int)$", 2, 0, 1),
]

float_reg = [
    create_reg_obj(
        r"^(\w+)\s*?\=\s*?([1-9]\d*\.\d*|0\.\d*[1-9]\d*$|-([1-9]\d*\.\d*|0\.\d*[1-9]\d*)$)",
        3,
        0,
        context=2,
    ),
    create_reg_obj(
        r"^(\w+)\s*?:\s*?(float)\s*?\=\s*?([1-9]\d*\.\d*|0\.\d*[1-9]\d*$|-([1-9]\d*\.\d*|0\.\d*[1-9]\d*)$)",
        4,
        0,
        1,
        2,
    ),
    create_reg_obj(r"^(\w+)\s*?:\s*?(float)\s*?$", 2, 0, type=1),
]

str_reg = [
    create_reg_obj(r"^(\w+)\s*?:(str)\s*?=\s*?(\'|\")(\w+)(\'|\")$", 5, 0, 1, 3),
    create_reg_obj(r"^(\w+)\s*?\s*?\=\s*?(\'|\")(\w+)?(\'|\")$", 4, 0, context=2),
    create_reg_obj(r"^(\w+)\s*?:(str)", 2, 0, type=1),
]

bool_reg = [
    {
        "reg": re.compile(r"^(\w+)\=(True|False)"),
        "name": 0,
        "res_len": 2,
        "context": 1,
        "type": "bool",
    }
]

# 识别没有指定默认值的参数
params_reg = [
    create_reg_obj(
        r"^(\w+|\*\*\w+|\*\w+)\s*?\:\s*?(\w+\.\w+|\w+\[\w+\.\w+|\w+|.*\]|\w+)\s*?\=\s*?(.*)$",
        3,
        0,
        1,
        2,
    ),
    create_reg_obj(
        r"^(\w+|\*\*\w+|\*\w+)\s*?\:\s*?(\w+\.\w+|\w+\[\w+\.\w+|\w+|.*\]|\w+)$",
        2,
        0,
        type=1,
    ),
    create_reg_obj(r"^(\w+|\*\*\w+|\*\w+)(\s*?)$", 2, 0),  # 添加 (\s*?) 为了可以返回2元格式的结果
    create_reg_obj(r"^(\w+)\s?\=\s?(\w+)$", 2, 0, context=1),
]

func_reg = [
    {
        # "reg":re.compile(r'^(\s*)?(class|def)\s*?(\w+)\((.*)\)\s*?(\->)?\s*?(\w+\.\w+|\w+)?\s*?\:'),
        "reg": re.compile(
            r"^(\s*)?(async def|def)\s+(\w+)\(\s*?(.*)\s*?\)\s*?(\->)?\s*?([a-zA-Z\.->\s\[\]\$\|]+)?\s*?\:"
        ),
        "res_len": 6,
        "name": 2,
        "type": 1,
        "return_type": 5,
        "params": 3,
        "indent": 0,
    }
]

class_reg = [
    {
        "reg": re.compile(
            r"^(\s*)?class\s*?(\w+)?\((.*)\)\s*?(\->)?\s*?(\w+\.\w+|\w+)?\s*?\:"
        ),
        "res_len": 5,
        "name": 2,
        "type": 1,
        "return_type": 5,
        "params": 3,
        "indent": 0,
    }
]

python_reg = {
    # 旧
    # "class":class_reg,
    # "func":func_reg,
    # "string":str_reg,
    # "int":int_reg,
    # "float":float_reg,
    # "bool":bool_reg,
    # "param":params_reg,
    # 新
    "checkType": {
        "class": class_reg,  # 判断是否 对象
        "func": func_reg,  # 判断是否 函数
        "param": params_reg,  # 判断是否 参数
    },
    # 判断参数是什么类型，同时返回默认值
    "paramType": {
        "string": str_reg,
        "int": int_reg,
        "float": float_reg,
        "bool": bool_reg,
        "param": params_reg,
        # "dict":None, # 未完成
        # "list":None, # 未完成
    },
    "except": {"param": ["self", "cls"]},
}


if __name__ == "__main__":

    # 测试用参数字符串
    params_list = [
        # 整数
        r"int_param = 555",
        r"int_param:int",
        r"int_param:int = -5566",
        r"int_param:int=-111111",
        r"int_param : int = 0",
        # 字符串
        r'str_param=""',
        r"alignment=''",
        r'str_param:str=""',
        r"str_param:str",
        r'str_param="str_context"',
        r'str_param:str = "45123"',
        r'str_param:str="str_context:str"',
        # 浮点数
        r"float_param: float",
        r"float_param= 0.06",
        r"float_param:float = -1.77",
        r"float_param:float=-0.5",
        # 通用匹配带类型 - 无默认参数
        r"self",
        r"target",
        r"cc=None",
        r"isTrue:bool = True",
        r"list_str:list[str]",
        r"list_dict:list[dict]",
        r"list_custom:list[custom]",
        r"map_str:map[custom]",
        r"set_str:set[custom]=None",
        r"tuple_str:tuple[custom]=[]",
        r"object_param:subilme.Region",
        r"dict_custom:subilme.Region",
        r"dict_custom:dict[custom]",
        r"fix=True",
    ]

    # 测试 函数、对象字符串
    func_str = """
class ParamsParser():
    class TesttCommentsCreatorCommand( target, age=5, bill=-5.1, flag=None, default_name="ccvbb", *key,**rt ):
        def test( target, age=5, bill=-5.1, flag=None, default_name='ccvbb', *key,**rt ):
        def get_pre_line_point(selfff, curt_line, reg):
    def get_old_comments(self, insert_position:int, comment_begin:str, comment_end:str) -> sublime.Region:
def extract(params_list:list, reg_obj:list) -> list:
    def comment_params(self, params_obj, tmpl, alignment=""):
def check_data(self, data, fix=True, tip=True):
    def find_str_by_line_region(self, line_region:sublime.Region, find_str:str, max_search_count:int=1, direction:str='up') -> Optional[str]:
async def test(item: Any):
    def get_window_info(hwnd: T.Hwnd) -> T.HwndInfo | None:
    def find_sub_window_ex( parent_hwnd: T.Hwnd, class_name: str = None, window_text: str = None ) -> T.HwndInfo | None:
"""

    func_list = [each for each in func_str.split("\n") if each != ""]

    def test(params_list: list, reg_obj: list) -> list:
        """
        @Description 测试函数

        - param params_list :{list} {description}
        - param reg_obj     :{list} {description}

        @returns `{list}` {description}

        """
        result: list = []
        i = 0

        for index, each_param in enumerate(params_list):
            for reg_index, each_reg in enumerate(reg_obj):
                # type
                # t=""
                # if 'type' in each_reg:
                #     if isinstance(each_reg['type'], str):
                #         t = each_reg['type']
                #     elif isinstance(each_reg['type'], int):
                #         t = res[0][each_reg['type']]

                res = each_reg["reg"].findall(each_param)
                if not res or len(res) == 0:
                    print(f"【第{index}行】: ", each_param)
                    continue
                else:
                    i += 1
                    params_list[index] = ""

                    ret = {"id": index}
                    for each in each_reg.keys():
                        if each in ["reg", "res_len"]:
                            continue
                        ret[each] = res[0][each_reg[each]]

                    result.append(ret)
                    print(f"【第{index}行】: ", ret)
                break

        return result

    # test(params_list, int_reg)
    # test(params_list, bool_reg)
    # test(params_list, params_reg)
    # test(params_list, float_reg)
    # test(params_list, params_reg)
    # res = python_reg['func']['reg'].findall(func_str[0])

    test(func_list, func_reg)
