---
title: UR7e Robotic Arm Remote Control Setup Guide
category:
  - Technology
tags:
  - UR7e
  - ROS2
  - MoveIt
  - Robotics
typora-root-url: UR7e Robotic Arm Remote Control Setup Guide
date: 2026-05-30 00:00:00
---


> 📖 中文版本 / Chinese Version：{% post_link UR7e机械臂工作站远程操控记录 %}

## Introduction

This post documents the complete workflow for setting up remote control of a UR7e robotic arm from scratch — covering SSH configuration on the arm side, URCap plugin installation, and ROS2 Driver + MoveIt setup on the workstation side. Suitable for readers who already have basic hands-on experience with the UR7e and want to integrate it into the ROS ecosystem 🫡.

<iframe src="https://player.bilibili.com/player.html?bvid=BV19EV56YEPz&page=1&high_quality=1&danmaku=0"
    scrolling="no" border="0" frameborder="no" framespacing="0"
    allowfullscreen="true"
    style="width:100%; aspect-ratio:16/9;">
</iframe>

## Arm-Side Configuration

### Enabling Remote SSH

Default credentials for the robotic arm (use your custom password if you've changed it):

- Username: `root`
- Password: `the password you set` (initial default is `easybot`, changeable via the teach pendant)
- Port: `22`

On the teach pendant, verify the following settings:

1. The arm must be connected in **Local Mode**
2. **Safety > General**: leave all rules blank (no entries)
3. **Safety > General**: enable **Allow SSH** and **Allow Port Forwarding**
4. **System > Remote Control**: enable

> After configuration, test the SSH connection before proceeding to the next step.

### Installing the External Control URCap

Download the official remote control plugin [externalcontrol-1.0.5.urcap](https://github.com/UniversalRobots/Universal_Robots_ExternalControl_URCap/releases/download/v1.0.5/externalcontrol-1.0.5.urcap), then upload it to the arm via SCP:

```shell
scp ~/Downloads/externalcontrol-1.0.5.urcap root@$ARM_IP:/programs/
```

On the teach pendant:

1. Navigate to **Settings > System > URCap**
2. Unlock with the admin password
3. Click the **+** button under URCap info, locate `externalcontrol-1.0.5.urcap`, add it, and **reboot** the device

### Configuring External Control

After reboot, go to **Installation Settings > URCap** — you should see a new **External Control** option:

- Set **Host IP** and **Host Name** to your workstation's static IP (referred to as `<STATION_IP>` below), e.g., `192.168.1.110`

> For safety, save a separate configuration: click **Save > Save Installation Settings** at the top and give it a name.

Also note: **Installation Settings > Fieldbus** must be completely disabled (unless you specifically need it), otherwise the next step will throw an error.

## Workstation-Side Configuration

### Installing UR Driver

Install the ROS package UR Driver on your workstation, then launch the connection:

```shell
ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur7e robot_ip:=$ARM_IP launch_rviz:=true
```

An RViz window should appear, with the arm's pose matching the physical robot.

![loading](thumbnailwebp.webp)

### Creating the Teach Pendant Control Program

On the teach pendant, create an empty program under **Programs**. Go to **URCaps**, find **External Control**, and insert it. The program structure should look like:

```
Robot Program
  -> Control by <STATION_IP>
```

Nothing else is needed. Save the program (e.g., as `ec.urp`) for quick reuse later.

## Connection Testing

### Verify Controller Status

Without closing the original terminal, open a new one and run:

```shell
source /opt/ros/humble/setup.bash
ros2 control list_controllers
```

You should see the following output, indicating a successful connection:

```
joint_state_broadcaster                active
scaled_joint_trajectory_controller     active
io_and_status_controller               active
speed_scaling_state_broadcaster        active
```

### Verify Joint State Messages

Confirm that joint state messages are being received correctly:

```shell
ros2 topic echo /joint_states --once
```

Expected output should resemble:

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

### Verify MoveIt Configuration

```shell
ros2 pkg prefix ur_moveit_config
```

Should return something like:

```
/opt/ros/humble
```

## Controlling the Arm with MoveIt

Launch MoveIt:

```shell
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur7e launch_rviz:=true
```

An RViz window will appear. The **MotionPlanning** panel in the bottom-left corner is where you control the arm:

1. MotionPlanning → Planning → Planning Group: select `ur_manipulator`
2. In the 3D view, you should see a **semi-transparent / colored end-effector target pose marker** near the tip of the arm

![loading](thumbnailwebp-17801363313762.webp)

Gently drag to adjust the pose (keep movements small during testing), click **Plan** to preview the trajectory, then click **Execute**. If the arm moves — congratulations 👍!

## Summary

Remote control of the UR7e requires at least these three steps. The commands below can be used as a simple script for quickly launching the arm control program:

```shell
# 1. Workstation establishes the connection
ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur7e robot_ip:=$ARM_IP launch_rviz:=false

# 2. On the teach pendant, open the connection program (saved as ec.urp)

# 3. Workstation launches the control program (MoveIt manual control shown here; replace with other programs as needed)
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur7e launch_rviz:=true
```

## References

- [Universal Robots External Control URCap](https://github.com/UniversalRobots/Universal_Robots_ExternalControl_URCap)
- [UR Robot Driver - ROS2](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver)
