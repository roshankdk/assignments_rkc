#!/usr/bin/env python3
"""
Personal Health Monitoring System - Raspberry Pi Simulation
This simulates the Raspberry Pi implementation without actual hardware
Can run on any computer or online Python environment
"""

import time
import random
import json
import sqlite3
import threading
from datetime import datetime, timedelta
import os

# Simulated GPIO class (replaces RPi.GPIO)
class SimulatedGPIO:
    BCM = "BCM"
    OUT = "OUT"
    IN = "IN"
    PUD_UP = "PUD_UP"
    FALLING = "FALLING"
    
    def __init__(self):
        self.pins = {}
        self.callbacks = {}
        
    def setmode(self, mode):
        print(f"GPIO Mode set to: {mode}")
        
    def setup(self, pin, direction, pull_up_down=None):
        self.pins[pin] = {
            'direction': direction,
            'state': False,
            'pull': pull_up_down
        }
        print(f"Pin {pin} configured as {direction}")
        
    def output(self, pin, state):
        if pin in self.pins:
            self.pins[pin]['state'] = state
            if pin == 17:  # Red LED
                print(f"🔴 Red LED: {'ON' if state else 'OFF'}")
            elif pin == 27:  # Green LED
                print(f"🟢 Green LED: {'ON' if state else 'OFF'}")
                
    def input(self, pin):
        return self.pins.get(pin, {}).get('state', False)
        
    def add_event_detect(self, pin, edge, callback, bouncetime=300):
        self.callbacks[pin] = callback
        print(f"Button event handler added for pin {pin}")
        
    def cleanup(self):
        print("GPIO cleanup completed")

# Replace RPi.GPIO with simulation
GPIO = SimulatedGPIO()

# Pin definitions
RED_LED = 17
GREEN_LED = 27
BUTTON = 22

# Health thresholds
HR_MIN = 60
HR_MAX = 100
SPO2_MIN = 95

# ThingSpeak Configuration (simulated)
THINGSPEAK_WRITE_KEY = "DEMO_API_KEY_12345"
THINGSPEAK_CHANNEL_ID = "1234567"

class SimulatedSensor:
    """Simulates MAX30102 sensor readings"""
    def __init__(self):
        self.base_hr = 75
        self.base_spo2 = 98
        self.hr_trend = 0
        self.spo2_trend = 0
        
    def read(self):
        """Simulate realistic sensor readings"""
        # Add some realistic variation
        self.hr_trend += random.uniform(-0.5, 0.5)
        self.hr_trend = max(-5, min(5, self.hr_trend))  # Limit trend
        
        self.spo2_trend += random.uniform(-0.2, 0.2)
        self.spo2_trend = max(-2, min(2, self.spo2_trend))
        
        hr = int(self.base_hr + self.hr_trend + random.randint(-3, 3))
        spo2 = int(self.base_spo2 + self.spo2_trend + random.randint(-1, 1))
        
        # Constrain to realistic ranges
        hr = max(50, min(130, hr))
        spo2 = max(90, min(100, spo2))
        
        return hr, spo2
        
    def simulate_activity(self):
        """Simulate different activity levels"""
        activity = random.choice(['rest', 'normal', 'active'])
        if activity == 'rest':
            self.base_hr = random.randint(60, 70)
        elif activity == 'normal':
            self.base_hr = random.randint(70, 85)
        else:  # active
            self.base_hr = random.randint(85, 110)

