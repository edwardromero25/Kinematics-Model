# Author: Edward Romero, OSTEM Intern, Spring 2025, NASA Kennedy Space Center

import os
import webbrowser
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
from dateutil import parser
from matplotlib import rcParams
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from PIL import Image, ImageTk
from spherical_coordinates import DataProcessor, PathVisualization
from rigid_body import RigidBody
import matplotlib.animation as animation
import csv
from matplotlib.backend_bases import MouseEvent

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

class CustomToolbar(NavigationToolbar2Tk):
     def __init__(self, canvas, parent, export_callback=None, export_components_callback=None, export_distribution_callback=None):
         self.toolitems = list(NavigationToolbar2Tk.toolitems)
         if export_callback:
             self.toolitems.append(("ExportData", "Export data to CSV", "filesave", "export_data"))
         if export_components_callback:
             self.toolitems.append(("ExportComponents", "Export data to CSV", "filesave", "export_components_data"))
         if export_distribution_callback:
             self.toolitems.append(("ExportDistribution", "Export data to CSV", "filesave", "export_distribution_data"))
         super().__init__(canvas, parent)
         self.export_callback = export_callback
         self.export_components_callback = export_components_callback
         self.export_distribution_callback = export_distribution_callback
 
     def export_data(self):
         if self.export_callback:
             self.export_callback()
 
     def export_components_data(self):
         if self.export_components_callback:
             self.export_components_callback()

     def export_distribution_data(self):
         if self.export_distribution_callback:
             self.export_distribution_callback()


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 0
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify=tk.LEFT,
            background="systembuttonface", relief=tk.SOLID, borderwidth=1,
        )
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Microgravity Simulation Support Facility - NASA")
        self.master.configure(bg="#f1f1f1")
        self.current_mode = "Spherical Coordinates"
        self.setup_gui_elements()
        self.setup_plot_frames()   

    def setup_gui_elements(self):
        self.load_images()
        self.master.iconphoto(False, self.favicon)
        self.create_custom_theme()
        font_style = ("Calibri", 12)
        title_font_style = ("Calibri", 20, "bold")
        category_font_style = ("Calibri", 14, "bold")
        input_frame = tk.Frame(self.master, padx=1, pady=1, bg="#f1f1f1")
        input_frame.pack(side=tk.TOP, anchor=tk.CENTER)
        self.create_title_frame(input_frame, title_font_style)
        center_frame = tk.Frame(input_frame, bg="#f1f1f1")
        center_frame.pack()
        self.create_mode_frame(center_frame, font_style, category_font_style)
        self.create_frame_velocities_frame(center_frame, font_style, category_font_style)
        self.create_distance_frame(center_frame, font_style, category_font_style)
        self.create_simulation_duration_frame(center_frame, font_style, category_font_style)
        self.create_time_period_analysis_frame(center_frame, font_style, category_font_style)
        self.create_time_period_analysis_exp_frame(center_frame, font_style, category_font_style)
        self.create_start_button(center_frame, font_style)
        self.create_accelerometer_data_frame(center_frame, font_style, category_font_style)
        self.distance_frame.grid_remove()

    def load_images(self):
        nasa_image = Image.open(os.path.join(SCRIPT_DIR, 'images', 'NASA_logo.png')).resize((69, 58), Image.LANCZOS)
        self.nasa_logo = ImageTk.PhotoImage(nasa_image)
        mssf_image = Image.open(os.path.join(SCRIPT_DIR, 'images', 'MSSF_logo.png')).resize((65, 58), Image.LANCZOS)
        self.mssf_logo = ImageTk.PhotoImage(mssf_image)
        self.favicon = ImageTk.PhotoImage(file=os.path.join(SCRIPT_DIR, 'images', 'favicon.ico'))
        info_image = Image.open(os.path.join(SCRIPT_DIR, 'images', 'info.png')).resize((16, 16), Image.LANCZOS)
        self.info_icon = ImageTk.PhotoImage(info_image)

    def create_title_frame(self, parent, font_style):
        title_frame = tk.Frame(parent)
        title_frame.pack(pady=(10, 0))
        nasa_label = tk.Label(title_frame, image=self.nasa_logo)
        nasa_label.pack(side=tk.LEFT, padx=1)
        nasa_label.bind("<Button-1>", lambda e: self.open_url("https://www.nasa.gov/"))
        title_label = tk.Label(title_frame, text="Computer Model", font=font_style)
        title_label.pack(side=tk.LEFT, padx=1)
        mssf_label = tk.Label(title_frame, image=self.mssf_logo)
        mssf_label.pack(side=tk.LEFT, padx=1)
        mssf_label.bind("<Button-1>", lambda e: self.open_url("https://public.ksc.nasa.gov/partnerships/capabilities-and-testing/testing-and-labs/microgravity-simulation-support-facility/"))

    def create_mode_frame(self, parent, font_style, category_font_style):
        mode_frame = tk.Frame(parent, padx=1, pady=1)
        mode_frame.grid(row=0, column=0, padx=20)
        mode_label_frame = tk.Frame(mode_frame)
        mode_label_frame.pack()
        self.mode_label = tk.Label(mode_label_frame, text="Mode", font=category_font_style)
        self.mode_label.pack(side=tk.LEFT)
        self.mode_icon = tk.Label(mode_label_frame, image=self.info_icon)
        self.mode_icon.pack(side=tk.LEFT, padx=(1, 0))
        self.mode_icon.bind("<Button-1>", lambda e: self.open_info_link())
        ToolTip(self.mode_icon, "Reference")  
        self.mode_var = tk.StringVar(value="Spherical Coordinates")
        menu_button = tk.Menubutton(mode_frame, text="Theoretical", font=font_style, bg="#aeb0b5", activebackground="#d6d7d9", relief=tk.RAISED, pady=6)
        self.mode_menu = tk.Menu(menu_button, tearoff=0)
        self.mode_menu.config(font=("Calibri", 10), bg="#d6d7d9")
        menu_button.config(menu=self.mode_menu)
        theoretical_menu = tk.Menu(self.mode_menu, tearoff=0)
        theoretical_menu.config(font=("Calibri", 10), bg="#d6d7d9")
        self.mode_menu.add_cascade(label="Theoretical", menu=theoretical_menu)
        theoretical_menu.add_command(label="Mathematical Model", command=None, font=("Calibri", 10, "bold"), foreground="black", activeforeground="black", activebackground="#d6d7d9")
        theoretical_menu.add_radiobutton(label="Spherical Coordinates", variable=self.mode_var, value="Spherical Coordinates", command=lambda: self.switch_mode("Spherical Coordinates"))
        theoretical_menu.add_radiobutton(label="3D Rigid Body Kinematics", variable=self.mode_var, value="3D Rigid Body Kinematics", command=lambda: self.switch_mode("3D Rigid Body Kinematics"))
        self.mode_menu.add_radiobutton(label="Experimental", variable=self.mode_var, value="Experimental", command=lambda: self.switch_mode("Experimental"))
        menu_button.pack()

    def create_frame_velocities_frame(self, parent, font_style, category_font_style):
        self.frame_velocities_frame = tk.Frame(parent, padx=1, pady=1)
        self.frame_velocities_frame.grid(row=0, column=1, padx=20)
        tk.Label(self.frame_velocities_frame, text="Frame Velocities (rpm)", font=category_font_style).pack()
        operating_input_frame = tk.Frame(self.frame_velocities_frame)
        operating_input_frame.pack()
        self.inner_velocity_label = tk.Label(operating_input_frame, text="Inner:", font=font_style)
        self.inner_velocity_label.pack(side=tk.LEFT)
        self.inner_velocity_entry = tk.Entry(operating_input_frame, font=font_style, width=10)
        self.inner_velocity_entry.pack(side=tk.LEFT)
        self.outer_velocity_label = tk.Label(operating_input_frame, text="Outer:", font=font_style)
        self.outer_velocity_label.pack(side=tk.LEFT, padx=(10, 0))
        self.outer_velocity_entry = tk.Entry(operating_input_frame, font=font_style, width=10)
        self.outer_velocity_entry.pack(side=tk.LEFT)

    def create_distance_frame(self, parent, font_style, category_font_style):
        self.distance_frame = tk.Frame(parent, padx=1, pady=1)
        self.distance_frame.grid(row=0, column=2, padx=20)
        tk.Label(self.distance_frame, text="Distance from Center (cm)", font=category_font_style).pack()
        self.distance_entry = tk.Entry(self.distance_frame, font=font_style)
        self.distance_entry.pack()

    def create_simulation_duration_frame(self, parent, font_style, category_font_style):
        self.simulation_duration_frame = tk.Frame(parent, padx=1, pady=1)
        self.simulation_duration_frame.grid(row=0, column=3, padx=20)
        tk.Label(self.simulation_duration_frame, text="Simulation Duration (hours)", font=category_font_style).pack()
        self.simulation_duration_entry = tk.Entry(self.simulation_duration_frame, font=font_style)
        self.simulation_duration_entry.pack()

    def create_time_period_analysis_frame(self, parent, font_style, category_font_style):
        self.time_period_analysis_frame = tk.Frame(parent, padx=1, pady=1)
        self.time_period_analysis_frame.grid(row=0, column=4, padx=20)
        tk.Label(self.time_period_analysis_frame, text="Time Period of Analysis (hours)", font=category_font_style).pack()
        analysis_period_frame = tk.Frame(self.time_period_analysis_frame)
        analysis_period_frame.pack()
        self.start_analysis_entry = tk.Entry(analysis_period_frame, font=font_style, width=10)
        self.start_analysis_entry.pack(side=tk.LEFT)
        tk.Label(analysis_period_frame, text="-", font=font_style).pack(side=tk.LEFT)
        self.end_analysis_entry = tk.Entry(analysis_period_frame, font=font_style, width=10)
        self.end_analysis_entry.pack(side=tk.LEFT)

    def create_time_period_analysis_exp_frame(self, parent, font_style, category_font_style):
        self.time_period_analysis_exp_frame = tk.Frame(parent, padx=1, pady=1)
        self.time_period_analysis_exp_frame.grid(row=0, column=5, padx=20)
        self.time_period_analysis_exp_frame.grid_remove()
        tk.Label(self.time_period_analysis_exp_frame, text="Time Period of Analysis (hours)", font=category_font_style).pack()
        analysis_period_frame_exp = tk.Frame(self.time_period_analysis_exp_frame)
        analysis_period_frame_exp.pack()
        self.start_analysis_exp_entry = tk.Entry(analysis_period_frame_exp, font=font_style, width=10)
        self.start_analysis_exp_entry.pack(side=tk.LEFT)
        tk.Label(analysis_period_frame_exp, text="-", font=font_style).pack(side=tk.LEFT)
        self.end_analysis_exp_entry = tk.Entry(analysis_period_frame_exp, font=font_style, width=10)
        self.end_analysis_exp_entry.pack(side=tk.LEFT)

    def create_start_button(self, parent, font_style):
        self.start_button = tk.Button(parent, text="Start", command=self.start_simulation, font=font_style, bg="#0066b2", fg="#ffffff", activebackground="#3380cc", activeforeground="#ffffff")
        self.start_button.grid(row=1, column=0, columnspan=5, pady=(10, 5))

    def create_accelerometer_data_frame(self, parent, font_style, category_font_style):
        self.accelerometer_data_frame = tk.Frame(parent, padx=1, pady=1)
        tk.Label(self.accelerometer_data_frame, text="Accelerometer Data", font=category_font_style).pack()
        self.upload_file_button = tk.Button(self.accelerometer_data_frame, text="Upload File (CSV)", command=self.import_data, font=font_style, bg="#aeb0b5", activebackground="#d6d7d9")
        self.upload_file_button.pack()

    def setup_plot_frames(self):
        plot_frame = tk.Frame(self.master, padx=5, pady=5, bg="#f1f1f1")
        plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=(5, 5), pady=(0, 5))
        self.notebook = ttk.Notebook(plot_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.gravitational_acceleration_frame = tk.Frame(self.notebook, borderwidth=0, relief=tk.SOLID)
        self.acceleration_distribution_frame = tk.Frame(self.notebook, borderwidth=0, relief=tk.SOLID)
        self.notebook.add(self.gravitational_acceleration_frame, text="Gravitational Acceleration")
        self.notebook.add(self.acceleration_distribution_frame, text="Acceleration Distribution")
        rcParams['font.family'] = 'Calibri'
        rcParams['font.size'] = 10
        self.setup_gravitational_acceleration_plot()
        self.setup_acceleration_distribution_plots()
        self.clear_plots()

    def setup_gravitational_acceleration_plot(self):
        self.gravitational_acceleration_frame_left = tk.Frame(self.gravitational_acceleration_frame, borderwidth=1, relief=tk.SOLID)
        self.gravitational_acceleration_frame_left.grid(row=0, column=0, sticky="nsew")
        self.gravitational_acceleration_toolbar_frame_left = tk.Frame(self.gravitational_acceleration_frame_left, borderwidth=0, relief=tk.SOLID)
        self.gravitational_acceleration_toolbar_frame_left.pack(side=tk.BOTTOM, fill=tk.X)
        self.gravitational_acceleration_frame_right = tk.Frame(self.gravitational_acceleration_frame, borderwidth=1, relief=tk.SOLID)
        self.gravitational_acceleration_frame_right.grid(row=0, column=1, sticky="nsew")
        self.gravitational_acceleration_toolbar_frame_right = tk.Frame(self.gravitational_acceleration_frame_right, borderwidth=0, relief=tk.SOLID)
        self.gravitational_acceleration_toolbar_frame_right.pack(side=tk.BOTTOM, fill=tk.X)
        self.gravitational_acceleration_frame.grid_columnconfigure(0, weight=1)
        self.gravitational_acceleration_frame.grid_columnconfigure(1, weight=1)
        self.gravitational_acceleration_frame.grid_rowconfigure(0, weight=1)
        self.gravitational_acceleration_figure_left = plt.Figure()
        self.gravitational_acceleration_ax_left = self.gravitational_acceleration_figure_left.add_subplot(1, 1, 1)
        self.gravitational_acceleration_ax_left.set_title("Time-Averaged Gravitational Acceleration")
        self.gravitational_acceleration_ax_left.set_xlabel('Time (hours)')
        self.gravitational_acceleration_ax_left.set_ylabel('Acceleration (g)')
        self.gravitational_acceleration_canvas_left = FigureCanvasTkAgg(self.gravitational_acceleration_figure_left, self.gravitational_acceleration_frame_left)
        self.gravitational_acceleration_canvas_left.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.gravitational_acceleration_toolbar_left = CustomToolbar(self.gravitational_acceleration_canvas_left, self.gravitational_acceleration_toolbar_frame_left, self._export_magnitude_data)
        self.gravitational_acceleration_toolbar_left.update()
        self.gravitational_acceleration_figure_right = plt.Figure()
        self.gravitational_acceleration_ax_right = self.gravitational_acceleration_figure_right.add_subplot(1, 1, 1)
        self.gravitational_acceleration_canvas_right = FigureCanvasTkAgg(self.gravitational_acceleration_figure_right, self.gravitational_acceleration_frame_right)
        self.gravitational_acceleration_canvas_right.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.gravitational_acceleration_toolbar_right = CustomToolbar(self.gravitational_acceleration_canvas_right, self.gravitational_acceleration_toolbar_frame_right, export_components_callback=self._export_components_data)
        self.gravitational_acceleration_toolbar_right.update()
        self.create_time_averaged_gravitational_acceleration_fig([], [], [], [], legend=False, title=False)

    def _export_magnitude_data(self):
         file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
         if file_path:
             try:
                 if not self.gravitational_acceleration_ax_left.lines:
                     raise ValueError("No data available to export.")
                 with open(file_path, mode='w', newline='') as file:
                     writer = csv.writer(file)
                     writer.writerow(["Time (hours)", "Acceleration (g)"])
                     for time, mag in zip(self.gravitational_acceleration_ax_left.lines[0].get_xdata(), self.gravitational_acceleration_ax_left.lines[0].get_ydata()):
                         writer.writerow([time, mag])
                 messagebox.showinfo("Success", "Data exported successfully.")
             except Exception as e:
                 messagebox.showerror("Error", str(e))

    def _export_components_data(self):
         file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
         if file_path:
             try:
                 if not self.gravitational_acceleration_ax_right.lines:
                     raise ValueError("No data available to export.")
                 with open(file_path, mode='w', newline='') as file:
                     writer = csv.writer(file)
                     writer.writerow(["Time (hours)", "X (g)", "Y (g)", "Z (g)"])
                     time_data = self.gravitational_acceleration_ax_right.lines[0].get_xdata()
                     x_data = self.gravitational_acceleration_ax_right.lines[0].get_ydata()
                     y_data = self.gravitational_acceleration_ax_right.lines[1].get_ydata()
                     z_data = self.gravitational_acceleration_ax_right.lines[2].get_ydata()
                     for time, x, y, z in zip(time_data, x_data, y_data, z_data):
                         writer.writerow([time, x, y, z])
                 messagebox.showinfo("Success", "Data exported successfully.")
             except Exception as e:
                 messagebox.showerror("Error", str(e))
    
    def _export_distribution_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                if not self.acceleration_distribution_ax.lines:
                    raise ValueError("No data available to export.")
            
                line = self.acceleration_distribution_ax.lines[0]
                x_data, y_data, z_data = line.get_data_3d()
                time_data = self.gravitational_acceleration_ax_left.lines[0].get_xdata()
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Time (hours)", "X", "Y", "Z"]) 
                    for time, x, y, z in zip(time_data, x_data, y_data, z_data):
                        writer.writerow([time, x, y, z])
            
                messagebox.showinfo("Success", "Data exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))


    def setup_acceleration_distribution_plots(self):
        self.acceleration_distribution_frame_left = tk.Frame(self.acceleration_distribution_frame, borderwidth=1, relief=tk.SOLID)
        self.acceleration_distribution_frame_left.grid(row=0, column=0, sticky="nsew")
        self.acceleration_distribution_toolbar_frame_left = tk.Frame(self.acceleration_distribution_frame_left, borderwidth=0, relief=tk.SOLID)
        self.acceleration_distribution_toolbar_frame_left.pack(side=tk.BOTTOM, fill=tk.X)
        self.acceleration_distribution_frame_right = tk.Frame(self.acceleration_distribution_frame, borderwidth=1, relief=tk.SOLID)
        self.acceleration_distribution_frame_right.grid(row=0, column=1, sticky="nsew")
        self.acceleration_distribution_toolbar_frame_right = tk.Frame(self.acceleration_distribution_frame_right, borderwidth=0, relief=tk.SOLID)
        self.acceleration_distribution_toolbar_frame_right.pack(side=tk.BOTTOM, fill=tk.X)
        self.acceleration_distribution_frame.grid_columnconfigure(0, weight=1)
        self.acceleration_distribution_frame.grid_columnconfigure(1, weight=1)
        self.acceleration_distribution_frame.grid_rowconfigure(0, weight=1)

        self.acceleration_distribution_figure = plt.Figure()
        self.acceleration_distribution_ax = self.acceleration_distribution_figure.add_subplot(1, 1, 1, projection='3d')
        self.configure_3d_axes(self.acceleration_distribution_ax, "Acceleration Distribution")
        self.acceleration_distribution_canvas = FigureCanvasTkAgg(self.acceleration_distribution_figure, self.acceleration_distribution_frame_left)
        self.acceleration_distribution_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.acceleration_distribution_analysis_figure = plt.Figure()
        self.acceleration_distribution_ax_analysis = self.acceleration_distribution_analysis_figure.add_subplot(1, 1, 1, projection='3d')
        self.configure_3d_axes(self.acceleration_distribution_ax_analysis, "Acceleration Distribution")
        self.acceleration_distribution_canvas_analysis = FigureCanvasTkAgg(self.acceleration_distribution_analysis_figure, self.acceleration_distribution_frame_right)
        self.acceleration_distribution_canvas_analysis.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.acceleration_distribution_toolbar = CustomToolbar(self.acceleration_distribution_canvas, self.acceleration_distribution_toolbar_frame_left, export_distribution_callback=self._export_distribution_data)
        self.acceleration_distribution_toolbar.update()
        self.acceleration_distribution_analysis_toolbar = NavigationToolbar2Tk(self.acceleration_distribution_canvas_analysis, self.acceleration_distribution_toolbar_frame_right)
        self.acceleration_distribution_analysis_toolbar.update()

    def configure_3d_axes(self, ax, title):
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_xlim(-1, 1)
        ax.set_ylim(1, -1)
        ax.set_zlim(-1, 1)
        ax.set_xticks([-1, -0.5, 0, 0.5, 1])  
        ax.set_yticks([-1, -0.5, 0, 0.5, 1])  
        ax.set_zticks([-1, -0.5, 0, 0.5, 1])  
        ax.set_title(title)

    def create_custom_theme(self):
        style = ttk.Style()
        style.theme_create("yummy", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [1, 0, 0, 0], "background": "#f1f1f1"}},
            "TNotebook.Tab": {
                "configure": {"padding": [5, 1], "background": "#aeb0b5", "font": ("Calibri", 12), "focuscolor": ""},
                "map": {"background": [("selected", "#d6d7d9")], "expand": [("selected", [1, 1, 1, 0])]}
            }
        })
        style.theme_use("yummy")

    def open_info_link(self):
        if self.current_mode == "Spherical Coordinates":
            webbrowser.open("https://www.frontiersin.org/journals/space-technologies/articles/10.3389/frspt.2022.1032610/full")
        elif self.current_mode == "3D Rigid Body Kinematics":
            webbrowser.open("https://biomedical-engineering-online.biomedcentral.com/articles/10.1186/s12938-017-0337-8")

    def switch_mode(self, mode):
        if self.current_mode == mode:
            return
        self.current_mode = mode

        if mode in ["Spherical Coordinates", "3D Rigid Body Kinematics"]:
            self.mode_menu.master.config(text="Theoretical")
            self.mode_label.config(text="Mode")
            self.mode_icon.pack(side=tk.LEFT, padx=(1, 0))  
        else:
            self.mode_menu.master.config(text=mode)
            self.mode_label.config(text="Mode")
            self.mode_icon.pack_forget()  

        if mode == "Spherical Coordinates":
            self.show_spherical_inputs()
        elif mode == "Experimental":
            self.show_experimental_inputs()
        elif mode == "3D Rigid Body Kinematics":
            self.show_3d_rigid_body_inputs()

    def show_spherical_inputs(self):
        self.frame_velocities_frame.grid()
        self.distance_frame.grid_remove()
        self.simulation_duration_frame.grid()
        self.time_period_analysis_frame.grid()
        self.time_period_analysis_exp_frame.grid_remove()
        self.accelerometer_data_frame.grid_remove()
        self.start_button.grid(row=1, column=0, columnspan=5, pady=(10, 5))
        if hasattr(self, 'rigid_body_tabs_created') and self.rigid_body_tabs_created:
            self.notebook.forget(self.rigid_body_gravitational_acceleration_frame)
            self.notebook.forget(self.rigid_body_non_gravitational_acceleration_frame)
            self.notebook.forget(self.rigid_body_acceleration_distribution_frame)
            self.rigid_body_tabs_created = False
        if not self.notebook.index("end"):
            self.notebook.add(self.gravitational_acceleration_frame, text="Gravitational Acceleration")
            self.notebook.add(self.acceleration_distribution_frame, text="Acceleration Distribution")
        self.clear_plots()

    def show_experimental_inputs(self):
        self.frame_velocities_frame.grid_remove()
        self.distance_frame.grid_remove()
        self.simulation_duration_frame.grid_remove()
        self.time_period_analysis_frame.grid_remove()
        self.time_period_analysis_exp_frame.grid(row=0, column=2, padx=20)
        self.accelerometer_data_frame.grid(row=0, column=1, padx=20)
        self.start_button.grid(row=1, column=0, columnspan=3, pady=(10, 5))
        if hasattr(self, 'rigid_body_tabs_created') and self.rigid_body_tabs_created:
            self.notebook.forget(self.rigid_body_gravitational_acceleration_frame)
            self.notebook.forget(self.rigid_body_non_gravitational_acceleration_frame)
            self.notebook.forget(self.rigid_body_acceleration_distribution_frame)
            self.rigid_body_tabs_created = False
        if not self.notebook.index("end"):
            self.notebook.add(self.gravitational_acceleration_frame, text="Gravitational Acceleration")
            self.notebook.add(self.acceleration_distribution_frame, text="Acceleration Distribution")
        self.clear_plots()

    def show_3d_rigid_body_inputs(self):
        self.frame_velocities_frame.grid()
        self.distance_frame.grid()
        self.simulation_duration_frame.grid()
        self.time_period_analysis_frame.grid()
        self.time_period_analysis_exp_frame.grid_remove()
        self.accelerometer_data_frame.grid_remove()
        self.start_button.grid(row=1, column=0, columnspan=5, pady=(10, 5))
        self.notebook.forget(self.gravitational_acceleration_frame)
        self.notebook.forget(self.acceleration_distribution_frame)
        if not hasattr(self, 'rigid_body_tabs_created') or not self.rigid_body_tabs_created:
            self.rigid_body_gravitational_acceleration_frame = tk.Frame(self.notebook, borderwidth=0, relief=tk.SOLID)
            self.rigid_body_gravitational_acceleration_frame_left = tk.Frame(self.rigid_body_gravitational_acceleration_frame, borderwidth=1, relief=tk.SOLID)
            self.rigid_body_gravitational_acceleration_frame_left.grid(row=0, column=0, sticky="nsew")
            self.rigid_body_gravitational_acceleration_toolbar_frame_left = tk.Frame(self.rigid_body_gravitational_acceleration_frame_left, borderwidth=0, relief=tk.SOLID)
            self.rigid_body_gravitational_acceleration_toolbar_frame_left.pack(side=tk.BOTTOM, fill=tk.X)
            self.rigid_body_gravitational_acceleration_frame_right = tk.Frame(self.rigid_body_gravitational_acceleration_frame, borderwidth=1, relief=tk.SOLID)
            self.rigid_body_gravitational_acceleration_frame_right.grid(row=0, column=1, sticky="nsew")
            self.rigid_body_gravitational_acceleration_toolbar_frame_right = tk.Frame(self.rigid_body_gravitational_acceleration_frame_right, borderwidth=0, relief=tk.SOLID)
            self.rigid_body_gravitational_acceleration_toolbar_frame_right.pack(side=tk.BOTTOM, fill=tk.X)
            self.rigid_body_gravitational_acceleration_frame.grid_columnconfigure(0, weight=1)
            self.rigid_body_gravitational_acceleration_frame.grid_columnconfigure(1, weight=1)
            self.rigid_body_gravitational_acceleration_frame.grid_rowconfigure(0, weight=1)
            self.rigid_body_non_gravitational_acceleration_frame = tk.Frame(self.notebook, borderwidth=0, relief=tk.SOLID)
            self.rigid_body_non_gravitational_acceleration_frame_left = tk.Frame(self.rigid_body_non_gravitational_acceleration_frame, borderwidth=1, relief=tk.SOLID)
            self.rigid_body_non_gravitational_acceleration_frame_left.grid(row=0, column=0, sticky="nsew")
            self.rigid_body_non_gravitational_acceleration_toolbar_frame_left = tk.Frame(self.rigid_body_non_gravitational_acceleration_frame_left, borderwidth=0, relief=tk.SOLID)
            self.rigid_body_non_gravitational_acceleration_toolbar_frame_left.pack(side=tk.BOTTOM, fill=tk.X)
            self.rigid_body_non_gravitational_acceleration_frame_right = tk.Frame(self.rigid_body_non_gravitational_acceleration_frame, borderwidth=1, relief=tk.SOLID)
            self.rigid_body_non_gravitational_acceleration_frame_right.grid(row=0, column=1, sticky="nsew")
            self.rigid_body_non_gravitational_acceleration_toolbar_frame_right = tk.Frame(self.rigid_body_non_gravitational_acceleration_frame_right, borderwidth=0, relief=tk.SOLID)
            self.rigid_body_non_gravitational_acceleration_toolbar_frame_right.pack(side=tk.BOTTOM, fill=tk.X)
            self.rigid_body_non_gravitational_acceleration_frame.grid_columnconfigure(0, weight=1)
            self.rigid_body_non_gravitational_acceleration_frame.grid_columnconfigure(1, weight=1)
            self.rigid_body_non_gravitational_acceleration_frame.grid_rowconfigure(0, weight=1)
            self.rigid_body_acceleration_distribution_frame = tk.Frame(self.notebook, borderwidth=0, relief=tk.SOLID)
            self.notebook.add(self.rigid_body_gravitational_acceleration_frame, text="Gravitational Acceleration")
            self.notebook.add(self.rigid_body_non_gravitational_acceleration_frame, text="Non-Gravitational Acceleration")
            self.notebook.add(self.rigid_body_acceleration_distribution_frame, text="Acceleration Distribution")
            self.rigid_body_gravitational_acceleration_figure = plt.Figure()
            self.rigid_body_gravitational_acceleration_ax = self.rigid_body_gravitational_acceleration_figure.add_subplot(1, 1, 1)
            self.rigid_body_gravitational_acceleration_canvas = FigureCanvasTkAgg(self.rigid_body_gravitational_acceleration_figure, self.rigid_body_gravitational_acceleration_frame_left)
            self.rigid_body_gravitational_acceleration_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.rigid_body_gravitational_components_figure = plt.Figure()
            self.rigid_body_gravitational_components_ax = self.rigid_body_gravitational_components_figure.add_subplot(1, 1, 1)
            self.rigid_body_gravitational_components_canvas = FigureCanvasTkAgg(self.rigid_body_gravitational_components_figure, self.rigid_body_gravitational_acceleration_frame_right)
            self.rigid_body_gravitational_components_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.rigid_body_gravitational_components_toolbar = CustomToolbar(self.rigid_body_gravitational_components_canvas, self.rigid_body_gravitational_acceleration_toolbar_frame_right, export_components_callback=self._export_rigid_body_components_data)
            self.rigid_body_gravitational_components_toolbar.update()
            self.rigid_body_gravitational_acceleration_toolbar = CustomToolbar(self.rigid_body_gravitational_acceleration_canvas, self.rigid_body_gravitational_acceleration_toolbar_frame_left, self._export_rigid_body_magnitude_data)
            self.rigid_body_gravitational_acceleration_toolbar.update()
            self.rigid_body_non_gravitational_acceleration_figure = plt.Figure()
            self.rigid_body_non_gravitational_acceleration_ax = self.rigid_body_non_gravitational_acceleration_figure.add_subplot(1, 1, 1)
            self.rigid_body_non_gravitational_acceleration_canvas = FigureCanvasTkAgg(self.rigid_body_non_gravitational_acceleration_figure, self.rigid_body_non_gravitational_acceleration_frame_left)
            self.rigid_body_non_gravitational_acceleration_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.rigid_body_non_gravitational_components_figure = plt.Figure()
            self.rigid_body_non_gravitational_components_ax = self.rigid_body_non_gravitational_components_figure.add_subplot(1, 1, 1)
            self.rigid_body_non_gravitational_components_canvas = FigureCanvasTkAgg(self.rigid_body_non_gravitational_components_figure, self.rigid_body_non_gravitational_acceleration_frame_right)
            self.rigid_body_non_gravitational_components_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.rigid_body_non_gravitational_acceleration_toolbar = CustomToolbar(self.rigid_body_non_gravitational_acceleration_canvas, self.rigid_body_non_gravitational_acceleration_toolbar_frame_left, self._export_rigid_body_non_g_magnitude_data)
            self.rigid_body_non_gravitational_acceleration_toolbar.update()
            self.rigid_body_non_gravitational_components_toolbar = CustomToolbar(self.rigid_body_non_gravitational_components_canvas, self.rigid_body_non_gravitational_acceleration_toolbar_frame_right, export_components_callback=self._export_rigid_body_non_g_components_data)
            self.rigid_body_non_gravitational_components_toolbar.update()
            self.rigid_body_acceleration_distribution_frame_left = tk.Frame(self.rigid_body_acceleration_distribution_frame, borderwidth=1, relief=tk.SOLID)
            self.rigid_body_acceleration_distribution_frame_left.grid(row=0, column=0, sticky="nsew")
            self.rigid_body_acceleration_distribution_toolbar_frame_left = tk.Frame(self.rigid_body_acceleration_distribution_frame_left, borderwidth=0, relief=tk.SOLID)
            self.rigid_body_acceleration_distribution_toolbar_frame_left.pack(side=tk.BOTTOM, fill=tk.X)
            self.rigid_body_acceleration_distribution_frame_right = tk.Frame(self.rigid_body_acceleration_distribution_frame, borderwidth=1, relief=tk.SOLID)
            self.rigid_body_acceleration_distribution_frame_right.grid(row=0, column=1, sticky="nsew")
            self.rigid_body_acceleration_distribution_toolbar_frame_right = tk.Frame(self.rigid_body_acceleration_distribution_frame_right, borderwidth=0, relief=tk.SOLID)
            self.rigid_body_acceleration_distribution_toolbar_frame_right.pack(side=tk.BOTTOM, fill=tk.X)
            self.rigid_body_acceleration_distribution_frame.grid_columnconfigure(0, weight=1)
            self.rigid_body_acceleration_distribution_frame.grid_columnconfigure(1, weight=1)
            self.rigid_body_acceleration_distribution_frame.grid_rowconfigure(0, weight=1)
            self.rigid_body_acceleration_distribution_figure = plt.Figure()
            self.rigid_body_acceleration_distribution_ax = self.rigid_body_acceleration_distribution_figure.add_subplot(1, 1, 1, projection='3d')
            self.configure_3d_axes(self.rigid_body_acceleration_distribution_ax, "Acceleration Distribution")
            self.rigid_body_acceleration_distribution_canvas = FigureCanvasTkAgg(self.rigid_body_acceleration_distribution_figure, self.rigid_body_acceleration_distribution_frame_left)
            self.rigid_body_acceleration_distribution_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.rigid_body_acceleration_distribution_analysis_figure = plt.Figure()
            self.rigid_body_acceleration_distribution_analysis_ax = self.rigid_body_acceleration_distribution_analysis_figure.add_subplot(1, 1, 1, projection='3d')
            self.configure_3d_axes(self.rigid_body_acceleration_distribution_analysis_ax, "Acceleration Distribution")
            self.rigid_body_acceleration_distribution_analysis_canvas = FigureCanvasTkAgg(self.rigid_body_acceleration_distribution_analysis_figure, self.rigid_body_acceleration_distribution_frame_right)
            self.rigid_body_acceleration_distribution_analysis_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.rigid_body_acceleration_distribution_toolbar = CustomToolbar(self.rigid_body_acceleration_distribution_canvas, self.rigid_body_acceleration_distribution_toolbar_frame_left, export_distribution_callback=self._export_rigid_body_distribution_data)
            self.rigid_body_acceleration_distribution_toolbar.update()
            self.rigid_body_acceleration_distribution_analysis_toolbar = NavigationToolbar2Tk(self.rigid_body_acceleration_distribution_analysis_canvas, self.rigid_body_acceleration_distribution_toolbar_frame_right)
            self.rigid_body_acceleration_distribution_analysis_toolbar.update()
            self.rigid_body_tabs_created = True
        self.clear_rigid_body_tabs()

    def _export_rigid_body_magnitude_data(self):
         file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
         if file_path:
             try:
                 if not self.rigid_body_gravitational_acceleration_ax.lines:
                     raise ValueError("No data available to export.")
                 with open(file_path, mode='w', newline='') as file:
                     writer = csv.writer(file)
                     writer.writerow(["Time (hours)", "Acceleration (g)"])
                     for time, mag in zip(self.rigid_body_gravitational_acceleration_ax.lines[0].get_xdata(), self.rigid_body_gravitational_acceleration_ax.lines[0].get_ydata()):
                         writer.writerow([time, mag])
                 messagebox.showinfo("Success", "Data exported successfully.")
             except Exception as e:
                 messagebox.showerror("Error", str(e))

    def _export_rigid_body_components_data(self):
         file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
         if file_path:
             try:
                 if not self.rigid_body_gravitational_components_ax.lines:
                     raise ValueError("No data available to export.")
                 with open(file_path, mode='w', newline='') as file:
                     writer = csv.writer(file)
                     writer.writerow(["Time (hours)", "X (g)", "Y (g)", "Z (g)"])
                     time_data = self.rigid_body_gravitational_components_ax.lines[0].get_xdata()
                     x_data = self.rigid_body_gravitational_components_ax.lines[0].get_ydata()
                     y_data = self.rigid_body_gravitational_components_ax.lines[1].get_ydata()
                     z_data = self.rigid_body_gravitational_components_ax.lines[2].get_ydata()
                     for time, x, y, z in zip(time_data, x_data, y_data, z_data):
                         writer.writerow([time, x, y, z])
                 messagebox.showinfo("Success", "Data exported successfully.")
             except Exception as e:
                 messagebox.showerror("Error", str(e))

    def _export_rigid_body_non_g_magnitude_data(self):
         file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
         if file_path:
             try:
                 if not self.rigid_body_non_gravitational_acceleration_ax.lines:
                     raise ValueError("No data available to export.")
                 with open(file_path, mode='w', newline='') as file:
                     writer = csv.writer(file)
                     writer.writerow(["Time (hours)", "Acceleration (g)"])
                     for time, mag in zip(self.rigid_body_non_gravitational_acceleration_ax.lines[0].get_xdata(), self.rigid_body_non_gravitational_acceleration_ax.lines[0].get_ydata()):
                         writer.writerow([time, mag])
                 messagebox.showinfo("Success", "Data exported successfully.")
             except Exception as e:
                 messagebox.showerror("Error", str(e))

    def _export_rigid_body_non_g_components_data(self):
         file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
         if file_path:
             try:
                 if not self.rigid_body_non_gravitational_components_ax.lines:
                     raise ValueError("No data available to export.")
                 with open(file_path, mode='w', newline='') as file:
                     writer = csv.writer(file)
                     writer.writerow(["Time (hours)", "X (g)", "Y (g)", "Z (g)"])
                     time_data = self.rigid_body_non_gravitational_components_ax.lines[0].get_xdata()
                     x_data = self.rigid_body_non_gravitational_components_ax.lines[0].get_ydata()
                     y_data = self.rigid_body_non_gravitational_components_ax.lines[1].get_ydata()
                     z_data = self.rigid_body_non_gravitational_components_ax.lines[2].get_ydata()
                     for time, x, y, z in zip(time_data, x_data, y_data, z_data):
                         writer.writerow([time, x, y, z])
                 messagebox.showinfo("Success", "Data exported successfully.")
             except Exception as e:
                 messagebox.showerror("Error", str(e))

    def _export_rigid_body_distribution_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                if not self.rigid_body_acceleration_distribution_ax.lines:
                    raise ValueError("No data available to export.")
            
                line = self.rigid_body_acceleration_distribution_ax.lines[0]
                x_data, y_data, z_data = line.get_data_3d()
                time_data = self.rigid_body_non_gravitational_acceleration_ax.lines[0].get_xdata()
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Time (hours)", "X", "Y", "Z"]) 
                    for time, x, y, z in zip(time_data, x_data, y_data, z_data):
                        writer.writerow([time, x, y, z])
            
                messagebox.showinfo("Success", "Data exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def clear_rigid_body_tabs(self):
        self.rigid_body_gravitational_acceleration_ax.clear()
        self.rigid_body_gravitational_acceleration_ax.set_title("Time-Averaged Gravitational Acceleration")
        self.rigid_body_gravitational_acceleration_ax.set_xlabel('Time (hours)')
        self.rigid_body_gravitational_acceleration_ax.set_ylabel('Acceleration (g)')
        self.rigid_body_gravitational_acceleration_canvas.draw()
        self.rigid_body_gravitational_components_ax.clear()
        self.rigid_body_gravitational_components_ax.set_title("Time-Averaged Gravitational Acceleration")
        self.rigid_body_gravitational_components_ax.set_xlabel('Time (hours)')
        self.rigid_body_gravitational_components_ax.set_ylabel('Acceleration (g)')
        self.rigid_body_gravitational_components_canvas.draw()
        self.rigid_body_non_gravitational_acceleration_ax.clear()
        self.rigid_body_non_gravitational_acceleration_ax.set_title("Time-Averaged Non-Gravitational Acceleration")
        self.rigid_body_non_gravitational_acceleration_ax.set_xlabel('Time (hours)')
        self.rigid_body_non_gravitational_acceleration_ax.set_ylabel('Acceleration (g)')
        self.rigid_body_non_gravitational_acceleration_canvas.draw()
        self.rigid_body_non_gravitational_components_ax.clear()
        self.rigid_body_non_gravitational_components_ax.set_title("Time-Averaged Non-Gravitational Acceleration")
        self.rigid_body_non_gravitational_components_ax.set_xlabel('Time (hours)')
        self.rigid_body_non_gravitational_components_ax.set_ylabel('Acceleration (g)')
        self.rigid_body_non_gravitational_components_canvas.draw()
        self.rigid_body_acceleration_distribution_ax.clear()
        self.configure_3d_axes(self.rigid_body_acceleration_distribution_ax, "Acceleration Distribution")
        self.rigid_body_acceleration_distribution_canvas.draw()
        self.rigid_body_acceleration_distribution_analysis_ax.clear()
        self.configure_3d_axes(self.rigid_body_acceleration_distribution_analysis_ax, "Acceleration Distribution")
        self.rigid_body_acceleration_distribution_analysis_canvas.draw()

    def clear_plots(self):
        self.gravitational_acceleration_ax_left.clear()
        self.gravitational_acceleration_ax_left.set_title("Time-Averaged Gravitational Acceleration")
        self.gravitational_acceleration_ax_left.set_xlabel('Time (hours)')
        self.gravitational_acceleration_ax_left.set_ylabel('Acceleration (g)')
        self.gravitational_acceleration_canvas_left.draw()
        self.gravitational_acceleration_toolbar_left.update() 

        self.gravitational_acceleration_ax_right.clear()
        self.gravitational_acceleration_ax_right.set_title("Time-Averaged Gravitational Acceleration")
        self.gravitational_acceleration_ax_right.set_xlabel('Time (hours)')
        self.gravitational_acceleration_ax_right.set_ylabel('Acceleration (g)')
        self.gravitational_acceleration_canvas_right.draw()
        self.gravitational_acceleration_toolbar_right.update()  

        self.acceleration_distribution_ax.clear()
        self.configure_3d_axes(self.acceleration_distribution_ax, "Acceleration Distribution")
        self.acceleration_distribution_canvas.draw()
        self.acceleration_distribution_toolbar.update() 

        self.acceleration_distribution_ax_analysis.clear()
        self.configure_3d_axes(self.acceleration_distribution_ax_analysis, "Acceleration Distribution")
        self.acceleration_distribution_canvas_analysis.draw()
        self.acceleration_distribution_analysis_toolbar.update() 

    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    main_array = file.read().replace("   ", " ").replace('\t', ' ').replace('\n', ' ').replace(',', ' ').split(' ')
                self.experimental_data = main_array
                messagebox.showinfo("Success", "CSV file uploaded successfully.")
            except FileNotFoundError:
                messagebox.showerror("File Error", f"File not found: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def process_experimental_data(self, main_array, start_analysis, end_analysis):
        datetime_str = []
        x, y, z = [], [], []
        for k in range(0, len(main_array) - 4, 5):
            try:
                dt = parser.parse(main_array[k] + " " + main_array[k + 1])
            except ValueError:
                dt = parser.parse(main_array[k + 1] + " " + main_array[k])
            datetime_str.append(dt)
            x.append(float(main_array[k + 2]))
            y.append(float(main_array[k + 3]))
            z.append(float(main_array[k + 4]))
        time_in_seconds = [(dt - datetime_str[0]).total_seconds() for dt in datetime_str]
        time_in_hours = [t / 3600 for t in time_in_seconds]
        path_vis = PathVisualization("experimental", x, y, z)
        distribution_score = path_vis.get_distribution()
        self.update_experimental_plots(x, y, z, time_in_hours, start_analysis, end_analysis, distribution_score)

    def animate_distribution(self, ax, canvas, x_data, y_data, z_data, color, label):
        ax.clear()
        self.configure_3d_axes(ax, "Acceleration Distribution")
        line, = ax.plot([], [], [], color=color, linewidth=1)

        path_vis = PathVisualization("animated", x_data, y_data, z_data)
        distribution_score = path_vis.get_distribution()

        def update(num):
            line.set_data(x_data[:num], y_data[:num])
            line.set_3d_properties(z_data[:num])
            return line,

        ax.legend([f"Distribution: {distribution_score}"])
        ani = animation.FuncAnimation(
            ax.figure, update, frames=len(x_data), interval=100, blit=False  
        )
        canvas.draw()

    def update_experimental_plots(self, x, y, z, time_in_hours, start_analysis, end_analysis, distribution_score):
        rcParams['font.family'] = 'Calibri'
        self.gravitational_acceleration_ax_left.clear()
        self.gravitational_acceleration_ax_left.set_title("Time-Averaged Gravitational Acceleration")
        self.gravitational_acceleration_ax_left.set_xlim(left=0, right=time_in_hours[-1])
        x_time_avg = np.cumsum(x) / np.arange(1, len(x) + 1)
        y_time_avg = np.cumsum(y) / np.arange(1, len(y) + 1)
        z_time_avg = np.cumsum(z) / np.arange(1, len(z) + 1)
        magnitude = np.sqrt(x_time_avg**2 + y_time_avg**2 + z_time_avg**2)
        avg_mag_full = np.mean(magnitude)
        self.gravitational_acceleration_ax_left.plot(time_in_hours, magnitude, color='#0066B2', label=f"Magnitude: {avg_mag_full:.3g}")
        self.gravitational_acceleration_ax_left.legend()
        self.gravitational_acceleration_ax_left.set_xlabel('Time (hours)')
        self.gravitational_acceleration_ax_left.set_ylabel('Acceleration (g)')
        y_min = np.min(magnitude)
        y_max = np.max(magnitude)
        self.gravitational_acceleration_ax_left.set_ylim(y_min, y_max)
        self.gravitational_acceleration_canvas_left.draw()
        self.acceleration_distribution_ax.clear()
        if start_analysis is not None and end_analysis is not None:
            start_seg = next(i for i, t in enumerate(time_in_hours) if t >= start_analysis)
            end_seg = next(i for i, t in enumerate(time_in_hours) if t >= end_analysis)
            self.gravitational_acceleration_ax_left.axvline(x=start_analysis, color='#EC1C24', linestyle='--')
            self.gravitational_acceleration_ax_left.axvline(x=end_analysis, color='#EC1C24', linestyle='--')
            avg_mag_analysis = np.mean(magnitude[start_seg:end_seg])
            self.gravitational_acceleration_ax_left.plot(time_in_hours[start_seg:end_seg], magnitude[start_seg:end_seg], color='#EC1C24', label=f"Magnitude: {avg_mag_analysis:.3g}")
        self.gravitational_acceleration_ax_left.legend()
        self.gravitational_acceleration_ax_left.set_xlabel('Time (hours)')
        self.gravitational_acceleration_ax_left.set_ylabel('Acceleration (g)')
        self.gravitational_acceleration_ax_left.set_xlim(left=0, right=time_in_hours[-1])
        self.gravitational_acceleration_canvas_left.draw()
        self.acceleration_distribution_ax.clear()
        self.acceleration_distribution_ax.plot(x, y, z, color='#0066b2', linewidth=1)
        self.configure_3d_axes(self.acceleration_distribution_ax, "Acceleration Distribution")
        self.acceleration_distribution_ax.legend([f"Distribution: {distribution_score}"])
        self.acceleration_distribution_canvas.draw()
        self.create_time_averaged_gravitational_acceleration_fig(x_time_avg, y_time_avg, z_time_avg, time_in_hours)
        self.acceleration_distribution_ax_analysis.clear()
        if start_analysis is not None and end_analysis is not None:
            start_seg = next(i for i, t in enumerate(time_in_hours) if t >= start_analysis)
            end_seg = next(i for i, t in enumerate(time_in_hours) if t >= end_analysis)
            sliced_x, sliced_y, sliced_z = x[start_seg:end_seg], y[start_seg:end_seg], z[start_seg:end_seg]
            path_vis_analysis = PathVisualization("experimental", sliced_x, sliced_y, sliced_z)
            distribution_score_analysis = path_vis_analysis.get_distribution()
            self.animate_distribution(
                self.acceleration_distribution_ax_analysis,
                self.acceleration_distribution_canvas_analysis,
                sliced_x, sliced_y, sliced_z,
                color='#ec1c24',
                label=f"Distribution: {distribution_score_analysis}"
            )
        else:
            self.configure_3d_axes(self.acceleration_distribution_ax_analysis, "Acceleration Distribution")
            self.acceleration_distribution_canvas_analysis.draw()

    def start_simulation(self):
        try:
            if self.mode_var.get() == "Spherical Coordinates":
                self.process_spherical_data()
            elif self.mode_var.get() == "Experimental":
                self.process_experimental_data_submission()
            elif self.mode_var.get() == "3D Rigid Body Kinematics":
                self.process_rigid_body_data()
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def process_spherical_data(self):
        if not all([self.inner_velocity_entry.get(), self.outer_velocity_entry.get(), self.simulation_duration_entry.get()]):
            raise ValueError("Set frame velocities and simulation duration.")
        inner_velocity = float(self.inner_velocity_entry.get())
        outer_velocity = float(self.outer_velocity_entry.get())
        simulation_duration = float(self.simulation_duration_entry.get())
        start_analysis = self.start_analysis_entry.get()
        end_analysis = self.end_analysis_entry.get()
        if simulation_duration <= 0:
            raise ValueError("Simulation duration must be positive.")
        start_analysis = float(start_analysis) if start_analysis else None
        end_analysis = float(end_analysis) if end_analysis else None
        if start_analysis and end_analysis:
            if start_analysis < 0 or end_analysis < 0:
                raise ValueError("Time values must be positive.")
            if end_analysis <= start_analysis:
                raise ValueError("Upper bound for analysis period must be greater than the lower bound.")
            if end_analysis > simulation_duration:
                raise ValueError("Upper bound for analysis period must be less than or equal to the simulation duration.")
        analysis = DataProcessor(inner_velocity, outer_velocity, simulation_duration, start_analysis, end_analysis)
        path_vis = PathVisualization(inner_velocity, analysis.x, analysis.y, analysis.z)
        x_time_avg, y_time_avg, z_time_avg = analysis._get_time_avg()
        magnitude = analysis._get_magnitude(x_time_avg, y_time_avg, z_time_avg)
        avg_mag_seg, avg_mag_analysis = analysis._get_mag_seg(magnitude)
        dis_score = analysis.get_distribution()
        self.update_spherical_plots(analysis, magnitude, start_analysis, end_analysis, avg_mag_seg, avg_mag_analysis, inner_velocity, outer_velocity, dis_score, path_vis)

    def process_experimental_data_submission(self):
        if not hasattr(self, 'experimental_data') or not self.experimental_data:
            raise ValueError("Upload a CSV file.")
        start_analysis = self.start_analysis_exp_entry.get()
        end_analysis = self.end_analysis_exp_entry.get()
        start_analysis = float(start_analysis) if start_analysis else None
        end_analysis = float(end_analysis) if end_analysis else None
        if start_analysis and end_analysis:
            if start_analysis < 0 or end_analysis < 0:
                raise ValueError("Time values must be positive.")
            if end_analysis <= start_analysis:
                raise ValueError("Upper bound for analysis period must be greater than the lower bound.")
            datetime_str = []
            for k in range(0, len(self.experimental_data) - 4, 5):
                try:
                    dt = parser.parse(self.experimental_data[k] + " " + self.experimental_data[k + 1])
                except ValueError:
                    dt = parser.parse(self.experimental_data[k + 1] + " " + self.experimental_data[k])
                datetime_str.append(dt)
            time_in_hours = [(dt - datetime_str[0]).total_seconds() / 3600 for dt in datetime_str]
            if end_analysis > max(time_in_hours):
                raise ValueError("Upper bound for analysis period exceeds the final timestamp in the CSV.")
        self.process_experimental_data(self.experimental_data, start_analysis, end_analysis)

    def update_spherical_plots(self, analysis, magnitude, start_analysis, end_analysis, avg_mag_seg, avg_mag_analysis, inner_velocity, outer_velocity, dis_score, path_vis):
        rcParams['font.family'] = 'Calibri'
        f_time = path_vis.format_time(analysis.time)
        x_time_avg, y_time_avg, z_time_avg = analysis._get_time_avg()
        self.gravitational_acceleration_ax_left.clear()
        self.gravitational_acceleration_ax_left.set_title("Time-Averaged Gravitational Acceleration")
        self.gravitational_acceleration_ax_left.set_xlim(left=0, right=f_time[-1])
        self.gravitational_acceleration_ax_left.plot(f_time, magnitude, color='#0066b2', label=f"Magnitude: {avg_mag_seg:.3g}")
        y_min = np.min(magnitude)
        y_max = np.max(magnitude)
        self.gravitational_acceleration_ax_left.set_ylim(y_min, y_max)
        if start_analysis is not None and end_analysis is not None:
            start_index = next(i for i, t in enumerate(f_time) if t >= start_analysis)
            end_index = next(i for i, t in enumerate(f_time) if t >= end_analysis)
            self.gravitational_acceleration_ax_left.axvline(x=start_analysis, color='#ec1c24', linestyle='--')
            self.gravitational_acceleration_ax_left.axvline(x=end_analysis, color='#ec1c24', linestyle='--')
            self.gravitational_acceleration_ax_left.plot(f_time[start_index:end_index], magnitude[start_index:end_index], color='#ec1c24', label=f"Magnitude: {avg_mag_analysis:.3g}")
        self.gravitational_acceleration_ax_left.legend()
        self.gravitational_acceleration_ax_left.set_xlabel('Time (hours)')
        self.gravitational_acceleration_ax_left.set_ylabel('Acceleration (g)')
        self.gravitational_acceleration_canvas_left.draw()
        self.acceleration_distribution_ax.clear()
        self.acceleration_distribution_ax.plot(analysis.x, analysis.y, analysis.z, color='#0066b2', linewidth=1)
        self.configure_3d_axes(self.acceleration_distribution_ax, "Acceleration Distribution")
        self.acceleration_distribution_ax.legend([f"Distribution: {dis_score}"])
        self.acceleration_distribution_canvas.draw()
        x_time_avg, y_time_avg, z_time_avg = analysis._get_time_avg()
        self.create_time_averaged_gravitational_acceleration_fig(x_time_avg, y_time_avg, z_time_avg, analysis.time)
        self.acceleration_distribution_ax_analysis.clear()
        if start_analysis is not None and end_analysis is not None:
            start_index = next(i for i, t in enumerate(f_time) if t >= start_analysis)
            end_index = next(i for i, t in enumerate(f_time) if t >= end_analysis)
            sliced_x, sliced_y, sliced_z = analysis.x[start_index:end_index], analysis.y[start_index:end_index], analysis.z[start_index:end_index]
            path_vis_analysis = PathVisualization("spherical", sliced_x, sliced_y, sliced_z)
            distribution_score_analysis = path_vis_analysis.get_distribution()
            self.animate_distribution(
                self.acceleration_distribution_ax_analysis,
                self.acceleration_distribution_canvas_analysis,
                sliced_x, sliced_y, sliced_z,
                color='#ec1c24',
                label=f"Distribution: {distribution_score_analysis}"
            )
        else:
            self.configure_3d_axes(self.acceleration_distribution_ax_analysis, "Acceleration Distribution")
            self.acceleration_distribution_canvas_analysis.draw()

    def create_time_averaged_gravitational_acceleration_fig(self, x_time_avg, y_time_avg, z_time_avg, time_data, legend=True, title=True):
        if self.mode_var.get() == "Spherical Coordinates":
            time_in_hours = [t / 3600 for t in time_data]
        else:
            time_in_hours = time_data
        self.gravitational_acceleration_ax_right.clear()
        if title:
            self.gravitational_acceleration_ax_right.set_title('Time-Averaged Gravitational Acceleration')
        if time_in_hours:
            self.gravitational_acceleration_ax_right.plot(time_in_hours, x_time_avg, label='X', color='#6EAE39')
            self.gravitational_acceleration_ax_right.plot(time_in_hours, y_time_avg, label='Y', color='#EF7A35')
            self.gravitational_acceleration_ax_right.plot(time_in_hours, z_time_avg, label='Z', color='mediumorchid')
            self.gravitational_acceleration_ax_right.set_xlim(left=0, right=time_in_hours[-1])
            self.gravitational_acceleration_ax_right.set_xlabel('Time (hours)')
            self.gravitational_acceleration_ax_right.set_ylabel('Acceleration (g)')
            y_min = min(np.min(x_time_avg), np.min(y_time_avg), np.min(z_time_avg))
            y_max = max(np.max(x_time_avg), np.max(y_time_avg), np.max(z_time_avg))
            self.gravitational_acceleration_ax_right.set_ylim(y_min, y_max)
            if legend:
                self.gravitational_acceleration_ax_right.legend()
        self.gravitational_acceleration_canvas_right.draw()

    def process_rigid_body_data(self):
        start_analysis = self.start_analysis_entry.get()
        end_analysis = self.end_analysis_entry.get()
        start_analysis = float(start_analysis) if start_analysis else None
        end_analysis = float(end_analysis) if end_analysis else None
        if start_analysis and end_analysis:
            if start_analysis < 0 or end_analysis < 0:
                raise ValueError("Time values must be positive.")
            if end_analysis <= start_analysis:
                raise ValueError("Upper bound for analysis period must be greater than the lower bound.")
            if end_analysis > float(self.simulation_duration_entry.get()):
                raise ValueError("Upper bound for analysis period must be less than or equal to the simulation duration.")

        if not all([self.inner_velocity_entry.get(), self.outer_velocity_entry.get(), self.distance_entry.get(), self.simulation_duration_entry.get()]):
            raise ValueError("Set frame velocities, distance, and simulation duration.")
        
        duration_hours = float(self.simulation_duration_entry.get())
        if duration_hours <= 0:
            raise ValueError("Simulation duration must be positive.")
        
        inner_rpm = float(self.inner_velocity_entry.get())
        outer_rpm = float(self.outer_velocity_entry.get())
        delta_cm = float(self.distance_entry.get())  
        delta_m = delta_cm / 100  
        delta_x, delta_y, delta_z = delta_m, delta_m, delta_m  

        rigid_body = RigidBody(inner_rpm, outer_rpm, delta_x, delta_y, delta_z, duration_hours)
        time_array, g_array, a_array, a_tot_array = rigid_body.calculate_acceleration()
        g_x_avg = np.cumsum(g_array[0]) / np.arange(1, len(g_array[0]) + 1)
        g_y_avg = np.cumsum(g_array[1]) / np.arange(1, len(g_array[1]) + 1)
        g_z_avg = np.cumsum(g_array[2]) / np.arange(1, len(g_array[2]) + 1)
        g_magnitude = np.sqrt(g_x_avg**2 + g_y_avg**2 + g_z_avg**2)
        avg_g_magnitude = np.mean(g_magnitude)
        a_x_avg = np.cumsum(a_array[0]) / np.arange(1, len(a_array[0]) + 1)
        a_y_avg = np.cumsum(a_array[1]) / np.arange(1, len(a_array[1]) + 1)
        a_z_avg = np.cumsum(a_array[2]) / np.arange(1, len(a_array[2]) + 1)
        a_magnitude = np.sqrt(a_x_avg**2 + a_y_avg**2 + a_z_avg**2)
        avg_a_magnitude = np.mean(a_magnitude)
        self.update_rigid_body_gravitational_acceleration_plot(time_array, g_magnitude, avg_g_magnitude, g_x_avg, g_y_avg, g_z_avg)
        self.update_rigid_body_gravitational_components_plot(time_array, g_x_avg, g_y_avg, g_z_avg)
        self.update_rigid_body_non_gravitational_acceleration_plot(time_array, a_magnitude, avg_a_magnitude, a_x_avg, a_y_avg, a_z_avg)
        self.update_rigid_body_non_gravitational_components_plot(time_array, a_x_avg, a_y_avg, a_z_avg)
        self.update_rigid_body_acceleration_distribution_plot(a_tot_array, time_array)

    def update_rigid_body_gravitational_acceleration_plot(self, time_array, g_magnitude, avg_g_magnitude, g_x_avg, g_y_avg, g_z_avg):
        time_in_hours = time_array / 3600
        self.rigid_body_gravitational_acceleration_ax.clear()
        self.rigid_body_gravitational_acceleration_ax.set_title("Time-Averaged Gravitational Acceleration")
        self.rigid_body_gravitational_acceleration_ax.plot(time_in_hours, g_magnitude, color='#0066b2', label=f"Magnitude: {avg_g_magnitude:.3g}")
        start_analysis = self.start_analysis_entry.get()
        end_analysis = self.end_analysis_entry.get()
        start_analysis = float(start_analysis) if start_analysis else None
        end_analysis = float(end_analysis) if end_analysis else None
        if start_analysis is not None and end_analysis is not None:
            self.rigid_body_gravitational_acceleration_ax.axvline(x=start_analysis, color='#EC1C24', linestyle='--')
            self.rigid_body_gravitational_acceleration_ax.axvline(x=end_analysis, color='#EC1C24', linestyle='--')
            start_index = next(i for i, t in enumerate(time_in_hours) if t >= start_analysis)
            end_index = next(i for i, t in enumerate(time_in_hours) if t >= end_analysis)
            avg_g_magnitude_analysis = np.mean(g_magnitude[start_index:end_index])
            self.rigid_body_gravitational_acceleration_ax.plot(time_in_hours[start_index:end_index], g_magnitude[start_index:end_index], color='#EC1C24', label=f"Magnitude: {avg_g_magnitude_analysis:.3g}")
        y_min = np.min(g_magnitude)
        y_max = np.max(g_magnitude)
        self.rigid_body_gravitational_acceleration_ax.set_ylim(y_min, y_max)
        self.rigid_body_gravitational_acceleration_ax.legend()
        self.rigid_body_gravitational_acceleration_ax.set_xlim(left=0, right=time_in_hours[-1])
        self.rigid_body_gravitational_acceleration_ax.set_xlabel('Time (hours)')
        self.rigid_body_gravitational_acceleration_ax.set_ylabel('Acceleration (g)')
        self.rigid_body_gravitational_acceleration_canvas.draw()

    def update_rigid_body_gravitational_components_plot(self, time_array, g_x_avg, g_y_avg, g_z_avg):
        time_in_hours = time_array / 3600
        self.rigid_body_gravitational_components_ax.clear()
        self.rigid_body_gravitational_components_ax.set_title("Time-Averaged Gravitational Acceleration")
        self.rigid_body_gravitational_components_ax.plot(time_in_hours, g_x_avg, label='X', color='#6EAE39')
        self.rigid_body_gravitational_components_ax.plot(time_in_hours, g_y_avg, label='Y', color='#EF7A35')
        self.rigid_body_gravitational_components_ax.plot(time_in_hours, g_z_avg, label='Z', color='mediumorchid')
        self.rigid_body_gravitational_components_ax.legend()
        self.rigid_body_gravitational_components_ax.set_xlim(left=0, right=time_in_hours[-1])
        self.rigid_body_gravitational_components_ax.set_xlabel('Time (hours)')
        self.rigid_body_gravitational_components_ax.set_ylabel('Acceleration (g)')
        y_min = min(np.min(g_x_avg), np.min(g_y_avg), np.min(g_z_avg))
        y_max = max(np.max(g_x_avg), np.max(g_y_avg), np.max(g_z_avg))
        self.rigid_body_gravitational_components_ax.set_ylim(y_min, y_max)
        self.rigid_body_gravitational_components_canvas.draw()

    def update_rigid_body_non_gravitational_acceleration_plot(self, time_array, a_magnitude, avg_a_magnitude, a_x_avg, a_y_avg, a_z_avg):
        time_in_hours = time_array / 3600
        self.rigid_body_non_gravitational_acceleration_ax.clear()
        self.rigid_body_non_gravitational_acceleration_ax.set_title("Time-Averaged Non-Gravitational Acceleration")
        self.rigid_body_non_gravitational_acceleration_ax.plot(time_in_hours, a_magnitude, color='#0066b2', label=f"Magnitude: {avg_a_magnitude:.3g}")
        start_analysis = self.start_analysis_entry.get()
        end_analysis = self.end_analysis_entry.get()
        start_analysis = float(start_analysis) if start_analysis else None
        end_analysis = float(end_analysis) if end_analysis else None
        if start_analysis is not None and end_analysis is not None:
            self.rigid_body_non_gravitational_acceleration_ax.axvline(x=start_analysis, color='#EC1C24', linestyle='--')
            self.rigid_body_non_gravitational_acceleration_ax.axvline(x=end_analysis, color='#EC1C24', linestyle='--')
            start_index = next(i for i, t in enumerate(time_in_hours) if t >= start_analysis)
            end_index = next(i for i, t in enumerate(time_in_hours) if t >= end_analysis)
            avg_a_magnitude_analysis = np.mean(a_magnitude[start_index:end_index])
            self.rigid_body_non_gravitational_acceleration_ax.plot(time_in_hours[start_index:end_index], a_magnitude[start_index:end_index], color='#EC1C24', label=f"Magnitude: {avg_a_magnitude_analysis:.3g}")
        y_min = np.min(a_magnitude)
        y_max = np.max(a_magnitude)
        self.rigid_body_non_gravitational_acceleration_ax.set_ylim(y_min, y_max)
        self.rigid_body_non_gravitational_acceleration_ax.legend()
        self.rigid_body_non_gravitational_acceleration_ax.set_xlim(left=0, right=time_in_hours[-1])
        self.rigid_body_non_gravitational_acceleration_ax.set_xlabel('Time (hours)')
        self.rigid_body_non_gravitational_acceleration_ax.set_ylabel('Acceleration (g)')
        self.rigid_body_non_gravitational_acceleration_ax.yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        self.rigid_body_non_gravitational_acceleration_ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        self.rigid_body_non_gravitational_acceleration_canvas.draw()

    def update_rigid_body_non_gravitational_components_plot(self, time_array, a_x_avg, a_y_avg, a_z_avg):
        time_in_hours = time_array / 3600
        self.rigid_body_non_gravitational_components_ax.clear()
        self.rigid_body_non_gravitational_components_ax.set_title("Time-Averaged Non-Gravitational Acceleration")
        self.rigid_body_non_gravitational_components_ax.plot(time_in_hours, a_x_avg, label='X', color='#6EAE39')
        self.rigid_body_non_gravitational_components_ax.plot(time_in_hours, a_y_avg, label='Y', color='#EF7A35')
        self.rigid_body_non_gravitational_components_ax.plot(time_in_hours, a_z_avg, label='Z', color='mediumorchid')
        self.rigid_body_non_gravitational_components_ax.legend()
        self.rigid_body_non_gravitational_components_ax.set_xlim(left=0, right=time_in_hours[-1])
        self.rigid_body_non_gravitational_components_ax.set_xlabel('Time (hours)')
        self.rigid_body_non_gravitational_components_ax.set_ylabel('Acceleration (g)')
        self.rigid_body_non_gravitational_components_ax.yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        self.rigid_body_non_gravitational_components_ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        y_min = min(np.min(a_x_avg), np.min(a_y_avg), np.min(a_z_avg))
        y_max = max(np.max(a_x_avg), np.max(a_y_avg), np.max(a_z_avg))
        self.rigid_body_non_gravitational_components_ax.set_ylim(y_min, y_max)
        self.rigid_body_non_gravitational_components_canvas.draw()

    def update_rigid_body_acceleration_distribution_plot(self, a_tot_array, time_array):
        self.rigid_body_acceleration_distribution_ax.clear()
        self.rigid_body_acceleration_distribution_ax.plot(a_tot_array[0], a_tot_array[1], a_tot_array[2], color='#0066b2', linewidth=1)
        self.configure_3d_axes(self.rigid_body_acceleration_distribution_ax, "Acceleration Distribution")
        distribution_score = PathVisualization("rigid_body", a_tot_array[0], a_tot_array[1], a_tot_array[2]).get_distribution()
        self.rigid_body_acceleration_distribution_ax.legend([f"Distribution: {distribution_score}"])
        self.rigid_body_acceleration_distribution_canvas.draw()
        self.rigid_body_acceleration_distribution_analysis_ax.clear()
        start_analysis = self.start_analysis_entry.get()
        end_analysis = self.end_analysis_entry.get()
        start_analysis = float(start_analysis) if start_analysis else None
        end_analysis = float(end_analysis) if end_analysis else None
        if start_analysis is not None and end_analysis is not None:
            time_in_hours = time_array / 3600
            start_index = next(i for i, t in enumerate(time_in_hours) if t >= start_analysis)
            end_index = next(i for i, t in enumerate(time_in_hours) if t >= end_analysis)
            sliced_x, sliced_y, sliced_z = a_tot_array[0][start_index:end_index], a_tot_array[1][start_index:end_index], a_tot_array[2][start_index:end_index]
            path_vis_analysis = PathVisualization("rigid_body", sliced_x, sliced_y, sliced_z)
            distribution_score_analysis = path_vis_analysis.get_distribution()
            self.animate_distribution(
                self.rigid_body_acceleration_distribution_analysis_ax,
                self.rigid_body_acceleration_distribution_analysis_canvas,
                sliced_x, sliced_y, sliced_z,
                color='#ec1c24',
                label=f"Distribution: {distribution_score_analysis}"
            )
        else:
            self.configure_3d_axes(self.rigid_body_acceleration_distribution_analysis_ax, "Acceleration Distribution")
            self.rigid_body_acceleration_distribution_analysis_canvas.draw()

    def open_url(self, url):
        webbrowser.open_new(url)

if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()