from django.urls import path, re_path
from . import views

from . import views

app_name = "booking"

urlpatterns = [
    re_path(r'^api/getBookings', views.get_bookings),
    re_path(r'^api/bookRoom', views.room_booking),
    re_path(r'^api/roomDetails/room=(?P<room_no>[0-9]+)\+date=(?P<year>[0-9]+)-(?P<month>[0-9]+)-(?P<day>[0-9]+)', views.room_detail),
    re_path(r'^api/all-rooms', views.all_rooms),

]