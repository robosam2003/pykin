import warnings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pykin.utils import transform_utils as tf

try:
    import fcl
except ImportError:
    warnings.warn(
        "Cannot display mesh. Library 'fcl' not installed.")

try:
    import trimesh
except ImportError:
    warnings.warn(
        "Cannot display mesh. Library 'trimesh' not installed.")

# Colors of each directions axes. For ex X is green
directions_colors = ["green", "cyan", "orange"]


def _check_color_type(color):
    """
    Check color's data type
    """
    if isinstance(color, str):
        color = color
    
    if isinstance(color, list):
        if len(color) == 0:
            color = 'k'
        else:
            color = color[0]
    
    if isinstance(color, np.ndarray):
        if len(color) == 0:
            color = np.array([0.2, 0.2, 0.2, 1.])
        else:
            color = color

    if isinstance(color, dict):
        if len(color) == 0:
            color = np.array([0.2, 0.2, 0.2, 1.])
        else:
            color = list(color.values())[0]
    return color


def plot_basis(robot=None, ax=None):
    """
    Plot a frame fitted to the robot size
    """
    if robot is not None:
        offset = np.linalg.norm(robot.offset.pos)
    else:
        offset = 1
        
    if offset == 0:
        offset = 1

    ax.set_xlim3d([-1.0 * offset, 1.0 * offset])
    ax.set_xlabel('X')

    ax.set_ylim3d([-1.0 * offset, 1.0 * offset])
    ax.set_ylabel('Y')

    ax.set_zlim3d([-1.0 * offset, 1.0 * offset])
    ax.set_zlabel('Z')


    ax.plot([0, offset * 1.5], [0, 0], [0, 0],
            c=directions_colors[0], label="X")
    ax.plot([0, 0], [0, offset * 1.5], [0, 0],
            c=directions_colors[1], label="Y")
    ax.plot([0, 0], [0, 0], [0, offset * 1.5],
            c=directions_colors[2], label="Z")


def plot_robot(
    robot, 
    ax=None, 
    transformations=None, 
    visible_visual=False,
    visible_collision=False, 
    mesh_path='../asset/urdf/baxter/',
    visible_text=True,
    visible_scatter=True):

    """
    Plot robot
    """

    if transformations is None:
        transformations = robot.init_transformations

    name = robot.robot_name
    plot_basis(robot, ax)
    
    links = []
    nodes = []
    transformation_matrix = []

    for i, (link, transformation) in enumerate(transformations.items()):
        links.append(link)
        transformation_matrix.append(transformation.homogeneous_matrix)

    for link, matrix in zip(links, transformation_matrix):
        nodes.append(tf.get_pos_mat_from_homogeneous(matrix))

    if name == "baxter":
        plot_baxter(nodes, ax, visible_text, visible_scatter)
    else:
        lines = ax.plot([x[0] for x in nodes], [x[1] for x in nodes], [
            x[2] for x in nodes], linewidth=5, label=name)

        if visible_text:
            label = '(%0.4f, %0.4f, %0.4f)' % (
                nodes[-1][0], nodes[-1][1], nodes[-1][2])

            ax.text(nodes[-1][0], nodes[-1][1],
                    nodes[-1][2], label, size="8")
        
        if visible_scatter:
            ax.scatter([x[0] for x in nodes], [x[1] for x in nodes],
                [x[2] for x in nodes], s=55, c=lines[0].get_color())
    
    if visible_visual:
        plot_mesh(robot, transformations, mesh_path)

    if visible_collision:
        plot_collision(robot, transformations, ax)

    ax.legend()

