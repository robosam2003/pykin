import numpy as np
import trimesh
import copy
np.seterr(divide='ignore', invalid='ignore')
import pykin.utils.plot_utils as plt
import pykin.utils.transform_utils as t_utils

class GraspManager:
    def __init__(self, gripper=None, max_width=None):
        if gripper is not None:
            self.gripper = gripper
            self.grasp_c_manager = trimesh.collision.CollisionManager()
        self.max_width = max_width
    
        self.mesh_point = np.zeros(3)
        self.contact_points = None
        self.x = None
        self.y = None
        self.z = None

    def get_pre_grasp_posture(
        self, 
        robot, 
        grasp_pose=None, 
        desired_distance=0.1,
        n_steps=3, 
        epsilon=1e-2
    ):
        assert grasp_pose is not None
        
        pre_grasp_posture = np.eye(4)
        grasp_posure = copy.deepcopy(grasp_pose)

        pre_grasp_posture[:3, :3] = grasp_posure[:3, :3]
        pre_grasp_posture[:3, 3] = grasp_posure[:3, 3] - desired_distance * grasp_posure[:3,2]
        
        transforms, is_grasp_success= self._compute_posture(robot, pre_grasp_posture, n_steps, epsilon)
        return transforms, is_grasp_success

    def get_grasp_posture(self, robot, grasp_pose=None, n_steps=3, epsilon=1e-1):
        assert grasp_pose is not None
        transforms, is_grasp_success= self._compute_posture(robot, grasp_pose, n_steps, epsilon)
        return transforms, is_grasp_success

    def _compute_posture(self, robot, grasp_pose, n_steps, epsilon):
        eef_pose, qpos, transforms = self._compute_kinematics(robot, grasp_pose)
        is_grasp_success = False

        for _ in range(n_steps):
            transforms = robot.forward_kin(np.array(qpos))
            goal_pose = transforms[robot.eef_name].h_mat

            is_joint_limit = robot.check_limit_joint(qpos)
            error_pose = robot.get_pose_error(grasp_pose, goal_pose)
            print(error_pose)
            if is_joint_limit and error_pose < epsilon:
                is_grasp_success = True
                break
            qpos = robot.inverse_kin(np.random.randn(len(qpos)), eef_pose, method="LM")

        if is_grasp_success:
            return transforms, is_grasp_success

        return None, is_grasp_success

    def _compute_kinematics(self, robot, grasp_pose):
        eef_pose = t_utils.get_pose_from_homogeneous(grasp_pose)
        qpos = robot.inverse_kin(np.random.randn(7), eef_pose)
        transforms = robot.forward_kin(np.array(qpos))

        return eef_pose, qpos, transforms

    def compute_grasp_pose(self, mesh, approach_distance=0.08, limit_angle=0.02):
        while True:
            vertices, normals = self.surface_sampling(mesh, n_samples=2)
            if self.is_force_closure(vertices, normals, limit_angle):
                break

        self.contact_points = vertices

        p1 = self.contact_points[0]
        p2 = self.contact_points[1]
        center_point = (p1 + p2) / 2

        #TODO : change to get mesh_point
        # self.mesh_point = self.compute_mesh_point(mesh, center_point)
        self.mesh_point, _, _ = trimesh.proximity.closest_point(mesh, [center_point])

        self.y = self.normalize(p1 - p2)
        self.z = center_point - self.mesh_point[0]
        self.z = self.normalize(self.z - self.projection(self.z, self.y)) # Gram-Schmidt
        self.x = self.normalize(np.cross(self.y, self.z))

        grasp_pose = np.eye(4)
        grasp_pose[:3,0] = self.x
        grasp_pose[:3,1] = self.y
        grasp_pose[:3,2] = self.z
        grasp_pose[:3,3] = self.mesh_point - approach_distance * self.z

        return grasp_pose

    def compute_robust_force_closure(self, mesh, vertices, normals, limit_radian=0.02, n_trials=5):
        sigma = 1e-3
        noise = np.random.normal(0, sigma, (n_trials, 2, 3))
        
        count = 0
        for i in range(n_trials):
            # vertices_copy = vertices.copy()
            new_vertices = vertices + noise[i]

            points, _, faces = trimesh.proximity.closest_point(mesh, new_vertices)        
            normals = mesh.face_normals[faces]

            is_fc = self.is_force_closure(points, normals, limit_radian)
            if is_fc:
                count += 1
        return count/n_trials

    def is_force_closure(self, vertices, normals, limit_angle=0.1):
        vectorA = vertices[0]
        vectorB = vertices[1]

        normalA = -normals[0]
        normalB = -normals[1]

        vectorAB = vectorB - vectorA
        distance = np.linalg.norm(vectorAB)

        unit_vectorAB = self.normalize(vectorAB)
        angle_A2AB = np.arccos(normalA.dot(unit_vectorAB))

        unit_vectorBA = -1 * unit_vectorAB
        angle_B2AB = np.arccos(normalB.dot(unit_vectorBA))

        if distance > self.max_width:
            return False

        if angle_A2AB > limit_angle or angle_B2AB > limit_angle:
            return False

        return True

    @staticmethod
    def surface_sampling(mesh, n_samples=2):
        vertices, face_ind = trimesh.sample.sample_surface(mesh, count=n_samples)
        normals = mesh.face_normals[face_ind]
        return vertices, normals

    @staticmethod
    def compute_mesh_point(mesh, point):
        pass

    @staticmethod
    def find_intersections(mesh, p1, p2):
        ray_origin = (p1 + p2) / 2
        ray_length = np.linalg.norm(p1 - p2)
        ray_dir = (p2 - p1) / ray_length
        locations, index_ray, index_tri = mesh.ray.intersects_location(
            ray_origins=[ray_origin, ray_origin],
            ray_directions=[ray_dir, -ray_dir],
            multiple_hits=True)
        if len(locations) == 0:
            return [], []
        dist_to_center = np.linalg.norm(locations - ray_origin, axis=1)
        dist_mask = dist_to_center <= (ray_length / 2) # only keep intersections on the segment.
        on_segment = locations[dist_mask]
        faces = index_tri[dist_mask]
        return on_segment, faces

    @staticmethod
    def projection(v, u):
        return np.dot(v, u) / np.dot(u, u) * u

    @staticmethod
    def normalize(vec):
        return vec / np.linalg.norm(vec)

    def visualize_grasp_pose(self, ax):
        plt.plot_vertices(ax, self.contact_points)
        plt.plot_vertices(ax, self.mesh_point)   
        plt.plot_normal_vector(ax, self.mesh_point, self.x, scale=0.1, edgecolor="red")    
        plt.plot_normal_vector(ax, self.mesh_point, self.y, scale=0.1, edgecolor="green")    
        plt.plot_normal_vector(ax, self.mesh_point, self.z, scale=0.1, edgecolor="blue")  