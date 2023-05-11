import streamlit as st
from PIL import Image


st.set_page_config(page_title = 'Home')

image_patch = 'logo.png'
image = Image.open(image_patch) #Comando para importar imagem da LIB PIL
st.sidebar.image(image, width = 200)

# Criando os primeiros elementos da barra lateral
st.sidebar.markdown('# Cury Company') # Comando sidebar cria o botão da barra lateral
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Bruno Henrique')

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi Construído para acompanhar as métricas de crescimento dos Entregadores e Resutaurantes.
    ### Como Utilizar esse Growth Dashboard?
    
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de Comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de Geolocalização.
    - Visão Entregador:
        - Acompanhamento dos Indicadores semanais de crescimento        
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    
    ### Ask for Help
    - Time de Data Sciense no Discord
        - @Bruno Henrique#2610
    
    """)

