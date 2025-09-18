import json
import logging
import groq
import random
from config import settings

logger = logging.getLogger(__name__)

class LLMCandidateGenerator:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
        self.api_key = settings.GROQ_API_KEY
        
    def generate_candidate(self, metadata):
        # Prepare the prompt
        prompt = f"""
        Based on the following metadata from a software system, generate a likely root cause:
        {metadata}
        
        Return your answer in a JSON format with keys 'anomaly_id', 'root_cause', and 'confidence'.
        """
        
        if self.provider == "groq":
            try:
                return self._call_groq(prompt)
            except Exception as e:
                logger.error(f"Error calling Groq API: {e}")
                # Fallback to mock response using metadata
                return self._mock_llm_call(metadata)
        else:
            return self._mock_llm_call(metadata)
    
    def _call_groq(self, prompt):
        client = groq.Client(api_key=self.api_key)
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful DevOps engineer analyzing system anomalies."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            response_format={"type": "json_object"}
        )
        
        return response.choices[0].message.content

    def _mock_llm_call(self, metadata):
        # Use metadata to generate varied mock responses
        service = metadata.get('service', 'unknown service')
        log_level = metadata.get('log_level', '')
        cpu_usage = metadata.get('cpu_usage', 0)
        latency = metadata.get('latency', 0)
        span_id = metadata.get('span_id', '')
        
        if log_level in ['ERROR', 'FATAL']:
            root_cause = f"{log_level} log detected in {service}, possibly due to a software bug or configuration error."
        elif cpu_usage > 90:
            root_cause = f"High CPU usage ({cpu_usage}%) in {service}, possibly due to a memory leak or inefficient code."
        elif latency > 500:
            root_cause = f"High latency ({latency}ms) in {service}, possibly due to network congestion or resource exhaustion."
        elif span_id is None:
            root_cause = f"Missing span ID in {service}, indicating a tracing issue or service disruption."
        else:
            root_cause = "Anomaly detected due to multiple factors, requiring further investigation."
        
        mock_response = {
            'anomaly_id': metadata.get('id', 'unknown'),
            'root_cause': root_cause,
            'confidence': round(0.7 + 0.3 * random.random(), 2)  # Random confidence between 0.7 and 1.0
        }
        
        return json.dumps(mock_response)
    
    def parse_response(self, response):
        # Parse the JSON response from the LLM
        try:
            data = json.loads(response)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return None