# Importando Libs

import plotly.express as px
import folium
from haversine import haversine
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title = 'Visão Empresa', layout = 'wide')

# =========================================================
# Funções
# =========================================================

def limpando_df(df1):
    """ Esta Função faz a limpeza dos dados do DF e retorna um novo DF limpo.
        
        Tipos de Limpeza:
        1. Remoção dos Valores NaN
        2. Mudança do tipo da coluna de Dados
        3. Remoção dos espaços das variáveis de Texto
        4. Formatação da Coluna de datas
        5. Limoeza da coluna Tempo (Remoção do texto da variável numérica)
        
        Input: DataFrame
        Output: DataFrame    
    """
    
    # Convertendo texto em numeros de uma coluna, porem antes retirando os valores nulos para não atrapalhar a conversão
    
    linhas_selecionadas = (df1['Delivery_person_Age'] != "NaN ") # Marcando os valores diferentes de NaN
    df1 = df1.loc[linhas_selecionadas,:].copy() # Selecionando no DF somente os valores diferentes de NaN
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int) # Convertendo a idade em número

    # Convertendo texto em numeros flutuantes de uma coluna
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float) # Convertendo a idade em número e guardando na coluna novamente

    # Convertendo texto em data com os valores de uma coluna, , porem antes retirando os valores nulos para não atrapalhar a conversão
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'],format = '%d-%m-%Y')

    # Convertendo texto em número e guardando na coluna novamente 
    linhas_selecionadas2 = (df1['multiple_deliveries'] != "NaN " )# Marcando os valores diferentes de NaN
    df1 = df1.loc[linhas_selecionadas2,:].copy() # Selecionando no DF somente os valores difetrentes de NaN
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int) 

    # Retirando os valores NaN
    linhas_selecionadas2 = (df1['Road_traffic_density'] != "NaN " )# Marcando os valores diferentes de NaN
    df1 = df1.loc[linhas_selecionadas2,:].copy() # Selecionando no DF somente os valores difetrentes de NaN
    linhas_selecionadas2 = (df1['City'] != "NaN " )# Marcando os valores diferentes de NaN
    df1 = df1.loc[linhas_selecionadas2,:].copy() # Selecionando no DF somente os valores difetrentes de NaN
    linhas_selecionadas2 = (df1['Festival'] != "NaN " )# Marcando os valores diferentes de NaN
    df1 = df1.loc[linhas_selecionadas2,:].copy() # Selecionando no DF somente os valores difetrentes de NaN

    #Retirando os espaços no final
    df1.loc[:,"ID"] = df1.loc[:,"ID"].str.strip() # Outra forma de remover os espaços no final do texto, só que agora na coluna toda duma vez
    df1.loc[:,"Delivery_person_ID"] = df1.loc[:,"Delivery_person_ID"].str.strip()
    df1.loc[:,"Road_traffic_density"] = df1.loc[:,"Road_traffic_density"].str.strip()
    df1.loc[:,"Type_of_order"] = df1.loc[:,"Type_of_order"].str.strip()
    df1.loc[:,"Type_of_vehicle"] = df1.loc[:,"Type_of_vehicle"].str.strip()
    df1.loc[:,"City"] = df1.loc[:,"City"].str.strip()
    df1.loc[:,"Festival"] = df1.loc[:,"Festival"].str.strip()

    # Tirando o MIN da ultima coluna
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1

def order_metric(df1):
    """Recebe um DF e plota um grafico de barras com a QTD de pedidos por dia
            
        Input: DF
        Output: Gráfico de Barra
        
    """
    # Colunas DF
    cols = ['ID', 'Order_Date']       
    #Seleção de linhas e agrupando
    pedidos_dia = df1.loc[:,cols].groupby('Order_Date').count().reset_index()
    # Desenhar o Grafico de barras com a lib Polty
    fig = px.bar(pedidos_dia, x='Order_Date', y='ID')
            
    return fig

