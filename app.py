import streamlit as st
import requests

# 1. Configuração da página
st.set_page_config(page_title="Visualização do Pallet", page_icon="🍷", layout="centered")

# 2. Pega o parâmetro 'pallet' ou 'p' diretamente da URL do Streamlit (Semelhante ao getPalletFromUrl)
query_params = st.query_params
pallet = query_params.get("pallet") or query_params.get("p")

# 3. Função para buscar vinhos na API (Substitui o base44.entities.Vinho.list())
@st.cache_data(ttl=60)
def carregar_vinhos_api():
    try:
        # Exemplo de chamada HTTP para a API Base44 ou backend correspondente
        response = requests.get("https://sua-api-base44.com/api/vinhos")
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    # Caso a API não esteja conectada, retorna lista vazia
    return []

# Banners de tipo (Cores estilizadas)
def badge_tipo(tipo):
    cores = {
        "Tinto": "#FEE2E2; color: #991B1B",
        "Branco": "#FEF3C7; color: #92400E",
        "Rosé": "#FCE7F3; color: #9D174D",
        "Espumante": "#CCFBF1; color: #115E59"
    }
    cor_estilo = cores.get(tipo, "#E5E7EB; color: #1F2937")
    return f'<span style="background-color: {cor_estilo}; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{tipo}</span>'

# Interface Principal
if not pallet:
    st.warning("📍 Nenhum pallet informado. Escaneie um QR Code ou use a busca.")
else:
    st.markdown("### ✅ QR Code lido com sucesso")
    st.title(f"Vinhos alocados em: **{pallet}**")

    # Botão para ver todo o estoque
    if st.button("⬅️ Ver todo o estoque"):
        st.query_params.clear()
        st.rerun()

    st.markdown("---")

    # Carrega os dados da API
    with st.spinner("Carregando vinhos..."):
        vinhos = carregar_vinhos_api()

    # Filtra os vinhos pelo pallet lido
    termo = pallet.strip().lower()
    encontrados = []
    
    for v in vinhos:
        # Pega a localização do vinho
        loc = str(v.get("pallet", "") or v.get("localizacao", "")).lower()
        if loc and (termo in loc or loc in termo):
            encontrados.append(v)

    # Exibição dos resultados
    if not encontrados:
        st.info(f"🍷 Nenhum vinho cadastrado em **{pallet}** até o momento.")
    else:
        for v in encontrados:
            with st.container():
                col_info, col_loc = st.columns([3, 1])
                
                with col_info:
                    nome = v.get("nome", "Sem nome")
                    tipo = v.get("tipo", "")
                    safra = v.get("safra", "")
                    
                    html_badge = badge_tipo(tipo) if tipo else ""
                    html_safra = f'<span style="background-color: #F3F4F6; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Safra {safra}</span>' if safra else ""
                    
                    st.markdown(f"### {nome} {html_badge} {html_safra}", unsafe_allow_html=True)
                    st.write(f"**Lado:** {v.get('lado', '—')} · **Caixa:** {v.get('caixa', '—')} · **Volume:** {v.get('volume', '—')}")
                
                with col_loc:
                    st.markdown(f"📍 **{v.get('pallet', 'S/L')}**")
                
                st.markdown("---")