class HealthMonitor:
    def __init__(self):
        # GPIO Setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RED_LED, GPIO.OUT)
        GPIO.setup(GREEN_LED, GPIO.OUT)
        GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Initialize sensor
        self.sensor = SimulatedSensor()
        
        # Initialize database
        self.init_database()
        
        # Current readings
        self.current_hr = 75
        self.current_spo2 = 98
        self.current_status = "Normal"
        
        # Threading control
        self.running = True
        self.button_pressed = False
        
        # Statistics
        self.reading_count = 0
        self.alert_count = 0
        
    def init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('health_data.db', check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                heart_rate INTEGER,
                spo2 INTEGER,
                status TEXT
            )
        ''')
        self.conn.commit()
        print("✅ Database initialized")
        
    def read_sensors(self):
        """Read from simulated sensor"""
        hr, spo2 = self.sensor.read()
        self.current_hr = hr
        self.current_spo2 = spo2
        return hr, spo2
        
    def check_vitals(self, hr, spo2):
        """Check if vitals are within normal range"""
        is_normal = (HR_MIN <= hr <= HR_MAX and spo2 >= SPO2_MIN)
        
        if is_normal:
            GPIO.output(GREEN_LED, True)
            GPIO.output(RED_LED, False)
            status = "Normal"
        else:
            GPIO.output(RED_LED, True)
            GPIO.output(GREEN_LED, False)
            status = "Alert"
            self.alert_count += 1
            
        self.current_status = status
        return status
        
    def save_to_database(self, hr, spo2, status):
        """Save reading to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO readings (heart_rate, spo2, status)
            VALUES (?, ?, ?)
        ''', (hr, spo2, status))
        self.conn.commit()
        self.reading_count += 1
        
    def send_to_cloud(self, hr, spo2):
        """Simulate sending data to ThingSpeak"""
        print(f"\n☁️  Sending to ThingSpeak...")
        time.sleep(0.5)  # Simulate network delay
        
        # Simulate API response
        if random.random() > 0.1:  # 90% success rate
            print(f"✅ Data sent successfully!")
            print(f"   Channel: {THINGSPEAK_CHANNEL_ID}")
            print(f"   Entry ID: {random.randint(1000, 9999)}")
            return True
        else:
            print(f"❌ Failed to send (network error)")
            return False
            
    def button_callback(self, channel=None):
        """Handle button press"""
        if not self.button_pressed:
            self.button_pressed = True
            print("\n🔘 Button pressed - Manual save triggered")
            
            hr, spo2 = self.read_sensors()
            status = self.check_vitals(hr, spo2)
            
            # Save locally
            self.save_to_database(hr, spo2, status)
            
            # Send to cloud
            if self.send_to_cloud(hr, spo2):
                # Flash green LED
                for _ in range(3):
                    GPIO.output(GREEN_LED, True)
                    time.sleep(0.1)
                    GPIO.output(GREEN_LED, False)
                    time.sleep(0.1)
                    
            self.button_pressed = False
            
    def daily_summary(self):
        """Calculate and display daily summary"""
        cursor = self.conn.cursor()
        
        # Get today's data
        cursor.execute('''
            SELECT AVG(heart_rate), AVG(spo2), COUNT(*), 
                   MIN(heart_rate), MAX(heart_rate),
                   MIN(spo2), MAX(spo2)
            FROM readings
            WHERE DATE(timestamp) = DATE('now')
        ''')
        result = cursor.fetchone()
        
        if result and result[2] > 0:
            avg_hr, avg_spo2, count, min_hr, max_hr, min_spo2, max_spo2 = result
            
            print("\n" + "="*50)
            print("📊 DAILY HEALTH SUMMARY")
            print("="*50)
            print(f"Total Readings: {count}")
            print(f"Heart Rate:")
            print(f"  Average: {avg_hr:.1f} bpm")
            print(f"  Range: {min_hr} - {max_hr} bpm")
            print(f"Blood Oxygen:")
            print(f"  Average: {avg_spo2:.1f}%")
            print(f"  Range: {min_spo2} - {max_spo2}%")
            print(f"Alerts Today: {self.alert_count}")
            print("="*50 + "\n")
            
            # Send summary to cloud
            self.send_to_cloud(int(avg_hr), int(avg_spo2))
            
    def simulate_button_press(self):
        """Simulate button press for testing"""
        while self.running:
            time.sleep(random.uniform(10, 30))  # Random interval
            if self.running and random.random() > 0.7:  # 30% chance
                print("\n💡 Simulating button press...")
                self.button_callback()
                
    def monitor_loop(self):
        """Main monitoring loop"""
        print("\n🏥 Health Monitoring System Started")
        print("=" * 50)
        print("Monitoring vital signs...")
        print("Simulating sensor readings...\n")
        
        last_display_time = 0
        last_summary_time = time.time()
        
        while self.running:
            current_time = time.time()
            
            # Read sensors every second
            if current_time - last_display_time >= 1:
                hr, spo2 = self.read_sensors()
                status = self.check_vitals(hr, spo2)
                
                # Display current readings
                timestamp = datetime.now().strftime("%H:%M:%S")
                status_icon = "✅" if status == "Normal" else "⚠️"
                
                print(f"\r[{timestamp}] HR: {hr:3d} bpm | SpO2: {spo2:3d}% | {status_icon} {status}   ", 
                      end='', flush=True)
                
                last_display_time = current_time
                
                # Occasionally change activity level
                if random.random() > 0.95:
                    self.sensor.simulate_activity()
                    print(f"\n🏃 Activity level changed")
                
            # Daily summary every 60 seconds (simulating daily)
            if current_time - last_summary_time >= 60:
                self.daily_summary()
                last_summary_time = current_time
                
            time.sleep(0.1)
            
    def get_recent_data(self, hours=24):
        """Get recent readings for the dashboard"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT timestamp, heart_rate, spo2, status
            FROM readings
            WHERE timestamp > datetime('now', '-{} hours')
            ORDER BY timestamp DESC
            LIMIT 100
        '''.format(hours))
        
        return cursor.fetchall()
        
    def run(self):
        """Start the monitoring system"""
        # Start button simulation thread
        button_thread = threading.Thread(target=self.simulate_button_press)
        button_thread.start()
        
        try:
            self.monitor_loop()
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down...")
            self.running = False
            button_thread.join()
            GPIO.cleanup()
            self.conn.close()
            print("✅ System shutdown complete")

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
        
    monitor = HealthMonitor()
    monitor.run()