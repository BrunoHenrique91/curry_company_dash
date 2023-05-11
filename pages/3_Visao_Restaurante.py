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

st.set_page_config(page_title = 'Visão Restaurantes', layout = 'wide')
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

def distancia_media( df1 ):
    # Selecionando as colunas e depois usando a LIB HAVERSINE calculando a 
    # distancia entre restaurante e destino usando também LAMBDA e 
    # criando mais uma coluna chamada distance
    cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df1['distance'] = df1.loc[:,cols].apply( lambda x: 
                                            haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']),
                                            (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),
                                            axis=1)
    # Calculando a média após criar a coluna distance
    distancia_media = np.round(df1.loc[:,'distance'].mean(),2)
    col2.metric('Distancia Média', distancia_media)

def avg_std_festival( df1, festival, calc):
    """ Esta Função calcula o tempo médio e o desvio padrão das entregas considerando a interferencia ou não do Festival.
        Parâmetros:
            df1 => Dataframe com os dados necessários para o cálculo
            festival => Indicação da existencia ou não de festival (Yes ou No)
            calc => Indicação de qual operação será realizada (avg ou std)
        
        Input: 
            df1 => DataFrame
            festival => Se tem festival: Yes / Se não tem festival: No
            calc => Operador Média: avg / Desvio Padrão: std
        Output: 
            Valor caluculado
    """
    # Selecionando as Colunas do DF
    cols = ['Time_taken(min)','Festival']            
    # Calculando a média e o Desvio Padrão            
    med_std_tempo_cidade_trafego = df1.loc[:,cols].groupby(['Festival']).agg({'Time_taken(min)':['mean','std']})
    med_std_tempo_cidade_trafego.columns = ['Avg_time','Std_time']
    aux = med_std_tempo_cidade_trafego.reset_index()
    # Selecionando Condição do Festival
    linhas = aux['Festival'] == festival
    # Selecionando métrica a ser calculada (avg ou std)
    if calc == 'avg':
        aux = np.round(aux.loc[linhas,'Avg_time'],2)
    elif calc == 'std':
        aux = np.round(aux.loc[linhas,'Std_time'],2)
        
    return aux

def distancia_medio_entrega_cidade( df1 ): 
    """ Esta Função calcula a distancia média das entrega por cidade .
        Parâmetros:
            df1 => Dataframe com os dados necessários para o cálculo
        
        Input: 
            df1 => DataFrame
        Output: 
            Gráfico de Pizza
    """
    # Selecionando as colunas e depois usando a LIB HAVERSINE calculando a 
    # distancia entre restaurante e destino usando também LAMBDA e 
    # criando mais uma coluna chamada distance
    cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df1['distance'] = df1.loc[:,cols].apply( lambda x: 
                                            haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']),
                                            (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),
                                             axis=1)
    # Calculando a média e agrupando após criar a coluna distance
    distancia_media = df1.loc[:,['City','distance']].groupby('City').mean().reset_index()
    fig = go.Figure(data = [go.Pie(labels = distancia_media['City'],values = distancia_media['distance'], pull=[0,0.1,0])])
            
    return fig

def time_avg_std_cidade(df1):
    """ Esta Função calcula o tempo médio e o Desvio Padrão das entrega por cidade .
        Parâmetros:
            df1 => Dataframe com os dados necessários para o cálculo
        
        Input: 
            df1 => DataFrame
        Output: 
            Gráfico de Barras com linha de erro (std)
    """
    # Selecionando as colunas do DF e Calculando o tempo médio e Desvio Padrão agrupado por cidade
    cols = ['Order_Date','City','Time_taken(min)']
    med_std_tempo_cidade = df1.loc[:,cols].groupby(['City']).agg({'Time_taken(min)':['mean','std']})
    med_std_tempo_cidade.columns = ['Avg_time','Std_time']
    med_std_tempo_cidade = med_std_tempo_cidade.reset_index()
    # Comandos para formar o gráfico de barras com intervalos
    fig = go.Figure()
    fig.add_trace(go.Bar(name = 'Control',
                            x = med_std_tempo_cidade['City'],
                            y = med_std_tempo_cidade['Avg_time'],
                            error_y=dict(type = 'data', array = med_std_tempo_cidade['Std_time'])))
    fig_aux = fig.update_layout(barmode='group')
    
    return fig_aux

