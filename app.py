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
# 2. MENU LATERAL (SIDEBAR)
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
        "📊 Dashboard & Consulta",
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

# --- PÁGINA 1: CADASTRAR PALLET (SEU FORMULÁRIO COMPLETO + FOTO) ---
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
        "Adicionar foto via:",
        ["📁 Galeria / Arquivo", "📷 Câmera"],
        horizontal=True,
    )

    foto_vinho = None
    if modo_foto == "📁 Galeria / Arquivo":
      foto_vinho = st.file_uploader(
          "Selecione a imagem do vinho", type=["jpg", "jpeg", "png"]
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

# --- PÁGINA 2: DASHBOARD & CONSULTA ---
elif menu == "📊 Dashboard & Consulta":
  st.title("📊 Consulta de Estoque & Pallets")

  # Métricas resumo
  col1, col2, col3 = st.columns(3)
  col1.metric("Total Registrados", len(st.session_state["estoque"]))
  col2.metric(
      "Corredores em Uso", st.session_state["estoque"]["Corredor"].nunique()
  )
  col3.metric(
      "Marcas / Vinhos", st.session_state["estoque"]["Vinho"].nunique()
  )

  st.markdown("---")
  st.subheader("🔍 Buscar Pallet / Vinho")
  busca = st.text_input("Digite o nome do vinho, corredor ou pallet:")

  df_base = st.session_state["estoque"]

  if busca:
    mask = (
        df_base["Vinho"].str.contains(busca, case=False, na=False)
        | df_base["Corredor"].str.contains(busca, case=False, na=False)
        | df_base["Pallet"].str.contains(busca, case=False, na=False)
    )
    df_base = df_base[mask]

  # Exibição dos itens em cards com fotos
  if not df_base.empty:
    for idx, row in df_base.iterrows():
      with st.container():
        c1, c2 = st.columns([3, 1])
        with c1:
          st.markdown(f"### 🍷 {row['Vinho']}")
          st.write(
              f"**Localização:** {row['Corredor']} | {row['Pallet']} | Lado"
              f" {row['Lado']}"
          )
          st.write(
              f"**Detalhes:** Tipo: {row['Tipo']} | Safra: {row['Safra']} |"
              f" Caixas: {row['Garrafas_Caixa']} | Vol: {row['Volume']}"
          )
        with c2:
          if row["Foto"] is not None:
            st.image(row["Foto"], caption="Rótulo", width=120)
          else:
            st.caption("Sem foto")
        st.markdown("---")
  else:
    st.info("Nenhum pallet encontrado.")

# --- PÁGINA 3: GERADOR DE QR CODE ---
elif menu == "🖨️ Gerar QR Code de Pallet":
  st.title("🖨️ Gerador de QR Code de Localização")

  if not st.session_state["estoque"].empty:
    opcoes = [
        f"{row['Corredor']} - {row['Pallet']} ({row['Vinho']})"
        for idx, row in st.session_state["estoque"].iterrows()
    ]
    selecao = st.selectbox("Escolha o item para gerar o QR Code:", opcoes)

    idx_sel = opcoes.index(selecao)
    item = st.session_state["estoque"].iloc[idx_sel]

    conteudo_qr = f"CORREDOR: {item['Corredor']} | PALLET: {item['Pallet']} | VINHO: {item['Vinho']}"

    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(conteudo_qr)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="#580A18", back_color="white")

    buf = io.BytesIO()
    img_qr.save(buf, format="PNG")
    byte_im = buf.getvalue()

    col_qr, col_info = st.columns([1, 2])
    with col_qr:
      st.image(byte_im, caption=f"{item['Corredor']} - {item['Pallet']}")
      st.download_button(
          "💾 Baixar QR Code",
          data=byte_im,
          file_name=f"qrcode_{item['Pallet']}.png",
          mime="image/png",
      )
    with col_info:
      st.write(f"**Vinho:** {item['Vinho']}")
      st.write(f"**Corredor:** {item['Corredor']}")
      st.write(f"**Pallet:** {item['Pallet']}")
      st.write(f"**Lado:** {item['Lado']}")
  else:
    st.warning("Nenhum pallet cadastrado ainda.")
