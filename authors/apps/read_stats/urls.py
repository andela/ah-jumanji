from django.urls import path
from .views import AddRead, GetReads

urlpatterns = [
    path(
        'add/<slug>/', AddRead.as_view(),
        name='read'),
    path(
        'reads/', GetReads.as_view(),
        name='reads'),
]
