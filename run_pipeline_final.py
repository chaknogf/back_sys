import httpx
import json
import time
import sys

BASE = 'http://127.0.0.1:8000/fah'

# Usar streaming para ver progreso
print("Iniciando pipeline SIGSA-3...\n")
t0 = time.time()

with httpx.Client(timeout=1800) as client:
    # Login
    login = client.post(f'{BASE}/auth/login',
                        data={'username': 'admin', 'password': 'admin'})
    if login.status_code != 200:
        print(f'Login failed: {login.status_code}')
        sys.exit(1)
    token = login.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print('Login OK\n')

    # Streaming para ver progreso
    with client.stream('POST', f'{BASE}/sigsa3/asociar-pacientes-masivo-stream',
                       headers=headers) as resp:
        print(f'Status: {resp.status_code}\n')
        last_step = None
        for line in resp.iter_lines():
            if not line:
                continue
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                except json.JSONDecodeError:
                    print(f'  [RAW] {line[:200]}')
                    continue

                step = data.get('step', '?')
                progress = data.get('progress', '?')
                msg = data.get('message', '')
                elapsed = time.time() - t0

                # Imprimir cada cambio de paso o cada 30s
                if step != last_step or (elapsed % 30 < 1):
                    print(f'  [{elapsed:6.0f}s] step={step} progress={progress}% {msg}')
                    last_step = step

                if step == 'done':
                    elapsed = time.time() - t0
                    print(f'\n{"="*60}')
                    print(f'COMPLETADO EN {elapsed:.0f}s ({elapsed/60:.1f} min)')
                    print(f'{"="*60}')
                    print(json.dumps(data, indent=2, default=str))
                    break
                if step == 'error':
                    print(f'\nERROR: {json.dumps(data, indent=2, default=str)}')
                    break
            else:
                # Línea no estándar
                if line.strip():
                    print(f'  [OTHER] {line[:200]}')
