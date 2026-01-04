# Crypto Dashboard

Small pipeline that streams BTC and ETH spot prices into Kafka, stores them in Postgres, and runs a quick linear regression to predict the next-minute price. Designed to be Grafana-friendly for dashboards and alerts.

---

## Stack

- Kafka + Zookeeper for streaming
- Postgres for storage (schema auto-seeded from `config/init.sql`)
- Python workers:
  - `crypto_producer.py` pulls prices from CryptoCompare and publishes to Kafka
  - `crypto_consumer.py` reads Kafka messages and writes to Postgres
  - `crypto_prediction.py` trains a short-horizon linear regression on the last 30 minutes and writes predictions to Postgres
- Grafana for visualization

---

## Prerequisites

- Docker and Docker Compose (for Kafka/Postgres/Grafana)
- Python 3.11+ with `pip` (for the workers)
- Network access to `min-api.cryptocompare.com`

Install Python deps:

```bash
pip install -r requirements.txt
```

---

## Run the stack

1) Start infrastructure (Kafka, Postgres, Grafana):

```bash
docker-compose up -d
```

2) Start the producer (fetches prices every 2 minutes):

```bash
python crypto_producer.py
```

3) Start the consumer (persists prices into Postgres):

```bash
python crypto_consumer.py
```

4) Run predictions (fits per-symbol linear regression on last 30 minutes and writes next-minute forecast):

```bash
python crypto_prediction.py
```

Tip: run the producer and consumer continuously (tmux/systemd). The prediction script can be run on a schedule (e.g., cron) or looped.

---

## Database schema

Seeded automatically when Postgres starts via `config/init.sql`:

- `crypto_prices(symbol text, timestamp timestamp, price float)`
- `crypto_prediction(symbol text, timestamp timestamp, predicted_price float)`

Credentials used by the workers: user `crypto` / password `crypto123` against database `cryptodb` on `localhost:5432`.

---

## Grafana

Grafana listens on `localhost:3000` (admin/admin by default). Add Postgres as a data source pointing to `cryptodb` and use queries like:

**BTC time-series**

```sql
SELECT $__time(timestamp) AS time, price AS value
FROM crypto_prices
WHERE symbol = 'BTC'
ORDER BY timestamp;
```

**Daily high & low (last 24h)**

```sql
SELECT symbol || ' high_24h' AS metric, MAX(price) AS value
FROM crypto_prices
WHERE timestamp >= NOW() - INTERVAL '24 HOURS'
GROUP BY symbol

UNION

SELECT symbol || ' low_24h' AS metric, MIN(price) AS value
FROM crypto_prices
WHERE timestamp >= NOW() - INTERVAL '24 HOURS'
GROUP BY symbol;
```

**Percent change (last 24h)**

```sql
WITH changes AS (
   SELECT symbol,
             (MAX(price) - MIN(price)) / NULLIF(MIN(price), 0) * 100 AS percent_change
   FROM crypto_prices
   WHERE timestamp >= NOW() - INTERVAL '24 HOURS'
   GROUP BY symbol
)
SELECT symbol AS metric, ROUND(percent_change::numeric, 2) AS value
FROM changes;
```

**Predicted BTC prices**

```sql
SELECT $__time(timestamp) AS time, predicted_price AS value
FROM crypto_prediction
WHERE symbol = 'BTC';
```
