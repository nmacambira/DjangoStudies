from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
# router.register(r'employees', views.EmployeeViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'departments', views.DepartmentViewSet)
router.register(r'clients', views.ClientViewSet)
router.register(r'jobs', views.JobViewSet)


app_name = "Empresa Top 10"
# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/v1/', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls')),  # include the login and logout views for the browsable API.
    path('api/v1/login/', views.CustomObtainAuthToken.as_view()),
    path('api/v1/users/', views.EmployeeListView.as_view()),
    path('api/v1/users/<pk>/', views.EmployeeDetailView.as_view()),
    path('api/v1/change-password/', views.ChangePasswordView.as_view()),
    path('api/v1/recover-password/', views.RecoverPasswordView.as_view()),
    path('api/v1/reset-password/<str:hash>', views.reset_password, name='reset-password'),
    path('api/v1/device-token/', views.PushNotificationDeviceTokenView.as_view()),
    path('api/v1/contact/', views.ContactView.as_view(), name='contact'),

]