elif menu == "🗑️ Excluir vinho":
    st.subheader("🗑️ Remover do Estoque")
    if st.session_state.estoque:
        opcoes = [
            f"{i + 1}. {v.get('nome')} - {v.get('pallet')}"
            for i, v in enumerate(st.session_state.estoque)
        ]
        idx = st.selectbox(
            "Selecione para excluir:", range(len(opcoes)), format_func=lambda x: opcoes[x]
        )
        if st.button("🗑️ Excluir Item Selecionado", use_container_width=True):
            removido = st.session_state.estoque.pop(idx)
            salvar_dados(st.session_state.estoque)
            st.success(f"✅ '{removido.get('nome')}' foi excluído com sucesso!")
            st.rerun()
    else:
        st.info("ℹ️ Não há vinhos cadastrados para excluir.")

elif menu == "📥 Importar planilha (CSV/Excel)":
    st.subheader("📥 Importar Dados Externos")
    arquivo_import = st.file_uploader("Envie arquivo CSV ou Excel", type=["csv", "xlsx"])
    if arquivo_import is not None:
        try:
            if arquivo_import.name.endswith(".csv"):
                df_imp = pd.read_csv(arquivo_import)
            else:
                df_imp = pd.read_excel(arquivo_import)
            
            if st.button("💾 Confirmar Importação e Substituir Estoque", use_container_width=True):
                st.session_state.estoque = df_imp.to_dict(orient="records")
                salvar_dados(st.session_state.estoque)
                st.success("✅ Estoque importado com sucesso!")
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")

elif menu == "📤 Exportar planilha (CSV)":
    st.subheader("📤 Exportar Dados do Estoque")
    if st.session_state.estoque:
        df_exp = pd.DataFrame(st.session_state.estoque)
        if "foto" in df_exp.columns:
            df_exp = df_exp.drop(columns=["foto"])
        csv_data = df_exp.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Baixar Arquivo CSV",
            data=csv_data,
            file_name="estoque_galpao_premium.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("ℹ️ Estoque vazio para exportação.")

elif menu == "🏷️ Gerar QR Code do Pallet":
    st.subheader("🏷️ Gerador de QR Codes para as Posições")
    c_cor, c_pal = st.columns(2)
    with c_cor:
        sel_c = st.selectbox("Corredor:", LISTA_CORREDORES, key="qr_corredor")
    with c_pal:
        sel_p = st.selectbox("Pallet:", LISTA_PALLETS, key="qr_pallet")

    pallet_alvo = f"{sel_c} - {sel_p}"
    url_qrcode = f"{URL_APLICATIVO}/?auth={SENHA_ACESSO}&pallet={urllib.parse.quote_plus(pallet_alvo)}"

    st.markdown(f"**Link de Acesso Direto:** `{url_qrcode}`")
    
    qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote_plus(url_qrcode)}"
    st.image(qr_img_url, caption=f"QR Code para {pallet_alvo}", width=250)
    st.info("💡 Dica: Você pode clicar com o botão direito na imagem acima para salvar e imprimir a etiqueta do pallet.")

elif menu == "📷 Escanear QR Code":
    st.subheader("📷 Leitor de QR Code via Câmera")
    st.write("Envie uma foto contendo o QR Code da etiqueta do pallet para consultar instantaneamente:")
    
    foto_qr = st.file_uploader("Foto da Etiqueta/QR Code:", type=["jpg", "jpeg", "png"], key="upload_qr")
    if foto_qr is not None:
        bytes_qr = foto_qr.getvalue()
        st.image(bytes_qr, caption="Imagem Enviada", width=300)
        
        resultado_decodificado = decodificar_qr_code(bytes_qr)
        
        if resultado_decodificado:
            st.success(f"✅ QR Code Lido com Sucesso: `{resultado_decodificado}`")
            
            parsed_url = urllib.parse.urlparse(resultado_decodificado)
            query_dict = urllib.parse.parse_qs(parsed_url.query)
            
            pallet_encontrado = None
            if "pallet" in query_dict:
                pallet_encontrado = query_dict["pallet"][0]
            else:
                pallet_encontrado = resultado_decodificado
                
            st.markdown(f"### 📦 Vinhos no local: **{pallet_encontrado}**")
            vinhos_lido = [v for v in st.session_state.estoque if v.get("pallet") == pallet_encontrado]
            
            if vinhos_lido:
                for v in vinhos_lido:
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
            else:
                st.warning(f"⚠️ Nenhum vinho registrado na posição **{pallet_encontrado}**.")
        else:
            st.error("❌ Não foi possível detectar um QR Code válido na imagem. Certifique-se de que a imagem está nítida e bem iluminada.")
