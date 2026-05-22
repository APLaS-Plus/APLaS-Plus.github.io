---
title: YOLOv5🚀上手记录
typora-root-url: YOLOv5🚀上手记录
date: 2024-05-11 18:54:20
category: 
   - Technology
tags:
   - YOLO
   - PyTorch
   - CUDA
---

## 名词简介

环境管理：Annaconda

技术：CUDA，Pytorch，YOLO

> 都熟悉的话可以直接翻到第二节实验过程了🫡

* **YOLO**是一个基于**Pytorch技术**，用于图像识别的模型，需要通过大量人工标记过的数据集来训练，从而达到高精准度的图像识别，他的特点是只用识别一次，YOLO便是“You only look once”的缩写，以下是官方的简介：

  ![image-20240401230711546](image-20240401230711546.png)

* **Pytorch**是Facebook人工智能研究团队研发的一个**深度学习框架**，他最强大的功能是可以调用**GPU的算力**（基于CUDA🫡）来进行模型训练，以下是官方的简介：

![image-20240402000539882](image-20240402000539882.png)

* **CUDA**是英伟达NVIDIA开发的可以利用英伟达显卡上的强大算力来进行编译，运行程序的工具包，下文会提到要想训练**YOLO**的速度快些，最好要有能借助**CUDA**的**Pytorch**版本。
* **Annaconda**是一个python的**库管理器**（Library）和**环境管理器**（ Environment），本次实验使用的环境就是Annaconda建立的，下文会提到使用原因。



## 实验过程📜

