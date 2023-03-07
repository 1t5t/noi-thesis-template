# 信息学竞赛中国国家集训队论文模板

~~教练现在就没有理由不发论文集了~~

## 使用方法

clone 该仓库，在仓库目录下按照如下方式整理所有文件

```
directory1
  main.tex
  other_files
directory2
  main.tex
  other_files
...
compiler.py
main.tex
noithesis.cls
```

在该目录下运行 `compiler.py`，编译完成后该目录下的 `main.pdf` 即为编译结果。

## 编写要求

论文提交的文件整理格式为

```
your_name
  main.tex
  other_files
```

其中提交的文件需要满足以下要求：

- `your_name` 文件夹下的所有 `tex` 文件中恰有一个 `\begin{document}` 字符串（即不能有注释掉的 `\begin{document}`）。这个文件不必命名为 `main.tex`，但下文中认为这个文件为 `main.tex`。其他辅助的 tex 文件可放在子文件夹中。
- `main.tex` 中恰有一个 `\title{}` 和 `\author{}`。其中 `\author{}` 格式为 “学校 姓名”，中间用任何合理的空白符分隔。
- 未使用 `\setcounter{page}{X}` 更换页码
- 使用 `xelatex->xelatex` 或 `xelatex->bibtex->xelatex->xelatex` 编译命令可正常编译
