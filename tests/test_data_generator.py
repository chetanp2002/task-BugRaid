import unittest
import pandas as pd
from src.data_generator import SyntheticDataGenerator

class TestDataGenerator(unittest.TestCase):
    
    def test_data_generation(self):
        """Test that data is generated with correct structure"""
        generator = SyntheticDataGenerator()
        generator.size = 1000  # Small test dataset
        df = generator.generate_data()
        
        # Check basic structure
        self.assertEqual(len(df), 1000)
        self.assertIn('service', df.columns)
        self.assertIn('log_level', df.columns)
        self.assertIn('cpu_usage', df.columns)
        
        # Check that anomalies exist
        error_logs = df[df['log_level'].isin(['ERROR', 'FATAL'])]
        high_cpu = df[df['cpu_usage'] > 90]
        
        self.assertGreater(len(error_logs), 0, "Should have error logs")
        self.assertGreater(len(high_cpu), 0, "Should have high CPU values")

if __name__ == '__main__':
    unittest.main()