import csv
import urllib.request
import urllib.parse
import json
import time

def check_ips(filename, api_key):
    base_url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Key": api_key,
        "Accept": "application/json"
    }
    results = []

    with open(filename, newline='') as csvfile:
        ip_reader = csv.reader(csvfile)
        for row in ip_reader:
            ip = row[0]
            params = {
                "ipAddress": ip,
                "maxAgeInDays": "90",
                "verbose": "true"
            }
            query_string = urllib.parse.urlencode(params)
            req_url = f"{base_url}?{query_string}"
            request = urllib.request.Request(req_url, headers=headers)
            
            try:
                with urllib.request.urlopen(request) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode())
                        score = data['data']['abuseConfidenceScore']
                        results.append((ip, score, data['data']))
                        print(f"Checked IP {ip}: Abuse Confidence Score = {score}")
                    else:
                        print(f"Failed to retrieve data for IP {ip}: Status code = {response.status}")
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    print(f"Rate limit exceeded. Pausing for 60 seconds.")
                    time.sleep(60)  # Pause for 60 seconds before retrying
                    continue  # Optionally add logic to retry the request
                print(f"HTTP error for IP {ip}: {e.code}")
            except urllib.error.URLError as e:
                print(f"URL error for IP {ip}: {e.reason}")
            time.sleep(1)  # Sleep for 1 second between requests to avoid hitting rate limit

    results.sort(key=lambda x: x[1], reverse=True)
    return results

# Example usage
api_key = "API KEY HERE"  # Replace with your actual API key
filename = "list.csv"  # CSV file containing IPs, each IP should be in a new row
results = check_ips(filename, api_key)
for ip, score, data in results:
    print(f"IP: {ip}, Abuse Confidence Score: {score}, Data: {data}")