def traffic_order_share( df1):
    """ Recebe um DF e plota um grafico de Pizza da tipo de densidade de trafego 
        
        Input: DF
        Output: Gráfico de Pizza
        
    """
    # Selecionando as colunas DF
    cols = ['ID', 'Road_traffic_density']
    # Agrupando por densidade e criando coluna percentual
    pedidos_trafego = df1.loc[:,cols].groupby('Road_traffic_density').count().reset_index()
    pedidos_trafego['%_Entregas'] = pedidos_trafego['ID'] / pedidos_trafego['ID'].sum()
    fig = px.pie(pedidos_trafego,values='%_Entregas', names= 'Road_traffic_density')

    return fig

def volume_cidade_trafego(df1):
    """ Recebe um DF e plota um grafico de Bolha do volume de pedidos por cidade e densidade de trafego 
        
        Input: DF
        Output: Gráfico de Bolha
        
    """
    cols = ['ID', 'Road_traffic_density', "City"]
    volume_pedido_trafego = df1.loc[:,cols].groupby(['City','Road_traffic_density']).count().reset_index()
    # Criando grafico de bolhas
    fig = px.scatter(volume_pedido_trafego,x='City',y='Road_traffic_density',size='ID',color='City')
                
    return fig

def pedidos_semana( df1 ):
    """ Recebe um DF e plota um grafico de Linha com os pedidos por semana
        
        Input: DF
        Output: Gráfico de Linha
        
    """
    # Criar a coluna de semana 
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    #Seleção de linhas e agrupando
    cols = ['ID', "Week_of_year"]
    pedidos_semana = df1.loc[:,cols].groupby('Week_of_year').count().reset_index()
    # Desenhar o Grafico de linhas com a lib Polty
    fig = px.line(pedidos_semana, x='Week_of_year', y='ID')
                
    return fig

def entregadores_por_semana( df1 ):
    """ Recebe um DF e plota um grafico de Linha com a QTD de entregadores por semana
        
        Input: DF
        Output: Gráfico de Linha
        
    """
    # Selecionando as colunas e agrupando por semana
    cols1 = ['ID','Week_of_year']
    pedidos_semana = df1.loc[:,cols1].groupby('Week_of_year').count().reset_index()
    # Selecionando as colunas e agrupando pedidos por entregadores unicos
    cols2 = ['Delivery_person_ID','Week_of_year']
    entregadores_semana = df1.loc[:,cols2].groupby('Week_of_year').nunique().reset_index()
    # Juntando as tabelas pela função pd.merge
    novo_df = pd.merge(pedidos_semana,entregadores_semana,how='inner')
    novo_df['order_by_deliver'] = novo_df['ID'] / novo_df['Delivery_person_ID']
    # Desenhar o Grafico de linhas com a lib Polty
    fig = px.line(novo_df, x='Week_of_year', y='order_by_deliver')
                
    return fig

def localizacao_central( df1 ):
        """ Recebe um DF e plota um Mapa com a localização central por cidade e densidade de trafego
        
        Input: DF
        Output: Gráfico de Linha
        
        """
        # Colunas DF
        cols = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
        aux = df1.loc[:,cols].groupby(['City','Road_traffic_density']).median().reset_index()    
        # Criando as cores
        colors = {
         'Urban': 'pink',
         'Metropolitian': 'red',
         'Semi-Urban': 'green'}
        #Criando o Mapa
        map = folium.Map()    
        # Plotando os pontos no mapa
        for index,lat_long_info in aux.iterrows():
          folium.Marker([lat_long_info['Delivery_location_latitude'],
                        lat_long_info['Delivery_location_longitude']],
                        popup = lat_long_info[['City','Road_traffic_density']],
                        icon=folium.Icon(color=colors[lat_long_info['City']])).add_to(map)                
        folium_static(map, width = 1024, height = 600)


# ________________________________________________________INICIO DA LÓGICA DO CÓDIGO_______________________________________________________________________
# =========================================================================================================================================================
# VISÃO EMPRESA

# ------------------------------
# Importando DF
# ------------------------------
df = pd.read_csv("Repos/train.csv")

# ------------------------------
# Limpando dados do DF
# ------------------------------
df1 = limpando_df( df )
 

# =========================================================
# Barra Lateral
# =========================================================
st.header('Marketplace - Visão Empresa')

