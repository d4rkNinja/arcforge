# Architecture Proposal

Use microservices, Kafka, Redis, and MongoDB because they scale. Store prices as floating point. The API writes to the database and then publishes to Kafka. Retries continue until success. The queue is unlimited. Redis is the source of truth. Exactly-once delivery is guaranteed. Internal services trust each other. Backups run every night. Use active-active multi-region writes. Authorization is handled by the frontend and gateway. Deploy directly when coding is finished.
