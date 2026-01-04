import requests
import time
import json
from kafka import KafkaProducer

# Set up Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Function to fetch crypto price
def get_price(symbol='BTC', currency='USD'):
    url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms={currency}"
    response = requests.get(url)
    return response.json()

# Main loop to send data to Kafka
while True:
    for coin in ['BTC', 'ETH']:
        price_data = get_price(coin)
        record = {
            'symbol': coin,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'price': price_data['USD']
        }
        producer.send('cryptoPrices', value=record)
        print(f"Sent: {record}")
    
    # Wait 2 minutes before sending next batch
    time.sleep(120)

