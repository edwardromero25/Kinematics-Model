# Author: Edward Romero, OSTEM Intern, Spring 2025, NASA Kennedy Space Center
# This is a computer model that evaluates the efficacy of a 3D clinostat's microgravity simulation.

import tkinter as tk
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from dataCompile import DataProcessor
from dataCompile import PathVisualization
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np
from datetime import datetime
from PIL import Image, ImageTk
import webbrowser
import tkinter.ttk as ttk
import os

script_dir = os.path.abspath(os.path.dirname(__file__))

class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Computer Model for Microgravity Simulators - NASA")

        self.create_custom_theme()

        nasa_image_path = os.path.join(script_dir, 'images', 'NASA_logo.png')
        nasa_image = Image.open(nasa_image_path)
        nasa_image = nasa_image.resize((70, 58), Image.LANCZOS)
        self.nasa_logo = ImageTk.PhotoImage(nasa_image)

        mssf_image_path = os.path.join(script_dir, 'images', 'MSSF_logo.png')
        mssf_image = Image.open(mssf_image_path)
        mssf_image = mssf_image.resize((65, 58), Image.LANCZOS)
        self.mssf_logo = ImageTk.PhotoImage(mssf_image)

        favicon_path = os.path.join(script_dir, 'images', 'favicon.ico')
        self.favicon = ImageTk.PhotoImage(file=favicon_path)
        master.iconphoto(False, self.favicon)

        font_style = ("Calibri", 12)
        title_font_style = ("Calibri", 20, "bold")
        category_font_style = ("Calibri", 14, "bold")

        input_frame = tk.Frame(master, padx=1, pady=1)
        input_frame.pack(side=tk.TOP, anchor=tk.CENTER)

        title_frame = tk.Frame(input_frame)
        title_frame.pack(pady=(10, 0))

        nasa_label = tk.Label(title_frame, image=self.nasa_logo)
        nasa_label.pack(side=tk.LEFT, padx=1)
        nasa_label.bind("<Button-1>", lambda e: self.open_url("https://www.nasa.gov/"))

        title_label = tk.Label(title_frame, text="Computer Model", font=title_font_style)
        title_label.pack(side=tk.LEFT, padx=1)

        mssf_label = tk.Label(title_frame, image=self.mssf_logo)
        mssf_label.pack(side=tk.LEFT, padx=1)
        mssf_label.bind("<Button-1>", lambda e: self.open_url("https://public.ksc.nasa.gov/partnerships/capabilities-and-testing/testing-and-labs/microgravity-simulation-support-facility/"))

        center_frame = tk.Frame(input_frame)
        center_frame.pack()

        mode_frame = tk.Frame(center_frame, padx=1, pady=1)
        mode_frame.grid(row=0, column=0, padx=30)

        mode_label = tk.Label(mode_frame, text="Mode", font=category_font_style)
        mode_label.pack()

        self.mode_var = tk.StringVar(value="Theoretical")
        self.mode_menu = tk.OptionMenu(mode_frame, self.mode_var, "Theoretical", "Experimental", command=self.switch_mode)
        self.mode_menu.config(font=font_style, bg="lightgray")
        self.mode_menu.pack()

        self.operating_frame = tk.Frame(center_frame, padx=1, pady=1)
        self.operating_frame.grid(row=0, column=1, padx=30)

        operating_label = tk.Label(self.operating_frame, text="Frame Velocities (rpm)", font=category_font_style)
        operating_label.pack()

        operating_input_frame = tk.Frame(self.operating_frame)
        operating_input_frame.pack()

        self.innerV_label = tk.Label(operating_input_frame, text="Inner:", font=font_style)
        self.innerV_label.pack(side=tk.LEFT)
        self.innerV_entry = tk.Entry(operating_input_frame, font=font_style, width=10)
        self.innerV_entry.pack(side=tk.LEFT)

        self.outerV_label = tk.Label(operating_input_frame, text="Outer:", font=font_style)
        self.outerV_label.pack(side=tk.LEFT, padx=(10, 0))
        self.outerV_entry = tk.Entry(operating_input_frame, font=font_style, width=10)
        self.outerV_entry.pack(side=tk.LEFT)

        self.duration_frame = tk.Frame(center_frame, padx=1, pady=1)
        self.duration_frame.grid(row=0, column=2, padx=30) 

        duration_label = tk.Label(self.duration_frame, text="Simulation Duration (hours)", font=category_font_style)
        duration_label.pack()

        self.maxSeg_entry = tk.Entry(self.duration_frame, font=font_style)
        self.maxSeg_entry.pack()

        self.analysis_frame = tk.Frame(center_frame, padx=1, pady=1)
        self.analysis_frame.grid(row=0, column=3, padx=30) 

        analysis_label = tk.Label(self.analysis_frame, text="Time Period of Analysis (hours)", font=category_font_style)
        analysis_label.pack()

        analysis_period_frame = tk.Frame(self.analysis_frame)
        analysis_period_frame.pack()

        self.startAnalysis_entry = tk.Entry(analysis_period_frame, font=font_style, width=10)
        self.startAnalysis_entry.pack(side=tk.LEFT)
        hyphen_label = tk.Label(analysis_period_frame, text="-", font=font_style)
        hyphen_label.pack(side=tk.LEFT)
        self.endAnalysis_entry = tk.Entry(analysis_period_frame, font=font_style, width=10)
        self.endAnalysis_entry.pack(side=tk.LEFT)

        self.analysis_frame_exp = tk.Frame(center_frame, padx=1, pady=1)
        self.analysis_frame_exp.grid(row=0, column=4, padx=30) 
        self.analysis_frame_exp.grid_remove() 

        analysis_label_exp = tk.Label(self.analysis_frame_exp, text="Time Period of Analysis (hours)", font=category_font_style)
        analysis_label_exp.pack()

        analysis_period_frame_exp = tk.Frame(self.analysis_frame_exp)
        analysis_period_frame_exp.pack()

        self.startAnalysis_entry_exp = tk.Entry(analysis_period_frame_exp, font=font_style, width=10)
        self.startAnalysis_entry_exp.pack(side=tk.LEFT)
        hyphen_label_exp = tk.Label(analysis_period_frame_exp, text="-", font=font_style)
        hyphen_label_exp.pack(side=tk.LEFT)
        self.endAnalysis_entry_exp = tk.Entry(analysis_period_frame_exp, font=font_style, width=10)
        self.endAnalysis_entry_exp.pack(side=tk.LEFT)

        self.submit_button = tk.Button(center_frame, text="Start", command=self.submit, font=font_style, bg="#E4002B", fg="white")
        self.submit_button.grid(row=1, column=0, columnspan=4, pady=(10, 5))

        self.accelerometer_frame = tk.Frame(center_frame, padx=1, pady=1)
        accelerometer_label = tk.Label(self.accelerometer_frame, text="Accelerometer Data", font=category_font_style)
        accelerometer_label.pack()

        self.import_button = tk.Button(self.accelerometer_frame, text="Upload CSV", command=self.import_data, font=font_style, bg="lightgray")
        self.import_button.pack()

        plot_frame = tk.Frame(master, padx=5, pady=5)
        plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=(5, 5), pady=(0, 5))

        notebook = ttk.Notebook(plot_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.magnitude_frame = tk.Frame(notebook, borderwidth=1, relief=tk.SOLID)
        self.vector_components_frame = tk.Frame(notebook, borderwidth=1, relief=tk.SOLID)
        self.path_frame = tk.Frame(notebook, borderwidth=1, relief=tk.SOLID)

        notebook.add(self.magnitude_frame, text="Resultant Vector")
        notebook.add(self.vector_components_frame, text="Vector Components")
        notebook.add(self.path_frame, text="Vector Path")

        rcParams['font.family'] = 'Calibri'

        self.figure = plt.Figure()
        self.ax = self.figure.add_subplot(1, 1, 1)
        self.ax.set_yscale('log')
        self.ax.set_title("Time-Averaged Resultant Acceleration Vector")
        self.ax.set_xlabel('Time (hours)')
        self.ax.set_ylabel('Magnitude (g)')
        self.canvas = FigureCanvasTkAgg(self.figure, self.magnitude_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.magnitude_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.path_figure = plt.Figure()
        self.path_ax = self.path_figure.add_subplot(1, 1, 1, projection='3d')
        self.path_ax.set_xlabel('X')
        self.path_ax.set_ylabel('Y')
        self.path_ax.set_zlabel('Z')
        ticks = np.arange(-1.0, 1.5, 0.5)
        self.path_ax.set_xticks(ticks)
        self.path_ax.set_yticks(ticks)
        self.path_ax.set_zticks(ticks)
        self.path_ax.set_title("Acceleration Vector Path")
        self.path_canvas = FigureCanvasTkAgg(self.path_figure, self.path_frame)
        self.path_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.path_toolbar = NavigationToolbar2Tk(self.path_canvas, self.path_frame)
        self.path_toolbar.update()
        self.path_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.components_figure = plt.Figure()
        self.components_ax = self.components_figure.add_subplot(1, 1, 1)
        self.components_ax.set_title("Time-Averaged Acceleration Vector Components")
        self.components_ax.set_xlabel('Time (hours)')
        self.components_ax.set_ylabel('Magnitude (g)')
        self.components_canvas = FigureCanvasTkAgg(self.components_figure, self.vector_components_frame)
        self.components_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.components_toolbar = NavigationToolbar2Tk(self.components_canvas, self.vector_components_frame)
        self.components_toolbar.update()
        self.components_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.clear_plots()

        messagebox.showinfo("Welcome!", "This is a computer model that evaluates the efficacy of a 3D clinostat's microgravity simulation.")

    def create_custom_theme(self):
        style = ttk.Style()
        style.theme_create("yummy", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [2, 0, 2, 0], "background": "SystemButtonFace"}},
            "TNotebook.Tab": {
                "configure": {"padding": [5, 1], "background": "lightgray"},
                "map": {"background": [("selected", "gainsboro")],
                        "expand": [("selected", [1, 1, 1, 0])]}
            }
        })
        style.theme_use("yummy")

    def switch_mode(self, mode):
        if mode == "Theoretical":
            self.show_theoretical_inputs()
        else:
            self.show_experimental_inputs()

    def show_theoretical_inputs(self):
        self.operating_frame.grid()
        self.duration_frame.grid()
        self.analysis_frame.grid()
        self.analysis_frame_exp.grid_remove()
        self.accelerometer_frame.grid_remove()
        self.submit_button.grid(row=1, column=0, columnspan=4, pady=(10, 5))
        self.clear_plots()

    def show_experimental_inputs(self):
        self.operating_frame.grid_remove()
        self.duration_frame.grid_remove()
        self.analysis_frame.grid_remove()
        self.analysis_frame_exp.grid(row=0, column=2, padx=30)
        self.accelerometer_frame.grid(row=0, column=1, padx=30)
        self.submit_button.grid(row=1, column=0, columnspan=4, pady=(10, 5)) 
        self.clear_plots()

    def clear_plots(self):
        self.ax.clear()
        self.ax.set_yscale('log')
        self.ax.set_title("Time-Averaged Resultant Acceleration Vector")
        self.ax.set_xlabel('Time (hours)')
        self.ax.set_ylabel('Magnitude (g)')
        self.ax.set_yticks([10**(-i) for i in range(0, 17, 2)])
        self.ax.set_ylim(10**-17, 10**0) 
        self.canvas.draw()

        self.path_ax.clear()
        self.path_ax.set_xlabel('X')
        self.path_ax.set_ylabel('Y')
        self.path_ax.set_zlabel('Z')
        ticks = np.arange(-1.0, 1.5, 0.5)
        self.path_ax.set_xticks(ticks)
        self.path_ax.set_yticks(ticks)
        self.path_ax.set_zticks(ticks)
        self.path_ax.set_title("Acceleration Vector Path")
        self.path_canvas.draw()

        self.components_ax.clear()
        self.components_ax.set_title("Time-Averaged Acceleration Vector Components")
        self.components_ax.set_xlabel('Time (hours)')
        self.components_ax.set_ylabel('Magnitude (g)')
        self.components_canvas.draw()

    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    mainarray = file.read().replace("   ", " ").replace('\t', ' ').replace('\n', ' ').replace(',', ' ').split(' ')
                self.experimental_data = mainarray
                messagebox.showinfo("Success", "CSV file uploaded successfully.")
            except FileNotFoundError:
                messagebox.showerror("File Error", f"File not found: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def process_experimental_data(self, mainarray, startAnalysis, endAnalysis):
        datetime_str = []
        x = []
        y = []
        z = []
        timestamp = []

        for k in range(0, len(mainarray) - 4, 5):
            datetime_str.append(mainarray[k] + " " + mainarray[k + 1])
            x.append(float(mainarray[k + 2]))
            y.append(float(mainarray[k + 3]))
            z.append(float(mainarray[k + 4]))

        datetime_obj = [datetime.strptime(dt, '%H:%M:%S %m/%d/%Y') for dt in datetime_str]
        time_in_seconds = [(dt - datetime_obj[0]).total_seconds() for dt in datetime_obj]
        time_in_hours = [t / 3600 for t in time_in_seconds]

        path_visualization = PathVisualization("experimental", x, y, z)
        distribution_score = path_visualization.getDistribution()

        self.update_experimental_plots(x, y, z, time_in_hours, startAnalysis, endAnalysis, distribution_score)

    def update_experimental_plots(self, x, y, z, time_in_hours, startAnalysis, endAnalysis, distribution_score):
        rcParams['font.family'] = 'Calibri'

        self.ax.clear()
        self.ax.set_yscale('log')
        self.ax.set_title("Time-Averaged Resultant Acceleration Vector")

        xTimeAvg = np.cumsum(x) / np.arange(1, len(x) + 1)
        yTimeAvg = np.cumsum(y) / np.arange(1, len(y) + 1)
        zTimeAvg = np.cumsum(z) / np.arange(1, len(z) + 1)
        magnitude = np.sqrt(xTimeAvg**2 + yTimeAvg**2 + zTimeAvg**2)
        avgMagFull = np.mean(magnitude)

        self.ax.plot(time_in_hours, magnitude, color='#0032A0', label="Average Magnitude: " + f"{avgMagFull:.3g}")

        startSeg = next(i for i, t in enumerate(time_in_hours) if t >= startAnalysis)
        endSeg = next(i for i, t in enumerate(time_in_hours) if t >= endAnalysis)

        self.ax.axvline(x=startAnalysis, color='#E4002B', linestyle='--')
        self.ax.axvline(x=endAnalysis, color='#E4002B', linestyle='--')

        avgMagAnalysis = np.mean(magnitude[startSeg:endSeg])
        self.ax.plot(time_in_hours[startSeg:endSeg], magnitude[startSeg:endSeg], color='#E4002B', label="Average Magnitude: " + f"{avgMagAnalysis:.3g}")

        self.ax.legend()
        self.ax.set_xlabel('Time (hours)')
        self.ax.set_ylabel('Magnitude (g)')
        self.canvas.draw()

        self.path_ax.clear()
        self.path_ax.plot(x, y, z, color='#0032A0', linewidth=1)
        self.path_ax.set_xlabel('X')
        self.path_ax.set_ylabel('Y')
        self.path_ax.set_zlabel('Z')
        ticks = np.arange(-1.0, 1.5, 0.5)
        self.path_ax.set_xticks(ticks)
        self.path_ax.set_yticks(ticks)
        self.path_ax.set_zticks(ticks)
        self.path_ax.set_title("Acceleration Vector Path")
        self.path_ax.legend([f"Distribution: {distribution_score}"])

        self.path_canvas.draw()

        self.create_time_avg_fig(xTimeAvg, yTimeAvg, zTimeAvg, time_in_hours, mode='show')

    def submit(self):
        try:
            if self.mode_var.get() == "Theoretical":
                if not self.innerV_entry.get() or not self.outerV_entry.get() or not self.maxSeg_entry.get() or not self.startAnalysis_entry.get() or not self.endAnalysis_entry.get():
                    raise ValueError("All input fields must be filled.")

                innerV = float(self.innerV_entry.get())
                outerV = float(self.outerV_entry.get())
                maxSeg = float(self.maxSeg_entry.get())
                startAnalysis = float(self.startAnalysis_entry.get())
                endAnalysis = float(self.endAnalysis_entry.get())

                if innerV <= 0 or outerV <= 0:
                    raise ValueError("Frame velocities must be positive.")
                if startAnalysis < 0 or endAnalysis < 0 or maxSeg <= 0:
                    raise ValueError("Time values must be positive.")
                if endAnalysis <= startAnalysis:
                    raise ValueError("Upper bound for analysis period must be greater than the lower bound.")
                if endAnalysis > maxSeg:
                    raise ValueError("Upper bound must be less than or equal to the simulation duration.")
                if startAnalysis == endAnalysis:
                    raise ValueError("Upper and lower bounds must not be equal.")

                analysis = DataProcessor(innerV, outerV, maxSeg, startAnalysis, endAnalysis)
                path_visualization = PathVisualization(innerV, analysis.x, analysis.y, analysis.z)
                xTimeAvg, yTimeAvg, zTimeAvg = analysis._getTimeAvg()
                magnitude = analysis._getMagnitude(xTimeAvg, yTimeAvg, zTimeAvg)
                avgMagSeg, avgMagAnalysis = analysis._getMagSeg(magnitude)
                disScore = analysis.getDistribution()
                self.update_plot(analysis, magnitude, startAnalysis, endAnalysis, avgMagSeg, avgMagAnalysis, innerV, outerV, disScore, path_visualization)
            else:
                if not self.startAnalysis_entry_exp.get() or not self.endAnalysis_entry_exp.get():
                    raise ValueError("All input fields must be filled.")
                if not hasattr(self, 'experimental_data') or not self.experimental_data:
                    raise ValueError("Upload a CSV file.")

                startAnalysis = float(self.startAnalysis_entry_exp.get())
                endAnalysis = float(self.endAnalysis_entry_exp.get())

                if startAnalysis < 0 or endAnalysis < 0:
                    raise ValueError("Time values must be positive.")
                if endAnalysis <= startAnalysis:
                    raise ValueError("Upper bound for analysis period must be greater than the lower bound.")

                self.process_experimental_data(self.experimental_data, startAnalysis, endAnalysis)

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_plot(self, analysis, magnitude, startAnalysis, endAnalysis, avgMagSeg, avgMagAnalysis, innerV, outerV, disScore, path_visualization):
        rcParams['font.family'] = 'Calibri' 

        self.ax.clear()
        fTime = path_visualization.formatTime(analysis.time) 
        
        startIndex = next(i for i, t in enumerate(fTime) if t >= startAnalysis)
        endIndex = next(i for i, t in enumerate(fTime) if t >= endAnalysis)

        self.ax.set_yscale('log')
        self.ax.set_title("Time-Averaged Resultant Acceleration Vector")
        self.ax.plot(fTime, magnitude, color='#0032A0', label="Average Magnitude: " + f"{avgMagSeg:.3g}")
        self.ax.axvline(x=startAnalysis, color='#E4002B', linestyle='--')
        self.ax.axvline(x=endAnalysis, color='#E4002B', linestyle='--')
        self.ax.plot(fTime[startIndex:endIndex], magnitude[startIndex:endIndex], color='#E4002B', label="Average Magnitude: " + f"{avgMagAnalysis:.3g}")
        self.ax.legend()
        self.ax.set_xlabel('Time (hours)')
        self.ax.set_ylabel('Magnitude (g)')

        self.canvas.draw()

        self.path_ax.clear()
        self.path_ax.plot(analysis.x, analysis.y, analysis.z, color='#0032A0', linewidth=1)
        self.path_ax.set_xlabel('X')
        self.path_ax.set_ylabel('Y')
        self.path_ax.set_zlabel('Z')
        ticks = np.arange(-1.0, 1.5, 0.5)
        self.path_ax.set_xticks(ticks)
        self.path_ax.set_yticks(ticks)
        self.path_ax.set_zticks(ticks)
        self.path_ax.set_title("Acceleration Vector Path")
        self.path_ax.legend([f"Distribution: {disScore}"])

        self.path_canvas.draw()

        xTimeAvg, yTimeAvg, zTimeAvg = analysis._getTimeAvg()
        self.create_time_avg_fig_theoretical(xTimeAvg, yTimeAvg, zTimeAvg, analysis.time, mode='show')

    def create_time_avg_fig(self, xTimeAvg, yTimeAvg, zTimeAvg, time_in_hours, mode='save', legend=True, title=True):
        self.components_ax.clear()
        if title:
            self.components_ax.set_title('Time-Averaged Acceleration Vector Components')

        self.components_ax.plot(time_in_hours, xTimeAvg, label='X-Component', color='#0032A0')
        self.components_ax.plot(time_in_hours, yTimeAvg, label='Y-Component', color='#E4002B')
        self.components_ax.plot(time_in_hours, zTimeAvg, label='Z-Component', color='gray')
        self.components_ax.set_xlabel('Time (hours)')
        self.components_ax.set_ylabel('Magnitude (g)')

        if legend:
            self.components_ax.legend()

        self.components_canvas.draw()

    def create_time_avg_fig_theoretical(self, xTimeAvg, yTimeAvg, zTimeAvg, time_in_seconds, mode='save', legend=True, title=True):
        time_in_hours = [t / 3600 for t in time_in_seconds]

        self.components_ax.clear()
        if title:
            self.components_ax.set_title('Time-Averaged Acceleration Vector Components')

        self.components_ax.plot(time_in_hours, xTimeAvg, label='X-Component', color='#0032A0')
        self.components_ax.plot(time_in_hours, yTimeAvg, label='Y-Component', color='#E4002B')
        self.components_ax.plot(time_in_hours, zTimeAvg, label='Z-Component', color='gray')
        self.components_ax.set_xlabel('Time (hours)')
        self.components_ax.set_ylabel('Magnitude (g)')

        if legend:
            self.components_ax.legend()

        self.components_canvas.draw()

    def format_time(self, time):
        return time 

    def open_url(self, url):
        webbrowser.open_new(url)

if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()