from urllib.request import ProxyHandler, build_opener, install_opener

from .models import Reservations
from .serializers import ReservationsSerializer, AllReservationsSerializer, UpdateReservationSerializer, \
    BookRoomSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
import json
from urllib import request
import time
from django.core.exceptions import ObjectDoesNotExist
import requests

ip_facilities = "http://127.0.0.1:8095"
get_all_facilities_path = '/get-all-facilities'
add_facility_reservation_path = '/add-facility-reservation'
cancel_facility_path = '/cancel-facility-reservation'
get_all_rooms_path = '/get-all-rooms'

proxy_support = ProxyHandler({"http":"http://127.0.0.1:8000"})
opener = build_opener(proxy_support)
install_opener(opener)

def get_facilities(facilities):
    url = ip_facilities + get_all_facilities_path
    serialized_data = request.urlopen(url)
    data = json.loads(serialized_data.read())
    if not bool(facilities):
        return True
    else:
        for facility in data:
            if facility["type"] == facilities:
                if facility["isActive"]:
                    return True
        return False


def facility_add_delete(path, start_date, end_date, rooms, facility):
    url = ip_facilities + path
    start_date = (time.mktime(start_date.timetuple()))
    end_date = (time.mktime(end_date.timetuple()))
    data = {
        "start_date": start_date,
        "end_date": end_date,
        "room_id": rooms,
        "facility_type": facility
    }
    response = requests.post(url, json=data)
    resp_dict = json.loads(response.text)
    try:
        if resp_dict["status"] == "success":
            return True
    except KeyError:
        return False


def get_rooms(capacity):
    url = ip_facilities + get_all_rooms_path
    serialized_data = request.urlopen(url)
    data = json.loads(serialized_data.read())
    room_number = []
    for room in data:
        if room["number"]:
            if room["capacity"] == capacity:
                room_number.append(room["number"])
    if room_number:
        return room_number
    else:
        return False


def format_time(input_data):
    t = datetime.strptime(input_data, "%Y-%m-%d %H:%M")
    s = t.strftime('%Y-%m-%d %H:%M')
    tail = s[-2:]
    f = round(float(tail), -1)
    temp = "%i" % f
    formatted_date = datetime.strptime("%s%s" % (s[:-2], temp), "%Y-%m-%d %H:%M")
    return formatted_date


def get_strptime(date):
    return datetime.strptime(date, '%Y-%m-%d %H:%M')


def is_available(serializer):
    rooms = get_rooms(serializer.data["people"])
    for reservation in Reservations.objects.all():
        check_in_date = get_strptime(reservation.check_in.strftime('%Y-%m-%d %H:%M'))
        check_out_date = get_strptime(reservation.check_out.strftime('%Y-%m-%d %H:%M'))
        proposed_date_in = get_strptime(serializer.data["check_in"])
        proposed_date_out = get_strptime(serializer.data["check_out"])
        if proposed_date_in >= proposed_date_out:
            return False
        if rooms:
            try:
                if check_in_date <= proposed_date_in <= check_out_date:
                    rooms.remove(int(reservation.room))
                if check_in_date <= proposed_date_out <= check_out_date:
                    rooms.remove(int(reservation.room))
            except ValueError:
                pass
    if rooms:
        return rooms[0]
    else:
        return False


@api_view(['GET'])
def get_bookings(get_bookings_request):
    try:
        reservations = Reservations.objects.all().order_by("check_in")
        serializer = ReservationsSerializer(reservations, many=True)
        return Response(serializer.data)
    except ValueError:
        return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR})


@api_view(['POST'])
def room_booking(booking_request):
    serializer = AllReservationsSerializer(data=booking_request.data, partial=True)
    if serializer.is_valid():
        facility_reservation = True
        rooms = is_available(serializer)
        if not rooms:
            return Response({"status": 200, "result": False}, status=200)
        serializer_copy = serializer.data.copy()
        serializer_copy["check_in"] = format_time(serializer_copy["check_in"])
        serializer_copy["check_out"] = format_time(serializer_copy["check_out"])
        try:
            facility = booking_request.data["facilities"]
            facility_reservation = facility_add_delete(add_facility_reservation_path, serializer_copy["check_in"],
                                                       serializer_copy["check_out"], rooms, facility)
            if not facility_reservation:
                return Response({"status": 200, "result": False, "lack of facility": facility}, status=200)
            serializer_copy["facility_type"] = facility
        except KeyError:
            pass
        serializer_copy["room"] = rooms

        serializer = BookRoomSerializer(data=serializer_copy)
        if facility_reservation and serializer.is_valid():
            serializer.save()
            return Response({"status": 200, "result": True, "room": rooms}, status=200)
        else:
            return Response({"status": 200, "result": False, "lack of facility": facility}, status=200)
    else:
        return Response({"status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
def room_detail(room_detail_request, room_no, year, month, day):
    try:
        room_filter = Reservations.objects.filter(room=room_no, check_in__date=year + "-" + month + "-" + day)
        room = room_filter.get()
    except ObjectDoesNotExist:
        return Response({"status": 200, "result": False}, status=200)
    if room_detail_request.method == 'PUT':
        serializer = UpdateReservationSerializer(room, data=room_detail_request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": 200, "result": True}, status=200)
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)

    elif room_detail_request.method == 'DELETE':
        cancel_facility = True
        if room.facility_type != -1:
            cancel_facility = facility_add_delete(cancel_facility_path, room.check_in, room.check_out, room.room,
                                                  room.facility_type)
        if cancel_facility:
            room.delete()
            return Response({"status": status.HTTP_200_OK, "result": True})
        else:
            return Response({"status": status.HTTP_406_NOT_ACCEPTABLE, "result": False})
