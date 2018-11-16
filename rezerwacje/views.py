from .models import Reservations
from .serializers import ReservationsSerializer, AllReservationsSerializer, UpdateReservationSerializer
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
import json
from urllib import request
import time
import requests

ip_facilities = "http://127.0.0.1:8095"


def get_facilities(facilities):
    url = ip_facilities + '/get-all-facilities'
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


def reserve_facility(facility, start_date, end_date):
    url = ip_facilities + '/add-facility-reservation'
    start_date = (time.mktime(start_date.timetuple()))
    end_date = (time.mktime(end_date.timetuple()))
    data = {
        "start_date": start_date,
        "end_date": end_date,
        "room_id": 1,
        "facility_type": facility
    }
    response = requests.post(url, json=data)
    resp_dict = json.loads(response.text)
    if resp_dict["status"] != "success":
        return False
    return True


def get_rooms(capacity):
    url = ip_facilities + '/get-all-rooms'
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
            return Response({"status": status.HTTP_400_BAD_REQUEST, "result": False},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        if rooms:
            if check_in_date <= proposed_date_in <= check_out_date:
                rooms.remove(int(reservation.room))
            if check_in_date <= proposed_date_out <= check_out_date:
                rooms.remove(int(reservation.room))
    if rooms:
        return rooms[0]
    else:
        return Response({"status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)


class ReservationsLit(generics.ListCreateAPIView):
    queryset = Reservations.objects.all().order_by("check_in")
    serializer_class = ReservationsSerializer


@api_view(['GET'])
def reservation_list(request, check_in_year, check_in_month, check_in_day):
    if request.method == 'GET':
        dates = []
        try:
            for reservation in Reservations.objects.all():
                check_in_date = datetime.strptime(str(reservation.check_in), '%Y-%m-%d')
                check_out_date = datetime.strptime(str(reservation.check_out), '%Y-%m-%d')
                requested_date = datetime.strptime(check_in_year + "-" + check_in_month + "-" + check_in_day, '%Y-%m-%d')
                try:
                    if check_in_date <= requested_date <= check_out_date:
                        dates.append(reservation)
                except:
                    pass
            serializer = ReservationsSerializer(dates, many=True)
            return Response(serializer.data)
        except:
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR})


@api_view(['GET', 'POST'])
def getBookings(request):
    if request.method == 'GET':
        try:
            reservations = Reservations.objects.all().order_by("check_in")
            serializer = AllReservationsSerializer(reservations, many=True)
            return Response(serializer.data)
        except:
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR})

    elif request.method == 'POST':
        serializer = AllReservationsSerializer(data=request.data, partial=True)
        if serializer.is_valid():
                rooms = is_available(serializer)
                try:
                    serializer_copy = serializer.data.copy()
                    serializer_copy["room"] = rooms
                    serializer_copy["check_in"] = format_time(serializer_copy["check_in"])
                    serializer_copy["check_out"] = format_time(serializer_copy["check_out"])
                    serializer = AllReservationsSerializer(data=serializer_copy)
                    facility_reservation = reserve_facility(request.data["facilities"], serializer_copy["check_in"],
                                                            serializer_copy["check_out"])
                    if facility_reservation and serializer.is_valid():
                        # serializer.save()
                        return Response({"status": 200, "room": rooms[0], "result": True},
                                        status=status.HTTP_201_CREATED)
                    else:
                        return Response({"status": 200, "result": False, "lack of facility": request.data["facilities"]},
                                        status=status.HTTP_409_CONFLICT)
                except:
                    return Response({"status": 200, "result": False}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT', 'DELETE'])
def room_detail(request, pk, check_in_year, check_in_month, check_in_day):
    """
    Retrieve, update or delete a reservation on specific day.
    """
    try:
        room = Reservations.objects.get(room__pk=pk, check_in=check_in_year + "-" + check_in_month + "-" + check_in_day)
    except:
        return Response({"status": 200, "result": False})

    if request.method == 'PUT':
        serializer = UpdateReservationSerializer(room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": 200, "result": True}, status=status.HTTP_201_CREATED)
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        room.delete()
        # facility = request.data["facilities"]
        # data = parse.urlencode({"facilities": facility}).encode()
        # request.Request(ip_facilities+"/deleteFacility", data=data)
        return Response({"status": status.HTTP_200_OK, "result": True})
