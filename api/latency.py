from http.server import BaseHTTPRequestHandler
import json
import math

DATA = [
  {"region": "apac", "service": "support", "latency_ms": 135.42, "uptime_pct": 98.355, "timestamp": 20250301},
  {"region": "apac", "service": "payments", "latency_ms": 110.18, "uptime_pct": 99.143, "timestamp": 20250302},
  {"region": "apac", "service": "analytics", "latency_ms": 127.58, "uptime_pct": 99.481, "timestamp": 20250303},
  {"region": "apac", "service": "analytics", "latency_ms": 200.71, "uptime_pct": 97.943, "timestamp": 20250304},
  {"region": "apac", "service": "checkout", "latency_ms": 123.16, "uptime_pct": 97.787, "timestamp": 20250305},
  {"region": "apac", "service": "payments", "latency_ms": 185.62, "uptime_pct": 98.5, "timestamp": 20250306},
  {"region": "apac", "service": "payments", "latency_ms": 200.95, "uptime_pct": 98.413, "timestamp": 20250307},
  {"region": "apac", "service": "payments", "latency_ms": 193.71, "uptime_pct": 99.123, "timestamp": 20250308},
  {"region": "apac", "service": "support", "latency_ms": 155.29, "uptime_pct": 97.183, "timestamp": 20250309},
  {"region": "apac", "service": "catalog", "latency_ms": 148.19, "uptime_pct": 97.778, "timestamp": 20250310},
  {"region": "apac", "service": "checkout", "latency_ms": 138.21, "uptime_pct": 97.23, "timestamp": 20250311},
  {"region": "apac", "service": "catalog", "latency_ms": 200.86, "uptime_pct": 99.211, "timestamp": 20250312},
  {"region": "emea", "service": "support", "latency_ms": 144.44, "uptime_pct": 98.696, "timestamp": 20250301},
  {"region": "emea", "service": "checkout", "latency_ms": 198.26, "uptime_pct": 98.928, "timestamp": 20250302},
  {"region": "emea", "service": "catalog", "latency_ms": 197.47, "uptime_pct": 98.517, "timestamp": 20250303},
  {"region": "emea", "service": "checkout", "latency_ms": 120.38, "uptime_pct": 97.607, "timestamp": 20250304},
  {"region": "emea", "service": "payments", "latency_ms": 208.15, "uptime_pct": 99.28, "timestamp": 20250305},
  {"region": "emea", "service": "analytics", "latency_ms": 137.79, "uptime_pct": 97.162, "timestamp": 20250306},
  {"region": "emea", "service": "analytics", "latency_ms": 211.59, "uptime_pct": 97.371, "timestamp": 20250307},
  {"region": "emea", "service": "analytics", "latency_ms": 171.7, "uptime_pct": 97.525, "timestamp": 20250308},
  {"region": "emea", "service": "catalog", "latency_ms": 123.6, "uptime_pct": 98.469, "timestamp": 20250309},
  {"region": "emea", "service": "support", "latency_ms": 134.46, "uptime_pct": 97.133, "timestamp": 20250310},
  {"region": "emea", "service": "checkout", "latency_ms": 145.23, "uptime_pct": 97.36, "timestamp": 20250311},
  {"region": "emea", "service": "payments", "latency_ms": 125.77, "uptime_pct": 97.673, "timestamp": 20250312},
  {"region": "amer", "service": "recommendations", "latency_ms": 212.91, "uptime_pct": 97.543, "timestamp": 20250301},
  {"region": "amer", "service": "support", "latency_ms": 212.9, "uptime_pct": 97.693, "timestamp": 20250302},
  {"region": "amer", "service": "checkout", "latency_ms": 126.61, "uptime_pct": 97.242, "timestamp": 20250303},
  {"region": "amer", "service": "payments", "latency_ms": 217.7, "uptime_pct": 98.433, "timestamp": 20250304},
  {"region": "amer", "service": "support", "latency_ms": 111.29, "uptime_pct": 98.565, "timestamp": 20250305},
  {"region": "amer", "service": "checkout", "latency_ms": 230.94, "uptime_pct": 97.109, "timestamp": 20250306},
  {"region": "amer", "service": "recommendations", "latency_ms": 175.15, "uptime_pct": 98.995, "timestamp": 20250307},
  {"region": "amer", "service": "recommendations", "latency_ms": 155.38, "uptime_pct": 98.571, "timestamp": 20250308},
  {"region": "amer", "service": "checkout", "latency_ms": 150.25, "uptime_pct": 98.062, "timestamp": 20250309},
  {"region": "amer", "service": "payments", "latency_ms": 179.33, "uptime_pct": 97.434, "timestamp": 20250310},
  {"region": "amer", "service": "support", "latency_ms": 108.64, "uptime_pct": 99.151, "timestamp": 20250311},
  {"region": "amer", "service": "support", "latency_ms": 219.91, "uptime_pct": 98.07, "timestamp": 20250312}
]


def percentile(values, p):
    if not values:
        return 0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    k = (p / 100.0) * (n - 1)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    d0 = sorted_vals[f] * (c - k)
    d1 = sorted_vals[c] * (k - f)
    return d0 + d1


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            req = json.loads(body)

            regions = req.get("regions", [])
            threshold_ms = req.get("threshold_ms", 180)

            results = {}
            # Flatten data for easier filtering
            # But the logic below filters from DATA global nicely.
            
            for region in regions:
                records = [d for d in DATA if d["region"] == region]
                if not records:
                    results[region] = {
                        "avg_latency": 0,
                        "p95_latency": 0,
                        "avg_uptime": 0,
                        "breaches": 0
                    }
                    continue

                latencies = [r["latency_ms"] for r in records]
                uptimes = [r["uptime_pct"] for r in records]

                avg_latency = round(sum(latencies) / len(latencies), 2)
                p95_latency = round(percentile(latencies, 95), 2)
                avg_uptime = round(sum(uptimes) / len(uptimes), 3)
                breaches = sum(1 for l in latencies if l > threshold_ms)

                results[region] = {
                    "avg_latency": avg_latency,
                    "p95_latency": p95_latency,
                    "avg_uptime": avg_uptime,
                    "breaches": breaches
                }
            
            response_body = json.dumps(results)
            status_code = 200

        except Exception as e:
            status_code = 400
            response_body = json.dumps({"error": str(e)})

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_body.encode())

