# Personal Health Monitoring System - Complete Setup Guide

This guide will walk you through setting up both the Arduino simulation and the Raspberry Pi simulation with Flask dashboard.

## Table of Contents
1. [Arduino/Wokwi Online Simulation](#part-1-arduinowokwi-simulation)
2. [Raspberry Pi Simulation with Flask](#part-2-raspberry-pi-simulation)
3. [Running on Different Platforms](#part-3-running-options)

---

## Part 1: Arduino/Wokwi Simulation

### Step 1: Access Wokwi Simulator
1. Open your browser and go to [https://wokwi.com](https://wokwi.com)
2. Click "Start Simulation" or "New Project"
3. Select "Arduino Uno"

### Step 2: Set Up the Circuit
1. In the Wokwi editor, click on "diagram.json" tab
2. Replace all content with the content from `diagram.json` file
3. Click "sketch.ino" tab to return to code view

### Step 3: Add the Code
1. Delete default code in sketch.ino
2. Copy all content from `health_monitor_arduino.ino`
3. Paste into the editor

### Step 4: Run Simulation
1. Click green "Start Simulation" button
2. Open Serial Monitor (click terminal icon)
3. You should see initialization messages

### Step 5: Test Features
- **Adjust Heart Rate**: Turn left potentiometer (40-140 bpm range)
- **Adjust SpO2**: Turn right potentiometer (85-100% range)  
- **Normal Values**: Green LED on (HR: 60-100, SpO2: ≥95%)
- **Alert Values**: Red LED on (values outside normal range)
- **Manual Save**: Press button to save to cloud
- **Auto Save**: Wait 60 seconds for automatic save

### Troubleshooting Wokwi
- If LCD doesn't show text, check I2C connections
- If LEDs don't light, verify resistor connections
- If button doesn't work, check pull-up configuration

---

## Part 2: Raspberry Pi Simulation

### Option A: Run Locally on Your Computer

#### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

#### Step 1: Create Project Directory
```bash
mkdir health-monitor
cd health-monitor
```

#### Step 2: Create Required Directories
```bash
mkdir templates
mkdir static
mkdir data
```

#### Step 3: Save Files
1. Save `main_simulator.py` in the project root
2. Save `app.py` in the project root
3. Save `dashboard.html` in `templates/` folder
4. Save `requirements.txt` in the project root

#### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 5: Run the Simulator
Open two terminal windows:

**Terminal 1 - Run Main Simulator:**
```bash
python main_simulator.py
```
You should see:
- Health monitoring started
- Simulated readings every second
- Periodic button presses
- Daily summaries every 60 seconds

**Terminal 2 - Run Flask Dashboard:**
```bash
python app.py
```
You should see:
- Flask server starting
- Dashboard URL: http://localhost:5000

#### Step 6: View Dashboard
1. Open browser to http://localhost:5000
2. You'll see real-time health data
3. Charts update automatically
4. Export data using the export button

### Option B: Run on Online Python Platform

#### Using Repl.it (Free)
1. Go to [https://replit.com](https://replit.com)
2. Create new Python repl
3. Upload all files
4. In Shell, run:
   ```bash
   pip install flask
   python app.py
   ```
5. Click "Open in new tab" when web view appears

#### Using Google Colab
1. Go to [https://colab.research.google.com](https://colab.research.google.com)
2. Create new notebook
3. Install requirements:
   ```python
   !pip install flask
   ```
4. Upload files using sidebar
5. Run Flask with ngrok:
   ```python
   !pip install pyngrok
   from pyngrok import ngrok
   
   # Run Flask in background
   !python app.py &
   
   # Create tunnel
   public_url = ngrok.connect(5000)
   print(public_url)
   ```

### Option C: Run on Raspberry Pi

If you have an actual Raspberry Pi:

#### Step 1: Install Dependencies
```bash
sudo apt-get update
sudo apt-get install python3-pip
pip3 install -r requirements.txt
```

#### Step 2: For Real Hardware
Uncomment these lines in requirements.txt:
```
RPi.GPIO==0.7.1
max30102==0.3.3
```

#### Step 3: Modify Code for Real Hardware
In `main_simulator.py`, replace the SimulatedGPIO class with:
```python
import RPi.GPIO as GPIO
```

And replace SimulatedSensor with actual MAX30102:
```python
import max30102

class RealSensor:
    def __init__(self):
        self.m = max30102.MAX30102()
        
    def read(self):
        return self.m.read_sequential()
```

---

## Part 3: Running Options

### Testing Flow

1. **Start with Wokwi** (5 minutes)
   - Test basic logic
   - Verify LED responses
   - Check serial output

2. **Run Python Simulation** (10 minutes)
   - Test full system flow
   - Verify database operations
   - Check web dashboard

3. **Deploy to Raspberry Pi** (when ready)
   - Connect real hardware
   - Test with actual sensor
   - Deploy to cloud

### File Structure
```
health-monitor/
├── main_simulator.py      # Main monitoring system
├── app.py                 # Flask web server
├── requirements.txt       # Python dependencies
├── health_data.db        # SQLite database (created automatically)
├── templates/
│   └── dashboard.html    # Web interface
├── static/               # Static files (optional)
└── data/                 # Data directory
```

### Common Issues & Solutions

#### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000
# Kill the process
kill -9 <PID>
```

#### Database Locked
- Stop all Python processes
- Delete health_data.db
- Restart the application

#### No Data Showing
1. Ensure main_simulator.py is running
2. Check console for errors
3. Verify database has data:
   ```bash
   sqlite3 health_data.db "SELECT COUNT(*) FROM readings;"
   ```

### Cloud Deployment Options

#### Free Cloud Platforms

1. **ThingSpeak Setup**
   - Create account at [thingspeak.com](https://thingspeak.com)
   - Create new channel with fields:
     - Field 1: Heart Rate
     - Field 2: SpO2
   - Copy Write API Key
   - Update `main_simulator.py` with your key

2. **Ngrok for Remote Access**
   ```bash
   # Download ngrok
   wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
   unzip ngrok-stable-linux-amd64.zip
   
   # Run Flask app
   python app.py
   
   # In another terminal
   ./ngrok http 5000
   ```

3. **Deploy to Render.com (Free)**
   - Create account at render.com
   - New Web Service
   - Connect GitHub repo
   - Auto-deploys on push

### Testing Your Implementation

1. **Unit Tests**
   - Sensor readings in range
   - Alert thresholds work
   - Database saves correctly
   - API endpoints respond

2. **Integration Tests**
   - Button triggers save
   - LEDs respond to alerts
   - Dashboard updates live
   - Export function works

3. **Demo Preparation**
   - Test all features
   - Prepare backup data
   - Record demo video
   - Have offline version ready

### Project Submission Checklist

- [ ] Arduino simulation video/screenshots
- [ ] Python simulation running
- [ ] Dashboard screenshots
- [ ] Code well-commented
- [ ] All features implemented
- [ ] Report sections complete
- [ ] Presentation ready

---

## Quick Start Commands

```bash
# Clone or create project
mkdir health-monitor && cd health-monitor

# Create structure
mkdir templates static data

# Save all files from artifacts

# Install and run
pip install -r requirements.txt

# Terminal 1
python main_simulator.py

# Terminal 2  
python app.py

# Open browser
# http://localhost:5000
```

## Support Resources

- Wokwi Documentation: https://docs.wokwi.com
- Flask Documentation: https://flask.palletsprojects.com
- Chart.js Documentation: https://www.chartjs.org/docs
- ThingSpeak API: https://www.mathworks.com/help/thingspeak

Good luck with your project!