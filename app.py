import streamlit as st
import numpy as np
import plotly.graph_objects as go


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
st.title("Calculadora de transformaciones lineales en R²", anchor=False)
st.divider()
if "logica" not in st.session_state:
    st.session_state.logica = Transformador(None, None, None)
if "historial" not in st.session_state:
    st.session_state.historial = []

columnaIzq, columnaDer = st.columns([1, 2])

with columnaIzq:

    st.subheader("Elige la cantidad de puntos de tu figura", anchor=False)
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

        if len(st.session_state.historial) == 0:
            st.session_state.logica.setFigura(matriz)
            st.session_state.logica.setFiguraFinal(matriz)
    else:
        if len(st.session_state.historial) == 0:
            st.session_state.logica.setFigura(None)
            st.session_state.logica.setFiguraFinal(None)

    st.divider()
    st.subheader("Elige el tipo de transformación:", anchor=False)

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
            st.info("El angulo debe estar entre 0 y 360 grados")

            colAng1, colAng2 = st.columns([1, 2])

            with colAng1:
                inputAngulo = st.text_input(
                    label="angulo_input", label_visibility="collapsed"
                )

            if inputAngulo:
                try:
                    numAngulo = int(inputAngulo)
                    if numAngulo < 0 or numAngulo > 360:
                        st.error("No esta dentro del limite")
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
                    case "Escalado":
                        if escaladoV is not None:
                            nueva = st.session_state.logica.homotecia(escaladoV)
                            st.session_state.logica.setFiguraFinal(nueva)
                    case "Reflexión":
                        if ejeV is not None:
                            nueva = st.session_state.logica.reflejar(ejeV)
                            st.session_state.logica.setFiguraFinal(nueva)

    with cb3:
        if st.button("Reiniciar todas las transformaciones", use_container_width=True):
            st.session_state.logica.setFigura(None)
            st.session_state.logica.setFiguraFinal(None)
            st.session_state.historial = []
            st.rerun()

with columnaDer:
    fig = go.Figure()

    figOriginal = st.session_state.logica.getFigura()
    figFinal = st.session_state.logica.getFiguraFinal()

    if figOriginal is None and len(puntosValidados) > 0:
        ptsArray = np.array(puntosValidados)
        fig.add_trace(
            go.Scatter(
                x=ptsArray[:, 0],
                y=ptsArray[:, 1],
                mode="markers",
                name="puntosss",
                marker=dict(color="blue", size=10),
            )
        )

    if figOriginal is not None:
        fig.add_trace(
            go.Scatter(
                x=figOriginal[:, 0],
                y=figOriginal[:, 1],
                mode="lines+markers",
                name="forma inicial",
                line=dict(color="blue", width=2),
            )
        )

    if figFinal is not None and len(st.session_state.historial) > 0:
        fig.add_trace(
            go.Scatter(
                x=figFinal[:, 0],
                y=figFinal[:, 1],
                mode="lines+markers",
                name="figura resultado",
                line=dict(color="orange", width=3),
            )
        )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        dragmode="pan",
        xaxis=dict(
            range=[-200, 200],
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="black",
            showgrid=True,
            gridcolor="#d4d4d4",
            color="black",
            tickfont=dict(color="black"),
        ),
        yaxis=dict(
            range=[-200, 200],
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="black",
            showgrid=True,
            gridcolor="#d4d4d4",
            color="black",
            tickfont=dict(color="black"),
            scaleanchor="x",
            scaleratio=1,
        ),
        height=700,
        margin=dict(l=10, r=10, t=10, b=10),
    )

    botPlanoCarte = {
        "modeBarButtonsToRemove": [
            "lasso2d",
            "select2d",
            "autoScale2d",
            "resetScale2d",
            "hoverClosestCartesian",
            "hoverCompareCartesian",
            "toggleSpikelines",
            "toImage",
            "pan2d",
            "zoom2d",
        ],
        "displaylogo": False,
    }

    st.plotly_chart(fig, use_container_width=True, config=botPlanoCarte)
