# Consulting company webapp
Simple CRUD application implementing business process of submitting case to consulting company and assigning it to employee:
![](https://github.com/xbound/consulting-webapp/blob/master/bpmn_diagram.svg) 
![](https://github.com/xbound/consulting-webapp/blob/master/recording.gif) 
### Requirements 
* Python 3
* pip
* Django 2.0
### Setup 
Clone repository. Install requirements:
```shell
$ pip install -r requirements.txt
```
Apply migrations:
```shell
$ python manage.py migrate
```
Create admin user:
```shell
$ python manage.py createsuperuser
```
Run server:
```shell
$ python manage.py runserver
```
Log in to the admin page as admin user and create users of type `Employee` and `Manager`.

Login to app with user credentials of `Manager` or `Employee` on [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard).
