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
    page_title="WMS - Galpão de Vinhos",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# ESTILIZAÇÃO CUSTOMIZADA (ESTILO SHADCN UI / REACT)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Estilo global da página */
    .main {
        background-color: #FAFAFA;
    }
    
    /* Card Container */
    .wine-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease-in-out;
    }
    .wine-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
    }
    
    /* Títulos */
    .wine-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #0F172A;
        margin: 0;
        padding: 0;
    }
    
    /* Subtítulos e Detalhes */
    .wine-details {
        font-size: 0.875rem;
        color: #64748B;
        margin-top: 6px;
    }
    
    /* Badges de Tipo de Vinho */
    .badge-tinto {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-branco {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-rose {
        background-color: #FCE7F3;
        color: #9D174D;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-espumante {
        background-color: #CCFBF1;
        color: #115E59;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-safra {
        background-color: #F1F5F9;
        color: #334155;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
        margin-left: 6px;
    }
    
    /* Ícone de Localização */
    .location-tag {
        color: #4A0E17;
        font-weight: 600;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    /* Suprimir rodapés nativos */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

ARQUIVO_BANCO = "estoque_galpao.json"

# ---------------------------------------------------------
# BANCO DE DADOS (JSON)
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

def gerar_qr_code(link_url):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
    qr.add_data(link_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def get_badge_class(tipo):
    mapping = {
        "Tinto": "badge-tinto",
        "Branco": "badge-branco",
        "Rosé": "badge-rose",
        "Espumante": "badge-espumante"
    }
    return mapping.get(tipo, "badge-safra")

# ---------------------------------------------------------
# INICIALIZAÇÃO
# ---------------------------------------------------------
dados_estoque = carregar_dados()
params = st.query_params
pallet_url = params.get("pallet") or params.get("p")

# ---------------------------------------------------------
# MODO 1: LEITURA DO QR CODE (TELA ESTILIZADA COMO REACT)
# ---------------------------------------------------------
if pallet_url:
    # Cabeçalho da leitura
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; color: #16A34A; margin-bottom: 4px;">
                <span style="font-size: 1.2rem;">CheckCircle2</span>
                <span style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">QR Code lido com sucesso</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<h1 style='font-size: 2.2rem; font-weight: 700; color: #0F172A; margin: 0;'>Vinhos alocados em <span style='color: #4A0E17;'>{pallet_url}</span></h1>", unsafe_allow_html=True)
    
    with col_h2:
        st.write("")
        st.write("")
        if st.button("⬅️ Ver todo o estoque", use_container_width=True):
            st.query_params.clear()
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Filtragem
    termo = pallet_url.strip().lower()
    encontrados = [
        v for v in dados_estoque 
        if termo in str(v.get("pallet", "")).lower() or str(v.get("pallet", "")).lower() in termo
    ]

    # Lista de resultados no formato de Cards
    if not encontrados:
        st.markdown(f"""
            <div class="wine-card" style="text-align: center; padding: 40px 20px;">
                <p style="color: #64748B; margin: 0;">🍷 Nenhum vinho cadastrado em <strong>{pallet_url}</strong> até o momento.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        for v in encontrados:
            tipo_class = get_badge_class(v.get("tipo", ""))
            tipo_html = f'<span class="{tipo_class}">{v.get("tipo", "")}</span>' if v.get("tipo") else ""
            safra_html = f'<span class="badge-safra">Safra {v.get("safra")}</span>' if v.get("safra") else ""

            st.markdown(f"""
                <div class="wine-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                        <div>
                            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                                <h3 class="wine-title">{v.get("nome", "Sem nome")}</h3>
                                {tipo_html}
                                {safra_html}
                            </div>
                            <div class="wine-details">
                                Lado: <strong>{v.get("lado", "—")}</strong> &nbsp;·&nbsp; 
                                Caixa: <strong>{v.get("caixa", "—")}</strong> &nbsp;·&nbsp; 
                                Volume: <strong>{v.get("volume", "—")}</strong> &nbsp;·&nbsp; 
                                Qtd: <strong>{v.get("quantidade", 0)} garrafas</strong>
                            </div>
                        </div>
                        <div class="location-tag">
                            📍 {v.get("pallet", "—")}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.stop()

# ---------------------------------------------------------
# MODO 2: PAINEL COMPLETO
# ---------------------------------------------------------
st.sidebar.title("🍷 Menu Galpão")
opcao_menu = st.sidebar.radio("Selecione:", ["📦 Visualizar Estoque", "➕ Cadastrar Vinho", "🔲 Gerar QR Codes", "📊 Relatórios"])

url_app_base = st.sidebar.text_input(
    "URL do App (para os QR Codes):", 
    value="https://mapa-estoque-galpao-premium-vbewrgwbe5ktw8ptefwxmf.streamlit.app"
)

if opcao_menu == "📦 Visualizar Estoque":
    st.markdown("<h2 style='color: #4A0E17;'>📋 Lista Geral de Produtos</h2>", unsafe_allow_html=True)
    
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

    for p in produtos_filtrados:
        tipo_class = get_badge_class(p.get("tipo", ""))
        tipo_html = f'<span class="{tipo_class}">{p.get("tipo", "")}</span>' if p.get("tipo") else ""
        safra_html = f'<span class="badge-safra">Safra {p.get("safra")}</span>' if p.get("safra") else ""
        link_qr = f"{url_app_base}/?pallet={p.get('pallet', '')}"

        st.markdown(f"""
            <div class="wine-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                            <h3 class="wine-title">{p.get("nome")}</h3>
                            {tipo_html}
                            {safra_html}
                        </div>
                        <div class="wine-details">
                            Caixa: <strong>{p.get("caixa", "—")}</strong> (Lado {p.get("lado", "—")}) &nbsp;·&nbsp; 
                            Volume: <strong>{p.get("volume", "—")}</strong> &nbsp;·&nbsp; 
                            Estoque: <strong>{p.get("quantidade", 0)} un.</strong>
                        </div>
                    </div>
                    <div>
                        <div class="location-tag" style="margin-bottom: 6px;">📍 {p.get("pallet", "—")}</div>
                        <a href="{link_qr}" target="_blank" style="font-size: 0.8rem; color: #0284C7; text-decoration: none;">🔗 Simular QR Code</a>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

elif opcao_menu == "➕ Cadastrar Vinho":
    st.markdown("<h2 style='color: #4A0E17;'>➕ Novo Cadastro</h2>", unsafe_allow_html=True)
    with st.form("form_cadastrar"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Vinho *")
            tipo = st.selectbox("Tipo *", ["Tinto", "Branco", "Rosé", "Espumante"])
            safra = st.text_input("Safra", "2021")
            volume = st.text_input("Volume", "750ml")
        with c2:
            pallet = st.text_input("Pallet / Localização *", "Corredor 01 - Pallet 01")
            caixa = st.text_input("Caixa", "CX-100")
            lado = st.selectbox("Lado", ["A", "B", "C", "D"])
            quantidade = st.number_input("Quantidade", min_value=1, value=12)

        if st.form_submit_button("Salvar no Estoque"):
            if nome and pallet:
                novo_id = max([item.get("id", 0) for item in dados_estoque], default=0) + 1
                dados_estoque.append({
                    "id": novo_id, "nome": nome, "tipo": tipo, "safra": safra,
                    "volume": volume, "lado": lado, "caixa": caixa, "pallet": pallet,
                    "quantidade": int(quantidade)
                })
                salvar_dados(dados_estoque)
                st.success(f"Vinho '{nome}' cadastrado com sucesso!")
                st.rerun()

elif opcao_menu == "🔲 Gerar QR Codes":
    st.markdown("<h2 style='color: #4A0E17;'>🔲 Gerador de QR Code</h2>", unsafe_allow_html=True)
    pallets = sorted(list(set([item.get("pallet", "") for item in dados_estoque if item.get("pallet")])))
    pallet_sel = st.selectbox("Selecione o Pallet:", pallets)
    if pallet_sel:
        link = f"{url_app_base}/?pallet={pallet_sel}"
        qr = gerar_qr_code(link)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(qr, width=200)
        with col2:
            st.write(f"Link: `{link}`")
            st.download_button("📥 Baixar Imagem QR Code", qr, file_name=f"{pallet_sel}.png", mime="image/png")

elif opcao_menu == "📊 Relatórios":
    st.markdown("<h2 style='color: #4A0E17;'>📊 Resumo do Estoque</h2>", unsafe_allow_html=True)
    df = pd.DataFrame(dados_estoque)
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Rótulos Diferentes", len(df))
        c2.metric("Total Garrafas", int(df["quantidade"].sum()))
        c3.metric("Pallets Ativos", df["pallet"].nunique())
        st.dataframe(df, use_container_width=True)
