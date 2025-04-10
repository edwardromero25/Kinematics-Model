# Author: Edward Romero, OSTEM Intern, NASA Kennedy Space Center, Spring 2025

import csv
import os
import re
import webbrowser
import matplotlib
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.animation import FFMpegWriter
from matplotlib.ticker import ScalarFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from dateutil import parser
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
from math_model import MathModel
from path_visualization import PathVisualization

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

def validate_float(value):
    return re.fullmatch(r"-?\d*\.?\d*", value) is not None

def validate_positive_float(value):
    return re.fullmatch(r"\d*\.?\d*", value) is not None

class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, parent, export_magnitude_callback=None, export_components_callback=None, export_distribution_callback=None, export_animation_callback=None):
        self.toolitems = list(NavigationToolbar2Tk.toolitems)
        if export_magnitude_callback:
            self.toolitems.append(("ExportMagnitude", "Export the data to a CSV file", "export", "export_magnitude_data"))
        if export_components_callback:
            self.toolitems.append(("ExportComponents", "Export the data to a CSV file", "export", "export_components_data"))
        if export_distribution_callback:
            self.toolitems.append(("ExportDistribution", "Export the data to a CSV file", "export", "export_distribution_data"))
        if export_animation_callback:
            self.toolitems.append(("ExportAnimation", "Export the animation to a MP4 file", "export", "export_animation_data"))
        super().__init__(canvas, parent)
        self.export_magnitude_callback = export_magnitude_callback
        self.export_components_callback = export_components_callback
        self.export_distribution_callback = export_distribution_callback
        self.export_animation_callback = export_animation_callback

    def export_magnitude_data(self):
        if self.export_magnitude_callback:
            self.export_magnitude_callback()

    def export_components_data(self):
        if self.export_components_callback:
            self.export_components_callback()

    def export_distribution_data(self):
        if self.export_distribution_callback:
            self.export_distribution_callback()

    def export_animation_data(self):
        if self.export_animation_callback:
            self.export_animation_callback()

