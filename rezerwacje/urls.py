from django.urls import path, re_path
from . import views

from . import views

app_name = "booking"

urlpatterns = [
    re_path(r'^api/$', views.ReservationsLit.as_view()),
    re_path(r'^api/update$', views.ReservationsLit.as_view()),
    re_path(r'^api/getRoomsToClean/date=(?P<check_in_year>[0-9]+)-(?P<check_in_month>[0-9]+)-(?P<check_in_day>[0-9]+)', views.reservation_list),
    re_path(r'^api/getBookings', views.getBookings),
    re_path(r'^api/bookRoom', views.getBookings),
    re_path(r'^api/roomDetails/room=(?P<pk>[0-9]+)\+date=(?P<check_in_year>[0-9]+)-(?P<check_in_month>[0-9]+)-(?P<check_in_day>[0-9]+)', views.room_detail),

]