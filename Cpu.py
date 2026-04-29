import time as tm
from datetime import datetime

import psutil as ps
from plyer import notification as np


class CpuMonitor:
    def get_cpu_usage(self):
        return int(ps.cpu_percent(interval=None))

    def check_status(self, cpu):
        if cpu > 80:
            return "CPU Usage is High"
        if cpu >= 50:
            return "CPU Usage is Medium"
        return "CPU Usage is Normal"

    def get_temperature(self):
        """Get CPU temperature in Celsius, with a usage-based fallback."""
        try:
            temps = ps.sensors_temperatures()
            if temps:
                for entries in temps.values():
                    if entries:
                        return entries[0].current
        except AttributeError:
            pass

        try:
            import wmi

            c = wmi.WMI()
            for sensor in c.Win32_TemperatureProbe():
                if sensor.CurrentReading:
                    return float(sensor.CurrentReading) / 10 - 273.15
        except Exception:
            pass

        cpu = self.get_cpu_usage()
        if cpu > 80:
            return 75 + (cpu - 80) * 0.5
        if cpu > 50:
            return 55 + (cpu - 50) * 0.4
        return 40 + cpu * 0.15

    def check_temp_status(self, temp):
        if temp is None:
            return "N/A"
        if temp > 85:
            return f"Hot ({temp:.1f} C)"
        if temp > 70:
            return f"Warm ({temp:.1f} C)"
        return f"Cool ({temp:.1f} C)"

    def get_ram_usage(self):
        try:
            return ps.virtual_memory().percent
        except Exception:
            return 0

    def get_process_count(self):
        try:
            return len(ps.pids())
        except Exception:
            return 0

    def get_uptime(self):
        try:
            uptime_seconds = tm.time() - ps.boot_time()
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        except Exception:
            return "N/A"

    def get_boot_time(self):
        try:
            boot_time = datetime.fromtimestamp(ps.boot_time())
            return boot_time.strftime("%d %b %I:%M %p")
        except Exception:
            return "N/A"

    def send_alert(self, cpu):
        np.notify(
            title="High CPU Usage",
            message=f"CPU usage is {cpu}%. Laptop heavy load me hai.",
            timeout=5,
        )

    def run(self):
        while True:
            cpu = self.get_cpu_usage()
            print(f"CPU: {cpu}% - {self.check_status(cpu)}")
            tm.sleep(2)


if __name__ == "__main__":
    CpuMonitor().run()
