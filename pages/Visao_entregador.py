
#Importando bibliotecas
import pandas as pd
import re
import plotly.express as px
import plotly.graph_objects as go
import folium 
import seaborn as se
from haversine import haversine
import streamlit as st
from PIL import Image 
from datetime import datetime
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores',page_icon=':motor_scooter:',layout='wide')
#===================================================================================================================
#           FUNÇÕES
#===================================================================================================================
def clean_code(df1):
    """ Esta função tem como finalidade fazer a limpeza do dataframe
        TIPOS DE LIMPEZA:
        
        1. Remoção dos dados NaN
        2. Limpeza de espaço da variaveis de str
        3. Mudandça do tipo da coluna de dados (int, flot , str)
        4. Formatação da data
        5. Limpeza da coluna de tempo (retirando o texto min)
        
        Input:Dataframe
        Output:Dataframe
    """
    #limpando o DataFreme 
    df1.loc[:,'ID']=df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Delivery_person_ID']=df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:,'Road_traffic_density']=df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order']=df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle']=df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'Festival']=df1.loc[:,'Festival'].str.strip()
    df1.loc[:,'City']=df1.loc[:,'City'].str.strip()

    #Tirando os 'NaN' para transformar em numeros
    linhas_vazias= df1['Delivery_person_Age'] != 'NaN '
    df1=df1.loc[linhas_vazias,:]

    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1=df1.loc[linhas_vazias, :]

    linhas_vazias = df1['City'] != 'NaN '
    df1=df1.loc[linhas_vazias, :]

    linhas_vazias = df1['Festival'] != 'NaN '
    df1=df1.loc[linhas_vazias, :]

    linhas_vazias = df1['City'] != 'NaN'
    df1=df1.loc[linhas_vazias, :]

    linhas_vazias = df1['Road_traffic_density'] != 'NaN'
    df1=df1.loc[linhas_vazias, :]

    linhas_vazias = df1['Festival'] != 'NaN'
    df1=df1.loc[linhas_vazias, :]

    #transformando colunas em numeros inteiros 
    df1['Delivery_person_Age']=(df1['Delivery_person_Age']).astype(int)
    df1['Delivery_person_Ratings']=(df1['Delivery_person_Ratings']).astype(float)
    df1['multiple_deliveries']=(df1['multiple_deliveries']).astype(int)

    #transformando o Formato da Data
    df1['Order_Date']= pd.to_datetime(df1 ['Order_Date'], format='%d-%m-%Y')

    #Tirando o nome min da coluna 

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split( '(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1


def top_delivers (df1):
    df2=(df1.loc[:,['Delivery_person_ID','Time_taken(min)','City']]
            .groupby(['City','Time_taken(min)'])
            .min()
            .sort_values(['City','Time_taken(min)'], ascending= True)
            .reset_index())
            
    df1_aux1=df2.loc[df2['City']=='Metropolitian',:].head(10)
    df1_aux2=df2.loc[df2['City']=='Urban',:].head(10)
    df1_aux3=df2.loc[df2['City']=='Semi-Urban',:].head(10)
    df3=pd.concat( [df1_aux1, df1_aux2, df1_aux3] )
        
    return df3

def slowe_dalivery(df1):
    df2=(df1.loc[:,['Delivery_person_ID','Time_taken(min)','City']]
            .groupby(['City','Time_taken(min)'])
            .min().sort_values(['City','Time_taken(min)'], ascending= False)
            .reset_index())
    df1_aux1=df2.loc[df2['City']=='Metropolitian',:].head(10)
    df1_aux2=df2.loc[df2['City']=='Urban',:].head(10)
    df1_aux3=df2.loc[df2['City']=='Semi-Urban',:].head(10)
            
    df3=pd.concat( [df1_aux1, df1_aux2, df1_aux3] )
            
    return (df3)
    


#==================================================================================================================
#                                     INICIO DA ESTRUTURA LÓGICA DO CÓDIGO
#==================================================================================================================

#Abrir  arquivo no JupterLab
df=pd.read_csv('train.csv')
df1=df.copy()

df1=clean_code(df1)


#===================================================================================================================
##Barra Lateral 
##==================================================================================================================
st.header('Marketplace- Visão Entregadores')


image_path='curry.jpeg'
image=Image.open(image_path)
st.sidebar.image(image, width=130)

#criando a barra lateral
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Tow')
st.sidebar.markdown("""____""")

#Colocando o Filtro na barra lateral 
st.sidebar.markdown('### Selecione uma data limite')

date_slider=st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

#filtro para Round Traffic densit

traffic_options=st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low', 'Medium','High','Jam'],
    default=['Low', 'Medium','High','Jam'])

st.sidebar.markdown("""---""")
#filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1=df1.loc[linhas_selecionadas,:]

#Filtro de tipo de tráfego 
linhas_selecionadas=df1['Road_traffic_density'].isin(traffic_options)
df1=df1.loc[linhas_selecionadas,:] 
#=================================================================
##Layout no Streamilit
##================================================================

tab1,tab2,tab3 =st.tabs(['Visão Gerencial','-','-' ])

with tab1:
#criando o primeiro container sobre as metricas 
    with st.container():
        st.title('Métricas Gerais')
        col1,col2,col3,col4=st.columns(4)
        
        with col1:
            #Maior idade dos entregadores
            maior = df1['Delivery_person_Age'].max()
            col1.metric('Maior IDADE ',maior)
            
        with col2:
            #Menor idade dos entregadores
            menor=df1['Delivery_person_Age'].min()
            col2.metric('MENOR IDADE',menor)
       
        with col3:
            #melhor condição do veiculo 
            best_condition=df1['Vehicle_condition'].max()
            col3.metric('Veículo Melhores',best_condition)
       
        
        with col4: 
            #pior condição do veiculo 
            worst_condition= df1['Vehicle_condition'].min()
            col4.metric('Veículos Piores',worst_condition)

#criando o segundo container 
    with st.container():
        st.markdown("""-----""")
            
        col1,col2=st.columns(2)
        with col1:
            #Avaliação média de entregadores 
            st.subheader('Avaliação Media de Entregadores')
            
            df_agv_ratings=(df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                               .groupby('Delivery_person_ID')
                               .mean()
                               .reset_index())
            st.dataframe(df_agv_ratings)

           
          
        with col2:
            with st.container():
                #avaliação média por tipo de transito 
                st.subheader('Avaliação por tipo de Trânsito')
                ranting_transit=(df1.loc[:,['Road_traffic_density','Delivery_person_Ratings']]
                                    .groupby('Road_traffic_density')
                                    .agg([ 'mean' , 'std' ])
                                    .reset_index())
                st.dataframe(ranting_transit)
                
                
            with st.container():
                #avaliação por condições climaticas
                st.markdown("""---""")
                st.subheader('Médiae STD por condições Climáticas')
                climatic_conditions=(df1.loc[:,['Road_traffic_density','Delivery_person_Ratings']]
                                        .groupby('Road_traffic_density')
                                        .agg([ 'mean' , 'std' ])
                                        .reset_index()) 
                st.dataframe(climatic_conditions)

#criando o terceiro container 
    with st.container():
        st.markdown("""---""")
        #Avaliações por entregadores por cidade
        st.subheader('VELOCIDADE DE ENTREGA POR CIDADE')
        col1,col2=st.columns(2)
       
        
        with col1:
            #entregadores mais rapidos 
            st.subheader('Entrega mais rápida')
            df3=top_delivers(df1)
            st.dataframe(df3)
 
        with col2:
            st.subheader('Entrega mais lenta')
            df3=slowe_dalivery(df1)
            st.dataframe(df3)
   
