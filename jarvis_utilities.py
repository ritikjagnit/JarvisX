import datetime
import re
import socket
from typing import Optional, Union

# Optional System Info Extension
try:
    import psutil
except ImportError:
    psutil = None

class JarvisUtilities:
    """
    100% Offline Utilities Class for JARVIS.
    No web scraping, APIs, or AI Wrappers needed. Provides instantaneous logic
    routing for math, unit conversions, local time operations, and system metrics.
    """
    
    def __init__(self):
        # Cached Conversion Rates Map (Hard-coded for offline scenarios)
        self.cached_exchange_rates = {
            "usd": 1.0,
            "inr": 83.50, # 1 USD = 83.50 INR (~Reference)
            "eur": 0.92,
            "gbp": 0.79,
            "jpy": 150.0
        }
        
        # Hard-coded UTC minute offsets for Standard Time formatting locally without pytz
        # Use simple mapping for major queries
        self.timezone_offsets = {
            "tokyo": 9 * 60,         # UTC +9
            "london": 0,             # UTC 0
            "new york": -5 * 60,     # UTC -5
            "california": -8 * 60,   # UTC -8
            "sydney": 10 * 60,       # UTC +10
            "dubai": 4 * 60,         # UTC +4
            "mumbai": 5 * 60 + 30    # UTC +5:30
        }

    # ============================================================
    # 1. CALCULATOR & MATH
    # ============================================================
    def calculate(self, expression: str) -> Optional[str]:
        """Handles basic arithmetic, percentages, and basic currency."""
        expr = expression.lower().strip()
        expr = expr.replace("equals", "").replace("what is", "").replace("calculate", "").strip()
        
        # Handle Percentages (e.g., "15% of 850" or "15 percent of 850")
        percent_match = re.search(r"(\d+(?:\.\d+)?)[\s]*%?[\s]*(?:percent)?[\s]*of[\s]*(\d+(?:\.\d+)?)", expr)
        if percent_match:
            percent_val = float(percent_match.group(1))
            total_val = float(percent_match.group(2))
            result = (percent_val / 100) * total_val
            return f"{percent_val}% of {total_val} is {round(result, 2)}"
            
        # Currency Conversion ("convert 100 usd to inr")
        currency_match = re.search(r"convert (\d+(?:\.\d+)?) ([a-z]{3}) to ([a-z]{3})", expr)
        if currency_match:
            amount = float(currency_match.group(1))
            from_cur = currency_match.group(2)
            to_cur = currency_match.group(3)
            
            if from_cur in self.cached_exchange_rates and to_cur in self.cached_exchange_rates:
                # Convert to USD first, then to target
                amount_in_usd = amount / self.cached_exchange_rates[from_cur]
                final_amount = amount_in_usd * self.cached_exchange_rates[to_cur]
                return f"{amount} {from_cur.upper()} equals approximately {round(final_amount, 2)} {to_cur.upper()}"
            return "Currency parameters mismatched in offline cache."

        # Word to Operator Translation
        replacements = {
            "plus": "+", "minus": "-", "multiply": "*", "times": "*", 
            "divided": "/", "divide": "/", "by": "", "into": "/", 
            "mod": "%", "power": "**"
        }
        for word, op in replacements.items():
            expr = expr.replace(word, op)

        # Basic Safe Calculation ("what is 25 + 75")
        safe_expr = re.sub(r'[^0-9+\-*/. %*()]', '', expr)
        # Ensure it actually has mathematical operations
        if safe_expr.strip() and re.search(r'[+\-*/%**]', safe_expr):
            try:
                result = eval(safe_expr, {"__builtins__": None}, {})
                return str(round(result, 3) if isinstance(result, float) else result)
            except Exception:
                pass
        return None

    # ============================================================
    # 2. TIME & DATE
    # ============================================================
    def get_time_date(self, query: str) -> Optional[str]:
        """Provides native datetime formatting + generic timezone shifts."""
        q = query.lower()
        now = datetime.datetime.now()
        
        # Checking local Time/Date targets
        if "time is it" in q or "current time" in q and "in " not in q:
            return f"The time is {now.strftime('%I:%M %p')}."
        if "date" in q and "today" in q:
            return f"Today's date is {now.strftime('%A, %B %d, %Y')}."
            
        # City Zone Target checking ("time in tokyo")
        time_in_match = re.search(r"time in ([a-z\s]+)", q)
        if time_in_match:
            city = time_in_match.group(1).strip()
            if city in self.timezone_offsets:
                # Use timezone-aware UTC datetime standard extraction
                utc_now = datetime.datetime.now(datetime.timezone.utc)
                city_time = utc_now + datetime.timedelta(minutes=self.timezone_offsets[city])
                return f"The current time in {city.title()} is {city_time.strftime('%I:%M %p')}."
            return f"I do not have the offline timezone data for {city}."
            
        return None

    # ============================================================
    # 3. UNIT CONVERSIONS
    # ============================================================
    def convert_units(self, query: str) -> Optional[str]:
        """Calculates rigid distance and temperature thresholds offline."""
        q = query.lower()
        
        # Distance (km <-> miles)
        dist_match = re.search(r"convert (\d+(?:\.\d+)?) (km|kilometers|miles|mi) to (km|kilometers|miles|mi)", q)
        if dist_match:
            val = float(dist_match.group(1))
            unit_from = dist_match.group(2)
            unit_to = dist_match.group(3)
            
            if "km" in unit_from or "kilometer" in unit_from:
                if "mi" in unit_to:
                    return f"{val} kilometers is equal to {round(val * 0.621371, 2)} miles."
            elif "mi" in unit_from:
                if "km" in unit_to or "kilometer" in unit_to:
                    return f"{val} miles is equal to {round(val * 1.60934, 2)} kilometers."

        # Temperature (Celsius <-> Fahrenheit)
        temp_match = re.search(r"convert (\d+(?:\.\d+)?) (celsius|c|fahrenheit|f) to (celsius|c|fahrenheit|f)", q)
        if temp_match:
            val = float(temp_match.group(1))
            u_from = temp_match.group(2)[0] # Extract the leading c or f
            u_to = temp_match.group(3)[0]
            
            if u_from == 'c' and u_to == 'f':
                res = (val * 9/5) + 32
                return f"{val} degrees Celsius equals {round(res, 1)} Fahrenheit."
            elif u_from == 'f' and u_to == 'c':
                res = (val - 32) * 5/9
                return f"{val} degrees Fahrenheit equals {round(res, 1)} Celsius."

        return None

    # ============================================================
    # 4. SYSTEM INFORMATION
    # ============================================================
    def check_system_info(self, query: str) -> Optional[str]:
        """Probes local OS system modules using PSUTIL natively."""
        q = query.lower()
        
        # WIFI Connectivity
        if "wifi" in q or "internet" in q:
            try:
                # 1 second fast ping
                socket.create_connection(("8.8.8.8", 53), timeout=1)
                return "Your WiFi connection is fully operational and online."
            except OSError:
                return "The system is currently completely offline. Internet ping failed."

        # System Metrics using Psutil
        if psutil:
            if "battery" in q:
                battery = psutil.sensors_battery()
                if battery:
                    plugged = "plugged in" if battery.power_plugged else "on battery power"
                    return f"System battery is at {battery.percent} percent, currently {plugged}."
                return "Battery monitoring capabilities are restricted on this device architecture."
                
            if "cpu" in q or "processor" in q:
                usage = psutil.cpu_percent(interval=0.5)
                return f"Currently, the CPU is running at {usage} percent capacity."
                
        elif "battery" in q or "cpu" in q:
            return "I require the psutil Python module to scan system hardware metrics directly."

        return None

    # ============================================================
    # ROUTER INTEGRATION
    # ============================================================
    def process_utility_command(self, query: str) -> str:
        """Main delegator to drop into your `process_voice_command` loop!"""
        result = self.convert_units(query)
        if result: return result
        
        result = self.calculate(query)
        if result: return result
        
        result = self.get_time_date(query)
        if result: return result
        
        result = self.check_system_info(query)
        if result: return result
        
        return "" # Completely unhandled

if __name__ == '__main__':
    # Offline Unit Diagnostics
    utils = JarvisUtilities()
    print("Beginning JARVIS 100% OFFLINE Unit Extraction Array...\n")
    
    test_queries = [
        "calculate 15% of 850",
        "what is 25 + 75",
        "convert 100 usd to inr",
        "what time is it",
        "time in tokyo",
        "convert 30 celsius to fahrenheit",
        "convert 5 km to miles",
        "battery percentage",
        "wifi status"
    ]
    
    for q in test_queries:
        print(f"User:   '{q}'")
        print(f"Jarvis: {utils.process_utility_command(q)}\n")
