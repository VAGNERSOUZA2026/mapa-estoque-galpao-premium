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
NOME_ARQUIVO = "estoque_galpao.json"

# URL OFICIAL DO SEU APLICATIVO NO STREAMLIT CLOUD
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
    {
        "nome": "Stoneburn Sauvignon Blanc",
        "tipo": "Branco",
        "safra": "2022",
        "pallet": "Corredor 03 - Pallet 04",
        "lado": "Direito",
        "caixa": "12 garrafas",
        "volume": "750ml",
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


# Inicializa a sessão do estoque
if "estoque" not in st.session_state:
    st.session_state.estoque = carregar_dados()

# --- 🎯 LEITURA DO QR CODE (PEGA O PALLET DA URL) ---
query_params = st.query_params

# Suporta tanto ?pallet= quanto ?p=
pallet_qr = query_params.get("pallet") or query_params.get("p")

if pallet_qr:
    st.markdown("---")
    st.success("📱 **QR CODE LIDO COM SUCESSO!**")
    st.header(f"📦 Vinhos Alocados em: **{pallet_qr}**")

    # Filtra os vinhos ignorando maiúsculas/minúsculas e espaços extras
    vinhos_encontrados = []
    for v in st.session_state.estoque:
        p_estoque = str(v.get("pallet", "")).strip().lower()
        p_busca = str(pallet_qr).strip().lower()
        if p_busca in p_estoque or p_estoque in p_busca:
            vinhos_encontrados.append(v)

    if vinhos_encontrados:
        for v in vinhos_encontrados:
            with st.container():
                st.markdown(
                    f"### 🍷 **{v.get('nome')}**\n"
                    f"* **Safra:** {v.get('safra')} | **Lado:** {v.get('lado')}\n"
                    f"* **Caixa:** {v.get('caixa')} | **Volume:** {v.get('volume')}"
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

# --- TÍTULO E LOGO ---
col_logo, col_titulo = st.columns([1, 4])

nomes_logo = [
    "PremiumWines_OG-Image.jpg",
    "logo.jpg",
    "logo.png",
    "logo.jpeg",
    "logo.webp",
]
arquivo_logo = None
for arquivo in nomes_logo:
    if os.path.exists(arquivo):
        arquivo_logo = arquivo
        break

with col_logo:
    if arquivo_logo:
        st.image(arquivo_logo, use_container_width=True)
    else:
        st.title("🍷")

with col_titulo:
    st.title("MAPA ESTOQUE GALPÃO PREMIUM")
    st.caption("Sistema de Localização de vinhos do Galpão")

st.markdown("---")

# --- MENU LATERAL ---
st.sidebar.markdown("### 🏬 Galpão Principal")

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

    termo = (
        st.text_input(
            "🔎 Digite o termo de busca (Ex: Corredor 01 ou Falernia):"
        )
        .strip()
        .lower()
    )

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
            st.warning(f"⚠️ Nenhum vinho encontrado para '{termo}'.")
        else:
            st.success(f"Encontrado(s) {len(resultados)} resultado(s):")
            for v in resultados:
                lado_txt = (
                    f" - Lado {v.get('lado')}" if v.get("lado") else ""
                )
                safra_txt = f" ({v.get('safra')})" if v.get("safra") else ""
                with st.expander(
                    f"🍷 {v.get('nome', 'Sem nome')}{safra_txt} [{v.get('tipo', 'S/T')}] ➔ 📍 {v.get('pallet', 'S/P')}{lado_txt}",
                    expanded=True,
                ):
                    st.write(
                        f"**Localização no Galpão:** {v.get('pallet', 'N/I')}"
                    )
                    st.write(
                        f"**Lado do Corredor:** {v.get('lado', 'Não informado')}"
                    )
                    st.write(f"**Safra:** {v.get('safra', 'N/I')}")
                    st.write(f"**Caixa:** {v.get('caixa', 'N/I')}")
                    st.write(f"**Volume:** {v.get('volume', 'N/I')}")

# 2. VER TODOS OS VINHOS
elif menu == "2. Ver todos os vinhos":
    st.header("🍷 ESTOQUE COMPLETO DO GALPÃO")

    if not st.session_state.estoque:
        st.warning("Nenhum vinho cadastrado no galpão.")
    else:
        ordem = st.radio(
            "Como deseja visualizar?",
            [
                "Ordem padrão",
                "Ordem Alfabética (Nome)",
                "Agrupado por Localização (Corredor/Pallet)",
            ],
        )

        lista_exibicao = [dict(v) for v in st.session_state.estoque]

        if ordem == "Ordem Alfabética (Nome)":
            lista_exibicao.sort(key=lambda x: str(x.get("nome", "")).lower())
        elif ordem == "Agrupado por Localização (Corredor/Pallet)":
            lista_exibicao.sort(key=lambda x: str(x.get("pallet", "")).lower())

        df = pd.DataFrame(lista_exibicao)
        colunas_map = {
            "nome": "Nome do Vinho",
            "tipo": "Tipo",
            "safra": "Safra",
            "pallet": "Localização / Pallet",
            "lado": "Lado do Corredor",
            "caixa": "Caixa",
            "volume": "Volume",
        }
        df.rename(columns=colunas_map, inplace=True)
        st.dataframe(df, use_container_width=True)

# 3. CADASTRAR VINHO
elif menu == "3. Cadastrar novo vinho":
    st.header("➕ CADASTRAR VINHO NO GALPÃO")

    nome = st.text_input("Nome do vinho / Marca:").strip()

    outras_safras = []
    if nome:
        outras_safras = [
            v
            for v in st.session_state.estoque
            if str(v.get("nome", "")).strip().lower() == nome.lower()
        ]

    if outras_safras:
        st.info(
            f"ℹ️ **Atenção:** Este vinho já possui **{len(outras_safras)} registro(s)** no galpão:"
        )
        for item in outras_safras:
            st.write(
                f"- **Safra {item.get('safra', 'N/I')}** ➔ Local: `{item.get('pallet', 'N/I')}` (Lado: {item.get('lado', 'N/I')})"
            )

    with st.form("form_cadastrar"):
        col_tipo, col_safra = st.columns(2)
        with col_tipo:
            tipo = st.text_input(
                "Tipo (Tinto, Branco, Rosé, Espumante...):"
            ).strip()
        with col_safra:
            safra_opcao = st.selectbox("📅 Safra:", OPCOES_SAFRA)

        safra_custom = ""
        if safra_opcao == "Outra / Mais antiga":
            safra_custom = st.text_input("Digite o ano da safra (Ex: 1985):")

        col_corr, col_pal, col_lad = st.columns(3)
        with col_corr:
            sel_corredor = st.selectbox("🛣️ Corredor:", LISTA_CORREDORES)
        with col_pal:
            sel_pallet = st.selectbox("📦 Pos./Pallet:", LISTA_PALLETS)
        with col_lad:
            lado = st.selectbox("↔️ Lado:", LISTA_LADOS)

        caixa_opcao = st.selectbox(
            "📦 Quantidade de garrafas por caixa:", OPCOES_CAIXA
        )

        caixa_custom = ""
        if caixa_opcao == "Outra quantidade":
            caixa_custom = st.text_input("Digite a quantidade de garrafas:")

        vol_opcao = st.selectbox(
            "🧪 Volume / Tamanho da garrafa:",
            ["750ml", "375ml", "1500ml (Magnum)", "Outro valor"],
        )

        volume_custom = ""
        if vol_opcao == "Outro valor":
            volume_custom = st.text_input("Digite o volume customizado:")

        submit = st.form_submit_button("✅ Salvar no Galpão")

        if submit:
            safra_final = (
                safra_custom
                if safra_opcao == "Outra / Mais antiga"
                else safra_opcao
            )
            caixa_final = (
                caixa_custom
                if caixa_opcao == "Outra quantidade"
                else caixa_opcao
            )
            volume_final = (
                volume_custom if vol_opcao == "Outro valor" else vol_opcao
            )

            pallet_final = f"{sel_corredor} - {sel_pallet}"

            if nome and tipo:
                novo_vinho = {
                    "nome": nome,
                    "tipo": tipo,
                    "safra": safra_final if safra_final else "Sem Safra (NV)",
                    "pallet": pallet_final,
                    "lado": lado,
                    "caixa": caixa_final if caixa_final else "12 garrafas",
                    "volume": volume_final if volume_final else "750ml",
                }
                st.session_state.estoque.append(novo_vinho)
                salvar_dados(st.session_state.estoque)
                st.success(
                    f"✅ '{nome}' ({safra_final}) cadastrado com sucesso em `{pallet_final}`!"
                )
                st.rerun()
            else:
                st.error("❌ Nome e Tipo são obrigatórios!")

# 4. EDITAR VINHO
elif menu == "4. Editar vinho existente":
    st.header("✏️ EDITAR VINHO NO GALPÃO")

    if not st.session_state.estoque:
        st.warning("Nenhum vinho cadastrado.")
    else:
        opcoes = [
            f"{i + 1}. {v.get('nome', 'Sem nome')} ({v.get('safra', 'S/S')}) - 📍 {v.get('pallet', 'Sem local')}"
            for i, v in enumerate(st.session_state.estoque)
        ]
        idx_selecionado = st.selectbox(
            "Selecione o vinho que deseja editar:",
            range(len(opcoes)),
            format_func=lambda x: opcoes[x],
        )

        vinho = st.session_state.estoque[idx_selecionado]

        with st.form("form_editar"):
            novo_nome = st.text_input("Novo Nome:", str(vinho.get("nome", "")))

            col_t, col_s = st.columns(2)
            with col_t:
                novo_tipo = st.text_input(
                    "Novo Tipo:", str(vinho.get("tipo", ""))
                )
            with col_s:
                safra_atual = str(vinho.get("safra", "Sem Safra (NV)"))
                idx_s = (
                    OPCOES_SAFRA.index(safra_atual)
                    if safra_atual in OPCOES_SAFRA
                    else 0
                )
                nova_safra = st.selectbox(
                    "Nova Safra:", OPCOES_SAFRA, index=idx_s
                )

            novo_pallet = st.text_input(
                "Nova Localização:", str(vinho.get("pallet", ""))
            )

            lado_atual = vinho.get("lado", "Direito")
            idx_l = (
                LISTA_LADOS.index(lado_atual)
                if lado_atual in LISTA_LADOS
                else 0
            )
            novo_lado = st.selectbox("Novo Lado:", LISTA_LADOS, index=idx_l)

            caixa_atual = vinho.get("caixa", "12 garrafas")
            idx_caixa = (
                OPCOES_CAIXA.index(caixa_atual)
                if caixa_atual in OPCOES_CAIXA
                else 0
            )
            nova_caixa = st.selectbox("Caixa:", OPCOES_CAIXA, index=idx_caixa)

            novo_volume = st.text_input(
                "Volume:", str(vinho.get("volume", "750ml"))
            )

            submit_edit = st.form_submit_button("💾 Salvar Alterações")

            if submit_edit:
                st.session_state.estoque[idx_selecionado] = {
                    "nome": novo_nome,
                    "tipo": novo_tipo,
                    "safra": nova_safra,
                    "pallet": novo_pallet,
                    "lado": novo_lado,
                    "caixa": nova_caixa,
                    "volume": novo_volume,
                }
                salvar_dados(st.session_state.estoque)
                st.success(f"✅ '{novo_nome}' atualizado com sucesso!")
                st.rerun()

# 5. EXCLUIR VINHO
elif menu == "5. Excluir vinho":
    st.header("🗑️ EXCLUIR VINHO DO GALPÃO")

    if not st.session_state.estoque:
        st.warning("Nenhum vinho cadastrado.")
    else:
        opcoes_excluir = [
            f"{i + 1}. {v.get('nome', 'Sem nome')} ({v.get('safra', 'NV')}) - 📍 {v.get('pallet', 'Sem local')} ({v.get('lado', 'S/L')})"
            for i, v in enumerate(st.session_state.estoque)
        ]

        idx_excluir = st.selectbox(
            "Selecione o vinho a remover:",
            range(len(opcoes_excluir)),
            format_func=lambda x: opcoes_excluir[x],
        )

        vinho_alvo = st.session_state.estoque[idx_excluir]

        if st.button("❌ Confirmar Exclusão"):
            nome_removido = vinho_alvo.get("nome", "Vinho")
            st.session_state.estoque.pop(idx_excluir)
            salvar_dados(st.session_state.estoque)
            st.success(f"✅ '{nome_removido}' excluído com sucesso!")
            st.rerun()

# 6. EXPORTAR PLANILHA
elif menu == "6. Exportar planilha (CSV)":
    st.header("📤 EXPORTAR PARA EXCEL (CSV)")

    if st.session_state.estoque:
        df = pd.DataFrame(st.session_state.estoque)
        csv_data = df.to_csv(index=False, sep=";").encode("utf-8-sig")

        st.download_button(
            label="📥 Baixar Planilha do Galpão em Excel / CSV",
            data=csv_data,
            file_name="estoque_galpao.csv",
            mime="text/csv",
        )
    else:
        st.warning("Nenhum dado para exportar.")

# 7. GERAR QR CODE DO PALLET
elif menu == "7. Gerar QR Code do Pallet":
    st.header("📱 GERADOR DE ETIQUETAS QR CODE")
    st.write(
        "Gere QR Codes inteligentes para colar nos pallets e consultar os vinhos na hora usando a câmera do celular."
    )

    c1, c2 = st.columns(2)
    with c1:
        qr_corr = st.selectbox("Selecione o Corredor:", LISTA_CORREDORES)
    with c2:
        qr_pal = st.selectbox("Selecione o Pallet:", LISTA_PALLETS)

    pallet_alvo = f"{qr_corr} - {qr_pal}"

    vinhos_no_pallet = [
        v
        for v in st.session_state.estoque
        if str(v.get("pallet", "")).strip().lower() == pallet_alvo.lower()
    ]

    st.markdown("---")
    st.subheader(f"📍 Pallet Selecionado: `{pallet_alvo}`")

    if vinhos_no_pallet:
        st.success(
            f"📦 Encontrado(s) {len(vinhos_no_pallet)} produto(s) neste pallet:"
        )
        for v in vinhos_no_pallet:
            st.write(
                f"- **{v.get('nome')}** | Safra: **{v.get('safra')}** | Lado: {v.get('lado')} | Cx: {v.get('caixa')}"
            )
    else:
        st.info("ℹ️ NENHUM vinho cadastrado neste pallet no momento.")

    # Constrói o link com a URL exata do seu app no Streamlit Cloud
    link_pallet_especifico = (
        f"{URL_APLICATIVO}/?pallet={urllib.parse.quote(pallet_alvo)}"
    )
    url_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(link_pallet_especifico)}"

    st.markdown("### 🖨️ QR Code de Acesso Direto ao Pallet:")
    st.image(url_qr, caption=f"Etiqueta QR Code para: {pallet_alvo}", width=250)
    st.info(f"🔗 Link gerado: `{link_pallet_especifico}`")
