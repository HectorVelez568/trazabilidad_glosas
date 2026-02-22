import requests

BASE_URL = "http://127.0.0.1:8000"  # Cambia si usas otro host/puerto

def test_health():
    """Prueba si la API está en funcionamiento."""
    try:
        response = requests.get(f"{BASE_URL}/")
        print("[/] Estado API:", response.status_code, response.json())
    except Exception as e:
        print("Error al conectar con la API:", e)

def test_list_glosas():
    """Prueba el endpoint de listado de glosas (GET /glosas)."""
    try:
        response = requests.get(f"{BASE_URL}/glosas")
        print("[/glosas] Respuesta:", response.status_code)
        if response.status_code == 200:
            print("Datos:", response.json())
    except Exception as e:
        print("Error en /glosas:", e)

def test_create_glosa():
    """Prueba el endpoint para crear una glosa (POST /glosas)."""
    data = {
        "factura": "FE12345",
        "motivo": "Glosa por inconsistencia",
        "valor": 10000
    }
    try:
        response = requests.post(f"{BASE_URL}/glosas", json=data)
        print("[POST /glosas] Respuesta:", response.status_code)
        print("Datos:", response.json())
    except Exception as e:
        print("Error en POST /glosas:", e)

def test_get_glosa_by_id(glosa_id):
    """Prueba obtener una glosa por ID (GET /glosas/{id})."""
    try:
        response = requests.get(f"{BASE_URL}/glosas/{glosa_id}")
        print(f"[/glosas/{glosa_id}] Respuesta:", response.status_code)
        print("Datos:", response.json())
    except Exception as e:
        print(f"Error en /glosas/{glosa_id}:", e)

if __name__ == "__main__":
    test_health()
    test_list_glosas()
    test_create_glosa()
    test_get_glosa_by_id(1)  # Cambia el ID según tu base de datos
