import flet as ft
import Pyro4
import threading


agendaId = ft.TextField(label="ID da agenda")
serverIp = ft.TextField(label="IP do servidor")
contactName = ft.TextField(label="Nome do contato")
phoneNumber = ft.TextField(label="Telefone do contato")
actions = ft.Dropdown(options=[
    ft.dropdown.Option(key="1",text="Adicionar Contato"),
    ft.dropdown.Option(key="2",text="Remover Contato"),
    ft.dropdown.Option(key="3",text="Atualizar Contato"),
    ft.dropdown.Option(key="4",text="Listar Contatos")
], width=180, value="1", label="Opcoes da agenda")



debugLog = ft.Column()


class Client:
    def __init__(self):
        self.proxy  = None

    def connect(self):
        print("EntrouAQUI")
        try:
            self.proxy = Pyro4.Proxy(f"PYRONAME:agenda.{agendaId.value}@{serverIp.value}:9090")
            debugLog.controls.append(ft.Text(f"Conectado com sucesso!"))
            print("CONNECTADO")
            debugLog.update()
        except Pyro4.errors.CommunicationError as e:
            print(e)
            debugLog.controls.append(ft.Text(f"{e}."))
            debugLog.update()

    def choose_op(self):
        choice = int(actions.value)
        
        if choice == 1:
            self.add_contact_to_agenda()
        elif choice == 2:
            self.remove_contact_from_agenda()
        elif choice == 3:
            self.update_contact_on_agenda()
        else:
            self.get_contact_from_agenda()

    def add_contact_to_agenda(self):
        name  = contactName.value
        phone = phoneNumber.value
        try:
            self.proxy.add_contacts(name, phone)
            debugLog.controls.append(ft.Text("Contato adicionado."))
            debugLog.update()
        except Pyro4.errors.CommunicationError as e:
            debugLog.controls.append(ft.Text("ERRO: Agenda indisponível, tente uma nova agenda."))
            debugLog.update()

    def remove_contact_from_agenda(self):
        try:
            self.proxy.remove_contact(contactName.value)
            debugLog.controls.append(ft.Text(f"Contato removido."))
            debugLog.update()
        except Pyro4.errors.CommunicationError as e:
            debugLog.controls.append(ft.Text(f"ERRO: Agenda indisponível, tente uma nova agenda."))
            debugLog.update()
        
    def update_contact_on_agenda(self):
        try:
            self.proxy.update_contact(contactName.value, phoneNumber.value)
            debugLog.controls.append(ft.Text(f"Contato atualizado."))
            debugLog.update()
        except Pyro4.errors.CommunicationError as e:
            debugLog.controls.append(ft.Text(f"ERRO: Agenda indisponível, tente uma nova agenda."))
            debugLog.update()

    def get_contact_from_agenda(self):
        try:
            contacts = self.proxy.get_contacts()
            debugLog.controls.append(ft.Text(f"Lista de contatos: {contacts}."))
            debugLog.update()
        except Pyro4.errors.CommunicationError as e:
            debugLog.controls.append(ft.Text(f"ERRO: Agenda indisponível, tente uma nova agenda."))
            debugLog.update()

client = Client()

def connect(e):
    client.connect()
def callAction(e):
    client.choose_op()
    
def main(page: ft.Page):
    page.window.width = 850
    page.window.height = 600
    page.add(ft.Column([
       ft.Row([serverIp,agendaId]),
       ft.FilledButton("Conectar", on_click=connect),
       ft.Row([contactName, phoneNumber, actions]),
       ft.FilledButton("Executar", on_click=callAction),
       debugLog
    ],horizontal_alignment="center"))


ft.app(main)
