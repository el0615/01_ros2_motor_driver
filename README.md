# ROS2 Motor Driver with Isaac Sim

> A ROS2-based mobile robot control project developed from fundamental ROS2 concepts to real-time robot control in NVIDIA Isaac Sim.

---

## Overview

This project was built to learn the complete ROS2 communication pipeline by developing a custom mobile robot controller from scratch.

Starting from basic ROS2 node creation, the project gradually evolved into a complete control system capable of operating the Nova Carter robot in NVIDIA Isaac Sim.

---

## Learning Progress

The project was developed step by step through the following milestones.

| Step | Topic |
|------|-----------------------------|
| DN-001 ~ DN-006 | ROS2 Fundamentals |
| DN-007 | Publisher & Subscriber |
| DN-008 | Build & Source |
| DN-009 | Twist Message |
| DN-010 | Motor Driver Refactoring |
| DN-011 | Keyboard Teleoperation |
| DN-012 | Launch File |
| DN-013 | ROS2 Parameters |
| DN-014 | ROS2 Logging |
| DN-015 | QoS Profile |
| DN-016 | Timer |
| DN-017 | Isaac Sim Integration |

---

## Features

- Custom ROS2 command node
- Keyboard teleoperation
- Publisher / Subscriber communication
- geometry_msgs/Twist message
- Adjustable linear & angular velocity
- ROS2 Parameters
- ROS2 Logging
- QoS configuration
- Timer-based publishing
- Launch file
- NVIDIA Isaac Sim integration
- Nova Carter control
- Action Graph

---

## System Architecture

Keyboard
↓
command_node
↓
Twist (/cmd_vel)
↓
ROS2 Subscribe Twist
↓
Differential Controller
↓
Articulation Controller
↓
Nova Carter

---

## Demo

The project demonstrates:

- Forward
- Backward
- Left Turn
- Right Turn
- Stop

Demo Video

videos/project1_demo.mp4

---

## Technologies

- ROS2 Jazzy
- Python
- NVIDIA Isaac Sim
- Nova Carter
- Ubuntu 24.04

---

## Future Work

- Odometry Feedback
- Closed-loop Motion Control
- Automatic Motion
- Navigation2
- Person Tracking

---

## Status

Completed