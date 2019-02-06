from django.urls import path

from test_app import views

urlpatterns = [
    path('restricted-model-view/', views.restricted_model_view),
    path('restricted-model-view-explicit/', views.restricted_model_with_explicit_reference_view),
    path('restricted-global-view/', views.restricted_global_view),
]
