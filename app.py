import json
import os
import urllib.parse
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Premium Wines | Gestão de Estoque & Galpão",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 🎨 ESTILIZAÇÃO CSS CUSTOMIZADA (LAYOUT PREMIUM) ---
st.markdown(
    """
    <style>
    /* Estilo Geral e Fontes */
    .main {
        background-color: #FAFAFA;
    }
    
    /* Header do Galpão */
    .premium-header {
        background: linear-gradient(135deg, #4A0E17 0%, #6B1D2F 100%);
        padding: 24px 30px;
        border-radius: 12px;
        color: #FFFFFF;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    .premium-header h1 {
        color: #F8F9FA !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        margin-bottom: 4px;
        font-size: 2.2rem;
    }
    .premium-badge {
        background-color: #D4AF37;
        color: #1A1A1A;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-top: 6px;
    }

    /* Cards de Vinhos */
    .wine-card {
        background-color: #FFFFFF;
        border-left: 5px solid #6B1D2F;
        border-radius: 8px;
        padding: 18px 22px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .wine-title {
        color: #4A0E17;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .wine-detail {
        color: #555555;
        font-size: 0.95rem;
    }
    
    /* Customização de Métricas */
    [data-testid="stMetricValue"] {
        color: #6B1D2F !important;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- CONFIGURAÇÕES E DADOS ---
NOME_ARQUIVO = "estoque_galpao.json"
URL_APLICATIVO = "https://mapa-estoque-galpao-premium-vbewrgwbe5ktw8ptefwxmf.streamlit.app"

NOME_DEV = "Vagner Souza"
FONE_DEV = "(31) 98968-4010"

LISTA_CORREDORES = [f"Corredor {i:02d}" for i in range(1, 26)]
LISTA_PALLETS = [f"Pallet {i:02d}" for i in range(1, 26)]
LISTA_LADOS = ["Direito", "Esquerdo", "Centro / Único"]

ANOS_SAFRA = [str(ano) for ano in range(2026, 1989, -1)]
OPCOES_SAFRA = ["Sem Safra (NV)", "Outra / Mais antiga"] + ANOS_SAFRA

OPCOES_CAIXA = [
    "24 garrafas",
    "12 garrafas",
    "6 garrafas",
    "3 garrafas",
    "1 garrafa",
    "Outra quantidade",
]

estoque_padrao = [
    {
        "nome": "Falérnia Reserva",
        "tipo": "Tinto",
        "safra": "2021",
        "pallet": "Corredor 01 - Pallet 01",
        "lado": "Direito",
        "caixa": "12 garrafas",
        "volume": "750ml",
    },
    {
        "nome": "Volpaia Chianti (375ml)",
        "tipo": "Tinto",
        "safra": "2020",
        "pallet": "Corredor 02 - Pallet 01",
        "lado": "Esquerdo",
        "caixa": "24 garrafas",
        "volume": "375ml",
    },
]


def carregar_dados():
    if os.path.exists(NOME_ARQUIVO):
        try:
            with open(NOME_ARQUIVO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if isinstance(dados, list) and len(dados) > 0:
                    return dados
        except Exception:
            pass
    return [dict(item) for item in estoque_padrao]


def salvar_dados(estoque):
    try:
        with open(NOME_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(estoque, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Erro ao salvar dados: {e}")


def formatar_caixa(valor_caixa):
    if not valor_caixa:
        return "12 garrafas"
    valor_str = str(valor_caixa).strip()
    if valor_str.isdigit():
        return f"{valor_str} garrafas"
    return valor_str


if "estoque" not in st.session_state:
    st.session_state.estoque = carregar_dados()

# Controle de scanner secundário
if "modo_scan_rapido" not in st.session_state:
    st.session_state.modo_scan_rapido = False

# --- 🎯 LEITURA DO QR CODE (TELA DO CELULAR) ---
query_params = st.query_params
pallet_qr = query_params.get("pallet") or query_params.get("p")

if pallet_qr:
    st.markdown(
        f"""
        <div class="premium-header">
            <span class="premium-badge">📍 LEITURA DE PALLET</span>
            <h1>{pallet_qr}</h1>
            <p style="margin:0; opacity:0.8;">Consulta de estoque local em tempo real</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    vinhos_encontrados = []
    for v in st.session_state.estoque:
        p_estoque = str(v.get("pallet", "")).strip().lower()
        p_busca = str(pallet_qr).strip().lower()
        if p_busca in p_estoque or p_estoque in p_busca:
            vinhos_encontrados.append(v)

    if vinhos_encontrados:
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Rótulos Distintos", len(vinhos_encontrados))
        col_m2.metric(
            "Localização",
            vinhos_encontrados[0].get("pallet", "Galpão Principal"),
        )

        st.markdown("---")

        for v in vinhos_encontrados:
            caixa_exibicao = formatar_caixa(v.get("caixa"))
            st.markdown(
                f"""
                <div class="wine-card">
                    <div class="wine-title">🍷 {v.get('nome')}</div>
                    <div class="wine-detail">
                        <b>Tipo:</b> {v.get('tipo', 'N/I')} | <b>Safra:</b> {v.get('safra', 'N/I')}<br>
                        <b>Caixa:</b> {caixa_exibicao} | <b>Volume:</b> {v.get('volume', '750ml')}<br>
                        <b>Lado no Corredor:</b> <span style="color:#6B1D2F; font-weight:bold;">{v.get('lado', 'Centro')}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.warning(
            f"⚠️ Nenhum vinho está vinculado atualmente ao **{pallet_qr}**."
        )

    st.markdown("---")

    # --- BOTÕES DE AÇÃO RÁPIDA ---
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("📷 Ler Outro QR Code", use_container_width=True):
            st.session_state.modo_scan_rapido = True
            st.rerun()

    with col_btn2:
        if st.button(
            "🏠 Ver Todo o Estoque",
            use_container_width=True,
            type="primary",
        ):
            st.query_params.clear()
            st.session_state.modo_scan_rapido = False
            st.rerun()

    # Campo de Entrada Rápida se clicar em "Ler Outro QR Code"
    if st.session_state.modo_scan_rapido:
        st.info("💡 **Aponte a câmera para o novo QR Code** ou selecione abaixo:")
        c1, c2 = st.columns(2)
        corr_temp = c1.selectbox("Corredor:", LISTA_CORREDORES, key="c_temp")
        pal_temp = c2.selectbox("Pallet:", LISTA_PALLETS, key="p_temp")

        if st.button("🔍 Ir para este Pallet"):
            st.query_params["pallet"] = f"{corr_temp} - {pal_temp}"
            st.session_state.modo_scan_rapido = False
            st.rerun()

    st.stop()


# --- HEADER PRINCIPAL ---
st.markdown(
    """
    <div class="premium-header">
        <span class="premium-badge">EXCLUSIVIDADE EM MINAS GERAIS</span>
        <h1>PREMIUM WINES — GALPÃO & ESTOQUE</h1>
        <p style="margin:0; opacity:0.85;">Sistema Inteligente de Localização e Gestão de Pallets</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- MENU LATERAL PREMIUM ---
st.sidebar.markdown("### 🏬 **Painel de Controle**")

menu = st.sidebar.radio(
    "Navegação:",
    [
        "1. Buscar vinho",
        "2. Ver todos os vinhos",
        "3. Cadastrar novo vinho",
        "4. Editar vinho existente",
        "5. Excluir vinho",
        "6. Exportar planilha (CSV)",
        "7. Gerar QR Code do Pallet",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"👨‍💻 **Desenvolvimento:** {NOME_DEV}")
st.sidebar.markdown(f"📞 **Suporte:** {FONE_DEV}")


# 1. BUSCAR VINHO
if menu == "1. Buscar vinho":
    st.subheader("🔍 Localizar Rótulo no Galpão")

    sub_op = st.radio(
        "Filtrar busca por:",
        ["Por Nome", "Por Tipo", "Por Safra", "Por Pallet / Corredor"],
        horizontal=True,
    )

    termo = st.text_input("🔎 Digite o termo de busca:").strip().lower()

    if termo:
        resultados = []
        for v in st.session_state.estoque:
            nome_vinho = str(v.get("nome", "")).lower()
            tipo_vinho = str(v.get("tipo", "")).lower()
            safra_vinho = str(v.get("safra", "")).lower()
            pallet_vinho = str(v.get("pallet", "")).lower()

            if sub_op == "Por Nome" and termo in nome_vinho:
                resultados.append(v)
            elif sub_op == "Por Tipo" and termo in tipo_vinho:
                resultados.append(v)
            elif sub_op == "Por Safra" and termo in safra_vinho:
                resultados.append(v)
            elif sub_op == "Por Pallet / Corredor" and termo in pallet_vinho:
                resultados.append(v)

        if not resultados:
            st.warning(f"Nenhum resultado para '{termo}'.")
        else:
            st.success(f"Foram encontrados {len(resultados)} rótulo(s):")
            for v in resultados:
                caixa_txt = formatar_caixa(v.get("caixa"))
                st.markdown(
                    f"""
                    <div class="wine-card">
                        <div class="wine-title">🍷 {v.get('nome')} ({v.get('safra')})</div>
                        <div class="wine-detail">
                            <b>Localização:</b> <span style="color:#6B1D2F; font-weight:bold;">{v.get('pallet')}</span> ({v.get('lado')})<br>
                            <b>Tipo:</b> {v.get('tipo')} | <b>Caixa:</b> {caixa_txt} | <b>Volume:</b> {v.get('volume')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# 2. VER TODOS OS VINHOS
elif menu == "2. Ver todos os vinhos":
    st.subheader("🍷 Relatório Geral do Galpão")

    if not st.session_state.estoque:
        st.warning("Nenhum vinho cadastrado.")
    else:
        lista_exibicao = []
        for v in st.session_state.estoque:
            v_copy = dict(v)
            v_copy["caixa"] = formatar_caixa(v_copy.get("caixa"))
            lista_exibicao.append(v_copy)

        df = pd.DataFrame(lista_exibicao)
        df.rename(
            columns={
                "nome": "Vinho",
                "tipo": "Tipo",
                "safra": "Safra",
                "pallet": "Localização",
                "lado": "Lado",
                "caixa": "Caixa",
                "volume": "Volume",
            },
            inplace=True,
        )
        st.dataframe(df, use_container_width=True)

# 3. CADASTRAR VINHO
elif menu == "3. Cadastrar novo vinho":
    st.subheader("➕ Novo Vínculo de Produto / Pallet")

    nome = st.text_input("Nome do Vinho / Marca:").strip()

    with st.form("form_cadastrar"):
        c1, c2 = st.columns(2)
        tipo = c1.text_input("Tipo (Tinto, Branco, etc.):").strip()
        safra_opcao = c2.selectbox("Safra:", OPCOES_SAFRA)

        c3, c4, c5 = st.columns(3)
        sel_corredor = c3.selectbox("Corredor:", LISTA_CORREDORES)
        sel_pallet = c4.selectbox("Pallet:", LISTA_PALLETS)
        lado = c5.selectbox("Lado:", LISTA_LADOS)

        caixa_opcao = st.selectbox(
            "Garrafas por Caixa:", OPCOES_CAIXA, index=1
        )
        volume_opcao = st.selectbox(
            "Volume:", ["750ml", "375ml", "1500ml (Magnum)", "Outro"]
        )

        submit = st.form_submit_button("✅ Cadastrar Produto", type="primary")

        if submit:
            pallet_final = f"{sel_corredor} - {sel_pallet}"
            if nome and tipo:
                novo = {
                    "nome": nome,
                    "tipo": tipo,
                    "safra": safra_opcao,
                    "pallet": pallet_final,
                    "lado": lado,
                    "caixa": formatar_caixa(caixa_opcao),
                    "volume": volume_opcao,
                }
                st.session_state.estoque.append(novo)
                salvar_dados(st.session_state.estoque)
                st.success(f"✅ Vinho '{nome}' alocado no {pallet_final}!")
                st.rerun()

# 4. EDITAR VINHO
elif menu == "4. Editar vinho existente":
    st.subheader("✏️ Alterar Cadastro / Alocação")

    if st.session_state.estoque:
        opcoes = [
            f"{i+1}. {v.get('nome')} ({v.get('safra')}) - {v.get('pallet')}"
            for i, v in enumerate(st.session_state.estoque)
        ]
        idx = st.selectbox("Selecione o Item:", range(len(opcoes)), format_func=lambda x: opcoes[x])
        v = st.session_state.estoque[idx]

        with st.form("form_editar"):
            nnome = st.text_input("Nome:", v.get("nome"))
            ntipo = st.text_input("Tipo:", v.get("tipo"))
            npallet = st.text_input("Pallet:", v.get("pallet"))
            ncaixa = st.selectbox("Caixa:", OPCOES_CAIXA, index=1)
            submit_edit = st.form_submit_button("💾 Atualizar", type="primary")

            if submit_edit:
                st.session_state.estoque[idx].update(
                    {
                        "nome": nnome,
                        "tipo": ntipo,
                        "pallet": npallet,
                        "caixa": formatar_caixa(ncaixa),
                    }
                )
                salvar_dados(st.session_state.estoque)
                st.success("Atualizado com sucesso!")
                st.rerun()

# 5. EXCLUIR VINHO
elif menu == "5. Excluir vinho":
    st.subheader("🗑️ Remover do Estoque")
    if st.session_state.estoque:
        opcoes_ex = [
            f"{i+1}. {v.get('nome')} - {v.get('pallet')}"
            for i, v in enumerate(st.session_state.estoque)
        ]
        idx_ex = st.selectbox("Item para remover:", range(len(opcoes_ex)), format_func=lambda x: opcoes_ex[x])

        if st.button("❌ Confirmar Exclusão", type="primary"):
            st.session_state.estoque.pop(idx_ex)
            salvar_dados(st.session_state.estoque)
            st.success("Item removido!")
            st.rerun()

# 6. EXPORTAR PLANILHA
elif menu == "6. Exportar planilha (CSV)":
    st.subheader("📤 Exportar Relatório de Estoque")
    if st.session_state.estoque:
        df = pd.DataFrame(st.session_state.estoque)
        csv = df.to_csv(index=False, sep=";").encode("utf-8-sig")
        st.download_button("📥 Baixar Planilha Excel/CSV", data=csv, file_name="estoque_premium_wines.csv", mime="text/csv")

# 7. GERAR QR CODE DO PALLET
elif menu == "7. Gerar QR Code do Pallet":
    st.subheader("📱 Impressão de Etiquetas QR Code")

    c1, c2 = st.columns(2)
    qr_corr = c1.selectbox("Corredor:", LISTA_CORREDORES)
    qr_pal = c2.selectbox("Pallet:", LISTA_PALLETS)

    pallet_alvo = f"{qr_corr} - {qr_pal}"
    link_especifico = f"{URL_APLICATIVO}/?pallet={urllib.parse.quote(pallet_alvo)}"
    url_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(link_especifico)}"

    st.markdown("---")
    st.image(url_qr, caption=f"Etiqueta Oficial: {pallet_alvo}", width=220)
    st.info(f"🔗 Link direto: `{link_especifico}`")