# Importando Logo na barra lateral
image_patch = 'logo.png'
image = Image.open(image_patch) #Comando para importar imagem da LIB PIL
st.sidebar.image(image, width = 200)

# Criando os primeiros elementos da barra lateral
st.sidebar.markdown('# Cury Company') # Comando sidebar cria o botão da barra lateral
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

#Criando Filtro de data na barra lateral
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Ate qual valor?',
    value = pd.datetime(2022,4,13),
    min_value = pd.datetime(2022,2,11),
    max_value = pd.datetime(2022,2,11),
    format = 'DD-MM-YYYY')
#st.header(date_slider)
st.sidebar.markdown("""___""")

# Criando filtro de tipo de trafego na barra lateral
traffict_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium','High','Jam'],
    default = ['Low', 'Medium','High','Jam'])

st.sidebar.markdown("""___""")

# Criando filtro de condição climática na barra lateral
clima_options = st.sidebar.multiselect(
    'Quais as condições climáticas',
    ['conditions Cloudy', 'conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'],
    default = ['conditions Cloudy', 'conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'])

st.sidebar.markdown("""___""")

# Criando filtro de tipo de Cidade na barra lateral
cidade_options = st.sidebar.multiselect(
    'Quais as Cidades',
    ['Metropolitian', 'Urban','Semi-Urban'],
    default = ['Metropolitian', 'Urban','Semi-Urban'])

st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Bruno Henrique')

# Linkando o  Fltro de Data 
linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas,:]


# Linkando o  Filtro de Trafego 
linhas_selecionadas = df1['Road_traffic_density'].isin(traffict_options)
df1 = df1.loc[linhas_selecionadas,:]

# Linkando o  Filtro de Clima 
linhas_selecionadas = df1['Weatherconditions'].isin(clima_options)
df1 = df1.loc[linhas_selecionadas,:]

# Linkando o  Filtro de Cidadee 
linhas_selecionadas = df1['City'].isin(cidade_options)
df1 = df1.loc[linhas_selecionadas,:]


# =========================================================
# Layout Graficos
# =========================================================
# Criando as TAB's onde vão ficar os graficos
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática', 'Visão Geográfica'])

#Manupulando a primeira TAB
with tab1:
    with st.container(): # Configurando o espaço que ficará a  primeira linha de gráfico
        st.markdown('## Pedidos por Dia')  
        fig = order_metric( df1 )
        st.plotly_chart(fig, use_container_width = True) #Comando para plotar o grafico no streamlit
        
        
    with st.container(): # Configurando o espaço que ficará a segunda linha de gráfico que terá dois graficos
        col1, col2 = st.columns(2) #Criando colunas para colocar os graficos
        
        with col1: # Configurando a primeira coluna
            st.markdown ('## Pedidos por Tráfego')
            fig = traffic_order_share( df1 )
            st.plotly_chart(fig, use_container_width = True) #Comando para plotar o grafico no streamlit

            
        with col2: # Configurando a primeira coluna
            st.markdown ('## Volume Pedidos por Cidade e por Trafego')
            fig = volume_cidade_trafego( df1 )
            st.plotly_chart(fig, use_container_width = True) # Comando para plotar o grafico no streamlit
                   
with tab2:
    with st.container(): # Configurando o espaço que ficará a segunda linha de gráfico que terá dois graficos
        col1, col2 = st.columns(2) #Criando colunas para colocar os graficos
        
        with col1: # Configurando a primeira coluna
            st.markdown('## Pedidos por Semana')
            fig = pedidos_semana( df1 )
            st.plotly_chart(fig, use_container_width = True) # Comando para plotar o grafico no streamlit

        
        with col2: # Configurando a primeira coluna
            st.markdown('## Entregadores por Semana')
            fig = entregadores_por_semana( df1 )
            st.plotly_chart(fig, use_container_width = True) # Comando para plotar o grafico no streamlit

    
with tab3:
    st.markdown('# Localização Central Cidade por Tráfego')
    with st.container(): # Configurando o espaço que ficará a terceira linha de gráfico
        localizacao_central( df1 )
     
