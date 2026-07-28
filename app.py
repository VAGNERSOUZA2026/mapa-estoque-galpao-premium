import base64
import json
import os
import urllib.parse
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Mapa Estoque Galpão Premium",
    page_icon="🍷",
    layout="wide",
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
    "lado": "A",
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


# Inicializa a sessão
if "estoque" not in st.session_state:
  st.session_state.estoque = carregar_dados()

if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

# CHAVE DE REFRESH PARA LIMPAR O FORMULÁRIO APÓS SALVAR
if "form_key" not in st.session_state:
  st.session_state.form_key = 0

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
  st.title("🔒 ACESSO RESTRITO - GALPÃO")
  st.subheader("Mapa Estoque Galpão Premium")
  st.caption("Sistema de Localização de vinhos do Galpão")

  senha_digitada = st.text_input("Senha de Acesso:", type="password")
  if st.button("🔑 Entrar no Sistema"):
    if senha_digitada == SENHA_ACESSO:
      st.session_state.autenticado = True
      st.success("Acesso Liberado!")
      st.rerun()
    else:
      st.error("Senha incorreta!")
  st.stop()

# --- 🎯 LEITURA DO QR CODE (PEGA O PALLET DA URL) ---
query_params = st.query_params
pallet_qr = query_params.get("pallet") or query_params.get("p")

if pallet_qr:
  st.markdown("---")
  st.success("📱 **QR CODE LIDO COM SUCESSO!**")
  st.header(f"📦 Vinhos Alocados em: **{pallet_qr}**")

  vinhos_encontrados = []
  for v in st.session_state.estoque:
    p_estoque = str(v.get("pallet", "")).strip().lower()
    p_busca = str(pallet_qr).strip().lower()
    if p_busca in p_estoque or p_estoque in p_busca:
      vinhos_encontrados.append(v)

  if vinhos_encontrados:
    for v in vinhos_encontrados:
      with st.container():
        c_info, c_img = st.columns([3, 1])
        with c_info:
          st.markdown(
              f"### 🍷 **{v.get('nome')}**\n"
              f"* **Safra:** {v.get('safra')} | **Lado:** {v.get('lado')}\n"
              f"* **Tipo de Caixa:** {v.get('caixa')} | **Volume:**"
              f" {v.get('volume')}"
          )
        with c_img:
          if v.get("foto"):
            st.image(
                base64.b64decode(v.get("foto")),
                caption="Rótulo",
                use_container_width=True,
            )
        st.markdown("---")
  else:
    st.warning(
        f"⚠️ Nenhum vinho cadastrado em **{pallet_qr}** até o momento."
    )

  if st.button("⬅️ Ver Todo o Estoque do Galpão"):
    st.query_params.clear()
    st.rerun()
  st.stop()

# --- TÍTULO ---
st.title("🍷 MAPA ESTOQUE GALPÃO PREMIUM")
st.caption("Sistema de Localização e Gestão de Vinhos")
st.markdown("---")

# --- MENU LATERAL ---
st.sidebar.markdown("### 🏬 Galpão Principal")
if st.sidebar.button("🔒 Sair do Sistema"):
  st.session_state.autenticado = False
  st.rerun()

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "📌 Escolha uma opção:",
    [
        "1. Buscar vinho",
        "2. Ver todos os vinhos",
        "3. Cadastrar novo vinho",
        "4. Editar vinho existente",
        "5. Excluir vinho",
        "6. Exportar planilha (CSV)",
        "7. Gerar QR Code do Pallet",
        "8. Escanear QR Code com a Câmera",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"👨‍💻 **Desenvolvido por:** {NOME_DEV}")
st.sidebar.markdown(f"📞 **Contato:** {FONE_DEV}")

# 1. BUSCAR VINHO
if menu == "1. Buscar vinho":
  st.header("🔍 BUSCAR VINHO NO GALPÃO")
  sub_op = st.radio(
      "Como deseja buscar?",
      ["Por Nome", "Por Tipo", "Por Safra", "Por Pallet / Corredor"],
  )
  termo = st.text_input("🔎 Digite o termo de busca:").strip().lower()

  if termo:
    resultados = [
        v
        for v in st.session_state.estoque
        if termo in str(v.get(sub_op.split()[-1].lower(), "")).lower()
        or termo in str(v.get("nome", "")).lower()
    ]
    if not resultados:
      st.warning(f"⚠️ Nenhum vinho encontrado para '{termo}'.")
    else:
      st.success(f"Encontrado(s) {len(resultados)} resultado(s):")
      for v in resultados:
        col_txt, col_pic = st.columns([3, 1])
        with col_txt:
          st.write(
              f"🍷 **{v.get('nome')}** ({v.get('safra')}) ➔ 📍 `{v.get('pallet')}`"
              f" | {v.get('caixa')}"
          )
        with col_pic:
          if v.get("foto"):
            st.image(
                base64.b64decode(v.get("foto")), caption="Rótulo", width=90
            )

# 2. VER TODOS OS VINHOS
elif menu == "2. Ver todos os vinhos":
  st.header("🍷 ESTOQUE COMPLETO DO GALPÃO")
  if not st.session_state.estoque:
    st.warning("Nenhum vinho cadastrado.")
  else:
    df = pd.DataFrame(st.session_state.estoque)
    if "foto" in df.columns:
      df = df.drop(columns=["foto"])
    st.dataframe(df, use_container_width=True)

