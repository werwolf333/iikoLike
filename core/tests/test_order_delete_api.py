import json
from django.urls import reverse
import pytest
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
    return Order.objects.create(
        table_number=1,
        status=Order.Status.PENDING,
        items=[{"item": "Pizza", "price": 10.99}],
        total_price=10.99
    )


@pytest.mark.django_db
def test_order_delete_api_success(client_and_db, test_order):
    """
    Тест успешного удаления заказа через API.
    """
    client, db = client_and_db
    url = reverse('core:order_delete_api', args=[test_order.id])

    # Отправляем DELETE-запрос
    response = client.delete(url)

    # Проверяем статус ответа
    assert response.status_code == 200

    # Проверяем, что заказ действительно удалён из базы данных
    with pytest.raises(Order.DoesNotExist):
        Order.objects.get(id=test_order.id)

    # Проверяем содержимое ответа
    assert response.json() == {"message": "Заказ удалён"}


@pytest.mark.django_db
def test_order_delete_api_method_not_allowed(client_and_db, test_order):
    """
    Тест неподдерживаемого метода для удаления заказа.
    """
    client, db = client_and_db
    url = reverse('core:order_delete_api', args=[test_order.id])

    # Отправляем несоответствующий метод GET
    response = client.get(url)

    # Проверяем статус ответа
    assert response.status_code == 405

    # Проверяем содержимое ответа
    assert response.json() == {"error": "Метод не разрешён"}


@pytest.mark.django_db
def test_order_delete_api_not_found(client_and_db):
    """
    Тест попытки удалить несуществующий заказ.
    """
    client, db = client_and_db
    url = reverse('core:order_delete_api', args=[999])  # Несуществующий ID

    # Отправляем DELETE-запрос
    response = client.delete(url)

    # Проверяем статус ответа
    assert response.status_code == 404

    # Проверяем содержимое ответа
    assert response.json() == {"error": "Заказ не найден"}
