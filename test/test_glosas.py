import requests

BASE_URL = "http://127.0.0.1:8000"  # Cambia si tu API corre en otro host/puerto


def test_health():
    """Verifica que la API responda correctamente en el endpoint raíz."""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    print("✔ / OK")


def test_list_glosas():
    """Prueba el listado de glosas (GET /glosas)."""
    response = requests.get(f"{BASE_URL}/glosas")
    assert response.status_code == 200
    print("✔ /glosas OK")


def test_create_glosa():
    """Prueba la creación de una glosa (POST /glosas)."""
    data = {
        "factura": "FE_TEST_001",
        "motivo": "Prueba automatizada",
        "valor": 12345
    }
    response = requests.post(f"{BASE_URL}/glosas", json=data)
    assert response.status_code in [200, 201]
    print("✔ POST /glosas OK")


def test_get_glosa_by_id():
    """Prueba obtener una glosa por ID (GET /glosas/{id})."""
    glosa_id = 1  # Cambia si tienes otro ID válido
    response = requests.get(f"{BASE_URL}/glosas/{glosa_id}")
    assert response.status_code in [200, 404]
    print(f"✔ /glosas/{glosa_id} OK")
