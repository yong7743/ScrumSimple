# Scrum Simple

目前Esri的ArcGIS Earth在使用该工具进行团队组员作为辅助的scrum工具，希望能将整个团队开发过程系统化流程化。

Esri's ArcGIS Earth is currently using this tool as a team scrum tool supporting the team, hoping to systematize the entire team development process.


## 目前的界面 

首页

http://localhost:5000/

<img src="https://user-images.githubusercontent.com/5510943/34347653-2511db5c-ea40-11e7-8563-a702b8fa07c4.png" alt="Drawing" width="480"/>

点击导航到其他页面

<img src="https://user-images.githubusercontent.com/5510943/34347656-2a609238-ea40-11e7-9bc3-9ff8a8c7b0c1.png" alt="Drawing" width="480"/>


每天需要写自己做的事情，这部分会集中在这个页面显示。

http://localhost:5000/reports

<img src="https://user-images.githubusercontent.com/5510943/34347662-2f5d927c-ea40-11e7-8cbf-174d532e19f7.png" alt="Drawing" width="480"/>

组员的用户页面：

http://localhost:5000/user/Ben%20Tan

<img src="https://user-images.githubusercontent.com/5510943/34347665-38566426-ea40-11e7-8341-c8b73d417be9.png" alt="Drawing" width="480"/>

Earth组每周需要把每一个组员的工作内容汇报给其他相关团队。这个页面会根据组员每天填写的内容生成表格，便于邮件发送。

http://localhost:5000/scrum

<img src="https://user-images.githubusercontent.com/5510943/34347670-3d05dda8-ea40-11e7-83d1-cfd386bd8c04.png" alt="Drawing" width="480"/>

Earth组每周一的时候还会计划本周的工作，这个版块的UI还在开发中，暂无截图。


## How to use it


### Login

使用GitHub账号登陆，会要求github的公开数据访问权限。

登陆之后，页面右上角会显示你的头像。


### Reports tab

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



## 部署

### 安装依赖 Install dependences

pip install -r requirments/dev.txt

### 初始化数据库 Init Database

python manage.py db init
python manage.py db migrate -m "init"
python manage.py db upgrade

first runshell then keyin 
db.drop_all()
db.create_all() 
to init the database

### 运行 Run

create run and run shell in pycharm

runshell
script: C:\Projects\team-status\manage.py
parameters: shell
env: DEV_DATABASE_URL=sqlite:///c:/projects/team-status/data/data-dev.sqlite;PYTHONUNBUFFERED=1

run
script: C:\Projects\team-status\manage.py
parameters: runserver
env: DEV_DATABASE_URL=sqlite:///c:/projects/team-status/data/data-dev.sqlite;PYTHONUNBUFFERED=1


### 实验性质功能

#### 词云统计

- [scrum word cloud wiki](https://github.com/bentan2013/ScrumSimple/wiki/Scrum-Word-Cloud)

<img src="https://camo.githubusercontent.com/bf03f284e6c89e56b52e7367898f4f489e2b811f/687474703a2f2f6f72343568756e69312e626b742e636c6f7564646e2e636f6d2f31382d332d31342f33323039353930362e6a7067" alt="Drawing" width="480"/>



### 待办事项Next

- 用户名密码的登陆方式，以减少github验证的网络延时。More choices for authorization
- Associate github issues and commit



## Note

非商用软件，由Flask Web开发 - 基于Python的Web应用开发实战 一书中附带的代码修改而来。



各部分源码地址：
- [home page](https://github.com/BlackrockDigital/startbootstrap-stylish-portfolio)
- [Main](https://github.com/miguelgrinberg/flasky)
