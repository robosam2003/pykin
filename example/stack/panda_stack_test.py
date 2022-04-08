import numpy as np
import sys, os
import trimesh

pykin_path = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.append(pykin_path)

from pykin.robots.single_arm import SingleArm
from pykin.kinematics.transform import Transform
from pykin.collision.collision_manager import CollisionManager
from pykin.tasks.grasp import GraspManager, GraspStatus
from pykin.utils.task_utils import get_relative_transform
from pykin.objects.object_manager import ObjectManager
import pykin.utils.plot_utils as plt

file_path = '../../asset/urdf/panda/panda.urdf'
robot = SingleArm(file_path, Transform(rot=[0.0, 0.0, 0.0], pos=[0, 0, 0.913]))
robot.setup_link_name(eef_name="panda_right_hand")

init_qpos = [0.0, np.pi/6, 0.0, -np.pi*12/24, 0.0, np.pi*5/8,0.0]
fk = robot.forward_kin(np.array(init_qpos))

mesh_path = pykin_path+"/asset/urdf/panda/"
c_manager = CollisionManager(mesh_path)
c_manager.setup_robot_collision(robot, fk)

grasp_obj1_pose = Transform(pos=np.array([0.6, 0.2, 0.77]))
grasp_obj2_pose = Transform(pos=np.array([0.4, 0.2, 0.77]))
grasp_obj3_pose = Transform(pos=np.array([0.6, 0.1, 0.77]))

obs_pos2 = Transform(pos=np.array([0.6, -0.2, 0.77]), rot=np.array([0, np.pi/2, 0]))
obs_pos3 = Transform(pos=np.array([0.4, 0.24, 0.0]))

cube_mesh = trimesh.load(pykin_path+'/asset/objects/meshes/ben_cube.stl')
box_goal_mesh = trimesh.load(pykin_path+'/asset/objects/meshes/box_goal.stl')
table_mesh = trimesh.load(pykin_path+'/asset/objects/meshes/custom_table.stl')

cube_mesh.apply_scale(0.06)
box_goal_mesh.apply_scale(0.001)
table_mesh.apply_scale(0.01)

objects = ObjectManager()
objects.add_object(name="red_box", gtype="mesh", gparam=cube_mesh, h_mat=grasp_obj1_pose.h_mat, for_grasp=True)
objects.add_object(name="blue_box", gtype="mesh", gparam=cube_mesh, h_mat=grasp_obj2_pose.h_mat, for_grasp=True)
objects.add_object(name="green_box", gtype="mesh", gparam=cube_mesh, h_mat=grasp_obj3_pose.h_mat, for_grasp=True)
objects.add_object(name="box", gtype="mesh", gparam=box_goal_mesh, h_mat=obs_pos2.h_mat, for_support=True)
objects.add_object(name="table", gtype="mesh", gparam=table_mesh, h_mat=obs_pos3.h_mat)

print(objects)

objects.update_object_pose("red_box", obs_pos3.h_mat)

print(objects.get_info("red_box")[objects.POSE])