# team-status

pip install -r requirments/common.txt

python run.py runserver


---

users
- id
- username
- password
- role


reports
- id
- user_id
- date
- today_report
- position(optional)


Notes:

create run and run shell in pycharm

runshell
script: C:\Projects\team-status\manage.py
parameters: shell
env: DEV_DATABASE_URL=sqlite:///c:/projects/team-status/data/data-dev.sqlite;PYTHONUNBUFFERED=1

run
script: C:\Projects\team-status\manage.py
parameters: runserver
env: DEV_DATABASE_URL=sqlite:///c:/projects/team-status/data/data-dev.sqlite;PYTHONUNBUFFERED=1


python manage.py db init
python manage.py db migrate -m "init"
python manage.py db upgrade

first runshell then keyin 
db.drop_all()
db.create_all() 
to init the database


数据库迁移
数据导出
权限与角色
其他用户数据浏览