import httpx
import json
import time

BASE = 'http://127.0.0.1:8000/fah'

with httpx.Client(timeout=600) as client:
    # Login
    login = client.post(f'{BASE}/auth/login',
                        data={'username': 'admin', 'password': 'admin'})
    if login.status_code != 200:
        print(f'Login failed: {login.status_code} {login.text}')
        exit(1)
    token = login.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Login OK\n')

    # Ejecutar pipeline SIN streaming para ver resultado completo
    print('Ejecutando pipeline (sin streaming)...\n')
    t0 = time.time()

    resp = client.post(f'{BASE}/sigsa3/asociar-pacientes-masivo-stream',
                       headers=headers)
    elapsed = time.time() - t0

    print(f'Status: {resp.status_code}')
    print(f'Tiempo: {elapsed:.1f}s\n')

    # Intentar parsear como JSON primero
    try:
        data = resp.json()
        print(json.dumps(data, indent=2, default=str))
    except:
        # Si no es JSON, mostrar como texto
        print('Response (text):')
        print(resp.text[:5000])
