import time
import requests
import os
from keycloak import KeycloakAdmin

def configurar_keycloak():
    # Detectar si estamos en Docker o en Local
    # Si existe la variable DATABASE_URL suele ser Docker
    dentro_de_docker = os.getenv("DATABASE_URL") is not None
    
    # En Docker, el host es el nombre del servicio en docker-compose
    host = "vinculo_keycloak" if dentro_de_docker else "localhost"
    URL = f"http://{host}:8080"
    
    ADMIN_USER = "admin"
    ADMIN_PASS = "admin"
    REALM_NAME = "Vinculo"
    CLIENT_ID = "vinculo-app"

    print(f"⏳ Esperando a que Keycloak responda en {URL}...")
    for _ in range(30):
        try:
            # Intentar conectar
            res = requests.get(f"{URL}/")
            if res.status_code == 200: 
                print("✅ Keycloak está vivo.")
                break
        except Exception:
            pass
        time.sleep(2)

    # 1. Loguearse en Master
    try:
        master_adm = KeycloakAdmin(
            server_url=URL+"/", 
            username=ADMIN_USER, 
            password=ADMIN_PASS, 
            realm_name="master", 
            verify=True
        )
    except Exception as e:
        print(f"❌ No se pudo conectar a Keycloak: {e}")
        return

    # 2. Asegurar Realm Vinculo
    try:
        if not any(r['realm'] == REALM_NAME for r in master_adm.get_realms()):
            master_adm.create_realm(payload={"realm": REALM_NAME, "enabled": True})
            print(f"✅ Realm '{REALM_NAME}' creado.")
        else:
            print(f"ℹ️ Realm '{REALM_NAME}' ya existe.")
    except Exception as e:
        print(f"❌ Error creando realm: {e}")

    # 3. Crear instancia para Realm Vinculo
    adm = KeycloakAdmin(
        server_url=URL+"/",
        username=ADMIN_USER,
        password=ADMIN_PASS,
        realm_name=REALM_NAME,
        user_realm_name="master",
        verify=True
    )

    # 4. Asegurar Cliente
    client_payload = {
        "clientId": CLIENT_ID,
        "publicClient": True,
        "directAccessGrantsEnabled": True,
        "standardFlowEnabled": True,
        "redirectUris": ["*"],
        "webOrigins": ["*"],
        "enabled": True
    }

    try:
        clients = adm.get_clients()
        existing = next((c for c in clients if c['clientId'] == CLIENT_ID), None)
        if existing:
            adm.update_client(client_id=existing['id'], payload=client_payload)
            print(f"🔄 Cliente '{CLIENT_ID}' actualizado.")
        else:
            adm.create_client(payload=client_payload)
            print(f"✅ Cliente '{CLIENT_ID}' creado.")
    except Exception as e:
        print(f"❌ Error en cliente: {e}")

    # 5. Asegurar Usuario
    try:
        username = "testuser"
        users = adm.get_users({"username": username})
        if not users:
            adm.create_user(payload={
                "username": username, "enabled": True, "email": "test@vinculo.com",
                "firstName": "Test", "lastName": "User",
                "credentials": [{"value": "password123", "type": "password", "temporary": False}]
            })
            print(f"✅ Usuario '{username}' creado.")
        else:
            print(f"ℹ️ Usuario '{username}' ya existe.")
    except Exception as e:
        print(f"❌ Error en usuario: {e}")

    print("\n🚀 CONFIGURACIÓN DE VINCULO COMPLETADA.")

if __name__ == "__main__":
    configurar_keycloak()