1. 首先是在官网下载[**YOLOv5的6.0**](https://github.com/ultralytics/yolov5/tree/v6.0)版本，根据需求配置环境。

> 根据官方的requirment.txt，下载必要的库之外，还需要配置**pytorch**和CUDA的环境，具体看这个[**教程**](https://www.bilibili.com/video/BV1uN411E7gV/?spm_id_from=333.880.my_history.page.click&vd_source=99294a2a1c5504f559670de616463ae4)，全程几乎傻瓜式配置方法，原理是使用**Annaconda**来创建一个虚拟的python环境，隔绝系统环境带来的影响（你干的好啊😍），这个视频没有教怎么安装**CUDA**（先看下面注释），这里贴个[**官网**](https://developer.nvidia.com/cuda-toolkit)吧。
>
> > 注：没有CUDA也可以跑这个模型，但是CPU跑的太慢了受不了😑。
>
> > 值得强调的一点YOLO对pytorch的版本要求不是很高，但是pytorch对CUDA的要求极其高，参考其[**官网**](https://pytorch.org/get-started/locally/)，文档很详细，里面描述一个pytorch版本必须对应一个特别的CUDA版本，也就是不具备兼容性。

2. 然后是人工对其数据集**datasets**进行人工标记哪些物品是哪些（俗称打标🤐，谷歌很多机器人验证其实也是用于收集打标数据），因为机器学习和人一样需要学习资料参考，这里使用的是一位大神开发的开源网站，也可以部署到本地用，叫[**Makesense**](https://www.makesense.ai/)，操作的话在第四步的链接里面开始有提到。
3. 打完标之后在YOLOv5的文件夹下面新建自己的**数据目录**（datasets），图片库中创建训练集train2017，测试集val2017，名字什么的可以自己起，会改配置文件就行😏，数据集按什么比例分成训练集和测试集按自己喜好，我的比例接近7:1，标签库中同理，结构如下图：

![](image-20240401201729529.png)

4. 根据**学长的[教程](https://blog.csdn.net/m0_63292184/article/details/136963850?spm=1001.2014.3001.5501)**改相应的数值（第三节配置参数开始看），也就是调整模型以适配你的需求，核心参数在注释中提，按照调整顺序。标签和标签数量一定要和你打标时设置的一样，这个在坑点2会有所介绍。

   > * train.py中需要修改的参数
   >
   >   weights -- 训练时使用的模型权重文件，后缀.pt
   >
   >   cfg -- 模型参数配置文件
   >
   >   data -- 模型数据文件，里面存有标签数，标签类型
   >
   >   hyp -- 模型训练参数
   >
   >   batch-size -- 占用算力
   >
   >   evole -- 优化次数
   >
   >   device -- 设备，其实就是用于调用NVIDIA显卡的参数
   >
   >   workers -- 同时加载数（推测是）
   >
   >   patience -- 迭代后没有进步后最多走多少步
   >
   >   epochs -- 参考一些文档的描述，是数据集会被用于运算多少次的意思
   >
   > * data指向的文件，这里是初始的coco128.yaml
   >
   >   path -- 指向你设置的数据集，后两个为训练集和测试集对应的文件夹
   >
   >   nc -- 总标签数
   >
   >   name -- 标签名集合
   >
   > * cfg指向的文件，即模型本体
   >
   >   nc -- 总标签数
   >
   > * hyp指向的文件，即训练参数文件
   >
   >   lf0 -- 初始学习率
   >
   >   lrf -- 最终学习率
   >
   >   degree -- 识别图片旋转过的程度
   >
   >   shear -- 识别图片有没有被剪切过的程度
   >
   >   perspective -- 识别图片有没被遮挡的程度

5. 最后就是运行程序了，相信你看完教程之后用的是pycharm来运行的，直接观察运行结果，打开**runs文件夹**，你设置的训练集的**最后一次训练结果**的文件夹。

   > 例如我这里的路径是 `.\runs\train2017\exp38`

   这里面就有你的训练结果了，这里展示一下我的results.jpg（有点差虽然，因为拟合曲线不算特别平滑，可能是数据集的问题🤨）：

   ![](results.png)

	数据集的问题在上面[学长的文档](https://blog.csdn.net/m0_63292184/article/details/136963850?spm=1001.2014.3001.5501)里面有提到过训练得不好的处理方法，在此不多赘述，个人认为我的训练结果没什么太大问题，里面的参数我只能看懂一些，准确率**precision**，召回率**recall**，训练丢失率**loss**，其他的会在后期学习上遇到，在此不多补充。



## 坑点集合😅

1. 鉴于python的读取机制，容易出现的一个问题是读取的时候**编码错误**，形式如下：

   `UnicodeDecodeError: ‘gbk‘ codec can‘t decode byte 0x80 in position 198: illegal multibyte sequence`

   对于这个包主要针对的是yaml类配置文件，官方大聪明在更新的时候放了个火箭的emoji（🚀就这个）进去还有注释中辅助寻找原始文件的友好注释里面，加了个箭头（“←”就这个），删掉才能正常运行。
   
   原理是pyhton识别不了这类字符，他们不在utf-8和GBK的编码体系中，类似下面这种情况：
   
   ![image-20240402171214308](image-20240402171214308.png)

> 参考文档：[小火箭“🚀”删除](https://wanghao.blog.csdn.net/article/details/128225609?spm=1001.2101.3001.6650.10&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromBaidu%7ERate-10-128225609-blog-122971106.235%5Ev43%5Epc_blog_bottom_relevance_base7&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromBaidu%7ERate-10-128225609-blog-122971106.235%5Ev43%5Epc_blog_bottom_relevance_base7) [左箭头“←”删除](https://blog.csdn.net/shuangshuangboole/article/details/131420080?spm=1001.2014.3001.5502)

2. 这个坑点会遇到完全是因为开始学的时候照搬了学长的教程。`data.yaml`中**nc**的值一定要是你**测试集中的类别数**，否则出现报错如下，意思是存在标签编号大于标签数的情况：

   ![image-20240402172046895](image-20240402172046895.png)

> 参考文档：[该网址的2.1节](https://www.cnblogs.com/zhaoyingjie/p/14620817.html)
