from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'), # register 沒有內建 view 要自己寫
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('', RedirectView.as_view(pattern_name='expense_list')),  # 根路徑導向 expense_list
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add/', views.add_expense, name='add_expense'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
]