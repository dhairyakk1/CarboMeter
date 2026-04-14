import math

class CarbonTracker:
    def __init__(self):
        # Global Statistics for Percentile Calculations
        self.GLOBAL_MEAN = 400.0
        self.GLOBAL_STD_DEV = 200.0
        
        # Transport Emission Factors (kg CO2 per km)
        self.TRANSPORT_FACTORS = {
            "Electric Two-Wheeler": 0.02,
            "Train/Metro": 0.04,
            "Electric Four-Wheeler": 0.05,
            "Petrol Two-Wheeler": 0.05,
            "Bus": 0.08,
            "Petrol Car": 0.14,
            "Diesel Car": 0.17
        }
        
        # Diet Additive Penalties (kg CO2 per month)
        self.DIET_MEAT = {"Never": 0, "1-2 times/week": 30, "3-5 times/week": 60, "Daily": 100}
        self.DIET_DAIRY = {"Never": 0, "Occasional": 10, "Daily": 30}
        self.DIET_OILY = {"Rarely": 0, "Occasional": 10, "Daily": 25}

    def calculate_emissions(self, vehicle, distance, kwh, meat, dairy, oily):
        """Calculates the distinct categories and the grand total."""
        # Transport
        transport_factor = self.TRANSPORT_FACTORS.get(vehicle, 0.0)
        transport_total = distance * transport_factor
        
        # Energy
        energy_total = kwh * 0.85
        
        # Diet (Base 100kg + Penalties)
        diet_total = 100.0 
        diet_total += self.DIET_MEAT.get(meat, 0)
        diet_total += self.DIET_DAIRY.get(dairy, 0)
        diet_total += self.DIET_OILY.get(oily, 0)
        
        emissions_dict = {
            "Transport": transport_total,
            "Energy": energy_total,
            "Diet": diet_total
        }
        
        return emissions_dict

    def get_gradient_status(self, total):
        """Returns the status string and associated UI color based on thresholds."""
        if total < 200: return ("Very Low", "green")
        if total < 350: return ("Low", "light green")
        if total < 550: return ("Moderate", "orange")
        if total < 900: return ("High", "red")
        return ("Extreme", "dark red")

    def get_percentile(self, total):
        """Calculates the global percentile using a Normal Distribution CDF."""
        z_score = (total - self.GLOBAL_MEAN) / self.GLOBAL_STD_DEV
        cdf = 0.5 * (1.0 + math.erf(z_score / math.sqrt(2.0)))
        top_percentile = (1.0 - cdf) * 100.0
        return max(0.1, round(top_percentile, 1))

    def get_action_plan(self, emissions_dict, inputs):
        """Dynamic Decision Tree to target the specific worst habit."""
        highest_category = max(emissions_dict, key=emissions_dict.get)
        
        if highest_category == "Transport":
            vehicle = inputs["vehicle"]
            if vehicle in ["Diesel Car", "Petrol Car"]:
                return f"Action Plan: Your {vehicle} is your biggest emitter. Substituting just 2 days of driving with public transit can drastically lower your percentile."
            elif vehicle in ["Electric Two-Wheeler", "Train/Metro"]:
                return "Action Plan: Even though transport is your highest category, you are using highly efficient methods. Try optimizing trip distances."
            else:
                return "Action Plan: Consider carpooling or switching to a more efficient vehicle to reduce your transport footprint."
                
        elif highest_category == "Diet":
            if inputs["meat"] in ["3-5 times/week", "Daily"]:
                return "Action Plan: Diet is your biggest factor. Swapping red/white meat for plant-based proteins a few times a week will cause a massive drop in your footprint."
            if inputs["oily"] == "Daily":
                return "Action Plan: Heavily processed cooking oils are driving up your diet footprint. Switching to whole foods will lower this significantly."
            return "Action Plan: Look into reducing dairy consumption or locally sourcing your food to optimize your dietary emissions."
            
        elif highest_category == "Energy":
            return "Action Plan: Energy consumption is your largest factor. Unplugging idle devices and managing HVAC usage can efficiently cut this down."
            
        return "Action Plan: Keep monitoring your habits!"