import numpy as np
import sys, os
import yaml

pykin_path = os.path.dirname(os.path.dirname(os.path.dirname(os.getcwd())))
sys.path.append(pykin_path)

from pykin.kinematics.transform import Transform
from pykin.robots.bimanual import Bimanual
from pykin.scene.scene import SceneManager
from pykin.utils.mesh_utils import get_object_mesh
import pykin.utils.plot_utils as plt

fig, ax = plt.init_3d_figure(figsize=(10,6), dpi=120)

file_path = '../../../asset/urdf/baxter/baxter.urdf'

robot = Bimanual(file_path, Transform(rot=[0.0, 0.0, 0.0], pos=[0, 0, 0.913]))
robot.setup_link_name("base", "right_wrist")
robot.setup_link_name("base", "left_wrist")

# set target joints angle
custom_fpath = '../../../asset/config/baxter_init_params.yaml'
with open(custom_fpath) as f:
    controller_config = yaml.safe_load(f)

init_qpos = controller_config["init_qpos"]
init_qpos = np.concatenate((np.zeros(1), np.array(init_qpos)))

red_box_pose = Transform(pos=np.array([0.6, 0.2, 0.77]))
blue_box_pose = Transform(pos=np.array([0.6, 0.2, 0.77 + 0.06]))
green_box_pose = Transform(pos=np.array([0.6, 0.2, 0.77 + 0.12]))
support_box_pose = Transform(pos=np.array([0.6, -0.2, 0.77]), rot=np.array([0, np.pi/2, 0]))
table_pose = Transform(pos=np.array([0.4, 0.24, 0.0]))

red_cube_mesh = get_object_mesh('ben_cube.stl', 0.06)
blue_cube_mesh = get_object_mesh('ben_cube.stl', 0.06)
green_cube_mesh = get_object_mesh('ben_cube.stl', 0.06)
box_goal_mesh = get_object_mesh('box_goal.stl', 0.001)
table_mesh = get_object_mesh('custom_table.stl', 0.01)

scene_mngr = SceneManager("visual", True)
scene_mngr.add_object(name="table", gtype="mesh", gparam=table_mesh, h_mat=table_pose.h_mat, color=[0.39, 0.263, 0.129])
scene_mngr.add_object(name="red_box", gtype="mesh", gparam=red_cube_mesh, h_mat=red_box_pose.h_mat, color=[1.0, 0.0, 0.0])
scene_mngr.add_object(name="blue_box", gtype="mesh", gparam=blue_cube_mesh, h_mat=blue_box_pose.h_mat, color=[0.0, 0.0, 1.0])
scene_mngr.add_object(name="green_box", gtype="mesh", gparam=green_cube_mesh, h_mat=green_box_pose.h_mat, color=[0.0, 1.0, 0.0])
scene_mngr.add_object(name="goal_box", gtype="mesh", gparam=box_goal_mesh, h_mat=support_box_pose.h_mat, color=[1.0, 0, 1.0])
scene_mngr.add_robot(robot)
############################# Render Test #############################
scene_mngr.set_robot_eef_pose(init_qpos)

scene_mngr.render_all_scene(ax)
scene_mngr.show()

