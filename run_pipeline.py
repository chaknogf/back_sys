import httpx
import json
import time

BASE = 'http://127.0.0.1:8000/fah'

with httpx.Client(timeout=300) as client:
    # Login (form data OAuth2)
    login = client.post(f'{BASE}/auth/login',
                        data={'username': 'admin', 'password': 'admin'})
    if login.status_code != 200:
        print(f'Login failed: {login.status_code} {login.text}')
        exit(1)
    token = login.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Login OK\n')

    # Ejecutar pipeline con streaming
    print('Ejecutando pipeline...\n')
    t0 = time.time()

    with client.stream('POST', f'{BASE}/sigsa3/asociar-pacientes-masivo-stream',
                       headers=headers) as resp:
        print(f'Status: {resp.status_code}\n')
        for line in resp.iter_lines():
            print(f'RAW: {line!r}')
            if line.startswith('data: '):
                data = json.loads(line[6:])
                step = data.get('step', '?')
                progress = data.get('progress', '?')
                msg = data.get('message', '')

                elapsed = time.time() - t0
                print(f'  -> [{step}] {progress}% ({elapsed:.1f}s) - {msg}')

                if step == 'done':
                    elapsed = time.time() - t0
                    print(f'\n{"="*60}')
                    print(f'COMPLETADO EN {elapsed:.1f}s')
                    print(f'{"="*60}')
                    print(json.dumps(data, indent=2, default=str))
                    break
                if step == 'error':
                    print(f'\nERROR: {data}')
                    break
