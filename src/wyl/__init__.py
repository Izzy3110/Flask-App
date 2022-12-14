def validate_post_data(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    if not data.get('name') or not isinstance(data['name'], str):
        return False
    if data.get('age') and not isinstance(data['age'], int):
        return False
    return True
