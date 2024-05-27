---
title: 关于Pycharm调试器的离谱bug后记
typora-root-url: 关于Pycharm调试器的离谱bug后记
date: 2024-05-27 14:05:16
category:Record
tags: Record
---

## 事情简述

pycharm的编译器程序没完善导致的离谱报错浪费我整整一天来处理结果发现根本不影响使用😅。写出这篇是为了让更多人能提前知道这个bug并不影响调试，那就看看我的受苦过程吧😵。。。

## 受苦过程

前两天我在试着通过调试看YOLO代码结构的时候发现的，报错如下，并且不断按步进他一直卡在一个地方：

```python
Traceback (most recent call last):
  File "_pydevd_bundle\pydevd_cython_win32_38_64.pyx", line 1597, in _pydevd_bundle.pydevd_cython_win32_38_64.ThreadTracer.__call__
  File "_pydevd_bundle\pydevd_cython_win32_38_64.pyx", line 940, in _pydevd_bundle.pydevd_cython_win32_38_64.PyDBFrame.trace_dispatch
  File "_pydevd_bundle\pydevd_cython_win32_38_64.pyx", line 928, in _pydevd_bundle.pydevd_cython_win32_38_64.PyDBFrame.trace_dispatch
  File "_pydevd_bundle\pydevd_cython_win32_38_64.pyx", line 585, in _pydevd_bundle.pydevd_cython_win32_38_64.PyDBFrame.do_wait_suspend
  File "E:/jb/PyCharm 2023.3.5/plugins/python/helpers/pydev/pydevd.py", line 1184, in do_wait_suspend
    self._do_wait_suspend(thread, frame, event, arg, suspend_type, from_this_thread)
  File "E:/jb/PyCharm 2023.3.5/plugins/python/helpers/pydev/pydevd.py", line 1191, in _do_wait_suspend
    self._activate_mpl_if_needed()
  File "E:/jb/PyCharm 2023.3.5/plugins/python/helpers/pydev/pydevd.py", line 749, in _activate_mpl_if_needed
    activate_function()
  File "E:\jb\PyCharm 2023.3.5\plugins\python\helpers\pydev\pydev_ipython\matplotlibtools.py", line 181, in activate_pyplot
    pyplot.show._needmain = False
AttributeError: partially initialized module 'matplotlib.pyplot' has no attribute 'show' (most likely due to a circular import)
```

意思是有引用库重了，当时就觉得十分蹊跷，觉得作为高级语言，python不可能没有识别重复引用模块并忽视重复引用的机制，最离谱的是我正常运行没有问题，但是一调试就立刻有问题了，而且报错的位置都是pycharm的插件或者自带的调试器，心想肯定不是代码的问题，而且之前调试的时候似乎也没有这个问题。

> 就这样我就进行了漫长的探索（折磨）🤐。。。

看了网上很多的“解决方案”，其一是文件命名和pycharm调试器的文件命名重合了，但是YOLOv5是在2020年开发的，这时候已经有pycharm了，使用pycharm的开发者必然会提出这个问题，事实上我找到最早的关于这个bug的博客是在2019年的，也就是pycharm过了5年还是没修复这个问题😥。。我一查YOLOv5项目里面含有可能重名的文件加上文件里面的引用，就已经有110个，想改很麻烦。

![image-20240527150209400](image-20240527150209400.png)

参考文档：[ModuleNotFoundError: No module named '_pydevd_bundle.pydevd_cython' error on debug](https://blog.csdn.net/weixin_30480651/article/details/99028558)

另一个可能的原因是pycharm的设置里面最下面倒数第二行开了PyQt兼容，有开发者说关了就能用，所以我关了试，开了把里面每个选项都调一次，重启pycharm，清理缓存，把每个选项都试了个遍，结果还是不行，结论是这个解决方案对于我的问题没有帮助😵。

![image-20240527150454576](image-20240527150454576.png)

> PyQt是什么🫡
>
> ![image-20240527150701760](image-20240527150701760.png)

参考文档：[【Python问题解决】PyCharm中debug报错：using cython not found. pydev debugger: process 13108 is connecting原因及解决](https://blog.csdn.net/weixin_43876206/article/details/101914566)

我还看到一个原因是因为没有调用cpython来加速，但是我的windows环境本来就是一坨💩了，于是就没有去搞这个了。

那么最后是怎么解决的呢？答案是我试着一直点步进，结果点着点着就能正常调试了，也就是之前的调试报错根本不影响你调试器正常调试🤪。。虚空索敌了啊淦！！！

## 最后

希望大家在不影响正常使用的时候忽略这个历史悠久的bug。
