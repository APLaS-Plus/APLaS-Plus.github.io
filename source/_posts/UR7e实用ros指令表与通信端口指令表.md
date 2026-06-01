---
title: UR7e实用ROS指令表与通信端口指令表
category:
  - Technology
tags:
  - UR7e
  - ROS2
  - 机械臂
  - Dashboard
typora-root-url: UR7e实用ROS指令表与通信端口指令表
date: 2026-06-01 00:00:00
---


> 📖 English Version / 英文版本：{% post_link UR7e-ROS-Commands-and-Communication-Ports %}

## 简介

在实际项目中频繁通过示教器操作机械臂既不高效也不够自动化。UR7e 提供了丰富的 ROS2 接口和 Dashboard 通信端口，让我们可以通过命令行完成状态读取、轨迹控制和远程启停等操作。本文整理了一套实用的指令速查表，覆盖日常开发和调试中最常用到的 ROS topic 命令、控制器状态管理、关节轨迹控制以及 Dashboard TCP 命令🦾。

> ⚠️ 本文所有命令执行的前提：已通过 UR Driver 建立连接。

## ROS2 状态读取

### 读取关节位姿

```shell
ros2 topic echo /joint_states --once
```

### 读取 TCP 位姿

```shell
ros2 topic echo /tcp_pose_broadcaster/pose --once
```

### 读取速度缩放比例

```shell
ros2 topic echo /speed_scaling_state_broadcaster/speed_scaling --once
```

### 确认控制器状态

```shell
ros2 control list_controllers | grep scaled_joint_trajectory_controller
```

## 控制器状态一览

### 必须 Active 的控制器

这些控制器是实机控制的核心，缺任意一个都无法正常操作：

| Controller / Broadcaster             | 当前状态 | 是否必须 active | 用途                                                                 |
| ------------------------------------ | :------: | :---------: | -------------------------------------------------------------------- |
| `joint_state_broadcaster`            |  active  |   **必须**   | 发布 `/joint_states`，RViz / MoveIt / 状态读取都依赖它                     |
| `speed_scaling_state_broadcaster`    |  active  |   **必须**   | 发布速度缩放，`scaled_joint_trajectory_controller` 依赖它                  |
| `scaled_joint_trajectory_controller` |  active  |   **必须**   | 实机轨迹控制主控制器，MoveIt Execute / `ros2 action send_goal` 用它         |
| `io_and_status_controller`           |  active  | 建议 active  | 读写 IO、机器人状态、Dashboard 辅助状态                                       |
| `tcp_pose_broadcaster`               |  active  | 建议 active  | 发布 TCP 位姿，读末端位姿用                                                 |
| `force_torque_sensor_broadcaster`    |  active  | 建议 active  | 发布力矩传感器数据                                                        |
| `ur_configuration_controller`        |  active  | 建议 active  | 读取 UR 配置、校准等信息                                                   |

### 不需要的控制器

以下控制器在你的场景下不需要关注，保持 inactive 即可：

| Controller                          | 当前状态 | 是否必须 active | 说明                                                                     |
| ----------------------------------- | :------: | :---------: | ---------------------------------------------------------------------- |
| `joint_trajectory_controller`       | inactive |    不需要     | 普通 trajectory controller；你现在用的是 `scaled_joint_trajectory_controller` |
| `forward_position_controller`       | inactive |    不需要     | 直接位置控制，普通轨迹控制不用                                                     |
| `forward_velocity_controller`       | inactive |    不需要     | 直接速度控制，普通轨迹控制不用                                                     |
| `forward_effort_controller`         | inactive |    不需要     | 直接力矩 / effort 控制，普通 UR 实机一般不用                                          |
| `force_mode_controller`             | inactive |    不需要     | UR force mode 才用                                                       |
| `passthrough_trajectory_controller` | inactive |    不需要     | passthrough trajectory 模式才用                                            |
| `freedrive_mode_controller`         | inactive |    不需要     | freedrive 拖动模式才用                                                       |
| `tool_contact_controller`           | inactive |    不需要     | 工具接触检测功能才用                                                           |
| `friction_model_controller`         | inactive |    不必须     | 摩擦模型相关，不影响基础控制                                                      |