class ToolTip:
    def __init__(self, widget, text, x_offset, y_offset):
        self.widget = widget
        self.text = text
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + self.x_offset
        y += self.widget.winfo_rooty() + self.y_offset
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="systembuttonface", relief=tk.SOLID, borderwidth=1)
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
        self.master.state('zoomed')
        self.master.wm_minsize(1280, 720)
        self.current_mode = "Theoretical"
        self.register_validations()
        self.setup_gui_elements()
        self.setup_plot_frames()
        self.show_theoretical_inputs()
        self.last_mode = None
        self.last_inner_velocity = None
        self.last_outer_velocity = None
        self.last_inner_position = None
        self.last_outer_position = None
        self.last_simulation_duration = None
        self.last_distance = None
        self.last_experimental_data = None
        self.last_start_analysis_theo = None
        self.last_end_analysis_theo = None
        self.last_start_analysis_exp = None
        self.last_end_analysis_exp = None

    def setup_gui_elements(self):
        self.load_images()
        self.master.iconphoto(False, self.favicon)
        self.create_custom_theme()

        font_style = ("Calibri", 11)
        title_font_style = ("Calibri", 19, "bold")
        category_font_style = ("Calibri", 13, "bold")

        input_frame = tk.Frame(self.master, padx=1, pady=1, bg="#f1f1f1")
        input_frame.pack(side=tk.TOP, anchor=tk.CENTER)

        self.create_title_frame(input_frame, title_font_style)

        center_frame = tk.Frame(input_frame, bg="#f1f1f1")
        center_frame.pack()

        self.create_mode_frame(center_frame, font_style, category_font_style)
        self.create_theoretical_input_frames(center_frame, font_style, category_font_style)
        self.create_experimental_input_frames(center_frame, font_style, category_font_style)
        self.create_start_button(center_frame, font_style)

    def load_images(self):
        nasa_image = Image.open(os.path.join(SCRIPT_DIR, 'images', 'NASA_logo.png')).resize((60, 50), Image.LANCZOS)
        self.nasa_logo = ImageTk.PhotoImage(nasa_image)
        mssf_image = Image.open(os.path.join(SCRIPT_DIR, 'images', 'MSSF_logo.png')).resize((56, 50), Image.LANCZOS)
        self.mssf_logo = ImageTk.PhotoImage(mssf_image)
        self.favicon = ImageTk.PhotoImage(file=os.path.join(SCRIPT_DIR, 'images', 'favicon.ico'))
        info_image = Image.open(os.path.join(SCRIPT_DIR, 'images', 'info.png')).resize((16, 16), Image.LANCZOS)
        self.info_icon = ImageTk.PhotoImage(info_image)
        asterisk_image = Image.open(os.path.join(SCRIPT_DIR, 'images', 'asterisk.png')).resize((9, 10), Image.LANCZOS)
        self.asterisk_icon = ImageTk.PhotoImage(asterisk_image)

    def create_title_frame(self, parent, font_style):
        title_frame = tk.Frame(parent)
        title_frame.pack(pady=(8, 0))
        nasa_label = tk.Label(title_frame, image=self.nasa_logo, cursor="hand2")
        nasa_label.pack(side=tk.LEFT, padx=1)
        nasa_label.bind("<Button-1>", lambda e: self.open_url("https://www.nasa.gov/"))
        title_label = tk.Label(title_frame, text="Computer Model", font=font_style)
        title_label.pack(side=tk.LEFT, padx=1)
        mssf_label = tk.Label(title_frame, image=self.mssf_logo, cursor="hand2")
        mssf_label.pack(side=tk.LEFT, padx=1)
        mssf_label.bind("<Button-1>", lambda e: self.open_url("https://public.ksc.nasa.gov/partnerships/capabilities-and-testing/testing-and-labs/microgravity-simulation-support-facility/"))

    def create_mode_frame(self, parent, font_style, category_font_style):
        mode_frame = tk.Frame(parent, padx=1, pady=1)
        mode_frame.grid(row=0, column=0, padx=15)

        mode_label_frame = tk.Frame(mode_frame)
        mode_label_frame.pack()

        self.mode_label = tk.Label(mode_label_frame, text="Mode", font=category_font_style)
        self.mode_label.pack(side=tk.LEFT)

        self.mode_icon = tk.Label(mode_label_frame, image=self.info_icon, cursor="hand2")
        self.mode_icon.pack(side=tk.LEFT, padx=(0, 0))
        self.mode_icon.bind("<Button-1>", lambda e: self.open_info_link())
        ToolTip(self.mode_icon, "Reference", x_offset=20, y_offset=0)

        self.mode_var = tk.StringVar(value="Theoretical")
        menu_button = tk.Menubutton(mode_frame, text="Theoretical", font=font_style, bg="#aeb0b5", activebackground="#d6d7d9", relief=tk.RAISED, pady=6)
        self.mode_menu = tk.Menu(menu_button, tearoff=0)
        self.mode_menu.config(font=("Calibri", 9), bg="#d6d7d9")
        menu_button.config(menu=self.mode_menu)
        self.mode_menu.add_radiobutton(label="Theoretical", variable=self.mode_var, value="Theoretical", command=lambda: self.switch_mode("Theoretical"))
        self.mode_menu.add_radiobutton(label="Experimental", variable=self.mode_var, value="Experimental", command=lambda: self.switch_mode("Experimental"))
        menu_button.pack()

    def register_validations(self):
        self.validate_float_cmd = self.master.register(validate_float)
        self.validate_positive_float_cmd = self.master.register(validate_positive_float)

    def create_theoretical_input_frames(self, parent, font_style, category_font_style):
        self.theoretical_angular_velocity_frame = tk.Frame(parent, padx=1, pady=1)
        self.theoretical_angular_velocity_frame.grid(row=0, column=1, padx=15)
        
        velocity_label_frame = tk.Frame(self.theoretical_angular_velocity_frame)
        velocity_label_frame.pack()
        tk.Label(velocity_label_frame, text="Angular Velocity (rpm)", font=category_font_style).pack(side=tk.LEFT)
        
        velocity_asterisk_icon = tk.Label(velocity_label_frame, image=self.asterisk_icon)
        velocity_asterisk_icon.pack(side=tk.LEFT, padx=(0, 0))
        ToolTip(velocity_asterisk_icon, "Required", x_offset=13, y_offset=-3)
        
        velocity_input_frame = tk.Frame(self.theoretical_angular_velocity_frame)
        velocity_input_frame.pack()
        self.inner_velocity_label = tk.Label(velocity_input_frame, text="Inner:", font=font_style)
        self.inner_velocity_label.pack(side=tk.LEFT)
        self.inner_velocity_entry = tk.Entry(velocity_input_frame, font=font_style, width=5, validate="key", validatecommand=(self.validate_float_cmd, "%P"))
        self.inner_velocity_entry.pack(side=tk.LEFT)
        self.outer_velocity_label = tk.Label(velocity_input_frame, text="Outer:", font=font_style)
        self.outer_velocity_label.pack(side=tk.LEFT, padx=(10, 0))
        self.outer_velocity_entry = tk.Entry(velocity_input_frame, font=font_style, width=5, validate="key", validatecommand=(self.validate_float_cmd, "%P"))
        self.outer_velocity_entry.pack(side=tk.LEFT)

        self.theoretical_angular_position_frame = tk.Frame(parent, padx=1, pady=1)
        self.theoretical_angular_position_frame.grid(row=0, column=2, padx=15)
        tk.Label(self.theoretical_angular_position_frame, text="Initial Angular Position (deg)", font=category_font_style).pack()
        position_input_frame = tk.Frame(self.theoretical_angular_position_frame)
        position_input_frame.pack()
        self.inner_position_label = tk.Label(position_input_frame, text="Inner:", font=font_style)
        self.inner_position_label.pack(side=tk.LEFT)
        self.inner_position_entry = tk.Entry(position_input_frame, font=font_style, width=5, validate="key", validatecommand=(self.validate_float_cmd, "%P"))
        self.inner_position_entry.pack(side=tk.LEFT)
        self.outer_position_label = tk.Label(position_input_frame, text="Outer:", font=font_style)
        self.outer_position_label.pack(side=tk.LEFT, padx=(10, 0))
        self.outer_position_entry = tk.Entry(position_input_frame, font=font_style, width=5, validate="key", validatecommand=(self.validate_float_cmd, "%P"))
        self.outer_position_entry.pack(side=tk.LEFT)

        self.theoretical_distance_frame = tk.Frame(parent, padx=1, pady=1)
        self.theoretical_distance_frame.grid(row=0, column=3, padx=15)
        tk.Label(self.theoretical_distance_frame, text="Distance from Center (cm)", font=category_font_style).pack()
        self.distance_entry = tk.Entry(self.theoretical_distance_frame, font=font_style, width=20, validate="key", validatecommand=(self.validate_positive_float_cmd, "%P"))
        self.distance_entry.pack()

        self.theoretical_duration_frame = tk.Frame(parent, padx=1, pady=1)
        self.theoretical_duration_frame.grid(row=0, column=4, padx=15)
        duration_label_frame = tk.Frame(self.theoretical_duration_frame)
        duration_label_frame.pack()
        tk.Label(duration_label_frame, text="Simulation Duration (h)", font=category_font_style).pack(side=tk.LEFT)
       
        duration_asterisk_icon = tk.Label(duration_label_frame, image=self.asterisk_icon)
        duration_asterisk_icon.pack(side=tk.LEFT, padx=(0, 0))
        ToolTip(duration_asterisk_icon, "Required", x_offset=13, y_offset=-3)
        
        self.simulation_duration_entry = tk.Entry(self.theoretical_duration_frame, font=font_style, width=20, validate="key", validatecommand=(self.validate_positive_float_cmd, "%P"))
        self.simulation_duration_entry.pack()

        self.theoretical_analysis_period_frame = tk.Frame(parent, padx=1, pady=1)
        self.theoretical_analysis_period_frame.grid(row=0, column=5, padx=15)
        tk.Label(self.theoretical_analysis_period_frame, text="Time Period of Analysis (h)", font=category_font_style).pack()
        analysis_period_frame = tk.Frame(self.theoretical_analysis_period_frame)
        analysis_period_frame.pack()
        self.start_analysis_theo_entry = tk.Entry(analysis_period_frame, font=font_style, width=10, validate="key", validatecommand=(self.validate_positive_float_cmd, "%P"))
        self.start_analysis_theo_entry.pack(side=tk.LEFT)
        tk.Label(analysis_period_frame, text="-", font=font_style).pack(side=tk.LEFT)
        self.end_analysis_theo_entry = tk.Entry(analysis_period_frame, font=font_style, width=10, validate="key", validatecommand=(self.validate_positive_float_cmd, "%P"))
        self.end_analysis_theo_entry.pack(side=tk.LEFT)

    def create_experimental_input_frames(self, parent, font_style, category_font_style):
        self.experimental_data_frame = tk.Frame(parent, padx=1, pady=1)
        self.experimental_data_frame.grid(row=0, column=1, padx=15)
        
        data_label_frame = tk.Frame(self.experimental_data_frame)
        data_label_frame.pack()
        tk.Label(data_label_frame, text="Accelerometer Data", font=category_font_style).pack(side=tk.LEFT)
        
        data_asterisk_icon = tk.Label(data_label_frame, image=self.asterisk_icon)
        data_asterisk_icon.pack(side=tk.LEFT, padx=(0, 0))
        ToolTip(data_asterisk_icon, "Required", x_offset=13, y_offset=-3)
        
        self.upload_file_button = tk.Button(self.experimental_data_frame, text="Upload CSV File", command=self.import_data, font=font_style, bg="#aeb0b5", activebackground="#d6d7d9")
        self.upload_file_button.pack()

        self.experimental_analysis_period_frame = tk.Frame(parent, padx=1, pady=1)
        self.experimental_analysis_period_frame.grid(row=0, column=5, padx=15)
        self.experimental_analysis_period_frame.grid_remove()
        tk.Label(self.experimental_analysis_period_frame, text="Time Period of Analysis (h)", font=category_font_style).pack()
        analysis_period_frame_exp = tk.Frame(self.experimental_analysis_period_frame)
        analysis_period_frame_exp.pack()
        self.start_analysis_exp_entry = tk.Entry(analysis_period_frame_exp, font=font_style, width=10, validate="key", validatecommand=(self.validate_positive_float_cmd, "%P"))
        self.start_analysis_exp_entry.pack(side=tk.LEFT)
        tk.Label(analysis_period_frame_exp, text="-", font=font_style).pack(side=tk.LEFT)
        self.end_analysis_exp_entry = tk.Entry(analysis_period_frame_exp, font=font_style, width=10, validate="key", validatecommand=(self.validate_positive_float_cmd, "%P"))
        self.end_analysis_exp_entry.pack(side=tk.LEFT)

    def create_start_button(self, parent, font_style):
        self.start_button = tk.Button(parent, text="Start", command=self.start_simulation, font=font_style, bg="#0066b2", fg="#ffffff", activebackground="#3380cc", activeforeground="#ffffff")
        self.start_button.grid(row=1, column=0, columnspan=6, pady=(10, 5))

    def setup_plot_frames(self):
        plot_frame = tk.Frame(self.master, padx=5, pady=5, bg="#f1f1f1")
        plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=(5, 5), pady=(0, 5))

        self.notebook = ttk.Notebook(plot_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        rcParams['font.family'] = 'Calibri'
        rcParams['font.size'] = 9

        self.setup_theoretical_plot_frames()
        self.setup_experimental_plot_frames()
        self.clear_theoretical_plots()

    def setup_theoretical_plot_frames(self):
        self.theoretical_g_acceleration_frame = tk.Frame(self.notebook, borderwidth=0, relief=tk.SOLID)
        self.theoretical_non_g_acceleration_frame = tk.Frame(self.notebook, borderwidth=0, relief=tk.SOLID)
        self.theoretical_acceleration_distribution_frame = tk.Frame(self.notebook, borderwidth=0, relief=tk.SOLID)

        self.notebook.add(self.theoretical_g_acceleration_frame, text="Gravitational Acceleration")
        self.notebook.add(self.theoretical_non_g_acceleration_frame, text="Non-Gravitational Acceleration")
        self.notebook.add(self.theoretical_acceleration_distribution_frame, text="Acceleration Distribution")

        self.theoretical_g_acceleration_frame_left = tk.Frame(self.theoretical_g_acceleration_frame, borderwidth=1, relief=tk.SOLID)
        self.theoretical_g_acceleration_frame_left.grid(row=0, column=0, sticky="nsew")
        self.theoretical_g_acceleration_toolbar_frame_left = tk.Frame(self.theoretical_g_acceleration_frame_left, borderwidth=0, relief=tk.SOLID)
        self.theoretical_g_acceleration_toolbar_frame_left.pack(side=tk.BOTTOM, fill=tk.X)

        self.theoretical_g_acceleration_frame_right = tk.Frame(self.theoretical_g_acceleration_frame, borderwidth=1, relief=tk.SOLID)
        self.theoretical_g_acceleration_frame_right.grid(row=0, column=1, sticky="nsew")
        self.theoretical_g_acceleration_toolbar_frame_right = tk.Frame(self.theoretical_g_acceleration_frame_right, borderwidth=0, relief=tk.SOLID)
        self.theoretical_g_acceleration_toolbar_frame_right.pack(side=tk.BOTTOM, fill=tk.X)

        self.theoretical_g_acceleration_frame.grid_columnconfigure(0, weight=1)
        self.theoretical_g_acceleration_frame.grid_columnconfigure(1, weight=1)
        self.theoretical_g_acceleration_frame.grid_rowconfigure(0, weight=1)

        self.theoretical_g_acceleration_figure = plt.Figure()
        self.theoretical_g_acceleration_ax = self.theoretical_g_acceleration_figure.add_subplot(1, 1, 1)
        self.theoretical_g_acceleration_ax.set_title("Time-Averaged Gravitational Acceleration")
        self.theoretical_g_acceleration_ax.set_xlabel('Time (h)')
        self.theoretical_g_acceleration_ax.set_ylabel('Acceleration (g)')
        self.theoretical_g_acceleration_canvas = FigureCanvasTkAgg(self.theoretical_g_acceleration_figure, self.theoretical_g_acceleration_frame_left)
        self.theoretical_g_acceleration_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.theoretical_g_components_figure = plt.Figure()
        self.theoretical_g_components_ax = self.theoretical_g_components_figure.add_subplot(1, 1, 1)
        self.theoretical_g_components_ax.set_title("Time-Averaged Gravitational Acceleration")
        self.theoretical_g_components_ax.set_xlabel('Time (h)')
        self.theoretical_g_components_ax.set_ylabel('Acceleration (g)')
        self.theoretical_g_components_canvas = FigureCanvasTkAgg(self.theoretical_g_components_figure, self.theoretical_g_acceleration_frame_right)
        self.theoretical_g_components_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.theoretical_g_acceleration_toolbar = CustomToolbar(self.theoretical_g_acceleration_canvas, self.theoretical_g_acceleration_toolbar_frame_left, self.export_theoretical_g_magnitude_data)
        self.theoretical_g_acceleration_toolbar.update()
        self.theoretical_g_components_toolbar = CustomToolbar(self.theoretical_g_components_canvas, self.theoretical_g_acceleration_toolbar_frame_right, export_components_callback=self.export_theoretical_g_components_data)
        self.theoretical_g_components_toolbar.update()

        self.theoretical_non_g_acceleration_frame_left = tk.Frame(self.theoretical_non_g_acceleration_frame, borderwidth=1, relief=tk.SOLID)
        self.theoretical_non_g_acceleration_frame_left.grid(row=0, column=0, sticky="nsew")
        self.theoretical_non_g_acceleration_toolbar_frame_left = tk.Frame(self.theoretical_non_g_acceleration_frame_left, borderwidth=0, relief=tk.SOLID)
        self.theoretical_non_g_acceleration_toolbar_frame_left.pack(side=tk.BOTTOM, fill=tk.X)

        self.theoretical_non_g_acceleration_frame_right = tk.Frame(self.theoretical_non_g_acceleration_frame, borderwidth=1, relief=tk.SOLID)
        self.theoretical_non_g_acceleration_frame_right.grid(row=0, column=1, sticky="nsew")
        self.theoretical_non_g_acceleration_toolbar_frame_right = tk.Frame(self.theoretical_non_g_acceleration_frame_right, borderwidth=0, relief=tk.SOLID)
        self.theoretical_non_g_acceleration_toolbar_frame_right.pack(side=tk.BOTTOM, fill=tk.X)

        self.theoretical_non_g_acceleration_frame.grid_columnconfigure(0, weight=1)
        self.theoretical_non_g_acceleration_frame.grid_columnconfigure(1, weight=1)
        self.theoretical_non_g_acceleration_frame.grid_rowconfigure(0, weight=1)

        self.theoretical_non_g_acceleration_figure = plt.Figure()
        self.theoretical_non_g_acceleration_ax = self.theoretical_non_g_acceleration_figure.add_subplot(1, 1, 1)
        self.theoretical_non_g_acceleration_ax.set_title("Time-Averaged Non-Gravitational Acceleration")
        self.theoretical_non_g_acceleration_ax.set_xlabel('Time (h)')
        self.theoretical_non_g_acceleration_ax.set_ylabel('Acceleration (g)')
        self.theoretical_non_g_acceleration_canvas = FigureCanvasTkAgg(self.theoretical_non_g_acceleration_figure, self.theoretical_non_g_acceleration_frame_left)
        self.theoretical_non_g_acceleration_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.theoretical_non_g_components_figure = plt.Figure()
        self.theoretical_non_g_components_ax = self.theoretical_non_g_components_figure.add_subplot(1, 1, 1)
        self.theoretical_non_g_components_ax.set_title("Time-Averaged Non-Gravitational Acceleration")
        self.theoretical_non_g_components_ax.set_xlabel('Time (h)')
        self.theoretical_non_g_components_ax.set_ylabel('Acceleration (g)')
        self.theoretical_non_g_components_canvas = FigureCanvasTkAgg(self.theoretical_non_g_components_figure, self.theoretical_non_g_acceleration_frame_right)
        self.theoretical_non_g_components_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.theoretical_non_g_acceleration_toolbar = CustomToolbar(self.theoretical_non_g_acceleration_canvas, self.theoretical_non_g_acceleration_toolbar_frame_left, self.export_theoretical_non_g_magnitude_data)
        self.theoretical_non_g_acceleration_toolbar.update()
        self.theoretical_non_g_components_toolbar = CustomToolbar(self.theoretical_non_g_components_canvas, self.theoretical_non_g_acceleration_toolbar_frame_right, export_components_callback=self.export_theoretical_non_g_components_data)
        self.theoretical_non_g_components_toolbar.update()

        self.theoretical_acceleration_distribution_frame_left = tk.Frame(self.theoretical_acceleration_distribution_frame, borderwidth=1, relief=tk.SOLID)
        self.theoretical_acceleration_distribution_frame_left.grid(row=0, column=0, sticky="nsew")
        self.theoretical_acceleration_distribution_toolbar_frame_left = tk.Frame(self.theoretical_acceleration_distribution_frame_left, borderwidth=0, relief=tk.SOLID)
        self.theoretical_acceleration_distribution_toolbar_frame_left.pack(side=tk.BOTTOM, fill=tk.X)

        self.theoretical_acceleration_distribution_frame_right = tk.Frame(self.theoretical_acceleration_distribution_frame, borderwidth=1, relief=tk.SOLID)
        self.theoretical_acceleration_distribution_frame_right.grid(row=0, column=1, sticky="nsew")
        self.theoretical_acceleration_distribution_toolbar_frame_right = tk.Frame(self.theoretical_acceleration_distribution_frame_right, borderwidth=0, relief=tk.SOLID)
        self.theoretical_acceleration_distribution_toolbar_frame_right.pack(side=tk.BOTTOM, fill=tk.X)

        self.theoretical_acceleration_distribution_frame.grid_columnconfigure(0, weight=1)
        self.theoretical_acceleration_distribution_frame.grid_columnconfigure(1, weight=1)
        self.theoretical_acceleration_distribution_frame.grid_rowconfigure(0, weight=1)

        self.theoretical_acceleration_distribution_figure = plt.Figure()
        self.theoretical_acceleration_distribution_ax = self.theoretical_acceleration_distribution_figure.add_subplot(1, 1, 1, projection='3d')
        self.configure_3d_axes(self.theoretical_acceleration_distribution_ax, "Acceleration Distribution")
        self.theoretical_acceleration_distribution_canvas = FigureCanvasTkAgg(self.theoretical_acceleration_distribution_figure, self.theoretical_acceleration_distribution_frame_left)
        self.theoretical_acceleration_distribution_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.theoretical_acceleration_distribution_analysis_figure = plt.Figure()
        self.theoretical_acceleration_distribution_analysis_ax = self.theoretical_acceleration_distribution_analysis_figure.add_subplot(1, 1, 1, projection='3d')
        self.configure_3d_axes(self.theoretical_acceleration_distribution_analysis_ax, "Acceleration Distribution")
        self.theoretical_acceleration_distribution_analysis_canvas = FigureCanvasTkAgg(self.theoretical_acceleration_distribution_analysis_figure, self.theoretical_acceleration_distribution_frame_right)
        self.theoretical_acceleration_distribution_analysis_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.theoretical_acceleration_distribution_toolbar = CustomToolbar(self.theoretical_acceleration_distribution_canvas, self.theoretical_acceleration_distribution_toolbar_frame_left, export_distribution_callback=self.export_theoretical_distribution_data)
        self.theoretical_acceleration_distribution_toolbar.update()
        self.theoretical_acceleration_distribution_analysis_toolbar = CustomToolbar(self.theoretical_acceleration_distribution_analysis_canvas, self.theoretical_acceleration_distribution_toolbar_frame_right, export_animation_callback=self.export_animation_data)
        self.theoretical_acceleration_distribution_analysis_toolbar.update()

    def setup_experimental_plot_frames(self):
        self.experimental_g_acceleration_frame = tk.Frame(self.notebook, borderwidth=0, relief=tk.SOLID)
        self.experimental_acceleration_distribution_frame = tk.Frame(self.notebook, borderwidth=0, relief=tk.SOLID)

        self.experimental_g_acceleration_frame_left = tk.Frame(self.experimental_g_acceleration_frame, borderwidth=1, relief=tk.SOLID)
        self.experimental_g_acceleration_frame_left.grid(row=0, column=0, sticky="nsew")
        self.experimental_g_acceleration_toolbar_frame_left = tk.Frame(self.experimental_g_acceleration_frame_left, borderwidth=0, relief=tk.SOLID)
        self.experimental_g_acceleration_toolbar_frame_left.pack(side=tk.BOTTOM, fill=tk.X)

        self.experimental_g_acceleration_frame_right = tk.Frame(self.experimental_g_acceleration_frame, borderwidth=1, relief=tk.SOLID)
        self.experimental_g_acceleration_frame_right.grid(row=0, column=1, sticky="nsew")
        self.experimental_g_acceleration_toolbar_frame_right = tk.Frame(self.experimental_g_acceleration_frame_right, borderwidth=0, relief=tk.SOLID)
        self.experimental_g_acceleration_toolbar_frame_right.pack(side=tk.BOTTOM, fill=tk.X)

        self.experimental_g_acceleration_frame.grid_columnconfigure(0, weight=1)
        self.experimental_g_acceleration_frame.grid_columnconfigure(1, weight=1)
        self.experimental_g_acceleration_frame.grid_rowconfigure(0, weight=1)

        self.experimental_g_acceleration_figure_left = plt.Figure()
        self.experimental_g_acceleration_ax_left = self.experimental_g_acceleration_figure_left.add_subplot(1, 1, 1)
        self.experimental_g_acceleration_ax_left.set_title("Time-Averaged Gravitational Acceleration")
        self.experimental_g_acceleration_ax_left.set_xlabel('Time (h)')
        self.experimental_g_acceleration_ax_left.set_ylabel('Acceleration (g)')
        self.experimental_g_acceleration_canvas_left = FigureCanvasTkAgg(self.experimental_g_acceleration_figure_left, self.experimental_g_acceleration_frame_left)
        self.experimental_g_acceleration_canvas_left.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.experimental_g_acceleration_figure_right = plt.Figure()
        self.experimental_g_acceleration_ax_right = self.experimental_g_acceleration_figure_right.add_subplot(1, 1, 1)
        self.experimental_g_acceleration_ax_right.set_title("Time-Averaged Gravitational Acceleration")
        self.experimental_g_acceleration_ax_right.set_xlabel('Time (h)')
        self.experimental_g_acceleration_ax_right.set_ylabel('Acceleration (g)')
        self.experimental_g_acceleration_canvas_right = FigureCanvasTkAgg(self.experimental_g_acceleration_figure_right, self.experimental_g_acceleration_frame_right)
        self.experimental_g_acceleration_canvas_right.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.experimental_g_acceleration_toolbar_left = CustomToolbar(self.experimental_g_acceleration_canvas_left, self.experimental_g_acceleration_toolbar_frame_left, self.export_experimental_g_magnitude_data)
        self.experimental_g_acceleration_toolbar_left.update()
        self.experimental_g_acceleration_toolbar_right = CustomToolbar(self.experimental_g_acceleration_canvas_right, self.experimental_g_acceleration_toolbar_frame_right, export_components_callback=self.export_experimental_g_components_data)
        self.experimental_g_acceleration_toolbar_right.update()

        self.experimental_acceleration_distribution_frame_left = tk.Frame(self.experimental_acceleration_distribution_frame, borderwidth=1, relief=tk.SOLID)
        self.experimental_acceleration_distribution_frame_left.grid(row=0, column=0, sticky="nsew")
        self.experimental_acceleration_distribution_toolbar_frame_left = tk.Frame(self.experimental_acceleration_distribution_frame_left, borderwidth=0, relief=tk.SOLID)
        self.experimental_acceleration_distribution_toolbar_frame_left.pack(side=tk.BOTTOM, fill=tk.X)

        self.experimental_acceleration_distribution_frame_right = tk.Frame(self.experimental_acceleration_distribution_frame, borderwidth=1, relief=tk.SOLID)
        self.experimental_acceleration_distribution_frame_right.grid(row=0, column=1, sticky="nsew")
        self.experimental_acceleration_distribution_toolbar_frame_right = tk.Frame(self.experimental_acceleration_distribution_frame_right, borderwidth=0, relief=tk.SOLID)
        self.experimental_acceleration_distribution_toolbar_frame_right.pack(side=tk.BOTTOM, fill=tk.X)

        self.experimental_acceleration_distribution_frame.grid_columnconfigure(0, weight=1)
        self.experimental_acceleration_distribution_frame.grid_columnconfigure(1, weight=1)
        self.experimental_acceleration_distribution_frame.grid_rowconfigure(0, weight=1)

        self.experimental_acceleration_distribution_figure = plt.Figure()
        self.experimental_acceleration_distribution_ax = self.experimental_acceleration_distribution_figure.add_subplot(1, 1, 1, projection='3d')
        self.configure_3d_axes(self.experimental_acceleration_distribution_ax, "Acceleration Distribution")
        self.experimental_acceleration_distribution_canvas = FigureCanvasTkAgg(self.experimental_acceleration_distribution_figure, self.experimental_acceleration_distribution_frame_left)
        self.experimental_acceleration_distribution_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.experimental_acceleration_distribution_analysis_figure = plt.Figure()
        self.experimental_acceleration_distribution_analysis_ax = self.experimental_acceleration_distribution_analysis_figure.add_subplot(1, 1, 1, projection='3d')
        self.configure_3d_axes(self.experimental_acceleration_distribution_analysis_ax, "Acceleration Distribution")
        self.experimental_acceleration_distribution_analysis_canvas = FigureCanvasTkAgg(self.experimental_acceleration_distribution_analysis_figure, self.experimental_acceleration_distribution_frame_right)
        self.experimental_acceleration_distribution_analysis_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.experimental_acceleration_distribution_toolbar = CustomToolbar(self.experimental_acceleration_distribution_canvas, self.experimental_acceleration_distribution_toolbar_frame_left, export_distribution_callback=self.export_experimental_distribution_data)
        self.experimental_acceleration_distribution_toolbar.update()
        self.experimental_acceleration_distribution_analysis_toolbar = CustomToolbar(self.experimental_acceleration_distribution_analysis_canvas, self.experimental_acceleration_distribution_toolbar_frame_right, export_animation_callback=self.export_animation_data)
        self.experimental_acceleration_distribution_analysis_toolbar.update()

    def configure_3d_axes(self, ax, title):
        ax.set_xlabel('X (g)')
        ax.set_ylabel('Y (g)')
        ax.set_zlabel('Z (g)')
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
                "configure": {"padding": [5, 1], "background": "#aeb0b5", "font": ("Calibri", 11), "focuscolor": ""},
                "map": {"background": [("selected", "#d6d7d9")], "expand": [("selected", [1, 1, 1, 0])]}
            }
        })
        style.theme_use("yummy")

    def open_info_link(self):
        if self.current_mode == "Theoretical":
            webbrowser.open("https://rdcu.be/eg58N")

    def switch_mode(self, mode):
        if self.current_mode == mode:
            return
        self.current_mode = mode

        self.mode_menu.master.config(text=mode)
        self.mode_label.config(text="Mode")

        if mode == "Theoretical":
            self.mode_icon.pack(side=tk.LEFT, padx=(1, 0))
            self.show_theoretical_inputs()
        else:
            self.mode_icon.pack_forget()
            self.show_experimental_inputs()

    def show_theoretical_inputs(self):
        self.theoretical_angular_velocity_frame.grid()
        self.theoretical_angular_position_frame.grid()
        self.theoretical_distance_frame.grid()
        self.theoretical_duration_frame.grid()
        self.theoretical_analysis_period_frame.grid()
        self.experimental_data_frame.grid_remove()
        self.experimental_analysis_period_frame.grid_remove()
        self.start_button.grid(row=1, column=0, columnspan=6, pady=(10, 5))

        while self.notebook.index("end") > 0:
            self.notebook.forget(0)

        self.notebook.add(self.theoretical_g_acceleration_frame, text="Gravitational Acceleration")
        self.notebook.add(self.theoretical_non_g_acceleration_frame, text="Non-Gravitational Acceleration")
        self.notebook.add(self.theoretical_acceleration_distribution_frame, text="Acceleration Distribution")
        self.clear_theoretical_plots()

    def show_experimental_inputs(self):
        self.theoretical_angular_velocity_frame.grid_remove()
        self.theoretical_angular_position_frame.grid_remove()
        self.theoretical_distance_frame.grid_remove()
        self.theoretical_duration_frame.grid_remove()
        self.theoretical_analysis_period_frame.grid_remove()
        self.experimental_data_frame.grid(row=0, column=1, padx=15)
        self.experimental_analysis_period_frame.grid(row=0, column=2, padx=15)
        self.start_button.grid(row=1, column=0, columnspan=3, pady=(10, 5))

        while self.notebook.index("end") > 0:
            self.notebook.forget(0)

        self.notebook.add(self.experimental_g_acceleration_frame, text="Gravitational Acceleration")
        self.notebook.add(self.experimental_acceleration_distribution_frame, text="Acceleration Distribution")
        self.clear_experimental_plots()

    def export_theoretical_g_magnitude_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                if not self.theoretical_g_acceleration_ax.lines:
                    raise ValueError("No data available to export.")
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Time (h)", "Acceleration (g)"])
                    for time, mag in zip(self.theoretical_g_acceleration_ax.lines[0].get_xdata(), self.theoretical_g_acceleration_ax.lines[0].get_ydata()):
                        writer.writerow([time, mag])
                messagebox.showinfo("Success", "Data exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_theoretical_g_components_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                if not self.theoretical_g_components_ax.lines:
                    raise ValueError("No data available to export.")
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Time (h)", "X (g)", "Y (g)", "Z (g)"])
                    time_data = self.theoretical_g_components_ax.lines[0].get_xdata()
                    x_data = self.theoretical_g_components_ax.lines[0].get_ydata()
                    y_data = self.theoretical_g_components_ax.lines[1].get_ydata()
                    z_data = self.theoretical_g_components_ax.lines[2].get_ydata()
                    for time, x, y, z in zip(time_data, x_data, y_data, z_data):
                        writer.writerow([time, x, y, z])
                messagebox.showinfo("Success", "Data exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_theoretical_non_g_magnitude_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                if not self.theoretical_non_g_acceleration_ax.lines:
                    raise ValueError("No data available to export.")
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Time (h)", "Acceleration (g)"])
                    for time, mag in zip(self.theoretical_non_g_acceleration_ax.lines[0].get_xdata(), self.theoretical_non_g_acceleration_ax.lines[0].get_ydata()):
                        writer.writerow([time, mag])
                messagebox.showinfo("Success", "Data exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_theoretical_non_g_components_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                if not self.theoretical_non_g_components_ax.lines:
                    raise ValueError("No data available to export.")
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Time (h)", "X (g)", "Y (g)", "Z (g)"])
                    time_data = self.theoretical_non_g_components_ax.lines[0].get_xdata()
                    x_data = self.theoretical_non_g_components_ax.lines[0].get_ydata()
                    y_data = self.theoretical_non_g_components_ax.lines[1].get_ydata()
                    z_data = self.theoretical_non_g_components_ax.lines[2].get_ydata()
                    for time, x, y, z in zip(time_data, x_data, y_data, z_data):
                        writer.writerow([time, x, y, z])
                messagebox.showinfo("Success", "Data exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_theoretical_distribution_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                if not self.theoretical_acceleration_distribution_ax.lines:
                    raise ValueError("No data available to export.")
                line = self.theoretical_acceleration_distribution_ax.lines[0]
                x_data, y_data, z_data = line.get_data_3d()
                time_data = self.theoretical_non_g_acceleration_ax.lines[0].get_xdata()
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Time (h)", "X (g)", "Y (g)", "Z (g)"])
                    for time, x, y, z in zip(time_data, x_data, y_data, z_data):
                        writer.writerow([time, x, y, z])
                messagebox.showinfo("Success", "Data exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_experimental_g_magnitude_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                if not self.experimental_g_acceleration_ax_left.lines:
                    raise ValueError("No data available to export.")
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Time (h)", "Acceleration (g)"])
                    for time, mag in zip(self.experimental_g_acceleration_ax_left.lines[0].get_xdata(), self.experimental_g_acceleration_ax_left.lines[0].get_ydata()):
                        writer.writerow([time, mag])
                messagebox.showinfo("Success", "Data exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_experimental_g_components_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                if not self.experimental_g_acceleration_ax_right.lines:
                    raise ValueError("No data available to export.")
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Time (h)", "X (g)", "Y (g)", "Z (g)"])
                    time_data = self.experimental_g_acceleration_ax_right.lines[0].get_xdata()
                    x_data = self.experimental_g_acceleration_ax_right.lines[0].get_ydata()
                    y_data = self.experimental_g_acceleration_ax_right.lines[1].get_ydata()
                    z_data = self.experimental_g_acceleration_ax_right.lines[2].get_ydata()
                    for time, x, y, z in zip(time_data, x_data, y_data, z_data):
                        writer.writerow([time, x, y, z])
                messagebox.showinfo("Success", "Data exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_experimental_distribution_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                if not self.experimental_acceleration_distribution_ax.lines:
                    raise ValueError("No data available to export.")
                line = self.experimental_acceleration_distribution_ax.lines[0]
                x_data, y_data, z_data = line.get_data_3d()
                time_data = self.experimental_g_acceleration_ax_left.lines[0].get_xdata()
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Time (h)", "X (g)", "Y (g)", "Z (g)"])
                    for time, x, y, z in zip(time_data, x_data, y_data, z_data):
                        writer.writerow([time, x, y, z])
                messagebox.showinfo("Success", "Data exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_animation_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        if file_path:
            try:
                matplotlib.rcParams['animation.ffmpeg_path'] = r"ffmpeg\ffmpeg.exe"
                start_analysis = self.last_start_analysis_theo if self.mode_var.get() == "Theoretical" else self.last_start_analysis_exp
                end_analysis = self.last_end_analysis_theo if self.mode_var.get() == "Theoretical" else self.last_end_analysis_exp

                if self.last_mode == "Theoretical":
                    if not self.theoretical_acceleration_distribution_analysis_ax.lines:
                        raise ValueError("No data available to export.")
                    inner_rpm = self.last_inner_velocity if self.last_inner_velocity is not None else 0.0
                    outer_rpm = self.last_outer_velocity if self.last_outer_velocity is not None else 0.0
                    theta_1_init = self.last_inner_position if self.last_inner_position is not None else 0.0
                    theta_2_init = self.last_outer_position if self.last_outer_position is not None else 0.0
                    delta_m = self.last_distance / 100 if self.last_distance is not None else 0.0
                    duration_hours = self.last_simulation_duration
                    theoretical_model = MathModel(inner_rpm, outer_rpm, delta_m, delta_m, delta_m, duration_hours, theta_1_init, theta_2_init)
                    time_array, g_array, _ = theoretical_model.calculate_acceleration()
                    x_data, y_data, z_data = g_array[0], g_array[1], g_array[2]
                    time_data = time_array / 3600

                elif self.last_mode == "Experimental":
                    if not self.experimental_acceleration_distribution_analysis_ax.lines:
                        raise ValueError("No data available to export.")
                    
                    if isinstance(self.last_experimental_data, tuple): 
                        time_data, x_data, y_data, z_data = self.last_experimental_data
                    else: 
                        datetime_str = []
                        x_data, y_data, z_data = [], [], []
                        for k in range(0, len(self.last_experimental_data) - 4, 5):
                            try:
                                dt = parser.parse(self.last_experimental_data[k] + " " + self.last_experimental_data[k + 1])
                            except ValueError:
                                dt = parser.parse(self.last_experimental_data[k + 1] + " " + self.last_experimental_data[k])
                            datetime_str.append(dt)
                            x_data.append(float(self.last_experimental_data[k + 2]))
                            y_data.append(float(self.last_experimental_data[k + 3]))
                            z_data.append(float(self.last_experimental_data[k + 4]))
                        time_data = [(dt - datetime_str[0]).total_seconds() / 3600 for dt in datetime_str]

                start_index = next(i for i, t in enumerate(time_data) if t >= start_analysis)
                end_index = next(i for i, t in enumerate(time_data) if t >= end_analysis)
                sliced_x = np.array(x_data[start_index:end_index])
                sliced_y = np.array(y_data[start_index:end_index])
                sliced_z = np.array(z_data[start_index:end_index])

                if sliced_x.size == 0 or sliced_y.size == 0 or sliced_z.size == 0:
                    raise ValueError("No data available to export.")

                fig = plt.Figure(figsize=(8, 6), dpi=100)
                ax = fig.add_subplot(111, projection='3d')
                self.configure_3d_axes(ax, "Acceleration Distribution")

                def update(num):
                    ax.clear()
                    self.configure_3d_axes(ax, "Acceleration Distribution")
                    ax.plot(sliced_x[:num], sliced_y[:num], sliced_z[:num], color='#ec1c24', linewidth=1)
                    return ax,

                ani = animation.FuncAnimation(fig, update, frames=len(sliced_x), interval=100, blit=False)
                writer = FFMpegWriter(fps=10, metadata=dict(artist='NASA'), bitrate=1800)
                ani.save(file_path, writer=writer)

                plt.close(fig)
                messagebox.showinfo("Success", "Animation exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def clear_theoretical_plots(self):
        self.theoretical_g_acceleration_ax.clear()
        self.theoretical_g_acceleration_ax.set_title("Time-Averaged Gravitational Acceleration")
        self.theoretical_g_acceleration_ax.set_xlabel('Time (h)')
        self.theoretical_g_acceleration_ax.set_ylabel('Acceleration (g)')
        self.theoretical_g_acceleration_canvas.draw()

        self.theoretical_g_components_ax.clear()
        self.theoretical_g_components_ax.set_title("Time-Averaged Gravitational Acceleration")
        self.theoretical_g_components_ax.set_xlabel('Time (h)')
        self.theoretical_g_components_ax.set_ylabel('Acceleration (g)')
        self.theoretical_g_components_canvas.draw()

        self.theoretical_non_g_acceleration_ax.clear()
        self.theoretical_non_g_acceleration_ax.set_title("Time-Averaged Non-Gravitational Acceleration")
        self.theoretical_non_g_acceleration_ax.set_xlabel('Time (h)')
        self.theoretical_non_g_acceleration_ax.set_ylabel('Acceleration (g)')
        self.theoretical_non_g_acceleration_canvas.draw()

        self.theoretical_non_g_components_ax.clear()
        self.theoretical_non_g_components_ax.set_title("Time-Averaged Non-Gravitational Acceleration")
        self.theoretical_non_g_components_ax.set_xlabel('Time (h)')
        self.theoretical_non_g_components_ax.set_ylabel('Acceleration (g)')
        self.theoretical_non_g_components_canvas.draw()

        self.theoretical_acceleration_distribution_ax.clear()
        self.configure_3d_axes(self.theoretical_acceleration_distribution_ax, "Acceleration Distribution")
        self.theoretical_acceleration_distribution_canvas.draw()

        self.theoretical_acceleration_distribution_analysis_ax.clear()
        self.configure_3d_axes(self.theoretical_acceleration_distribution_analysis_ax, "Acceleration Distribution")
        self.theoretical_acceleration_distribution_analysis_canvas.draw()

    def clear_experimental_plots(self):
        self.experimental_g_acceleration_ax_left.clear()
        self.experimental_g_acceleration_ax_left.set_title("Time-Averaged Gravitational Acceleration")
        self.experimental_g_acceleration_ax_left.set_xlabel('Time (h)')
        self.experimental_g_acceleration_ax_left.set_ylabel('Acceleration (g)')
        self.experimental_g_acceleration_canvas_left.draw()

        self.experimental_g_acceleration_ax_right.clear()
        self.experimental_g_acceleration_ax_right.set_title("Time-Averaged Gravitational Acceleration")
        self.experimental_g_acceleration_ax_right.set_xlabel('Time (h)')
        self.experimental_g_acceleration_ax_right.set_ylabel('Acceleration (g)')
        self.experimental_g_acceleration_canvas_right.draw()

        self.experimental_acceleration_distribution_ax.clear()
        self.configure_3d_axes(self.experimental_acceleration_distribution_ax, "Acceleration Distribution")
        self.experimental_acceleration_distribution_canvas.draw()

        self.experimental_acceleration_distribution_analysis_ax.clear()
        self.configure_3d_axes(self.experimental_acceleration_distribution_analysis_ax, "Acceleration Distribution")
        self.experimental_acceleration_distribution_analysis_canvas.draw()

    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                try:
                    self.experimental_data = import_sci_spinner_format_data(file_path)
                    messagebox.showinfo("Success", "CSV file uploaded successfully.")
                except ValueError:
                    with open(file_path, 'r') as file:
                        main_array = file.read().replace("   ", " ").replace('\t', ' ').replace('\n', ' ').replace(',', ' ').split(' ')
                    self.experimental_data = main_array
                    messagebox.showinfo("Success", "CSV file uploaded successfully.")
            except FileNotFoundError:
                messagebox.showerror("File Error", f"File not found: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def process_experimental_data(self, main_array, start_analysis, end_analysis, is_sci_spinner_format=False):
        if is_sci_spinner_format:
            time_in_hours, x, y, z = main_array
        else:
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

        if not time_in_hours or not any(x) or not any(y) or not any(z):
            messagebox.showerror(
                "Error",
                "Invalid CSV file format.\n\n"
                "Supported CSV file formats:\n"
                "(1) Date (yyyy-mm-dd), Time (hh:mm:ss), X, Y, Z\n"
                "     Example: 2001-11-21, 1:00:00, 0.5, 0.5, 0.5\n\n"
                "OR\n\n"
                "(2) Time (s), X, Y, Z\n"
                "     Example: 3600, 0.5, 0.5, 0.5"
            )
            return

        if end_analysis is not None:
            if end_analysis > max(time_in_hours):
                raise ValueError("Upper bound for time period of analysis exceeds the final timestamp available in the CSV file.")
        if start_analysis is not None and end_analysis is not None:
            if end_analysis <= start_analysis:
                raise ValueError("Lower bound for time period of analysis must be < the upper bound.")

        path_vis = PathVisualization("experimental", x, y, z)
        distribution_score = path_vis.get_distribution()
        self.update_experimental_plots(x, y, z, time_in_hours, start_analysis, end_analysis, distribution_score)

    def process_experimental_data_submission(self):
        try:
            if not hasattr(self, 'experimental_data') or not self.experimental_data:
                raise ValueError("Upload a CSV file.")

            start_analysis = self.start_analysis_exp_entry.get()
            end_analysis = self.end_analysis_exp_entry.get()
            start_analysis = float(start_analysis) if start_analysis else None
            end_analysis = float(end_analysis) if end_analysis else None

            if isinstance(self.experimental_data, tuple): 
                self.process_experimental_data(self.experimental_data, start_analysis, end_analysis, is_sci_spinner_format=True)
            else:
                self.process_experimental_data(self.experimental_data, start_analysis, end_analysis)

        except ValueError as ve:
            if "Upload a CSV file" in str(ve):
                messagebox.showerror("Error", str(ve))
            elif "Upper bound for time period of analysis" in str(ve):
                messagebox.showerror("Error", str(ve))
            elif "Lower bound for time period of analysis" in str(ve):
                messagebox.showerror("Error", str(ve))
            else:
                messagebox.showerror(
                    "Error",
                    "Invalid CSV file format.\n\n"
                    "Supported CSV file formats:\n"
                    "(1) Date (yyyy-mm-dd), Time (hh:mm:ss), X, Y, Z\n"
                    "     Example: 2001-11-21, 1:00:00, 0.5, 0.5, 0.5\n\n"
                    "OR\n\n"
                    "(2) Time (s), X, Y, Z\n"
                    "     Example: 3600, 0.5, 0.5, 0.5"
                )
        except Exception as e:
            messagebox.showerror("Error", str(e))

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
        ani = animation.FuncAnimation(ax.figure, update, frames=len(x_data), interval=100, blit=False)
        canvas.draw()

    def update_experimental_plots(self, x, y, z, time_in_hours, start_analysis, end_analysis, distribution_score):
        self.experimental_g_acceleration_ax_left.clear()
        self.experimental_g_acceleration_ax_left.set_title("Time-Averaged Gravitational Acceleration")

        x_time_avg = np.cumsum(x) / np.arange(1, len(x) + 1)
        y_time_avg = np.cumsum(y) / np.arange(1, len(y) + 1)
        z_time_avg = np.cumsum(z) / np.arange(1, len(z) + 1)
        magnitude = np.sqrt(x_time_avg**2 + y_time_avg**2 + z_time_avg**2)
        avg_mag_full = np.mean(magnitude)

        self.experimental_g_acceleration_ax_left.plot(time_in_hours, magnitude, color='#0066B2', label=f"Magnitude: {avg_mag_full:.3g}")
        
        if start_analysis is not None and end_analysis is not None:
            start_seg = next(i for i, t in enumerate(time_in_hours) if t >= start_analysis)
            end_seg = next(i for i, t in enumerate(time_in_hours) if t >= end_analysis)
            self.experimental_g_acceleration_ax_left.axvline(x=start_analysis, color='#EC1C24', linestyle='--')
            self.experimental_g_acceleration_ax_left.axvline(x=end_analysis, color='#EC1C24', linestyle='--')
            avg_mag_analysis = np.mean(magnitude[start_seg:end_seg])
            self.experimental_g_acceleration_ax_left.plot(time_in_hours[start_seg:end_seg], magnitude[start_seg:end_seg], color='#EC1C24', label=f"Magnitude: {avg_mag_analysis:.3g}")

        self.experimental_g_acceleration_ax_left.legend()
        self.experimental_g_acceleration_ax_left.set_xlabel('Time (h)')
        self.experimental_g_acceleration_ax_left.set_ylabel('Acceleration (g)')
        self.experimental_g_acceleration_canvas_left.draw()

        self.experimental_g_acceleration_ax_right.clear()
        self.experimental_g_acceleration_ax_right.set_title('Time-Averaged Gravitational Acceleration')
        self.experimental_g_acceleration_ax_right.plot(time_in_hours, x_time_avg, label='X', color='#6EAE39')
        self.experimental_g_acceleration_ax_right.plot(time_in_hours, y_time_avg, label='Y', color='#EF7A35')
        self.experimental_g_acceleration_ax_right.plot(time_in_hours, z_time_avg, label='Z', color='mediumorchid')
        self.experimental_g_acceleration_ax_right.set_xlabel('Time (h)')
        self.experimental_g_acceleration_ax_right.set_ylabel('Acceleration (g)')
        self.experimental_g_acceleration_ax_right.legend()
        self.experimental_g_acceleration_canvas_right.draw()

        self.experimental_acceleration_distribution_ax.clear()
        self.experimental_acceleration_distribution_ax.plot(x, y, z, color='#0066b2', linewidth=1)
        self.configure_3d_axes(self.experimental_acceleration_distribution_ax, "Acceleration Distribution")
        self.experimental_acceleration_distribution_ax.legend([f"Distribution: {distribution_score}"])
        self.experimental_acceleration_distribution_canvas.draw()

        self.experimental_acceleration_distribution_analysis_ax.clear()
        if start_analysis is not None and end_analysis is not None:
            start_seg = next(i for i, t in enumerate(time_in_hours) if t >= start_analysis)
            end_seg = next(i for i, t in enumerate(time_in_hours) if t >= end_analysis)
            sliced_x, sliced_y, sliced_z = x[start_seg:end_seg], y[start_seg:end_seg], z[start_seg:end_seg]
            path_vis_analysis = PathVisualization("experimental", sliced_x, sliced_y, sliced_z)
            distribution_score_analysis = path_vis_analysis.get_distribution()
            self.animate_distribution(
                self.experimental_acceleration_distribution_analysis_ax,
                self.experimental_acceleration_distribution_analysis_canvas,
                sliced_x, sliced_y, sliced_z,
                color='#ec1c24',
                label=f"Distribution: {distribution_score_analysis}"
            )
        else:
            self.configure_3d_axes(self.experimental_acceleration_distribution_analysis_ax, "Acceleration Distribution")
            self.experimental_acceleration_distribution_analysis_canvas.draw()

    def start_simulation(self):
        try:
            if self.mode_var.get() == "Theoretical":
                self.process_theoretical_data()
            elif self.mode_var.get() == "Experimental":
                self.process_experimental_data_submission()

            self.last_start_analysis_theo = float(self.start_analysis_theo_entry.get()) if self.start_analysis_theo_entry.get() else None
            self.last_end_analysis_theo = float(self.end_analysis_theo_entry.get()) if self.end_analysis_theo_entry.get() else None
            self.last_start_analysis_exp = float(self.start_analysis_exp_entry.get()) if self.start_analysis_exp_entry.get() else None
            self.last_end_analysis_exp = float(self.end_analysis_exp_entry.get()) if self.end_analysis_exp_entry.get() else None
            self.last_mode = self.mode_var.get()
            self.last_inner_velocity = float(self.inner_velocity_entry.get()) if self.inner_velocity_entry.get() else None
            self.last_outer_velocity = float(self.outer_velocity_entry.get()) if self.outer_velocity_entry.get() else None
            self.last_inner_position = float(self.inner_position_entry.get()) if self.inner_position_entry.get() else None
            self.last_outer_position = float(self.outer_position_entry.get()) if self.outer_position_entry.get() else None
            self.last_simulation_duration = float(self.simulation_duration_entry.get()) if self.simulation_duration_entry.get() else None
            self.last_distance = float(self.distance_entry.get()) if self.distance_entry.get() else None
            self.last_experimental_data = getattr(self, 'experimental_data', None)

        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def process_theoretical_data(self):
        start_analysis = self.start_analysis_theo_entry.get()
        end_analysis = self.end_analysis_theo_entry.get()
        start_analysis = float(start_analysis) if start_analysis else None
        end_analysis = float(end_analysis) if end_analysis else None

        if not self.simulation_duration_entry.get() or not any([self.inner_velocity_entry.get(), self.outer_velocity_entry.get()]):
            raise ValueError("Set angular velocities and simulation duration.")
        
        if start_analysis is not None and end_analysis is not None:
            if end_analysis <= start_analysis:
                raise ValueError("Lower bound for time period of analysis must be < the upper bound.")
            
            simulation_duration = float(self.simulation_duration_entry.get())
            if end_analysis > simulation_duration:
                raise ValueError("Upper bound for time period of analysis must be ≤ the simulation duration.")

        duration_hours = float(self.simulation_duration_entry.get())
        delta_cm = float(self.distance_entry.get()) if self.distance_entry.get() else 0.0  
        inner_rpm = float(self.inner_velocity_entry.get()) if self.inner_velocity_entry.get() else 0.0
        outer_rpm = float(self.outer_velocity_entry.get()) if self.outer_velocity_entry.get() else 0.0
        theta_1_init = float(self.inner_position_entry.get()) if self.inner_position_entry.get() else 0.0
        theta_2_init = float(self.outer_position_entry.get()) if self.outer_position_entry.get() else 0.0
        delta_m = delta_cm / 100
        delta_x, delta_y, delta_z = delta_m, delta_m, delta_m

        theoretical_model = MathModel(inner_rpm, outer_rpm, delta_x, delta_y, delta_z, duration_hours, theta_1_init, theta_2_init)
        time_array, g_array, a_array = theoretical_model.calculate_acceleration()

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

        self.update_theoretical_g_acceleration_plot(time_array, g_magnitude, avg_g_magnitude)
        self.update_theoretical_g_components_plot(time_array, g_x_avg, g_y_avg, g_z_avg)
        self.update_theoretical_non_g_acceleration_plot(time_array, a_magnitude, avg_a_magnitude)
        self.update_theoretical_non_g_components_plot(time_array, a_x_avg, a_y_avg, a_z_avg)
        self.update_theoretical_acceleration_distribution_plot(g_array, time_array)

    def update_theoretical_g_acceleration_plot(self, time_array, g_magnitude, avg_g_magnitude):
        time_in_hours = time_array / 3600
        self.theoretical_g_acceleration_ax.clear()
        self.theoretical_g_acceleration_ax.set_title("Time-Averaged Gravitational Acceleration")
        self.theoretical_g_acceleration_ax.plot(time_in_hours, g_magnitude, color='#0066b2', label=f"Magnitude: {avg_g_magnitude:.3g}")

        start_analysis = self.start_analysis_theo_entry.get()
        end_analysis = self.end_analysis_theo_entry.get()
        start_analysis = float(start_analysis) if start_analysis else None
        end_analysis = float(end_analysis) if end_analysis else None

        if start_analysis is not None and end_analysis is not None:
            self.theoretical_g_acceleration_ax.axvline(x=start_analysis, color='#EC1C24', linestyle='--')
            self.theoretical_g_acceleration_ax.axvline(x=end_analysis, color='#EC1C24', linestyle='--')
            start_index = next(i for i, t in enumerate(time_in_hours) if t >= start_analysis)
            end_index = next(i for i, t in enumerate(time_in_hours) if t >= end_analysis)
            avg_g_magnitude_analysis = np.mean(g_magnitude[start_index:end_index])
            self.theoretical_g_acceleration_ax.plot(time_in_hours[start_index:end_index], g_magnitude[start_index:end_index], color='#EC1C24', label=f"Magnitude: {avg_g_magnitude_analysis:.3g}")

        self.theoretical_g_acceleration_ax.legend()
        self.theoretical_g_acceleration_ax.set_xlabel('Time (h)')
        self.theoretical_g_acceleration_ax.set_ylabel('Acceleration (g)')
        self.theoretical_g_acceleration_canvas.draw()

    def update_theoretical_g_components_plot(self, time_array, g_x_avg, g_y_avg, g_z_avg):
        time_in_hours = time_array / 3600
        self.theoretical_g_components_ax.clear()
        self.theoretical_g_components_ax.set_title("Time-Averaged Gravitational Acceleration")
        self.theoretical_g_components_ax.plot(time_in_hours, g_x_avg, label='X', color='#6EAE39')
        self.theoretical_g_components_ax.plot(time_in_hours, g_y_avg, label='Y', color='#EF7A35')
        self.theoretical_g_components_ax.plot(time_in_hours, g_z_avg, label='Z', color='mediumorchid')
        self.theoretical_g_components_ax.legend()
        self.theoretical_g_components_ax.set_xlabel('Time (h)')
        self.theoretical_g_components_ax.set_ylabel('Acceleration (g)')
        self.theoretical_g_components_canvas.draw()

    def update_theoretical_non_g_acceleration_plot(self, time_array, a_magnitude, avg_a_magnitude):
        time_in_hours = time_array / 3600
        self.theoretical_non_g_acceleration_ax.clear()
        self.theoretical_non_g_acceleration_ax.set_title("Time-Averaged Non-Gravitational Acceleration")
        self.theoretical_non_g_acceleration_ax.plot(time_in_hours, a_magnitude, color='#0066b2', label=f"Magnitude: {avg_a_magnitude:.3g}")

        start_analysis = self.start_analysis_theo_entry.get()
        end_analysis = self.end_analysis_theo_entry.get()
        start_analysis = float(start_analysis) if start_analysis else None
        end_analysis = float(end_analysis) if end_analysis else None

        if start_analysis is not None and end_analysis is not None:
            self.theoretical_non_g_acceleration_ax.axvline(x=start_analysis, color='#EC1C24', linestyle='--')
            self.theoretical_non_g_acceleration_ax.axvline(x=end_analysis, color='#EC1C24', linestyle='--')
            start_index = next(i for i, t in enumerate(time_in_hours) if t >= start_analysis)
            end_index = next(i for i, t in enumerate(time_in_hours) if t >= end_analysis)
            avg_a_magnitude_analysis = np.mean(a_magnitude[start_index:end_index])
            self.theoretical_non_g_acceleration_ax.plot(time_in_hours[start_index:end_index], a_magnitude[start_index:end_index], color='#EC1C24', label=f"Magnitude: {avg_a_magnitude_analysis:.3g}")

        self.theoretical_non_g_acceleration_ax.legend()
        self.theoretical_non_g_acceleration_ax.set_xlabel('Time (h)')
        self.theoretical_non_g_acceleration_ax.set_ylabel('Acceleration (g)')
        formatter = ScalarFormatter(useMathText=True)
        formatter.set_scientific(True)
        self.theoretical_non_g_acceleration_ax.yaxis.set_major_formatter(formatter)
        self.theoretical_non_g_acceleration_ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        self.theoretical_non_g_acceleration_canvas.draw()

    def update_theoretical_non_g_components_plot(self, time_array, a_x_avg, a_y_avg, a_z_avg):
        time_in_hours = time_array / 3600
        self.theoretical_non_g_components_ax.clear()
        self.theoretical_non_g_components_ax.set_title("Time-Averaged Non-Gravitational Acceleration")
        self.theoretical_non_g_components_ax.plot(time_in_hours, a_x_avg, label='X', color='#6EAE39')
        self.theoretical_non_g_components_ax.plot(time_in_hours, a_y_avg, label='Y', color='#EF7A35')
        self.theoretical_non_g_components_ax.plot(time_in_hours, a_z_avg, label='Z', color='mediumorchid')
        self.theoretical_non_g_components_ax.legend()
        self.theoretical_non_g_components_ax.set_xlabel('Time (h)')
        self.theoretical_non_g_components_ax.set_ylabel('Acceleration (g)')
        formatter = ScalarFormatter(useMathText=True)
        formatter.set_scientific(True)
        self.theoretical_non_g_components_ax.yaxis.set_major_formatter(formatter)
        self.theoretical_non_g_components_ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        self.theoretical_non_g_components_canvas.draw()

    def update_theoretical_acceleration_distribution_plot(self, g_array, time_array):
        self.theoretical_acceleration_distribution_ax.clear()
        self.theoretical_acceleration_distribution_ax.plot(g_array[0], g_array[1], g_array[2], color='#0066b2', linewidth=1)
        self.configure_3d_axes(self.theoretical_acceleration_distribution_ax, "Acceleration Distribution")
        distribution_score = PathVisualization("theoretical", g_array[0], g_array[1], g_array[2]).get_distribution()
        self.theoretical_acceleration_distribution_ax.legend([f"Distribution: {distribution_score}"])
        self.theoretical_acceleration_distribution_canvas.draw()

        self.theoretical_acceleration_distribution_analysis_ax.clear()
        start_analysis = self.start_analysis_theo_entry.get()
        end_analysis = self.end_analysis_theo_entry.get()
        start_analysis = float(start_analysis) if start_analysis else None
        end_analysis = float(end_analysis) if end_analysis else None

        if start_analysis is not None and end_analysis is not None:
            time_in_hours = time_array / 3600
            start_index = next(i for i, t in enumerate(time_in_hours) if t >= start_analysis)
            end_index = next(i for i, t in enumerate(time_in_hours) if t >= end_analysis)
            sliced_x, sliced_y, sliced_z = g_array[0][start_index:end_index], g_array[1][start_index:end_index], g_array[2][start_index:end_index]
            path_vis_analysis = PathVisualization("theoretical", sliced_x, sliced_y, sliced_z)
            distribution_score_analysis = path_vis_analysis.get_distribution()
            self.animate_distribution(
                self.theoretical_acceleration_distribution_analysis_ax,
                self.theoretical_acceleration_distribution_analysis_canvas,
                sliced_x, sliced_y, sliced_z,
                color='#ec1c24',
                label=f"Distribution: {distribution_score_analysis}"
            )
        else:
            self.configure_3d_axes(self.theoretical_acceleration_distribution_analysis_ax, "Acceleration Distribution")
            self.theoretical_acceleration_distribution_analysis_canvas.draw()

    def open_url(self, url):
        webbrowser.open_new(url)

def import_sci_spinner_format_data(file_path):
    try:
        time_in_seconds = []
        x = []
        y = []
        z = []

        with open(file_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                time_in_seconds.append(float(row['timestamp']))
                x.append(float(row['x_acc']))
                y.append(float(row['y_acc']))
                z.append(float(row['z_acc']))

        time_in_hours = [t / 3600 for t in time_in_seconds]

        def normalize_vectors(x, y, z):
            g_const = 9.80665
            normalized_x = np.array(x) / g_const
            normalized_y = np.array(y) / g_const
            normalized_z = np.array(z) / g_const
            return normalized_x, normalized_y, normalized_z

        x, y, z = normalize_vectors(x, y, z)
        return time_in_hours, x, y, z

    except KeyError:
        raise ValueError(
            "Error",
            "Invalid CSV file format.\n\n"
            "Supported CSV file formats:\n"
            "(1) Date (yyyy-mm-dd), Time (hh:mm:ss), X, Y, Z\n"
            "     Example: 2001-11-21, 1:00:00, 0.5, 0.5, 0.5\n\n"
            "OR\n\n"
            "(2) Time (s), X, Y, Z\n"
            "     Example: 3600, 0.5, 0.5, 0.5"
        )

if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()