def plot_animation(
    robot, 
    trajectory,
    fig=None,
    ax=None,
    obstacles=None,
    visible_obstacles=False,
    visible_collision=False,
    visible_text=True,
    visible_scatter=True,
    interval=100, 
    repeat=False,
    result=None):

    """
    Plot animation
    """

    def update(i):
        print(f"{i/len(trajectory) * 100:.1f} %")
    
        if i == len(trajectory)-1:
            print(f"{i/(len(trajectory)-1) * 100:.1f} %")
            print("Animation Finished..")
        ax.clear()

        if visible_obstacles and obstacles:
            plot_obstacles(obstacles, ax)
          
        if result is not None:
            print(result[i])
            print()

        plot_robot(
            robot, 
            transformations=trajectory[i], 
            ax=ax, 
            visible_collision=visible_collision,
            visible_text=visible_text,
            visible_scatter=visible_scatter)

    ani = animation.FuncAnimation(fig, update, np.arange(len(trajectory)), interval=interval, repeat=repeat)
    plt.show()

def plot_obstacles(obstacles, ax):    
    for _, value in obstacles:
        o_type = value[0]
        o_param = value[1]
        o_pose = np.array(value[2])
        if o_type == "sphere":
            plot_sphere(ax, radius=o_param, p=o_pose, alpha=0.8, color='g')
        if o_type == "box":
            A2B = tf.get_homogeneous_matrix(o_pose)
            plot_box(ax, size=o_param, A2B=A2B, alpha=0.8, color='b')
        if o_type == "cylinder":
            A2B = tf.get_homogeneous_matrix(o_pose)
            plot_cylinder(ax, radius=o_param[0], length=o_param[1], A2B=A2B, n_steps=100, alpha=0.8, color='r')

def plot_baxter(nodes, ax, visible_text=True, visible_scatter=True):
    """
    Plot baxter robot
    """
    torso_nodes = [nodes[0]] + [nodes[3]]
    head_nodes = torso_nodes + nodes[7:12]
    pedestal_nodes = torso_nodes + [nodes[6]]
    right_nodes = torso_nodes + nodes[13:18] + nodes[20:29]
    left_nodes = torso_nodes + nodes[31:36] + nodes[38:47]

    head_lines = ax.plot([x[0] for x in head_nodes], [x[1] for x in head_nodes], [
        x[2] for x in head_nodes], linewidth=5, label="head")
    pedestal_lines = ax.plot([x[0] for x in pedestal_nodes], [x[1] for x in pedestal_nodes], [
        x[2] for x in pedestal_nodes], linewidth=5, label="pedestal")
    right_lines = ax.plot([x[0] for x in right_nodes], [x[1] for x in right_nodes], [
        x[2] for x in right_nodes], linewidth=5, label="right arm")
    left_lines = ax.plot([x[0] for x in left_nodes], [x[1] for x in left_nodes], [
        x[2] for x in left_nodes], linewidth=5, label="left arm")

    if visible_text:
        head_label = '(%0.4f, %0.4f, %0.4f)' % (
            head_nodes[-1][0], head_nodes[-1][1], head_nodes[-1][2])
        pedestal_label = '(%0.4f, %0.4f, %0.4f)' % (
            pedestal_nodes[-1][0], pedestal_nodes[-1][1], pedestal_nodes[-1][2])
        right_label = '(%0.4f, %0.4f, %0.4f)' % (
            right_nodes[8][0], right_nodes[8][1], right_nodes[8][2])
        left_label = '(%0.4f, %0.4f, %0.4f)' % (
            left_nodes[8][0], left_nodes[8][1], left_nodes[8][2])

        ax.text(head_nodes[-1][0], head_nodes[-1][1],
                head_nodes[-1][2], head_label, size="8")
        ax.text(pedestal_nodes[-1][0], pedestal_nodes[-1][1],
            pedestal_nodes[-1][2], pedestal_label, size="8")
        ax.text(right_nodes[-1][0], right_nodes[-1][1],
                right_nodes[-1][2], right_label, size="8")
        ax.text(left_nodes[-1][0], left_nodes[-1][1],
                left_nodes[-1][2], left_label, size="8")

    if visible_scatter:
        ax.scatter([x[0] for x in head_nodes], [x[1] for x in head_nodes], 
            [x[2] for x in head_nodes], s=55, c=head_lines[0].get_color())
        ax.scatter([x[0] for x in pedestal_nodes], [x[1] for x in pedestal_nodes], 
            [x[2] for x in pedestal_nodes], s=55, c=pedestal_lines[0].get_color())
        ax.scatter([x[0] for x in right_nodes], [x[1] for x in right_nodes], 
            [x[2] for x in right_nodes], s=55, c=right_lines[0].get_color())
        ax.scatter([x[0] for x in left_nodes], [x[1] for x in left_nodes], 
            [x[2] for x in left_nodes], s=55, c=left_lines[0].get_color())


