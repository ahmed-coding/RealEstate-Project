from django.urls import path
from . import views
urlpatterns = [
    path('ticket-type/',
         views.TicketViewsets.as_view({'get': 'list'}), name='get_ticket_type'),
    path('create/',
         views.TicketViewsets.as_view({'post': 'create'}), name='create_ticket'),

]
