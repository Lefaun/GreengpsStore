import streamlit as st
import folium
from streamlit_folium import st_folium
import networkx as nx
import numpy as np

# 🔑 Usuários e senhas fixos
USUARIOS = {"admin": "1234", "user1": "abcd"}

# 🗺️ Lista fixa de localidades (latitude, longitude, nome)
LOCALIDADES = [
    {"nome": "Amadora", "lat": 38.7597, "lon": -9.2399},
    {"nome": "Queluz", "lat": 38.7566, "lon": -9.2545},
    {"nome": "Reboleira", "lat": 38.7599, "lon": -9.2245},
    {"nome": "Damaia", "lat": 38.7414, "lon": -9.2125},
    {"nome": "Alfragide", "lat": 38.7323, "lon": -9.2095},
    {"nome": "Benfica", "lat": 38.7503, "lon": -9.2037},
    {"nome": "Pontinha", "lat": 38.7713, "lon": -9.1964},
    {"nome": "Odivelas", "lat": 38.7920, "lon": -9.1835},
    {"nome": "Carnide", "lat": 38.7671, "lon": -9.1774},
    {"nome": "Lumiar", "lat": 38.7755, "lon": -9.1603}
]

# 🛒 Loja de produtos sustentáveis (nome, preço, link)
PRODUTOS = [
    {"nome": "Cesta de Frutas Orgânicas", "preco": 15, "link": "https://mercado-sustentavel.com/cesta"},
    {"nome": "Mel Puro de Apicultura Local", "preco": 10, "link": "https://mercado-sustentavel.com/mel"},
    {"nome": "Sabonete Natural de Alecrim", "preco": 5, "link": "https://mercado-sustentavel.com/sabonete"},
    {"nome": "Farinha de Aveia Orgânica", "preco": 7, "link": "https://mercado-sustentavel.com/aveia"},
    {"nome": "Óleo de Coco Extra Virgem", "preco": 12, "link": "https://mercado-sustentavel.com/oleo"},
]

# 🔐 Função de autenticação
def autenticar(usuario, senha):
    return USUARIOS.get(usuario) == senha

# 🛣️ Encontra o caminho mais sustentável entre os locais escolhidos
def encontrar_melhor_caminho(pontos):
    G = nx.Graph()
    for i, ponto in enumerate(pontos):
        G.add_node(i, pos=(ponto["lat"], ponto["lon"]))

    # Conectar os pontos com distâncias simuladas (simplificado)
    for i in range(len(pontos)):
        for j in range(i + 1, len(pontos)):
            dist = np.sqrt((pontos[i]["lat"] - pontos[j]["lat"])**2 + 
                           (pontos[i]["lon"] - pontos[j]["lon"])**2)
            G.add_edge(i, j, weight=dist)

    # Encontrar caminho otimizado (heurística)
    caminho = nx.approximation.traveling_salesman_problem(G, cycle=True)
    return [pontos[i] for i in caminho]

# 🗺️ Criar mapa interativo
def criar_mapa(pontos):
    centro = [np.mean([p["lat"] for p in pontos]), np.mean([p["lon"] for p in pontos])]
    mapa = folium.Map(location=centro, zoom_start=12)

    for ponto in pontos:
        folium.Marker(
            [ponto["lat"], ponto["lon"]],
            popup=ponto["nome"],
            tooltip=ponto["nome"]
        ).add_to(mapa)

    # Traçar caminho
    coords = [[p["lat"], p["lon"]] for p in pontos]
    coords.append(coords[0])  # Fecha o ciclo
    folium.PolyLine(coords, color="blue", weight=3, opacity=0.7).add_to(mapa)

    return mapa

# 🎯 Interface principal
def main():
    st.title("🚲 Otimizador de Percurso Sustentável & Loja Online")

    # 🔐 Login
    if "logado" not in st.session_state:
        st.session_state.logado = False

    if not st.session_state.logado:
        st.subheader("🔐 Login")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if autenticar(usuario, senha):
                st.session_state.logado = True
                st.success(f"Bem-vindo, {usuario}!")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos!")
        return

    # 🔓 Se logado, mostrar a aplicação
    st.sidebar.button("🚪 Sair", on_click=lambda: st.session_state.update({"logado": False}))

    # 📌 Seleção de pontos de partida e chegada
    locais_nomes = [p["nome"] for p in LOCALIDADES]
    inicio = st.selectbox("📍 Escolha o ponto de partida:", locais_nomes)
    destino = st.selectbox("🏁 Escolha o destino:", locais_nomes)

    if st.button("Calcular Percurso"):
        if inicio == destino:
            st.warning("⚠️ O ponto de partida e o destino são iguais!")
        else:
            locais_escolhidos = [p for p in LOCALIDADES if p["nome"] in [inicio, destino]]
            caminho_otimizado = encontrar_melhor_caminho(locais_escolhidos)

            # Salvar o caminho na sessão (EVITA QUE O MAPA DESAPAREÇA)
            st.session_state["mapa"] = criar_mapa(caminho_otimizado)

    # Mostrar o mapa armazenado
    if "mapa" in st.session_state:
        st_folium(st.session_state["mapa"], width=800, height=500)

    # 🛒 Loja Online
    st.subheader("🛒 Loja Sustentável")

    # Inicializa o carrinho de compras
    if "carrinho" not in st.session_state:
        st.session_state["carrinho"] = []

    # Exibir produtos
    for produto in PRODUTOS:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**{produto['nome']}** - 💰 {produto['preco']}€")
        with col2:
            if st.button("🛍️ Adicionar", key=produto["nome"]):
                st.session_state["carrinho"].append(produto)
        with col3:
            st.markdown(f"[🔗 Comprar]({produto['link']})")

    # 🛍️ Mostrar Carrinho
    if st.session_state["carrinho"]:
        st.subheader("🛍️ Meu Carrinho")
        total = sum(prod["preco"] for prod in st.session_state["carrinho"])
        for item in st.session_state["carrinho"]:
            st.write(f"✅ {item['nome']} - {item['preco']}€")
        st.markdown(f"**💰 Total: {total}€**")
        if st.button("🧹 Esvaziar Carrinho"):
            st.session_state["carrinho"] = []
            st.experimental_rerun()

if __name__ == "__main__":
    main()
