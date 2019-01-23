from django.urls import path

from test_app import views

urlpatterns = [
    path('restricted-view/', views.restricted_view),
]
