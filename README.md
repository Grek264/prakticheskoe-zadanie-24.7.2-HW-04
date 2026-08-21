# API-тесты PetFriends

Учебный проект автоматизированного тестирования REST API сервиса PetFriends.

## Что проверяется

- получение API-ключа;
- создание питомца с фотографией и без неё;
- получение списка питомцев;
- добавление фотографии;
- изменение данных питомца;
- удаление питомца;
- негативные сценарии для авторизации, идентификаторов и обязательных параметров.

## Стек

- Python;
- Pytest;
- Requests;
- REST API, JSON и HTTP-коды ответа.

## Установка

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install pytest requests
```

## Настройка тестовых данных

Учётные данные не хранятся в репозитории. Перед запуском задайте переменные окружения:

```powershell
$env:PETFRIENDS_EMAIL = "your-test-email@example.com"
$env:PETFRIENDS_PASSWORD = "your-test-password"
```

Используйте отдельную тестовую учётную запись и не публикуйте заполненный `.env`.

## Запуск

```bash
pytest tests/test_pet_friends.py -v
```

Тесты создают, изменяют и удаляют данные во внешнем сервисе. Результат зависит от доступности PetFriends и текущего поведения его API.

## Структура

- `api.py` — клиентские методы для API;
- `tests/test_pet_friends.py` — позитивные и негативные проверки;
- `tests/test_images/` — тестовое изображение;
- `tests/test_user_log.py` — чтение учётных данных из окружения.
