import os

# Data generation settings
DATA_SIZE = 1000  # Number of records to generate
ERROR_RATE = 0.1   # Rate of error logs
ANOMALY_RATE = 0.1 # Rate of metric anomalies

# SQS settings
SQS_QUEUE_NAME = "anomaly-detection-queue"
SQS_MAX_MESSAGES = 10
SQS_VISIBILITY_TIMEOUT = 30

# Model settings
Z_SCORE_THRESHOLD = 3.0
ISOLATION_FOREST_CONTAMINATION = 0.01
ONE_CLASS_SVM_NU = 0.01
LSTM_EPOCHS = 10
LSTM_BATCH_SIZE = 64

# LLM settings - Updated for Groq and open-source models
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # Use Groq as default
LLM_MODEL = os.getenv("LLM_MODEL", "llama3-70b-8192")  # Open-source model
LLM_MAX_TOKENS = 500
LLM_TEMPERATURE = 0.1

# Groq API settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Performance settings
CHUNK_SIZE = 10000  # For processing data in chunks