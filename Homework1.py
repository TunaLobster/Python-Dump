"""
Charlie Johnson
MAE 5010 Autopilot Design and Test
Homework 1
8/27/2019
"""

from itertools import product, combinations

import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
import mpl_toolkits.mplot3d.axes3d as p3
import numpy as np
import scipy.integrate
from celluloid import Camera
from numba import jit


class MAVProperties:
    def __init__(self, mass, Ix, Iy, Iz, Ixz):
        """

        :param mass: lbm
        :param Ix: slug*ft**2
        :param Iy: slug*ft**2
        :param Iz: slug*ft**2
        :param Ixz: slug*ft**2
        """
        self.mass = mass  # lbm
        self.Ix = Ix  # slug*ft**2
        self.Iy = Iy  # slug*ft**2
        self.Iz = Iz  # slug*ft**2
        self.Ixz = Ixz  # slug*ft**2


class Plane:
    def __init__(self):
        self.MAV = MAVProperties(16300, 3549, 58611, 59669, 0)  # F-104-A
        self.g = 32.2  # ft/s**2
        # Fx, Fy, Fz, L, M, N = [0, 0, 0, 0, 0, 0]
        # self.FM = [Fx, Fy, Fz, L, M, N]

        # Initial states at zero
        pn, pe, pd = [0, 0, 0]
        u, v, w = [0, 0, 0]
        e0, e1, e2, e3 = [0, 0, 0, 0]
        p, q, r = [0, 0, 0]
        self.state = [pn, pe, pd, u, v, w, e0, e1, e2, e3, p, q, r]

    @staticmethod
    @jit(nopython=True)
    def Euler3212EP(euler: tuple):
        """

        :param euler: Euler angle of the format heading, pitch, roll or psi, theta, phi in degrees
        :return: Quaternion (e0, e1, e2, e3)
        """
        psi, theta, phi = euler  # heading, pitch, roll
        psi = np.deg2rad(psi)
        theta = np.deg2rad(theta)
        phi = np.deg2rad(phi)
        e0 = np.cos(psi / 2) * np.cos(theta / 2) * np.cos(phi / 2) + np.sin(psi / 2) * np.sin(theta / 2) * np.sin(
            phi / 2)
        e1 = np.cos(psi / 2) * np.cos(theta / 2) * np.sin(phi / 2) - np.sin(psi / 2) * np.sin(theta / 2) * np.cos(
            phi / 2)
        e2 = np.cos(psi / 2) * np.sin(theta / 2) * np.cos(phi / 2) + np.sin(psi / 2) * np.cos(theta / 2) * np.sin(
            phi / 2)
        e3 = np.sin(psi / 2) * np.cos(theta / 2) * np.cos(phi / 2) - np.cos(psi / 2) * np.sin(theta / 2) * np.sin(
            phi / 2)
        return e0, e1, e2, e3

    @staticmethod
    @jit(nopython=True)
    def EP2Euler321(quaternion: tuple):
        """

        :param quaternion: Quaternion (e0, e1, e2, e3)
        :return: Euler angle of format heading, pitch, roll or psi, theta, phi
        """
        e0, e1, e2, e3 = quaternion
        psi = np.arctan2(2 * (e0 * e3 + e1 * e2), (e0 ** 2 + e1 ** 2 - e2 ** 2 - e3 ** 2))
        theta = np.arcsin(2 * (e0 * e2 - e1 * e3))
        phi = np.arctan2(2 * (e0 * e1 + e2 * e3), (e0 ** 2 + e3 ** 2 - e1 ** 2 - e2 ** 2))
        return psi, theta, phi

    @staticmethod
    @jit(nopython=True)
    def R_FB(phi, theta, psi):
        return np.array([[np.cos(theta) * np.cos(psi),
                          np.sin(phi) * np.sin(theta) * np.cos(psi) - np.cos(phi) * np.sin(psi),
                          np.cos(phi) * np.sin(theta) * np.cos(psi) + np.sin(phi) * np.sin(psi)],
                         [np.cos(theta) * np.sin(psi),
                          np.sin(phi) * np.sin(theta) * np.sin(psi) + np.cos(phi) * np.cos(psi),
                          np.cos(phi) * np.sin(theta) * np.sin(psi) - np.sin(phi) * np.cos(psi)],
                         [-np.sin(theta), np.sin(phi) * np.cos(theta), np.cos(phi) * np.cos(theta)]])

    def R_BF(self, phi, theta, psi):
        return self.R_FB(phi, theta, psi).T

    def derivatives2(self, state, t, Fx, Fy, Fz, Ell, M, N):
        pn, pe, pd, u, v, w, e0, e1, e2, e3, p, q, r = state
        psi, theta, phi = self.EP2Euler321((e0, e1, e2, e3))

        Fx, Fy, Fz = np.matmul(self.R_BF(phi, theta, psi), [0, 0, 0])
        Fx += 20e3 * np.sin(t)

        pn_dot, pe_dot, pd_dot = np.matmul(self.R_FB(phi, theta, psi), np.array([u, v, w]).T).T
        M += 1e3

        u_dot = (r * v - q * w) + (Fx / self.MAV.mass)
        v_dot = (p * w - r * u) + (Fy / self.MAV.mass)
        w_dot = (q * u - p * v) + (Fz / self.MAV.mass)

        a = np.multiply(0.5, np.array([[0, -p, -q, -r], [p, 0, r, -q], [q, -r, 0, p], [r, q, -p, 0]]))
        b = np.array([[e0], [e1], [e2], [e3]])

        c = np.matmul(a, b)

        e0_dot, e1_dot, e2_dot, e3_dot = c.T[0]

        Gamma = self.MAV.Ix * self.MAV.Iz - self.MAV.Ixz ** 2
        Gamma_1 = (self.MAV.Ixz * (self.MAV.Ix - self.MAV.Iy + self.MAV.Iz)) / Gamma
        Gamma_2 = (self.MAV.Iz * (self.MAV.Iz - self.MAV.Iy) + self.MAV.Ixz ** 2) / Gamma
        Gamma_3 = self.MAV.Iz / Gamma
        Gamma_4 = self.MAV.Ixz / Gamma
        Gamma_5 = (self.MAV.Iz - self.MAV.Ix) / self.MAV.Iy
        Gamma_6 = self.MAV.Ixz / self.MAV.Iy
        Gamma_7 = ((self.MAV.Ix - self.MAV.Iy) * self.MAV.Ix + self.MAV.Ixz ** 2) / Gamma
        Gamma_8 = self.MAV.Ix / Gamma

        p_dot_mat = np.add(np.array(
            [[Gamma_1 * p * q - Gamma_2 * q * r],
             [Gamma_5 * p * r - Gamma_6 * (p ** 2 - r ** 2)],
             [Gamma_7 * p * q - Gamma_1 * q * r]]), np.array([[Gamma_3 * Ell + Gamma_4 * N],
                                                              [M / self.MAV.Iy],
                                                              [Gamma_4 * Ell + Gamma_8 * N]]))
        testing = np.add(np.array([1, 2, 3]), np.array([6, 7, 8]))
        # print(p_dot_mat.T)
        p_dot, q_dot, r_dot = p_dot_mat.T[0]
        result = [pn_dot, pe_dot, pd_dot, u_dot, v_dot, w_dot, e0_dot, e1_dot, e2_dot, e3_dot, p_dot, q_dot, r_dot]
        return result

    def derivatives(self, state, t, Fx, Fy, Fz, Ell, M, N):
        pn, pe, pd, u, v, w, e0, e1, e2, e3, p, q, r = state
        psi, theta, phi = self.EP2Euler321((e0, e1, e2, e3))

        # rotate gravity from fixed frame to body frame
        Fx, Fy, Fz = np.matmul(self.R_BF(phi, theta, psi), [0, 0, self.MAV.mass * self.g])

        pn_dot, pe_dot, pd_dot = np.matmul(self.R_FB(phi, theta, psi), np.array([u, v, w]).T).T

        u_dot = (r * v - q * w) + (Fx / self.MAV.mass)
        v_dot = (p * w - r * u) + (Fy / self.MAV.mass)
        w_dot = (q * u - p * v) + (Fz / self.MAV.mass)

        a = np.multiply(0.5, np.array([[0, -p, -q, -r], [p, 0, r, -q], [q, -r, 0, p], [r, q, -p, 0]]))
        b = np.array([[e0], [e1], [e2], [e3]])

        c = np.matmul(a, b)

        e0_dot, e1_dot, e2_dot, e3_dot = c.T[0]

        Gamma = self.MAV.Ix * self.MAV.Iz - self.MAV.Ixz ** 2
        Gamma_1 = (self.MAV.Ixz * (self.MAV.Ix - self.MAV.Iy + self.MAV.Iz)) / Gamma
        Gamma_2 = (self.MAV.Iz * (self.MAV.Iz - self.MAV.Iy) + self.MAV.Ixz ** 2) / Gamma
        Gamma_3 = self.MAV.Iz / Gamma
        Gamma_4 = self.MAV.Ixz / Gamma
        Gamma_5 = (self.MAV.Iz - self.MAV.Ix) / self.MAV.Iy
        Gamma_6 = self.MAV.Ixz / self.MAV.Iy
        Gamma_7 = ((self.MAV.Ix - self.MAV.Iy) * self.MAV.Ix + self.MAV.Ixz ** 2) / Gamma
        Gamma_8 = self.MAV.Ix / Gamma

        p_dot_mat = np.add(np.array(
            [[Gamma_1 * p * q - Gamma_2 * q * r],
             [Gamma_5 * p * r - Gamma_6 * (p ** 2 - r ** 2)],
             [Gamma_7 * p * q - Gamma_1 * q * r]]), np.array([[Gamma_3 * Ell + Gamma_4 * N],
                                                              [M / self.MAV.Iy],
                                                              [Gamma_4 * Ell + Gamma_8 * N]]))
        # print(p_dot_mat.T)
        p_dot, q_dot, r_dot = p_dot_mat.T[0]
        result = [pn_dot, pe_dot, pd_dot, u_dot, v_dot, w_dot, e0_dot, e1_dot, e2_dot, e3_dot, p_dot, q_dot, r_dot]
        return result