## 关节轨迹控制

### 基础 Action 模板

```shell
ros2 action send_goal /scaled_joint_trajectory_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory "{trajectory: {joint_names: [shoulder_pan_joint, shoulder_lift_joint, elbow_joint, wrist_1_joint, wrist_2_joint, wrist_3_joint], points: [{positions: [q0, q1, q2, q3, q4, q5], time_from_start: {sec: 3, nanosec: 0}}]}}"
```

这条命令的本质是：给 `scaled_joint_trajectory_controller` 发送一个 **关节轨迹目标**。

### 模板拆解

把上面的命令展开来看：

```shell
ros2 action send_goal \
  /scaled_joint_trajectory_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "{trajectory: {joint_names: [...], points: [{positions: [...], time_from_start: {...}}]}}"
```

各字段含义如下：

| 字段 | 含义 |
| :--- | :--- |
| `ros2 action send_goal` | ROS 2 命令行发送 action goal |
| `/scaled_joint_trajectory_controller/follow_joint_trajectory` | 发送目标给哪个控制器（UR 推荐的带速度缩放轨迹控制器） |
| `control_msgs/action/FollowJointTrajectory` | action 消息类型，表示"跟踪一条关节轨迹" |
| `trajectory` | 轨迹主体 |
| `joint_names` | 这条轨迹控制哪些关节 |
| `points` | 轨迹点列表，可以有一个点，也可以有多个点 |
| `positions` | 每个关节的目标角度，单位是 **rad** |
| `time_from_start` | 从轨迹开始到达该点的时间 |

### 实际示例

```shell
ros2 action send_goal /scaled_joint_trajectory_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory "{trajectory: {joint_names: [shoulder_pan_joint, shoulder_lift_joint, elbow_joint, wrist_1_joint, wrist_2_joint, wrist_3_joint], points: [{positions: [-0.521943, -1.571192, -1.527148, -1.613868, 1.631616, 1.426293], time_from_start: {sec: 3, nanosec: 0}}]}}"
```

命令中各关节的对应关系：

| joint name          | position    | 含义               |
| :------------------ | :---------- | :--------------- |
| `shoulder_pan_joint`  | -0.521943   | 底座水平旋转关节目标角     |
| `shoulder_lift_joint` | -1.571192   | 肩部抬升关节目标角       |
| `elbow_joint`         | -1.527148   | 肘关节目标角          |
| `wrist_1_joint`       | -1.613868   | 腕关节 1 目标角       |
| `wrist_2_joint`       | 1.631616    | 腕关节 2 目标角       |
| `wrist_3_joint`       | 1.426293    | 腕关节 3 目标角       |

### ⚠️ 关键注意事项

**positions 是绝对关节角，不是增量。**

举个例子：假设 `wrist_3_joint` 当前值是 `1.396293`，命令设置为 `1.426293`，实际只转动了：

$$
1.426293 - 1.396293 = 0.03 \ \mathrm{rad} \approx 1.72^\circ
$$

**time_from_start 控制速度：**

- `time_from_start: {sec: 3, nanosec: 0}` 表示用 **3 秒** 到达目标点
- 时间越短，动作越快；时间越长，动作越慢

**多轨迹点示例：**

```yaml
points:
  - positions: [...]
    time_from_start: {sec: 2}
  - positions: [...]
    time_from_start: {sec: 5}
```

- 第 2 秒到达第一个点
- 第 5 秒到达第二个点

**joint_names 和 positions 必须一一对应：**

`/joint_states` 输出的顺序**不一定**是 action 需要的顺序。发 action 时请固定按以下顺序填写 `joint_names`：

