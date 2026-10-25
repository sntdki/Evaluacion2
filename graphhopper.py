import os
import requests
import urllib.parse

route_url = "https://graphhopper.com/api/1/route?"
key = os.environ.get("GRAPHHOPPER_API_KEY")
if not key:
    print("Falta la API Key. Defina la variable de entorno GRAPHHOPPER_API_KEY.")
    raise SystemExit(1)

def geocodificar(ubicacion, key):
    while ubicacion == "":
        ubicacion = input("Ingrese nuevamente la ubicación: ")
    url = "https://graphhopper.com/api/1/geocode?" + urllib.parse.urlencode(
        {"q": ubicacion, "limit": "1", "locale": "es", "key": key})
    r = requests.get(url)
    estado = r.status_code
    if estado == 200 and r.json().get("hits"):
        hit = r.json()["hits"][0]
        nombre = f"{hit.get('name', ubicacion)}, {hit.get('country', '')}".strip(", ")
        return estado, hit["point"]["lat"], hit["point"]["lng"], nombre
    return estado, None, None, ubicacion

SALIR = ["s", "salir"]
while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Perfiles de vehículo disponibles en GraphHopper: car, bike, foot")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    vehiculo = input("Ingrese un perfil de vehículo (o 's' / 'salir' para terminar): ").lower()
    if vehiculo in SALIR:
        print("Saliendo del programa. ¡Hasta luego!")
        break
    if vehiculo not in ["car", "bike", "foot"]:
        vehiculo = "car"
        print("Perfil no válido. Se usará 'car'.")

    loc1 = input("Ubicación de origen (o 's' / 'salir' para terminar): ")
    if loc1.lower() in SALIR:
        print("Saliendo del programa. ¡Hasta luego!")
        break
    loc2 = input("Destino (o 's' / 'salir' para terminar): ")
    if loc2.lower() in SALIR:
        print("Saliendo del programa. ¡Hasta luego!")
        break

    est1, lat1, lng1, nom1 = geocodificar(loc1, key)
    est2, lat2, lng2, nom2 = geocodificar(loc2, key)
    if lat1 is None or lat2 is None:
        print("No se pudo encontrar el origen o el destino. Intente nuevamente.")
        continue

    url = route_url + urllib.parse.urlencode([
        ("key", key), ("vehicle", vehiculo), ("locale", "es"),
        ("point", f"{lat1},{lng1}"), ("point", f"{lat2},{lng2}")])
    r = requests.get(url)
    print("=================================================")
    print("Estado de la API de rutas:", r.status_code)
    if r.status_code == 200:
        ruta = r.json()["paths"][0]
        km = ruta["distance"] / 1000
        millas = km / 1.609
        seg = int(ruta["time"] / 1000)
        print("=================================================")
        print(f"Direcciones desde {nom1} hasta {nom2} en modo {vehiculo}")
        print("=================================================")
        print(f"Distancia recorrida: {millas:.2f} millas / {km:.2f} km")
        print(f"Duración del viaje: {seg // 3600:02d}:{(seg % 3600) // 60:02d}:{seg % 60:02d}")
        print("=================================================")
        for paso in ruta["instructions"]:
            d_km = paso["distance"] / 1000
            print(f"{paso['text']} ( {d_km:.2f} km / {d_km / 1.609:.2f} millas )")
        print("=================================================")
    else:
        print("Mensaje de error:", r.json().get("message"))