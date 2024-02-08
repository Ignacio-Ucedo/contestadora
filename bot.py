import xml.etree.ElementTree as ET
import os
import json

class Bot: 
    
    def __init__(self):

        if not os.path.exists("mensajes_automaticos.xml"):
            root = ET.Element("raiz")

            ET.SubElement(root, "contenidos")
            ET.SubElement(root, "disparadores")

            tree = ET.ElementTree(root)

            tree.write("mensajes_automaticos.xml")
            print("se ha creado el archivo")
        else:
            tree = ET.parse("mensajes_automaticos.xml")
            root = tree.getroot()
            print("se ha recuperado el archivo de mensajes")

        if os.path.exists("interacciones.json"):
            with open("interacciones.json") as archivo:
                self.interacciones = json.load(archivo)
        else:
            self.interacciones = {}
            self.actualizar_json()

        self.mensajes = root
        resultados = self.mensajes.findall(".//contenidos/mensaje")
        self.cantidad_mensajes = len(resultados)

        consulta_saludo = self.mensajes.find('.//disparador[@tipo="saludo"]/..')
        if consulta_saludo != None:
            self.saludo_id = consulta_saludo.get("id_mensaje")


    def agregar_mensaje(self,contenido, id = None, lista_siguientes =None):
        mensaje = ET.SubElement(self.mensajes.find("contenidos"), "mensaje")
        mensaje.set("id" , str(self.cantidad_mensajes))
        if id:
            resultado = self.mensajes.find(f'.//contenidos/mensaje[@id="{id}"]')
            mensaje = resultado
        nodo_contenido = ET.SubElement(mensaje, "contenido")
        nodo_contenido.text = contenido
        self.cantidad_mensajes+=1

        if lista_siguientes != None:
            mensaje.set("lista_siguientes", str(lista_siguientes))

        tree = ET.ElementTree(self.mensajes)
        tree.write("mensajes_automaticos.xml")
    
    def agregar_disparador(self, id_mensaje, tipo, entorno= None, condicion = None, contenido = None):
        # Crear el elemento disparador
        resultado = self.mensajes.find(f'.//disparadores/mensaje[@id="{id_mensaje}"]')
        if not resultado:
            nodo_mensaje = ET.SubElement(self.mensajes.find("disparadores"), "mensaje")
            nodo_mensaje.set("id_mensaje", str(id_mensaje))
        else:
            nodo_mensaje = resultado
        nodo_disparador = ET.SubElement(nodo_mensaje, "disparador")

        nodo_disparador.set("tipo", tipo)
        if entorno :
           nodo_disparador.set("entorno", entorno)

        if condicion:
            nodo_disparador.set("condicion", condicion)

        if tipo == "texto":
            nodo_disparador.text = contenido
    
        tree = ET.ElementTree(self.mensajes)
        tree.write("mensajes_automaticos.xml")

    #sirve para agregar también
    def modificar_interaccion(self, usuario_id, ultimo_mensaje_id):
        interaccion = self.interacciones.setdefault(usuario_id,{})
        interaccion["ultimo_mensaje_id"] = ultimo_mensaje_id


    def actualizar_json(self):
        with open("interacciones.json", "w") as archivo:
                json.dump(self.interacciones, archivo) 

    def contestar(self, mensaje, usuario_id):
        
        if usuario_id not in self.interacciones:        
            if self.saludo_id:
                self.enviar_mensaje(self.saludo_id, usuario_id)
                self.interacciones[usuario_id] = self.saludo_id


    def enviar_mensaje(self, id_mensaje, usuario_id):
        contenidos_a_enviar = self.mensajes.findall(f'.//mensaje[@id="{id_mensaje}"]/contenido')
        for contenido in contenidos_a_enviar:
            print(contenido.text)


        
