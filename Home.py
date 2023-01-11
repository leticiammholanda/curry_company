import streamlit as st
from PIL import Image 

st.set_page_config(
    page_title="Home",
    page_icon=":bar_chart:"
)

#image_path='/home/leticia/Documentos/FTC/ExerciciojupterLab/'
image= Image.open( 'curry.jpeg') 
st.sidebar.image (image,width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Tow')
st.sidebar.markdown("""____""")

st.write("# Curry Company Growth Dashbord")
         
st.markdown(
    """
    Growth Dashbord foi construido para acompanhar as métricas de crecimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Metricas gerais de comportamento.
        -Visão tática: Indicadores semais de crescimento.
        Visão Geográfica: Insights de geolocalização.
   
   -Visão Entregador
        -Acompanhamento dos indicadores semanais de crescimento.
    
    -Visão Restaurante
        -Indicadores semanis de crescimento dos restaurantes
        
    ### Ask for Help 
        -Time de Data Science no Discord 
        -@Letícia Holanda#2926
    """)