---
title: UR7e Practical ROS Commands & Communication Ports Reference
category:
  - Technology
tags:
  - UR7e
  - ROS2
  - Robotics
  - Dashboard
typora-root-url: UR7e Practical ROS Commands & Communication Ports Reference
date: 2026-06-01 00:00:00
---


> 📖 中文版本 / Chinese Version：{% post_link UR7e实用ros指令表与通信端口指令表 %}

## Introduction

Operating a robotic arm via teach pendant in everyday project workflows is neither efficient nor automated enough. The UR7e offers rich ROS2 interfaces and Dashboard communication ports, allowing you to perform state queries, trajectory control, and remote start / stop entirely via command line. This post serves as a practical quick-reference for the most frequently used ROS topic commands, controller state management, joint trajectory control, and Dashboard TCP commands in daily development and debugging 🦾.

> ⚠️ Prerequisite for all commands in this post: the UR Driver connection must already be established.

## Reading States via ROS2

### Read Joint States

```shell
ros2 topic echo /joint_states --once
```

### Read TCP Pose

```shell
ros2 topic echo /tcp_pose_broadcaster/pose --once
```

### Read Speed Scaling

```shell
ros2 topic echo /speed_scaling_state_broadcaster/speed_scaling --once
```

### Check Controller Status

```shell
ros2 control list_controllers | grep scaled_joint_trajectory_controller
```

## Controller Status Overview

### Must-Be-Active Controllers

These controllers are the core of real-robot operation — lacking any one of them breaks normal functionality:

| Controller / Broadcaster             |  Status |   Required   | Purpose                                                                                  |
| ------------------------------------ | :-----: | :----------: | ---------------------------------------------------------------------------------------- |
| `joint_state_broadcaster`            | active  | **Required** | Publishes `/joint_states`; RViz / MoveIt / state queries all depend on it                    |
| `speed_scaling_state_broadcaster`    | active  | **Required** | Publishes speed scaling; `scaled_joint_trajectory_controller` depends on it                   |
| `scaled_joint_trajectory_controller` | active  | **Required** | Primary trajectory controller; used by MoveIt Execute / `ros2 action send_goal`              |
| `io_and_status_controller`           | active  | Recommended  | Read / write IO, robot status, auxiliary Dashboard states                                      |
| `tcp_pose_broadcaster`               | active  | Recommended  | Publishes TCP pose for reading end-effector position                                          |
| `force_torque_sensor_broadcaster`    | active  | Recommended  | Publishes force-torque sensor data                                                            |
| `ur_configuration_controller`        | active  | Recommended  | Reads UR configuration and calibration info                                                   |

### Unnecessary Controllers

These controllers are irrelevant to your use case — leave them inactive:

| Controller                          |  Status  |   Required   | Notes                                                                               |
| ----------------------------------- | :------: | :----------: | ----------------------------------------------------------------------------------- |
| `joint_trajectory_controller`       | inactive | Not required | Generic trajectory controller; you're using `scaled_joint_trajectory_controller`    |
| `forward_position_controller`       | inactive | Not required | Direct position control, not needed for normal trajectory control                    |
| `forward_velocity_controller`       | inactive | Not required | Direct velocity control, not needed for normal trajectory control                    |
| `forward_effort_controller`         | inactive | Not required | Direct torque / effort control, generally not used with standard UR hardware             |
| `force_mode_controller`             | inactive | Not required | Only used for UR force mode                                                        |
| `passthrough_trajectory_controller` | inactive | Not required | Only used for passthrough trajectory mode                                           |
| `freedrive_mode_controller`         | inactive | Not required | Only used for freedrive (hand-guiding) mode                                         |
| `tool_contact_controller`           | inactive | Not required | Only used for tool contact detection                                                |
| `friction_model_controller`         | inactive | Not required | Friction model related; does not affect basic control                               |

## Joint Trajectory Control

### Basic Action Template

```shell
ros2 action send_goal /scaled_joint_trajectory_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory "{trajectory: {joint_names: [shoulder_pan_joint, shoulder_lift_joint, elbow_joint, wrist_1_joint, wrist_2_joint, wrist_3_joint], points: [{positions: [q0, q1, q2, q3, q4, q5], time_from_start: {sec: 3, nanosec: 0}}]}}"
```

In essence, this sends a **joint trajectory goal** to the `scaled_joint_trajectory_controller`.

### Template Breakdown

Expanding the command:

```shell
ros2 action send_goal \
  /scaled_joint_trajectory_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "{trajectory: {joint_names: [...], points: [{positions: [...], time_from_start: {...}}]}}"
```

Field-by-field explanation:

| Field | Description |
| :--- | :--- |
| `ros2 action send_goal` | CLI command to send an action goal |
| `/scaled_joint_trajectory_controller/follow_joint_trajectory` | Target controller (UR-recommended speed-scaled trajectory controller) |
| `control_msgs/action/FollowJointTrajectory` | Action message type: "follow a joint trajectory" |
| `trajectory` | The trajectory definition |
| `joint_names` | Which joints this trajectory controls |
| `points` | List of trajectory waypoints (one or more) |
| `positions` | Target angle for each joint, in **radians** |
| `time_from_start` | Time to reach this waypoint from trajectory start |

### Concrete Example

