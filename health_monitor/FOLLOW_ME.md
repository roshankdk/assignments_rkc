# Health Monitor Setup Guide

## Environment Setup
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application
1. Open two terminal windows
2. In terminal 1:
    ```bash
    python app.py
    ```
3. In terminal 2:
    ```bash
    python main_simulator.py
    ```
4. Open your browser and navigate to [http://localhost:5000](http://localhost:5000)