def time_avg_std_cidade_tipo_pedido( df1 ):
    """ Esta Função calcula o tempo médio e o Desvio Padrão das entrega por cidade e tipo e pedido.
        Parâmetros:
            df1 => Dataframe com os dados necessários para o cálculo
        
        Input: 
            df1 => DataFrame
        Output: 
            DataFrame com as informações calculadas
    """
    # Selecionando as Colunas do DF e Calculando o tempo médio e Desvio Padrão agrupdo por cidade e tipo de entrega
    cols = ['City','Time_taken(min)','Type_of_order']
    med_std_tempo_cidade_pedido = df1.loc[:,cols].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']})
    med_std_tempo_cidade_pedido.columns = ['Avg_time','Std_time']
    df3 = med_std_tempo_cidade_pedido.reset_index()
    st.dataframe(df3)
        
def time_avg_std_cidade_tipo_trafego( df1 ):
    """ Esta Função calcula o tempo médio e o Desvio Padrão das entrega por cidade e tipo de tráfego.
        Parâmetros:
            df1 => Dataframe com os dados necessários para o cálculo
        
        Input: 
            df1 => DataFrame
        Output: 
            Gráfico de Sunburst
    """
    # Selecionando as Colunas do DF e Calculando o tempo médio e Desvio Padrão agrupdo por cidade e tipo de trafego
    cols = ['City','Time_taken(min)','Road_traffic_density']
    med_std_tempo_cidade_trafego = df1.loc[:,cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
    med_std_tempo_cidade_trafego.columns = ['Avg_time','Std_time']
    med_std_tempo_cidade_trafego = med_std_tempo_cidade_trafego.reset_index()
    # Desenhando o gráfico de Sunbarst
    fig = px.sunburst(med_std_tempo_cidade_trafego, path=['City','Road_traffic_density'],values='Avg_time',
                        color='Std_time', color_continuous_scale='RdBu',
                        color_continuous_midpoint=np.average(med_std_tempo_cidade_trafego['Std_time']))
    return fig
# _______________________________________________________INICIO DA LÓGICA DO CÓDIGO_______________________________________________________________________
# =========================================================================================================================================================
# VISÃO RESTAURANTE

# Importando DF
df = pd.read_csv("Repos/train.csv")
df1 = limpando_df( df )

# =========================================================
# Barra Lateral
# =========================================================
st.header('Marketplace - Visão Restaurante')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_', '_'])

with tab1:
    with st.container():
        st.title('Metricas Gerais')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            # Selecionando a Coluna do DF e calculando os valores únicos
            cols = ['Delivery_person_ID']
            qts_entregadores = df1.loc[:,cols].nunique()            
            # Plotando no Dashboard
            col1.metric('Entregadores Únicos',qts_entregadores)
            
        with col2:
            distancia_media( df1 )

        with col3:
            aux = avg_std_festival( df1, festival = 'Yes', calc = 'avg')
            col3.metric('AVG_Time Festival',aux)
            
        with col4:
            aux = avg_std_festival( df1, festival = 'Yes', calc = 'std')
            col4.metric('STD_Time Festival',aux)
            
        with col5:
            aux = avg_std_festival( df1, festival = 'No', calc = 'avg')
            col5.metric('AVG_Time S/ Festival',aux)
            
        with col6:
            aux = avg_std_festival( df1, festival = 'No', calc = 'std')
            col6.metric('STD_Time S/ Festival',aux)
            
    with st.container():
        st.markdown('## Distancia média de entrega por cidade')
        fig = distancia_medio_entrega_cidade( df1 )
        st.plotly_chart(fig, use_container_width = True) # Comando para plotar o grafico no streamlit
    
    with st.container():
        st.title('Distribuição do tempo')
        col1, col2 = st.columns ( 2 )
        with col1:
            st.markdown('##### Médio e Desvio Padrão por Cidade')
            fig = time_avg_std_cidade( df1 )
            st.plotly_chart(fig, use_container_width = True) # Comando para plotar o grafico no streamlit
            
        with col2:
            st.markdown('##### Médio e Desvio Padrão por Cidade e Tipo de Pedido')
            time_avg_std_cidade_tipo_pedido( df1 )
            
    with st.container():
        st.markdown('##### Médio e Devio Padrão de entrega por cidade e tipo de tráfego')
        fig = time_avg_std_cidade_tipo_trafego( df1 )
        st.plotly_chart(fig, use_container_width = True) # Comando para plotar o grafico no streamlit
        