# 3. CADASTRAR VINHO (LIMPEZA AUTOMÁTICA)
elif menu == "3. Cadastrar novo vinho":
  st.header("➕ CADASTRAR VINHO NO GALPÃO")

  # Formulário dinâmico utilizando a chave de controle
  with st.form(f"form_cadastrar_{st.session_state.form_key}"):
    nome = st.text_input("Nome do vinho / Marca:").strip()

    c_tipo, c_safra = st.columns(2)
    with c_tipo:
      tipo = st.text_input("Tipo (Tinto, Branco...):").strip()
    with c_safra:
      safra = st.selectbox("📅 Safra:", OPCOES_SAFRA)

    c_corr, c_pal, c_lad = st.columns(3)
    with c_corr:
      sel_corredor = st.selectbox("🛣️ Corredor:", LISTA_CORREDORES)
    with c_pal:
      sel_pallet = st.selectbox("📦 Pos./Pallet:", LISTA_PALLETS)
    with c_lad:
      lado = st.selectbox("↔️ Lado:", LISTA_LADOS)

    caixa = st.selectbox("📦 Formato da Caixa:", OPCOES_CAIXA)
    volume = st.selectbox("🧪 Volume:", ["750ml", "375ml", "1500ml"])

    st.markdown("---")
    st.subheader("📸 Foto do Vinho / Rótulo")
    foto_upload = st.file_uploader(
        "Selecione da galeria ou fotografe:", type=["jpg", "jpeg", "png"]
    )

    btn_salvar = st.form_submit_button("✅ Salvar no Galpão")

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

        # Incrementa a chave do formulário para forçar a limpeza dos campos
        st.session_state.form_key += 1

        st.success(f"✅ '{nome}' cadastrado com sucesso!")
        st.rerun()
      else:
        st.error("⚠️ Preencha pelo menos o Nome e o Tipo do vinho.")

# 4. EDITAR VINHO
elif menu == "4. Editar vinho existente":
  st.header("✏️ EDITAR VINHO")
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
          "Atualizar Foto (Opcional):", type=["jpg", "jpeg", "png"]
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
elif menu == "5. Excluir vinho":
  st.header("🗑️ EXCLUIR VINHO")
  if st.session_state.estoque:
    opcoes = [
        f"{v.get('nome')} - {v.get('pallet')}"
        for v in st.session_state.estoque
    ]
    idx = st.selectbox(
        "Selecione para remover:",
        range(len(opcoes)),
        format_func=lambda x: opcoes[x],
    )
    if st.button("❌ Confirmar Exclusão"):
      st.session_state.estoque.pop(idx)
      salvar_dados(st.session_state.estoque)
      st.success("Removido!")
      st.rerun()

# 6. EXPORTAR PLANILHA
elif menu == "6. Exportar planilha (CSV)":
  st.header("📤 EXPORTAR PARA EXCEL")
  if st.session_state.estoque:
    df_exp = pd.DataFrame(st.session_state.estoque)
    if "foto" in df_exp.columns:
      df_exp = df_exp.drop(columns=["foto"])
    csv = df_exp.to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button("📥 Baixar CSV", csv, "estoque_galpao.csv", "text/csv")

# 7. GERAR QR CODE DO PALLET
elif menu == "7. Gerar QR Code do Pallet":
  st.header("📱 Impressão de Etiquetas QR Code")

  c1, c2 = st.columns(2)
  with c1:
    qr_corr = st.selectbox("Corredor:", LISTA_CORREDORES)
  with c2:
    qr_pal = st.selectbox("Pallet:", LISTA_PALLETS)

  pallet_alvo = f"{qr_corr} - {qr_pal}"

  st.markdown("---")
  st.subheader(f"📋 Vinhos Atualmente Cadastrados em: `{pallet_alvo}`")

  vinhos_no_pallet = [
      v
      for v in st.session_state.estoque
      if str(v.get("pallet", "")).strip().lower() == pallet_alvo.lower()
  ]

  if vinhos_no_pallet:
    for v in vinhos_no_pallet:
      st.info(
          f"🍷 **{v.get('nome')}** | Safra: `{v.get('safra')}` | Lado:"
          f" `{v.get('lado')}` | Embalagem: `{v.get('caixa')}`"
      )
  else:
    st.warning(f"⚠️ Nenhum vinho cadastrado em {pallet_alvo} ainda.")

  st.markdown("---")
  pallet_encoded = urllib.parse.quote_plus(pallet_alvo)
  link_pallet_especifico = f"{URL_APLICATIVO}/?pallet={pallet_encoded}"
  url_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(link_pallet_especifico)}"

  st.image(url_qr, caption=f"Etiqueta Oficial {pallet_alvo}", width=250)
  st.caption(f"🔗 Link direto de acesso: {link_pallet_especifico}")

# 8. ESCANEAR QR CODE
elif menu == "8. Escanear QR Code com a Câmera":
  st.header("📷 Leitor de QR Code via Câmera")
  st.write("Aponte a câmera do seu celular para ler a etiqueta do pallet:")

  st.components.v1.html(
      """
        <div id="reader" style="width:100%; max-width:400px; margin:auto;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            function onScanSuccess(decodedText, decodedResult) {
                window.top.location.href = decodedText;
            }

            let html5QrcodeScanner = new Html5QrcodeScanner(
                "reader", 
                { 
                    fps: 10, 
                    qrbox: 250,
                    videoConstraints: { facingMode: { ideal: "environment" } }
                }
            );
            html5QrcodeScanner.render(onScanSuccess);
        </script>
        """,
      height=460,
  )
