from copy import deepcopy
import trimesh
import numpy as np

import pykin.utils.plot_utils as plt
from pykin.collision.collision_manager import CollisionManager
from pykin.utils.task_utils import get_absolute_transform


class GripperManager:
    def __init__(
        self,
        robot,
        mesh_path,
        color=None,
        logical_state = {},
        **configures
    ):
        self.robot = robot
        self.mesh_path = mesh_path
        self.color = color
        self.gripper_names = configures.get("gripper_names", None)
        self.gripper_names.insert(0, self.robot.eef_name)
        self.gripper_names.append("tcp")
        
        self.name = self.robot.robot_name+"_gripper"
        self.max_width = configures.get("gripper_max_width", 0.0)
        self.max_depth = configures.get("gripper_max_depth", 0.0)
        self.tcp_position = configures.get("tcp_position", np.zeros(3))
        
        self.col_manager = CollisionManager()
        self.init_gripper = self.create_gripper()
        self.gripper = deepcopy(self.init_gripper)

        self.setup_col_manager()
        self.logical_state = logical_state

    def create_gripper(self):
        gripper = {}
        for link, transform in self.robot.init_fk.items():
            if link in self.gripper_names:
                h_mat = transform.h_mat
                gtype = None
                gparam = None
                if self.robot.links[link].collision.gtype == "mesh":
                    mesh_name = self.robot.links[link].collision.gparam.get('filename')
                    file_name = self.mesh_path + mesh_name
                    gtype = "mesh"
                    mesh = trimesh.load_mesh(file_name)
                    gparam = mesh
                    h_mat = np.dot(transform.h_mat, self.robot.links[link].collision.offset.h_mat)
                gripper[link] = [link, gtype, gparam, h_mat]
        return gripper

    def set_tcp_transform(self, tcp_pose=np.eye(4)):
        for link, info, in self.init_gripper.items():
            T = get_absolute_transform(self.init_gripper[self.gripper_names[-1]][3], tcp_pose)
            self.gripper[link][3] = np.dot(T, info[3])
            if self.robot.links[link].collision.gtype == "mesh":
                self.col_manager.set_transform(link, np.dot(T, info[3]))

    def set_eef_transform(self, eef_pose=np.eye(4)):
        tcp_pose = self.get_tcp_pose_from_eef_pose(eef_pose)
        for link, info, in self.init_gripper.items():
            T = get_absolute_transform(self.init_gripper[self.gripper_names[-1]][3], tcp_pose)
            self.gripper[link][3] = np.dot(T, info[3])
            if self.robot.links[link].collision.gtype == "mesh":
                self.col_manager.set_transform(link, np.dot(T, info[3]))

    def setup_col_manager(self):
        for link, transform in self.robot.init_fk.items():
            if link in self.gripper_names:
                if self.robot.links[link].collision.gtype == "mesh":
                    mesh_name = self.robot.links[link].collision.gparam.get('filename')
                    file_name = self.mesh_path + mesh_name
                    mesh = trimesh.load_mesh(file_name)
                    h_mat = np.dot(transform.h_mat, self.robot.links[link].collision.offset.h_mat)
                    self.col_manager.add_object(link, gtype="mesh", gparam=mesh, h_mat=h_mat)
                    
    def get_eef_pose_from_tcp_pose(self, tcp_pose=np.eye(4)):
        eef_pose = np.eye(4)
        eef_pose[:3, :3] = tcp_pose[:3, :3]
        eef_pose[:3, 3] = tcp_pose[:3, 3] - np.dot(self.tcp_position[-1], tcp_pose[:3, 2])
        return eef_pose

    def get_tcp_pose_from_eef_pose(self, eef_pose=np.eye(4)):
        tcp_pose = np.eye(4)
        tcp_pose[:3, :3] = eef_pose[:3, :3]
        tcp_pose[:3, 3] = eef_pose[:3, 3] + np.dot(self.tcp_position[-1], eef_pose[:3, 2])
        return tcp_pose

    def visualize(
        self, 
        ax, 
        gripper:dict=None,
        alpha=0.3,
        color=None,
        visible_tcp_point=True
    ):
        plt.plot_basis(ax, self.robot)

        if color is None:
            color = self.color

        for link, info in gripper.items():
            mesh = info[2]
            h_mat = info[3]
            mesh_color = color
            if self.robot.links[link].collision.gtype == "mesh":
                if color is None:
                    mesh_color = self.robot.links[link].collision.gparam.get('color')
                    mesh_color = np.array([color for color in mesh_color.values()]).flatten()
                if "finger" in link:
                    alpha = 1
                plt.plot_mesh(ax, mesh, h_mat=h_mat, color=mesh_color, alpha=alpha)
        
        if visible_tcp_point:
            ax.scatter(gripper["tcp"][3][0,3], gripper["tcp"][3][1,3], gripper["tcp"][3][2,3], s=5, c='r')