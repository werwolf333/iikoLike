import pytest
from django.urls import reverse
from core.models import Order
from decimal import Decimal


@pytest.fixture
def client_and_db(client, db):
    """
    Фикстура, которая предоставляет клиент и очищенную базу данных.
    Это делается для того, чтобы каждый тест был изолирован.
    """
    return client, db


@pytest.fixture
def test_order(db):
    """
    Фикстура для создания тестового заказа.
    """
    return Order.objects.create(
        table_number=1,
        status=Order.Status.PENDING,
        items=[{"item": "Pizza", "price": 10.99}],
        total_price=10.99
    )


def test_order_detail_api_get(client_and_db, test_order):
    """
    Тест проверяет получение деталей заказа через API:
    1. Проверка, что запрос возвращает успешный ответ (200 OK).
    2. Проверка, что данные, возвращаемые API, соответствуют данным в базе данных.
    """
    client, db = client_and_db  # Распаковываем фикстуру для клиента и базы данных

    # Формируем URL для запроса с использованием ID тестового заказа
    url = reverse('core:order_detail_api', args=[test_order.id])

    # Отправляем GET-запрос для получения деталей заказа
    response = client.get(url)

    # Проверка, что статус ответа равен 200 (успешный запрос)
    assert response.status_code == 200

    # Получаем данные из ответа в формате JSON
    data = response.json()

    # Проверка, что все поля данных совпадают с полями тестового заказа
    assert data["id"] == test_order.id
    assert data["table_number"] == test_order.table_number
    assert data["status"] == test_order.status
    assert Decimal(data["total_price"]) == Decimal(str(test_order.total_price))
    assert data["items"] == test_order.items
    assert data["created_at"] == test_order.created_at.replace(microsecond=0).strftime(
        '%Y-%m-%dT%H:%M:%S.') + f"{test_order.created_at.microsecond // 1000:03d}Z"
