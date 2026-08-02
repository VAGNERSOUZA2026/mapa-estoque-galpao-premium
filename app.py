import streamlit as st
import pandas as pd
import json
import os
import random
import urllib.parse
from datetime import datetime, timedelta, timezone

# IMPORTANDO AS FUNÇÕES E OS MÓDULOS SEPARADOS
from utils import carregar_dados, salvar_dados
import financeiro
import presenca
import sorteio
import admin
import dashboard

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE FUSO HORÁRIO E DIRETÓRIOS
# -----------------------------------------------------------------------------
fuso_br = timezone(timedelta(hours=-3))
hoje_dt = datetime.now(fuso_br)
hoje_str = hoje_dt.strftime("%d/%m")
mes_vigente_str = hoje_dt.strftime("%m/%Y")
data_hoje_id = hoje_dt.strftime("%Y-%m-%d")

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

COMPROVANTES_DIR = "data/comprovantes_imgs"
if not os.path.exists(COMPROVANTES_DIR):
    os.makedirs(COMPROVANTES_DIR)

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Futebol Feminino",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (DARK MODE + TOQUE FEMININO ELEGANTE)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Poppins', sans-serif; 
    }

    /* Fundo geral escuro estilo aplicativo moderno */
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }

    /* Sidebar moderna */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(236, 72, 153, 0.2);
    }

    /* Estilização dos containers/cards para parecer com o app da foto */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: #1e293b !important;
        border: 1px solid rgba(236, 72, 153, 0.25) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25) !important;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
        border-color: #f43f5e !important;
        transform: translateY(-2px);
    }

    /* Botões personalizados com toque feminino (rosa/magenta elegante) */
    .stButton > button {
        background: linear-gradient(135deg, #f43f5e 0%, #db2777 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        box-shadow: 0 4px 12px rgba(244, 63, 94, 0.3);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #fb7185 0%, #f43f5e 100%);
        box-shadow: 0 6px 16px rgba(244, 63, 94, 0.5);
        color: white;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(236, 72, 153, 0.3);
        border-radius: 20px;
        padding: 25px 20px;
        text-align: center;
        color: #FFFFFF;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        margin-bottom: 25px;
    }
    .hero-title { font-size: 2.2rem; font-weight: 800; margin-bottom: 5px; color: #f43f5e; letter-spacing: -0.5px; }
    .hero-subtitle { font-size: 0.95rem; font-weight: 400; color: #cbd5e1; }

    /* Cartão de Aniversário */
    .card-bday {
        background: linear-gradient(135deg, #500724 0%, #831843 100%);
        border-left: 6px solid #f43f5e;
        padding: 18px;
        border-radius: 14px;
        margin-bottom: 20px;
        color: #fce7f3;
        text-align: center;
        font-size: 1.1rem;
        box-shadow: 0px 6px 15px rgba(131, 24, 67, 0.4);
    }

    /* Rodapé */
    .developer-footer {
        background: #0f172a;
        color: #94a3b8;
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        margin-top: 35px;
        font-size: 0.85rem;
        border: 1px solid rgba(236, 72, 153, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CAMINHOS DOS ARQUIVOS (DIRETÓRIO DATA)
# -----------------------------------------------------------------------------
DATA_FILE = "data/jogadoras.json"
PRESENCAS_FILE = "data/presencas.json"
AVISOS_FILE = "data/avisos.json"
FINANCE_FILE = "data/financeiro.json"
ADMINS_FILE = "data/administradores.json"
REGULAMENTO_FILE = "data/regulamento.json"
SORTEIO_FILE = "data/sorteio.json"
COMPROVANTES_FILE = "data/comprovantes.json"

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])
if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])
if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])
if "comprovantes" not in st.session_state:
    st.session_state.comprovantes = carregar_dados(COMPROVANTES_FILE, [])
if "administradores" not in st.session_state:
    def_admins = [{"nome": "Admin Principal", "login": "admin", "senha": "1980", "principal": True}]
    st.session_state.administradores = carregar_dados(ADMINS_FILE, def_admins)
if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10 de cada mês",
        "recado": "Favor chegarem 10 minutos antes para organizar o jogo!",
        "pix": "peladinhafc@email.com",
        "limite_vagas": 15
    })
