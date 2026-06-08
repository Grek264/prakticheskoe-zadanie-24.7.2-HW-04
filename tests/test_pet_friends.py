import os

import pytest
from api import get_api_key, create_pet_simple, get_pets_list, add_new_pet_with_photo, set_pet_photo, delete_pet, \
    update_pet_info
from test_user_log import valid_email, valid_password


def test_get_api_key_success():
    """Проверка получения API-ключа с корректными email и паролем."""
    key = get_api_key(valid_email, valid_password)

    assert isinstance(key, str), "Ключ должен быть строкой"
    assert len(key) > 0, "Ключ не может быть пустым"


def test_create_pet_simple_success():
    """Успешное создание питомца без фото."""
    api_key = get_api_key(valid_email, valid_password)

    pet_name = "Бобик"
    animal_type = "собака"
    age = 3
    response = create_pet_simple(api_key, pet_name, animal_type, age)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["name"] == pet_name
    assert json_data["animal_type"] == animal_type
    assert int(json_data["age"]) == age

def test_get_pets_list_success():
    api_key = get_api_key(valid_email, valid_password)
    response = get_pets_list(api_key)
    assert response.status_code == 200
    data = response.json()
    assert "pets" in data
    assert isinstance(data["pets"], list)

def test_add_new_pet_with_photo():
    api_key = get_api_key(valid_email, valid_password)
    current_dir = os.path.dirname(__file__)
    photo_path = os.path.join(current_dir, "test_images", "test_cat.jpg")
    assert os.path.exists(photo_path), f"Файл {photo_path} не найден"

    pet_name = "Мурзик"
    animal_type = "кот"
    age = 2
    response = add_new_pet_with_photo(api_key, pet_name, animal_type, age, photo_path)

def test_set_pet_photo():
    """Добавление фото существующему питомцу."""
    # 1. Получаем ключ
    api_key = get_api_key(valid_email, valid_password)

    # 2. Создаём питомца без фото
    pet_name = "не мурзик"
    animal_type = "кот"
    age = 1
    create_response = create_pet_simple(api_key, pet_name, animal_type, age)
    assert create_response.status_code == 200
    pet_data = create_response.json()
    pet_id = pet_data["id"]
    assert pet_data["pet_photo"] == "", "Изначально фото должно быть пустым"

    # 3. Путь к тестовому изображению
    current_dir = os.path.dirname(__file__)
    photo_path = os.path.join(current_dir, "test_images", "test_cat.jpg")
    assert os.path.exists(photo_path), f"Файл {photo_path} не найден"

    # 4. Добавляем фото
    set_photo_response = set_pet_photo(api_key, pet_id, photo_path)
    assert set_photo_response.status_code == 200
    updated_pet = set_photo_response.json()
    assert updated_pet["id"] == pet_id
    assert updated_pet["name"] == pet_name
    assert updated_pet["animal_type"] == animal_type
    assert int(updated_pet["age"]) == age
    assert updated_pet["pet_photo"] != "", "Фото должно быть добавлено"

def test_delete_pet():
    api_key = get_api_key(valid_email, valid_password)
    pet_name = "На удаление"
    animal_type = "хомяк"
    age = 1
    create_response = create_pet_simple(api_key, pet_name, animal_type, age)
    assert create_response.status_code == 200
    pet_id = create_response.json()["id"]

    delete_response = delete_pet(api_key, pet_id)
    assert delete_response.status_code == 200, f"Ожидался 200, получен {delete_response.status_code}"

def test_update_pet_info():
    api_key = get_api_key(valid_email, valid_password)

    # 1. Создаём питомца с исходными данными
    old_name = "Старик"
    old_type = "собака"
    old_age = 5
    create_response = create_pet_simple(api_key, old_name, old_type, old_age)
    assert create_response.status_code == 200
    pet_id = create_response.json()["id"]

    # 2. Обновляем данные
    new_name = "Молодой"
    new_type = "волкодав"
    new_age = 2
    update_response = update_pet_info(api_key, pet_id, name=new_name, animal_type=new_type, age=new_age)
    assert update_response.status_code == 200
    updated_pet = update_response.json()