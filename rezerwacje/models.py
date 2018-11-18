from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError


class Reservations(models.Model):
    room = models.IntegerField()
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=100)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    people = models.IntegerField()
    facility_type = models.IntegerField(default=None)

    def clean(self, *args, **kwargs):
        super(Reservations, self).clean(*args, **kwargs)

        if self.check_out < self.check_in+timedelta(days=1):
            raise ValidationError('Check in date must be later than check out.')

    def __str__(self):
        return self.surname + ' - ' + str(self.check_in)




