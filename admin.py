import streamlit as st
import pandas as pd

def run(salvar_dados, AVISOS_FILE, DATA_FILE, ADMINS_FILE, REGULAMENTO_FILE, mes_vigente_str):
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
                        st.success("Dados atualizados!")
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
