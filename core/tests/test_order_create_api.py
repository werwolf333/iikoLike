import json
from decimal import Decimal
import pytest
from django.urls import reverse
from django.test import Client
from core.models import Order
from typing import Tuple

@pytest.fixture
def client_and_db(client: Client, db) -> Tuple[Client, None]:
    """
    Фикстура, которая предоставляет клиент и очищенную базу данных.
    Это делается для того, чтобы каждый тест был изолирован.
    """
    return client, db


def test_order_create_api(client_and_db: Tuple[Client, None]) -> None:
    """
    Тест проверяет создание заказа через API:
    1. Проверяет статус ответа (должен быть 201 Created).
    2. Проверяет, что заказ был успешно сохранён в базе данных (один объект).
    3. Проверяет правильность всех полей заказа:
       - Номер столика.
       - Статус заказа.
       - Список позиций заказа.
       - Общую стоимость заказа.
    """
    client, db = client_and_db  # Распаковываем фикстуру

    url: str = reverse('core:order_create_api')
    data: dict = {
        "table_number": 2,
        "status": "pending",
        "items": [{"item": "Burger", "price": 8.99}],
        "total_price": 8.99
    }

    # Отправка запроса на создание заказа
    response = client.post(url, content_type='application/json', data=json.dumps(data))

    assert response.status_code == 201
    assert Order.objects.count() == 1
    order: Order = Order.objects.first()  # Тип явно указан
    assert order.table_number == 2
    assert order.status == Order.Status.PENDING
    assert order.items == data["items"]
    assert order.total_price == Decimal(str(data["total_price"]))
