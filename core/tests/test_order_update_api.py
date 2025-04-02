import json
import pytest
from decimal import Decimal
from django.urls import reverse
from core.models import Order

@pytest.fixture
def client_and_db(client, db):
    """
    Фикстура, которая предоставляет клиент и очищенную базу данных.
    Это делается для того, чтобы каждый тест был изолирован.
    """
    return client, db


def test_order_update_api(client_and_db):
    """
    Тест проверяет обновление заказа через API:
    1. Проверяет статус ответа (должен быть 200 OK).
    2. Проверяет, что заказ был успешно обновлён в базе данных.
    3. Проверяет правильность всех обновленных полей заказа:
       - Номер столика.
       - Статус заказа.
       - Общую стоимость заказа.
    """
    client, db = client_and_db  # Распаковываем фикстуру

    # Создание начального заказа в базе данных
    initial_data = {
        "table_number": 1,
        "status": "pending",
        "items": [
            {"name": "apple", "price": 100, "quantity": 1},
            {"name": "banana", "price": 200, "quantity": 2}
        ]
    }
    order = Order.objects.create(**initial_data)
    order.update_total_price()  # Пересчитываем total_price

    # URL для обновления заказа
    url = reverse('core:order_update_api', args=[order.id])

    # Данные для обновления заказа
    update_data = {
        "table_number": 3,
        "status": "ready",
        "items": [
            {"name": "apple", "price": 100, "quantity": 2},
            {"name": "banana", "price": 150, "quantity": 3}
        ]
    }

    # Отправка PUT-запроса на обновление заказа
    response = client.put(
        url,
        content_type='application/json',
        data=json.dumps(update_data)
    )

    # Проверка статуса ответа
    assert response.status_code == 200

    # Проверка, что заказ был обновлён в базе данных
    order.refresh_from_db()
    assert order.table_number == update_data["table_number"]
    assert order.status == "ready"

    # Пересчитываем total_price на основе обновленных данных в items
    total_price = sum(item['price'] * item['quantity'] for item in update_data['items'])
    order.update_total_price()  # Обновляем общую стоимость
    assert order.total_price == Decimal(str(total_price))
