# pykin

[![PyPI version](https://badge.fury.io/py/pykin.svg)](https://badge.fury.io/py/pykin)  [![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

Python Interface for the Robot Kinematics Library pykin

This library has been created simply by referring to <a href="https://github.com/Phylliade/ikpy.git" target="_blank">ikpy</a>

You can see a Pick and Place demo video using pykin library <a href="https://youtu.be/p9TlIp-xxbs" target="_blank">here</a> in Mujoco 

## Features

- Pure python library
- Support only URDF file
- Compute forward, inverse kinematics and jacobian, referred to the [Introduction to Humanoid Robotics book](https://link.springer.com/book/10.1007/978-3-642-54536-8).
- Check robot self-collision and collision between objects
- Path Planning (Caretsian Planning)
- Motion Planning (RRT-star)
- Plot robot kinematic chain and mesh
- Compute and visualize pick and place pose

## Installation

### Requirements

You need a [python-fcl](https://github.com/BerkeleyAutomation/python-fcl) package to do object collision checking.

- For Ubuntu, using  `apt`

  `sudo apt install liboctomap-dev`

  `sudo apt install libfcl-dev`
- For Mac, First, Download the source and build it.

  - octomap

    `git clone https://github.com/OctoMap/octomap.git`

    ~~~
    $ cd octomap
    $ mkdir build
    $ cd build
    $ cmake ..
    $ make
    $ make install
    ~~~
  - fcl

    `git clone https://github.com/flexible-collision-library/fcl.git`

    Since python-fcl uses version 0.5.0 of fcl, checkout with tag 0.5.0

    ~~~
    $ cd fcl
    $ git checkout 0.5.0
    $ mkdir build
    $ cd build
    $ cmake ..
    $ make
    $ make install
    ~~~

### Install Pykin

~~~
pip install pykin
~~~

When clone a repository, use the **--recurse-submodules** option.
The download may take a long time due to the large urdf file size.

~~~
git clone --recurse-submodules https://github.com/jdj2261/pykin.git
~~~

If you hadn't done this

~~~
$ git clone https://github.com/jdj2261/pykin.git
$ cd pykin
$ git submodule init
$ git submodule update
~~~

## Quick Start

You can see various examples in example directory

- Robot Info

  You can see 6 robot info.

  `baxter, sawyer, iiwa14, iiwa7, panda, ur5e`

  ~~~shell
  $ cd example/single_stage
  $ python robot_info.py $(robot_name)
  # baxter
  $ python robot_info.py baxter
  # saywer
  $ python robot_info.py sawyer
  ~~~

- Forward kinematics

  You can compute the forward kinematics as well as visualize the visual or collision geometry.

  ~~~shell
  $ cd example/single_stage/forward_kinematics
  $ python robot_fk_baxter_test.py
  ~~~

  |                            visual                            |                          collision                           |
  | :----------------------------------------------------------: | :----------------------------------------------------------: |
  | <img src="img/baxter_plot_visual.png" width="400" height="300"/> | <img src="img/baxter_plot_collision.png" width="400" height="300"/> |

- Inverse Kinematics

  You can compute the inverse kinematics using levenberg marquardt(LM) or newton raphson(NR) method

  ~~~shell
  $ cd example/single_stage/inverse_kinematics
  $ python robot_ik_baxter_test.py
  ~~~

- Collision check

  The image below shows the collision result as well as visualize robot using trimesh.Scene class

  ~~~shell
  $ cd example/single_stage/collision
  $ python sawyer_collision_test.py
  ~~~

  |                        trimesh.Scene                         |                            Result                            |
  | :----------------------------------------------------------: | :----------------------------------------------------------: |
  | <img src="img/sawyer_mesh_collision.png" width="200" height="200"/> | <img src="img/sawyer_collision_result.png" width="600" height="200"/> |

## Visualization

You can see visualization using matplotlib library or trimesh.Scene class.

- Visualize simple urdf using Matplotlib


  |                        ur5e                        |                        sawyer                        |                        iiwa14                        |                        panda                        |
  | :------------------------------------------------: | :--------------------------------------------------: | :--------------------------------------------------: | :-------------------------------------------------: |
  | <img src="img/ur5e.png" width="200" height="200"/> | <img src="img/sawyer.png" width="200" height="200"/> | <img src="img/iiwa14.png" width="200" height="200"/> | <img src="img/panda.png" width="200" height="200"/> |


- Visualize visual geometry using Matplotlib


  |                           ur5e                            |                           sawyer                            |                           iiwa14                            |                           panda                            |
  | :-------------------------------------------------------: | :---------------------------------------------------------: | :---------------------------------------------------------: | :--------------------------------------------------------: |
  | <img src="img/ur5e_visual.png" width="200" height="200"/> | <img src="img/sawyer_visual.png" width="200" height="200"/> | <img src="img/iiwa14_visual.png" width="200" height="200"/> | <img src="img/panda_visual.png" width="200" height="200"/> |


- Visualize collision geometry using Matplotlib


  |                             ur5e                             |                            sawyer                            |                            iiwa14                            |                            panda                             |
  | :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: |
  | <img src="img/ur5e_collision.png" width="200" height="200"/> | <img src="img/sawyer_collision.png" width="200" height="200"/> | <img src="img/iiwa14_collision.png" width="200" height="200"/> | <img src="img/panda_collision.png" width="200" height="200"/> |

- Visualize mesh about visual/collision geometry using trimesh.Scene class

  ![baxter](img/all_robot.png)

## SceneManager

- Scene 

  You can manage entire scene using SceneManager class. We recommend using the SceneManager.  
  For example, You can manage robot, object, gripper pose or collision as well as visualize their geom.   
  In addition, You can compute cartesian or motion planning.  
  You can see various examples in `example/scene` directory. 

  - Render using trimesh.Scene

    |                           baxter                           |                           sawyer                           |                           iiwa14                           |                           panda                           |
    | :--------------------------------------------------------: | :--------------------------------------------------------: | :--------------------------------------------------------: | :-------------------------------------------------------: |
    | <img src="img/baxter_scene.png" width="200" height="200"/> | <img src="img/sawyer_scene.png" width="200" height="200"/> | <img src="img/iiwa14_scene.png" width="200" height="200"/> | <img src="img/panda_scene.png" width="200" height="200"/> |

  - Render using matplotlib

    |                            baxter                            |                            sawyer                            |                            iiwa14                            |                            panda                             |
    | :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: |
    | <img src="img/baxter_scene_matplotlib.png" width="200" height="200"/> | <img src="img/sawyer_scene_matplotlib.png" width="200" height="200"/> | <img src="img/iiwa14_scene_matplotlib.png" width="200" height="200"/> | <img src="img/panda_scene_matplotlib.png" width="200" height="200"/> |

- Collision Check

  You can check collision of (robot and object), (gripper and object), (robot self collision)

  |                     Robot self collision                     |                      Robot and objects                       |                   Only gripper and objects                   |
  | :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: |
  | <img src="img/self_collision.png" width="200" height="200"/> | <img src="img/robot_and_object.png" width="200" height="200"/> | <img src="img/gripper_and_object.png" width="200" height="200"/> |
  | <img src="img/self_collision_result.png" width="300" height="200"/> | <img src="img/robot_and_object_result.png" width="300" height="200"/> | <img src="img/gripper_and_object_result.png" width="500" height="200"/> |

- Attach/Detach object to Gripper

  

- Planning

  *You can see an planning animation that visualizes trajectory*

  - Cartesian planning

    |                            iiwa14                            |                            panda                             |                            sawyer                            |
    | :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: |
    | <img src="img/iiwa_cartesian.gif" width="500" height="200"/> | <img src="img/panda_cartesian.gif" width="500" height="200"/> | <img src="img/sawyer_cartesian.gif" width="500" height="200"/> |

  - RRT-star planning

    |                         iiwa14                         |                          panda                          |                          sawyer                          |
    | :----------------------------------------------------: | :-----------------------------------------------------: | :------------------------------------------------------: |
    | <img src="img/iiwa_rrt.gif" width="500" height="200"/> | <img src="img/panda_rrt.gif" width="500" height="200"/> | <img src="img/sawyer_rrt.gif" width="500" height="200"/> |

- Grasping

  You can see an visualization the pose for the robot to grasp and release an object.

  - Compute panda robot's pick and place waypoints.

    | <img src="img/grasp01.png" width="400" height="400"/> | <img src="img/grasp02.png" width="400" height="400"/> |
    | ----------------------------------------------------- | ----------------------------------------------------- |

  - Compute pick and place waypoints for 2 or more objects.

    As a result, you can show pick and place demo in MuJoCo Simulator.

    | <img src="img/pnp_result.png" width="400" height="400"/> | <img src="img/sim_result.png" width="400" height="400"/> |
    | -------------------------------------------------------- | -------------------------------------------------------- |