```
shoulder_pan_joint  shoulder_lift_joint  elbow_joint  wrist_1_joint  wrist_2_joint  wrist_3_joint
```

然后 `positions` 也按此顺序填入对应的角度值。

## Dashboard 远程控制

根据 UR 通讯接口文档，我们可以通过 TCP 端口远程控制 Dashboard，完全不需要示教器介入。

![](1780280070135.png)

### 基础命令格式

```shell
timeout 2 bash -c 'printf "命令\n" | nc $ARM_IP 29999'
```

> 注意将 `$ARM_IP` 替换为你的机械臂实际 IP，例如 `192.168.1.100`。

### 常用 Dashboard 命令

完整命令表见官方文档：[UR Dashboard Server Commands](https://www.universal-robots.com/manuals/EN/HTML/SW5_25/Content/prod-dashboard/Dashboard_table.htm)

| 命令 | 作用 |
| :--- | :--- |
| `robotmode`                 | 查看机器人模式（`IDLE` / `RUNNING` 等） |
| `safetystatus`              | 查看安全状态（`NORMAL` 等）             |
| `programState`              | 查看当前程序状态                        |
| `load external_control.urp` | 加载保存的 External Control 程序        |
| `play`                      | 运行当前程序                            |
| `stop`                      | 停止当前程序                            |
| `pause`                     | 暂停当前程序                            |
| `is in remote control`      | 判断是否处于 Remote Control 模式          |

### 实操示例

```shell
# 查看当前模式
timeout 2 bash -c 'printf "robotmode\n" | nc $ARM_IP 29999'

# 加载并运行 External Control 程序
timeout 2 bash -c 'printf "load external_control.urp\n" | nc $ARM_IP 29999'
timeout 2 bash -c 'printf "play\n" | nc $ARM_IP 29999'

# 停止程序
timeout 2 bash -c 'printf "stop\n" | nc $ARM_IP 29999'
```

Dashboard 命令配合脚本使用可以大幅简化机械臂启停流程，是自动化部署的关键一环💡。

## 端口与功能对照

UR7e 提供了多个通信端口，不同场景选用不同接口。以下对照表帮助快速定位：

| 功能 | 选用接口 |
| :--- | :--- |
| 轨迹优化结果执行 | `scaled_joint_trajectory_controller` |
| MoveIt / CuRobo 接入 | ROS2 Driver |
| 实时状态读取 | ROS topic，必要时 RTDE |
| 自动加载 / 启动程序 | Dashboard `29999` |
| 临时 URScript 测试 | Primary / Secondary Client Interface |
| 夹爪 / 外设 | 优先 ROS / URCap / Modbus；必要时 Socket |
| PLC / 工业产线集成 | Modbus / EthernetIP / Profinet |

## 总结

本文整理了 UR7e 在日常开发和调试中最实用的 ROS2 指令和通信端口命令：

1. **状态读取** — `ros2 topic echo` 快速获取关节位姿、TCP 位姿、速度缩放
2. **控制器管理** — `ros2 control list_controllers` 确认各控制器状态，分清哪些必须 active
3. **轨迹控制** — `ros2 action send_goal` 发送关节轨迹目标，注意 absolute position 和 joint order
4. **Dashboard 远程** — TCP `29999` 端口实现程序的 load / play / stop，无需示教器
5. **端口选型** — 不同需求对应不同通信接口，按表选用即可

建议把这些命令封装成脚本或 alias，调试效率会明显提升🚀。

## 参考资料

- [UR Dashboard Server Commands](https://www.universal-robots.com/manuals/EN/HTML/SW5_25/Content/prod-dashboard/Dashboard_table.htm)
- [Universal Robots External Control URCap](https://github.com/UniversalRobots/Universal_Robots_ExternalControl_URCap)
- [UR Robot Driver - ROS2](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver)
