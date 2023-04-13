## 简介|Introductions

<div>
    <img flex="left" src="https://img.shields.io/badge/python-%3E%3D3.8.0-3776AB"/>
    <img flex="left" src="https://img.shields.io/badge/Sublime%20Text-FF9800?style=flat&logo=Sublime%20Text&logoColor=white"/>
    <img flex="left" src="https://img.shields.io/github/license/caoxiemeihao/electron-vite-vue?style=flat"/>
</div>

自用的 jdDoc 格式注释模板注入插件，原理是采用正则匹配，以前不知道有**AST**模块的时候写的，也没时间重构，就边用边更新了。

注意: 插件市场有专业的功能相似的插件，我只是单纯为了自己用的爽菜写的 😁，才不是因为它配置太复杂才自己造轮子，请有需要的朋友请使用专业插件。

> - 本插件为团队内部打造使用，不对外更新负责，
> - 2023年了，前端建议采用**VSCode**。
> 


## 功能|Feature
![screenshot](/screenshot/sublimeTextPlugs/cps-Comments-Creator/cps-Comments-Creator.gif)
![cps-Comments-Creator](http://localhost:45462/image/cps-Comments-Creator.gif)
- 在光标所选的函数上创建jsdoc风格的注释
- 在新增参数的旧注释上，保留原注释的情况下追加新参数
- 支持多行写法的函数（参数太多）
- 支持`py`和`js系`
- 核心采用了正则匹配，后续可能会更新为AST语法解析的模式（有想法，没时间系列）



## 使用|Usage

快捷键：`Alt + q` 在函数行键入即可，暂时 py 使用比较多，js 和 ts 部分语法不能识别，也没空更新

### **创建注释块**

![setp1](http://screenshot/sublimeTextPlugs/cps-Comments-Creator/setp1.gif)

![step1](http://localhost:45462/image/step1.gif)

### **更新现有注释块**

![setp2](http://screenshot/sublimeTextPlugs/cps-Comments-Creator/setp2.gif)

![step2](http://localhost:45462/image/step2.gif)

## **插件配置|Configure**

```js
// Packages/User/cps.sublime-settings
{
  "name": "tett 插件",
  "author": "CPS",
  "mail": "373704015@qq.com", //本插件任何问题请联系qq

  // prettier-ignore
  "cps_comments_creator": {
    // 全局默认配置
    "max_search_count":80,       // 搜索行数（正数从上向下查找， 负数反之）
    "params_alignment":"  ",     // [indent<string>] 是否对齐参数
    "comments_direction":"up",   // "down"|"up" 函数名字上一行，函数名字下一行
    "default_tmpl":{
      "comments_contexts":{
        "Description":true,
        "param":":param {type} {name} {description}",
        "returns":":returns {type} {description}",
      }
    },

    /* 根据后缀名设置 */
    "py": {
      "comments_direction": "down",
      "comments_contexts":{
        "Description":"@Description {description}\n",
        "param":"- param {name} :{type} {description}",
        "returns":"\n@returns `{type}` {description}"
      },
      "comments_header": [
        "    \"\"\"",      // 注释区的开始标识
        "    ",            // 内容位置的前缀
        "    \"\"\"",      // 注释区的结束
      ]
    },

    "js":{
      "comments_contexts":{
        "Description":"@Description - {description}\n",
        "param":"@param {type} {name}  - {description}",
        "returns":"\n@returns {type} - {description}"
      },
      "comments_header": [
        "/**",        //    /**
        " * ",        //     * 内容位置的前缀
        " */"         //     */
      ]
    },

    "mjs":{
      "comments_contexts":{
        "Description":"@Description - {description}\n",
        "param":"@param {type} {name}  - {description}",
        "returns":"\n@returns {type} - {description}"
      },
      "comments_header": [
        "/**",        //    /**
        " * ",        //     * 内容位置的前缀
        " */"         //     */
      ]
    },

    "ts":{
      "comments_contexts":{
        "Description":"@Description - {description}\n",
        "param":"@param {type} {name}  - {description}",
        "returns":"\n@returns {type} - {description}"
      },
      "comments_header": [
        "/**",        // /**
        " * ",        //  * 内容位置的前缀
        " */"         //  */
      ]
    },

    "vue":{
      "comments_contexts":{
        "Description":" @Description {description}\n",
        "param":" @param {type} {name}  {description}",
        "returns":"\n @returns {type} {description}"
      },
      "comments_header": [
        "/**",      // /**
        " * ",      //  * @Description:
        " */"       //  */
      ]
    }
  }
  // prettier-ignore
}
```

## 联系方式|Contact

- **373704015 (qq、wechat、email)**
