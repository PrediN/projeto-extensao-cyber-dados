import requests
import time

def cep_para_latlong(cep):
    # 1. Busca endereço no ViaCEP
    cep = cep.replace("-", "")
    r = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
    dados = r.json()

    if "erro" in dados:
        raise ValueError(f"CEP {cep} não encontrado")

    endereco = f"{dados['logradouro']}, {dados['localidade']}, {dados['uf']}, Brasil"

    # 2. Geocodifica no Nominatim
    headers = {"User-Agent": "meu-projeto-faculdade/1.0"}  # obrigatório!
    r2 = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": endereco, "format": "json", "limit": 1},
        headers=headers
    )

    print("Calculando sua rota.....")
    time.sleep(1)  # respeitar rate limit do Nominatim (1 req/s)

    resultados = r2.json()
    if not resultados:
        raise ValueError(f"Endereço não geocodificado: {endereco}")

    lat = float(resultados[0]["lat"])
    lon = float(resultados[0]["lon"])
    return lat, lon


def calcular_rota(cep_origem, cep_destino):
    lat1, lon1 = cep_para_latlong(cep_origem)
    lat2, lon2 = cep_para_latlong(cep_destino)

    # OSRM espera lon,lat (invertido!)
    print("Calculando sua rota.....")
    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{lon1},{lat1};{lon2},{lat2}"
        f"?overview=full&geometries=geojson"
    )

    r = requests.get(url)
    dados = r.json()

    if dados.get("code") != "Ok":
        raise ValueError(f"Erro ao calcular rota: {dados.get('message', dados.get('code'))}")

    rota = dados["routes"][0]

    return {
        "distancia_km": rota["distance"] / 1000,
        "duracao_min": rota["duration"] / 60,
        "geometria": rota["geometry"],  # GeoJSON LineString da rota
        "origem": {"lat": lat1, "lon": lon1},
        "destino": {"lat": lat2, "lon": lon2},
    }


# Uso
cep1 = str(input("Insira aqui o primeiro CEP: "))
cep2 = str(input("Insira aqui o segundo CEP: "))
resultado = calcular_rota(cep1, cep2)
print(f"Distância: {resultado['distancia_km']:.1f} km")
print(f"Duração: {resultado['duracao_min']:.0f} min")