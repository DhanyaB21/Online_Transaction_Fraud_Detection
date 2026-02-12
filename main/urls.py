from django.urls import path
from .views import PredictFraud, dashboard_view 

urlpatterns = [
    path('predict/', PredictFraud.as_view(), name='predict_fraud'),
    path('dashboard/', dashboard_view, name='dashboard'),
]