import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

class KimModel:
    def __init__(self, inner_rpm, outer_rpm, delta_x, delta_y, delta_z, duration_hours):
        """
        Initialize the 3D clinostat model.
        
        Parameters:
        - inner_rpm: Inner frame rotation speed (RPM) 
        - outer_rpm: Outer frame rotation speed (RPM)
        - delta_x, delta_y, delta_z: Position deviations from clinostat center (meters)
        - duration_hours: Simulation duration (hours)
        """
        self.inner_rpm = inner_rpm  
        self.outer_rpm = outer_rpm 
        self.delta_x = delta_x      # Δx
        self.delta_y = delta_y      # Δy
        self.delta_z = delta_z      # Δz
        self.duration_hours = duration_hours
        self.pi_over_30 = np.pi / 30  # Conversion factor from RPM to rad/s
        self.g = np.array([[0], [0], [-1]])  # Shape: (3, 1)

    def rpm_to_rad_sec(self, rpm):
        """Convert RPM to radians per second."""
        return rpm * self.pi_over_30

    def calculate_acceleration(self):
        """
        Calculate total acceleration in Local 2 frame over time.
        
        Returns:
        - time_array: Time points (seconds)
        - ax, ay, az: Acceleration components in Local 2 frame (m/s²)
        """
        # Convert RPM to rad/s
        inner_rad_sec = self.rpm_to_rad_sec(self.inner_rpm)  # θ₁ (inner frame)
        outer_rad_sec = self.rpm_to_rad_sec(self.outer_rpm)  # θ₂ (outer frame)

        # Time array in seconds
        time_array = np.linspace(0, self.duration_hours * 3600, num=int(self.duration_hours * 3600))

        # Angles as function of time
        theta_1 = inner_rad_sec * time_array  # θ₁ (inner frame angle)
        theta_2 = outer_rad_sec * time_array  # θ₂ (outer frame angle)

        # Total angular velocity w = w₁ + w₂
        w = np.array([
            inner_rad_sec * np.ones_like(time_array),          # w_x = θ₁̇
            outer_rad_sec * np.cos(theta_1),                   # w_y = θ₂̇ cos(θ₁)
            outer_rad_sec * np.sin(theta_1)                    # w_z = θ₂̇ sin(θ₁)
        ])  # Shape: (3, len(time_array))

        # Angular acceleration (derivative of w)
        w_dot = np.array([
            np.zeros_like(time_array),                         # ẇ_x = 0 (constant θ₁̇)
            -inner_rad_sec * outer_rad_sec * np.sin(theta_1),  # ẇ_y = -θ₁̇ θ₂̇ sin(θ₁)
            inner_rad_sec * outer_rad_sec * np.cos(theta_1)    # ẇ_z = θ₁̇ θ₂̇ cos(θ₁)
        ])  # Shape: (3, len(time_array))

        # Position in global frame
        r = np.array([
            self.delta_x * np.cos(theta_2) + self.delta_z * np.sin(theta_2),
            self.delta_y * np.cos(theta_1) + self.delta_x * np.sin(theta_1) * np.sin(theta_2) - self.delta_z * np.sin(theta_1) * np.cos(theta_2),
            self.delta_y * np.sin(theta_1) - self.delta_x * np.cos(theta_1) * np.sin(theta_2) + self.delta_z * np.cos(theta_1) * np.cos(theta_2)
        ])

        # Acceleration components
        w_cross_r = np.cross(w.T, r.T).T
        w_cross_w_cross_r = np.cross(w.T, w_cross_r.T).T
        w_dot_cross_r = np.cross(w_dot.T, r.T).T
        a = -(w_dot_cross_r + w_cross_w_cross_r)  # a(t) = -{ẇ × r + w × (w × r)}

        # Rotation matrices (transposed)
        R_y_T = np.array([
            [np.cos(theta_1), np.zeros_like(theta_1), -np.sin(theta_1)],
            [np.zeros_like(theta_1), np.ones_like(theta_1), np.zeros_like(theta_1)],
            [np.sin(theta_1), np.zeros_like(theta_1), np.cos(theta_1)]
        ])  # R_y^T(θ₁)

        R_x_T = np.array([
            [np.ones_like(theta_2), np.zeros_like(theta_2), np.zeros_like(theta_2)],
            [np.zeros_like(theta_2), np.cos(theta_2), np.sin(theta_2)],
            [np.zeros_like(theta_2), -np.sin(theta_2), np.cos(theta_2)]
        ])  # R_x^T(θ₂)

        # Transform accelerations to Local 2 frame
        a_prime = np.einsum('ijk,jk->ik', R_y_T, np.einsum('ijk,jk->ik', R_x_T, a))  # a(t)''
        g_prime = np.einsum('ijk,jk->ik', R_y_T, np.einsum('ijk,jk->ik', R_x_T, self.g))  # g(t)''

        # Total acceleration in Local 2 frame
        a_tot_prime = a_prime + g_prime  # a(t)_{tot}''

        return time_array, g_prime, a_prime, a_tot_prime

