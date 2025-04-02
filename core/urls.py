from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    # Web-интерфейс
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/add/', views.OrderCreateView.as_view(), name='order_add'),
    path('orders/edit/<int:pk>/', views.OrderUpdateView.as_view(), name='order_edit'),
    path('orders/delete/<int:pk>/', views.OrderDeleteView.as_view(), name='order_delete'),
    path('orders/update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('revenue/', views.RevenueView.as_view(), name='revenue'),

    # API
    path('api-v1/orders/', views.order_list_api, name='order_list_api'),
    path('api-v1/orders/create/', views.order_create_api, name='order_create_api'),
    path('api-v1/orders/<int:pk>/', views.order_detail_api, name='order_detail_api'),
    path('api-v1/orders/<int:pk>/update/', views.order_update_api, name='order_update_api'),
    path('api-v1/orders/<int:pk>/delete/', views.order_delete_api, name='order_delete_api'),
    path('api-v1/orders/update-status/<int:order_id>/', views.update_order_status_api, name='update_order_status_api'),
    path('api-v1/revenue/', views.revenue_view, name='revenue_api'),
]
