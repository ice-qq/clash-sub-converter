
## docker compose
```
version: '3.8'

services:
  clash-sub-converter:
    image: clash-sub-converter:latest
    ports:
      - "0.0.0.0:5000:5000"
    volumes:
      - ./config:/app/config
```