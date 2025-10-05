
import json
import math
from typing import List

# Sample data from the provided JSON
SAMPLE_DATA = [
    {"region": "apac", "service": "catalog", "latency_ms": 195.09, "uptime_pct": 97.895, "timestamp": 20250301},
    {"region": "apac", "service": "checkout", "latency_ms": 195.24, "uptime_pct": 98.173, "timestamp": 20250302},
    {"region": "apac", "service": "payments", "latency_ms": 179.22, "uptime_pct": 97.68, "timestamp": 20250303},
    {"region": "apac", "service": "recommendations", "latency_ms": 132.22, "uptime_pct": 98.523, "timestamp": 20250304},
    {"region": "apac", "service": "payments", "latency_ms": 202.55, "uptime_pct": 97.403, "timestamp": 20250305},
    {"region": "apac", "service": "catalog", "latency_ms": 162.14, "uptime_pct": 98.187, "timestamp": 20250306},
    {"region": "apac", "service": "payments", "latency_ms": 189.19, "uptime_pct": 98.121, "timestamp": 20250307},
    {"region": "apac", "service": "payments", "latency_ms": 184.87, "uptime_pct": 99.187, "timestamp": 20250308},
    {"region": "apac", "service": "recommendations", "latency_ms": 139.03, "uptime_pct": 99.219, "timestamp": 20250309},
    {"region": "apac", "service": "checkout", "latency_ms": 147.57, "uptime_pct": 97.577, "timestamp": 20250310},
    {"region": "apac", "service": "analytics", "latency_ms": 129.86, "uptime_pct": 98.742, "timestamp": 20250311},
    {"region": "apac", "service": "payments", "latency_ms": 164.57, "uptime_pct": 99.339, "timestamp": 20250312},
    {"region": "emea", "service": "payments", "latency_ms": 122.71, "uptime_pct": 97.533, "timestamp": 20250301},
    {"region": "emea", "service": "checkout", "latency_ms": 154.63, "uptime_pct": 98.736, "timestamp": 20250302},
    {"region": "emea", "service": "support", "latency_ms": 226.6, "uptime_pct": 97.803, "timestamp": 20250303},
    {"region": "emea", "service": "checkout", "latency_ms": 176.9, "uptime_pct": 98.641, "timestamp": 20250304},
    {"region": "emea", "service": "checkout", "latency_ms": 197.09, "uptime_pct": 97.298, "timestamp": 20250305},
    {"region": "emea", "service": "catalog", "latency_ms": 180.61, "uptime_pct": 99.238, "timestamp": 20250306},
    {"region": "emea", "service": "payments", "latency_ms": 106.19, "uptime_pct": 99.085, "timestamp": 20250307},
    {"region": "emea", "service": "analytics", "latency_ms": 174.88, "uptime_pct": 98.446, "timestamp": 20250308},
    {"region": "emea", "service": "catalog", "latency_ms": 182.73, "uptime_pct": 98.383, "timestamp": 20250309},
    {"region": "emea", "service": "checkout", "latency_ms": 137.64, "uptime_pct": 97.432, "timestamp": 20250310},
    {"region": "emea", "service": "support", "latency_ms": 139.15, "uptime_pct": 98.843, "timestamp": 20250311},
    {"region": "emea", "service": "analytics", "latency_ms": 191.43, "uptime_pct": 98.267, "timestamp": 20250312},
    {"region": "amer", "service": "checkout", "latency_ms": 151.11, "uptime_pct": 97.361, "timestamp": 20250301},
    {"region": "amer", "service": "catalog", "latency_ms": 123.89, "uptime_pct": 99.127, "timestamp": 20250302},
    {"region": "amer", "service": "payments", "latency_ms": 117.05, "uptime_pct": 98.457, "timestamp": 20250303},
    {"region": "amer", "service": "catalog", "latency_ms": 126.57, "uptime_pct": 98.617, "timestamp": 20250304},
    {"region": "amer", "service": "recommendations", "latency_ms": 134.21, "uptime_pct": 98.947, "timestamp": 20250305},
    {"region": "amer", "service": "catalog", "latency_ms": 235.33, "uptime_pct": 98.696, "timestamp": 20250306},
    {"region": "amer", "service": "catalog", "latency_ms": 150.01, "uptime_pct": 98.007, "timestamp": 20250307},
    {"region": "amer", "service": "checkout", "latency_ms": 155.11, "uptime_pct": 98.534, "timestamp": 20250308},
    {"region": "amer", "service": "recommendations", "latency_ms": 154, "uptime_pct": 97.962, "timestamp": 20250309},
    {"region": "amer", "service": "payments", "latency_ms": 178.81, "uptime_pct": 98.552, "timestamp": 20250310},
    {"region": "amer", "service": "recommendations", "latency_ms": 150.03, "uptime_pct": 97.508, "timestamp": 20250311},
    {"region": "amer", "service": "recommendations", "latency_ms": 170.54, "uptime_pct": 99.173, "timestamp": 20250312}
]

def calculate_percentile(data: List[float], percentile: float) -> float:
    """Calculate percentile from list of values"""
    if not data:
        return 0.0
    
    sorted_data = sorted(data)
    index = (percentile / 100) * (len(sorted_data) - 1)
    
    if index.is_integer():
        return sorted_data[int(index)]
    else:
        lower = sorted_data[math.floor(index)]
        upper = sorted_data[math.ceil(index)]
        return lower + (upper - lower) * (index - math.floor(index))

def add_cors_headers(response):
    """Add CORS headers to response"""
    response['headers'] = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    return response

def main(request):
    try:
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            response = {
                'statusCode': 200,
                'body': ''
            }
            return add_cors_headers(response)
        
        if request.method != 'POST':
            response = {
                'statusCode': 405,
                'body': json.dumps({'error': 'Method not allowed'})
            }
            return add_cors_headers(response)
        
        # Parse request body
        body = request.body
        if isinstance(body, str):
            body = json.loads(body)
        
        regions = body.get('regions', [])
        threshold_ms = body.get('threshold_ms', 180)
        
        if not regions:
            response = {
                'statusCode': 400,
                'body': json.dumps({'error': 'No regions specified'})
            }
            return add_cors_headers(response)
        
        results = {}
        
        for region in regions:
            # Filter data for the current region
            region_data = [item for item in SAMPLE_DATA if item['region'] == region]
            
            if not region_data:
                results[region] = {
                    'avg_latency': 0,
                    'p95_latency': 0,
                    'avg_uptime': 0,
                    'breaches': 0
                }
                continue
            
            # Extract latencies and uptime percentages
            latencies = [item['latency_ms'] for item in region_data]
            uptimes = [item['uptime_pct'] for item in region_data]
            
            # Calculate metrics
            avg_latency = sum(latencies) / len(latencies)
            p95_latency = calculate_percentile(latencies, 95)
            avg_uptime = sum(uptimes) / len(uptimes)
            breaches = sum(1 for latency in latencies if latency > threshold_ms)
            
            results[region] = {
                'avg_latency': round(avg_latency, 2),
                'p95_latency': round(p95_latency, 2),
                'avg_uptime': round(avg_uptime, 2),
                'breaches': breaches
            }
        
        response = {
            'statusCode': 200,
            'body': json.dumps(results)
        }
        return add_cors_headers(response)
    
    except Exception as e:
        response = {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
        return add_cors_headers(response)
