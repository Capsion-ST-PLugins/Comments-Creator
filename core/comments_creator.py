# -*- coding: utf-8 -*-
#
# @Author: CPS
# @email: 373704015@qq.com
# @Date:
# @Last Modified by: CPS
# @Last Modified time: 2021-04-15 03:32:09.447327
# @file_path "D:\CPS\IDE\JS_SublmieText\Data\Packages\CPS\core"
# @Filename "comments_creator.py"
# @Description: 功能描述
#
import re

DEBUG = 0


def log(*args):
    if DEBUG:
        print(*args)


if __name__ == "__main__":
    from reg_python import python_reg

    log("python_reg: ", python_reg["checkType"].keys())
    from reg_js import js_reg

else:
    from .reg_python import python_reg
    from .reg_js import js_reg


class ParamsParser:
    def __init__(self, reg_obj):
        self.line_str = ""
        self.reg_obj = reg_obj
        self.syntax_tmpl = None

        self.result = {"params_obj": []}
        self.output_str = ""
        self.old_comment = {
            "description": "",
            "params": {},
            "return": "",
        }

        self.old_comment_list = []

    def __str__(self):
        return self.output_str

    # 提供旧的注释数据，提取内部对应的注释说明
    def set_old_comments(self, old_comments: str):
        self.old_comment_list = re.compile("\n").split(old_comments)

        # for index in range(len(self.old_comment_list)):
        #     log(f'{index}. {self.old_comment_list[index]}')
        # log('\n')

        self.old_comment["description"] = self.extract_description("description")
        # log("self.old_comment['description']: ", self.old_comment["description"])
        # log('\n')

        return self

    # 获取函数说明
    def get_description(self, tmpl: str) -> str:
        description = self.extract_description("description")
        res = tmpl.format(description=description) + "\n"
        return res

    # 获取函数返回说明注释
    def get_return(self, tmpl: str) -> str:
        description = self.extract_description("returns")
        res = tmpl.format(description=description) + "\n"
        return res

    # 从旧注释块内，提取对应关键字的说明文档，关键字是相应的参数名称
    def extract_description(self, key_word: str) -> str:
        key_word = key_word.lower()

        # 设置空格作为分隔符
        reg = re.compile(r"\s+")

        for each in self.old_comment_list:
            res = reg.split(each.strip())  # 转换数组

            if len(res) == 0 or not res:
                continue

            for index, _each in enumerate(res):

                # 字段必须包含 description
                if _each.lower().find(key_word) > -1:
                    # log("res: ", res)
                    # log(f'当前查找： [{key_word}] =>> [{_each}] => [{res[-1]}]\n')

                    # 获取最后一段当作注释内容
                    old_description = "".join(res[-1])
                    log("old_description: ", old_description)
                    return old_description

        # 没有识别到则返回一个模板
        return "{description}"

    # 主函数，根据提供的正则匹配当前输入的字符串是否符合，
    def match_line(self, line_str: str) -> bool:
        self.line_str = line_str

        # 更新新格式判断当前行是什么类型 对象|参数|函数
        if "checkType" in self.reg_obj:
            res = self.check_line_type(line_str)
            log("----------------- res: ", res)

            if not res or not "result" in res:
                log("错误~~~~~~~~~~~~~~~~~")
                return False

            # 匹配成功，提取出结果
            result = res["result"]
            reg = res["reg"]

            # 处理参数
            self.get_params(result[reg["params"]], self.reg_obj["paramType"].keys())

            # 获取缩进和其他参数
            self.result["line_start_indent"] = self.line_start_indent(
                result[reg["indent"]]
            )
            self.result["type"] = result[reg["type"]] if "type" in reg else ""
            self.result["name"] = result[reg["name"]]

            if "return_type" in reg:
                # 如果存在返回值，注入返回值的注释模板
                self.result["return"] = {"description": "{description}"}

                # 获取当前行的返回值
                self.result["return"]["type"] = result[reg["return_type"]]

            return True

        else:
            for each_reg in self.reg_obj["func"]:
                res = each_reg["reg"].findall(line_str)

                # 如果匹配结构不符合，执行下一次匹配
                if len(res) != 1 or len(res[0]) != each_reg["res_len"]:
                    continue

                # 匹配成功，提取出结果
                result = res[0]

                # 匹配 参数
                params_str: str = ""
                if "params" in each_reg:
                    params_str = result[each_reg["params"]]

                # 获取缩进和其他参数
                self.result["line_start_indent"] = self.line_start_indent(
                    result[each_reg["indent"]]
                )
                self.result["type"] = (
                    result[each_reg["type"]] if "type" in each_reg else ""
                )
                self.result["name"] = result[each_reg["name"]]
                self.result["params_obj"] = self.get_params(params_str)

                if "return_type" in each_reg:
                    self.result["return"] = {"description": "{description}"}
                    self.result["return"]["type"] = result[each_reg["return_type"]]

                return True

        return False

    # 监测当前行是什么类型：返回 "checkTpye" 的key ，class|func|param
    def check_line_type(self, line_str: str) -> dict:
        """
        @Description {description}

        - param line_str :{str} {description}

        returns `{dict}` {description}
        @returns
        ```py
        {
            "type":当前行是函数还是对象还是变量,
            "result":匹配结果，记录当前行所有信息的索引（参数在哪，类型标识在哪，名字在哪等）
            "reg":
        }

        ```
        """
        for each in self.reg_obj["checkType"].keys():
            log("each: ", each)

        if not "checkType" in self.reg_obj:
            log("没有发现 checkType")
            return {}

        for key in self.reg_obj["checkType"].keys():
            reg_list: list = self.reg_obj["checkType"][key]

            for each_reg in reg_list:
                # print("each_reg: ", each_reg)
                res = each_reg["reg"].findall(line_str)

                # 如果匹配结构不符合，执行下一次匹配
                if len(res) != 1 or len(res[0]) != each_reg["res_len"]:
                    continue

                # 匹配成功
                return {"type": key, "result": res[0], "reg": each_reg}

    def set_syntax_tmpl(self, syntax_tmpl):
        if syntax_tmpl:
            self.syntax_tmpl = syntax_tmpl

        return self

    # 将数据更新到模版上
    def format(self, syntax_tmpl: dict = None):
        self.set_syntax_tmpl(syntax_tmpl)

        if not self.syntax_tmpl:
            return self

        # 处理 description 行
        description = self.get_description(
            self.syntax_tmpl["comments_contexts"]["Description"]
        )

        # 处理 returns 行
        returns = self.syntax_tmpl["comments_contexts"]["returns"] + "\n"
        if "return" in self.result:
            returns = returns.format(
                type="{" + self.result["return"]["type"] + "}",
                description=self.extract_description("returns"),
            )

        # 获取参数之间的间隔符号，默认使用一个空格
        params_alignment: str = self.syntax_tmpl.get("params_alignment", " ")

        if "params_obj" in self.result:
            # 将数据渲染到注释模板中
            for each in self.result["params_obj"]:
                log(each)

            params = self.comment_params(
                self.result["params_obj"],
                self.syntax_tmpl["comments_contexts"]["param"],
                params_alignment,
            )

            # 合并所有内容
            contexts_list = [description, *params, returns]  # py3.8

            # 给每行注释添加 前缀 和 \n 结束符
            comment_prefix = self.syntax_tmpl["comments_header"][1]
            contexts_list = self.add_comment_prefix(comment_prefix, contexts_list)

            # 每行注释添加缩进
            line_indent = self.result["line_start_indent"]
            self.line_indent = line_indent
            output_str = self.add_line_indent(line_indent, contexts_list)

            # 合并所有注释
            begin = line_indent + self.syntax_tmpl["comments_header"][0] + "\n"
            end = line_indent + self.syntax_tmpl["comments_header"][-1] + "\n"
            self.output_str = begin + "".join(output_str) + end

        return self

    def comment_params(self, params_obj: dict, tmpl: str, alignment: str = "") -> list:
        params = []
        for each_param in params_obj:
            param = tmpl.format(
                # name = each_param['name'],
                name=each_param["context"],
                type="{" + each_param["type"] + "}",
                description=self.extract_description(each_param["name"]),
            )
            params.append(param)

        if alignment:
            params = self.insert_alignment(params, alignment)

        return [each + "\n" for each in params]

    @staticmethod
    def add_line_indent(indent, contexts_list):
        return [indent + each for each in contexts_list]

    @staticmethod
    def add_comment_prefix(comment_prefix, contexts_list):
        # 重新根据 \n 符号，重新分配每行
        constext_str = "".join(contexts_list)
        contexts_list = constext_str.split("\n")
        return [comment_prefix + each + "\n" for each in contexts_list]

    @staticmethod
    def insert_alignment(param_list: list, indent: str) -> list:
        res = []
        for each_param in param_list:
            # 默认模版使用空格分隔
            each_list = each_param.split(" ")

            # 获取每行的元素个数
            index = [e for e in range(len(each_list))]
            for i, each_index in enumerate(index):
                # 获取同一列最大的字符长度
                max_len = max(
                    [
                        len(each_param.split(" ")[each_index])
                        for each_param in param_list
                    ]
                )
                each_len = len(each_list[each_index])

                if each_len < max_len:
                    ex = " " * (max_len - each_len)
                    each_list[each_index] = each_list[each_index] + ex

            res.append(indent.join(each_list))
        return res

    def line_start_indent(self, indent_str: str, indent: str = " ") -> str:
        res = ""
        str_len = len(indent_str)
        if str_len > 0:
            res = indent * str_len
        return res

    def get_params(self, params_str: str, params_key_list: list) -> list:
        """
        @Description 调用`self.extract_params()`对所有参数进行处理，返回列表

        - param params_str :{str}    参数片段，括号内的内容

        returns `{list}` {description}
        ```json
        [
            {"id": 0, "type": "param", "name": "value", "context": ""},
            {"id": 1, "type": "param", "name": "xxxxx", "context": ""},
            {"id": 2, "type": "param", "name": "aaaaa", "context": ""},
        ]

        ```
        """
        if not params_str or len(params_str) == 0:
            return []

        res_list = []

        # 分割参数字符串 -> 转换数组处理
        params_list = params_str.replace(" ", "").strip().split(",")

        # 识别输入的字符串，识别出各个字段的类型和名字
        res_list = [
            res
            for each in params_key_list
            for res in self.extract_params(each, params_list)
            if len(res) > 0
        ]

        # id是依据读取时的顺序记录的，因为经过正则识别后，函数参数的顺序被打乱，通过id进行更正
        if len(res_list) > 0:
            self.result["params_obj"] = sorted(res_list, key=lambda item: item["id"])

        return self

    def extract_params(self, tar: str, params_list: list) -> list:
        """
        Description 根据tar提供的正则，遍历识别参数列表

        - param self        :{params} {description}
        - param tar         :{str}    要识别的参数
        - param params_list :{list}   根据self.reg_obj生成的keys列表

        returns `{list}` {description}
        @returns
        ```json
        {
            "id":0, // 参数的顺序id
            "type":["参数","字符串","数字", "数组"], // 参数的类型
            "name":"参数的名称",
            "context":"参数的内容"
        }
        ```
        """
        result: list = []
        for index, each_param in enumerate(params_list):

            for each_reg in self.reg_obj["paramType"][tar]:
                res = each_reg["reg"].findall(each_param)
                if not res or len(res) == 0:
                    continue
                # print(f'{tar} 当前匹配结果： >>> ', res[0])
                # print(f'params_list: *** {params_list}')

                # 已匹配的结果进行标记

                # type
                t = tar
                if "type" in each_reg:
                    if isinstance(each_reg["type"], str):
                        t = each_reg["type"]
                    elif isinstance(each_reg["type"], int):
                        t = res[0][each_reg["type"]]

                # 剔除一些不需要的参数，self，cls等
                # 对结果进行过滤，如果存在与 self.reg_obj['except']['param']中，则忽略
                if res[0][each_reg["name"]] in self.reg_obj["except"]["param"]:
                    continue

                params_list[index] = ""

                # 保留原始内容
                if "context" in each_reg:
                    context = "{}={}".format(
                        res[0][each_reg["name"]], res[0][each_reg["context"]]
                    )
                else:
                    context = res[0][each_reg["name"]]

                result.append(
                    {
                        "id": index,
                        "type": t,
                        "name": res[0][each_reg["name"]],
                        "context": context,
                    }
                )

                break
        return result

    def insert_default_comments(self):
        return self.syntax_tmpl["comments_header"]


