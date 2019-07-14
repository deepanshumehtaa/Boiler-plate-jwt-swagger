from django.urls import path
from . import views

urlpatterns = [
    path('', views.economy_home, name='economy_home'),
    path('deposit/', views.deposits, name='economy_deposit'),
    path('deposit/<int:deposit_id>', views.deposit_detail, name='economy_deposit_detail'),
    path('deposit/<int:deposit_id>/approve', views.deposit_approve, name='economy_approve_deposit'),
    path('deposit/<int:deposit_id>/invalidate', views.deposit_invalidate, name='economy_invalidate_deposit'),
    path('deposit/<int:deposit_id>/edit', views.deposit_edit, name='economy_edit_deposit'),

]