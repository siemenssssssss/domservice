import requests
import json

# Твои ключи DaData
DADATA_API_KEY = '8e980dcea9953279c53d89c4d290ee1721a18ff9'
DADATA_SECRET_KEY = 'd576ce94d243baaec1a3ba56ab93779cff4759e1'

def get_full_house_info(address):
    """
    Получает максимально полную информацию о доме по адресу.
    Возвращает словарь со всеми доступными данными.
    """
    headers = {
        'Authorization': f'Token {DADATA_API_KEY}',
        'X-Secret': f'{DADATA_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    
    # Используем метод clean для максимально детального разбора
    clean_payload = {
        "structure": ["AS_IS", "ADDRESS"],
        "data": [["", address]]
    }
    
    try:
        # Очистка и обогащение адреса
        response = requests.post(
            'https://dadata.ru/api/v2/clean',
            json=clean_payload,
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        
        if not result.get('data'):
            return None
            
        data = result['data'][0][1]  # Берём второй элемент с обогащёнными данными
        
        # Преобразуем данные в нужный формат
        house_info = {
            # Адресная часть
            'address_full': data.get('result', ''),
            'address_source': data.get('source', ''),
            'postal_code': data.get('postal_code', ''),
            'country': data.get('country', ''),
            'federal_district': data.get('federal_district', ''),
            'timezone': data.get('timezone', ''),
            
            # Региональная часть
            'region': data.get('region', ''),
            'region_type': data.get('region_type', ''),
            'area': data.get('area', ''),
            'city': data.get('city', ''),
            'city_district': data.get('city_district', ''),
            'settlement': data.get('settlement', ''),
            
            # Улица
            'street': data.get('street', ''),
            'street_type': data.get('street_type', ''),
            
            # Дом и квартира
            'house': data.get('house', ''),
            'house_type': data.get('house_type', ''),
            'block': data.get('block', ''),
            'flat': data.get('flat', ''),
            'flat_area': data.get('flat_area'),
            
            # Характеристики дома (из дополнительных полей)
            'building_year': data.get('house_build_year'),
            'floors': data.get('house_floors'),
            'flat_count': data.get('house_flat_count'),
            'material': data.get('house_material'),
            'cadastral_number': data.get('house_cadnum'),
            
            # Цены
            'flat_price': data.get('flat_price'),
            'square_meter_price': data.get('square_meter_price'),
            
            # Координаты
            'geo_lat': data.get('geo_lat'),
            'geo_lon': data.get('geo_lon'),
            'geo_quality': data.get('qc_geo'),
            
            # Метро (может быть массивом)
            'metro': data.get('metro', []),
            
            # Идентификаторы
            'fias_id': data.get('fias_id', ''),
            'house_fias_id': data.get('house_fias_id', ''),
            'street_fias_id': data.get('street_fias_id', ''),
            
            # Коды проверки
            'qc': data.get('qc'),
            'qc_geo': data.get('qc_geo'),
        }
        
        return house_info
        
    except requests.exceptions.RequestException as e:
        print(f'Ошибка DaData: {e}')
        return None