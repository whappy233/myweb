

# 标题
## 标题2
### 标题3
#### 标题4
##### 标题5
###### 标题6

<br>
<br>
<br>
<br>

# 段落

使用空白行将一行或多行文本进行分隔

不要用空格（spaces）或制表符（ tabs）缩进段落。

<br>
<br>
<br>
<br>

# 换行
实时搜索<br>顶顶顶顶

<br>
<br>
<br>
<br>

# 字体
**加粗1** <br>
*倾斜* <br>
***这是加粗倾斜*** <br>
~~这是加删除线~~

<br>
<br>
<br>
<br>

# 分割线
请在单独一行上使用三个或多个星号 (***)、破折号 (---) 或下划线 (___) ，并且不能包含其他内容, 请分隔线的前后均添加空白行。

***
___
*****
_______

<br>
<br>
<br>
<br>

# 引用
> 这是引用.块引用可以包含多个段落。为段落之间的空白行添加一个 > 符号。
>> 块引用可以嵌套。在要嵌套的段落前添加一个 >> 符号。
>
>> 块引用可以包含其他 Markdown 格式的元素。并非所有元素都可以使用，你需要进行实验以查看哪些元素有效.
>
>>>> Back to the first level.

> # The quarterly results look great!
>
> - Revenue was off the chart.
> - Profits were higher than ever.
>
>  *Everything* is going according to **plan**.

<br>
<br>
<br>
<br>

# 列表
- 无序列表(使用 * + - 作为标记, 跟内容之间都要有一个空格, 建议使用 - )
   - 列表内容
   + 列表内容
   * 列表内容
      * 嵌套
      * 嵌套

- 有序列表则使用数字接着一个英文句点作为标记. (只按第一个数字来排序，因此第一个最好是1)
   1. 列表内容
   2. 列表内容
   3. 列表内容
      1. 嵌套
      2. 嵌套

## 任务列表
- [x] Write the press release
- [ ] Update the website
- [ ] Contact the media

## 在列表中嵌套其他元素

要在保留列表连续性的同时在列表中添加另一种元素，请将该元素缩进四个空格或一个制表符，如下例所示：
### 引用
-   This is the first list item.
-   Here's the second list item.

    > A blockquote would look great below the second list item.

-   And here's the third list item.

### 段落
*   This is the first list item.
*   Here's the second list item.

    I need to add another paragraph below the second list item.

*   And here's the third list item.

### 代码块
代码块通常采用四个空格或一个制表符缩进。当它们被放在列表中时，请将它们缩进八个空格或两个制表符
1.  Open the file.
2.  Find the following code block on line 21:

        <html>
            <head>
            <title>Test</title>
            </head>
        </html>

3.  Update the title to match the name of your website.

### 图片
1.  Open the file containing the Linux mascot.
2.  Marvel at its beauty.

    ![Tux, the Linux mascot](/assets/images/tux.png)

3.  Close the file.

<br>
<br>
<br>
<br>

# 表格

默认左对齐|使用居中对齐|使用右对齐
---------|:--------:|--------:
内容|内容|内容
内容|内容|内容

- 文字默认居左对齐
- 两边加 **`:`** 表示文字居中对齐
- 右边加 **`:`** 表示文字居右对齐

<br>
<br>
<br>
<br>

# 代码
要创建代码块，请将代码块的每一行缩进至少四个空格或一个制表符. 前面要有一个空行和前面的文字分隔开

## 缩进代码块
    import ob
    print(os.environ)

## 单行代码 `from os import path`

## 围栏代码块
```python
def get_all_parents(self):
    """获取所有父级"""
    categorys = []
    def parse(c):
        categorys.append(c)
        if c.parent_category:
            return parse(c.parent_category)
    parse(self)
    return categorys
```

<br>
<br>
<br>
<br>

# Markdown 内嵌 HTML 标签

