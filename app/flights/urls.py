from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("passengers/", views.PassengersView.as_view(), name="passengers"),
    path("profile/<slug:username>/", views.ProfileView.as_view(), name="profile"),
    path("flight/<slug:usertripslug>/", views.FlightView.as_view(), name="flight"),
    path("flight/<slug:usertripslug>/update", views.FlightUpdateView.as_view(), name="flight_update"),
    path("flight/<slug:usertripslug>/delete", views.FlightDeleteView.as_view(), name="flight_delete"),
    path("add_flight/", views.AddFlightView.as_view(), name="add_flight")
]

# views.AddFlightView.as_view()
