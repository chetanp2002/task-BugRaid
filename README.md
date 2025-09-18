# Anomaly Detection & Candidate Generation Service

## Overview

A production-ready Python service that generates synthetic MELT (Metrics, Events, Logs, Traces) data, detects anomalies using multiple machine learning techniques, and generates candidate root causes using large language models.

## Features

* **Synthetic Data Generation**: Creates realistic MELT data with configurable anomaly injection
* **Multi-Model Anomaly Detection**: Isolation Forest, One-Class SVM, LSTM Autoencoder, and statistical thresholds
* **LLM-Powered Root Cause Analysis**: Uses Groq's open-source LLMs for intelligent root cause generation
* **Event Processing Pipeline**: SQS-based message queue for scalable data processing
* **Performance Monitoring**: Real-time tracking of execution time and memory usage

## Technical Specifications

### Data Generation

* **Volume**: 1,000,000 records (\~1GB)
* **Anomaly Types**: Error logs, metric spikes, missing trace spans, noisy events
* **Anomaly Rate**: Configurable error and anomaly injection rates

### Anomaly Detection Models

1. **Isolation Forest**: Unsupervised learning for anomaly detection
2. **One-Class SVM**: Support Vector Machines for novelty detection
3. **LSTM Autoencoder**: Deep learning for time-series anomaly detection
4. **Statistical Thresholds**: Z-score based anomaly detection

### LLM Integration

* **Provider**: Groq Cloud (open-source LLMs)
* **Models Supported**: Llama 3, Mixtral, Gemma
* **Privacy Compliance**: Only metadata sent, no raw log data

## Installation & Setup

### Prerequisites

* Python 3.9+
* Groq API account (free tier available)

### Local Installation

```bash
# Clone repository
git clone <repository-url>
cd anomaly-detection-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Groq API key
```

### Docker Installation

```bash
# Build and run with Docker
docker-compose build
docker-compose up
```

## Usage

### Basic Execution

```bash
python -m src.main
```

### Expected Output

* **Data Generation**: Creates `outputs/synthetic_data.csv`
* **Anomaly Detection**: Processes data through all models
* **Root Cause Analysis**: Generates `outputs/anomalies.json`
* **Performance Metrics**: Displays execution time and memory usage

### Configuration

Modify `config/settings.py` for custom settings:

```python
DATA_SIZE = 10000          # Number of records to generate
ERROR_RATE = 0.01           # Rate of error logs
ANOMALY_RATE = 0.01         # Rate of metric anomalies
LLM_MODEL = "gemma2-9b-it"  # LLM model selection
```

## Performance Metrics

### Test Environment

* **Hardware**: Intel i7-10750H, 16GB RAM
* **Dataset**: 10000 records (\~1GB)
* **Execution Time**: 139 seconds (2.3 minutes)
* **Memory Usage**: 714 MB peak

### Model Performance

| Model            | Precision | Recall |
| ---------------- | --------- | ------ |
| Isolation Forest | 1.0       | 0.030  |
| One-Class SVM    | 0.571     | 0.121  |
| LSTM Autoencoder | 1.0       | 0.030  |
| Statistical      | 1.0       | 0.151  |
| Combined         | 1.0       | 0.061  |

### Sample Output

#### Detected Anomalies

```json
[
      {
        "anomaly_id": 6,
        "root_cause": "Missing span ID in auth-service, indicating a tracing issue or service disruption.",
        "confidence": 0.83
    },
    {
        "anomaly_id": 15,
        "root_cause": "High CPU usage (99.0%) in database, possibly due to a memory leak or inefficient code.",
        "confidence": 0.98
    },
    {
        "anomaly_id": 28,
        "root_cause": "High CPU usage (97.0%) in web-server, possibly due to a memory leak or inefficient code.",
        "confidence": 0.75
    },
]
```

## Architecture

### Workflow

1. **Data Generation** → Synthetic MELT data creation
2. **Queue Processing** → SQS-based message handling
3. **Anomaly Detection** → Multi-model detection pipeline
4. **Root Cause Analysis** → LLM-powered candidate generation
5. **Result Export** → Structured JSON output

### Code Structure

```
src/
├── main.py              # Application entry point
├── data_generator.py    # Synthetic data generation
├── anomaly_detector.py  # ML anomaly detection
├── llm_candidate.py     # LLM integration
└── sqs_handler.py       # Queue management
```

## Model Evaluation

### Evaluation Methodology

* **Precision**: Ratio of true positives to all predicted positives
* **Recall**: Ratio of true positives to all actual positives
* **Synthetic ground truth**: Known anomalies injected during data generation

### Results Analysis

* **High Precision**: Most models achieved 1.0 precision (no false positives)
* **Variable Recall**: Different recall rates show model strengths/weaknesses
* **Ensemble Advantage**: Combined model maintains perfect precision

## Limitations & Future Enhancements

### Current Limitations

* Synthetic data patterns may differ from real-world data
* LSTM model requires significant computational resources
* LLM dependency on external API availability

### Enhancement Opportunities

* Real-time data streaming support
* Additional anomaly detection models
* Custom LLM fine-tuning capabilities
* Enhanced visualization and reporting

## Compliance & Security

### Data Privacy

* No raw log data transmitted to external services
* Only metadata sent to LLM for root cause analysis
* Local processing for sensitive data components

### API Security

* Secure credential management via environment variables
* Optional mock mode for testing without API dependencies


## License

MIT License - See LICENSE file for details
