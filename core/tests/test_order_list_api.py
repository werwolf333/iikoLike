import pytest
from django.urls import reverse
from django.test import Client
from core.models import Order
from typing import Tuple, List


@pytest.fixture
def client_and_db(client: Client, db) -> Tuple[Client, None]:
    """Фикстура, предоставляющая клиент и очищенную БД."""
    return client, db


@pytest.fixture
def create_orders(db) -> List[Order]:
    """Фикстура для создания нескольких заказов в базе данных."""
    return [
        Order.objects.create(table_number=1, status="pending", total_price=15.99),
        Order.objects.create(table_number=2, status="completed", total_price=20.50),
        Order.objects.create(table_number=1, status="pending", total_price=8.99),
    ]


@pytest.mark.django_db
def test_order_list_api(client_and_db: Tuple[Client, None], create_orders: List[Order]) -> None:
    """Тест получения всех заказов."""
    client, db = client_and_db
    url: str = reverse('core:order_list_api')

    response = client.get(url)

    assert response.status_code == 200
    data = response.json()

    assert len(data["orders"]) == 3  # Проверяем, что все 3 заказа в ответе
    assert {order["table_number"] for order in data["orders"]} == {1, 2}  # Проверяем номера столов


@pytest.mark.django_db
def test_order_list_api_filter_by_table_number(client_and_db: Tuple[Client, None], create_orders: List[Order]) -> None:
    """Тест фильтрации по номеру стола."""
    client, db = client_and_db
    url: str = reverse('core:order_list_api') + "?table_number=1"

    response = client.get(url)

    assert response.status_code == 200
    data = response.json()

    assert len(data["orders"]) == 2  # Должны получить только заказы с table_number=1
    assert all(order["table_number"] == 1 for order in data["orders"])


@pytest.mark.django_db
def test_order_list_api_filter_by_status(client_and_db: Tuple[Client, None], create_orders: List[Order]) -> None:
    """Тест фильтрации по статусу заказа."""
    client, db = client_and_db
    url: str = reverse('core:order_list_api') + "?status=pending"

    response = client.get(url)

    assert response.status_code == 200
    data = response.json()

    assert len(data["orders"]) == 2  # Должны получить только pending-заказы
    assert all(order["status"] == "pending" for order in data["orders"])


@pytest.mark.django_db
def test_order_list_api_no_orders(client_and_db: Tuple[Client, None]) -> None:
    """Тест, когда заказов нет (пустая база)."""
    client, db = client_and_db
    url: str = reverse('core:order_list_api')

    response = client.get(url)

    assert response.status_code == 200
    data = response.json()

    assert data["orders"] == []  # Должен вернуться пустой список
