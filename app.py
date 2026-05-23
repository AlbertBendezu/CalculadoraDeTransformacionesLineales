import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

class Transformador:
    def __init__(self, figura, figuraFinal, tipoTrans):
        self.__figura = figura
        self.__figuraFinal = figuraFinal
        self.__tipoTrans = tipoTrans

    def getFigura(self):
        return self.__figura

    def setFigura(self, figura):
        self.__figura = figura

    def getFiguraFinal(self):
        return self.__figuraFinal

    def setFiguraFinal(self, fig_final):
        self.__figuraFinal = fig_final

    def getTipoTrans(self):
        return self.__tipoTrans

    def setTipoTrans(self, tipoTrans):
        self.__tipoTrans = tipoTrans

    def rotar(self, angulo, sentido):
        match sentido:
            case "Antihorario":
                ang = angulo
            case _:
                ang = -angulo

        rad = np.radians(ang)
        matriz = np.array([[np.cos(rad), -np.sin(rad)], [np.sin(rad), np.cos(rad)]])
        return self.getFiguraFinal() @ matriz.T

    def homotecia(self, k):
        puntosF = self.getFiguraFinal()

        coordK = puntosF[:-1]
        cX = np.mean(coordK[:, 0])
        cY = np.mean(coordK[:, 1])

        coordCentro = np.array([cX, cY])

        coordK2 = puntosF - coordCentro
        matriz = np.array([[k, 0], [0, k]])
        coordEscalado = coordK2 @ matriz.T

        return coordEscalado + coordCentro

    def reflejar(self, refOp):
        match refOp:
            case "Eje x":
                matriz = np.array([[1, 0], [0, -1]])
            case "Eje y":
                matriz = np.array([[-1, 0], [0, 1]])
            case "Recta y=x":
                matriz = np.array([[0, 1], [1, 0]])
            case _:
                return self.getFiguraFinal()
        return self.getFiguraFinal() @ matriz.T

