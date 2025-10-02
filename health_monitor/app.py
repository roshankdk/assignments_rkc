#!/usr/bin/env python3
"""
Flask Web Dashboard for Health Monitoring System
Run this alongside main_simulator.py to view data in browser
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import sqlite3
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

# Configuration
DATABASE = 'health_data.db'
STATIC_DIR = 'static'
TEMPLATE_DIR = 'templates'

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database if it doesn't exist"""
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                heart_rate INTEGER,
                spo2 INTEGER,
                status TEXT
            )
        ''')
        
        # Add some sample data
        sample_data = []
        base_time = datetime.now() - timedelta(hours=24)
        for i in range(48):  # 48 half-hour readings
            time_offset = base_time + timedelta(minutes=30*i)
            hr = 75 + (i % 10) - 5
            spo2 = 98 - (i % 3)
            status = "Normal" if (60 <= hr <= 100 and spo2 >= 95) else "Alert"
            sample_data.append((time_offset, hr, spo2, status))
            
        cursor.executemany('''
            INSERT INTO readings (timestamp, heart_rate, spo2, status)
            VALUES (?, ?, ?, ?)
        ''', sample_data)
        
        conn.commit()
        conn.close()
        print("✅ Sample database created with test data")

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/current')
def get_current():
    """Get most recent reading"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT heart_rate, spo2, status, timestamp
        FROM readings
        ORDER BY timestamp DESC
        LIMIT 1
    ''')
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            'heart_rate': row['heart_rate'],
            'spo2': row['spo2'],
            'status': row['status'],
            'timestamp': row['timestamp']
        })
    return jsonify({'error': 'No data available'})

@app.route('/api/history')
def get_history():
    """Get historical readings"""
    hours = request.args.get('hours', 24, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT heart_rate, spo2, status, timestamp
        FROM readings
        WHERE timestamp > datetime('now', '-{} hours')
        ORDER BY timestamp DESC
        LIMIT {}
    '''.format(hours, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list and reverse for chronological order
    data = [{
        'heart_rate': row['heart_rate'],
        'spo2': row['spo2'],
        'status': row['status'],
        'timestamp': row['timestamp']
    } for row in rows]
    
    data.reverse()  # Chronological order for charts
    
    return jsonify(data)

@app.route('/api/statistics')
def get_statistics():
    """Get statistical summary"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Today's statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total_readings,
            AVG(heart_rate) as avg_hr,
            MIN(heart_rate) as min_hr,
            MAX(heart_rate) as max_hr,
            AVG(spo2) as avg_spo2,
            MIN(spo2) as min_spo2,
            MAX(spo2) as max_spo2,
            SUM(CASE WHEN status = 'Alert' THEN 1 ELSE 0 END) as alert_count
        FROM readings
        WHERE DATE(timestamp) = DATE('now')
    ''')
    
    today_stats = cursor.fetchone()
    
    # All-time statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total_readings,
            AVG(heart_rate) as avg_hr,
            AVG(spo2) as avg_spo2
        FROM readings
    ''')
    
    all_time_stats = cursor.fetchone()
    conn.close()
    
    return jsonify({
        'today': {
            'total_readings': today_stats['total_readings'] or 0,
            'avg_hr': round(today_stats['avg_hr'] or 0, 1),
            'hr_range': {
                'min': today_stats['min_hr'] or 0,
                'max': today_stats['max_hr'] or 0
            },
            'avg_spo2': round(today_stats['avg_spo2'] or 0, 1),
            'spo2_range': {
                'min': today_stats['min_spo2'] or 0,
                'max': today_stats['max_spo2'] or 0
            },
            'alert_count': today_stats['alert_count'] or 0
        },
        'all_time': {
            'total_readings': all_time_stats['total_readings'] or 0,
            'avg_hr': round(all_time_stats['avg_hr'] or 0, 1),
            'avg_spo2': round(all_time_stats['avg_spo2'] or 0, 1)
        }
    })

@app.route('/api/export')
def export_data():
    """Export data as JSON"""
    hours = request.args.get('hours', 24, type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM readings
        WHERE timestamp > datetime('now', '-{} hours')
        ORDER BY timestamp DESC
    '''.format(hours))
    
    rows = cursor.fetchall()
    conn.close()
    
    data = [{
        'id': row['id'],
        'timestamp': row['timestamp'],
        'heart_rate': row['heart_rate'],
        'spo2': row['spo2'],
        'status': row['status']
    } for row in rows]
    
    response = jsonify({
        'export_date': datetime.now().isoformat(),
        'record_count': len(data),
        'data': data
    })
    
    response.headers['Content-Disposition'] = 'attachment; filename=health_data_export.json'
    return response

# Serve static files (if needed)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    # Initialize database if needed
    init_db()
    
    # Create directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("\n🌐 Starting Health Monitor Dashboard")
    print("=" * 50)
    print("✅ Dashboard URL: http://localhost:5000")
    print("📊 API Endpoints:")
    print("   - /api/current    (current readings)")
    print("   - /api/history    (historical data)")
    print("   - /api/statistics (summary stats)")
    print("   - /api/export     (export data)")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)