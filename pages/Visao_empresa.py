#Libraries 
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


st.set_page_config(page_title='Visão Empresa',page_icon=':chart_with_downwards_trend:',layout='wide')
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


        
def order_metric(df1):
    #Order Metric
    #criando grafico de numero pedidos por dia 
    df_aux = df1[['ID','Order_Date']].groupby('Order_Date').count().reset_index()
    #fazendo o grafico de Linhas no streamlit uso a função st.ploty_chart()
    fig=px.bar(df_aux, x='Order_Date', y= 'ID')
         
    return fig


def traffic_order_share(df1):
    #Pedidos por tipo de trafico                
    df_aux= df1.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    
    #crio uma nova coluna para calcular a porcentagem para colocar no grafico 
    df_aux['porcent_de_deliveries']= 100 *(df_aux['ID']/ df_aux['ID'].sum())
    #criando graico de pizza
    fig=px.pie(df_aux, values='porcent_de_deliveries', names= 'Road_traffic_density')
    st.plotly_chart(fig,use_container_width=True) 
                
    return fig

def traffic_order_city(df1):
    df_aux= df1.loc[:,['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
                
    df_aux['percent_ID']=100* (df_aux['ID']/df_aux['ID'].sum())

    # gráfico
    fig=px.scatter(df_aux,x='City',y='Road_traffic_density',size='ID', color='City' )
                
    return fig
def order_by_week(df1):
    df1['semana']=df1['Order_Date'].dt.strftime("%U")
    df_aux= df1.loc[:,['semana','ID']].groupby('semana').count().reset_index()
    #criando o grafico de linha 
    fig=px.line(df_aux, x='semana', y='ID')
            
    return fig

def order_delivery(df1):
    df_aux1= df1.loc[:,['ID', 'semana']].groupby('semana').count().reset_index()
    df_aux2= df1.loc[:,['Delivery_person_ID', 'semana']].groupby(['semana']).nunique().reset_index()
    df_aux= pd.merge( df_aux1, df_aux2, how='inner')
    df_aux['order_by_delivery']=df_aux['ID']/df_aux['Delivery_person_ID']
    fig=px.line( df_aux, x='semana', y='order_by_delivery' )

    return fig
def country_maps(df1):
    data_plot = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()    

    # Desenhar o mapa
    map = folium.Map( zoom_start=11 )
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],  location_info['Delivery_location_longitude']],  popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
        folium_static( map, width=1024,height=600)

           
            




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
st.header('Marketplace- Visão Cliente')


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

#criando as abas para navegação 
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica' ])

#criando os ambientes da tab 

with tab1:
    with st.container():
        #Order Metric       
        st.markdown('### NÚMERO DE PEDIDOS POR DIA')
        fig = order_metric(df1)
        st.plotly_chart(fig, user_container_width=True)
   
    
    #criando graficos de pizzas em duas colunas 
    with st.container():
        col1, col2 =st.columns(2)
        with col1:
            fig= traffic_order_share(df1)
            st.markdown('#### QUANTIDADE DE PEDIDOS POR TRÁFEGO ')
            st.plotly_chart(fig,use_container_width=True)
            
 
        with col2:
            st.markdown('### TRÁFEGO POR CIDADE')
            fig=traffic_order_city(df1)
            st.plotly_chart(fig,use_container_width=True)

with tab2:
    with st.container():
        st.markdown('#### QUANTIDADE DE PEDIDOS POR SEMANA')
        fig=order_by_week(df1)
        st.plotly_chart(fig,use_container_width=True)

       
    with st.container():
        st.markdown('### PEDIDOS POR SEMANA')
        fig= order_delivery(df1)
        st.plotly_chart(fig,use_container_width=True)
    
with tab3:
    st.markdown('### MAPA DAS ENTREGAS')
    country_maps(df1)
    
