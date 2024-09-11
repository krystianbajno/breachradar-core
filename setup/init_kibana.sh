#!/bin/bash
set -e

until curl -s -u elastic:$ELASTIC_PASSWORD "http://localhost:9200/_cluster/health" | grep -q '"status":"green"'; do
  echo "Waiting for Elasticsearch to start..."
  sleep 10
done

echo "Elasticsearch is up. Creating service account and API key..."

curl -X POST "localhost:9200/_security/service/your-service-account/_create" -H "Content-Type: application/json" -u elastic:$ELASTIC_PASSWORD -d '{
  "metadata": {
    "description": "Service account for Kibana"
  },
  "roles": ["kibana_system"]
}'

response=$(curl -X POST "localhost:9200/_security/api_key" -H "Content-Type: application/json" -u elastic:$ELASTIC_PASSWORD -d '{
  "name": "kibana-api-key",
  "role_descriptors": {
    "kibana_system": {
      "cluster": ["all"],
      "index": [
        {
          "names": ["*"],
          "privileges": ["all"]
        }
      ]
    }
  }
}')

api_key=$(echo $response | jq -r '.api_key')

echo "ELASTIC_API_KEY=${api_key}" > /usr/share/kibana/elastic_api_key.env

echo "Service account and API key created."