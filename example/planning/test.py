import os, sys
pykin_path = os.path.abspath(os.path.dirname(__file__)+"../../" )
sys.path.append(pykin_path)

import numpy as np

from pykin.robots.bimanual import Bimanual
from pykin.kinematics.transform import Transform
from pykin.utils import plot_utils as plt
from pykin.utils.kin_utils import ShellColors as sc


# baxter_example
_, ax = plt.init_3d_figure()
file_path = '../../asset/urdf/baxter/baxter.urdf'
robot = Bimanual(file_path, Transform(rot=[0.0, 0.0, 0.0], pos=[0, 0, 0]))

print(robot.init_transformations)

head_thetas = [0.0]
right_arm_thetas = [np.pi/3, np.pi/5, np.pi/2, np.pi/7, 0, 0 ,0]
left_arm_thetas = [0, 0, 0, 0, 0, 0, 0]

thetas = head_thetas + right_arm_thetas + left_arm_thetas
fk = robot.forward_kin(thetas)

spheres = {}
radius = 0.13
obstacle_name = "obstacle_sphere_1"
sp_pos = (0.3, -0.65, 0.3)
spheres[obstacle_name] = (sp_pos, radius)


_, ax = plt.init_3d_figure()
plt.plot_robot(
    robot,
    transformations=fk,
    ax=ax,
)
plt.plot_sphere(ax, radius=radius, p=sp_pos, alpha=1.0, color="g")
plt.show_figure()

