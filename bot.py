import xml.etree.ElementTree as ET
import os
import json

class Bot: 
    
    def __init__(self):

        if not os.path.exists("mensajes_automaticos.xml"):
            root = ET.Element("raiz")

            mensajes = ET.SubElement(root, "mensajes")
            disparadores = ET.SubElement(root, "disparadores")

            tree = ET.ElementTree(root)

            tree.write("mensajes_automaticos.xml")
            print("se ha creado el archivo")
        else:
            tree = ET.parse("mensajes_automaticos.xml")
            root = tree.getroot()
            print("se ha recuperado el archivo")

        if os.path.exists("interacciones.json"):
            with open("interacciones.json") as archivo:
                contenido = archivo.read()
                self.interacciones = json.load(contenido)


        self.root = root 
        resultados = self.root.findall(".//mensaje")
        self.cantidad_mensajes = len(resultados)

    def agregar_mensaje(self,contenido, lista_siguientes =None):
        mensaje = ET.SubElement(self.root.find("mensajes"), "mensaje")
        mensaje.set("id" , str(self.cantidad_mensajes))
        nodo_contenido = ET.SubElement(mensaje, "contenido")
        nodo_contenido.text = contenido
        self.cantidad_mensajes+=1

        if lista_siguientes != None:
            mensaje.set("lista_siguientes", str(lista_siguientes))

        tree = ET.ElementTree(self.root)
        tree.write("mensajes_automaticos.xml")
    
    def agregar_disparador(self, id_mensaje, tipo, entorno= None, contenido = None):
        # Crear el elemento disparador
        nodo_disparador = ET.SubElement(self.root.find("disparadores"), "disparador")
        nodo_disparador.set("id_mensaje", str(id_mensaje))
        nodo_disparador.set("tipo", tipo)
        if entorno :
           nodo_disparador.set("entorno", entorno)

        if tipo == "texto":
            nodo_disparador.text = contenido
    
        tree = ET.ElementTree(self.root)
        tree.write("mensajes_automaticos.xml")

