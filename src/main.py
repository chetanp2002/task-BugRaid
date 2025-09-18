import logging
import json
import time
import random  
import pandas as pd
from memory_profiler import memory_usage
from src.data_generator import SyntheticDataGenerator
from src.anomaly_detector import AnomalyDetector
from src.llm_candidate import LLMCandidateGenerator
from src.sqs_handler import SQSHandler
from config import settings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    start_time = time.time()
    
    # Step 1: Generate synthetic data
    logger.info("Generating synthetic data...")
    data_generator = SyntheticDataGenerator()
    df = data_generator.to_csv('outputs/synthetic_data.csv')
    
    # Step 2: Set up SQS queue and send messages
    logger.info("Setting up SQS queue...")
    sqs = SQSHandler()
    sqs.create_queue(settings.SQS_QUEUE_NAME)
    
    # Send data to SQS in chunks
    for i in range(0, len(df), settings.CHUNK_SIZE):
        chunk = df.iloc[i:i+settings.CHUNK_SIZE]
        for _, row in chunk.iterrows():
            sqs.send_message(row.to_dict())
    
    # Step 3: Process messages from the queue and detect anomalies
    logger.info("Processing messages for anomaly detection...")
    detector = AnomalyDetector()
    llm_generator = LLMCandidateGenerator()
    
    # We'll collect anomalies and their metadata for LLM processing
    anomalies = []
    
    # Process messages in chunks for efficiency
    processed_count = 0
    while processed_count < len(df):
        messages = sqs.receive_messages(max_messages=settings.SQS_MAX_MESSAGES)
        if not messages:
            break
            
        # Convert messages to DataFrame
        data_batch = []
        for msg in messages:
            data_batch.append(json.loads(msg['Body']))
        batch_df = pd.DataFrame(data_batch)
        
        # Detect anomalies
        results = detector.detect_anomalies(batch_df)
        
        # For each row, if the combined model flags it as anomaly, collect metadata for LLM
        for i, row in batch_df.iterrows():
            if results['combined'][i] == 1:
                # Extract metadata (excluding raw message)
                metadata = {
                    'id': processed_count + i,
                    'timestamp': row['timestamp'],
                    'service': row['service'],
                    'log_level': row['log_level'],
                    'cpu_usage': row['cpu_usage'],
                    'latency': row['latency'],
                    'trace_id': row['trace_id'],
                    'span_id': row['span_id'],
                    'event_type': row['event_type']
                }
                anomalies.append(metadata)
                
        # Delete processed messages from queue
        for msg in messages:
            sqs.delete_message(msg)
            
        processed_count += len(messages)
        logger.info(f"Processed {processed_count} messages")
    
    # Step 4: Generate candidate root causes for anomalies using LLM
    logger.info(f"Generating candidate root causes for {len(anomalies)} anomalies...")
    candidates = []
    for anomaly in anomalies:
        response = llm_generator.generate_candidate(anomaly)
        candidate = llm_generator.parse_response(response)
        if candidate:
            candidates.append(candidate)
    
    # Save candidates to JSON file
    with open('outputs/anomalies.json', 'w') as f:
        json.dump(candidates, f, indent=4)
    
    # Step 5: Evaluate the models (since we know the synthetic anomalies)
    # For evaluation, we need the true labels. We'll create a true_anomalies list from the synthetic data.
    # In our synthetic data, we know anomalies were introduced in logs (ERROR/FATAL with error_rate) and metrics (spikes with anomaly_rate)
    true_anomalies = []
    for _, row in df.iterrows():
        is_anomaly = 0
        if row['log_level'] in ['ERROR', 'FATAL']:
            is_anomaly = 1
        if row['cpu_usage'] > 90 or row['latency'] > 500:
            is_anomaly = 1
        if row['span_id'] is None:
            is_anomaly = 1
        true_anomalies.append(is_anomaly)
    
    evaluation = detector.evaluate(df, true_anomalies)
    logger.info("Model Evaluation:")
    for model_name, metrics in evaluation.items():
        logger.info(f"{model_name}: Precision={metrics['precision']}, Recall={metrics['recall']}")
    
    end_time = time.time()
    logger.info(f"Total execution time: {end_time - start_time} seconds")
    
    # Memory usage
    mem_usage = memory_usage(-1, interval=1, timeout=1)
    logger.info(f"Peak memory usage: {max(mem_usage)} MiB")

if __name__ == '__main__':
    main()