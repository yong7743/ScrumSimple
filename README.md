# team-status



## How to use it

目前Esri的ArcGIS Earth在使用该工具进行团队组员状态跟踪。



### Login

使用GitHub账号登陆，会要求github的公开数据访问权限。

登陆之后，页面右上角会

### Home tab

- 可以填写自己今天做的事情
- 查看team member每天做的事情



### Profile tab

- 查看自己的基本信息
- 查看自己的所有工作日志



### Scrums tab

- 能够查看某一段时间的日志



### Users tab

- 展示当前所有组员

  ​

### Weekly plan tab

- 组员在每周一的周会时，可以填写当周的计划，这样在周会的时候，可以对着每周计划汇报工作



### About tab

- Some help information



## Deploy

### Install dependences

pip install -r requirments/dev.txt

### Init Database

python manage.py db init
python manage.py db migrate -m "init"
python manage.py db upgrade

first runshell then keyin 
db.drop_all()
db.create_all() 
to init the database

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



### Next

- More choices for authorization
- Associate github issues and commit



## Note

非商用软件，由Flask Web开发 - 基于Python的Web应用开发实战 一书中附带的代码修改而来。