import numpy as np
import math as m

class MathModel:
    def __init__(self, inner_rpm, outer_rpm, delta_x, delta_y, delta_z, duration_hours, theta_2_init, theta_1_init):
        self.inner_rpm = inner_rpm  
        self.outer_rpm = outer_rpm 
        self.delta_x = delta_x      
        self.delta_y = delta_y      
        self.delta_z = delta_z      
        self.duration_hours = duration_hours
        self.theta_2_init = self.deg_to_rad(theta_2_init)
        self.theta_1_init = self.deg_to_rad(theta_1_init)    
        self.pi_over_30 = np.pi / 30 
        self.g = np.array([[0], [0], [9.8]]) 

    def deg_to_rad(self, degrees):
        return np.radians(degrees)
    
    def rpm_to_rad_sec(self, rpm):
        return rpm * self.pi_over_30

    def calculate_acceleration(self):
        start_time_in_seconds = 0
        end_time_in_seconds = int(self.duration_hours * 3600) 
        time_array = np.linspace(start_time_in_seconds, end_time_in_seconds, m.floor(end_time_in_seconds / 0.1) + 1)

        inner_rad_sec = self.rpm_to_rad_sec(self.inner_rpm) 
        outer_rad_sec = self.rpm_to_rad_sec(self.outer_rpm)  

        theta_1 = outer_rad_sec * time_array + self.theta_1_init
        theta_2 = inner_rad_sec * time_array + self.theta_2_init   

        w = np.array([
            outer_rad_sec * np.ones_like(time_array),          
            inner_rad_sec * np.cos(theta_1),                   
            inner_rad_sec * np.sin(theta_1)                    
        ]) 

        w_dot = np.array([
            np.zeros_like(time_array),                        
            -outer_rad_sec * inner_rad_sec * np.sin(theta_1),  
            outer_rad_sec * inner_rad_sec * np.cos(theta_1)   
        ])  

        r = np.array([
            self.delta_x * np.cos(theta_2) + self.delta_z * np.sin(theta_2),
            self.delta_y * np.cos(theta_1) + self.delta_x * np.sin(theta_1) * np.sin(theta_2) - self.delta_z * np.sin(theta_1) * np.cos(theta_2),
            self.delta_y * np.sin(theta_1) - self.delta_x * np.cos(theta_1) * np.sin(theta_2) + self.delta_z * np.cos(theta_1) * np.cos(theta_2)
        ])

        w_cross_r = np.cross(w.T, r.T).T
        w_cross_w_cross_r = np.cross(w.T, w_cross_r.T).T
        w_dot_cross_r = np.cross(w_dot.T, r.T).T
        a = -(w_dot_cross_r + w_cross_w_cross_r)  

        R_y_T = np.array([
            [np.cos(theta_2), np.zeros_like(theta_2), -np.sin(theta_2)],
            [np.zeros_like(theta_2), np.ones_like(theta_2), np.zeros_like(theta_2)],
            [np.sin(theta_2), np.zeros_like(theta_2), np.cos(theta_2)]
        ])  

        R_x_T = np.array([
            [np.ones_like(theta_1), np.zeros_like(theta_1), np.zeros_like(theta_1)],
            [np.zeros_like(theta_1), np.cos(theta_1), np.sin(theta_1)],
            [np.zeros_like(theta_1), -np.sin(theta_1), np.cos(theta_1)]
        ]) 

        a_prime = np.einsum('ijk,jk->ik', R_y_T, np.einsum('ijk,jk->ik', R_x_T, a)) / 9.8
        g_prime = np.einsum('ijk,jk->ik', R_y_T, np.einsum('ijk,jk->ik', R_x_T, self.g)) / 9.8

        return time_array, g_prime, a_prime