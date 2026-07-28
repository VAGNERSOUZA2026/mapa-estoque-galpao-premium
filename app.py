import base64
import io
import json
import os
import urllib.parse
import pandas as pd
import streamlit as st
from PIL import Image

# 1. Configuração da página
st.set_page_config(
    page_title="Mapa Estoque - Galpão Premium",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="collapsed",  # Inicia recolhido para focar na tela no celular
)

# 2. CSS Personalizado para Design Mobile Premium
st.markdown(
    """
    <style>
    /* Fundo geral mais agradável */
    .stApp {
        background-color: #FAFAFA;
    }
    
    /* Cabeçalho do App */
    .header-container {
        text-align: center;
        padding: 10px 0 20px 0;
    }
    .main-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #581825;
        margin-top: 5px;
        letter-spacing: -0.5px;
    }
    .sub-title {
        font-size: 0.9rem;
        color: #777777;
        margin-bottom: 15px;
    }

    /* Card de Vinho Estilizado */
    .wine-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 15px;
        border: 1px solid #E2E8F0;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
    }
    .wine-title {
        color: #581825;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .badge-pallet {
        background-color: #581825;
        color: #FFFFFF;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-info {
        background-color: #F1F5F9;
        color: #334155;
        padding: 4px 8px;
        border-radius: 8px;
        font-size: 0.8rem;
        margin-left: 4px;
        display: inline-block;
    }
    
    /* Ajuste para inputs redondos e modernos */
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- CONFIGURAÇÕES DO GALPÃO ---
SENHA_ACESSO = "1980"
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
    "Caixa com 12 garrafas",
    "Caixa com 6 garrafas",
    "Caixa com 3 garrafas",
    "Garrafa Avulsa (1 un)",
    "Outra quantidade",
]

estoque_padrao = [{
    "nome": "Château Margaux Premier Grand Cru",
    "tipo": "Tinto",
    "safra": "2015",
    "pallet": "Corredor 01 - Pallet 01",
    "lado": "Direito",
    "caixa": "Caixa com 12 garrafas",
    "volume": "750ml",
    "foto": None,
}]


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


def converter_imagem_base64(uploaded_file):
  if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode("utf-8")
  return None


def calcular_hash_simples(img):
  img = img.convert("L").resize((8, 8), Image.Resampling.LANCZOS)
  pixels = list(img.getdata())
  media = sum(pixels) / len(pixels)
  return "".join(["1" if p > media else "0" for p in pixels])


def comparar_hashes(h1, h2):
  return sum(c1 != c2 for c1, c2 in zip(h1, h2))


# Inicialização de sessões
if "estoque" not in st.session_state:
  st.session_state.estoque = carregar_dados()

if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

if "form_key" not in st.session_state:
  st.session_state.form_key = 0

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
  st.markdown(
      """
        <div class="header-container">
            <h1 class="main-title">🍷 GALPÃO PREMIUM</h1>
            <p class="sub-title">Controle de Estoque e Localização</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  with st.form("login_form"):
    senha_digitada = st.text_input("🔑 Senha de Acesso:", type="password")
    btn_login = st.form_submit_button(
        "Entrar no Sistema", use_container_width=True
    )

    if btn_login:
      if senha_digitada == SENHA_ACESSO:
        st.session_state.autenticado = True
        st.success("Acesso Autorizado!")
        st.rerun()
      else:
        st.error("Senha incorreta!")
  st.stop()

# --- MENU LATERAL ---
with st.sidebar:
  st.markdown("<h2 style='color:#581825;'>🍷 Galpão Premium</h2>", unsafe_allow_html=True)
  menu = st.radio(
      "Menu:",
      [
          "🔍 Buscar vinho",
          "🍷 Ver estoque completo",
          "➕ Cadastrar novo vinho",
          "✏️ Editar vinho",
          "🗑️ Excluir vinho",
          "📤 Exportar planilha (CSV)",
          "🏷️ Gerar QR Code do Pallet",
          "📷 Escanear QR Code",
      ],
  )
  st.markdown("---")
  if st.button("🔒 Sair do Sistema", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()
  st.caption(f"👨‍💻 Dev: **{NOME_DEV}**\n\n📞 {FONE_DEV}")

# --- CABEÇALHO DA PÁGINA PRINCIPAL ---
st.markdown(
    """
    <div class="header-container">
        <h1 class="main-title">🍷 MAPA ESTOQUE GALPÃO</h1>
        <p class="sub-title">Painel de Localização em Tempo Real</p>
    </div>
""",
    unsafe_allow_html=True,
)

# 1. BUSCAR VINHO (COM BUSCA POR FOTO INTEGRADA!)
if menu == "🔍 Buscar vinho":
  st.subheader("🔍 Localizar Vinho no Galpão")

  # Abas para o usuário escolher como deseja buscar
  aba_texto, aba_foto = st.tabs(
      ["🔎 Buscar por Texto / Pallet", "📸 Buscar por Foto do Rótulo"]
  )

  # --- ABA 1: BUSCA POR TEXTO ---
  with aba_texto:
    c_tipo, c_busca = st.columns([1, 2])
    with c_tipo:
      sub_op = st.selectbox(
          "Filtrar por:",
          ["Por Nome", "Por Tipo", "Por Safra", "Por Pallet / Corredor"],
      )
    with c_busca:
      termo = st.text_input("Digite o que procura:").strip().lower()

    if termo:
      resultados = [
          v
          for v in st.session_state.estoque
          if termo in str(v.get(sub_op.split()[-1].lower(), "")).lower()
          or termo in str(v.get("nome", "")).lower()
      ]
      if not resultados:
        st.warning("⚠️ Nenhum vinho encontrado.")
      else:
        for v in resultados:
          c1, c2 = st.columns([3, 1])
          with c1:
            st.markdown(
                f"""
                        <div class="wine-card">
                            <div class="wine-title">🍷 {v.get('nome')} ({v.get('safra')})</div>
                            <p><span class="badge-pallet">📍 {v.get('pallet')}</span> <span class="badge-info">Lado: {v.get('lado')}</span></p>
                            <p style="margin-top:8px; font-size:0.9rem;"><b>Tipo:</b> {v.get('tipo')} | <b>Embalagem:</b> {v.get('caixa')}</p>
                        </div>
                        """,
                unsafe_allow_html=True,
            )
          with c2:
            if v.get("foto"):
              st.image(
                  base64.b64decode(v.get("foto")), caption="Rótulo", width=90
              )

  # --- ABA 2: BUSCA POR FOTO (INTEGRADA AQUI) ---
  with aba_foto:
    st.write("Tire uma foto ou envie a imagem do rótulo para pesquisar:")
    foto_pesquisa = st.file_uploader(
        "Selecione a foto da garrafa:", type=["jpg", "jpeg", "png"]
    )

    if foto_pesquisa is not None:
      try:
        img_pesquisa = Image.open(foto_pesquisa)
        st.image(img_pesquisa, caption="Foto para Busca", width=150)

        hash_pesquisa = calcular_hash_simples(img_pesquisa)
        encontrados = []

        for item in st.session_state.estoque:
          if item.get("foto"):
            try:
              bytes_banco = base64.b64decode(item["foto"])
              img_banco = Image.open(io.BytesIO(bytes_banco))
              hash_banco = calcular_hash_simples(img_banco)

              dif = comparar_hashes(hash_pesquisa, hash_banco)
              if dif <= 18:
                encontrados.append((dif, item))
            except Exception:
              pass

        encontrados.sort(key=lambda x: x[0])

        st.markdown("---")
        if encontrados:
          st.success(
              f"🎯 Encontrado(s) {len(encontrados)} resultado(s) parecido(s):"
          )
          for diff, v in encontrados:
            c1, c2 = st.columns([3, 1])
            with c1:
              st.markdown(
                  f"""
                            <div class="wine-card">
                                <div class="wine-title">🍷 {v.get('nome')}</div>
                                <p><span class="badge-pallet">📍 {v.get('pallet')}</span> <span class="badge-info">Lado: {v.get('lado')}</span></p>
                                <p style="margin-top:8px; font-size:0.9rem;"><b>Safra:</b> {v.get('safra')} | <b>Caixa:</b> {v.get('caixa')}</p>
                            </div>
                            """,
                  unsafe_allow_html=True,
              )
            with c2:
              if v.get("foto"):
                st.image(
                    base64.b64decode(v.get("foto")), caption="Banco", width=90
                )
        else:
          st.warning(
              "⚠️ Nenhum vinho idêntico ou similar encontrado no cadastro."
          )
      except Exception as e:
        st.error(f"Erro ao processar foto: {e}")

# 2. VER TODOS OS VINHOS
elif menu == "🍷 Ver estoque completo":
  st.subheader("📋 Tabela do Estoque Completo")
  if st.session_state.estoque:
    df = pd.DataFrame(st.session_state.estoque)
    if "foto" in df.columns:
      df = df.drop(columns=["foto"])
    st.dataframe(df, use_container_width=True)

# 3. CADASTRAR VINHO
elif menu == "➕ Cadastrar novo vinho":
  st.subheader("➕ Novo Cadastro no Galpão")

  with st.form(f"form_cadastrar_{st.session_state.form_key}"):
    nome = st.text_input("Nome do Vinho / Marca:").strip()

    c_tipo, c_safra = st.columns(2)
    with c_tipo:
      tipo = st.text_input("Tipo (ex: Tinto, Branco):").strip()
    with c_safra:
      safra = st.selectbox("📅 Safra:", OPCOES_SAFRA)

    c_corr, c_pal, c_lad = st.columns(3)
    with c_corr:
      sel_corredor = st.selectbox("🛣️ Corredor:", LISTA_CORREDORES)
    with c_pal:
      sel_pallet = st.selectbox("📦 Pos./Pallet:", LISTA_PALLETS)
    with c_lad:
      lado = st.selectbox("↔️ Lado:", LISTA_LADOS)

    c_cx, c_vol = st.columns(2)
    with c_cx:
      caixa = st.selectbox("📦 Formato da Caixa:", OPCOES_CAIXA)
    with c_vol:
      volume = st.selectbox("🧪 Volume:", ["750ml", "375ml", "1500ml"])

    foto_upload = st.file_uploader(
        "📸 Foto do Rótulo (Opcional):", type=["jpg", "jpeg", "png"]
    )

    btn_salvar = st.form_submit_button(
        "✅ Salvar Vinho", use_container_width=True
    )

    if btn_salvar:
      pallet_final = f"{sel_corredor} - {sel_pallet}"
      if nome and tipo:
        foto_b64 = converter_imagem_base64(foto_upload)

        novo_vinho = {
            "nome": nome,
            "tipo": tipo,
            "safra": safra,
            "pallet": pallet_final,
            "lado": lado,
            "caixa": caixa,
            "volume": volume,
            "foto": foto_b64,
        }
        st.session_state.estoque.append(novo_vinho)
        salvar_dados(st.session_state.estoque)

        # Limpa os campos automaticamente
        st.session_state.form_key += 1
        st.success(f"✅ '{nome}' cadastrado com sucesso!")
        st.rerun()
      else:
        st.error("⚠️ Preencha pelo menos o Nome e o Tipo.")

# 4. EDITAR VINHO
elif menu == "✏️ Editar vinho":
  st.subheader("✏️ Alterar Cadastro")
  if st.session_state.estoque:
    opcoes = [
        f"{i + 1}. {v.get('nome')} - {v.get('pallet')}"
        for i, v in enumerate(st.session_state.estoque)
    ]
    idx = st.selectbox(
        "Selecione:", range(len(opcoes)), format_func=lambda x: opcoes[x]
    )
    vinho = st.session_state.estoque[idx]

    with st.form("form_edit"):
      novo_nome = st.text_input("Nome:", vinho.get("nome"))
      novo_pallet = st.text_input("Pallet:", vinho.get("pallet"))
      nova_caixa = st.selectbox("Caixa:", OPCOES_CAIXA)
      foto_nova = st.file_uploader(
          "Atualizar Foto:", type=["jpg", "jpeg", "png"]
      )

      if st.form_submit_button("💾 Salvar"):
        vinho["nome"] = novo_nome
        vinho["pallet"] = novo_pallet
        vinho["caixa"] = nova_caixa
        if foto_nova is not None:
          vinho["foto"] = converter_imagem_base64(foto_nova)

        salvar_dados(st.session_state.estoque)
        st.success("Atualizado!")
        st.rerun()

# 5. EXCLUIR VINHO
elif menu == "🗑️ Excluir vinho":
  st.subheader("🗑️ Remover do Estoque")
  if st.session_state.estoque:
    opcoes = [
        f"{v.get('nome')} - {v.get('pallet')}"
        for v in st.session_state.estoque
    ]
    idx = st.selectbox(
        "Escolha para apagar:",
        range(len(opcoes)),
        format_func=lambda x: opcoes[x],
    )
    if st.button("❌ Apagar Registro", type="primary"):
      st.session_state.estoque.pop(idx)
      salvar_dados(st.session_state.estoque)
      st.success("Removido!")
      st.rerun()

# 6. EXPORTAR PLANILHA
elif menu == "📤 Exportar planilha (CSV)":
  st.subheader("📤 Baixar Dados em Planilha")
  if st.session_state.estoque:
    df_exp = pd.DataFrame(st.session_state.estoque)
    if "foto" in df_exp.columns:
      df_exp = df_exp.drop(columns=["foto"])
    csv = df_exp.to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button("📥 Download CSV", csv, "estoque_galpao.csv", "text/csv")

# 7. GERAR QR CODE DO PALLET
elif menu == "🏷️ Gerar QR Code do Pallet":
  st.subheader("🏷️ Etiquetas para Pallet")
  c1, c2 = st.columns(2)
  with c1:
    qr_corr = st.selectbox("Corredor:", LISTA_CORREDORES)
  with c2:
    qr_pal = st.selectbox("Pallet:", LISTA_PALLETS)

  pallet_alvo = f"{qr_corr} - {qr_pal}"
  pallet_encoded = urllib.parse.quote_plus(pallet_alvo)
  link_pallet = f"{URL_APLICATIVO}/?pallet={pallet_encoded}"
  url_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(link_pallet)}"

  st.image(url_qr, caption=f"Etiqueta {pallet_alvo}", width=200)

# 8. ESCANEAR QR CODE
elif menu == "📷 Escanear QR Code":
  st.subheader("📷 Câmera para Leitura de QR Code")
  st.components.v1.html(
      """
        <div id="reader" style="width:100%; max-width:380px; margin:auto;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            function onScanSuccess(decodedText) { window.top.location.href = decodedText; }
            let html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 220 });
            html5QrcodeScanner.render(onScanSuccess);
        </script>
        """,
      height=440,
  )
