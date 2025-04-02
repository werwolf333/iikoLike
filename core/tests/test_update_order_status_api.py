import json
from decimal import Decimal
import pytest
from django.urls import reverse
from django.test import Client
from core.models import Order
from typing import Tuple, Dict, Any


@pytest.fixture
def client_and_db(client: Client, db) -> Tuple[Client, None]:
    """
    Фикстура, которая предоставляет клиент и очищенную базу данных.
    Это делается для того, чтобы каждый тест был изолирован.
    """
    return client, db


@pytest.fixture
def test_order(db) -> Order:
    """
    Фикстура для создания тестового заказа.
    """
    return Order.objects.create(table_number=1, status="pending", total_price=Decimal("10.99"))


@pytest.mark.django_db
def test_update_order_status_api_success(client_and_db: Tuple[Client, None], test_order: Order) -> None:
    """
    Тест успешного обновления статуса заказа через API.
    """
    client, db = client_and_db
    order_to_update: Order = test_order
    url: str = reverse('core:update_order_status_api', args=[order_to_update.id])

    # Данные для обновления статуса
    new_status: Dict[str, str] = {'status': 'completed'}

    # Отправляем POST-запрос с новым статусом
    response = client.post(url, json.dumps(new_status), content_type='application/json')

    # Проверяем статус ответа
    assert response.status_code == 200

    # Проверяем, что статус заказа обновился в базе данных
    order_to_update.refresh_from_db()
    assert order_to_update.status == 'completed'

    # Проверяем содержимое ответа
    assert response.json() == {'message': 'Order status updated successfully'}


@pytest.mark.django_db
def test_update_order_status_api_not_found(client_and_db: Tuple[Client, None]) -> None:
    """
    Тест попытки обновить статус несуществующего заказа.
    """
    client, db = client_and_db
    url: str = reverse('core:update_order_status_api', args=[999])  # Используем несуществующий ID

    # Отправляем POST-запрос с новым статусом
    new_status: Dict[str, str] = {'status': 'completed'}
    response = client.post(url, json.dumps(new_status), content_type='application/json')

    # Проверяем статус ответа
    assert response.status_code == 404

    # Проверяем содержимое ответа
    assert response.json() == {'error': 'Order not found'}