st.set_page_config(page_title="Calculadora", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #06142E 0%, #0B1F3A 55%, #111827 100%);
    color: white;
}
[data-testid="stHeader"] {
    background-color: rgba(6, 20, 46, 0);
}
h1, h2, h3 {
    color: #00E5FF;
    font-weight: 800;
}
p, label, span, div {
    color: white;
}
.titulo-principal {
    background: linear-gradient(90deg, #00E5FF, #7C3AED);
    padding: 22px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0px 0px 25px rgba(0, 229, 255, 0.25);
}
.titulo-principal h1 {
    color: white;
    margin: 0;
    font-size: 38px;
}
.cabecera-seccion {
    background-color: rgba(17, 24, 39, 0.92);
    border: 1px solid #00E5FF;
    border-radius: 18px;
    box-shadow: 0px 0px 18px rgba(0, 229, 255, 0.18);
    color: white;
    font-weight: bold;
    font-size: 1.15rem;
    padding: 15px 22px;
    margin-bottom: 20px;
    text-align: center;
}
.stTextInput input {
    background-color: #0F172A;
    color: white;
    border: 1px solid #00E5FF;
    border-radius: 10px;
}
.stTextInput input:focus {
    border: 2px solid #7C3AED;
}
.stButton button {
    border-radius: 12px;
    border: 1px solid #00E5FF;
    background-color: #111827;
    color: white;
    font-weight: bold;
    height: 45px;
}
.stButton button:hover {
    background-color: #00E5FF;
    color: #06142E;
    border: 1px solid white;
}
hr {
    border: 1px solid #00E5FF;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="titulo-principal">
    <h1>Calculadora de transformaciones lineales en R²</h1>
</div>
""", unsafe_allow_html=True)

if "logica" not in st.session_state:
    st.session_state.logica = Transformador(None, None, None)
if "historial" not in st.session_state:
    st.session_state.historial = []
if "animar" not in st.session_state:
    st.session_state.animar = False
    
if "zoomEstado" not in st.session_state:
    st.session_state.zoomEstado = 0

columnaIzq, columnaDer = st.columns([1, 2])

with columnaIzq:

    st.markdown('<div class="cabecera-seccion">Elige la cantidad de puntos de tu figura</div>', unsafe_allow_html=True)
    
    puntosF = st.radio(
        label="oculto",
        options=[3, 4, 5, 6],
        horizontal=True,
        label_visibility="collapsed",
    )

    match puntosF:
        case 3:
            verticesF = ["A", "B", "C"]
        case 4:
            verticesF = ["A", "B", "C", "D"]
        case 5:
            verticesF = ["A", "B", "C", "D", "E"]
        case 6:
            verticesF = ["A", "B", "C", "D", "E", "F"]
        case _:
            verticesF = ["A", "B", "C"]

    st.write("Ingresa las coordenadas de cada punto:")
    st.info("Solo usa enteros")

    letras, puntosX, puntosY = st.columns([1, 1, 1])
    with puntosX:
        st.write("X")
    with puntosY:
        st.write("Y")

    puntosValidados = []

    for letra in verticesF:
        colLetra, colX, colY = st.columns([1, 1, 1])

        with colLetra:
            st.write(f"Punto {letra}")

        with colX:
            valX = st.text_input(label=f"x_{letra}", label_visibility="collapsed")

        with colY:
            valY = st.text_input(label=f"y_{letra}", label_visibility="collapsed")

        if valX and valY:
            try:
                numX = int(valX)
                numY = int(valY)
                puntosValidados.append([numX, numY])
            except ValueError:
                st.error("No es un numero valido")

    if len(puntosValidados) == puntosF:
        figuraCerrada = puntosValidados + [puntosValidados[0]]
        matriz = np.array(figuraCerrada)

        figura_guardada = st.session_state.logica.getFigura()
        
        if figura_guardada is None or not np.array_equal(matriz, figura_guardada):
            st.session_state.logica.setFigura(matriz)
            st.session_state.logica.setFiguraFinal(matriz)
            st.session_state.historial = [] 
            st.session_state.zoomEstado += 1 

    else:
        if st.session_state.logica.getFigura() is not None:
            st.session_state.zoomEstado += 1
            
        st.session_state.logica.setFigura(None)
        st.session_state.logica.setFiguraFinal(None)
        st.session_state.historial = []

    st.markdown('<div class="cabecera-seccion">Elige el tipo de transformación:</div>', unsafe_allow_html=True)

    transformacionesF = st.radio(
        label="oculto2",
        options=["Rotación", "Escalado", "Reflexión"],
        horizontal=True,
        label_visibility="collapsed",
    )

    anguloV = None
    sentidoV = None
    escaladoV = None
    ejeV = None

    match transformacionesF:
        case "Rotación":
            st.write("Ingrese el ángulo de rotación :")
            st.info("El angulo debe ser mayor a 0 y menor a 360 grados")

            colAng1, colAng2 = st.columns([1, 2])

            with colAng1:
                inputAngulo = st.text_input(
                    label="angulo_input", label_visibility="collapsed"
                )

            if inputAngulo:
                try:
                    numAngulo = int(inputAngulo)
                    if numAngulo <= 0 or numAngulo >= 360:
                        st.error("El angulo no esta dentro del limite")
                    else:
                        anguloV = numAngulo
                except ValueError:
                    st.error("Ingrese un angulo entero")

            sentidoV = st.radio(
                "¿En que sentido quieres que gire la figura? :",
                ["Antihorario", "Horario"],
                horizontal=True,
            )

        case "Escalado":
            st.write("Ingresa el numero al que la figura sera escalada:")
            st.info("Solo usa enteros positivos")
            colK1, colK2 = st.columns([1, 2])

            with colK1:
                inputK = st.text_input(label="k_input", label_visibility="collapsed")

            if inputK:
                try:
                    numK = int(inputK)
                    if numK <= 0:
                        st.error("No es un numero valido")
                    else:
                        escaladoV = numK
                except ValueError:
                    st.error("Solo usa enteros")

        case "Reflexión":
            st.write("Elige el eje al que se reflejara tu figura:")
            ejeV = st.radio(
                label="eje_input",
                options=["Eje x", "Eje y", "Recta y=x"],
                label_visibility="collapsed",
                horizontal=True,
            )
    
    st.write("")

    cb1, cb2, cb3 = st.columns(3)

    with cb1:
        if st.button("Deshacer ultima transformacion", use_container_width=True):
            if len(st.session_state.historial) > 0:
                estado_anterior = st.session_state.historial.pop()
                st.session_state.logica.setFiguraFinal(estado_anterior)

    with cb2:
        if st.button(
            "Aplicar transformacion", type="primary", use_container_width=True
        ):
            fig_actual = st.session_state.logica.getFiguraFinal()

            if fig_actual is not None:
                st.session_state.historial.append(fig_actual.copy())

                match transformacionesF:
                    case "Rotación":
                        if anguloV is not None:
                            nueva = st.session_state.logica.rotar(anguloV, sentidoV)
                            st.session_state.logica.setFiguraFinal(nueva)
                            st.session_state.animar = True
                    case "Escalado":
                        if escaladoV is not None:
                            nueva = st.session_state.logica.homotecia(escaladoV)
                            st.session_state.logica.setFiguraFinal(nueva)
                            st.session_state.animar = True
                    case "Reflexión":
                        if ejeV is not None:
                            nueva = st.session_state.logica.reflejar(ejeV)
                            st.session_state.logica.setFiguraFinal(nueva)
                            st.session_state.animar = True

    with cb3:
        if st.button("Reiniciar todas las transformaciones", use_container_width=True):
            st.session_state.logica.setFigura(None)
            st.session_state.logica.setFiguraFinal(None)
            st.session_state.historial = []
            st.session_state.zoomEstado += 1 
            st.rerun()

def aplicarDis(grafico):
        grafico.add_trace(go.Scatter(
            x=[-200, 200], y=[-200, 200], 
            mode="markers", marker=dict(color="rgba(0,0,0,0)"), 
            showlegend=False, hoverinfo="skip"
        ))
        
        grafico.update_layout(
            uirevision=st.session_state.zoomEstado, 
            showlegend=True,
            legend=dict(
                yanchor="top", y=0.99,
                xanchor="left", x=0.01,
                bgcolor="rgba(17, 24, 39, 0.7)", bordercolor="#00E5FF", borderwidth=1, font=dict(color="white")
            ),
            plot_bgcolor="#06142E", paper_bgcolor="#06142E", font=dict(color="white"), dragmode="pan",
            
            xaxis=dict(zeroline=True, zerolinewidth=3, zerolinecolor="#00E5FF", showgrid=True, gridcolor="#243B55", color="white", tickfont=dict(color="white")),
            yaxis=dict(zeroline=True, zerolinewidth=3, zerolinecolor="#00E5FF", showgrid=True, gridcolor="#243B55", color="white", tickfont=dict(color="white"), scaleanchor="x", scaleratio=1),
            height=700, margin=dict(l=10, r=10, t=10, b=10)
        )
        return grafico

def inAnimacion(an, fig_inicio, fig_final, fig_original, config_botones):
    frames = 10
        
    for i in range(frames + 1):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(x=fig_original[:, 0], y=fig_original[:, 1], mode="lines+markers", name="Forma inicial", line=dict(color="#8B5CF6", width=2)))
        
        figTemp = fig_inicio + (fig_final - fig_inicio) * (i / frames)
        
        if i == frames:
            nEstado = "Figura final"
        else:
            nEstado = "Transformando...."
            
        fig.add_trace(go.Scatter(x=figTemp[:, 0], y=figTemp[:, 1], mode="lines+markers", name=nEstado, line=dict(color="#FFB703", width=3)))
        
        fig = aplicarDis(fig)
        an.plotly_chart(fig, use_container_width=True, config=config_botones)
        time.sleep(0.08)

with columnaDer:

    st.markdown('<div class="cabecera-seccion">Plano Cartesiano</div>', unsafe_allow_html=True)

    animacionTotal = st.empty()

    botPlanoCarte = {
        "modeBarButtonsToRemove": [
            "lasso2d", "select2d", "autoScale2d", "resetScale2d",
            "hoverClosestCartesian", "hoverCompareCartesian",
            "toggleSpikelines", "toImage", "pan2d", "zoom2d",
        ],
        "displaylogo": False,
    }

    figOriginal = st.session_state.logica.getFigura()
    figFinal = st.session_state.logica.getFiguraFinal()

    if figOriginal is None and len(puntosValidados) > 0:
        fig = go.Figure()
        ptsArray = np.array(puntosValidados)
        fig.add_trace(go.Scatter(x=ptsArray[:, 0], y=ptsArray[:, 1], mode="markers", name="Ingresando puntos", marker=dict(color="#00E5FF", size=10)))
        fig = aplicarDis(fig)
        animacionTotal.plotly_chart(fig, use_container_width=True, config=botPlanoCarte)

    elif figFinal is not None and len(st.session_state.historial) > 0:
        if st.session_state.animar:
            figInicio = st.session_state.historial[-1] 
            inAnimacion(animacionTotal, figInicio, figFinal, figOriginal, botPlanoCarte)
            st.session_state.animar = False
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=figOriginal[:, 0], y=figOriginal[:, 1], mode="lines+markers", name="Forma inicial", line=dict(color="#8B5CF6", width=2)))
            fig.add_trace(go.Scatter(x=figFinal[:, 0], y=figFinal[:, 1], mode="lines+markers", name="Figura final", line=dict(color="#FFB703", width=3)))
            fig = aplicarDis(fig)
            animacionTotal.plotly_chart(fig, use_container_width=True, config=botPlanoCarte)

    elif figOriginal is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=figOriginal[:, 0], y=figOriginal[:, 1], mode="lines+markers", name="Forma inicial", line=dict(color="#8B5CF6", width=3)))
        fig = aplicarDis(fig)
        animacionTotal.plotly_chart(fig, use_container_width=True, config=botPlanoCarte)
        
    else:
        fig = go.Figure()
        fig = aplicarDis(fig)
        animacionTotal.plotly_chart(fig, use_container_width=True, config=botPlanoCarte)
