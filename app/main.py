import streamlit as st
import requests

# Configuracion de la pagina principal
st.set_page_config(page_title="Prediccion de Diabetes", layout="centered")

# Direccion de la API externa
API_URL = "https://diabetes-fast-api-q5dk.onrender.com/"

# Titulo y descripcion del programa
st.title("Asistente de Prediccion de Diabetes")
st.write("Esta aplicacion utiliza un modelo de inteligencia artificial para ayudar a predecir la posibilidad de tener diabetes basandose en datos de salud.")

# Funcion para revisar si la API esta funcionando y obtener la exactitud
def obtener_info_sistema():
    try:
        respuesta = requests.get(f"{API_URL}api/health", timeout=5)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            # Extraemos la exactitud de la nueva estructura: model_metrics -> best_accuracy
            metricas = datos.get("model_metrics", {})
            exactitud_valor = metricas.get("best_accuracy")
            
            if exactitud_valor is not None:
                # Formateamos como porcentaje (ej: 75.32%)
                exactitud_texto = f"{exactitud_valor * 100:.2f}%"
            else:
                exactitud_texto = "No disponible"
                
            return True, exactitud_texto
    except:
        return False, None
    return False, None

# Mostrar el estado de la conexion y la exactitud al inicio
estado_api, exactitud = obtener_info_sistema()

if estado_api:
    st.success(f"Conexion establecida. Exactitud del modelo: {exactitud}")
else:
    st.error("No se pudo conectar con el sistema de prediccion. Por favor, intente mas tarde.")

# Formulario para ingresar los datos del paciente
st.subheader("Datos del Paciente")

with st.form("formulario_diabetes"):
    # Dividimos la pantalla en dos columnas para que sea mas facil de ver
    col1, col2 = st.columns(2)
    
    with col1:
        pregnancies = st.number_input("Número de Embarazos", min_value=0, max_value=20, value=0, step=1, 
                                     help="Indica cuántas veces ha estado embarazada la persona.")
        glucose = st.number_input("Nivel de Glucosa en sangre", min_value=0, max_value=300, value=100,
                                  help="Es la cantidad de azúcar que tienes en la sangre.")
        blood_pressure = st.number_input("Presión Arterial (mmHg)", min_value=0, max_value=200, value=80,
                                         help="Es la fuerza con la que el corazón bombea la sangre cuando descansa.")
        skin_thickness = st.number_input("Grosor del pliegue cutáneo (mm)", min_value=0, max_value=100, value=20,
                                         help="Se mide en el brazo y sirve para estimar la grasa del cuerpo.")
    
    with col2:
        insulin = st.number_input("Nivel de Insulina (mu U/ml)", min_value=0, max_value=1000, value=80,
                                  help="Es una hormona que ayuda a que el azúcar de los alimentos entre a las células.")
        bmi = st.number_input("Indice de Masa Corporal (IMC)", min_value=0.0, max_value=70.0, value=25.0, format="%.1f",
                              help="Es un cálculo que se hace usando tu peso y tu altura.")
        diabetes_pedigree = st.number_input("Función de Pedigrí de Diabetes", min_value=0.0, max_value=3.0, value=0.5, format="%.3f",
                                            help="Es un puntaje que toma en cuenta si tienes familiares con diabetes.")
        age = st.number_input("Edad (años)", min_value=0, max_value=120, value=30, step=1,
                              help="La edad actual de la persona.")

    # Boton para enviar los datos
    boton_predecir = st.form_submit_button("Realizar Prediccion")

# Logica que ocurre cuando se presiona el boton
if boton_predecir:
    # Preparamos los datos en el formato que la API espera (un diccionario)
    datos_para_enviar = {
        "pregnancies": pregnancies,
        "glucose": glucose,
        "blood_pressure": blood_pressure,
        "skin_thickness": skin_thickness,
        "insulin": insulin,
        "bmi": bmi,
        "diabetes_pedigree_function": diabetes_pedigree,
        "age": age
    }
    
    # Mostramos un mensaje de espera mientras recibimos la respuesta
    with st.spinner("Procesando los datos..."):
        try:
            # Enviamos los datos a la API mediante un metodo POST
            respuesta_post = requests.post(f"{API_URL}api/predict", json=datos_para_enviar, timeout=10)
            
            if respuesta_post.status_code == 200:
                resultado = respuesta_post.json()
                print(resultado)
                prediccion = resultado.get("prediccion")
                mensaje = resultado.get("mensaje", "No se recibio un mensaje especifico")
                
                # Mostramos el resultado de forma visual
                st.subheader("Resultado de la Prediccion")
                if prediccion == 1:
                    st.warning(f"Resultado: {mensaje}. Se recomienda consultar con un especialista.")
                else:
                    st.success(f"Resultado: {mensaje}. Los indicadores parecen estar en rangos normales.")
            else:
                st.error(f"Hubo un problema con la respuesta del servidor (Error {respuesta_post.status_code})")
        
        except Exception as error:
            st.error(f"Error al intentar comunicarse con el sistema: {str(error)}")

st.info("Nota: Esta herramienta es informativa y no sustituye un diagnostico medico profesional.")