```shell
ros2 action send_goal /scaled_joint_trajectory_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory "{trajectory: {joint_names: [shoulder_pan_joint, shoulder_lift_joint, elbow_joint, wrist_1_joint, wrist_2_joint, wrist_3_joint], points: [{positions: [-0.521943, -1.571192, -1.527148, -1.613868, 1.631616, 1.426293], time_from_start: {sec: 3, nanosec: 0}}]}}"
```

Joint-to-position mapping:

| Joint Name           | Position   | Description                        |
| :------------------- | :--------- | :--------------------------------- |
| `shoulder_pan_joint`  | -0.521943  | Base horizontal rotation joint     |
| `shoulder_lift_joint` | -1.571192  | Shoulder lift joint                |
| `elbow_joint`         | -1.527148  | Elbow joint                        |
| `wrist_1_joint`       | -1.613868  | Wrist 1 joint                      |
| `wrist_2_joint`       | 1.631616   | Wrist 2 joint                      |
| `wrist_3_joint`       | 1.426293   | Wrist 3 joint                      |

### ⚠️ Key Points

**`positions` are absolute joint angles, not increments.**

Example: if the current `wrist_3_joint` is `1.396293` and the command sets `1.426293`, the actual movement is only:

$$
1.426293 - 1.396293 = 0.03 \ \mathrm{rad} \approx 1.72^\circ
$$

**`time_from_start` controls speed:**

- `time_from_start: {sec: 3, nanosec: 0}` means reach the target in **3 seconds**
- Shorter time → faster motion; longer time → slower motion

**Multiple waypoints:**

```yaml
points:
  - positions: [...]
    time_from_start: {sec: 2}
  - positions: [...]
    time_from_start: {sec: 5}
```

- Reach the first waypoint by second 2
- Reach the second waypoint by second 5

**`joint_names` order must match `positions` order exactly:**

The order in `/joint_states` output may NOT match what the action expects. Always use this fixed order for `joint_names`:

```
shoulder_pan_joint  shoulder_lift_joint  elbow_joint  wrist_1_joint  wrist_2_joint  wrist_3_joint
```

Then fill `positions` values in the same order.

## Remote Control via Dashboard

UR's communication interface documentation allows us to control the Dashboard remotely over TCP — no teach pendant required.

![](1780280070135.png)

### Basic Command Format

```shell
timeout 2 bash -c 'printf "command\n" | nc $ARM_IP 29999'
```

> Replace `$ARM_IP` with your arm's actual IP, e.g. `192.168.1.100`.

### Common Dashboard Commands

For the full command reference, see the official docs: [UR Dashboard Server Commands](https://www.universal-robots.com/manuals/EN/HTML/SW5_25/Content/prod-dashboard/Dashboard_table.htm)

| Command | Purpose |
| :--- | :--- |
| `robotmode`                 | Query robot mode (`IDLE` / `RUNNING`, etc.)       |
| `safetystatus`              | Query safety status (`NORMAL`, etc.)              |
| `programState`              | Query current program state                       |
| `load external_control.urp` | Load the saved External Control program           |
| `play`                      | Start the current program                         |
| `stop`                      | Stop the current program                          |
| `pause`                     | Pause the current program                         |
| `is in remote control`      | Check if in Remote Control mode                   |

### Usage Examples

```shell
# Check current mode
timeout 2 bash -c 'printf "robotmode\n" | nc $ARM_IP 29999'

# Load and start the External Control program
timeout 2 bash -c 'printf "load external_control.urp\n" | nc $ARM_IP 29999'
timeout 2 bash -c 'printf "play\n" | nc $ARM_IP 29999'

# Stop the program
timeout 2 bash -c 'printf "stop\n" | nc $ARM_IP 29999'
```

Combining Dashboard commands with scripts can significantly streamline the arm's start / stop workflow — a key piece of automated deployment 💡.

## Port & Function Reference

The UR7e exposes multiple communication ports. Choose the right interface for the right task:

| Use Case | Recommended Interface |
| :--- | :--- |
| Execute trajectory optimization results | `scaled_joint_trajectory_controller` |
| MoveIt / CuRobo integration | ROS2 Driver |
| Real-time state reading | ROS topics; RTDE if needed |
| Auto load / start programs | Dashboard `29999` |
| Ad-hoc URScript testing | Primary / Secondary Client Interface |
| Gripper / peripherals | Prefer ROS / URCap / Modbus; Socket if necessary |
| PLC / industrial line integration | Modbus / EthernetIP / Profinet |

## Summary

This post covers the most practical ROS2 commands and communication port references for UR7e development and debugging:

1. **State Reading** — `ros2 topic echo` for quick joint state, TCP pose, and speed scaling queries
2. **Controller Management** — `ros2 control list_controllers` to verify controller status and distinguish required vs. optional
3. **Trajectory Control** — `ros2 action send_goal` to send joint trajectory goals; watch out for absolute positions and joint order
4. **Dashboard Remote** — TCP port `29999` for program load / play / stop, no teach pendant needed
5. **Port Selection** — Different tasks call for different interfaces; use the reference table above

Consider wrapping these commands into scripts or shell aliases for a noticeable debugging speed boost 🚀.

## References

- [UR Dashboard Server Commands](https://www.universal-robots.com/manuals/EN/HTML/SW5_25/Content/prod-dashboard/Dashboard_table.htm)
- [Universal Robots External Control URCap](https://github.com/UniversalRobots/Universal_Robots_ExternalControl_URCap)
- [UR Robot Driver - ROS2](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver)
