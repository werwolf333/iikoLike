import json
from datetime import timedelta
from django.db.models import Sum
from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from core.models import Order


@csrf_exempt
def order_create_api(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        data: dict = json.loads(request.body)
        new_order: Order = Order(
            table_number=data['table_number'],
            status=data.get('status', Order.Status.PENDING),
            items=data.get('items', []),
            total_price=data.get('total_price', 0)
        )
        new_order.save()
        return JsonResponse({'message': 'Order created successfully', 'id': new_order.id}, status=201)


@csrf_exempt
def order_detail_api(request: HttpRequest, pk: int) -> JsonResponse:
    try:
        order: Order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    if request.method == 'GET':
        data: dict = {
            'id': order.id,
            'table_number': order.table_number,
            'status': order.status,
            'total_price': order.total_price,
            'items': order.items,
            'created_at': order.created_at
        }
        return JsonResponse(data)

    elif request.method == 'PUT':
        data: dict = json.loads(request.body)
        order.table_number = data.get('table_number', order.table_number)
        order.status = data.get('status', order.status)
        order.total_price = data.get('total_price', order.total_price)
        order.save()
        return JsonResponse({'message': 'Order updated successfully'})

    elif request.method == 'DELETE':
        order.delete()
        return JsonResponse({'message': 'Order deleted successfully'})


@csrf_exempt
def order_update_api(request: HttpRequest, pk: int) -> JsonResponse:
    order: Order = get_object_or_404(Order, pk=pk)
    if request.method == "PUT":
        try:
            data: dict = json.loads(request.body)
            order.table_number = data.get("table_number", order.table_number)
            order.status = data.get("status", order.status)
            order.items = data.get("items", order.items)
            order.update_total_price()
            order.save()
            return JsonResponse({"message": "Заказ обновлён", "order_id": order.id})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Неверный формат JSON"}, status=400)
    return JsonResponse({"error": "Метод не разрешён"}, status=405)


@csrf_exempt
def update_order_status_api(request: HttpRequest, order_id: int) -> JsonResponse:
    try:
        order: Order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    if request.method == 'POST':
        data: dict = json.loads(request.body)
        order.status = data.get('status', order.status)
        order.save()
        return JsonResponse({'message': 'Order status updated successfully'})


@csrf_exempt
def order_delete_api(request, pk: int) -> JsonResponse:
    try:
        order = Order.objects.get(pk=pk)  # Получаем заказ по ID
    except Order.DoesNotExist:
        return JsonResponse({"error": "Заказ не найден"}, status=404)

    if request.method == "DELETE":
        order.delete()
        return JsonResponse({"message": "Заказ удалён"})

    return JsonResponse({"error": "Метод не разрешён"}, status=405)


@csrf_exempt
def revenue_view(request: HttpRequest) -> JsonResponse:
    today = now().date()

    # Выручка за сегодня
    today_orders = Order.objects.filter(status=Order.Status.PAID, created_at__date=today)
    total_revenue_today: float = today_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Выручка за неделю
    last_week_orders = Order.objects.filter(
        status=Order.Status.PAID,
        created_at__gte=today - timedelta(days=7),
        created_at__lt=today
    )
    total_revenue_last_week: float = last_week_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Выручка за месяц
    last_month_orders = Order.objects.filter(
        status=Order.Status.PAID,
        created_at__gte=today.replace(day=1) - timedelta(days=today.day),
        created_at__lt=today
    )
    total_revenue_last_month: float = last_month_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0

    data: dict = {
        'today_revenue': total_revenue_today,
        'last_week_revenue': total_revenue_last_week,
        'last_month_revenue': total_revenue_last_month,
    }

    return JsonResponse(data)