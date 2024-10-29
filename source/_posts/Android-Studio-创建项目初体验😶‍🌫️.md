---
title: Android Studio|创建安卓项目初体验😶‍🌫️
typora-root-url: Android Studio|创建安卓项目初体验😶‍🌫️
date: 2024-10-16 15:44:48
category:
tags:
---

## 引言

嗨嗨嗨，也是时隔接近五个月没有更新了，这次就记录一下我学习安卓开发的过程吧！起因是最近有着想学习做个打卡机app，附加番茄钟的功能，然后顺便给自己寻找一些新爱好，于是选择学习基于kotlin的安卓开发，当然开发路途道阻且长，一开始差点没给我创死，也是遇到许多报错，下面开始介绍我的“hello world”开发过程。本文学习基于谷歌开发者提供的安卓开发教程——[Android 之 Compose 开发基础](https://developer.android.com/courses/android-basics-compose/course?hl=zh-cn)。

> 先写好，不推荐大家走安卓开发方向，作者在此也是仅仅作为爱好，国内安卓开发需求小，不容易找工，向本校的一位优秀学长讨教的时候就被他劝退了。

## 历程

首先安利一波在github上找到的学习资源——[awesome-kotlin](https://github.com/Heapy/awesome-kotlin)。这是近期仍然在更新的kotlin资料汇总，因此一开始选择的资源平台就是这里，前文提到的谷歌开发者教程也是在这找的，说实话比kotlin官方教程好些（指不收费）。

![image-20241016155741803](/../Android-Studio-创建安卓项目初体验😶‍🌫️/image-20241016155741803.png)

跟着第一步，安装Android Studio，跟着教程创建空模版，耐心等待，也是“hello world”上了，跟着教程创建一个UI样式🤪
![image-20241016163526374](/../Android-Studio-创建项目初体验😶‍🌫️/image-20241016163526374.png)

接着在创建模拟器的时候就有问题了，启动时报错：

![image-20241016193127195](/../Android-Studio-创建项目初体验😶‍🌫️/image-20241016193127195.png)

但是说实话这个并不详细，晚上查了许多解决方案都指向这个报错，参考[解决 Android studio 出现“The emulator process for AVD xxx has terminated.”的错误](https://www.jianshu.com/p/fc278242453c)，发现我的是因为c盘存储空间不够了。

```
2024-10-16 19:31:15,514 [18292406]   WARN - Emulator: Tianji API 30 - Not enough space to create userdata partition. Available: 6176.437500 MB at C:\Users\lzw20\.android\avd\..\avd\Tianji_API_30.avd, need 7372.800000 MB.
```

接着参考这篇文章——[Android Studio磁盘空间不足：Emulator: emulator: ERROR: Not enough space to create userdata partition](https://blog.csdn.net/weixin_45410882/article/details/106218813)，把虚拟机移动到空间更大的位置，虚拟机也是启动成功了😭，并且展示了在main函数中使用过的元素。

![image-20241016200007990](/../Android-Studio-创建项目初体验😶‍🌫️/image-20241016200007990.png)
