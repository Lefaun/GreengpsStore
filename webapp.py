import streamlit as st
import folium
from streamlit_folium import st_folium
import networkx as nx
import osmnx as ox
import pandas as pd

# 🔐 Usuários e senhas
USUARIOS = {"admin": "1234", "user1": "abcd"}

# 🗺️ Localidades (nome, coordenadas)
LOCALIDADES = {
    "Amadora": (38.7597, -9.2399),
    "Queluz": (38.7566, -9.2545),
    "Reboleira": (38.7599, -9.2245),
    "Damaia": (38.7414, -9.2125),
    "Alfragide": (38.7323, -9.2095),
    "Benfica": (38.7503, -9.2037),
    "Pontinha": (38.7713, -9.1964),
    "Odivelas": (38.7920, -9.1835),
    "Carnide": (38.7671, -9.1774),
    "Lumiar": (38.7755, -9.1603),
}

# 🛒 Loja (Produtos, preço, link)
PRODUTOS = [
    {"nome": "Cesta de Frutas Orgânicas", "preco": 15, "link": "https://mercado-sustentavel.com/cesta"},
    {"nome": "Mel Puro de Apicultura Local", "preco": 10, "link": "https://mercado-sustentavel.com/mel"},
    {"nome": "Sabonete Natural de Alecrim", "preco": 5, "link": "https://mercado-sustentavel.com/sabonete"},
]

# 🛣️ Carregar grafo de estradas de Lisboa para rotas otimizadas
grafo = ox.graph_from_place("Lisboa, Portugal", network_type="drive")

# 🔐 Função de autenticação
def autenticar(usuario, senha):
    return USUARIOS.get(usuario) == senha

# 🚗 Encontrar melhor rota via OSMnx (menos poluição e trânsito)
def encontrar_rota_otimizada(inicio, destino):
    #origem = ox.distance.nearest_nodes(grafo, LOCALIDADES[inicio][1], LOCALIDADES[inicio][0])
    #destino = ox.distance.nearest_nodes(grafo, LOCALIDADES[destino][1], LOCALIDADES[destino][0])
    origem = ox.distance.nearest_nodes(grafo, LOCALIDADES[inicio][1], LOCALIDADES[inicio][0], return_dist=True)[0]
    destino = ox.distance.nearest_nodes(grafo, LOCALIDADES[destino][1], LOCALIDADES[destino][0], return_dist=True)[0]
    caminho = nx.shortest_path(grafo, origem, destino, weight="length")  # Minimiza distância
    rota = [(grafo.nodes[n]["y"], grafo.nodes[n]["x"]) for n in caminho]
    
    grafo = ox.graph_from_place(
    ["Lisboa, Portugal", "Amadora, Portugal", "Queluz, Portugal"],
    network_type="drive"
)

    try:
        caminho = nx.shortest_path(grafo, origem, destino, weight="length")
        rota = [(grafo.nodes[n]["y"], grafo.nodes[n]["x"]) for n in caminho]
    except nx.NetworkXNoPath:
        st.error("🚨 Não há caminho disponível entre essas localidades!")
        return None

return rota


# 🗺️ Criar mapa com a rota escolhida
def criar_mapa(rota):
    centro = rota[0]  # Primeiro ponto da rota como centro
    mapa = folium.Map(location=centro, zoom_start=13)

    # Adicionar marcadores
    folium.Marker(rota[0], popup="Início", icon=folium.Icon(color="green")).add_to(mapa)
    folium.Marker(rota[-1], popup="Destino", icon=folium.Icon(color="red")).add_to(mapa)

    # Traçar a rota
    folium.PolyLine(rota, color="blue", weight=3, opacity=0.7).add_to(mapa)

    return mapa

# 🎯 Interface principal
def main():
    st.title("🚲 Roteiro Sustentável & Loja Online")

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

    # 🔓 Se logado, mostrar abas da aplicação
    abas = st.tabs(["🏡 Rotas Sustentáveis", "🛒 Loja", "📦 Meu Carrinho"])

    # 🏡 Aba 1: Seleção de Rota Sustentável
    with abas[0]:
        st.subheader("🌍 Planejar Percurso Sustentável")

        # Seleção de local de partida e destino
        locais = list(LOCALIDADES.keys())
        inicio = st.selectbox("📍 Escolha o ponto de partida:", locais)
        destino = st.selectbox("🏁 Escolha o destino:", locais)

        if st.button("Calcular Rota Sustentável"):
            if inicio == destino:
                st.warning("⚠️ Escolha um destino diferente do ponto de partida!")
            else:
                rota = encontrar_rota_otimizada(inicio, destino)

                # Salvar na sessão para evitar que o mapa desapareça
                st.session_state["mapa"] = criar_mapa(rota)

        # Mostrar mapa salvo
        if "mapa" in st.session_state:
            st_folium(st.session_state["mapa"], width=800, height=500)

    # 🛒 Aba 2: Loja Online
    with abas[1]:
        st.subheader("🛍️ Produtos Sustentáveis")

        for produto in PRODUTOS:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{produto['nome']}** - 💰 {produto['preco']}€")
            with col2:
                if st.button("🛍️ Adicionar", key=produto["nome"]):
                    if "carrinho" not in st.session_state:
                        st.session_state["carrinho"] = []
                    st.session_state["carrinho"].append(produto)
            with col3:
                st.markdown(f"[🔗 Comprar]({produto['link']})")

    # 📦 Aba 3: Carrinho
    with abas[2]:
        st.subheader("🛒 Meu Carrinho")

        if "carrinho" in st.session_state and st.session_state["carrinho"]:
            total = sum(prod["preco"] for prod in st.session_state["carrinho"])
            for item in st.session_state["carrinho"]:
                st.write(f"✅ {item['nome']} - {item['preco']}€")
            st.markdown(f"**💰 Total: {total}€**")

            if st.button("🛍️ Finalizar Compra"):
                st.success("Compra concluída com sucesso! 🛍️")
                st.session_state["carrinho"] = []

            if st.button("🧹 Esvaziar Carrinho"):
                st.session_state["carrinho"] = []
                st.experimental_rerun()
        else:
            st.write("🛒 Seu carrinho está vazio.")

if __name__ == "__main__":
 main()
