#Importando bibliotecas
import pandas as pd
import re
import plotly.express as px
import plotly.graph_objects as go
import folium 
import seaborn as se
#from haversine import haversine
import streamlit as st
from PIL import Image 
from datetime import datetime
from streamlit_folium import folium_static
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title='Visão Entregadores',page_icon=':stew: ',layout='wide')
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

def distance(df1):
    df1['Distance']=(df1.loc[:,['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']]
                                    .apply (lambda x:haversine((x['Restaurant_latitude'],x['Restaurant_longitude']), 
                                                               (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1))
    distance_mean=round(df1['Distance'].mean(),2)
    return distance_mean

def time_std_delivery(df1,festival,op):
    """
    Esta função calcula o desvio padrão e o tempo médio de entrega.
    Parâmetros 
    Input:
        -df: Dataframe com dados necessario para realização do cálculo 
        -op: tipo de operação que precisa ser calculada 
                'std':Cálcula o desvio padrão da entrega 
                'mean' : Cálcula a meadia da entrega 
        -festival:tempo e desvio padrão no festival 
    Output:
        -df: Dataframe com duas conlunas uma com devio padrão e a outra com a media 
    """
    df_aux=df1.loc[:,['Festival','Time_taken(min)']].groupby(['Festival']).agg(['mean','std']).reset_index()
    linhas= df_aux['Festival'] == 'Yes'
    df_aux.columns=['Festival','mean','std']
    df_aux=round( df_aux.loc[linhas, op],2)
    return df_aux


def time_city(df1):
    df_aux=df1.loc[:,['City','Time_taken(min)']].groupby(['City']).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns=['media','desvio']
    df_aux=df_aux.reset_index()
    fig=go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['media'], error_y=dict( type='data', array=df_aux['desvio'])))
    fig.update_layout(barmode='group')
                
    return fig
def time_of_city (df1):
    cols=['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df1['Distance']=df1.loc[:,cols].apply(lambda x:
                                          haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']),
                                                     (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1)
    avg_distance=df1.loc[:,['City','Distance']].groupby('City').mean().reset_index()
    fig=go.Figure( data=[go.Pie(labels=avg_distance['City'],values= avg_distance['Distance'],pull=[0,0.1,0])])
                
    return fig

def traffic_city(df1):
    df_aux=(df1.loc[:,['City','Time_taken(min)','Road_traffic_density',]].groupby(['City','Road_traffic_density']).agg(['mean','std']).reset_index())
    df_aux.columns=['City','Road_traffic_density','mean','std']
    fig=px.sunburst(df_aux,path=['City','Road_traffic_density'], values='mean',color='std',color_continuous_scale='RdBu',color_continuous_midpoint=np.average(df_aux['std']))

    return fig

#==================================================================================================================
#                                     INICIO DA ESTRUTURA LÓGICA DO CÓDIGO
#==================================================================================================================

#-------------------------------------------------------------------
#Import dataset
#-------------------------------------------------------------------

df=pd.read_csv('train.csv')
df1=df.copy()

#----------------------------------------------------
#Limpando os dados
#----------------------------------------------------
df1=clean_code(df1)

#=================================================================
##Barra Lateral 
##================================================================
st.header('Marketplace-Visão Restaurante')


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
#===================================================================================================================
##Layout no Streamilit
##==================================================================================================================

tab1,tab2,tab3=st.tabs(['Visão Gerencial', '-', '-'])
with tab1:
    with st.container():
        
        col1,col2,col3=st.columns(3)
        with col1:
            entregadores=len(df1['Delivery_person_ID'].unique())
            col1.metric('Nº de Entregadore',entregadores)
        
        with col2:
            distance_mean= distance(df1)
            col2.metric('Distância Media',distance_mean)
      

        with col3:
            df_aux=(df1.loc[:,['Festival','Time_taken(min)']].groupby(['Festival']).mean().reset_index())
            linhas= df_aux['Festival'] == 'Yes'
            df_aux= round(df_aux.loc[linhas,'Time_taken(min)'],2)
            col3.metric('time festival',df_aux)

    with st.container(): 
        col1,col2,col3=st.columns(3)       
        
        with col1:
            df_aux =time_std_delivery(df1,'Yes','std')
            col1.metric('Desvio de tempo festival',df_aux)
            
        with col2:
            df_aux =time_std_delivery(df1,'No','mean')
            col2.metric('Tempo  medio NÃO festival',df_aux)
           
        with col3:
            df_aux =time_std_delivery(df1,'No','std')
            col3.metric('STD NÃO festival',df_aux)
    
    
    with st.container():
        col1,col2=st.columns(2)
        with col1:
            st.markdown("""---""")
            st.markdown('###### TEMPO DE ENTREGA POR CIDADE')
            
            fig=time_city(df1)
            st.plotly_chart(fig,use_container_width=True)
   
        with col2:
            st.markdown("""---""")
            st.markdown('###### TEMPO MÉDIO E DESVIO PADRÃO POR CIDADE ')
            df_aux=df1.loc[:,['City','Time_taken(min)','Type_of_order',]].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']}).reset_index()
            st.dataframe(df_aux)
            
        
        

    
    with st.container():
        st.markdown("""---""")
        col1,col2=st.columns(2)
        with col1:
            st.markdown('###### TEMPO MEDIO POR CIDADE')
            fig=time_of_city(df1)
            st.plotly_chart(fig,use_container_width=True)
        
        with col2:
            st.markdown('###### TEMPO MEDIO POR CIDADE E TIPO DE TRÂNSITO')
            fig=traffic_city(df1)
            st.plotly_chart(fig,use_container_width=True)
        
        
   
            





