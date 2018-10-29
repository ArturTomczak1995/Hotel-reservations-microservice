from rest_framework import serializers
from .models import Reservations, Rooms

class ReservationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservations
        fields = ["check_in", "check_out", "people", "room"]

class AllReservationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservations
        fields = ["name", "surname", "check_in", "check_out", "people", "room"]

class UpdateReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservations
        fields = ["name", "surname", "people"]