if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {"topico": "📌 1. Prioridade nas Vagas", "regrinha": "Mensalistas confirmando até as 17:00 de segunda têm prioridade na lista principal. Avulsas vão para a fila de espera e sobem após esse horário se houver vagas."},
        {"topico": "⏳ 2. Fila de Espera", "regrinha": "Jogadoras avulsas entram na fila de espera por ordem de chegada."},
        {"topico": "❌ 3. Desistências", "regrinha": "Ao cancelar, a primeira da fila é incluída no jogo."},
        {"topico": "💸 4. Mensalidades", "regrinha": "Pagas via Pix até a data estipulada."}
    ])
if "sorteio_oficial" not in st.session_state:
    st.session_state.sorteio_oficial = carregar_dados(SORTEIO_FILE, {})
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "admin_nome" not in st.session_state:
    st.session_state.admin_nome = ""
if "aba_ativa" not in st.session_state:
    st.session_state.aba_ativa = "Entrar"
if "menu_escolhido" not in st.session_state:
    st.session_state.menu_escolhido = "🏠 Início / Dashboard"

# -----------------------------------------------------------------------------
# BANNER DA APLICAÇÃO
# -----------------------------------------------------------------------------
st.markdown("""
<div class='hero-banner'>
    <div class='hero-title'>⚽ PELADINHA FC</div>
    <div class='hero-subtitle'>Gestão Inteligente & Sorteio de Futebol Feminino</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ANIVERSARIANTES DO DIA E WHATSAPP
# -----------------------------------------------------------------------------
aniversariantes_hoje_obj = [j for j in st.session_state.jogadoras if j.get("nascimento", "").strip() == hoje_str]
if aniversariantes_hoje_obj:
    st.balloons()
    for j_aniv in aniversariantes_hoje_obj:
        nome_aniv = j_aniv["nome"]
        tel_aniv = j_aniv.get("contato", "").strip()
        msg_wapp = urllib.parse.quote(f"Parabéns, {nome_aniv}! O Peladinha FC deseja a você um feliz aniversário! Muita saúde e gols! ⚽🎂")
        link_wapp = f"https://wa.me/55{tel_aniv.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')}?text={msg_wapp}" if tel_aniv else "#"
        
        st.markdown(f"""
        <div class='card-bday'>
            🎂 🎉 <b>PARABÉNS, {nome_aniv.upper()}!</b> 🎉 🎂<br>
            O Peladinha FC deseja a você um FELIZ ANIVERSÁRIO! Muita saúde e gols! ⚽🎈
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.admin_logged:
            if tel_aniv:
                st.markdown(f"<a href='{link_wapp}' target='_blank'><button style='background-color:#25D366; color:white; border:none; padding:8px 16px; border-radius:6px; cursor:pointer; font-weight:bold; margin-bottom:15px;'>📱 Enviar Mensagem de Aniversário via WhatsApp</button></a>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MENU LATERAL (SIDEBAR) COM SINCRONIZAÇÃO DE CARDS
# -----------------------------------------------------------------------------
st.sidebar.title("📌 Navegação")
lista_menu = ["🏠 Início / Dashboard", "📌 Presença no Jogo", "🔀 Sorteio de Times", "💸 Pagamento & Pix", "📜 Regulamento", "📋 Elenco de Jogadoras"]
if st.session_state.admin_logged:
    lista_menu.insert(3, "📊 Fluxo de Caixa (Admin)")
lista_menu.append("⚙️ Painel Admin")

if st.session_state.menu_escolhido not in lista_menu:
    st.session_state.menu_escolhido = "🏠 Início / Dashboard"

menu = st.sidebar.radio("Ir para:", lista_menu, index=lista_menu.index(st.session_state.menu_escolhido), key="radio_menu_principal")
st.session_state.menu_escolhido = menu

st.sidebar.markdown("---")
st.sidebar.title("👤 Área da Jogadora")

if st.session_state.usuario_logado:
    st.sidebar.success(f"Logada: **{st.session_state.usuario_logado}**")
    if st.sidebar.button("🚪 Sair da Conta"):
        st.session_state.usuario_logado = None
        st.rerun()
else:
    tab_log, tab_cad = st.sidebar.tabs(["Entrar", "Cadastrar"] if st.session_state.aba_ativa == "Entrar" else ["Cadastrar", "Entrar"])
    with tab_log:
        if st.session_state.msg_cadastro_sucesso:
            st.success("🎉 Cadastro realizado com sucesso! Faça login:")
            st.session_state.msg_cadastro_sucesso = False
        with st.form("form_login_player"):
            l_user = st.text_input("Login")
            l_pass = st.text_input("Senha", type="password")
            if st.form_submit_button("🔑 Entrar", use_container_width=True):
                user_found = next((j for j in st.session_state.jogadoras if j.get("login") == l_user and j.get("senha") == l_pass), None)
                if user_found:
                    st.session_state.usuario_logado = user_found["nome"]
                    st.rerun()
                else:
                    st.error("Login ou senha incorretos!")
    with tab_cad:
        with st.form("form_cad_player", clear_on_submit=True):
            c_nome = st.text_input("Seu Nome *")
            c_nasc = st.text_input("Nascimento (DD/MM) *", placeholder="Ex: 15/05")
            c_cont = st.text_input("WhatsApp / Contato", placeholder="Ex: 31999999999")
            c_user = st.text_input("Escolha um Login *")
            c_pass = st.text_input("Escolha uma Senha *", type="password")
            if st.form_submit_button("📝 Criar Conta", use_container_width=True):
                if c_nome and c_user and c_pass:
                    if any(j.get("login") == c_user.strip() for j in st.session_state.jogadoras):
                        st.error("Este Login já está em uso. Escolha outro!")
                    else:
                        st.session_state.jogadoras.append({
                            "nome": c_nome.strip(), "nascimento": c_nasc.strip(),
                            "login": c_user.strip(), "senha": c_pass.strip(),
                            "tipo": "Avulso", "mes_vigente": mes_vigente_str,
                            "contato": c_cont.strip(), "status": "Ativo", "status_pagamento": "Pendente"
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.session_state.aba_ativa = "Entrar"
                        st.session_state.msg_cadastro_sucesso = True
                        st.rerun()
                else:
                    st.error("Preencha Nome, Login e Senha!")

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Área do Administrador")

if not st.session_state.admin_logged:
    with st.sidebar.form("form_login_admin"):
        adm_input = st.text_input("Login ou Senha Admin", type="password")
        if st.form_submit_button("Acessar Como Admin", use_container_width=True):
            admin_encontrado = next((adm for adm in st.session_state.administradores if adm_input in [adm.get("senha"), adm.get("login")]), None)
            if admin_encontrado or adm_input == "1980":
                st.session_state.admin_logged = True
                st.session_state.admin_nome = admin_encontrado["nome"] if admin_encontrado else "Admin Principal"
                st.rerun()
            else:
                st.error("Senha/Login Admin incorreto!")
else:
    st.sidebar.info(f"🔑 Admin: **{st.session_state.admin_nome}**")
    if st.sidebar.button("Sair do Admin"):
        st.session_state.admin_logged = False
        st.session_state.admin_nome = ""
        st.rerun()

# -----------------------------------------------------------------------------
# LÓGICA DE ORDENAÇÃO DE PRESENÇA
# -----------------------------------------------------------------------------
def obter_nome_p(p):
    return p["nome"] if isinstance(p, dict) else p

def obter_hora_p(p):
    return p.get("hora", "") if isinstance(p, dict) else ""

def obter_tipo_p(p):
    return p.get("tipo", "Avulso") if isinstance(p, dict) else "Avulso"

lista_atual = sorted(st.session_state.presencas, key=lambda x: x.get("dt_confirmacao", x.get("hora", "")))
mensalistas = [p for p in lista_atual if p.get("tipo") == "Mensalista"]
avulsas = [p for p in lista_atual if p.get("tipo") == "Avulso"]
limite = st.session_state.avisos.get("limite_vagas", 15)

confirmadas = mensalistas[:limite]
espera = mensalistas[limite:] + avulsas

passou_prazo = hoje_dt.weekday() == 0 and hoje_dt.hour >= 17

if passou_prazo and len(confirmadas) < limite:
    vagas_sobrando = limite - len(confirmadas)
    promovidas = espera[:vagas_sobrando]
    confirmadas.extend(promovidas)
    espera = espera[vagas_sobrando:]

# -----------------------------------------------------------------------------
# SORTEIO AUTOMÁTICO
# -----------------------------------------------------------------------------
if hoje_dt.weekday() == 0 and (hoje_dt.hour > 18 or (hoje_dt.hour == 18 and hoje_dt.minute >= 30)):
    sorteio_salvo = st.session_state.sorteio_oficial
    if sorteio_salvo.get("data") != data_hoje_id:
        nomes_confirmadas = [obter_nome_p(p) for p in confirmadas]
        if len(nomes_confirmadas) >= 2:
            random.shuffle(nomes_confirmadas)
            qtd_t = 2
            res_times = {f"Time {i+1}": [] for i in range(qtd_t)}
            for idx, p in enumerate(nomes_confirmadas):
                res_times[f"Time {idx % qtd_t + 1}"].append(p)
            
            st.session_state.sorteio_oficial = {
                "data": data_hoje_id,
                "hora": f"{hoje_dt.strftime('%H:%M')} (Automático)",
                "times": res_times
            }
            salvar_dados(SORTEIO_FILE, st.session_state.sorteio_oficial)

# -----------------------------------------------------------------------------
# PÁGINAS DO SISTEMA
# -----------------------------------------------------------------------------
if menu == "🏠 Início / Dashboard":
    dashboard.run(confirmadas, espera, limite, st.session_state)

elif menu == "📌 Presença no Jogo":
    presenca.run(fuso_br, hoje_dt, salvar_dados, PRESENCAS_FILE, SORTEIO_FILE, confirmadas, espera, limite, obter_nome_p, obter_hora_p, obter_tipo_p)

elif menu == "🔀 Sorteio de Times":
    sorteio.run(data_hoje_id, hoje_dt, salvar_dados, SORTEIO_FILE, confirmadas, obter_nome_p)

elif menu == "📊 Fluxo de Caixa (Admin)":
    if not st.session_state.admin_logged:
        st.error("🔒 Área restrita aos administradores!")
    else:
        financeiro.run(fuso_br, hoje_dt, salvar_dados, FINANCE_FILE)

elif menu == "💸 Pagamento & Pix":
    st.subheader("💸 Dados para Pagamento e Envio de Comprovante")
    
    st.markdown("### 🔑 Chave Pix Atual")
    pix_atual = st.session_state.avisos.get('pix', 'Não informada')
    st.code(pix_atual, language="text")
    st.write(f"📅 **Vencimento:** {st.session_state.avisos.get('vencimento')}")

    st.markdown("---")

    if st.session_state.admin_logged:
        with st.expander("🛠️ [Admin] Editar Chave Pix e Vencimento"):
            with st.form("form_edit_pix_direto"):
                novo_pix = st.text_input("Chave Pix", value=pix_atual)
                novo_venc = st.text_input("Dia de Vencimento", value=st.session_state.avisos.get("vencimento", ""))
                if st.form_submit_button("💾 Atualizar Chave Pix"):
                    st.session_state.avisos["pix"] = novo_pix
                    st.session_state.avisos["vencimento"] = novo_venc
                    salvar_dados(AVISOS_FILE, st.session_state.avisos)
                    st.success("Chave Pix atualizada com sucesso!")
                    st.rerun()
        st.markdown("---")

    st.subheader("📤 Enviar Comprovante de Pagamento")
    
    if not st.session_state.usuario_logado and not st.session_state.admin_logged:
        st.warning("⚠️ **Você precisa estar logada na sua conta no menu lateral para enviar o comprovante!**")
    else:
        with st.form("form_enviar_comprovante", clear_on_submit=True):
            if st.session_state.admin_logged and not st.session_state.usuario_logado:
                nomes_j_todas = [j["nome"] for j in st.session_state.jogadoras]
                remetente_sel = st.selectbox("Enviar em nome de (Painel Admin):", nomes_j_todas) if nomes_j_todas else None
            else:
                remetente_sel = st.session_state.usuario_logado
                st.write(f"Enviando comprovante como: **{remetente_sel}**")

            detalhes_pag = st.text_input("Detalhes / Observação (Ex: Mensalidade Referente a Agosto)")
            arquivo_sub = st.file_uploader("📎 Imagem do Comprovante (Obrigatório)", type=["png", "jpg", "jpeg", "pdf"])
            
            btn_envio = st.form_submit_button("🚀 Enviar Comprovante", use_container_width=True)

            if btn_envio:
                if not arquivo_sub:
                    st.error("❌ ERRO: É estritamente obrigatório anexar a imagem do comprovante!")
                elif not remetente_sel:
                    st.error("❌ ERRO: Nenhuma jogadora válida selecionada.")
                else:
                    file_ext = arquivo_sub.name.split('.')[-1]
                    file_name = f"{int(datetime.now().timestamp())}_{random.randint(1000,9999)}.{file_ext}"
                    file_path = os.path.join(COMPROVANTES_DIR, file_name)
                    with open(file_path, "wb") as f:
                        f.write(arquivo_sub.getbuffer())

                    st.session_state.comprovantes.append({
                        "nome": remetente_sel,
                        "detalhes": detalhes_pag.strip() if detalhes_pag else "Pagamento Pix",
                        "data": hoje_dt.strftime("%d/%m/%Y %H:%M"),
                        "arquivo": file_path,
                        "status": "Pendente"
                    })
                    salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                    st.success("✅ Comprovante enviado com sucesso com a imagem anexada!")

    if st.session_state.admin_logged:
        st.markdown("---")
        st.subheader("📥 Comprovantes Recebidos (Admin)")
        if not st.session_state.comprovantes:
            st.info("Nenhum comprovante enviado no momento.")
        else:
            for idx, comp in enumerate(st.session_state.comprovantes):
                with st.expander(f"📄 Comprovante de: {comp['nome']} — ({comp['data']}) [Status: {comp.get('status', 'Pendente')}]"):
                    st.write(f"**Observação:** {comp['detalhes']}")
                    if os.path.exists(comp.get("arquivo", "")):
                        st.image(comp["arquivo"], caption=f"Comprovante de {comp['nome']}", use_container_width=True)
                    else:
                        st.warning("⚠️ Imagem do comprovante não encontrada no servidor.")

                    col_acao1, col_acao2 = st.columns(2)
                    if comp.get("status") == "Pendente":
                        valor_pg = st.number_input(f"Valor a dar baixa (R$) para {comp['nome']}:", min_value=0.0, value=50.0, step=5.0, key=f"val_comp_{idx}")
                        
                        if col_acao1.button("✅ Confirmar Pagamento", key=f"conf_comp_{idx}"):
                            st.session_state.financeiro.append({
                                "data": hoje_dt.strftime("%d/%m/%Y"),
                                "descricao": f"Mensalidade - {comp['nome']}",
                                "tipo": "Entrada",
                                "valor": float(valor_pg)
                            })
                            salvar_dados(FINANCE_FILE, st.session_state.financeiro)

                            for j in st.session_state.jogadoras:
                                if j["nome"] == comp["nome"]:
                                    j["mes_vigente"] = mes_vigente_str
                                    j["status_pagamento"] = "Pago"
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)

                            st.session_state.comprovantes[idx]["status"] = "Confirmado"
                            salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                            st.success(f"Pagamento de {comp['nome']} confirmado!")
                            st.rerun()

                        if col_acao2.button("❌ Rejeitar Pagamento", key=f"rej_comp_{idx}"):
                            for j in st.session_state.jogadoras:
                                if j["nome"] == comp["nome"]:
                                    j["status_pagamento"] = "Pendente"
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)

                            st.session_state.comprovantes[idx]["status"] = "Rejeitado"
                            salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                            st.warning(f"Comprovante de {comp['nome']} marcado como rejeitado.")
                            st.rerun()
                    else:
                        st.info(f"Este comprovante já foi processado como: **{comp.get('status')}**")

elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento do Peladinha FC")
    st.markdown("---")
    for item in st.session_state.regulamento:
        with st.expander(f"**{item['topico']}**", expanded=True):
            st.write(item["regrinha"])

elif menu == "📋 Elenco de Jogadoras":
    st.subheader("🏃‍♀️ Elenco do Peladinha FC")
    tab_elenco, tab_mensalistas = st.tabs(["Todas as Cadastradas", "🌟 Mensalistas Ativas"])
    
    if st.session_state.jogadoras:
        df = pd.DataFrame(st.session_state.jogadoras)
        for j in st.session_state.jogadoras:
            if "mes_vigente" not in j:
                j["mes_vigente"] = mes_vigente_str
            if "status_pagamento" not in j:
                j["status_pagamento"] = "Pendente"

        cols_visiveis = [c for c in ["nome", "tipo", "nascimento", "status_pagamento", "status"] if c in df.columns]
        
        with tab_elenco:
            st.dataframe(df[cols_visiveis], use_container_width=True, hide_index=True)
            
        with tab_mensalistas:
            df_mensalistas = df[df["tipo"] == "Mensalista"]
            if not df_mensalistas.empty:
                st.write("Essas são as mensalistas ativas do nosso grupo neste ano/mês:")
                st.dataframe(df_mensalistas[cols_visiveis], use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma mensalista registrada no momento.")
    else:
        st.info("Nenhuma jogadora cadastrada.")

elif menu == "⚙️ Painel Admin":
    admin.run(salvar_dados, AVISOS_FILE, DATA_FILE, ADMINS_FILE, REGULAMENTO_FILE, mes_vigente_str)

# RODAPÉ
st.markdown("<div class='developer-footer'>Desenvolvido por <b>Vagner Souza / Ciência da Computação</b></div>", unsafe_allow_html=True)
