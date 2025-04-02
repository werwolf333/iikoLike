import json
from datetime import timedelta
from django.db.models import Sum, QuerySet
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, TemplateView
from django.urls import reverse_lazy
from core.models import Order
from typing import Any, Dict, List
from django.shortcuts import render


def custom_404_view(request, exception=None):
    return render(request, 'core/404.html', status=404)


class OrderListView(ListView):
    model = Order
    template_name = 'core/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self) -> QuerySet[Order]:
        queryset = super().get_queryset()

        search_table_number = self.request.GET.get('table_number')
        if search_table_number:
            queryset = queryset.filter(table_number=search_table_number)

        search_status = self.request.GET.get('status')
        if search_status:
            queryset = queryset.filter(status=search_status)

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['STATUS_CHOICES'] = Order.Status.choices
        context['search_table_number'] = self.request.GET.get('table_number', '')
        context['search_status'] = self.request.GET.get('status', '')

        return context


class OrderCreateView(CreateView):
    model = Order
    fields = ['table_number']
    template_name = 'core/add_order.html'
    success_url = reverse_lazy('core:order_list')

    def form_valid(self, form: Any) -> HttpResponseRedirect:
        items_json = self.request.POST.get('items_json')
        items: List[Dict[str, Any]] = json.loads(items_json)  # Безопаснее, чем eval

        total_price = sum(item["price"] * item["quantity"] for item in items)

        order = form.save(commit=False)
        order.status = Order.Status.PENDING
        order.items = items
        order.total_price = total_price
        order.save()

        return HttpResponseRedirect(self.success_url)


class OrderUpdateView(UpdateView):
    model = Order
    fields = ['table_number', 'status']
    template_name = 'core/edit_order.html'
    success_url = reverse_lazy('core:order_list')

    def form_valid(self, form: Any) -> Any:
        order = form.save(commit=False)

        # Получаем JSON из формы
        items_json = self.request.POST.get('items_json')

        if items_json:
            order.items = json.loads(items_json)

        order.update_total_price()
        order.save()
        return super().form_valid(form)


class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'core/order_confirm_delete.html'
    success_url = reverse_lazy('core:order_list')


# Функция для обновления статуса заказа
def update_order_status(request: Any, order_id: int) -> HttpResponseBadRequest | HttpResponseRedirect:
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in dict(Order.Status.choices):
            order.status = new_status
            order.save()
            return redirect('core:order_list')
        else:
            return HttpResponseBadRequest("Invalid status format")

    return HttpResponseBadRequest("Invalid HTTP method")


class RevenueView(TemplateView):
    template_name = 'core/revenue.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Получаем текущую дату
        today = now().date()

        # Фильтруем заказы за сегодняшний день
        today_orders = Order.objects.filter(status=Order.Status.PAID, created_at__date=today)

        # Вычисляем общую выручку
        total_revenue = today_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0

        # Фильтруем заказы за предыдущую неделю
        last_week_orders = Order.objects.filter(status=Order.Status.PAID, created_at__gte=today - timedelta(days=7), created_at__lt=today)
        last_week_revenue = last_week_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0

        # Фильтруем заказы за предыдущий месяц
        last_month_orders = Order.objects.filter(status=Order.Status.PAID, created_at__gte=today.replace(day=1) - timedelta(days=today.day), created_at__lt=today)
        last_month_revenue = last_month_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0

        # Добавляем данные в контекст
        context['today_revenue'] = total_revenue
        context['last_week_revenue'] = last_week_revenue
        context['last_month_revenue'] = last_month_revenue

        return context


def order_list_api(request: Any) -> JsonResponse:
    queryset = Order.objects.all()

    # Поиск по номеру стола
    table_number = request.GET.get("table_number")
    if table_number:
        queryset = queryset.filter(table_number=table_number)

    # Поиск по статусу
    status = request.GET.get("status")
    if status:
        queryset = queryset.filter(status=status)

    orders = list(queryset.values("id", "table_number", "status", "items", "total_price", "created_at"))

    return JsonResponse({"orders": orders})
