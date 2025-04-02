import numpy as np

class RigidBody:
    def __init__(self, inner_rpm, outer_rpm, delta_x, delta_y, delta_z, duration_hours):
        self.inner_rpm = inner_rpm  
        self.outer_rpm = outer_rpm 
        self.delta_x = delta_x      
        self.delta_y = delta_y      
        self.delta_z = delta_z      
        self.duration_hours = duration_hours
        self.pi_over_30 = np.pi / 30 
        self.g = np.array([[0], [0], [-9.8]]) 

    def rpm_to_rad_sec(self, rpm):
        return rpm * self.pi_over_30

    def calculate_acceleration(self):
        inner_rad_sec = self.rpm_to_rad_sec(self.inner_rpm) 
        outer_rad_sec = self.rpm_to_rad_sec(self.outer_rpm)  

        start_time_in_seconds = 0
        end_time_in_seconds = int(self.duration_hours * 3600) 
        time_array = np.arange(start_time_in_seconds, end_time_in_seconds + 1)

        theta_1 = inner_rad_sec * time_array  
        theta_2 = outer_rad_sec * time_array  

        w = np.array([
            outer_rad_sec * np.ones_like(time_array),          
            inner_rad_sec * np.cos(theta_2),                   
            inner_rad_sec * np.sin(theta_2)                    
        ]) 

        w_dot = np.array([
            np.zeros_like(time_array),                        
            -outer_rad_sec * inner_rad_sec * np.sin(theta_2),  
            outer_rad_sec * inner_rad_sec * np.cos(theta_2)   
        ])  

        r = np.array([
            self.delta_x * np.cos(theta_1) + self.delta_z * np.sin(theta_1),
            self.delta_y * np.cos(theta_2) + self.delta_x * np.sin(theta_2) * np.sin(theta_1) - self.delta_z * np.sin(theta_2) * np.cos(theta_1),
            self.delta_y * np.sin(theta_2) - self.delta_x * np.cos(theta_2) * np.sin(theta_1) + self.delta_z * np.cos(theta_2) * np.cos(theta_1)
        ])

        w_cross_r = np.cross(w.T, r.T).T
        w_cross_w_cross_r = np.cross(w.T, w_cross_r.T).T
        w_dot_cross_r = np.cross(w_dot.T, r.T).T
        a = -(w_dot_cross_r + w_cross_w_cross_r)  

        R_y_T = np.array([
            [np.cos(theta_1), np.zeros_like(theta_1), -np.sin(theta_1)],
            [np.zeros_like(theta_1), np.ones_like(theta_1), np.zeros_like(theta_1)],
            [np.sin(theta_1), np.zeros_like(theta_1), np.cos(theta_1)]
        ])  

        R_x_T = np.array([
            [np.ones_like(theta_2), np.zeros_like(theta_2), np.zeros_like(theta_2)],
            [np.zeros_like(theta_2), np.cos(theta_2), np.sin(theta_2)],
            [np.zeros_like(theta_2), -np.sin(theta_2), np.cos(theta_2)]
        ]) 

        a_prime = np.einsum('ijk,jk->ik', R_y_T, np.einsum('ijk,jk->ik', R_x_T, a)) 
        g_prime = np.einsum('ijk,jk->ik', R_y_T, np.einsum('ijk,jk->ik', R_x_T, self.g)) / 9.8

        a_tot_prime = a_prime + g_prime 

        return time_array, g_prime, a_prime, a_tot_prime