def main():
    plane = Plane()
    print([np.rad2deg(x) for x in plane.EP2Euler321((0.82205, 0.26538, 0.05601, 0.50066))])
    print(plane.Euler3212EP((50, 15, -30)))

    pn, pe, pd = [100, 200, -500]
    u, v, w = [0, 0, 0]
    e0, e1, e2, e3 = plane.Euler3212EP((90, 15, 20))
    p, q, r = [0, 0, 0]
    FM = [0, 0, 0, 0, 0, 0]
    initial_state = np.array([pn, pe, pd, u, v, w, e0, e1, e2, e3, p, q, r])
    t = np.linspace(0, 10, 500)

    # start = time.time()
    sol = scipy.integrate.odeint(plane.derivatives, initial_state, t, args=tuple(FM))
    # end = time.time()
    # print(end - start)

    # Plot position
    plt.figure(1)
    plt.plot(t, sol[:, 0], label='Pn')
    plt.plot(t, sol[:, 1], label='Pe')
    plt.plot(t, sol[:, 2], label='Pd')
    plt.legend()
    plt.title('Body NED position')
    plt.xlabel('Time (s)')
    plt.ylabel('Long/Lat/Alt (feet)')

    # Plot Euler angles
    sim_Euler = np.zeros((sol.shape[0], 3))
    for i in range(sol.shape[0]):
        sim_Euler[i] = plane.EP2Euler321(sol[i, 6:10])

    plt.figure(2)
    plt.plot(t, sim_Euler[:, 0], label='psi')
    plt.plot(t, sim_Euler[:, 1], label='theta')
    plt.plot(t, sim_Euler[:, 2], label='phi')
    plt.legend()
    plt.title('Body Euler rotation')
    plt.xlabel('Time (s)')
    plt.ylabel('Euler angles (radians)')

    # Plot rates
    plt.figure(3)
    plt.plot(t, sol[:, 10], label='p')
    plt.plot(t, sol[:, 11], label='q')
    plt.plot(t, sol[:, 12], label='r')
    plt.legend()
    plt.title('Body rates')
    plt.xlabel('Time (s)')
    plt.ylabel('Euler rates (radians/s)')
    plt.show()

    '''
    Do it again with a sinusoidal thruster
    '''

    pn, pe, pd = [100, 200, -500]
    u, v, w = [0, 0, 0]
    e0, e1, e2, e3 = plane.Euler3212EP((90, 15, 20))
    p, q, r = [0, 0, 0]
    FM = [0, 0, 0, 0, 0, 0]
    initial_state = np.array([pn, pe, pd, u, v, w, e0, e1, e2, e3, p, q, r])
    t = np.linspace(0, 60, 100)

    # start = time.time()
    sol2 = scipy.integrate.odeint(plane.derivatives2, initial_state, t, args=tuple(FM))
    # end = time.time()
    # print(end - start)

    # Plot position
    plt.figure(4)
    plt.plot(t, sol2[:, 0], label='Pn')
    plt.plot(t, sol2[:, 1], label='Pe')
    plt.plot(t, sol2[:, 2], label='Pd')
    plt.legend()
    plt.title('Body NED position')
    plt.xlabel('Time (s)')
    plt.ylabel('Long/Lat/Alt (feet)')

    # Plot Euler angles
    sim_Euler2 = np.zeros((sol2.shape[0], 3))
    for i in range(sol2.shape[0]):
        sim_Euler2[i] = plane.EP2Euler321(sol2[i, 6:10])

    # trying to figure out if the angle even changes at all
    print(np.std(sim_Euler2[:, 1]))

    plt.figure(5)
    plt.plot(t, sim_Euler2[:, 0], label='psi')
    plt.plot(t, sim_Euler2[:, 1], label='theta')
    plt.plot(t, sim_Euler2[:, 2], label='phi')
    plt.legend()
    plt.title('Body Euler rotation')
    plt.xlabel('Time (s)')
    plt.ylabel('Euler angles (radians)')

    # Plot rates
    plt.figure(6)
    plt.plot(t, sol2[:, 10], label='p')
    plt.plot(t, sol2[:, 11], label='q')
    plt.plot(t, sol2[:, 12], label='r')
    plt.legend()
    plt.title('Body rates')
    plt.xlabel('Time (s)')
    plt.ylabel('Euler rates (radians/s)')
    plt.show()

    '''
    Make some attempt at making a 3D visualization
    based on: https://stackoverflow.com/questions/18789232/rotate-a-3d-object-in-python
    animation and celluloid info: https://towardsdatascience.com/animations-with-matplotlib-d96375c5442c
    
    Issues: matplotlib takes a long time to render. So the better way would be to render each figure out to frames and 
    stitch them together in Blender, DaVinci Resolve, or Premier. Not the best for rapid development, but it works.
    '''

    fig = plt.figure(7)
    camera = Camera(fig)
    ax = p3.Axes3D(fig)
    ax.set_aspect("auto")
    # ax.set_autoscale_on(True)
    # flip y and z to get to NED
    ax.set(xlim=(-10, 10), ylim=(10, -10), zlim=(10, -10))
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')

    d = [-2, 2]
    forward = [[0, 0, 0], [2, 0, 0]]
    # Plane points are in normal station, waterline, and buttline coords.
    # Need to preform a 180 degree rotation about x and 180 about z
    # 3D matrix in the for form of line, (start,end), (x,y,z)
    plane_points = [[[0, 0, 0], [1, 1, 1]],  # start of fuselage
                    [[0, 0, 0], [1, 1, -1]],
                    [[0, 0, 0], [1, -1, 1]],
                    [[0, 0, 0], [1, -1, -1]],
                    [[1, 1, 1], [5, 1, 1]],
                    [[1, 1, -1], [5, 1, -1]],
                    [[1, -1, 1], [5, -1, 1]],
                    [[1, -1, -1], [5, -1, -1]],
                    [[5, 1, 1], [6, 0, 0]],
                    [[5, 1, -1], [6, 0, 0]],
                    [[5, -1, 1], [6, 0, 0]],
                    [[5, -1, -1], [6, 0, 0]],  # end of fuselage
                    [[1, -6, 1], [1, 6, 1]],  # start of wing
                    [[1, 6, 1], [2, 6, 1]],
                    [[2, 6, 1], [2, -6, 1]],
                    [[2, -6, 1], [1, -6, 1]]]  # end of wing

    def animate(i):
        euler = sim_Euler2[i]
        psi, theta, phi = euler

        # draw a cube
        for s, e in combinations(np.array(list(product(d, d, d))), 2):
            # s and e are x,y,z coords
            if np.sum(np.abs(s - e)) == d[1] - d[0]:
                # calculate rotation of cube points and plot them
                s_rotated = np.matmul(plane.R_FB(phi, theta, psi), np.array(s).T).T
                e_rotated = np.matmul(plane.R_FB(phi, theta, psi), np.array(e).T).T
                ax.plot3D(*zip(s_rotated, e_rotated), color='g')

        # draw a plane
        for row in plane_points:
            s, e = row
            # s_body = np.matmul(plane.R_FB(0, 0, 0), np.array(s).T).T
            # e_body = np.matmul(plane.R_FB(0, 0, 0), np.array(e).T).T
            # ax.plot3D(*zip(s_body, e_body), color='b')
            s_body = np.matmul(plane.R_FB(np.radians(180), 0, np.radians(180)), np.array(s).T).T
            e_body = np.matmul(plane.R_FB(np.radians(180), 0, np.radians(180)), np.array(e).T).T
            # ax.plot3D(*zip(s_body, e_body), color='r')
            s_rotated = np.matmul(plane.R_FB(phi, theta, psi), np.array(s_body).T).T
            e_rotated = np.matmul(plane.R_FB(phi, theta, psi), np.array(e_body).T).T
            ax.plot3D(*zip(s_rotated, e_rotated), color='b')

        # draw a point as "CG"
        ax.scatter([0], [0], [0], color='g', s=100)

        # draw a vector to point forward
        s_rotated = np.matmul(plane.R_FB(phi, theta, psi), np.array(forward[0]).T).T
        e_rotated = np.matmul(plane.R_FB(phi, theta, psi), np.array(forward[1]).T).T
        ax.quiver(s_rotated[0], s_rotated[1], s_rotated[2], e_rotated[0], e_rotated[1], e_rotated[2])
        camera.snap()
        return ax,

    for i in range(len(sim_Euler2) - 1):
        animate(i)
    animation = camera.animate(interval=50)
    animation.save('basic_animation_002.gif', writer=PillowWriter())
    plt.show()


if __name__ == '__main__':
    main()
