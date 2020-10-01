from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('index',views.index,name='index'),
    path('saveread/(?P<bookread>\d+)/)',views.saveread,name='saveread'),
    path('search',views.search,name='search')
]