def plot_kim_results(time_array, g_prime, a_prime, a_tot_prime):
    time_hours = time_array / 3600

    # Time-averaged gravitational acceleration
    g_x_avg = np.cumsum(g_prime[0]) / np.arange(1, len(g_prime[0]) + 1)
    g_y_avg = np.cumsum(g_prime[1]) / np.arange(1, len(g_prime[1]) + 1)
    g_z_avg = np.cumsum(g_prime[2]) / np.arange(1, len(g_prime[2]) + 1)
    g_magnitude_avg = np.sqrt(g_x_avg**2 + g_y_avg**2 + g_z_avg**2)

    # Time-averaged non-gravitational acceleration
    plt.figure()
    plt.plot(time_hours, g_magnitude_avg, color='blue')
    plt.title("Time-Averaged Gravitational Acceleration")
    plt.xlim(left=0, right=time_hours[-1])
    #plt.ylim(bottom=0)
    plt.yscale('log')
    plt.xlabel("Time (h)")
    plt.ylabel("Acceleration (m/s²)")
    plt.show()

    plt.figure()
    plt.plot(time_hours, g_x_avg, label="X", color='red')
    plt.plot(time_hours, g_y_avg, label="Y", color='lime')
    plt.plot(time_hours, g_z_avg, label="Z", color='blue')
    plt.plot(time_hours, g_magnitude_avg, label="X+Y+Z", color='black')
    plt.title("Time-Averaged Gravitational Acceleration")
    plt.xlim(left=0, right=time_hours[-1])
    plt.xlabel("Time (h)")
    plt.ylabel("Acceleration (m/s²)")
    plt.legend()
    plt.show()

    # Time-averaged non-gravitational acceleration
    a_x_avg = np.cumsum(a_prime[0]) / np.arange(1, len(a_prime[0]) + 1)
    a_y_avg = np.cumsum(a_prime[1]) / np.arange(1, len(a_prime[1]) + 1)
    a_z_avg = np.cumsum(a_prime[2]) / np.arange(1, len(a_prime[2]) + 1)
    a_magnitude_avg = np.sqrt(a_x_avg**2 + a_y_avg**2 + a_z_avg**2)

    plt.figure()
    plt.plot(time_hours, a_x_avg, label="X", color='red')
    plt.plot(time_hours, a_y_avg, label="Y", color='lime')
    plt.plot(time_hours, a_z_avg, label="Z", color='blue')
    plt.plot(time_hours, a_magnitude_avg, label="X+Y+Z", color='black')
    plt.title("Time-Averaged Non-Gravitational Acceleration")
    plt.xlim(left=0, right=time_hours[-1])
    plt.xlabel("Time (h)")
    plt.ylabel("Acceleration (m/s²)")
    plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    plt.gca().ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    plt.legend()
    plt.show()

    # Acceleration vector path plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Normalize the acceleration vectors to unit vectors
    a_tot_prime_magnitude = np.linalg.norm(a_tot_prime, axis=0)
    a_tot_prime_unit = a_tot_prime / a_tot_prime_magnitude
    
    ax.plot(a_tot_prime_unit[0], a_tot_prime_unit[1], a_tot_prime_unit[2], color='blue', linewidth=1)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ticks = np.arange(-1.0, 1.5, 0.5)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_zticks(ticks)
    ax.set_title("Acceleration Vector Path")
    plt.show()

if __name__ == "__main__":
    inner_rpm = float(input("Enter inner frame velocity (RPM): "))
    outer_rpm = float(input("Enter outer frame velocity (RPM): "))
    duration_hours = float(input("Enter duration (hours): "))

    model = KimModel(inner_rpm, outer_rpm, 0.1, 0.1, 0.1, duration_hours)
    time_array, g_prime, a_prime, a_tot_prime = model.calculate_acceleration()
    plot_kim_results(time_array, g_prime, a_prime, a_tot_prime)