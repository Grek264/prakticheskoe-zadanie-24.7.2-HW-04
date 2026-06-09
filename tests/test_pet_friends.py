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
    assert " " not in key, "Ключ не должен содержать пробелов"


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
    # ИСПРАВЛЕНО: id приходит как строка (UUID)
    assert "id" in json_data, "Ответ должен содержать id созданного питомца"
    assert isinstance(json_data["id"], str), "id должен быть строкой (UUID)"
    assert len(json_data["id"]) > 0, "id не может быть пустым"


def test_get_pets_list_success():
    api_key = get_api_key(valid_email, valid_password)
    response = get_pets_list(api_key)
    assert response.status_code == 200
    data = response.json()
    assert "pets" in data
    assert isinstance(data["pets"], list)
    if len(data["pets"]) > 0:
        for pet in data["pets"]:
            assert "id" in pet, "У каждого питомца в списке должен быть id"


def test_add_new_pet_with_photo():
    api_key = get_api_key(valid_email, valid_password)
    current_dir = os.path.dirname(__file__)
    photo_path = os.path.join(current_dir, "test_images", "test_cat.jpg")
    assert os.path.exists(photo_path), f"Файл {photo_path} не найден"

    pet_name = "Мурзик"
    animal_type = "кот"
    age = 2
    response = add_new_pet_with_photo(api_key, pet_name, animal_type, age, photo_path)
    assert response.status_code == 200, "Создание питомца с фото должно завершаться статусом 200"
    json_data = response.json()
    assert json_data["name"] == pet_name
    assert json_data["animal_type"] == animal_type
    assert int(json_data["age"]) == age
    assert json_data["pet_photo"] is not None and json_data["pet_photo"] != "", "Фото должно быть загружено"


def test_set_pet_photo():
    """Добавление фото существующему питомцу."""
    api_key = get_api_key(valid_email, valid_password)

    pet_name = "не мурзик"
    animal_type = "кот"
    age = 1
    create_response = create_pet_simple(api_key, pet_name, animal_type, age)
    assert create_response.status_code == 200
    pet_data = create_response.json()
    pet_id = pet_data["id"]
    assert pet_data["pet_photo"] == "", "Изначально фото должно быть пустым"

    current_dir = os.path.dirname(__file__)
    photo_path = os.path.join(current_dir, "test_images", "test_cat.jpg")
    assert os.path.exists(photo_path), f"Файл {photo_path} не найден"

    set_photo_response = set_pet_photo(api_key, pet_id, photo_path)
    assert set_photo_response.status_code == 200
    updated_pet = set_photo_response.json()
    assert updated_pet["id"] == pet_id
    assert updated_pet["name"] == pet_name
    assert updated_pet["animal_type"] == animal_type
    assert int(updated_pet["age"]) == age
    assert updated_pet["pet_photo"] != "", "Фото должно быть добавлено"
    assert isinstance(updated_pet["pet_photo"], str) and len(updated_pet["pet_photo"]) > 10, \
        "Фото должно быть представлено непустой строкой (base64 или URL)"


def test_delete_pet():
    """Позитивный тест удаления питомца."""
    api_key = get_api_key(valid_email, valid_password)
    pet_name = "На удаление"
    animal_type = "хомяк"
    age = 1
    create_response = create_pet_simple(api_key, pet_name, animal_type, age)
    assert create_response.status_code == 200
    pet_id = create_response.json()["id"]

    delete_response = delete_pet(api_key, pet_id)
    assert delete_response.status_code == 200, f"Ожидался 200, получен {delete_response.status_code}"

    # Повторное удаление (идемпотентность)
    second_delete = delete_pet(api_key, pet_id)
    assert second_delete.status_code == 200, "Повторное удаление также должно возвращать 200"


