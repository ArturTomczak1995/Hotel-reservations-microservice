from .models import Reservations, Rooms
from .serializers import ReservationsSerializer, AllReservationsSerializer, UpdateReservationSerializer
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
import json
from urllib import request, parse

ip_facilities = ""


def get_facilities(facilities):
    url = 'https://learnwebcode.github.io/json-example/animals-1.json'
    # url = ip_facilities + '/getFacilities?used=false' # POBIERA INFORMACJE O UDOGODNIENIACH
    serialized_data = request.urlopen(url)
    data = json.loads(serialized_data.read())[0]  # moze nie wymagac[0]
    lack_facility = []
    if not bool(facilities):
        return True
    else:
        for facility in facilities:
            if facility in data:  # moze tu data["facility"]
                pass
            else:
                lack_facility.append(facility)
        if lack_facility:
            return lack_facility
        return True


def format_time(input_data):
    t = datetime.strptime(input_data, "%Y-%m-%d %H:%M")
    s = t.strftime('%Y-%m-%d %H:%M')
    tail = s[-2:]
    f = round(float(tail), -1)
    temp = "%i" % f
    formated_date = datetime.strptime("%s%s" % (s[:-2], temp), "%Y-%m-%d %H:%M")
    return formated_date


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


### BOOK A ROOM OR CHECK ALL RESERVED ROOMS
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
            try:
                rooms = []
                for room in Rooms.objects.all():
                    rooms.append(room.room_no)
                for reservation in Reservations.objects.all():
                    check_inDate = datetime.strptime(reservation.check_in.strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
                    check_outDate = datetime.strptime(reservation.check_out.strftime('%Y-%m-%d %H:%M'),
                                                      '%Y-%m-%d %H:%M')
                    proposedDateIN = datetime.strptime(serializer.data["check_in"], '%Y-%m-%d %H:%M')
                    proposedDateOUT = datetime.strptime(serializer.data["check_out"], '%Y-%m-%d %H:%M')
                    if (proposedDateIN >= proposedDateOUT):
                        return Response({"status": status.HTTP_400_BAD_REQUEST, "result": False},
                                        status=status.HTTP_406_NOT_ACCEPTABLE)
                    try:
                        if check_inDate <= proposedDateIN <= check_outDate:
                            rooms.remove(int(reservation.room.pk))
                        if check_inDate <= proposedDateOUT <= check_outDate:
                            rooms.remove(int(reservation.room.pk))
                    except:
                        pass
                try:
                    fake_data = serializer.data.copy()
                    fake_data2 = serializer.data.copy()
                    fake_data["room"] = rooms[0]
                    fake_data["check_in"] = format_time(fake_data2["check_in"])
                    fake_data["check_out"] = format_time(fake_data2["check_out"])
                    serializer = AllReservationsSerializer(data=fake_data)
                    serializer.is_valid()
                    facility = get_facilities(request.data["facilities"])
                    if facility == True:
                        serializer.save()
                        return Response({"status": 200, "room": rooms[0], "result": True},
                                        status=status.HTTP_201_CREATED)
                    else:
                        return Response({"status": 200, "result": False, "lack of facility": facility},
                                        status=status.HTTP_409_CONFLICT)
                except:
                    return Response({"status": 200, "result": False}, status=status.HTTP_406_NOT_ACCEPTABLE)
            except:
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
            # facility = get_facilities(request.data["facilities"])
            # if facility == True:
            serializer.save()
            return Response({"status": 200, "result": True}, status=status.HTTP_201_CREATED)
            # else:
            #     return Response({ "status": 200, "result": False, "lack of facility": facility}, status=status.HTTP_409_CONFLICT)
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        room.delete()
        # facility = request.data["facilities"]
        # data = parse.urlencode({"facilities": facility}).encode()Ł
        # request.Request(ip_facilities+"/deleteFacility", data=data)
        return Response({"status": status.HTTP_200_OK, "result": True})
