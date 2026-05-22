---
title: YOLOv5使用二期
typora-root-url: YOLOv5使用二期
date: 2024-05-11 18:56:28
category: 
   - Technology
tags:
   - YOLO
   - PyTorch
   - Dataset
---

## 简述

遇到了至少8个**ERROR**😅，好在解决的都很迅速，这次使用，用到了给视频打标的功能，任务算是完成的比较好的吧。



## 流程

1. 试运行train.py，遇到**ERROR1**，具体解决过程参考该[文档](https://blog.csdn.net/weixin_52890053/article/details/132111731)，很容易解决，以下为报错：

`wandb: ERROR api_key not configured (no-tty). call wandb.login(key=[your_api_key])`

2. 配置环境，遇到**ERROR2**，具体解决过程直接翻到**ERROR**部分看，以下为报错：

```
# numpy版本太新
`np.int` was a deprecated alias for the builtin `int`. To avoid this error in existing code, use `int` by itself.
# 新版torch不会自动转换浮点型为整型
RuntimeError: result type Float can‘t be cast to the desired output type __int64
```

3. 觉得自己打标太麻烦，参照了该[视频](https://www.bilibili.com/video/BV13N411q7g1/?p=1&vd_source=99294a2a1c5504f559670de616463ae4),采用边训练边打标的模式，节约时间成本（这周真的太忙了，而且因为任务的特殊性，是标注叶子，打标也很麻烦），以下是使用的对应文件及其需要导出的参数：

   `python .\detect.py –-save-txt`

4. 采用上面办法，又遇到问题，这次是pillow的版本太高导致的，归类为**ERROR3**，[解决方案](https://zhuanlan.zhihu.com/p/662305030)报错如下：

   `DLL load failed while importing _imaging`

5. 决定放弃之前想省事的想法，原因如下：

   > 我们打标的对象是叶子，用上述方法，打了之后，需要自己筛选，其实花的时间和精力更大。
   >
   > > 不代表这种方法不能用，作为一个循环打标法，对于打标对象如果在图里面比较分散，这种方法是很实用，很省事的。

6. 时间不太多，打了50＋的图就打算拿来先训练了，遇到**ERROR4**，解决办法就是吧bitch-size改小，降低最大使用内存。

   `RuntimeError: DataLoader worker (pid(s) 16272) exited unexpectedly`

7. 启动detect.py，出现一个模块不联网启动不了这个包的问题，联网解决。

8. 发现任务搞错了，重新打标，认清任务目标之后，发现任可以沿用3的方法，借用LL打的标之后，继续进行训练，出现**ERROR5**，以下是内容：

   `WARNING: NMS time limit 10.0s exceeded`

   ![image-20240416045743769](image-20240416045743769.png)

	具体原理是进行NMS的时间阈值太短，需要调高阈值，具体解决过程看**ERROR PART**。

9. 后面又出现以下**ERROR6**，网上的说法是opencv里面多线程套了多线程，所以导致程序卡死，尝试把上一步的**time_limit**改小，有可能是开太大了，现在从1000.0秒改成100.0秒，暂时能正常工作。

   `cv2.error: Caught error in DataLoader worker process 5.`

10. 又出现两个新**error**，其一是检测图片有可能损坏，为下图，报错为`Corrupt JPEG data: 2 extraneous bytes before marker 0xd9`，其二仍是9的问题，查看一篇[文章](https://blog.csdn.net/weixin_46751388/article/details/126735247)，发现yolo会自动帮我们跳过这些损坏的图片，**遂不处理**，9的问题则限制最大多线程，具体参考这篇文章，剩下解决过程在**ERROR6**。

    ![image-20240416125607129](image-20240416125607129.png)

11. 解决了一直都有的一个**ERROR**，称其**ERROR7**，一直没影响就没管，解决方法放**ERROR**，报错如下：

    `AttributeError: 'FreeTypeFont' object has no attribute 'getsize'`

12. 执行**train.py**，生成的训练成果除了**train_loss**，**val_loss**有点训练不充分，其他的数据都比较正常：

    ![results](results.png)

13. 更改**detect.py**中pause_opt函数中的`--save-txt`参数，添加`default = True`来在运行**detect.py**时自动保存标签，来辅助打标，在150张量级的训练之后，准确率已经相当高了，只有一两个是没有标上的。



## 修改后参数表

无关紧要的就不在这里面了，都是默认参数

* train.py

```python
parser.add_argument('--epochs', type=int, default=400)
```

* scratch.yaml

```yaml
lr0: 0.02  # initial learning rate (SGD=1E-2, Adam=1E-3)
lrf: 0.2  # final OneCycleLR learning rate (lr0 * lrf)
degrees: 0.1  # image rotation (+/- deg)
shear: 0.1  # image shear (+/- deg)
perspective: 0.01  # image perspective (+/- fraction), range 0-0.001
```



## ERROR



1. `wandb: ERROR api_key not configured (no-tty). call wandb.login(key=[your_api_key])`

   > 其实就是这个叫wandb的东西没登录上，按照我给的[解决文档](https://blog.csdn.net/weixin_52890053/article/details/132111731)很快就搞定了

2. numpy版本太新

	![image-20240411013842130](image-20240411013842130.png)
	
	> 解决方案，根据你安装的YOLO包的**requirement.txt**去换**numpy**版本，以下提供几个可用命令
	>
	> ```
	> pip uninstall packname
	> # pip卸载指定包
	> pip install packname==version_number
	> # pip安装制定版本的包
	> ```
	>
	> 途中重装了很多次包，找到比较稳定的版本：**1.20.3**（谢谢你浪费我那么久来试😅）

* 新版torch不会自动转换浮点型为整型

  [解决方案](https://blog.csdn.net/m0_69290797/article/details/134759944)

3. `DLL load failed while importing _imaging`

   > pillow版本过高导致的，参考该[文档](https://zhuanlan.zhihu.com/p/662305030)，看看对应python版本，降一降版本就行了

4. bitch-size开太大

   `RuntimeError: DataLoader worker (pid(s) 16272) exited unexpectedly`

   我的卡太垃圾了，显存遭不住😩

   [参考文档](https://blog.csdn.net/KaelCui/article/details/106184158)

5. NMS时间阈值太低

   `WARNING: NMS time limit 10.0s exceeded`

   需要修改一个叫做**time_limit**，具体原理在[这篇文章](https://blog.csdn.net/baidu_39629638/article/details/128182056)，但是我用的版本**time_limit**参数设置不在**val.py**里面，而是在**general.py**里面，具体位置如下：

   ![image-20240416050646905](image-20240416050646905.png)

6. OpenCV多线程超时

   `cv2.error: Caught error in DataLoader worker process 5.`

   更改一个叫做workers的参数，这个直接在**train.py**的**parse_opt函数**里面可以找到，在下图最后一行，把默认值 (default) 改成比较小的数值就行了，为0则直接是关闭多线程。

   [灵感文档](https://blog.csdn.net/canpian7/article/details/115432429)

   ![image-20240416132745538](image-20240416132745538.png)

7. 找不到名为getsize的对象

   `AttributeError: 'FreeTypeFont' object has no attribute 'getsize'`

   原理是pillow在10.0版本之后删除了**getsize**的功能，你的解释器应该找不到这个方法，getsize()的目的是为了获取字体**宽度 (w)** 和**高度 (h)** ，大部分的文章都会叫你pillow降级，但是一个配好的环境，换一个版本的库可能就会运行不了，所以将报错的所有位置的`getsize()`换成以下形式代码即可：

   ```python
   # w,h = font.getsize(text) 更改前
   
   box = font.getbbox(text)
   w, h = box[2] - box[0], box[3] - box[1]
   ```

   笔者的只在**plots.py**中找到两处：

   ![image-20240416145641680](image-20240416145641680.png)



![image-20240416145658140](image-20240416145658140.png)

	[解决方法](https://blog.csdn.net/qq_63034152/article/details/131626091)：该篇文章的评论区的大神提到的方法

## 配置

* 系统环境：win11家庭版

* 英伟达显卡：GeForce RTX 3050

* YOLOv5：6.0

* pytorch:2.2.2

  
