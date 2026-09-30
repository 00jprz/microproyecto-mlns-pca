import streamlit as st
import matplotlib.pyplot as plt

from src.PaletteController import PaletteController


st.set_page_config(
    layout="wide",
    page_title="Generador de paletas de color",
    page_icon="🎨",
)


@st.cache_resource
def load_controller():
    return PaletteController()


try:
    ctrl = load_controller()
except Exception as exc:
    st.error(f"No fue posible cargar los modelos: {exc}")
    st.stop()

with st.container(border=True):
    controls_column, image_column = st.columns(2, gap="large")

    with controls_column:
        st.title("Generador de paletas de color")
        st.write("Carga una imagen y obtén sus colores dominantes con el modelo seleccionado.")
        style = st.selectbox("Estilo del modelo", ctrl.get_styles())
        model_name = st.selectbox("Obra de referencia", ctrl.get_model_names(style))
        generate_clicked = st.button("Generar paleta", type="primary")

    with image_column:
        uploaded_image = st.file_uploader(
            "Imagen",
            type=["png", "jpg", "jpeg", "webp"],
        )
        if uploaded_image is not None:
            st.image(uploaded_image, caption="Imagen cargada", width="stretch")

    if generate_clicked and uploaded_image is None:
        st.error("Carga una imagen para generar la paleta.")

if generate_clicked and uploaded_image is not None:
    try:
        result = ctrl.generate_palette(uploaded_image.getvalue(), style, model_name)
    except ValueError as exc:
        st.error(str(exc))
    else:
        with st.container(border=True):
            st.subheader("Distribución de colores")

            figure, axis = plt.subplots(figsize=(10, 1.5))
            offset = 0.0
            for color in result["colors"]:
                proportion = color["proporcion"]
                axis.barh(0, proportion, left=offset, color=color["HEX"], height=0.55)
                if proportion >= 0.1:
                    luminance = (
                        0.299 * color["R"] + 0.587 * color["G"] + 0.114 * color["B"]
                    )
                    text_color = "black" if luminance > 150 else "white"
                    axis.text(
                        offset + proportion / 2,
                        0,
                        f"{proportion:.0%}",
                        ha="center",
                        va="center",
                        color=text_color,
                    )
                offset += proportion
            axis.set_xlim(0, 1)
            axis.set_yticks([])
            axis.set_xticks([0, 0.25, 0.5, 0.75, 1], labels=["0%", "25%", "50%", "75%", "100%"])
            axis.set_xlabel("Proporción de píxeles")
            for spine in axis.spines.values():
                spine.set_visible(False)
            figure.tight_layout()
            st.pyplot(figure, use_container_width=True)
            plt.close(figure)

            swatch_columns = st.columns(len(result["colors"]))
            for column, color in zip(swatch_columns, result["colors"]):
                column.markdown(
                    f"<div style='height:48px;background:{color['HEX']};border:1px solid #888'></div>",
                    unsafe_allow_html=True,
                )
                column.caption(f"{color['HEX']} · {color['proporcion']:.1%}")

            st.dataframe(
                [
                    {
                        "Color": color["HEX"],
                        "Rojo": color["R"],
                        "Verde": color["G"],
                        "Azul": color["B"],
                        "Proporción": f"{color['proporcion']:.1%}",
                    }
                    for color in result["colors"]
                ],
                hide_index=True,
                use_container_width=True,
            )

st.caption(f"""
    <div style="
        background-color: #E3F2FD;
        color: #243746;
        text-align: center;
        padding: 16px;
        border-radius: 10px;
        line-height: 1.8;
    ">
        <em>JAVIER PEREZ OSORIO</em><br>
        <em>Generador de paletas de color</em><br>
        <em>Universidad de los Andes -</em>
        Microproyecto de Inteligencia Artificial
    </div>
    """,
    unsafe_allow_html=True)