def plot_collision(robot, transformations, ax, alpha=0.8):
    """
    Plot robot's collision
    """
    def _get_color(params):
        color = []
        if params is not None:
            visual_color = params.get('color')
            if visual_color is not None:
                color = list(visual_color.keys())
        return color

    for link, transformation in transformations.items():
        A2B = np.dot(transformation.homogeneous_matrix, robot.links[link].collision.offset.homogeneous_matrix)
        color = _get_color(robot.links[link].visual.gparam)

        if robot.links[link].collision.gtype == 'cylinder':
            length = float(robot.links[link].collision.gparam.get('length'))
            radius = float(robot.links[link].collision.gparam.get('radius'))
            plot_cylinder(ax, length=length, radius=radius, A2B=A2B, alpha=alpha, color=color)

        if robot.links[link].collision.gtype == 'sphere':
            radius = float(robot.links[link].collision.gparam.get('radius'))
            pos = A2B[:3,-1]
            plot_sphere(ax, radius=radius, p=pos, n_steps=20, alpha=alpha, color=color)
    
        if robot.links[link].collision.gtype == 'box':
            size = robot.links[link].collision.gparam.get('size')
            plot_box(ax, size, A2B=A2B, alpha=alpha, color=color)


def plot_cylinder(ax=None, length=1.0, radius=1.0,
                  A2B=np.eye(4), n_steps=100,
                  alpha=1.0, color="k"):
    """
    Plot cylinder
    """
    color = _check_color_type(color)
    axis_start = A2B.dot(np.array([0, 0, -length/2, 1]))[:3]
    axis_end =  A2B.dot(np.array([0, 0, length/2, 1]))[:3]

    axis = axis_end - axis_start
    axis /= length
    not_axis = np.array([1, 0, 0])
    if (axis == not_axis).all():
        not_axis = np.array([0, 1, 0])

    n1 = np.cross(axis, not_axis)
    n1 /= np.linalg.norm(n1)
    n2 = np.cross(axis, n1)

    t = np.array([0, length])

    theta = np.linspace(0, 2 * np.pi, n_steps)
    t, theta = np.meshgrid(t, theta)

    X, Y, Z = [axis_start[i] + axis[i] * t
            + radius * np.sin(theta) * n1[i]
            + radius * np.cos(theta) * n2[i] for i in [0, 1, 2]]

    ax.plot_surface(X, Y, Z, color=color, alpha=alpha, linewidth=0)


def plot_sphere(ax=None, radius=1.0, p=np.zeros(3), n_steps=20, alpha=1.0, color="k"):
    """
    Plot sphere
    """
    color = _check_color_type(color)
    phi, theta = np.mgrid[0.0:np.pi:n_steps * 1j, 0.0:2.0 * np.pi:n_steps * 1j]
    x = p[0] + radius * np.sin(phi) * np.cos(theta)
    y = p[1] + radius * np.sin(phi) * np.sin(theta)
    z = p[2] + radius * np.cos(phi)

    ax.plot_surface(x, y, z, color=color, alpha=alpha, linewidth=0)


