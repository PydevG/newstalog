from django.urls import path
from . import views

urlpatterns = [
    path("token/", views.get_access_token, name="mpesa-token"),
    path("stk-push/", views.stk_push, name="mpesa-stk-push"),
    path("simulate-c2b/", views.simulate_c2b_payment, name="simulate-c2b"),
    path("stk-callback/", views.stk_push_callback, name="stk-callback"),
]
