# Metal-3D-Printer --- CoppeliaSim Simulation

This repository contains the simulation environment, URDF files, and control scripts for a Cartesian Robot (XYZ) using **CoppeliaSim** (formerly V-REP).

## 📋 Overview
The main goal of this project is to simulate the kinematics and dynamics of a custom Cartesian manipulator for [insert application, e.g., Additive Manufacturing / Pick-and-Place]. The simulation leverages a URDF description imported from CAD to ensure physical accuracy.

**Key Features:**
* **Degrees of Freedom (DoF):** 3 (Linear X, Y, Z axes).
* **Format:** URDF (Unified Robot Description Format) based.
* **Physics Engine:** [e.g., Bullet / Newton / ODE].
* **Control Interface:** [e.g., ZeroMQ Remote API (Python) / Embedded Lua Scripts].

## 🚀 Prerequisites
To run this simulation, you will need:

* **[CoppeliaSim](https://www.coppeliarobotics.com/downloads)** (Edu or Pro version, release X.X or newer).
* **Python 3.8+** (if using external control scripts).
* **Libraries:**
  ```bash
  pip install pyrep numpy