def plot_box(ax=None, size=np.ones(3), alpha=1.0, A2B=np.eye(4), color="k"):
    """
    Plot box
    """
    color = _check_color_type(color)
    
    if not isinstance(size, np.ndarray):
        size = np.array(size)

    corners = np.array([
        [0, 0, 0],
        [0, 0, 1],
        [0, 1, 0],
        [0, 1, 1],
        [1, 0, 0],
        [1, 0, 1],
        [1, 1, 0],
        [1, 1, 1]
    ])
    corners = (corners - 0.5) * size
    PA = np.hstack(
        (corners, np.ones((len(corners), 1))))

    corners = np.dot(PA, A2B.T)[:, :3]
    p3c = Poly3DCollection(np.array([
        [corners[0], corners[1], corners[2]],
        [corners[1], corners[2], corners[3]],

        [corners[4], corners[5], corners[6]],
        [corners[5], corners[6], corners[7]],

        [corners[0], corners[1], corners[4]],
        [corners[1], corners[4], corners[5]],

        [corners[2], corners[6], corners[7]],
        [corners[2], corners[3], corners[7]],

        [corners[0], corners[4], corners[6]],
        [corners[0], corners[2], corners[6]],

        [corners[1], corners[5], corners[7]],
        [corners[1], corners[3], corners[7]],
    ]))

    p3c.set_alpha(alpha)
    p3c.set_facecolor(color)
    ax.add_collection3d(p3c)


def plot_mesh(robot, transformations, mesh_path):
    """
    Plot mesh
    """
    scene = trimesh.Scene()
    for link, transformation in transformations.items():
        if robot.links[link].visual.gtype == "mesh":
            mesh_name = robot.links[link].visual.gparam.get('filename')
            filename = mesh_path + mesh_name
            A2B = np.dot(transformation.homogeneous_matrix, robot.links[link].visual.offset.homogeneous_matrix)
            visual_color = robot.links[link].visual.gparam.get('color')
            color = np.array([0.2, 0.2, 0.2, 1.])
            if visual_color is not None:
                color = np.array([color for color in visual_color.values()]).flatten()
            scene = convert_trimesh_scene(scene, filename, A2B, color)
            scene.set_camera(np.array([np.pi/2, 0, np.pi/2]), 5)
    scene.show()


def convert_trimesh_scene(scene, filename=None, A2B=np.eye(4), color="k"):
    """
    Convert scene from mesh to trimesh
    """
    mesh = trimesh.load(filename)
    color = _check_color_type(color)
    mesh.visual.face_colors = color
    scene.add_geometry(mesh, transform=A2B)

    return scene


def plot_rrt_vertices(vertices, ax):
    """
    Plot rrt* trees
    """
    for vertex in vertices:
        ax.plot([x for (x, y, z) in vertex],[y for (x, y, z) in vertex], [z for (x, y, z) in vertex],'k', linewidth=0.1,)


def plot_path_planner(path, ax):
    """
    Plot rrt* path planner
    """
    if path is None:
        print("cannot create path")
        return

    ax.scatter([x for (x, y, z) in path], [y for (x, y, z) in path], [z for (x, y, z) in path], s=10, c='r')
    ax.plot([x for (x, y, z) in path], [y for (x, y, z) in path], [z for (x, y, z) in path], '-b', linewidth=0.5,)
    ax.text(path[0][0], path[0][1], path[0][2], 'Start', verticalalignment='bottom', horizontalalignment='center', size="20")
    ax.text(path[-1][0], path[-1][1], path[-1][2],'Goal', verticalalignment='bottom', horizontalalignment='center', size="20")


def init_3d_figure(name=None, figsize=(15,7.5), dpi= 80):
    """
    Initializes 3d figure
    """
    fig = plt.figure(name, figsize=figsize, dpi= dpi)
    ax = fig.add_subplot(111, projection='3d')
    return fig, ax


def show_figure():
    """
    Show figure
    """
    plt.show()
