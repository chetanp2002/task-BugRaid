import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import logging
from config import settings

logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    def __init__(self):
        self.size = settings.DATA_SIZE
        self.error_rate = settings.ERROR_RATE
        self.anomaly_rate = settings.ANOMALY_RATE
        self.log_levels = ['INFO', 'DEBUG', 'WARN', 'ERROR', 'FATAL']
        self.services = ['web-server', 'auth-service', 'payment-service', 'user-service', 'database']
        self.event_types = ['request', 'response', 'system', 'transaction']
        
    def generate_data(self):
        logger.info(f"Generating {self.size} synthetic MELT records")
        
        # Generate timestamps
        start_time = datetime.now() - timedelta(days=1)
        timestamps = [(start_time + timedelta(seconds=random.randint(0, 86400))).isoformat() for _ in range(self.size)]
        timestamps.sort()
        
        # Generate service names
        services = [random.choice(self.services) for _ in range(self.size)]
        
        # Generate log levels with a bias towards INFO and DEBUG
        log_levels = np.random.choice(self.log_levels, size=self.size, p=[0.5, 0.3, 0.1, 0.05, 0.05])
        
        # Introduce errors based on error rate
        messages = []
        for i in range(self.size):
            if log_levels[i] in ['ERROR', 'FATAL'] and random.random() < self.error_rate:
                messages.append(f"Error in {services[i]} at {timestamps[i]}")
            else:
                messages.append(f"Operation completed successfully in {services[i]}")
        
        # Generate metrics (cpu_usage, latency)
        cpu_usage = np.random.normal(50, 10, self.size)
        latency = np.random.normal(100, 20, self.size)
        
        # Introduce metric anomalies
        for i in range(self.size):
            if random.random() < self.anomaly_rate:
                cpu_usage[i] = random.randint(90, 100)
                latency[i] = random.randint(500, 1000)
        
        # Generate traces (trace_id, span_id)
        trace_ids = [f"trace_{i}" for i in range(self.size)]
        span_ids = [f"span_{i}" for i in range(self.size)]
        
        # Introduce missing spans (anomaly)
        for i in range(self.size):
            if random.random() < self.anomaly_rate:
                span_ids[i] = None
        
        # Generate events
        events = np.random.choice(self.event_types, size=self.size)
        
        # Create DataFrame
        data = {
            'timestamp': timestamps,
            'service': services,
            'log_level': log_levels,
            'message': messages,
            'cpu_usage': cpu_usage,
            'latency': latency,
            'trace_id': trace_ids,
            'span_id': span_ids,
            'event_type': events
        }
        
        return pd.DataFrame(data)
    
    def to_csv(self, file_path):
        df = self.generate_data()
        df.to_csv(file_path, index=False)
        logger.info(f"Synthetic data saved to {file_path}")
        return df