# Fully featured

Journaling + TODO + Notes + Glossary


```bash
git clone git@github.com:pedromadureira000/fully_featured.git
cd fully_featured
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp contrib/env-sample .env
psql postgres://username:pass@localhost:5432/postgres
postgres=# create database fully_featured;
postgres=# \q
python manage.py migrate
python manage.py createsuperuser
```

## django-extension commands
* generate admin
`
python manage.py admin_generator app_name
`

## Running celery
```
celery -A fully_featured worker -l INFO --pool=gevent --concurrency=8 --hostname=worker -E --queues=send_email
```

## Run server dev mode
```
ip addr show
python manage.py runserver <local-ip>:8000
```

## Nice commands
```
python manage.py shell_plus --print-sql --ipython
sudo systemctl start docker # docker might be off
```

## Header Authentication
* For clients to authenticate, the token key should be included in the Authorization HTTP header. The key should be prefixed by the string literal "Token", with whitespace separating the two strings. For example:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Get Auth Token

```
curl -X POST -d '
    {
        "email": "email@email.com",
        "password": "pass"
    }
    ' -H "Content-Type: application/json;" http://127.0.0.1:8000/api/user/gettoken
```

## Authenticated API calls
`
curl -X POST -d '{}' -H "Authorization: Token <your-token>" -H "Content-Type: application/json" http://127.0.0.1:8000/api_path
`

## Test View
* Get
`
curl -X GET -H "Authorization: Token <Token>" http://127.0.0.1:8000/test_view
`
* Post
`
curl -X POST -d '{"test_field": "right_field"}' -H "Authorization: Token <Token>" -H "Content-Type: application/json" http://127.0.0.1:8000/test_view
`
* Post with validation error
`
curl -X POST -d '{"test_field": "wrong_field"}' -H "Authorization: Token <Token>" -H "Content-Type: application/json" http://127.0.0.1:8000/test_view
`

## Create TODO
* 'completed' is optional.
``
curl -X POST -d '
    {
        "title": "Todo 01",
        "description": "THis is a nice todo",
        "completed": false
    }
    ' -H "Content-Type: application/json;" -H "Authorization: Token <token>" http://127.0.0.1:8000/todo_view
``
