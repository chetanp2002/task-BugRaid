import unittest
import numpy as np
import pandas as pd
from src.anomaly_detector import AnomalyDetector

class TestAnomalyDetector(unittest.TestCase):
    
    def setUp(self):
        """Create test data with known anomalies"""
        self.normal_data = pd.DataFrame({
            'cpu_usage': np.random.normal(50, 10, 100),
            'latency': np.random.normal(100, 20, 100)
        })
        
        # Add some obvious anomalies
        self.anomalous_data = self.normal_data.copy()
        self.anomalous_data.loc[5, 'cpu_usage'] = 95  # Too high
        self.anomalous_data.loc[10, 'latency'] = 500  # Too high
        
        self.detector = AnomalyDetector()
    
    def test_detection(self):
        """Test that anomalies are detected"""
        results = self.detector.detect_anomalies(self.anomalous_data)
        
        # Should detect our injected anomalies
        self.assertEqual(results['combined'][5], 1, "Should detect high CPU")
        self.assertEqual(results['combined'][10], 1, "Should detect high latency")
        
    def test_precision_recall(self):
        """Test evaluation metrics"""
        # Create known anomalies (1 = anomaly, 0 = normal)
        true_anomalies = [0] * 100
        true_anomalies[5] = 1  # We know this is anomalous
        true_anomalies[10] = 1  # We know this is anomalous
        
        evaluation = self.detector.evaluate(self.anomalous_data, true_anomalies)
        
        # Should have reasonable performance
        self.assertGreater(evaluation['combined']['precision'], 0.5)
        self.assertGreater(evaluation['combined']['recall'], 0.5)

if __name__ == '__main__':
    unittest.main()