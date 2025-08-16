import streamlit as st
import json
from src import database_manager as db

# --- TÍTULO DE LA PÁGINA ---
st.title("📝 Nuevo Examen")

# --- LÓGICA DE PANTALLAS BASADA EN EL ESTADO DE SESIÓN ---

# Pantalla 1: CONFIGURACIÓN (Estado inicial)
if 'exam_in_progress' not in st.session_state:
    st.header("Configura tu examen")
    num_questions = st.number_input(
        "Número de preguntas:",
        min_value=5,
        max_value=50,
        value=10,
        step=5
    )

    if st.button("Empezar Examen"):
        # 1. Obtener preguntas de la BBDD
        questions_data = db.get_questions(num_questions)

        # 2. Inicializar el estado de la sesión
        st.session_state.questions = questions_data
        st.session_state.current_question_index = 0
        st.session_state.user_answers = [None] * len(questions_data)
        st.session_state.exam_in_progress = True
        st.session_state.exam_saved = False  # Flag para evitar guardado múltiple
        st.rerun()

# Pantalla 2: REALIZACIÓN DEL EXAMEN (Estado "en progreso")
elif st.session_state.exam_in_progress:
    # Comprobar si aún quedan preguntas por mostrar
    if st.session_state.current_question_index < len(st.session_state.questions):
        question = st.session_state.questions[st.session_state.current_question_index]
        q_index = st.session_state.current_question_index
        total_questions = len(st.session_state.questions)

        st.header(f"Pregunta {q_index + 1} de {total_questions}")
        st.markdown(question['enunciado'])

        # Las opciones están como string JSON, hay que parsearlas
        try:
            options_dict = json.loads(question['opciones'])
            options_list = list(options_dict.values())
        except (json.JSONDecodeError, TypeError):
            st.error("Error al procesar las opciones de la pregunta.")
            options_list = []

        # Guardar la respuesta seleccionada en el estado de sesión
        user_choice = st.radio(
            "Selecciona tu respuesta:",
            options_list,
            key=f"q_{question['id']}",
            index=None  # Por defecto no hay nada seleccionado
        )

        # Lógica de navegación
        is_last_question = (q_index + 1 == total_questions)
        button_text = "Finalizar Examen" if is_last_question else "Siguiente Pregunta"

        if st.button(button_text):
            if user_choice is not None:
                # Mapear la respuesta de texto a la clave (ej. 'a', 'b', 'c')
                selected_key = next(
                    (key for key, value in options_dict.items() if value == user_choice),
                    None
                )
                st.session_state.user_answers[q_index] = selected_key
                st.session_state.current_question_index += 1
                st.rerun()
            else:
                st.warning("Por favor, selecciona una respuesta antes de continuar.")

    # Pantalla 3: REVISIÓN DE RESULTADOS (Estado final)
    else:
        st.header("Resultados del Examen")

        # 1. Calcular resultados
        correct_answers = 0
        results_to_save = []
        questions_to_update = []

        for i, question in enumerate(st.session_state.questions):
            user_answer = st.session_state.user_answers[i]
            is_correct = (user_answer == question['respuesta_correcta'])
            if is_correct:
                correct_answers += 1

            results_to_save.append({
                'question_id': question['id'],
                'selected_option': user_answer,
                'is_correct': is_correct
            })
            questions_to_update.append({
                'id': question['id'],
                'was_correct': is_correct
            })

        # 2. Guardar el examen en la BBDD (solo si no se ha guardado antes)
        if not st.session_state.get('exam_saved', False):
            db.save_exam_flow(results=results_to_save)
            st.session_state.exam_saved = True

        # 3. Mostrar resumen
        score = (correct_answers / len(st.session_state.questions)) * 100
        st.success(f"**Puntuación final: {correct_answers} / {len(st.session_state.questions)} ({score:.2f}%)**")
        st.progress(score / 100)

        # 4. Mostrar desglose
        st.subheader("Revisión de tus respuestas")
        for i, question in enumerate(st.session_state.questions):
            user_answer_key = st.session_state.user_answers[i]
            correct_answer_key = question['respuesta_correcta']
            options_dict = json.loads(question['opciones'])

            user_answer_text = options_dict.get(user_answer_key, "No respondida")
            correct_answer_text = options_dict.get(correct_answer_key, "N/A")

            with st.container(border=True):
                st.markdown(f"**{i + 1}. {question['enunciado']}**")
                if user_answer_key == correct_answer_key:
                    st.success(f"✅ Tu respuesta: {user_answer_text}")
                else:
                    st.error(f"❌ Tu respuesta: {user_answer_text}")
                    st.info(f"ℹ️ Respuesta correcta: {correct_answer_text}")

        # 5. Botón para reiniciar
        if st.button("Realizar otro examen"):
            # Limpiar el estado para volver a la pantalla de configuración
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
