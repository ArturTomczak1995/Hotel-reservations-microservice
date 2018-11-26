from rest_framework import serializers
from .models import Reservations


class ReservationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservations
        fields = ["check_in", "check_out", "people", "room"]


class AllReservationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservations
        time = serializers.DateField(format="%Y-%m-%d %H:%M")
        fields = ["name", "surname", "check_in", "check_out", "people"]


class BookRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservations
        time = serializers.DateField(format="%Y-%m-%d %H:%M")
        fields = '__all__'


class UpdateReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservations
        fields = ["name", "surname"]




