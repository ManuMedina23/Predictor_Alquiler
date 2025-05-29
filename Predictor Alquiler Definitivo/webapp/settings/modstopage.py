# Modificaciones css o html

#Estilo para la pagina de inicio
INICIO= """
    <style>
        h1{
            text-align: center;
            font-size: 50px;
            }    
        .stButton>button{
            color: white;    
            height: 3em;
            width: 15em;          
            }
        .stButton button:hover{
        border-color: #6D3FC0;
        color: white;
        
        }

    </style>
"""            

# Codigo para el footer personalizado
FOOTER="""
    <style>
        .footer a:link , .footer a:visited{
        color: #C09EE0;
        background-color: transparent;
        text-decoration: underline;
    }

    .footer a:hover,  .footer a:active {
        color: #6D3FC0;
        background-color: transparent;
        text-decoration: underline;
    }

    .footer p{
        color: #C09EE0;
    }

    .footer {
        position: absolute;
        left: 0;
        bottom: -20;
        margin-top: 80px;
        width: 100%;
        background-color: #0E1117;
        color: black;
        text-align: center;
    }
    </style>
    <div class="footer">
        <p>Desarrollado con ❤ por <a style='display: block; text-align: center;' href="https://www.linkedin.com/in/manuel-medina-rosa/" target="_blank">Manuel Medina Rosa</a></p>
    </div>
"""

# Permite rotar la flecha del delta de st.metric
METRIC_ARROW_ROTATE ="""
    <style>
        [data-testid="stMetricDelta"] svg {
            transform: rotate(180deg);
        }
    </style>
"""
# Permite desactivar la flecha del delta de st.metric
METRIC_ARROW_DISABLE = """
    <style>
        [data-testid="stMetricDelta"] svg {
            display: none;
        }
    </style>
"""

SLIDERBAR_COLOR="""
    <style>
    div.stSlider > div[data-baseweb = "slider"] > div > div  {
        color: white;
        background: violet;
    }
    </style>
"""    

MINMAX_COLOR = """
    <style> 
        div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {
        background: rgb(1 1 1 / 0%); 
        } 
    </style>
"""