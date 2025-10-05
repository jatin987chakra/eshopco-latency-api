from http.client import HTTPException
import json
import math
from typing import Dict, List, Optional

# Sample data - in production, this would come from a database
SAMPLE_DATA = {
    "emea": [
        {"latency_ms": 120, "status": "up"},
        {"latency_ms": 150, "status": "up"},
        {"latency_ms": 200, "status": "up"},
        {"latency_ms": 90, "status": "up"},
        {"latency_ms": 300, "status": "down"},
        {"latency_ms": 160, "status": "up"},
        {"latency_ms": 180, "status": "up"},
        {"latency_ms": 220, "status": "up"},
        {"latency_ms": 110, "status": "up"},
        {"latency_ms": 190, "status": "up"}
    ],
    "apac": [
        {"latency_ms": 140, "status": "up"},
        {"latency_ms": 170, "status": "up"},
        {"latency_ms": 210, "status": "up"},
        {"latency_ms": 95, "status": "up"},
        {"latency_ms": 250, "status": "down"},
        {"latency_ms": 165, "status": "up"},
        {"latency_ms": 195, "status": "up"},
        {"latency_ms": 230, "status": "up"},
        {"latency_ms": 125, "status": "up"},
        {"latency_ms": 205, "status": "up"}
    ],
    "nam": [
        {"latency_ms": 100, "status": "up"},
        {"latency_ms": 130, "status": "up"},
        {"latency_ms": 180, "status": "up"},
        {"latency_ms": 80, "status": "up"},
        {"latency_ms": 280, "status": "down"},
        {"latency_ms": 140, "status": "up"},
        {"latency_ms": 160, "status": "up"},
        {"latency_ms": 200, "status": "up"},
        {"latency_ms": 105, "status": "up"},
        {"latency_ms": 175, "status": "up"}
    ]
}

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

def handler(request):
    try:
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            }
        
        if request.method != 'POST':
            return {
                'statusCode': 405,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Method not allowed'})
            }
        
        # Parse request body
        body = request.body
        if isinstance(body, str):
            body = json.loads(body)
        
        regions = body.get('regions', [])
        threshold_ms = body.get('threshold_ms', 180)
        
        if not regions:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'No regions specified'})
            }
        
        results = {}
        
        for region in regions:
            if region not in SAMPLE_DATA:
                continue
                
            region_data = SAMPLE_DATA[region]
            
            # Filter only "up" status records for latency calculations
            up_records = [r for r in region_data if r['status'] == 'up']
            latencies = [r['latency_ms'] for r in up_records]
            all_latencies = [r['latency_ms'] for r in region_data]
            
            if not latencies:
                results[region] = {
                    'avg_latency': 0,
                    'p95_latency': 0,
                    'avg_uptime': 0,
                    'breaches': 0
                }
                continue
            
            # Calculate metrics
            avg_latency = sum(latencies) / len(latencies)
            p95_latency = calculate_percentile(latencies, 95)
            avg_uptime = len(up_records) / len(region_data)
            breaches = sum(1 for latency in all_latencies if latency > threshold_ms)
            
            results[region] = {
                'avg_latency': round(avg_latency, 2),
                'p95_latency': round(p95_latency, 2),
                'avg_uptime': round(avg_uptime, 2),
                'breaches': breaches
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(results)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