class Python(ParamsParser):
    def __init__(self):
        super(Python, self).__init__(python_reg)
        self.syntax_tmpl = {
            "insert_alignment": True,
            "insert_alignment_indent": "  ",
            "comments_contexts": {
                "Description": "Description\n",
                "param": "@param {name}:{type} paramDescription",
                "returns": ": returns {type} returnsDescription",
            },
            "comments_header": [
                '"""',
                "",
                '"""',
            ],
        }


class JavaScript(ParamsParser):
    def __init__(self):
        super(JavaScript, self).__init__(js_reg)
        self.syntax_tmpl = {
            "insert_alignment": True,  # 对齐
            "insert_alignment_indent": "  ",
            "comments_contexts": {
                "Description": "@Description - {description}\n",
                "param": "@param {type} {name}  - {description}",
                "returns": "\n@returns {type} - {description}",
            },
            "comments_header": ["/**", " * ", " */"],  # /**  #  * 内容位置的前缀  #  */
        }


PARSER = {
    "python": Python,
    "vue": JavaScript,
    "javascript": JavaScript,
    "typescript": JavaScript,
    "mts": JavaScript,
    "ctm": JavaScript,
    "js": JavaScript,
    "cjs": JavaScript,
    "mjs": JavaScript,
    "py": Python,
    "default": JavaScript,
}


if __name__ == "__main__":
    syntax_tmpl = {
        "params_alignment": "  ",
        "comments_contexts": {
            "Description": "Description - {description}\n",
            "param": ":param {type} {name} - {description}",
            "returns": "\n- returns {type} - {description}",
        },
        "comments_header": ['    """', "    ", '    """'],
    }

    old_comment = """    /**
     *  @Description 读取file格式123123
     *
     *  @param {params} e     {description}
     *  @param {file} file  file格式的文件对象
     *
     *  @returns {} {description}
     *
     */"""

    # test_str = "class Win32(object):"
    # test_str = "def debug(value='5', set=True):"
    test_str = (
        "    def insert_alignment(self, param_list:list=[], indent:str='STR') -> list:"
    )
    syntax = "py"

    test = Parser[syntax]()
    test.match_line(test_str)
    test.set_old_comments(old_comment).format(syntax_tmpl)

    log(test)
