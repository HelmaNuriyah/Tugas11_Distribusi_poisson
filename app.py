# app.py
from flask import Flask, render_template, request
import numpy as np
from scipy.stats import poisson
import pandas as pd

app = Flask(__name__)

def calculate_queue_probabilities(arrival_rate, max_queue=10):
    """Calculate probabilities for different queue lengths"""
    probs = {}
    for i in range(max_queue + 1):
        prob = poisson.pmf(i, arrival_rate)
        probs[i] = round(prob * 100, 2)
    return probs

def calculate_waiting_time(arrival_rate, service_rate):
    """Calculate waiting time probabilities"""
    utilization = arrival_rate / service_rate
    if utilization >= 1:
        return {
            'short': 0,
            'medium': 20,
            'long': 80
        }
    
    # Probabilitas waktu tunggu berdasarkan tingkat utilization
    short_wait = round((1 - utilization) * 100, 2)  # < 5 menit
    medium_wait = round(utilization * (1 - utilization) * 100, 2)  # 5-15 menit
    long_wait = round(utilization * utilization * 100, 2)  # > 15 menit
    
    return {
        'short': short_wait,
        'medium': medium_wait,
        'long': long_wait
    }

def calculate_service_levels(arrival_rate, num_counters):
    """Calculate service level probabilities"""
    # Probabilitas berbagai level layanan
    adequate_service = round(poisson.cdf(num_counters, arrival_rate) * 100, 2)
    busy_service = round((1 - poisson.cdf(num_counters, arrival_rate)) * 
                        poisson.cdf(num_counters + 2, arrival_rate) * 100, 2)
    overload = round((1 - poisson.cdf(num_counters + 2, arrival_rate)) * 100, 2)
    
    return {
        'adequate': adequate_service,
        'busy': busy_service,
        'overload': overload
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        arrival_rate = float(request.form['arrival_rate'])
        service_rate = float(request.form['service_rate'])
        num_counters = int(request.form['num_counters'])
        
        queue_probs = calculate_queue_probabilities(arrival_rate)
        waiting_times = calculate_waiting_time(arrival_rate, service_rate)
        service_levels = calculate_service_levels(arrival_rate, num_counters)
        
        # Perhitungan statistik tambahan
        expected_queue = arrival_rate / (service_rate - arrival_rate) if arrival_rate < service_rate else float('inf')
        utilization = (arrival_rate / (service_rate * num_counters)) * 100

        stats = {
            'Rata-rata Panjang Antrian': f"{round(expected_queue, 2)} orang",
            'Utilisasi Loket': f"{round(utilization, 2)}%",
            'Kedatangan per Jam': f"{round(arrival_rate * 60, 0)} orang",
            'Kapasitas Layanan': f"{round(service_rate * num_counters * 60, 0)} orang/jam"
        }
        
        return render_template(
            'index.html',
            queue_probs=queue_probs,
            waiting_times=waiting_times,
            service_levels=service_levels,
            stats=stats,
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            num_counters=num_counters,
            show_results=True
        )
    
    return render_template('index.html', show_results=False)

if __name__ == '__main__':
    app.run(debug=True)