---
title: UR7e机械臂工作站远程操控记录
category:
  - Technology
tags:
  - UR7e
  - ROS2
  - MoveIt
  - 机械臂
typora-root-url: UR7e机械臂工作站远程操控记录
date: 2026-05-30 00:00:00
---

> 📖 English Version / 英文版本：{% post_link UR7e-Remote-Control-Setup %}

## 简介

本文记录了从零配置 UR7e 机械臂远程操控的完整流程，包括机械臂端 SSH 开启、URCap 插件安装，以及工作站端 ROS2 Driver 和 MoveIt 的配置。适合已经上手 UR7e 基本操作、需要接入 ROS 生态的读者🫡。

<iframe src="https://player.bilibili.com/player.html?bvid=BV19EV56YEPz&page=1&high_quality=1&danmaku=0"
    scrolling="no" border="0" frameborder="no" framespacing="0"
    allowfullscreen="true"
    style="width:100%; aspect-ratio:16/9;">
</iframe>

## 机械臂端配置

### 开启远程 SSH

机械臂默认账户密码如下（如果之前改过密码则以你修改后的为准）：

- 用户名：`root`
- 密码：`the password you setted`（初始密码为 `easybot`，示教器上面可以更改）
- 端口：`22`

在示教器上确认以下设置：

1. 机械臂开**本地模式**下连接
2. **安全性 > 一般**：不要写任何规则，保持全空
3. **安全性 > 一般**：允许 SSH、允许端口转发，两项均打开
4. **系统 > 远程控制**：启用

> 配置完成后先测试能否 SSH 上去，确认通畅再进行下一步。

### 安装 External Control URCap

下载官方远程连接插件 [externalcontrol-1.0.5.urcap](https://github.com/UniversalRobots/Universal_Robots_ExternalControl_URCap/releases/download/v1.0.5/externalcontrol-1.0.5.urcap)，然后通过 SCP 上传到机械臂：

```shell
scp ~/Downloads/externalcontrol-1.0.5.urcap root@$ARM_IP:/programs/
```

上传后在示教器上操作：

1. 进入**设置 > 系统 > URCap**
2. 管理员密码解锁
3. 点 URCap 信息下面的加号，找到 `externalcontrol-1.0.5.urcap`，添加后**重启设备**

### 配置 External Control

重启后进入**安装设置 > URCap**，可以看到多了个 **External Control** 选项：

- 将 **Host IP** 和 **Host Name** 改成工作站静态 IP（下文用 `<STATION_IP>` 表示），例如 `192.168.1.110`

> 为了安全起见，建议单独保存一份设置：点中间上面的**保存 > 保存安装设置**，起个名字保存即可。

另外需要注意：**安装设置 > 现场总线**需要全部关掉（除非确实有用），否则下一步执行会报错。

## 工作站端配置

### 安装 UR Driver

工作站需要安装 ROS 包 UR Driver，然后运行以下命令启动连接：

```shell
ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur7e robot_ip:=$ARM_IP launch_rviz:=true
```

运行后会弹出一个 RViz 窗口，里面机械臂的位姿应当和真实机械臂一致。

![loading](thumbnailwebp.webp)

### 创建示教器控制程序

到示教器**程序**处创建一个空程序，到 URCaps 里面找到 **External Control**，点一下，让程序结构大致如下：

```
Robot Program
  -> Control by <STATION_IP>
```

其他什么也不要有。可以保存一份程序（比如 `ec.urp`），方便以后直接打开。

## 连接测试

### 确认控制器状态

别关终端，开新终端输入：

```shell
source /opt/ros/humble/setup.bash
ros2 control list_controllers
```

应当看到以下输出，说明受控连接成功：

```
joint_state_broadcaster                active
scaled_joint_trajectory_controller     active
io_and_status_controller               active
speed_scaling_state_broadcaster        active
```

### 确认关节消息

输入以下命令，确认能正常获取关节消息：

```shell
ros2 topic echo /joint_states --once
```

得到类似如下输出：

```
header:
  stamp:
    sec: 1780132790
    nanosec: 899974597
  frame_id: base_link
name:
  - shoulder_lift_joint
  - elbow_joint
  - wrist_1_joint
  - wrist_2_joint
  - wrist_3_joint
  - shoulder_pan_joint
position:
  - -1.5711990795531214
  - -1.5271751880645752
  - -1.6138745747008265
  - 1.631580114364624
  - 1.3962934017181396
  - -0.5219591299640101
velocity:
  - 0.0
  - -0.0
  - -0.0
  - -0.0
  - 0.0
  - 0.0
effort:
  - 2.3673009872436523
  - 2.242548942565918
  - 0.3209960460662842
  - -0.08298000693321228
  - -0.07773643732070923
  - 0.09178157150745392
```

### 确认 MoveIt 配置

```shell
ros2 pkg prefix ur_moveit_config
```

应当得到类似如下，确认 MoveIt 包已正确配置：

```
/opt/ros/humble
```

## 使用 MoveIt 操控机械臂

启动 MoveIt：

```shell
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur7e launch_rviz:=true
```

会弹出一个 RViz 窗口，左下角的 **MotionPlanning** 就是控制机械臂的地方：

1. MotionPlanning → Planning → Planning Group 选 `ur_manipulator`
2. 在 3D 视图中应该能看到一个**半透明 / 彩色的末端目标姿态 marker**，通常在机械臂末端附近

![loading](thumbnailwebp-17801363313762.webp)

轻微拖动调整位姿后（测试阶段不要幅度太大），点击 **Plan** 查看预览效果，确认无误后点击 **Execute**，机械臂就会动起来了。如果真动了，恭喜你👍！

## 总结

远程驱动 UR7e 至少需要以下三步，下面的程序可以作为一个简单的脚本去快捷开启机械臂控制程序：

```shell
# 1. 工作站创建连接
ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur7e robot_ip:=$ARM_IP launch_rviz:=false

# 2. 示教器打开连接程序（保存为 ec.urp，直接打开即可）

# 3. 工作站启动控制程序（这里以 MoveIt 手遥为例，可替换为其他控制程序）
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur7e launch_rviz:=true
```

## 参考资料

- [Universal Robots External Control URCap](https://github.com/UniversalRobots/Universal_Robots_ExternalControl_URCap)
- [UR Robot Driver - ROS2](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver)
