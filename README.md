# team-status

## Quick start

pip install -r requirments/dev.txt

python run.py --host=0.0.0.0

---

## Details

### Run

create run and run shell in pycharm

runshell
script: C:\Projects\team-status\manage.py
parameters: shell
env: DEV_DATABASE_URL=sqlite:///c:/projects/team-status/data/data-dev.sqlite;PYTHONUNBUFFERED=1

run
script: C:\Projects\team-status\manage.py
parameters: runserver
env: DEV_DATABASE_URL=sqlite:///c:/projects/team-status/data/data-dev.sqlite;PYTHONUNBUFFERED=1

### Init Database

```
python manage.py db init
python manage.py db migrate -m "init"
python manage.py db upgrade
python manage.py gtd
```

first runshell then keyin 

```
db.drop_all()
db.create_all() 
```

to init the database



### Next

- More choices for authorization
- Associate github issues and commit