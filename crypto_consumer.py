# crypto_consumer.py
from kafka import KafkaConsumer
import psycopg2
import json

# Kafka consumer
consumer = KafkaConsumer(
    'cryptoPrices',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# PostgreSQL connection
conn = psycopg2.connect(
    dbname='cryptodb',
    user='crypto',
    password='crypto123',
    host='localhost',
    port=5432
)

cur = conn.cursor()

print("Kafka consumer started. Waiting for messages...")

for msg in consumer:
    data = msg.value

    symbol = data['symbol']
    timestamp = data['timestamp']
    price = data['price']

    cur.execute(
        """
        INSERT INTO crypto_prices (symbol, timestamp, price)
        VALUES (%s, %s, %s)
        """,
        (symbol, timestamp, price)
    )

    conn.commit()
    print(f"Inserted: {symbol} @ {timestamp} = {price}")

