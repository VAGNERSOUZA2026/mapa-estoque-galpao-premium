import io
import pandas as pd
import qrcode
import streamlit as st
from PIL import Image

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Premium Wines | Estoque", page_icon="🍷", layout="wide"
)

# ==========================================
# 2. MENU LATERAL DE NAVEGAÇÃO
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
        "➕ Cadastrar Novo Pallet",
        "🔍 Buscar & Dashboard",
        "🖨️ Gerar QR Code de Pallet",
    ],
)

# ==========================================
# 3. BASE DE DADOS EM MEMÓRIA (SESSION STATE)
# ==========================================
if "estoque" not in st.session_state:
  st.session_state["estoque"] = pd.DataFrame({
      "Vinho": ["Cabernet Sauvignon Reserva", "Malbec Gran Reserva"],
      "Tipo": ["Tinto", "Tinto"],
      "Safra": ["2018", "2020"],
      "Corredor": ["Corredor 01", "Corredor 02"],
      "Pallet": ["Pallet 01", "Pallet 02"],
      "Lado": ["Direito", "Esquerdo"],
      "Garrafas_Caixa": ["12 garrafas", "6 garrafas"],
      "Volume": ["750ml", "750ml"],
      "Foto": [None, None],
  })

# ==========================================
# 4. PÁGINAS DO APLICATIVO
# ==========================================

# --- PÁGINA 1: CADASTRAR PALLET (TODOS OS CAMPOS + FOTO) ---
if menu == "➕ Cadastrar Novo Pallet":
  st.title("Pallet")

  with st.form("form_cadastro_pallet"):
    vinho = st.text_input("Nome do Vinho / Marca:", placeholder="")

    tipo = st.selectbox(
        "Tipo (Tinto, Branco, etc.):",
        [
            "Selecione...",
            "Tinto",
            "Branco",
            "Rosé",
            "Espumante",
            "Licoroso / Sobremesa",
        ],
    )

    safra = st.selectbox(
        "Safra:",
        ["Sem Safra (NV)"] + [str(ano) for ano in range(2026, 1990, -1)],
    )

    corredor = st.selectbox(
        "Corredor:", [f"Corredor {i:02d}" for i in range(1, 21)]
    )

    pallet = st.selectbox("Pallet:", [f"Pallet {i:02d}" for i in range(1, 31)])

    lado = st.selectbox("Lado:", ["Direito", "Esquerdo"])

    garrafas_caixa = st.selectbox(
        "Garrafas por Caixa:",
        ["6 garrafas", "12 garrafas", "24 garrafas", "Avulso / Outro"],
    )

    volume = st.selectbox(
        "Volume:", ["750ml", "375ml", "1.5L (Magnum)", "3.0L (Jeroboam)"]
    )

    st.markdown("---")
    st.subheader("📸 Foto do Vinho / Rótulo")

    modo_foto = st.radio(
        "Escolha como adicionar a foto:",
        ["📁 Galeria / Arquivo", "📷 Câmera"],
        horizontal=True,
    )

    foto_vinho = None
    if modo_foto == "📁 Galeria / Arquivo":
      foto_vinho = st.file_uploader(
          "Selecione a foto do vinho", type=["jpg", "jpeg", "png"]
      )
    else:
      foto_vinho = st.camera_input("Tire a foto do rótulo")

    st.markdown("---")
    salvar = st.form_submit_button("💾 Cadastrar Pallet")

    if salvar:
      if vinho.strip():
        img_pil = Image.open(foto_vinho) if foto_vinho is not None else None

        novo_registro = pd.DataFrame({
            "Vinho": [vinho.strip()],
            "Tipo": [tipo],
            "Safra": [safra],
            "Corredor": [corredor],
            "Pallet": [pallet],
            "Lado": [lado],
            "Garrafas_Caixa": [garrafas_caixa],
            "Volume": [volume],
            "Foto": [img_pil],
        })

        st.session_state["estoque"] = pd.concat(
            [st.session_state["estoque"], novo_registro], ignore_index=True
        )
        st.success(f"✅ Pallet cadastrado com sucesso para o vinho '{vinho}'!")
      else:
        st.error("⚠️ Por favor, informe o Nome do Vinho / Marca.")

