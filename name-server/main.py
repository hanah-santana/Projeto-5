import flet as ft
import threading
import Pyro4
import Pyro4.naming

debugLog = ft.Column()
textfield = ft.TextField(label="Seu IPV4")
button = ft.ElevatedButton("Iniciar servidor de nomes")
debugLog.controls.append(ft.Text("Log de debug", size=25))

class NameServer:
    def __init__(self):
        self.ip     = None

    def set_ip(self):
        self.ip = textfield.value
        if self.ip:
            self.launch_name_server()
        else:
            debugLog.controls.append(ft.Text("ERRO: ENTRADA VAZIA"))
            debugLog.update()

    def launch_name_server(self):
        threadNameServer = threading.Thread(
            target=Pyro4.naming.startNSloop, kwargs={"host": self.ip}, daemon=True
        )
        debugLog.controls.append(ft.Text("Servidor de nomes ativo"))
        debugLog.update()
        threadNameServer.start()

nameServer = NameServer()

def main(page: ft.Page):
    
    page.window.width = 600
    
    
    def button_click(e):
        nameServer.set_ip()
        
    button.on_click = button_click

    page.add(ft.Column([
       ft.Row([
           textfield,
           button
           ]),
        debugLog
    ]))

ft.app(main)
