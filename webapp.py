import streamlit as st
import folium
from streamlit_folium import st_folium
import networkx as nx
import osmnx as ox
import time

# Configuração do layout
tabs = st.tabs(["Mapa", "Loja Online"])

# Simulação de login
st.sidebar.title("Login")
usuario = st.sidebar.text_input("Usuário", value="admin")
senha = st.sidebar.text_input("Senha", type="password", value="1234", key="password")

if usuario == "admin" and senha == "1234":
    with tabs[0]:
        st.title("🚴 Otimizador de Percurso - GPS Ativo")

        LOCALIDADES = {
            "Amadora": (38.7597, -9.2249),
            "Queluz": (38.7566, -9.2546),
            "Lisboa": (38.7169, -9.1399),
            "Sintra": (38.8029, -9.3817),
            "Oeiras": (38.6979, -9.3017),
            "Cascais": (38.6970, -9.4223),
            "Loures": (38.8309, -9.1685),
            "Almada": (38.6766, -9.1668),
            "Setúbal": (38.5243, -8.8882)
        }

        inicio = st.selectbox("Escolha o ponto de partida", list(LOCALIDADES.keys()))
        destino = st.selectbox("Escolha o destino", list(LOCALIDADES.keys()))
        calcular_rota = st.button("Calcular Rota")

        if calcular_rota:
            try:
                # Criar grafo da rede viária para pedestres 🚶‍♂️
                grafo = ox.graph_from_place("Lisboa, Portugal", network_type="walk")
                
                # Encontrar os nós mais próximos das coordenadas selecionadas
                origem = ox.distance.nearest_nodes(grafo, LOCALIDADES[inicio][1], LOCALIDADES[inicio][0])
                destino = ox.distance.nearest_nodes(grafo, LOCALIDADES[destino][1], LOCALIDADES[destino][0])
                
                # Calcular o caminho mais curto 🚲
                caminho = nx.shortest_path(grafo, origem, destino, weight="length")
                coords = [(grafo.nodes[n]['y'], grafo.nodes[n]['x']) for n in caminho]

                # Criar mapa
                mapa = folium.Map(location=[(LOCALIDADES[inicio][0] + LOCALIDADES[destino][0]) / 2, 
                                            (LOCALIDADES[inicio][1] + LOCALIDADES[destino][1]) / 2], zoom_start=14)

                # Adicionar linha azul (como no GPS) 🟦
                folium.PolyLine(coords, color="blue", weight=6).add_to(mapa)

                # Adicionar um marcador inicial para a bicicleta 🚴‍♂️
                bicicleta = folium.Marker(
                    location=coords[0],
                    icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
                )
                bicicleta.add_to(mapa)

                # Exibir o mapa inicial
                mapa_placeholder = st_folium(mapa, width=800)

                # Simulação de navegação GPS ⏳
                for i in range(len(coords)):
                    mapa = folium.Map(location=coords[i], zoom_start=14)

                    # Linha azul sólida 🟦
                    folium.PolyLine(coords, color="blue", weight=6).add_to(mapa)

                    # Atualizar a posição da bicicleta 🚴‍♂️
                    bicicleta = folium.Marker(
                        location=coords[i],
                        icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
                    )
                    bicicleta.add_to(mapa)

                    # Atualiza o mapa
                    mapa_placeholder = st_folium(mapa, width=800)
                    time.sleep(1)  # Simula o deslocamento GPS

            except nx.NetworkXNoPath:
                st.error("❌ Não foi possível encontrar um caminho entre as localidades selecionadas.")
            except KeyError:
                st.error("❌ Erro ao acessar as localidades. Verifique as seleções e tente novamente.")
        else:
            mapa = folium.Map(location=[38.7169, -9.1399], zoom_start=11)
            st_folium(mapa, width=800)

    with tabs[1]:  # Correção da posição da aba Loja Online
        st.title("🛍️ Loja Sustentável")

        # Lista de produtos
        produtos = [
            {"nome": "Cesta Orgânica", "preco": 12.99, "img": "Horta.png"},
            {"nome": "Sabonete Natural", "preco": 7.50, "img": "soap.png"},
            {"nome": "Bolsa Ecológica", "preco": 15.00, "img": "BolsaCometico.png"},
            {"nome": "Kit Bambu", "preco": 9.99, "img": "KitBambu.png"},
            {"nome": "Mel Orgânico", "preco": 18.50, "img": "mel.png"},
            {"nome": "Horta Caseira", "preco": 25.00, "img": "Horta.jpg"},
            {"nome": "Cosméticos Naturais", "preco": 19.99, "img": "Cosmetico.png"},
            {"nome": "Chá Artesanal", "preco": 10.99, "img": "Chá.jpg"},
            {"nome": "Velas Ecológicas", "preco": 14.50, "img": "Velas.png"},
        ]

        # Inicializar carrinho
        st.session_state.setdefault("carrinho", {})

        def adicionar_ao_carrinho(produto):
            if produto in st.session_state["carrinho"]:
                st.session_state["carrinho"][produto] += 1
            else:
                st.session_state["carrinho"][produto] = 1

        cols = st.columns(3)  # Ajusta a disposição dos produtos

        for i, produto in enumerate(produtos):
            with cols[i % 3]:
                st.image(produto["img"], caption=produto["nome"])
                st.write(f"€ {produto['preco']:.2f}")
                if st.button(f"🛒 Adicionar {produto['nome']}", key=produto["nome"]):
                    adicionar_ao_carrinho(produto["nome"])
                    st.success(f"{produto['nome']} adicionado ao carrinho!")

        # Exibir Carrinho
        st.sidebar.title("🛒 Carrinho de Compras")
        if st.session_state["carrinho"]:
            total = 0
            for item, qtd in st.session_state["carrinho"].items():
                preco = next(p["preco"] for p in produtos if p["nome"] == item)
                subtotal = preco * qtd
                total += subtotal
                st.sidebar.write(f"{item} ({qtd}x) - 💲{subtotal:.2f}")

            st.sidebar.write(f"**Total: €{total:.2f}**")
            if st.sidebar.button("✅ Finalizar Pedido"):
                st.sidebar.success("Pedido realizado com sucesso! 🌱")
                st.session_state["carrinho"] = {}
        else:
            st.sidebar.write("Seu carrinho está vazio.")

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

