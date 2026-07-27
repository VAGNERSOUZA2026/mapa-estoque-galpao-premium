import io
import pandas as pd
import qrcode
import streamlit as st
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Premium Wines | Estoque", page_icon="🍷", layout="centered"
)

st.title("Pallet")

# Formulário com todos os seus campos originais
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

  # Opção para carregar arquivo da galeria ou usar a câmera do celular
  modo_foto = st.radio(
      "Adicionar foto:",
      ["📁 Galeria / Arquivo", "📷 Câmera"],
      horizontal=True,
  )

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
      st.success(f"✅ Pallet cadastrado com sucesso para o vinho '{vinho}'!")
      if foto_vinho is not None:
        st.image(foto_vinho, caption="Foto registrada", width=200)
    else:
      st.error("⚠️ Por favor, informe o Nome do Vinho / Marca.")
