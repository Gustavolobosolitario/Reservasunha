import streamlit as st
import pandas as pd
from datetime import datetime

# Nome do arquivo CSV para armazenar as reservas
DATABASE_FILE = "reservas.csv"

# Função para carregar as reservas
def load_reservations():
    try:
        return pd.read_csv(DATABASE_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Nome", "Email", "Motivo", "Data", "Hora"])

# Função para salvar as reservas
def save_reservation(data):
    data.to_csv(DATABASE_FILE, index=False)

# Carrega as reservas existentes
reservations = load_reservations()

# Configurações do Streamlit
st.title("Aplicativo de Agendamento")
st.sidebar.header("Menu")

# Formulário de Agendamento
st.subheader("Formulário de Agendamento")
with st.form("Agendar"):
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    motivo = st.text_area("Motivo da Reserva")
    selected_date = st.date_input("Escolha uma data:", min_value=datetime.now().date())
    available_times = ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
    selected_time = st.selectbox("Escolha um horário:", available_times)
    submit = st.form_submit_button("Reservar")

# Confirmação da Reserva
if submit:
    if not nome or not email or not motivo:
        st.warning("Por favor, preencha todos os campos.")
    else:
        if reservations[(reservations['Data'] == str(selected_date)) & (reservations['Hora'] == selected_time)].empty:
            new_reservation = pd.DataFrame({
                "Nome": [nome],
                "Email": [email],
                "Motivo": [motivo],
                "Data": [str(selected_date)],
                "Hora": [selected_time]
            })
            reservations = pd.concat([reservations, new_reservation], ignore_index=True)
            save_reservation(reservations)
            st.success("Reserva confirmada!")
        else:
            st.error("Horário já reservado. Escolha outro horário.")

# Exibir Reservas
st.subheader("Minhas Reservas")
if not reservations.empty:
    reservations_view = reservations[reservations['Data'] >= str(datetime.now().date())].sort_values(by=["Data", "Hora"])
    st.write(reservations_view)
else:
    st.info("Nenhuma reserva futura encontrada.")

# Função para contar as reservas por data
def get_reservations_by_date():
    return reservations['Data'].value_counts().to_dict()

# Preparando eventos para o calendário
reservations_count = get_reservations_by_date()
max_reservations_per_day = len(available_times)

events = []
for date, count in reservations_count.items():
    color = 'red' if count >= max_reservations_per_day else 'orange'
    events.append({
        "title": f"Reservas: {count}/{max_reservations_per_day}",
        "start": date,
        "color": color
    })

# FullCalendar Integration
st.subheader("Calendário de Agendamento Interativo")
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.0/main.min.css' rel='stylesheet' />
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.0/main.min.js'></script>
</head>
<body>
    <div id="calendar"></div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var calendarEl = document.getElementById('calendar');
            if (calendarEl) {{
                var calendar = new FullCalendar.Calendar(calendarEl, {{
                    initialView: 'dayGridMonth',
                    headerToolbar: {{
                        left: 'prev,next today',
                        center: 'title',
                        right: 'dayGridMonth,timeGridWeek,timeGridDay'
                    }},
                    selectable: true,
                    dateClick: function(info) {{
                        var selectedDate = info.dateStr;
                        var reservations = {reservations.to_dict(orient='records')};
                        var names = reservations.filter(res => res.Data === selectedDate).map(res => res.Nome);
                        if (names.length > 0) {{
                            alert('Reservas para o dia ' + selectedDate + ': ' + names.join(', '));
                        }} else {{
                            alert('Nenhuma reserva para o dia ' + selectedDate);
                        }}
                    }},
                    events: {events}
                }});
                calendar.render();
            }} else {{
                console.error('O elemento do calendário não foi encontrado.');
            }}
        }});
    </script>
</body>
</html>
"""

# Exibindo o calendário no Streamlit
st.components.v1.html(html_code, height=600)
