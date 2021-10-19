import os, sys
pykin_path = os.path.abspath(os.path.dirname(__file__)+"../../" )
sys.path.append(pykin_path)

import numpy as np

from pykin.kinematics.transform import Transform
from pykin.robots.single_arm import SingleArm
from pykin.utils import plot_utils as plt

file_path = '../../asset/urdf/sawyer/sawyer.urdf'

robot = SingleArm(file_path, Transform(rot=[0.0, 0.0, 0.0], pos=[0, 0, 0]))
robot.setup_link_name(eef_name="right_hand")

target_thetas = [np.pi/3, 0, 0, 0, 0, 0, 0, 0]
robot_transformations = robot.forward_kin(target_thetas)

_, ax = plt.init_3d_figure("FK")
plt.plot_robot(robot,
               ax=ax, 
               transformations=robot_transformations,
               visible_visual=False,
               visible_collision=True,
               mesh_path='../asset/urdf/sawyer/')
plt.show_figure()
