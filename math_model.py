import numpy as np
import math as m

class MathModel:
    def __init__(self, omega_alpha_rpm, omega_beta_rpm, alpha_0_deg, beta_0_deg, x, y, z, duration_hours):
        self.omega_alpha_rpm = omega_alpha_rpm  
        self.omega_beta_rpm = omega_beta_rpm
        self.alpha_0 = alpha_0_deg
        self.beta_0 = beta_0_deg 
        self.x = x / 100      
        self.y = y / 100     
        self.z = z / 100     
        self.duration_hours = duration_hours  
        self.pi_over_30 = np.pi / 30 
        self.g = np.array([[0], [0], [1]]) 

    def deg_to_rad(self, degrees):
        return np.radians(degrees)
    
    def rpm_to_rad_sec(self, rpm):
        return rpm * self.pi_over_30

    def calculate_acceleration(self):
        end_time_in_seconds = int(self.duration_hours * 3600) 
        time_array = np.linspace(0, end_time_in_seconds, m.floor(end_time_in_seconds / 0.1) + 1)

        omega_alpha = self.rpm_to_rad_sec(self.omega_alpha_rpm) 
        omega_beta = self.rpm_to_rad_sec(self.omega_beta_rpm)

        alpha_0 = self.deg_to_rad(self.alpha_0)
        beta_0 = self.deg_to_rad(self.beta_0)  

        alpha_t = omega_alpha * time_array + alpha_0
        beta_t = omega_beta * time_array + beta_0

        omega_tot = np.array([
            omega_alpha * np.ones_like(time_array),          
            omega_beta * np.cos(alpha_t),                   
            omega_beta * np.sin(alpha_t)                    
        ]) 

        omega_tot_dot = np.array([
            np.zeros_like(time_array),                        
            -omega_alpha * omega_beta * np.sin(alpha_t),  
            omega_alpha * omega_beta * np.cos(alpha_t)   
        ])  

        r = np.array([
            self.x * np.cos(beta_t) + self.z * np.sin(beta_t),
            self.y * np.cos(alpha_t) + self.x * np.sin(alpha_t) * np.sin(beta_t) - self.z * np.sin(alpha_t) * np.cos(beta_t),
            self.y * np.sin(alpha_t) - self.x * np.cos(alpha_t) * np.sin(beta_t) + self.z * np.cos(alpha_t) * np.cos(beta_t)
        ])

        omega_cross_r = np.cross(omega_tot.T, r.T).T
        omega_cross_omega_cross_r = np.cross(omega_tot.T, omega_cross_r.T).T
        omega_dot_cross_r = np.cross(omega_tot_dot.T, r.T).T
        a = -(omega_dot_cross_r + omega_cross_omega_cross_r)  

        R_y_T = np.array([
            [np.cos(beta_t), np.zeros_like(beta_t), -np.sin(beta_t)],
            [np.zeros_like(beta_t), np.ones_like(beta_t), np.zeros_like(beta_t)],
            [np.sin(beta_t), np.zeros_like(beta_t), np.cos(beta_t)]
        ])  

        R_x_T = np.array([
            [np.ones_like(alpha_t), np.zeros_like(alpha_t), np.zeros_like(alpha_t)],
            [np.zeros_like(alpha_t), np.cos(alpha_t), np.sin(alpha_t)],
            [np.zeros_like(alpha_t), -np.sin(alpha_t), np.cos(alpha_t)]
        ]) 

        a_local_2 = np.einsum('ijk,jk->ik', R_y_T, np.einsum('ijk,jk->ik', R_x_T, a)) 
        g_local_2 = np.einsum('ijk,jk->ik', R_y_T, np.einsum('ijk,jk->ik', R_x_T, self.g))

        a_tot_local_2 = a_local_2 + g_local_2 

        return time_array, g_local_2, a_local_2, a_tot_local_2