## 行级內联标签
HTML 的行级內联标签如` <span>、<cite>、<del> `不受限制，可以在 Markdown 的段落、列表或是标题里任意使用。依照个人习惯，甚至可以不用 Markdown 格式，而采用 HTML 标签来格式化。例如：如果比较喜欢 HTML 的 `<a> `或` <img>` 标签，可以直接使用这些标签，而不用 Markdown 提供的链接或是图片语法。当你需要更改元素的属性时（例如为文本指定颜色或更改图像的宽度），使用 HTML 标签更方便些。

This **word** is bold. This <em>word</em> is italic.

## 区块标签

区块元素──比如` <div>、<table>、<pre>、<p> `等标签，必须在前后加上空行，以便于内容区分。而且这些元素的开始与结尾标签，不可以用 tab 或是空白来缩进。Markdown 会自动识别这区块元素，避免在区块标签前后加上没有必要的 <p> 标签。

This is a regular paragraph.

<table>
    <tr>
        <td>Foo</td>
    </tr>
</table>

This is another regular paragraph.

<br>
<br>
<br>
<br>

# 字体、大小、颜色

<font face="黑体">我是黑体字</font>
<font color=red>我是红色</font>
<font size=1>我是尺寸</font>
<font face="黑体" color=green size=3>我是黑体，绿色，尺寸为5</font>
<table><tr><td bgcolor='#005500'>添加背景色</td></tr></table>
<center>文字居中</center>
<p align="left">左对齐</p>
<p align="right">右对齐</p>

H<sub>2</sub>O  CO<sub>2</sub> 我草<sup>TM</sup>

<br>
<br>
<br>
<br>

# 超链接

超链接Markdown语法代码：[超链接显示名](超链接地址 "超链接title(可选)")

<a href="超链接地址" target="_blank">超链接名</a>

http://www.example.com

<https://markdown.com.cn>

<fake@example.com>

粗体 **[EFF](https://eff.org)**.

斜体 *[Markdown Guide](https://www.markdownguide.org)*.

代码块 See the section on [`code`](#code).

***

## 参考式的链接

[应显示为链接的文本][显示了一个标签，该标签用于指向您存储在文档其他位置的链接, 可以包含字母，数字，空格或标点符号]
[标签]: url,可以选择将其括在尖括号中 "可选标题,可以将其括在双引号，单引号或括号中"

___

[hobbit-hole][1]

[1]: https://en.wikipedia.org/wiki/Hobbit#Lifestyle "Hobbit lifestyles"

___

I get 10 times more traffic from [Google][] than from[Yahoo][] or [MSN][].

[google]: http://google.com/        "Google1"
[yahoo]:  http://search.yahoo.com/  "Yahoo Search2"
[msn]:    http://search.msn.com/    "MSN Search3"

___

<br>
<br>
<br>
<br>


# 插入图片
要添加图像，请使用感叹号 (!), 然后在方括号增加替代文本，图片链接放在圆括号里，括号里的链接后可以增加一个可选的图片标题文本。

![替代文本](图片URL '可选的标题文本')


## 参考式的图片语法：

![Alt pic][图片参考的名称，图片参考的定义方式则和连结参考一样]

[id]: url/to/image  "Optional title attribute"

## 链接图片
[![沙漠中的岩石图片](/assets/img/shiprock.jpg "Shiprock")](指向的URL)

## 设置图片大小
<!-- <img src="http:..." width = "100" height = "100" div align=right /> -->

<br>
<br>
<br>
<br>


# LaTeX 公式
## 行内公式
$\ce{Hg^2+ ->[I-] HgI2 ->[I-] [Hg^{II}I4]^2-}$

## 块公式
$$H(D_2) = -\left(\frac{2}{4}\log_2 \frac{2}{4} + \frac{2}{4}\log_2 \frac{2}{4}\right) = 1$$

## 矩阵
$$
  \begin{pmatrix}
  1 & a_1 & a_1^2 & \cdots & a_1^n \\
  1 & a_2 & a_2^2 & \cdots & a_2^n \\
  \vdots & \vdots & \vdots & \ddots & \vdots \\
  1 & a_m & a_m^2 & \cdots & a_m^n \\
  \end{pmatrix}
$$


