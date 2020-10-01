from django.urls import path
from . import views
urlpatterns = [
    path('',views.accounts,name='accounts'),
    path('accounts/',views.accounts,name='accounts'),
    path('signup/',views.signUp,name='signup'),
    path('login/',views.Login,name='login'),
    path('logout/',views.Logout,name='logout')
]