# --- PÁGINA 2: BUSCA DE VINHO & DASHBOARD COMPLETO ---
elif menu == "🔍 Buscar & Dashboard":
  st.title("🔍 Busca de Vinho & Consulta de Estoque")

  # Métricas do topo
  c1, c2, c3 = st.columns(3)
  c1.metric("Total de Registros", len(st.session_state["estoque"]))
  c2.metric(
      "Corredores Ativos", st.session_state["estoque"]["Corredor"].nunique()
  )
  c3.metric(
      "Marcas / Vinhos", st.session_state["estoque"]["Vinho"].nunique()
  )

  st.markdown("---")

  # Campo de Busca Direta por Vinho / Marca ou Posição
  st.subheader("🔎 Digite para pesquisar:")
  termo_busca = st.text_input(
      "Buscar por Nome do Vinho, Tipo, Corredor ou Pallet:",
      placeholder="Ex: Cabernet, Tinto, Corredor 01...",
  )

  df_resultado = st.session_state["estoque"]

  if termo_busca.strip():
    termo = termo_busca.strip()
    mask = (
        df_resultado["Vinho"].str.contains(termo, case=False, na=False)
        | df_resultado["Tipo"].str.contains(termo, case=False, na=False)
        | df_resultado["Corredor"].str.contains(termo, case=False, na=False)
        | df_resultado["Pallet"].str.contains(termo, case=False, na=False)
        | df_resultado["Safra"].str.contains(termo, case=False, na=False)
    )
    df_resultado = df_resultado[mask]

  st.markdown("### 📋 Resultados encontrados:")

  if not df_resultado.empty:
    for idx, row in df_resultado.iterrows():
      with st.container():
        col_info, col_foto = st.columns([3, 1])

        with col_info:
          st.markdown(f"#### 🍷 **{row['Vinho']}** ({row['Tipo']})")
          st.write(
              f"📌 **Localização:** {row['Corredor']} | {row['Pallet']} | Lado:"
              f" {row['Lado']}"
          )
          st.write(
              f"📦 **Detalhes:** Safra: {row['Safra']} | Embalagem:"
              f" {row['Garrafas_Caixa']} | Volume: {row['Volume']}"
          )

        with col_foto:
          if row["Foto"] is not None:
            st.image(row["Foto"], caption="Rótulo Cadastrado", width=130)
          else:
            st.info("Sem foto")

        st.markdown("---")
  else:
    st.warning("⚠️ Nenhum vinho ou pallet encontrado com o termo digitado.")

# --- PÁGINA 3: GERADOR DE QR CODE ---
elif menu == "🖨️ Gerar QR Code de Pallet":
  st.title("🖨️ Gerador de QR Code do Pallet")

  if not st.session_state["estoque"].empty:
    lista_opcoes = [
        f"{row['Vinho']} - {row['Corredor']} ({row['Pallet']})"
        for idx, row in st.session_state["estoque"].iterrows()
    ]

    item_selecionado = st.selectbox(
        "Selecione o Vinho/Pallet para gerar a etiqueta:", lista_opcoes
    )
    idx = lista_opcoes.index(item_selecionado)
    dados = st.session_state["estoque"].iloc[idx]

    conteudo_qr = (
        f"VINHO: {dados['Vinho']}\nCORREDOR: {dados['Corredor']}\nPALLET:"
        f" {dados['Pallet']}\nLADO: {dados['Lado']}"
    )

    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(conteudo_qr)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="#580A18", back_color="white")

    buf = io.BytesIO()
    img_qr.save(buf, format="PNG")
    bytes_qr = buf.getvalue()

    col_qr, col_detalhes = st.columns([1, 2])
    with col_qr:
      st.image(
          bytes_qr, caption=f"Etiqueta QR Code - {dados['Pallet']}", width=200
      )
      st.download_button(
          "💾 Baixar QR Code (PNG)",
          data=bytes_qr,
          file_name=f"qrcode_{dados['Pallet']}.png",
          mime="image/png",
      )

    with col_detalhes:
      st.markdown(f"### 🍷 {dados['Vinho']}")
      st.write(f"**Tipo:** {dados['Tipo']}")
      st.write(f"**Safra:** {dados['Safra']}")
      st.write(f"**Posição:** {dados['Corredor']} | {dados['Pallet']}")
      st.write(f"**Caixa:** {dados['Garrafas_Caixa']} ({dados['Volume']})")
  else:
    st.info("Nenhum vinho cadastrado no momento.")
