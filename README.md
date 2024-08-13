# Emarketing backend

FastAPI app that can be used to authenticate users with their Google accounts and send HTML mails to up to 500 people.

### [Front end](https://github.com/qara-qurt/email_marketing_service)

## Features
* Oauth2 authentication with Google
* Server side cookies stored in Redis
* Email sending to up to 500 recipients
* Multiple recipient lists


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

### Configure databases
Update 'config/__init __.py'
```python
# config.__init__.py
DB_NAME=os.getenv('DB_NAME')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_URL = 'postgresql://localhost:5432'


REDIS_URL='redis://localhost:6379'
```
### Credentials
Create project at https://console.cloud.google.com and get OAuth credentials. Place them into config directory
```
emarketing_backend/src/config/client_secret.json
```

## Run the app
```commandline
cd src
uvicorn app:app
```
