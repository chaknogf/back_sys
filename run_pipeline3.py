import httpx
import json
import time

BASE = 'http://127.0.0.1:8000/fah'

with httpx.Client(timeout=1800) as client:  # 30 min timeout
    # Login
    login = client.post(f'{BASE}/auth/login',
                        data={'username': 'admin', 'password': 'admin'})
    if login.status_code != 200:
        print(f'Login failed: {login.status_code} {login.text}')
        exit(1)
    token = login.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Login OK\n')

    # Ejecutar pipeline (non-streaming - devuelve resultado final)
    print('Ejecutando pipeline (non-streaming)...\n')
    t0 = time.time()

    resp = client.post(f'{BASE}/sigsa3/asociar-pacientes-masivo',
                       headers=headers)
    elapsed = time.time() - t0

    print(f'Status: {resp.status_code}')
    print(f'Tiempo: {elapsed:.1f}s\n')

    try:
        data = resp.json()
        print(json.dumps(data, indent=2, default=str))
    except:
        print('Response (text):')
        print(resp.text[:10000])
