import streamlit as st

def run(fuso_br, hoje_dt, salvar_dados, PRESENCAS_FILE, SORTEIO_FILE, confirmadas, espera, limite, obter_nome_p, obter_hora_p, obter_tipo_p):
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
