from django.contrib import admin

from .models import *

admin.site.register(AircraftType)
admin.site.register(Airline)
admin.site.register(Airframe)
admin.site.register(FlightInfo)
admin.site.register(Flight)
admin.site.register(UserTrip)
admin.site.register(TrackImage)
admin.site.register(Meal)


