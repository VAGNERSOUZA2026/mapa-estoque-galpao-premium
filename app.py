import streamlit as st
import json
import os
import qrcode
import io
import pandas as pd

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Sistema WMS - Estoque Galpão de Vinhos",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded"
)

ARQUIVO_BANCO = "estoque_galpao.json"

# ---------------------------------------------------------
# FUNÇÕES DE BANCO DE DADOS (JSON)
# ---------------------------------------------------------
def carregar_dados():
    if not os.path.exists(ARQUIVO_BANCO):
        dados_iniciais = [
            {
                "id": 1,
                "nome": "Château Margaux Premier Grand Cru",
                "tipo": "Tinto",
                "safra": "2015",
                "volume": "750ml",
                "lado": "A",
                "caixa": "CX-102",
                "pallet": "Corredor 01 - Pallet 01",
                "quantidade": 24
            },
            {
                "id": 2,
                "nome": "Puligny-Montrachet Domaine",
                "tipo": "Branco",
                "safra": "2020",
                "volume": "750ml",
                "lado": "B",
                "caixa": "CX-205",
                "pallet": "Corredor 01 - Pallet 02",
                "quantidade": 12
            },
            {
                "id": 3,
                "nome": "Dom Pérignon Vintage",
                "tipo": "Espumante",
                "safra": "2012",
                "volume": "750ml",
                "lado": "A",
                "caixa": "CX-014",
                "pallet": "Corredor 02 - Pallet 01",
                "quantidade": 36
            }
        ]
        salvar_dados(dados_iniciais)
        return dados_iniciais
    try:
        with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def salvar_dados(dados):
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# ---------------------------------------------------------
# FUNÇÕES DE UTILIDADE E ESTILO
# ---------------------------------------------------------
def badge_tipo_html(tipo):
    cores = {
        "Tinto": "background-color: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5;",
        "Branco": "background-color: #FEF3C7; color: #92400E; border: 1px solid #FCD34D;",
        "Rosé": "background-color: #FCE7F3; color: #9D174D; border: 1px solid #FBCFE8;",
        "Espumante": "background-color: #CCFBF1; color: #115E59; border: 1px solid #99F6E4;"
    }
    estilo = cores.get(tipo, "background-color: #E5E7EB; color: #374151;")
    return f'<span style="{estilo} padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">{tipo}</span>'

