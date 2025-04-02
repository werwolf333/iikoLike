from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "В ожидании"
        READY = "ready", "Готово"
        PAID = "paid", "Оплачено"

    table_number = models.PositiveIntegerField(verbose_name="Номер стола")
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING, verbose_name="Статус"
    )
    items = models.JSONField(default=list, encoder=DjangoJSONEncoder, verbose_name="Список блюд")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Общая стоимость")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    def __str__(self):
        return f"Заказ {self.id} (Стол {self.table_number})"

    def update_total_price(self):
        self.total_price = sum(item.get("price", 0) * item.get("quantity", 1) for item in self.items)
        self.save()
