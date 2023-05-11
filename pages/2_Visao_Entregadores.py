# Importando Libs

import plotly.express as px
import folium
from haversine import haversine
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title = 'Visão Enregadores', layout = 'wide')
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

def avg_std_transito( df1 ):
    """Recebe um DF e calcula a média e o Desvio Padrão das Avaliações das Entregas por tipo de Tranito
            
        Input: DF
        Output: DF com AVG e STD
        
    """
    # Selecionando as Colunas do DF, agrupando e tirando a média e DP
    cols = ['Delivery_person_Ratings', 'Road_traffic_density']
    med_std_trafego = df1.loc[:,cols].groupby(['Road_traffic_density']).agg({'Delivery_person_Ratings':['mean','std']})
    med_std_trafego.columns = ['delivery_mean','delivery_std']
    st.dataframe(med_std_trafego.reset_index())

def avg_std_clima( df1 ):
    """Recebe um DF e calcula a média e o Desvio Padrão das Avaliações das Entregas pelo clima
            
        Input: DF
        Output: DF com AVG e STD
        
    """
    # Selecionando as Colunas do DF, agrupando e tirando a média e DP
    cols = ['Delivery_person_Ratings', 'Weatherconditions']
    med_std_trafego = df1.loc[:,cols].groupby(['Weatherconditions']).agg({'Delivery_person_Ratings':['mean','std']})
    med_std_trafego.columns = ['condition_mean','condition_std']
    st.dataframe(med_std_trafego.reset_index())
    
def top_entregadores( df1, top_asc ):
    """Recebe um DF e calcula o Top 10 por cidade dos entregadores mais rápidos ou mais lentos conforme seleção do usuário
        
        Parâmetros:
        df1 = Dataframe para manipulação
        top_asc = Seleciona se é o Top mais rápido (True) ou Top mais lento (False)
        
        Input: DF
        Output: DF com top 10 por cidade com tempo médio de entrega
        
    """
    # Selecionando as colunas do DF, agrupando e ordenando
    cols = ['Delivery_person_ID','Time_taken(min)','City']
    df2 = df1.loc[:,cols].groupby(['City','Delivery_person_ID']).mean().sort_values(['City','Time_taken(min)'], ascending = top_asc).reset_index()
    # Selecionando os 10 mais de cada cidade
    df2_aux01 = df2.loc[df2['City'] == 'Metropolitian',:].head(10)
    df2_aux02 = df2.loc[df2['City'] == 'Urban',:].head(10)
    df2_aux03 = df2.loc[df2['City'] == 'Semi-Urban',:].head(10)
    # Concatenando os resultados
    df3 = pd.concat( [df2_aux01, df2_aux02, df2_aux03] ).reset_index(drop = True)
    st.dataframe(df3)
    
# _______________________________________________________INICIO DA LÓGICA DO CÓDIGO_______________________________________________________________________
# =========================================================================================================================================================

# VISÃO ENTREGADORES

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
st.header('Marketplace - Visão Entregadores')

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
        st.title('Métricas Gerais')
        col1, col2, col3, col4 = st.columns(4, gap= 'large')
        with col1:
            # Selecionando as colunas do DF
            cols = ['Delivery_person_Age']
            
            # Maior Idade
            idade_max = df1.loc[:,cols].max()
            col1.metric('Maior Idade',idade_max)

        with col2:
            # Maior Idade
            idade_min = df1.loc[:,cols].min()
            col2.metric('Menor Idade',idade_min)

        with col3:
            # Selecionando as colunas do DF
            cols = ['Vehicle_condition']
            
            # Melhor Condição
            condicao_max = df1.loc[:,cols].max()
            col3.metric('Melhor Condição',condicao_max)
            
        with col4:
            # Pior Condição
            condicao_min = df1.loc[:,cols].min()
            col4.metric('Pior Condição',condicao_min)
            
    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### Avaliação média por Entregador')
            
            # Selecionando as Colunas do DF, agrupando e tirando a média
            cols = ['Delivery_person_ID','Delivery_person_Ratings']
            med_entregador = df1.loc[:,cols].groupby(['Delivery_person_ID']).mean().reset_index()
            st.dataframe(med_entregador)
            
        with col2:
            st.markdown('###### Avaliação Média e Desvio Padrão por transito')
            avg_std_transito( df1 )            
            st.markdown('###### Avaliação Média e Desvio Padrão por Clima ')
            avg_std_clima( df1 )

    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### Top Entregadores mais rápidos por cidade')
            top_entregadores( df1, top_asc = True )
            
        with col2:
            st.markdown('###### Top Entregadores mais Lentos por cidade')
            top_entregadores( df1, top_asc = False )
