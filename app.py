import os
import base64
import streamlit as st
import openai
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas


st.set_page_config(
    page_title="🧠 Tablero Inteligente",
    page_icon="🎨",
    layout="centered"
)


st.title("🧠 Tablero Inteligente")
st.markdown("""
Este experimento demuestra la capacidad de una IA para **interpretar un boceto hecho a mano**.  
Dibuja algo, presiona **“Analizar la imagen”**, y observa cómo el modelo lo describe. ✨
""")


with st.sidebar:
    st.header("💡 Acerca de esta app")
    st.markdown("""
    Esta aplicación utiliza el modelo **GPT-4o-mini con visión**,  
    capaz de **entender imágenes** y generar descripciones textuales.

    ---
    **Instrucciones:**
    1. 🖊️ Dibuja tu boceto en el lienzo.
    2. 🔑 Ingresa tu clave de API de OpenAI.
    3. 🤖 Haz clic en “Analizar la imagen”.

    ---
    **Consejos:**
    - Usa trazos claros y simples.
    - Dibuja formas o conceptos reconocibles.
    """)
    st.markdown("---")
    st.caption("Hecho con ❤️ usando Streamlit y OpenAI")


def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return None


st.subheader("🎨 Dibuja tu boceto")
st.markdown("Usa el panel de abajo para hacer un dibujo simple. Puedes ajustar el grosor del trazo en el menú lateral.")

stroke_width = st.sidebar.slider("✏️ Grosor del trazo", 1, 30, 5)
stroke_color = "#000000"
bg_color = "#FFFFFF"

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)


ke = st.text_input("🔑 Ingresa tu clave de OpenAI:", type="password")
if ke:
    os.environ["OPENAI_API_KEY"] = ke
    openai.api_key = ke
else:
    st.info("Por favor ingresa tu clave de API antes de continuar.")


analyze_button = st.button("🔍 Analizar la imagen", type="primary")

if canvas_result.image_data is not None and ke and analyze_button:
    with st.spinner("Analizando tu dibujo... 🧩"):
        # Convertir la imagen del lienzo
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype("uint8"), "RGBA")
        input_image.save("img.png")

        base64_image = encode_image_to_base64("img.png")
        if not base64_image:
            st.error("❌ No se pudo procesar la imagen. Intenta dibujar de nuevo.")
        else:
            prompt_text = "Describe brevemente en español lo que ves en la imagen."

            try:
                # Llamada a la API de OpenAI (visión)
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                                },
                            ],
                        }
                    ],
                    max_tokens=500,
                )

                # Mostrar respuesta
                if response.choices and response.choices[0].message.content:
                    description = response.choices[0].message.content
                    st.success("### 🧠 Descripción generada:")
                    st.write(description)
                else:
                    st.warning("No se pudo obtener una descripción. Intenta nuevamente.")

            except Exception as e:
                st.error(f"❌ Ocurrió un error al analizar la imagen: {e}")

elif analyze_button and not ke:
    st.warning("⚠️ Ingresa tu clave de API antes de analizar.")
elif analyze_button and canvas_result.image_data is None:
    st.warning("⚠️ Dibuja algo antes de presionar el botón.")


st.markdown("---")
st.caption("Desarrollado por OpenAI + Streamlit | Ejemplo educativo de IA visual")