def test_update_pet_info():
    api_key = get_api_key(valid_email, valid_password)

    old_name = "Старик"
    old_type = "собака"
    old_age = 5
    create_response = create_pet_simple(api_key, old_name, old_type, old_age)
    assert create_response.status_code == 200
    pet_id = create_response.json()["id"]

    new_name = "Молодой"
    new_type = "волкодав"
    new_age = 2
    update_response = update_pet_info(api_key, pet_id, name=new_name, animal_type=new_type, age=new_age)
    assert update_response.status_code == 200
    updated_pet = update_response.json()
    assert updated_pet["id"] == pet_id, "ID питомца не должен меняться при обновлении данных"
    assert updated_pet["name"] == new_name
    assert updated_pet["animal_type"] == new_type
    assert int(updated_pet["age"]) == new_age

    # ---------- НЕГАТИВНЫЕ ТЕСТЫ (5 штук) ----------

    def test_get_api_key_negative_wrong_credentials():
        """Негатив: неверная комбинация email/пароля -> исключение ValueError (403)."""
        with pytest.raises(ValueError, match="Ошибка 403"):
            get_api_key("wrong@example.com", "wrong_pass")

    def test_create_pet_negative_negative_age():
        """Негатив: создание питомца с отрицательным возрастом -> ошибка валидации."""
        api_key = get_api_key(valid_email, valid_password)
        response = create_pet_simple(api_key, "Тест", "собака", -3)
        # Ожидаем, что сервер не примет отрицательный возраст
        # Возможны варианты: 400 Bad Request или 200 с сообщением об ошибке
        assert response.status_code != 200, "Отрицательный возраст не должен приниматься"
        # Дополнительно проверяем, что в теле ответа есть упоминание об ошибке
        data = response.json()
        assert "error" in str(data).lower() or "age" in str(data).lower()

    def test_set_pet_photo_negative_invalid_pet_id():
        """Негатив: попытка добавить фото к несуществующему питомцу -> 404 Not Found."""
        api_key = get_api_key(valid_email, valid_password)
        fake_pet_id = "00000000-0000-0000-0000-000000000000"

        current_dir = os.path.dirname(__file__)
        photo_path = os.path.join(current_dir, "test_images", "test_cat.jpg")
        assert os.path.exists(photo_path), "Тестовое фото не найдено"

        response = set_pet_photo(api_key, fake_pet_id, photo_path)
        assert response.status_code == 404, "Должен вернуться статус 404 (питомец не найден)"

    def test_update_pet_negative_not_exist():
        """Негатив: обновление несуществующего питомца -> 404 Not Found."""
        api_key = get_api_key(valid_email, valid_password)
        fake_pet_id = "00000000-0000-0000-0000-000000000000"
        response = update_pet_info(api_key, fake_pet_id, name="Новое имя")
        assert response.status_code == 404, "Обновление несуществующего питомца должно вернуть 404"

    def test_delete_pet_negative_invalid_key():
        """Негатив: удаление питомца с неверным API-ключом -> 403 Forbidden."""
        # Сначала создадим реального питомца, чтобы убедиться, что ключ не подходит
        valid_key = get_api_key(valid_email, valid_password)
        create_resp = create_pet_simple(valid_key, "Временный", "кот", 1)
        assert create_resp.status_code == 200
        pet_id = create_resp.json()["id"]

        # Пытаемся удалить с неверным ключом
        fake_key = "00000000-0000-0000-0000-000000000000"
        delete_resp = delete_pet(fake_key, pet_id)
        assert delete_resp.status_code == 403, "Неверный ключ должен давать 403"

        # Очистка: удаляем питомца правильным ключом, чтобы не засорять БД
        delete_pet(valid_key, pet_id)

# ---------- НЕГАТИВ ----------

def test_get_api_key_negative_wrong_credentials():
    """Негатив: неверная комбинация email/пароля."""
    with pytest.raises(ValueError, match="Ошибка 403"):
        get_api_key("wrong@example.com", "wrong_pass")

def test_create_pet_negative_missing_auth_key():
    """Негатив: создание питомца без API-ключа -> 403."""
    response = create_pet_simple("", "Тест", "собака", 3)
    assert response.status_code == 403

def test_set_pet_photo_negative_invalid_pet_id():
    """Негатив: фото для несуществующего питомца -> 500."""
    api_key = get_api_key(valid_email, valid_password)
    fake_pet_id = "00000000-0000-0000-0000-000000000000"
    current_dir = os.path.dirname(__file__)
    photo_path = os.path.join(current_dir, "test_images", "test_cat.jpg")
    assert os.path.exists(photo_path)
    response = set_pet_photo(api_key, fake_pet_id, photo_path)
    assert response.status_code == 500

def test_update_pet_negative_not_exist():
    """Негатив: обновление несуществующего питомца -> 400."""
    api_key = get_api_key(valid_email, valid_password)
    fake_pet_id = "00000000-0000-0000-0000-000000000000"
    response = update_pet_info(api_key, fake_pet_id, name="Новое имя")
    assert response.status_code == 400

def test_delete_pet_negative_invalid_key():
    """Негатив: удаление с неверным ключом -> 403."""
    valid_key = get_api_key(valid_email, valid_password)
    create_resp = create_pet_simple(valid_key, "Временный", "кот", 1)
    assert create_resp.status_code == 200
    pet_id = create_resp.json()["id"]
    fake_key = "00000000-0000-0000-0000-000000000000"
    delete_resp = delete_pet(fake_key, pet_id)
    assert delete_resp.status_code == 403
    delete_pet(valid_key, pet_id)  # очистка