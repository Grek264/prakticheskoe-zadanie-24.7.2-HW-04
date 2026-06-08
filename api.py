import requests

pet_url = "https://petfriends.skillfactory.ru"

def get_api_key(email: str, password: str, base_url: str = pet_url) -> str:
    url = f"{base_url}/api/key"
    headers = {
        "accept": "application/json",
        "email": email,
        "password": password
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data["key"]
    elif response.status_code == 403:
        raise ValueError("Ошибка 403: неверная комбинация email и пароля.")
    else:
        response.raise_for_status()

def create_pet_simple(auth_key: str, name: str, animal_type: str, age: int):
    url = f"{pet_url}/api/create_pet_simple"
    headers = {"auth_key": auth_key}
    # Параметры передаются как form-data
    data = {
        "name": name,
        "animal_type": animal_type,
        "age": age
    }
    response = requests.post(url, headers=headers, data=data)
    return response

def get_pets_list(auth_key: str, filter: str = None) -> dict:
    url = f"{pet_url}/api/pets"
    headers = {"auth_key": auth_key}
    params = {}
    if filter:
        params["filter"] = filter
    response = requests.get(url, headers=headers, params=params)
    return response

def add_new_pet_with_photo(auth_key: str, name: str, animal_type: str, age: int, pet_photo_path: str):
    url = f"{pet_url}/api/pets"
    headers = {"auth_key": auth_key}
    with open(pet_photo_path, 'rb') as photo:
        files = {"pet_photo": photo}
        data = {
            "name": name,
            "animal_type": animal_type,
            "age": age
        }
        response = requests.post(url, headers=headers, data=data, files=files)
    return response

def set_pet_photo(auth_key: str, pet_id: str, pet_photo_path: str):
    url = f"{pet_url}/api/pets/set_photo/{pet_id}"
    headers = {"auth_key": auth_key}
    with open(pet_photo_path, 'rb') as photo:
        files = {"pet_photo": photo}
        response = requests.post(url, headers=headers, files=files)
    return response

def delete_pet(auth_key: str, pet_id: str) -> requests.Response:
    url = f"{pet_url}/api/pets/{pet_id}"
    headers = {"auth_key": auth_key}
    response = requests.delete(url, headers=headers)
    return response

def update_pet_info(auth_key: str, pet_id: str, name: str = None, animal_type: str = None, age: int = None) -> requests.Response:
    url = f"{pet_url}/api/pets/{pet_id}"
    headers = {"auth_key": auth_key}
    data = {}
    if name is not None:
        data["name"] = name
    if animal_type is not None:
        data["animal_type"] = animal_type
    if age is not None:
        data["age"] = age
    response = requests.put(url, headers=headers, data=data)
    return response