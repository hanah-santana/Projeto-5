import flet as ft
import threading
import Pyro4


debugLog = ft.Column([
    ft.Text("Log de debug", size=25)
])
serverName = ft.TextField(label="Nome do servidor")
serverIp = ft.TextField(label="IP do servidor")
serverPort = ft.TextField(label="Porta do servidor")
tree: list[ft.Control] = [ ft.Text("Contatos", size=25) ]
treeContainer = ft.Column(tree)

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Agenda:
    def __init__(self):
        self.contacts = {}  # Dicionario de contatos {nome: telefone}
        self.replicas = []  # lista de replicas (uris)
        self.uri      = None
    
    def add_replica(self, replica_uri):
        try:
            self.replicas.append(replica_uri)
            debugLog.controls.append(ft.Text(f"Replica {replica_uri} adicionada."))
            debugLog.update()
        except Exception as e:
            debugLog.controls.append(ft.Text(f"{e}"))
            debugLog.update()

    def synchronize(self):
        for uri in self.replicas:
            try:
                replica = Pyro4.Proxy(uri)
                replica.add_replica(self.uri)
                self.contacts.update(replica.get_contacts())
            except Pyro4.errors.CommunicationError:
                debugLog.controls.append(ft.Text(f"Falha de sincronização para {uri}."))
                debugLog.update()
            except Exception as e:
                debugLog.controls.append(ft.Text(f"{e}."))
                debugLog.update()
        
        for name, phone in self.contacts.items():
            tree.append(ft.Text(f"Nome: {name} | Telefone: {phone}", key=name))
            treeContainer.update()
    
    def get_contacts(self):
        return self.contacts
    
    def get_replicas(self):
        return self.replicas
    
    def get_uri(self):
        return self.uri
    
    def set_uri(self, uri):
        self.uri = uri
        debugLog.controls.append(ft.Text(f"URI: {uri}."))
        debugLog.update()

    def add_contacts(self, name, phone):
        if name in self.contacts:
            raise ValueError("Contato já existe.")
        self.contacts[name] = phone
        tree.append(ft.Text(f"Nome: {name} | Telefone: {phone}", key=name))
        treeContainer.update()
        self.propagate_change('add', name, phone)
    
    def remove_contact(self, name):
        if name not in self.contacts:
            raise ValueError("Contato não encontrado.")
        del self.contacts[name]
        for item in tree:
            if item.key == name:
                tree.remove(item)
                break
        treeContainer.update()
        self.propagate_change('remove', name)

    def update_contact(self, name, new_phone):
        if name not in self.contacts:
            raise ValueError("Contato não encontrado.")
        
        for contact_name, contact_phone in self.contacts.items():
            if contact_name == name and contact_phone == new_phone:
                raise ValueError("Contato atualizado.")

        self.contacts[name] = new_phone
        for item in tree:
            if item.key == name:
                tree.remove(item)
                tree.append(ft.Text(f"Nome: {name} | Telefone: {new_phone}", key=name))
        treeContainer.update()
        self.propagate_change('update', name, new_phone)
    
    def propagate_change(self, action, name, phone=None):
        for uri in self.replicas:
            try:
                replica = Pyro4.Proxy(uri)
                if action == 'add':
                    replica.add_contacts(name, phone)
                elif action == 'remove':
                    replica.remove_contact(name)
                elif action == 'update':
                    replica.update_contact(name, phone)
            except Pyro4.errors.CommunicationError:
                debugLog.controls.append(ft.Text(f"Falha de sincronização para {uri}."))
                debugLog.update()
            except ValueError:  # Exceção = Fim da recursão, não faz nada nem aponta erros
                pass
            except Exception as e:
                debugLog.controls.append(ft.Text(f"{e}"))
                debugLog.update()

def launch_remote_server(e):
    ip = serverIp.value
    port = int(serverPort.value)
    name = serverName.value

    threadRemoteServer = threading.Thread(
        target=start_remote_server, kwargs={"ip": ip, "port": port, "name": name}, daemon=True
    )
    threadRemoteServer.start()

def start_remote_server(ip, port, name):
    daemon  = Pyro4.Daemon(host=ip, port=port)
    try:
        ns  = Pyro4.locateNS(host=ip, port=9090)
        agenda = Agenda()
        replicas = ns.list(prefix="agenda.")
        for _, agenda_uri in replicas.items():
            agenda.add_replica(agenda_uri)
        uri = daemon.register(agenda)
        agenda.set_uri(uri)
        agenda.synchronize()
        ns.register(f"agenda.{name}", uri)
        daemon.requestLoop()
    except Exception as e:
        debugLog.controls.append(ft.Text(f"{e}"))
        debugLog.update()  


def main(page: ft.Page):
    page.add(ft.Column([
        ft.Column([
            serverIp,
            serverName,
            serverPort,
            ft.ElevatedButton("Iniciar servidor remoto", on_click=launch_remote_server)
        ]),
        treeContainer,
        debugLog
    ]))


ft.app(main)
