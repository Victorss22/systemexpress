import PySimpleGUI as sg
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import sqlite3

sg.theme('DarkAmber')  # Definindo o tema escuro


conn = sqlite3.connect('clientes.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT,
        ultima_consulta TEXT
    )
''')
conn.commit()

def cadastrar_cliente(nome, email):
    if nome and email:
        cursor.execute('INSERT INTO clientes (nome, email) VALUES (?, ?)', (nome, email))
        conn.commit()
        sg.popup(f"Cliente {nome} cadastrado com sucesso!")
    else:
        sg.popup_error("Preencha todos os campos.")

def obter_clientes():
    cursor.execute('SELECT nome, email, ultima_consulta FROM clientes ORDER BY nome')
    return cursor.fetchall()

def atualizar_ultima_consulta(nome, data_consulta):
    cursor.execute('UPDATE clientes SET ultima_consulta = ? WHERE nome = ?', (data_consulta, nome))
    conn.commit()

def excluir_cliente(nome):
    cursor.execute('DELETE FROM clientes WHERE nome = ?', (nome,))
    conn.commit()

def enviar_email(destinatario, assunto, mensagem):
    remetente_email = 'laboratorioninjatecnologia@gmail.com'
    remetente_senha = 'uznvduocvuvxtsca'

    msg = MIMEText(mensagem)
    msg['Subject'] = assunto
    msg['From'] = remetente_email
    msg['To'] = destinatario

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(remetente_email, remetente_senha)
        server.sendmail(remetente_email, destinatario, msg.as_string())

def marcar_consulta(data_consulta):
    if data_consulta:
        clientes_data = obter_clientes()
        for cliente_data in clientes_data:
            nome, info = cliente_data[0], cliente_data[1:]
            assunto = "Consulta Agendada"
            mensagem = f"Olá Sr(a). {nome}, sua consulta foi agendada para o dia {data_consulta}."
            enviar_email(info[0], assunto, mensagem)
            atualizar_ultima_consulta(nome, data_consulta)
        sg.popup("E-mail enviado com sucesso!")
    else:
        sg.popup_error("Preencha a data da consulta.")

def mostrar_clientes_cadastrados():
    clientes_data = obter_clientes()
    header = ['Nome', 'E-mail', 'Última Consulta']
    layout = [
        [sg.Table(values=clientes_data, headings=header, display_row_numbers=False, auto_size_columns=False, justification='right', key='Table')],
        [sg.Button("Fechar"), sg.Button("Excluir Cadastro", key='excluir_cadastro')]
    ]
    window = sg.Window("Clientes Cadastrados", layout)
    
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Fechar":
            break
        elif event == 'Table':

            if values['Table']:
                indice_selecionado = values['Table'][0]
                nome_selecionado = clientes_data[indice_selecionado][0]
                atualizar_cliente(nome_selecionado)

                window.Element('Table').update(values=obter_clientes())
        elif event == 'excluir_cadastro':

            if values['Table']:
                indice_selecionado = values['Table'][0]
                nome_selecionado = clientes_data[indice_selecionado][0]
                excluir_cliente(nome_selecionado)

                window.Element('Table').update(values=obter_clientes())

    window.close()


sg.set_options(icon='image/express_icon.ico')

def atualizar_cliente(nome):
    cliente = obter_dados_cliente(nome)
    if not cliente:
        sg.popup_error("Cliente não encontrado.")
        return

    layout = [
        [sg.Text(f"Atualizar Cliente: {nome}")],
        [sg.Text("Novo Nome:"), sg.InputText(key="novo_nome", default_text=cliente[0])],
        [sg.Text("Novo E-mail:"), sg.InputText(key="novo_email", default_text=cliente[1])],
        [sg.Button("Atualizar", key="atualizar_cliente")]
    ]
    window = sg.Window(f"Atualizar Cliente: {nome}", layout)
    
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "atualizar_cliente":
            novo_nome = values["novo_nome"]
            novo_email = values["novo_email"]
            if novo_nome and novo_email:
                cursor.execute('UPDATE clientes SET nome = ?, email = ? WHERE nome = ?', (novo_nome, novo_email, nome))
                conn.commit()
                sg.popup(f"Cliente {nome} atualizado com sucesso!")
                window.close()
                break
            else:
                sg.popup_error("Preencha todos os campos.")

    window.close()

def obter_dados_cliente(nome):
    cursor.execute('SELECT nome, email FROM clientes WHERE nome = ?', (nome,))
    return cursor.fetchone()

layout = [
    [sg.Text("Nome:"), sg.InputText(key="nome")],
    [sg.Text("E-mail:"), sg.InputText(key="email")],
    [sg.Button("Cadastrar", key="cadastrar")],
    [sg.Text("Data da Consulta:"), sg.InputText(key="data_consulta"), sg.CalendarButton("Escolher Data", target="data_consulta", format="%Y-%m-%d")],
    [sg.Button("Marcar Consulta", key="marcar_consulta")],
    [sg.Button("Mostrar Clientes Cadastrados", key="mostrar_clientes")],
]

window = sg.Window("SystemExpress", layout)
window.set_icon('image/express_icon.ico')

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break
    elif event == "cadastrar":
        cadastrar_cliente(values["nome"], values["email"])
    elif event == "marcar_consulta":
        data_consulta = values["data_consulta"]
        if data_consulta and len(data_consulta) == 10:
            try:
                datetime.strptime(data_consulta, "%Y-%m-%d")
                marcar_consulta(data_consulta)
            except ValueError:
                sg.popup_error("Formato de data inválido. Use YYYY-MM-DD.")
        else:
            sg.popup_error("Preencha a data da consulta.")
    elif event == "mostrar_clientes":
        mostrar_clientes_cadastrados()

window.close()

conn.close()
