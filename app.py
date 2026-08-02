import streamlit as st
import pandas as pd
import json
import os
import random
import urllib.parse
from datetime import datetime, timedelta, timezone

# IMPORTANDO AS FUNÇÕES DO UTILS E OS MÓDULOS
from utils import carregar_dados, salvar_dados
import financeiro

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
    page_title="Peladinha FC | Gestão de Futebol Feminino",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

    .hero-banner {
        background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.85)), 
                    url('https://images.unsplash.com/photo-1518091043644-c1d4457512c6?q=80&w=1200&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        padding: 25px 15px;
        text-align: center;
        color: #FFFFFF;
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15);
        margin-bottom: 20px;
    }
    .hero-title { font-size: 2.0rem; font-weight: 800; margin-bottom: 5px; color: #FFFFFF; }
    .hero-subtitle { font-size: 0.9rem; font-weight: 300; color: #E2E8F0; }

    .card-notice {
        background: #FEF3C7;
        border-left: 6px solid #F59E0B;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        color: #78350F;
    }

    .card-bday {
        background: linear-gradient(135deg, #FCE7F3 0%, #FBCFE8 100%);
        border-left: 6px solid #EC4899;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 20px;
        color: #831843;
        text-align: center;
        font-size: 1.1rem;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    }

    .card-team {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 5px solid #EC4899;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }

    .developer-footer {
        background: #0F172A;
        color: #94A3B8;
        text-align: center;
        padding: 12px;
        border-radius: 10px;
        margin-top: 30px;
        font-size: 0.85rem;
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
if "msg_cadastro_sucesso" not in st.session_state:
    st.session_state.msg_cadastro_sucesso = False


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
            else:
                st.caption(f"⚠️ A jogadora {nome_aniv} não tem número de WhatsApp/contato cadastrado.")

# -----------------------------------------------------------------------------
# MENU LATERAL (SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.title("📌 Navegação")
lista_menu = ["📌 Presença no Jogo", "🔀 Sorteio de Times", "💸 Pagamento & Pix", "📜 Regulamento", "📋 Elenco de Jogadoras"]
if st.session_state.admin_logged:
    lista_menu.insert(2, "📊 Fluxo de Caixa (Admin)")
lista_menu.append("⚙️ Painel Admin")

menu = st.sidebar.radio("Ir para:", lista_menu)

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
if menu == "📌 Presença no Jogo":
    st.markdown(f"""
    <div class='card-notice'>
        📢 <b>AVISOS:</b> Limitado a <b>{limite} vagas</b>. <br>
        ⭐ <b>Mensalistas têm prioridade até SEGUNDA-FEIRA às 17:00!</b> Avulsas ficam na fila de espera e sobem após esse horário caso haja vagas.<br>
        💡 <i>{st.session_state.avisos.get('recado')}</i><br>
        ⏰ <i>Sorteio oficial automático: <b>Segunda-feira às 18:30</b>.</i>
    </div>
    """, unsafe_allow_html=True)

    col_lista, col_acoes = st.columns([1, 1])

    with col_lista:
        st.subheader("📋 Lista de Presença")
        st.markdown(f"### 🟢 Confirmadas no Jogo ({len(confirmadas)}/{limite})")
        if not confirmadas:
            st.info("Nenhuma jogadora confirmada ainda.")
        else:
            for i, p in enumerate(confirmadas, 1):
                nome_p, hora_p, tipo_p = obter_nome_p(p), obter_hora_p(p), obter_tipo_p(p)
                st.write(f"**{i}.** {nome_p} `[{tipo_p}]` — *(às {hora_p})*")

        st.markdown("---")
        st.markdown(f"### ⏳ Fila de Espera ({len(espera)})")
        if not espera:
            st.caption("Nenhuma jogadora na fila de espera.")
        else:
            for i, p in enumerate(espera, 1):
                nome_p, hora_p, tipo_p = obter_nome_p(p), obter_hora_p(p), obter_tipo_p(p)
                badge = "🏃 Avulsa" if tipo_p == "Avulso" else "⭐ Mensalista"
                st.write(f"**{i}º na espera:** {nome_p} `[{badge}]` — *(às {hora_p})*")

    with col_acoes:
        st.subheader("✍️ Marcar Minha Presença")
        if not (st.session_state.usuario_logado or st.session_state.admin_logged):
            st.warning("⚠️ **Faça Login no menu lateral para confirmar presença!**")
        else:
            with st.form("form_presenca_express"):
                if st.session_state.admin_logged and not st.session_state.usuario_logado:
                    nomes_cad = [j["nome"] for j in st.session_state.jogadoras]
                    jogadora_sel = st.selectbox("Selecione a jogadora para alterar:", nomes_cad) if nomes_cad else None
                else:
                    jogadora_sel = st.session_state.usuario_logado
                    st.write(f"Conectada como: **{jogadora_sel}**")

                c1, c2 = st.columns(2)
                btn_confirmar = c1.form_submit_button("👍 Confirmar Presença", use_container_width=True)
                btn_cancelar = c2.form_submit_button("❌ Cancelar Presença", use_container_width=True)

            if jogadora_sel:
                dados_j = next((j for j in st.session_state.jogadoras if j["nome"] == jogadora_sel), None)
                tipo_j = dados_j.get("tipo", "Avulso") if dados_j else "Avulso"

                pos_confirmada = next((idx + 1 for idx, p in enumerate(confirmadas) if obter_nome_p(p) == jogadora_sel), None)
                pos_espera = next((idx + 1 for idx, p in enumerate(espera) if obter_nome_p(p) == jogadora_sel), None)

                if pos_confirmada:
                    st.success(f"🎉 **VOCÊ ESTÁ NO JOGO!** Posição **{pos_confirmada}**.")
                elif pos_espera:
                    st.warning(f"⏳ **VOCÊ ESTÁ NA FILA DE ESPERA!** Posição **{pos_espera}º**.")

                ja_na_lista = pos_confirmada is not None or pos_espera is not None

                if btn_confirmar:
                    if ja_na_lista:
                        st.warning("Seu nome já está registrado na lista!")
                    else:
                        st.session_state.presencas.append({
                            "nome": jogadora_sel, 
                            "hora": hoje_dt.strftime("%H:%M"),
                            "tipo": tipo_j,
                            "dt_confirmacao": hoje_dt.isoformat()
                        })
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.rerun()

                if btn_cancelar:
                    if ja_na_lista:
                        st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != jogadora_sel]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.info("Presença cancelada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Seu nome não está na lista.")

        if st.session_state.admin_logged:
            st.markdown("---")
            st.subheader("🚨 Ações de Admin")
            if st.button("🧹 Zerar Toda a Lista", use_container_width=True):
                st.session_state.presencas = []
                salvar_dados(PRESENCAS_FILE, [])
                st.session_state.sorteio_oficial = {}
                salvar_dados(SORTEIO_FILE, {})
                st.warning("Lista e sorteios zerados!")
                st.rerun()

elif menu == "🔀 Sorteio de Times":
    st.subheader("🔀 Sorteio de Times")
    tab_oficial, tab_quadra = st.tabs(["🏆 Sorteio Oficial (Pré-Jogo)", "⚡ Ajuste Rápido de Quadra"])

    with tab_oficial:
        sorteio_salvo = st.session_state.sorteio_oficial
        if sorteio_salvo and "times" in sorteio_salvo:
            st.success(f"✅ **Sorteio Oficial Realizado ({sorteio_salvo.get('hora', '')})**")
            cols = st.columns(len(sorteio_salvo["times"]))
            for idx, (nome_time, membros) in enumerate(sorteio_salvo["times"].items()):
                with cols[idx]:
                    st.markdown(f"<div class='card-team'><h3>⚽ {nome_time}</h3>", unsafe_allow_html=True)
                    for item in membros:
                        st.write(f"• **{item}**")
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("⏰ O Sorteio Oficial é realizado automaticamente às **Segundas-feiras, às 18:30**.")

        if st.session_state.admin_logged:
            st.markdown("---")
            st.write("#### 🛠️ Forçar Novo Sorteio (Admin)")
            confirmadas_nomes = [obter_nome_p(p) for p in confirmadas]
            qtd_t = st.slider("Dividir em quantos times?", 2, 4, 2, key="slider_oficial")
            if st.button("🎲 Executar Sorteio Agora", use_container_width=True):
                if len(confirmadas_nomes) < qtd_t:
                    st.error("Número insuficiente de confirmadas.")
                else:
                    temp = confirmadas_nomes.copy()
                    random.shuffle(temp)
                    res_times = {f"Time {i+1}": [] for i in range(qtd_t)}
                    for idx, p in enumerate(temp):
                        res_times[f"Time {idx % qtd_t + 1}"].append(p)
                    
                    st.session_state.sorteio_oficial = {
                        "data": data_hoje_id, "hora": f"{hoje_dt.strftime('%H:%M')} (Manual)", "times": res_times
                    }
                    salvar_dados(SORTEIO_FILE, st.session_state.sorteio_oficial)
                    st.rerun()

    with tab_quadra:
        st.write("### ⚡ Sorteio na Quadra")
        confirmadas_nomes = [obter_nome_p(p) for p in confirmadas]
        if not confirmadas_nomes:
            st.info("Nenhuma jogadora confirmada na lista principal.")
        else:
            presentes = st.multiselect("Marque as jogadoras presentes na quadra:", confirmadas_nomes, default=confirmadas_nomes)
            qtd_t_q = st.slider("Dividir em quantos times?", 2, 4, 2, key="slider_quadra")
            if st.button("🎲 Sortear Apenas Presentes", use_container_width=True):
                if len(presentes) < qtd_t_q:
                    st.error("Selecione mais jogadoras.")
                else:
                    temp = presentes.copy()
                    random.shuffle(temp)
                    times_q = [[] for _ in range(qtd_t_q)]
                    for idx, p in enumerate(temp):
                        times_q[idx % qtd_t_q].append(p)
                    cols_q = st.columns(qtd_t_q)
                    for i, t in enumerate(times_q):
                        with cols_q[i]:
                            st.markdown(f"<div class='card-team'><h3>⚽ Time {i+1} (Quadra)</h3>", unsafe_allow_html=True)
                            for item in t:
                                st.write(f"• **{item}**")
                            st.markdown("</div>", unsafe_allow_html=True)

elif menu == "📊 Fluxo de Caixa (Admin)":
    if not st.session_state.admin_logged:
        st.error("🔒 Área restrita aos administradores!")
    else:
        # AQUI É ONDE CHAMAMOS O MÓDULO FINANCEIRO SEPARADO!
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
    st.subheader("⚙️ Painel do Administrador")
    if not st.session_state.admin_logged:
        st.error("🔒 Faça login como Admin na barra lateral para acessar esta área!")
    else:
        t_conf, t_cad, t_ger_jog, t_admins, t_reg = st.tabs([
            "⚙️ Configurações Gerais", "➕ Cadastrar Jogadora", "📋 Gerenciar Elenco", "👥 Gerenciar Admins", "📜 Gerenciar Regulamento"
        ])
        
        with t_conf:
            limite_v = st.number_input("Limite de Vagas do Jogo:", value=st.session_state.avisos.get("limite_vagas", 15))
            rec_v = st.text_area("Recado/Aviso Geral:", value=st.session_state.avisos.get("recado", ""))
            pix_cfg = st.text_input("Chave Pix:", value=st.session_state.avisos.get("pix", ""))
            venc_cfg = st.text_input("Vencimento:", value=st.session_state.avisos.get("vencimento", ""))
            
            if st.button("💾 Salvar Configurações", use_container_width=True):
                st.session_state.avisos["limite_vagas"] = int(limite_v)
                st.session_state.avisos["recado"] = rec_v
                st.session_state.avisos["pix"] = pix_cfg
                st.session_state.avisos["vencimento"] = venc_cfg
                salvar_dados(AVISOS_FILE, st.session_state.avisos)
                st.success("Configurações salvas!")
                st.rerun()

        with t_cad:
            with st.form("form_adm_cad", clear_on_submit=True):
                a_nome = st.text_input("Nome Completo *")
                a_nasc = st.text_input("Data de Nascimento (DD/MM)")
                a_tipo = st.selectbox("Categoria Inicial", ["Mensalista", "Avulso"])
                a_cont = st.text_input("WhatsApp / Contato")
                a_user = st.text_input("Login")
                a_pass = st.text_input("Senha", type="password")

                if st.form_submit_button("➕ Cadastrar Jogadora", use_container_width=True):
                    if a_nome.strip():
                        st.session_state.jogadoras.append({
                            "nome": a_nome.strip(), "nascimento": a_nasc.strip(), "tipo": a_tipo,
                            "mes_vigente": mes_vigente_str, "login": a_user.strip(), "senha": a_pass.strip(),
                            "contato": a_cont.strip(), "status": "Ativo", "status_pagamento": "Pendente"
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"Jogadora {a_nome} cadastrada!")
                        st.rerun()

        with t_ger_jog:
            if not st.session_state.jogadoras:
                st.info("Nenhuma jogadora no elenco.")
            else:
                nomes_jog = [f"{j['nome']} ({j.get('tipo', 'Avulso')})" for j in st.session_state.jogadoras]
                idx_j_sel = st.selectbox("Selecione a jogadora:", range(len(nomes_jog)), format_func=lambda x: nomes_jog[x])
                j_obj = st.session_state.jogadoras[idx_j_sel]

                with st.form("form_edit_jog"):
                    ej_nome = st.text_input("Nome", value=j_obj.get("nome", ""))
                    ej_tipo = st.selectbox("Categoria", ["Mensalista", "Avulso"], index=0 if j_obj.get("tipo") == "Mensalista" else 1)
                    ej_nasc = st.text_input("Nascimento (DD/MM)", value=j_obj.get("nascimento", ""))
                    ej_cont = st.text_input("WhatsApp / Contato", value=j_obj.get("contato", ""))
                    ej_user = st.text_input("Login", value=j_obj.get("login", ""))
                    ej_pass = st.text_input("Senha", value=j_obj.get("senha", ""), type="password")
                    ej_pag = st.selectbox("Status Pagamento", ["Pendente", "Pago"], index=0 if j_obj.get("status_pagamento") != "Pago" else 1)

                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        st.session_state.jogadoras[idx_j_sel].update({
                            "nome": ej_nome.strip(), "nascimento": ej_nasc.strip(), "tipo": ej_tipo,
                            "contato": ej_cont.strip(), "login": ej_user.strip(), "senha": ej_pass.strip(),
                            "status_pagamento": ej_pag
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"Dados atualizados!")
                        st.rerun()

                if st.button("🗑️ Excluir Jogadora", type="primary", use_container_width=True):
                    st.session_state.jogadoras.pop(idx_j_sel)
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.success("Removida!")
                    st.rerun()

        with t_admins:
            for index, adm in enumerate(st.session_state.administradores):
                col_info, col_btn = st.columns([3, 1])
                col_info.write(f"👤 **{adm['nome']}** | Login: `{adm['login']}`")
                if not (adm.get("principal") or index == 0):
                    if col_btn.button("🗑️ Excluir", key=f"del_adm_{index}"):
                        st.session_state.administradores.pop(index)
                        salvar_dados(ADMINS_FILE, st.session_state.administradores)
                        st.rerun()

            if len(st.session_state.administradores) < 4:
                st.write("#### ➕ Adicionar Administrador")
                with st.form("form_novo_adm", clear_on_submit=True):
                    adm_n = st.text_input("Nome *")
                    adm_l = st.text_input("Login *")
                    adm_s = st.text_input("Senha *", type="password")
                    if st.form_submit_button("💾 Salvar Administrador"):
                        if adm_n.strip() and adm_l.strip() and adm_s.strip():
                            st.session_state.administradores.append({"nome": adm_n.strip(), "login": adm_l.strip(), "senha": adm_s.strip(), "principal": False})
                            salvar_dados(ADMINS_FILE, st.session_state.administradores)
                            st.rerun()

        with t_reg:
            if not st.session_state.regulamento:
                st.info("Nenhum tópico cadastrado.")
            sub_t_edit, sub_t_add, sub_t_del = st.tabs(["✏️ Editar Regra", "➕ Nova Regra", "🗑️ Excluir Regra"])

            with sub_t_edit:
                if st.session_state.regulamento:
                    lista_topicos = [r["topico"] for r in st.session_state.regulamento]
                    idx_reg_sel = st.selectbox("Escolha a regra para editar:", range(len(lista_topicos)), format_func=lambda x: lista_topicos[x])
                    reg_obj = st.session_state.regulamento[idx_reg_sel]

                    with st.form("form_edit_reg"):
                        er_topico = st.text_input("Título", value=reg_obj.get("topico", ""))
                        er_texto = st.text_area("Descrição", value=reg_obj.get("regrinha", ""), height=150)
                        if st.form_submit_button("💾 Salvar", use_container_width=True):
                            st.session_state.regulamento[idx_reg_sel] = {"topico": er_topico.strip(), "regrinha": er_texto.strip()}
                            salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                            st.rerun()

            with sub_t_add:
                with st.form("form_novo_reg", clear_on_submit=True):
                    r_topico = st.text_input("Título", placeholder="Ex: 📌 7. Uniformes")
                    r_texto = st.text_area("Descrição", placeholder="Texto...")
                    if st.form_submit_button("➕ Adicionar", use_container_width=True):
                        if r_topico and r_texto:
                            st.session_state.regulamento.append({"topico": r_topico.strip(), "regrinha": r_texto.strip()})
                            salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                            st.rerun()

            with sub_t_del:
                if st.session_state.regulamento:
                    lista_topicos_del = [r["topico"] for r in st.session_state.regulamento]
                    idx_reg_del = st.selectbox("Selecione para apagar:", range(len(lista_topicos_del)), format_func=lambda x: lista_topicos_del[x])
                    if st.button("🗑️ Confirmar Exclusão", type="primary", use_container_width=True):
                        st.session_state.regulamento.pop(idx_reg_del)
                        salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                        st.rerun()

# RODAPÉ
st.markdown("<div class='developer-footer'>Desenvolvido por <b>Vagner Souza / Ciência da Computação</b></div>", unsafe_allow_html=True)
