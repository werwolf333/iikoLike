import json
from decimal import Decimal
import pytest
from django.urls import reverse
from core.models import Order


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
    return Order.objects.create(table_number=1, status="pending", total_price=10.99)


def test_update_order_status_api_success(client_and_db, test_order):
    """
    Тест успешного обновления статуса заказа через API.
    """
    client, db = client_and_db
    order_to_update = test_order
    url = reverse('core:update_order_status_api', args=[order_to_update.id])

    # Данные для обновления статуса
    new_status = {'status': 'completed'}

    # Отправляем POST-запрос с новым статусом
    response = client.post(url, json.dumps(new_status), content_type='application/json')

    # Проверяем статус ответа
    assert response.status_code == 200

    # Проверяем, что статус заказа обновился в базе данных
    order_to_update.refresh_from_db()
    assert order_to_update.status == 'completed'

    # Проверяем содержимое ответа
    assert response.json() == {'message': 'Order status updated successfully'}


def test_update_order_status_api_not_found(client_and_db):
    """
    Тест попытки обновить статус несуществующего заказа.
    """
    client, db = client_and_db
    url = reverse('core:update_order_status_api', args=[999])  # Используем несуществующий ID

    # Отправляем POST-запрос с новым статусом
    new_status = {'status': 'completed'}
    response = client.post(url, json.dumps(new_status), content_type='application/json')

    # Проверяем статус ответа
    assert response.status_code == 404

    # Проверяем содержимое ответа
    assert response.json() == {'error': 'Order not found'}
