import time
import requests


HA灵牌 = '****'
HA网址 = 'http://homeassistant.local:8123'


def 获取游戏卧室温度() -> list[float]:
    res = requests.get('http://127.0.0.1:18765/rooms').json()
    return [r['temperature'] for r in res if r['role'] == 'Bedroom' and r['owners']]


def 获取空调id() -> str:
    r = requests.get(f'{HA网址}/api/states', headers={'Authorization': f'Bearer {HA灵牌}'})
    r.raise_for_status()
    res = r.json()
    climates = [s for s in res if s['entity_id'].startswith('climate.')]
    for c in climates:
        if 'cool' in c.get('attributes', {}).get('hvac_modes', []):
            return c['entity_id']
    raise RuntimeError('找不到空调！')


if __name__ == '__main__':
    空调 = 获取空调id()
    headers = {'Authorization': f'Bearer {HA灵牌}'}
    while True:
        time.sleep(1)
        游戏的所有卧室温度 = 获取游戏卧室温度()
        if not 游戏的所有卧室温度:
            continue
        目标温度 = max(16, min(31, round(sum(游戏的所有卧室温度)/len(游戏的所有卧室温度))))
        s = requests.get(f'{HA网址}/api/states/{空调}', headers=headers).json()
        if s['state'] == 'off':
            requests.post(f'{HA网址}/api/services/climate/turn_on', headers=headers, json={'entity_id': 空调})
        if s['state'] != 'cool':
            requests.post(f'{HA网址}/api/services/climate/set_hvac_mode', headers=headers, json={'entity_id': 空调, 'hvac_mode': 'cool'})
        if s['attributes'].get('temperature') != 目标温度:
            requests.post(f'{HA网址}/api/services/climate/set_temperature', headers=headers, json={'entity_id': 空调, 'temperature': 目标温度})
            print(f'空调设为{目标温度}度！')
