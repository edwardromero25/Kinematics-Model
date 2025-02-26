import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from dataCompile import MagnitudeAnalysis
import matplotlib.pyplot as plt
from matplotlib import rcParams

class MagnitudeAnalysisGUI:
    def __init__(self, master):
        self.master = master
        master.title("Computer Model")

        font_style = ("Calibri", 12)
        title_font_style = ("Calibri", 20, "bold")
        category_font_style = ("Calibri", 14, "bold")

        input_frame = tk.Frame(master, padx=10, pady=10)
        input_frame.pack(side=tk.TOP, anchor=tk.CENTER)

        self.nasa_logo = tk.PhotoImage(file="images/nasa_logo.png")
        self.mssf_logo = tk.PhotoImage(file="images/mssf_logo.png")

        title_frame = tk.Frame(input_frame)
        title_frame.pack(pady=(0, 10))

        nasa_label = tk.Label(title_frame, image=self.nasa_logo)
        nasa_label.pack(side=tk.LEFT, padx=5)

        title_label = tk.Label(title_frame, text="Computer Model", font=title_font_style)
        title_label.pack(side=tk.LEFT, padx=5)

        mssf_label = tk.Label(title_frame, image=self.mssf_logo)
        mssf_label.pack(side=tk.LEFT, padx=5)

        center_frame = tk.Frame(input_frame)
        center_frame.pack()

        operating_frame = tk.Frame(center_frame, padx=10, pady=10)
        operating_frame.grid(row=0, column=0, padx=10)

        operating_label = tk.Label(operating_frame, text="Operating Condition", font=category_font_style)
        operating_label.pack()

        self.innerV_label = tk.Label(operating_frame, text="Inner Frame Velocity:", font=font_style)
        self.innerV_label.pack(anchor=tk.W)
        self.innerV_entry = tk.Entry(operating_frame, font=font_style)
        self.innerV_entry.pack()

        self.outerV_label = tk.Label(operating_frame, text="Outer Frame Velocity:", font=font_style)
        self.outerV_label.pack(anchor=tk.W)
        self.outerV_entry = tk.Entry(operating_frame, font=font_style)
        self.outerV_entry.pack()

        duration_frame = tk.Frame(center_frame, padx=10, pady=10)
        duration_frame.grid(row=0, column=1, padx=10)

        duration_label = tk.Label(duration_frame, text="Simulation Duration", font=category_font_style)
        duration_label.pack()

        self.maxSeg_entry = tk.Entry(duration_frame, font=font_style)
        self.maxSeg_entry.pack()

        analysis_frame = tk.Frame(center_frame, padx=10, pady=10)
        analysis_frame.grid(row=0, column=2, padx=10)

        analysis_label = tk.Label(analysis_frame, text="Time Period of Analysis", font=category_font_style)
        analysis_label.pack()

        analysis_period_frame = tk.Frame(analysis_frame)
        analysis_period_frame.pack()

        self.startAnalysis_entry = tk.Entry(analysis_period_frame, font=font_style, width=10)
        self.startAnalysis_entry.pack(side=tk.LEFT)
        hyphen_label = tk.Label(analysis_period_frame, text="-", font=font_style)
        hyphen_label.pack(side=tk.LEFT)
        self.endAnalysis_entry = tk.Entry(analysis_period_frame, font=font_style, width=10)
        self.endAnalysis_entry.pack(side=tk.LEFT)

        self.submit_button = tk.Button(center_frame, text="Start", command=self.submit, font=font_style, bg="lightgray")
        self.submit_button.grid(row=1, column=0, columnspan=3, pady=10)

        plot_frame = tk.Frame(master, padx=10, pady=10)
        plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.figure = plt.Figure()
        self.ax = self.figure.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasTkAgg(self.figure, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()

    def submit(self):
        try:
            innerV = float(self.innerV_entry.get())
            outerV = float(self.outerV_entry.get())
            maxSeg = int(float(self.maxSeg_entry.get()))
            startAnalysis = float(self.startAnalysis_entry.get())
            endAnalysis = float(self.endAnalysis_entry.get())

            if innerV <= 0 or outerV <= 0:
                raise ValueError("Frame velocities must be positive.")
            if startAnalysis < 0 or endAnalysis < 0 or maxSeg <= 0:
                raise ValueError("Time values must be positive.")
            if endAnalysis <= startAnalysis:
                raise ValueError("Upper bound must be greater than the lower bound.")
            if endAnalysis > maxSeg:
                raise ValueError("Upper bound must be less than or equal to the simulation duration.")
            if startAnalysis == endAnalysis:
                raise ValueError("Upper and lower bounds must not be equal.")

            analysis = MagnitudeAnalysis(innerV, outerV, maxSeg, startAnalysis, endAnalysis)
            xTimeAvg, yTimeAvg, zTimeAvg = analysis._getTimeAvg()
            magnitude = analysis._getMagnitude(xTimeAvg, yTimeAvg, zTimeAvg)
            avgMagSeg, avgMagAnalysis = analysis._getMagSeg(magnitude)
            self.update_plot(analysis, magnitude, startAnalysis, endAnalysis, avgMagSeg, avgMagAnalysis, innerV, outerV)

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_plot(self, analysis, magnitude, startAnalysis, endAnalysis, avgMagSeg, avgMagAnalysis, innerV, outerV):
        rcParams['font.family'] = 'Calibri' 

        self.ax.clear()
        fTime = analysis.formatTime(analysis.time)
        
        startIndex = next(i for i, t in enumerate(fTime) if t >= startAnalysis)
        endIndex = next(i for i, t in enumerate(fTime) if t >= endAnalysis)

        self.ax.set_yscale('log')
        self.ax.set_title(f"Magnitude vs. Time (I={innerV}, O={outerV})")
        self.ax.plot(fTime, magnitude, color='dimgray', label="Average Magnitude: " + f"{avgMagSeg:.4g}")
        self.ax.axvline(x=startAnalysis, color='blue', linestyle='--')
        self.ax.axvline(x=endAnalysis, color='blue', linestyle='--')
        self.ax.plot(fTime[startIndex:endIndex], magnitude[startIndex:endIndex], color='blue', label="Average Magnitude: " + f"{avgMagAnalysis:.4g}")
        self.ax.legend()
        self.ax.set_xlabel('Time (hours)')
        self.ax.set_ylabel('Magnitude (g)')

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    gui = MagnitudeAnalysisGUI(root)
    root.mainloop()
