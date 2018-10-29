from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError

class Rooms(models.Model):
    STATUS_CHOICES = (
        (1, 1),(2, 2),(3, 3),(4, 4),(5, 5),
    )
    room_no = models.IntegerField(choices=STATUS_CHOICES)
    def __str__(self):
        return "Room number: " + str(self.room_no)

class Reservations(models.Model):
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE, default=None, related_name='room')
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=100)
    check_in = models.DateField()
    check_out = models.DateField()
    people = models.IntegerField()

    def clean(self, *args, **kwargs):
        super(Reservations, self).clean(*args, **kwargs)

        if self.check_out < self.check_in+timedelta(days=1):
            raise ValidationError('Check in date must be later than check out.')

    def __str__(self):
        return self.surname + ' - ' + str(self.check_in)




