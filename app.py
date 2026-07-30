from datetime import datetime
import pandas as pd
import streamlit as st

# Configuração da Página - Layout Wide
st.set_page_config(
    page_title="WMS - Adega de Vinhos",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- CSS PERSONALIZADO (ESTILO WMS / ERP CORPORATIVO) ---
st.markdown(
    """
    <style>
    /* Estilo Geral de Fundo */
    .stApp {
        background-color: #EBEBEB;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Ocultar cabeçalhos padrão do Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Barra Superior Dark */
    .top-header {
        background-color: #1A1A1A;
        color: #FFFFFF;
        padding: 8px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        border-bottom: 3px solid #800020;
    }
    .top-header b { color: #E67E22; }
    
    /* Breadcrumbs / Caminho da Página */
    .breadcrumb {
        font-size: 14px;
        color: #800020;
        font-weight: bold;
        margin: 10px 0px;
    }
    
    /* Botão Primário Laranja/Destaque */
    div.stButton > button {
        background-color: #E67E22;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 4px;
        height: 38px;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #D35400;
        color: white;
    }
    
    /* Cartões de Resumo/Totais no Rodapé */
    .summary-card {
        background-color: #E0E0E0;
        border: 1px solid #B0B0B0;
        border-radius: 4px;
        padding: 8px 12px;
        text-align: center;
    }
    .summary-card label {
        font-size: 11px;
        color: #555;
        font-weight: bold;
        display: block;
    }
    .summary-card span {
        font-size: 16px;
        font-weight: bold;
        color: #111;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- BARRA SUPERIOR (TOP BAR) ---
data_atual = datetime.now().strftime("%d/%m/%Y")
st.markdown(
    f"""
    <div class="top-header">
        <div><span style="font-size:18px; font-weight:bold; color:#FFF;">🍷 WMS - GESTÃO DE ADEGA</span></div>
        <div>
            👤 Logado como: <b>VAGNER SOUZA</b> &nbsp;|&nbsp; 
            🏬 Local: <b>ADEGA PRINCIPAL</b> &nbsp;|&nbsp; 
            📅 {data_atual}
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# --- MENU DE NAVEGAÇÃO HORIZONTAL ---
aba_selecionada = st.radio(
    "",
    [
        "🔍 Buscar Vinho",
        "➕ Cadastrar Vinho",
        "📊 Relatórios & Estoque",
    ],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("---")

# --- BASE DE DADOS EM MEMÓRIA (SESSÃO) ---
if "estoque_vinhos" not in st.session_state:
  st.session_state["estoque_vinhos"] = pd.DataFrame([
      {
          "Nome do Vinho": "Cabernet Sauvignon Reserva",
          "Tipo": "Tinto",
          "Safra": "2018",
          "Qtd na Caixa": 6,
          "Qtd de Caixas": 10,
          "Total Garrafas": 60,
          "Localização / Lugar": "Corredor A - Prateleira 2",
      },
      {
          "Nome do Vinho": "Chardonnay Gran Reserva",
          "Tipo": "Branco",
          "Safra": "2020",
          "Qtd na Caixa": 12,
          "Qtd de Caixas": 5,
          "Total Garrafas": 60,
          "Localização / Lugar": "Corredor B - Prateleira 1",
      },
      {
          "Nome do Vinho": "Malbec Estate",
          "Tipo": "Tinto",
          "Safra": "2021",
          "Qtd na Caixa": 6,
          "Qtd de Caixas": 8,
          "Total Garrafas": 48,
          "Localização / Lugar": "Corredor A - Prateleira 3",
      },
  ])

# =============================================================
# TELA 1: BUSCAR VINHO
# =============================================================
if aba_selecionada == "🔍 Buscar Vinho":
  st.markdown(
      '<div class="breadcrumb">📂 Consulta > Buscar Vinhos</div>',
      unsafe_allow_html=True,
  )

  # --- PAINEL DE FILTROS ---
  with st.container():
    c1, c2, c3, c4 = st.columns([3, 2, 2, 1.5])

    with c1:
      filtro_nome = st.text_input(
          "Nome do Vinho:", placeholder="Ex: Cabernet, Malbec..."
      )
    with c2:
      filtro_tipo = st.selectbox(
          "Tipo de Vinho:",
          ["Todos", "Tinto", "Branco", "Rosé", "Espumante", "Sobremesa/Porto"],
      )
    with c3:
      filtro_safra = st.text_input("Safra:", placeholder="Ex: 2020")
    with c4:
      st.write(" ")
      st.write(" ")
      btn_buscar = st.button("🔎 Buscar")

  st.markdown("---")

  # Aplicar Filtros no DataFrame
  df_exibir = st.session_state["estoque_vinhos"].copy()

  if filtro_nome:
    df_exibir = df_exibir[
        df_exibir["Nome do Vinho"]
        .str.lower()
        .str.contains(filtro_nome.lower())
    ]
  if filtro_tipo != "Todos":
    df_exibir = df_exibir[df_exibir["Tipo"] == filtro_tipo]
  if filtro_safra:
    df_exibir = df_exibir[
        df_exibir["Safra"].str.contains(filtro_safra)
    ]

  # --- RESULTADOS ---
  col_info, col_exp = st.columns([8, 2])
  with col_info:
    st.caption(f"Total de {len(df_exibir)} vinhos encontrados.")
  with col_exp:
    st.download_button(
        "📄 Exportar CSV",
        df_exibir.to_csv(index=False),
        "estoque_vinhos.csv",
        "text/csv",
    )

  st.dataframe(df_exibir, use_container_width=True, hide_index=True)

  # --- RODAPÉ COM RESUMO / TOTAIS ---
  st.markdown("### 📊 Resumo do Estoque Filtrado")
  r1, r2, r3, r4 = st.columns(4)

  total_caixas = (
      df_exibir["Qtd de Caixas"].sum() if not df_exibir.empty else 0
  )
  total_garrafas = (
      df_exibir["Total Garrafas"].sum() if not df_exibir.empty else 0
  )

  with r1:
    st.markdown(
        f"<div class='summary-card'><label>Rótulos Encontrados</label><span>{len(df_exibir)}</span></div>",
        unsafe_allow_html=True,
    )
  with r2:
    st.markdown(
        f"<div class='summary-card'><label>Total de Caixas</label><span>{total_caixas}</span></div>",
        unsafe_allow_html=True,
    )
  with r3:
    st.markdown(
        f"<div class='summary-card'><label>Total de Garrafas</label><span>{total_garrafas}</span></div>",
        unsafe_allow_html=True,
    )
  with r4:
    st.markdown(
        "<div class='summary-card'><label>Status Estoque</label><span"
        " style='color:green;'>REGULAR</span></div>",
        unsafe_allow_html=True,
    )

# =============================================================
# TELA 2: CADASTRAR VINHO
# =============================================================
elif aba_selecionada == "➕ Cadastrar Vinho":
  st.markdown(
      '<div class="breadcrumb">📂 Cadastros > Inserir Novo Vinho</div>',
      unsafe_allow_html=True,
  )

  with st.form("form_cadastro_vinho", clear_on_submit=True):
    st.subheader("📋 Informações do Vinho")

    c1, c2, c3 = st.columns([3, 2, 2])
    with c1:
      novo_nome = st.text_input(
          "Nome do Vinho:*", placeholder="Ex: Merlot Reserva"
      )
    with c2:
      novo_tipo = st.selectbox(
          "Tipo de Vinho:*",
          ["Tinto", "Branco", "Rosé", "Espumante", "Sobremesa/Porto"],
      )
    with c3:
      nova_safra = st.text_input("Safra:*", placeholder="Ex: 2022")

    st.subheader("📦 Armazenamento e Quantidades")
    c4, c5, c6 = st.columns([2, 2, 3])
    with c4:
      qtd_caixa = st.number_input(
          "Qtd de Garrafas por Caixa:*", min_value=1, value=6
      )
    with c5:
      qtd_caixas_recebidas = st.number_input(
          "Qtd de Caixas:*", min_value=1, value=1
      )
    with c6:
      novo_local = st.text_input(
          "Lugar / Localização onde vai ficar:*",
          placeholder="Ex: Corredor A - Prateleira 4",
      )

    st.markdown("---")
    btn_salvar = st.form_submit_button("💾 Salvar Cadastro no WMS")

    if btn_salvar:
      if not novo_nome or not nova_safra or not novo_local:
        st.error("Por favor, preencha todos os campos obrigatórios (*).")
      else:
        # Calcular total de garrafas
        total_garrafas_novas = qtd_caixa * qtd_caixas_recebidas

        # Criar novo registro
        novo_registro = {
            "Nome do Vinho": novo_nome,
            "Tipo": novo_tipo,
            "Safra": nova_safra,
            "Qtd na Caixa": qtd_caixa,
            "Qtd de Caixas": qtd_caixas_recebidas,
            "Total Garrafas": total_garrafas_novas,
            "Localização / Lugar": novo_local,
        }

        # Adicionar à tabela na memória
        st.session_state["estoque_vinhos"] = pd.concat(
            [
                st.session_state["estoque_vinhos"],
                pd.DataFrame([novo_registro]),
            ],
            ignore_index=True,
        )

        st.success(
            f"Vinho **{novo_nome}** ({novo_tipo} - Safra {nova_safra}) cadastrado"
            f" com sucesso! Local: {novo_local}"
        )

# =============================================================
# TELA 3: RELATÓRIOS
# =============================================================
else:
  st.markdown(
      '<div class="breadcrumb">📂 Relatórios > Visão Geral do Estoque</div>',
      unsafe_allow_html=True,
  )

  df_atual = st.session_state["estoque_vinhos"]

  col1, col2 = st.columns(2)
  with col1:
    st.subheader("Garrafas por Tipo")
    st.bar_chart(df_atual.groupby("Tipo")["Total Garrafas"].sum())

  with col2:
    st.subheader("Garrafas por Safra")
    st.bar_chart(df_atual.groupby("Safra")["Total Garrafas"].sum())
    