def gerar_qr_code(link_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(link_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

# ---------------------------------------------------------
# CARREGAMENTO E LEITURA DA URL (PARÂMETROS DE QR CODE)
# ---------------------------------------------------------
dados_estoque = carregar_dados()

# Pega parâmetros da URL gerados pela leitura do QR Code
params = st.query_params
pallet_url = params.get("pallet") or params.get("p")

# ---------------------------------------------------------
# CABEÇALHO PRINCIPAL
# ---------------------------------------------------------
st.markdown("<h1 style='color: #4A0E17;'>🍷 WMS Galpão - Gerenciamento de Estoque de Vinhos</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# MODO 1: TELA AUTOMÁTICA DE LEITURA DO QR CODE
# ---------------------------------------------------------
if pallet_url:
    st.success("✅ QR Code lido com sucesso!")
    
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown(f"## 📍 Vinhos alocados em: <span style='color:#8B1E2D;'>{pallet_url}</span>", unsafe_allow_html=True)
    with col_t2:
        if st.button("⬅️ Ver Todo o Estoque / Menu", use_container_width=True):
            st.query_params.clear()
            st.rerun()

    st.markdown("---")

    # Filtra os vinhos localizados no pallet recebido via URL
    termo = pallet_url.strip().lower()
    encontrados = [
        v for v in dados_estoque 
        if termo in str(v.get("pallet", "")).lower() or str(v.get("pallet", "")).lower() in termo
    ]

    if not encontrados:
        st.info(f"🍷 Nenhum vinho cadastrado no pallet **{pallet_url}** até o momento.")
    else:
        for v in encontrados:
            with st.container():
                c1, c2, c3 = st.columns([3, 2, 1])
                with c1:
                    st.markdown(f"### {v['nome']} {badge_tipo_html(v.get('tipo',''))}", unsafe_allow_html=True)
                    st.write(f"**Lado:** {v.get('lado','—')} | **Caixa:** {v.get('caixa','—')} | **Volume:** {v.get('volume','—')}")
                with c2:
                    st.write(f"**Safra:** {v.get('safra','—')}")
                    st.write(f"**Quantidade:** `{v.get('quantidade', 0)} garrafas`")
                with c3:
                    st.markdown(f"📍 **{v.get('pallet','—')}**")
                st.markdown("---")
    
    st.stop()  # Interrompe o restante para focar apenas na tela do QR Code

# ---------------------------------------------------------
# MODO 2: SISTEMA COMPLETO (NAVEGAÇÃO POR ABAS)
# ---------------------------------------------------------
st.sidebar.header("📌 Navegação")
opcao_menu = st.sidebar.radio(
    "Selecione uma opção:",
    ["📦 Visualizar Estoque", "➕ Cadastrar Vinho", "🔲 Gerar QR Codes de Pallets", "📊 Relatórios"]
)

# Base URL para geração dos QR Codes
url_app_base = st.sidebar.text_input(
    "URL Base do App (p/ QR Code):", 
    value="https://mapa-estoque-galpao-premium-vbewrgwbe5ktw8ptefwxmf.streamlit.app"
)

# ---------------------------------------------------------
# ABA 1: VISUALIZAR ESTOQUE
# ---------------------------------------------------------
if opcao_menu == "📦 Visualizar Estoque":
    st.subheader("📋 Lista Geral de Produtos")
    
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        busca = st.text_input("🔍 Buscar por Nome, Pallet ou Caixa:", "")
    with col_f2:
        filtro_tipo = st.selectbox("Filtrar por Tipo:", ["Todos", "Tinto", "Branco", "Rosé", "Espumante"])

    produtos_filtrados = dados_estoque
    if filtro_tipo != "Todos":
        produtos_filtrados = [p for p in produtos_filtrados if p.get("tipo") == filtro_tipo]
    
    if busca:
        b = busca.lower()
        produtos_filtrados = [
            p for p in produtos_filtrados 
            if b in p.get("nome", "").lower() or b in p.get("pallet", "").lower() or b in p.get("caixa", "").lower()
        ]

    st.write(f"Exibindo **{len(produtos_filtrados)}** item(ns).")
    st.markdown("---")

    for p in produtos_filtrados:
        with st.container():
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            with c1:
                st.markdown(f"**{p['nome']}** {badge_tipo_html(p.get('tipo',''))}", unsafe_allow_html=True)
                st.caption(f"Volume: {p.get('volume','—')} | Safra: {p.get('safra','—')}")
            with c2:
                st.write(f"📍 **Pallet:** {p.get('pallet','—')}")
                st.write(f"📦 **Caixa:** {p.get('caixa','—')} (Lado {p.get('lado','—')})")
            with c3:
                st.write(f"🔢 **Estoque:** `{p.get('quantidade',0)} garrafas`")
            with c4:
                url_qr = f"{url_app_base}/?pallet={p.get('pallet','')}"
                st.markdown(f"[🔗 Testar QR]({url_qr})")
            st.markdown("---")

# ---------------------------------------------------------
# ABA 2: CADASTRAR VINHO
# ---------------------------------------------------------
elif opcao_menu == "➕ Cadastrar Vinho":
    st.subheader("➕ Novo Cadastro no Estoque")
    
    with st.form("form_cadastrar"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Vinho *")
            tipo = st.selectbox("Tipo *", ["Tinto", "Branco", "Rosé", "Espumante"])
            safra = st.text_input("Safra (ex: 2018)", "2020")
            volume = st.text_input("Volume", "750ml")
        with col2:
            pallet = st.text_input("Pallet / Localização *", "Corredor 01 - Pallet 01")
            caixa = st.text_input("Identificação da Caixa", "CX-100")
            lado = st.selectbox("Lado do Galpão", ["A", "B", "C", "D"])
            quantidade = st.number_input("Quantidade Inicial (Garrafas)", min_value=1, value=12)

        submit = st.form_submit_button("Salvar no Estoque")
        if submit:
            if not nome or not pallet:
                st.error("Por favor, preencha os campos obrigatórios (Nome e Pallet).")
            else:
                novo_id = max([item.get("id", 0) for item in dados_estoque], default=0) + 1
                novo_item = {
                    "id": novo_id,
                    "nome": nome,
                    "tipo": tipo,
                    "safra": safra,
                    "volume": volume,
                    "lado": lado,
                    "caixa": caixa,
                    "pallet": pallet,
                    "quantidade": int(quantidade)
                }
                dados_estoque.append(novo_item)
                salvar_dados(dados_estoque)
                st.success(f"Vinho **{nome}** cadastrado com sucesso no **{pallet}**!")

# ---------------------------------------------------------
# ABA 3: GERAR QR CODES DE PALLETS
# ---------------------------------------------------------
elif opcao_menu == "🔲 Gerar QR Codes de Pallets":
    st.subheader("🔲 Gerador de Etiquetas de QR Code")
    st.write("Imprima estas etiquetas para colar nos pallets do galpão.")

    pallets_unicos = sorted(list(set([item.get("pallet", "") for item in dados_estoque if item.get("pallet")])))
    
    pallet_selecionado = st.selectbox("Selecione o Pallet para gerar a etiqueta:", pallets_unicos)
    
    if pallet_selecionado:
        link_qr = f"{url_app_base}/?pallet={pallet_selecionado}"
        qr_bytes = gerar_qr_code(link_qr)
        
        col_qr1, col_qr2 = st.columns([1, 2])
        with col_qr1:
            st.image(qr_bytes, caption=f"QR Code - {pallet_selecionado}", width=220)
        with col_qr2:
            st.markdown(f"**Pallet:** `{pallet_selecionado}`")
            st.markdown(f"**Link do QR Code:** `{link_qr}`")
            st.download_button(
                label="📥 Baixar Imagem do QR Code",
                data=qr_bytes,
                file_name=f"qrcode_{pallet_selecionado.replace(' ', '_')}.png",
                mime="image/png"
            )

# ---------------------------------------------------------
# ABA 4: RELATÓRIOS
# ---------------------------------------------------------
elif opcao_menu == "📊 Relatórios":
    st.subheader("📊 Resumo do Galpão")
    df = pd.DataFrame(dados_estoque)
    if not df.empty:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total de Rótulos", len(df))
        col_m2.metric("Total de Garrafas", int(df["quantidade"].sum()))
        col_m3.metric("Pallets Ocupados", df["pallet"].nunique())
        
        st.markdown("---")
        st.dataframe(df, use_container_width=True)
