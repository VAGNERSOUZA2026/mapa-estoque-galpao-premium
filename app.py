import io
import pandas as pd
import qrcode
import streamlit as st
from PIL import Image

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E ÍCONE
# ==========================================
st.set_page_config(
    page_title="Premium Wines | Estoque", page_icon="🍷", layout="wide"
)

# ==========================================
# 2. MENU LATERAL (SIDEBAR) COM A LOGO
# ==========================================
st.sidebar.markdown(
    """
    <div style="background-color: #580A18; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px;">
        <h2 style="color: #D4AF37; margin:0; font-family: 'Georgia', serif;">🍷 PREMIUM WINES</h2>
        <p style="color: #F5E6C8; margin:0; font-size: 12px;">Gestão de Estoque & Pallets</p>
    </div>
""",
    unsafe_allow_html=True,
)

st.sidebar.title("📌 Menu Principal")
menu = st.sidebar.radio(
    "Navegação:",
    [
        "📊 Dashboard & Consulta",
        "🖨️ Gerar QR Code de Pallet",
        "➕ Cadastrar Novo Pallet",
    ],
)

# ==========================================
# 3. BASE DE DADOS (SESSION STATE)
# ==========================================
if "estoque" not in st.session_state:
  st.session_state["estoque"] = pd.DataFrame({
      "Pallet": ["PAL-001", "PAL-002"],
      "Vinho": ["Cabernet Sauvignon Reserva", "Malbec Gran Reserva"],
      "Safra": [2018, 2020],
      "Garrafas": [600, 450],
      "Localização": ["Setor A - Fila 1", "Setor A - Fila 2"],
      "Foto": [None, None],
  })

# ==========================================
# 4. PÁGINAS DO APLICATIVO
# ==========================================

# --- PÁGINA 1: DASHBOARD & CONSULTA ---
if menu == "📊 Dashboard & Consulta":
  st.title("🍷 Premium Wines - Gestão de Estoque")

  col1, col2, col3 = st.columns(3)
  total_pallets = len(st.session_state["estoque"])
  total_garrafas = st.session_state["estoque"]["Garrafas"].sum()
  setores = st.session_state["estoque"]["Localização"].nunique()

  col1.metric("Total de Pallets", total_pallets)
  col2.metric("Total de Garrafas", f"{total_garrafas:,}".replace(",", "."))
  col3.metric("Setores Ativos", setores)

  st.markdown("---")

  st.subheader("🔍 Leitura de Pallet ou Busca Rápida")
  codigo_busca = st.text_input(
      "Escaneie o QR Code do Pallet ou digite o código:",
      placeholder="Ex: PAL-001",
  )

  if codigo_busca:
    df_filtrado = st.session_state["estoque"][
        st.session_state["estoque"]["Pallet"]
        .str.upper()
        .str.contains(codigo_busca.strip().upper())
    ]
    if not df_filtrado.empty:
      st.success(f"✅ Pallet(s) encontrado(s) para: '{codigo_busca}'")

      for idx, row in df_filtrado.iterrows():
        col_dados, col_img = st.columns([3, 1])
        with col_dados:
          st.write(f"**Pallet:** {row['Pallet']}")
          st.write(f"**Vinho:** {row['Vinho']}")
          st.write(f"**Safra:** {row['Safra']}")
          st.write(f"**Garrafas:** {row['Garrafas']}")
          st.write(f"**Localização:** {row['Localização']}")
        with col_img:
          if row["Foto"] is not None:
            st.image(
                row["Foto"], caption=f"Garrafa - {row['Vinho']}", width=150
            )
          else:
            st.info("Sem foto cadastrada.")
        st.markdown("---")
    else:
      st.warning(
          f"⚠️ Nenhum pallet informado ou encontrado com o código:"
          f" '{codigo_busca}'."
      )
  else:
    st.markdown("---")
    st.subheader("📦 Visão Geral do Armazém")
    df_exibicao = st.session_state["estoque"].drop(columns=["Foto"])
    st.dataframe(df_exibicao, use_container_width=True)

# --- PÁGINA 2: GERADOR DE QR CODE ---
elif menu == "🖨️ Gerar QR Code de Pallet":
  st.title("🖨️ Gerador de Etiqueta QR Code")

  pallet_selecionado = st.selectbox(
      "Selecione o Pallet:", st.session_state["estoque"]["Pallet"].unique()
  )

  dados_pallet = st.session_state["estoque"][
      st.session_state["estoque"]["Pallet"] == pallet_selecionado
  ].iloc[0]

  col_info, col_vnh, col_qr = st.columns([2, 1, 1])

  with col_info:
    st.write(f"**Vinho:** {dados_pallet['Vinho']}")
    st.write(f"**Safra:** {dados_pallet['Safra']}")
    st.write(f"**Quantidade:** {dados_pallet['Garrafas']} garrafas")
    st.write(f"**Localização:** {dados_pallet['Localização']}")

  with col_vnh:
    if dados_pallet["Foto"] is not None:
      st.image(dados_pallet["Foto"], caption="Rótulo", width=120)

  with col_qr:
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(dados_pallet["Pallet"])
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="#580A18", back_color="white")

    buf = io.BytesIO()
    img_qr.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.image(byte_im, caption=f"QR Code - {dados_pallet['Pallet']}")

# --- PÁGINA 3: CADASTRAR PALLET COM FOTO ---
elif menu == "➕ Cadastrar Novo Pallet":
  st.title("➕ Cadastrar Novo Pallet")

  col_a, col_b = st.columns(2)

  with col_a:
    novo_pallet = st.text_input("Código do Pallet *", placeholder="Ex: PAL-005")
    vinho = st.text_input("Nome do Vinho *", placeholder="Ex: Merlot Reserva")
    safra = st.number_input(
        "Safra", min_value=1900, max_value=2026, value=2022
    )

  with col_b:
    qtd = st.number_input(
        "Quantidade (Garrafas)", min_value=1, value=600, step=50
    )
    local = st.text_input("Localização", placeholder="Ex: Setor C - Fila 3")

  st.markdown("---")
  st.subheader("📸 Adicionar Foto do Vinho / Rótulo")

  modo_foto = st.radio(
      "Como deseja adicionar a foto?",
      ["📁 Enviar da Galeria / Arquivo", "📷 Tirar Foto com a Câmera"],
      horizontal=True,
  )

  foto_capturada = None

  if modo_foto == "📁 Enviar da Galeria / Arquivo":
    foto_capturada = st.file_uploader(
        "Escolha uma imagem (JPG ou PNG)", type=["jpg", "jpeg", "png"]
    )
  else:
    foto_capturada = st.camera_input("Tire uma foto do rótulo/garrafa")

  st.markdown("---")

  if st.button("💾 Salvar Pallet no Sistema", type="primary"):
    if novo_pallet and vinho:
      imagem_pil = None
      if foto_capturada is not None:
        imagem_pil = Image.open(foto_capturada)

      novo_registro = pd.DataFrame({
          "Pallet": [novo_pallet.strip().upper()],
          "Vinho": [vinho],
          "Safra": [safra],
          "Garrafas": [qtd],
          "Localização": [local],
          "Foto": [imagem_pil],
      })
      st.session_state["estoque"] = pd.concat(
          [st.session_state["estoque"], novo_registro], ignore_index=True
      )
      st.success(f"✅ Pallet '{novo_pallet.upper()}' cadastrado com sucesso!")
    else:
      st.error("⚠️ Preencha os campos obrigatórios (Código do Pallet e Vinho).")
