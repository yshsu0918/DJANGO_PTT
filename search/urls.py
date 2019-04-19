from django.urls import path

from . import views

urlpatterns = [
	    path('', views.index, name='index'),
		path('UPDATE/', views.UPDATE, name='UPDATE'),
		path('UPDATEDAY/', views.UPDATEDAY, name='UPDATEDAY'),		
	    path('TEST/', views.TEST, name='TEST'),
		]
