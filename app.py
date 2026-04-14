import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import your custom logic engine
from logic import CarbonTracker

class CarboMeterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CarboMeter Analytics")
        self.root.geometry("600x850")
        
        self.tracker = CarbonTracker()
        
        self.setup_ui()

    def setup_ui(self):
        # --- TITLE ---
        tk.Label(self.root, text="CarboMeter Dashboard", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # --- INPUT FORM FRAME ---
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)
        
        # Transport
        tk.Label(input_frame, text="Primary Transport:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.vehicle_var = tk.StringVar(value="Petrol Car")
        vehicle_options = list(self.tracker.TRANSPORT_FACTORS.keys())
        tk.OptionMenu(input_frame, self.vehicle_var, *vehicle_options).grid(row=0, column=1, sticky="ew")
        
        tk.Label(input_frame, text="Monthly Distance (km):").grid(row=1, column=0, sticky="w")
        self.distance_entry = tk.Entry(input_frame)
        self.distance_entry.insert(0, "500")
        self.distance_entry.grid(row=1, column=1)

        # Energy
        tk.Label(input_frame, text="Monthly Electricity (kWh):", font=("Helvetica", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(15,5))
        self.kwh_entry = tk.Entry(input_frame)
        self.kwh_entry.insert(0, "200")
        self.kwh_entry.grid(row=2, column=1)

        # Diet
        tk.Label(input_frame, text="Dietary Frequencies:", font=("Helvetica", 10, "bold")).grid(row=3, column=0, sticky="w", pady=(15,5))
        
        tk.Label(input_frame, text="Meat Consumption:").grid(row=4, column=0, sticky="w")
        self.meat_var = tk.StringVar(value="1-2 times/week")
        tk.OptionMenu(input_frame, self.meat_var, *self.tracker.DIET_MEAT.keys()).grid(row=4, column=1, sticky="ew")
        
        tk.Label(input_frame, text="Dairy Consumption:").grid(row=5, column=0, sticky="w")
        self.dairy_var = tk.StringVar(value="Occasional")
        tk.OptionMenu(input_frame, self.dairy_var, *self.tracker.DIET_DAIRY.keys()).grid(row=5, column=1, sticky="ew")
        
        tk.Label(input_frame, text="Oily/Fried Foods:").grid(row=6, column=0, sticky="w")
        self.oily_var = tk.StringVar(value="Occasional")
        tk.OptionMenu(input_frame, self.oily_var, *self.tracker.DIET_OILY.keys()).grid(row=6, column=1, sticky="ew")

        # --- CALCULATE BUTTON ---
        calc_btn = tk.Button(self.root, text="Calculate My Footprint", command=self.on_calculate, bg="lightblue", font=("Helvetica", 12, "bold"))
        calc_btn.pack(pady=20)

        # --- DASHBOARD OUTPUT FRAME ---
        self.output_frame = tk.Frame(self.root)
        self.output_frame.pack(fill="both", expand=True)
        
        self.lbl_total = tk.Label(self.output_frame, text="", font=("Helvetica", 16, "bold"))
        self.lbl_total.pack()
        
        self.lbl_gradient = tk.Label(self.output_frame, text="", font=("Helvetica", 12, "bold"))
        self.lbl_gradient.pack(pady=2)
        
        self.lbl_percentile = tk.Label(self.output_frame, text="", font=("Helvetica", 11, "italic"))
        self.lbl_percentile.pack(pady=2)
        
        self.lbl_action = tk.Label(self.output_frame, text="", font=("Helvetica", 10), wraplength=450, justify="center")
        self.lbl_action.pack(pady=10)
        
        # Dedicated frame for the Matplotlib chart
        self.chart_frame = tk.Frame(self.output_frame)
        self.chart_frame.pack()

    def on_calculate(self):
        """The Bridge: Gathers UI data, sends to Logic, updates UI."""
        try:
            # 1. Gather Inputs
            distance = float(self.distance_entry.get())
            kwh = float(self.kwh_entry.get())
            inputs = {
                "vehicle": self.vehicle_var.get(),
                "meat": self.meat_var.get(),
                "dairy": self.dairy_var.get(),
                "oily": self.oily_var.get()
            }
            
            # 2. Run Engine Logic
            emissions_dict = self.tracker.calculate_emissions(inputs["vehicle"], distance, kwh, inputs["meat"], inputs["dairy"], inputs["oily"])
            total_co2 = sum(emissions_dict.values())
            
            status_text, status_color = self.tracker.get_gradient_status(total_co2)
            percentile = 100-self.tracker.get_percentile(total_co2)
            action_plan = self.tracker.get_action_plan(emissions_dict, inputs)
            
            # 3. Update Text UI
            self.lbl_total.config(text=f"Total Emissions: {total_co2:.1f} kg CO2")
            self.lbl_gradient.config(text=f"Status: {status_text}", fg=status_color)
            self.lbl_percentile.config(text=f"Your Carbon Emission footprint is higher than {percentile}% of the Global Population.")
            self.lbl_action.config(text=action_plan)
            
            # 4. Draw Chart
            self.draw_chart(emissions_dict)
            
        except ValueError:
            messagebox.showerror("Input Error", "Please ensure Distance and Electricity are valid numbers.")

    def draw_chart(self, data_dict):
        """Embeds Matplotlib pie chart into Tkinter."""
        # Clear previous chart if it exists
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        labels = list(data_dict.keys())
        sizes = list(data_dict.values())
        colors = ['#ff9999','#66b3ff','#99ff99']
        
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Draw pie; autopct handles percentage text automatically
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title("Emission Breakdown")
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

# --- Application Entry Point ---
if __name__ == "__main__":
    root = tk.Tk()
    app = CarboMeterApp(root)
    root.mainloop()