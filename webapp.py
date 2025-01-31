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
    st.title("🚲 Otimizador de Percurso Sustentável")

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
            # Filtrar locais escolhidos + intermediários sustentáveis
            locais_escolhidos = [p for p in LOCALIDADES if p["nome"] in [inicio, destino]]
            caminho_otimizado = encontrar_melhor_caminho(locais_escolhidos)

            # Criar e exibir o mapa
            mapa = criar_mapa(caminho_otimizado)
            st_folium(mapa, width=800, height=500)
# === Criando abas ===
aba = st.sidebar.radio("Escolha uma opção:", ["🛍️ Loja Sustentável", "🗺️ Planejar Rota"])

# === Loja Sustentável ===
if aba == "🛍️ Loja Sustentável":
    st.title("🛍️ Loja Sustentável")
    produtos = [
        {"nome": "Cesta Orgânica", "preco": 12.99, "img": "https://via.placeholder.com/150"},
        {"nome": "Sabonete Natural", "preco": 7.50, "img": "https://via.placeholder.com/150"},
        {"nome": "Bolsa Ecológica", "preco": 15.00, "img": "https://via.placeholder.com/150"},
        {"nome": "Kit Bambu", "preco": 9.99, "img": "https://via.placeholder.com/150"},
        {"nome": "Mel Orgânico", "preco": 18.50, "img": "https://via.placeholder.com/150"},
        {"nome": "Horta Caseira", "preco": 25.00, "img": "https://via.placeholder.com/150"},
        {"nome": "Cosméticos Naturais", "preco": 19.99, "img": "https://via.placeholder.com/150"},
        {"nome": "Chá Artesanal", "preco": 10.99, "img": "https://via.placeholder.com/150"},
        {"nome": "Velas Ecológicas", "preco": 14.50, "img": "https://via.placeholder.com/150"},
    ]

    def adicionar_ao_carrinho(produto):
        if produto in st.session_state["carrinho"]:
            st.session_state["carrinho"][produto] += 1
        else:
            st.session_state["carrinho"][produto] = 1

    cols = st.columns(3)

    for i, produto in enumerate(produtos):
        with cols[i % 3]:
            st.image(produto["img"], caption=produto["nome"])
            st.write(f"💲 {produto['preco']:.2f}")
            if st.button(f"🛒 Adicionar {produto['nome']}", key=produto["nome"]):
                adicionar_ao_carrinho(produto["nome"])
                st.success(f"{produto['nome']} adicionado ao carrinho!")

    st.sidebar.title("🛒 Carrinho de Compras")
    if st.session_state["carrinho"]:
        total = 0
        for item, qtd in st.session_state["carrinho"].items():
            preco = next(p["preco"] for p in produtos if p["nome"] == item)
            subtotal = preco * qtd
            total += subtotal
            st.sidebar.write(f"{item} ({qtd}x) - 💲{subtotal:.2f}")

        st.sidebar.write(f"**Total: 💲{total:.2f}**")
        if st.sidebar.button("✅ Finalizar Pedido"):
            st.sidebar.success("Pedido realizado com sucesso! 🌱")
            st.session_state["carrinho"] = {}
    else:
        st.sidebar.write("Seu carrinho está vazio.")

if __name__ == "__main__":
    main()