# Função para enviar o e-mail
def enviar_email(pedido, total):
    remetente = "seuemail@gmail.com"  # Substitua pelo seu e-mail
    senha = "suasenha"  # Use senha do app se necessário (não use senhas reais diretamente no código)
    destinatario = "seuemail@gmail.com"  # E-mail para onde o pedido será enviado

    msg = MIMEMultipart()
    msg["From"] = remetente
    msg["To"] = destinatario
    msg["Subject"] = "Novo Pedido - Loja Sustentável"

    corpo_email = f"""
    Novo pedido recebido! 🛍️
    
    Produtos:
    {pedido}
    
    Total: 💲{total:.2f}
    
    Forma de pagamento: Transferência bancária / MB Way / PayPal
    Endereço de entrega: [Preencher com o endereço do cliente]

    Obrigado por sua compra! 🌱
    """

    msg.attach(MIMEText(corpo_email, "plain"))

    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remetente, senha)
        servidor.sendmail(remetente, destinatario, msg.as_string())
        servidor.quit()
        return True
    except Exception as e:
        return False


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

# Configuração do e-mail
EMAIL_REMETENTE = "seuemail@gmail.com"  # Substitua pelo seu e-mail
SENHA_EMAIL = "suasenha"  # Use uma senha de aplicativo para maior segurança
EMAIL_DESTINATARIO = "seuemail@gmail.com"  # Para onde o pedido será enviado
SMTP_SERVIDOR = "smtp.gmail.com"
SMTP_PORTA = 587

def enviar_email(pedido, total, endereco, pagamento):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINATARIO
    msg["Subject"] = "Novo Pedido - Loja Sustentável"

    corpo_email = f"""
    🛍️ Novo pedido recebido!
    
    Produtos:
    {pedido}
    
    Total: 💲{total:.2f}
    
    Forma de pagamento: {pagamento}
    Endereço de entrega: {endereco}
    
    Obrigado por sua compra! 🌱
    """
    msg.attach(MIMEText(corpo_email, "plain"))

    try:
        servidor = smtplib.SMTP(SMTP_SERVIDOR, SMTP_PORTA)
        servidor.starttls()
        servidor.login(EMAIL_REMETENTE, SENHA_EMAIL)
        servidor.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, msg.as_string())
        servidor.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

# Inicializa o carrinho na sessão
if "carrinho" not in st.session_state:
    st.session_state["carrinho"] = {}


st.sidebar.title("🛒 Carrinho de Compras")

if st.session_state["carrinho"]:
    total = 0
    pedido = ""
    for item, qtd in st.session_state["carrinho"].items():
        preco = next(p["preco"] for p in produtos if p["nome"] == item)
        subtotal = preco * qtd
        total += subtotal
        pedido += f"{item} ({qtd}x) - 💲{subtotal:.2f}\n"

    st.sidebar.write(f"**Total: €{total:.2f}**")
    endereco = st.sidebar.text_input("📍 Endereço de Entrega")
    pagamento = st.sidebar.selectbox("💳 Forma de Pagamento", ["Transferência Bancária", "MB Way", "PayPal"])

    if st.sidebar.button("✅ Finalizar Pedido"):
        if endereco:
            if enviar_email(pedido, total, endereco, pagamento):
                st.sidebar.success("Pedido realizado com sucesso! Um e-mail foi enviado. 📩")
                st.session_state["carrinho"] = {}
            else:
                st.sidebar.error("❌ Erro ao enviar e-mail. Tente novamente.")
        else:
            st.sidebar.error("❌ Informe um endereço de entrega.")
else:
    st.sidebar.write("Seu carrinho está vazio.")


#else:
    #st.sidebar.error("❌ Credenciais incorretas")
