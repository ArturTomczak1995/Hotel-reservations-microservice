# hotel-mikrorezerwacje
## Install Django:
* $ pip install django
## Install Django Rest Framework:
* $ pip install djangorestframework
* $ pip install requests
* $ django-request-logging
* $ python manage.py runserver 8000
### Server will run at:
```sh
http://127.0.0.1:8000/
```
# Docker:
## Download and run project:
* $ docker pull 221666/hotel_mikrousluga_rezerwacje_web
* $ docker run -p 8000:8000 -i -t 221666/hotel_mikrousluga_rezerwacje_web
### Check connection at:
```sh
http://localhost:8000/booking/api/all-rooms
```
