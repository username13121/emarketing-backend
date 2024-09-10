# Emarketing backend

FastAPI app that can be used to authenticate users with their Google accounts and send email using gmail.

### [Front end](https://github.com/qara-qurt/email_marketing_service)

## Features
- Google Oauth2 authentication
- Redis server side session with custom middleware
- Multiple recipient lists stored in PostgreSQL
- Connection to PostgreSQL with SQL Alchemy and asyncpg
- Asynchronous architecture with async/await


## Prerequisites
* [Python](https://python.org)
* [PostgreSQL](https://postgresql.org)
* [Redis](https://redis.io)


## Installation:

### Clone the repository

```commandline
git clone https://github.com/username13121/emarketing-backend.git
cd emarketing-backend
```

### Create a Virtual Environment

```commandline
python -m venv venv
venv/Scripts/activate
```

### Install dependencies
```commandline
pip install -r requirements.txt
```

### Credentials
Create project at https://console.cloud.google.com, add your callback URL and get OAuth credentials.
It should contain client_id and client_secret. Copy and paste those values into ".env" file.

### Configuration
Create ".env" file in the project root and fill all the data
```dotenv
DB_NAME=
DB_USER=postgres
DB_PASS=
DB_HOST=localhost
DB_PORT=5432

redis_url=redis://localhost:6379

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```


## Run the app
```commandline
uvicorn src.main:app
```

## Documentation
http://localhost:8000/docs
