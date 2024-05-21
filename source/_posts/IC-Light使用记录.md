---
title: IC-Light使用记录
typora-root-url: IC-Light使用记录
date: 2024-05-21 22:44:39
category:
tags:
---

## 简介

IC-Light全称 **\"Imposing Consistent Light\"** ，意为施加固定光源，其实就是图片加光影的意思，基于什么模型，具体什么原理笔者还没看，下面贴了官网链接，读者可以略览一番🫡。

## 官网与需要的环境配置

官网：[IC-Light](https://github.com/lllyasviel/IC-Light)

官方体验网：[IC-Light (Relighting with Foreground Condition)](https://huggingface.co/spaces/lllyasviel/IC-Light)

环境配置：conda、cuda（按适合自己电脑的来就行）

## 实验过程

1. 先上官网，按照指示下载（⚠注意！执行最后一句的时候需要挂魔法下载模型才能使用）：

   ```shell
   git clone https://github.com/lllyasviel/IC-Light.git
   cd IC-Light
   conda create -n iclight python=3.10
   conda activate iclight
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   pip install -r requirements.txt
   python gradio_demo.py
   ```

   > 没挂梯子执行最后会出现类似报错，意思就是不能登上某个网址：
   >
   > ```python
   >   warnings.warn(
   > Traceback (most recent call last):
   >   File "E:\IC-Light\gradio_demo.py", line 22, in <module>
   >     tokenizer = CLIPTokenizer.from_pretrained(sd15_name, subfolder="tokenizer")
   >   File "E:\Anaconda3\envs\iclight\lib\site-packages\transformers\tokenization_utils_base.py", line 2012, in from_pretrained
   >     raise EnvironmentError(
   > OSError: Can't load tokenizer for 'stablediffusionapi/realistic-vision-v51'. If you were trying to load it from 'https://huggingface.co/models', make sure you don't have a local directory with the same name. Otherwise, make sure 'stablediffusionapi/realistic-vision-v51' is the correct path to a directory containing all relevant files for a CLIPTokenizer tokenizer.
   > ```
   >
   >   连了就可以正常下载模型了：
   >
   > ![image-20240521225308392](image-20240521225308392-17163031926041.png)

2. 运行之后发现有好几次都是出现下面这种情况，出现网址但是无法连接（已解决，看第三步）：

   > ```python
   > Running on local URL:  http://0.0.0.0:7860
   > 
   > To create a public link, set `share=True` in `launch()`.
   > ```

​		根据提示，在主文件`gradio_demo.py`的最后一行给`launch()`函数加上值`share=True`。但是改了还是不能用，推测这个函数是用来发布到互联网上给别人用的，不是本地用的。

3. 笔者将`launch()`里面的`server_name`参数删掉，就可以正常访问了，原因未知。

4. 我们在下面的菜单里面挑好参数，就可以开始跑了。

   这是在官网体验网站使用的效果（体验网站这里提示词写了赛博朋克街道）：

   ![image-20240522003648241](image-20240522003648241-17163094106322.png)

   这是本地跑的效果（本地这里提示词写了太阳下，光影调成了背光）：

   ![image-20240522011036599](image-20240522011036599.png)

   看着还不错🫡，甚至耳朵的透光他也理解了，就是这个后腿，模型应该理解成肥腿猫了😏。

   ![img](image (1).jpeg)

   就是这个时间。。

   ![image-20240522004047353](image-20240522004047353.png)

   第四张图我的3050要加载半小时，直接硬控半小时，加上过程中GPU显存就没有不是满的时候😭。

   ![image-20240522010703772](image-20240522010703772.png)

## 后续打算

一开始是在[IT咖啡馆](https://space.bilibili.com/65564239?spm_id_from=333.788.0.0)的视频上看到的：

[「Github一周热点23」实用的IT工具箱，AI开发框架和知识库平台等5个火爆项目](https://www.bilibili.com/video/BV1Cw4m1D7GA/?spm_id_from=333.999.0.0&vd_source=99294a2a1c5504f559670de616463ae4)

看了觉得可以朋友圈修图，应该是很好用的。体验下来，觉得在本地跑很浪费时间，这个官网有一个体验网，可以在上面简单体验一下，本地跑大可不必，感觉有点伤显卡。

后续应该会用这个修一些发朋友圈的图，并且研究一下他的论文。
