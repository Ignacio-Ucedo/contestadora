import xml.etree.ElementTree as ET
import os
import json
import logging

class Bot: 
    def __init__(self, ruta_mensajes, ruta_interacciones):
        self.registrador = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO ,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        self.ruta_interacciones = ruta_interacciones
        self.ruta_mensajes = ruta_mensajes
        try:
            self._cargar_archivo_mensajes()
            self._cargar_interacciones()

            self._configurar_bot()
        except Exception as e:
            self.registrador.error(f"Error al inicializar el bot: {str(e)}")

    def _cargar_archivo_mensajes(self):
        if os.path.exists(self.ruta_mensajes):
            self.registrador.info(f"Se ha recuperado el archivo {self.ruta_mensajes}")
        else:
            raiz = ET.Element("raiz")
            ET.SubElement(raiz, "contenidos")
            ET.SubElement(raiz, "disparadores")
            ET.ElementTree(raiz).write(self.ruta_mensajes)
            self.registrador.info(f"Se ha creado el archivo {self.ruta_mensajes}")
        self.mensajes = ET.parse(self.ruta_mensajes).getroot()
        
    def _cargar_interacciones(self):
        if os.path.exists(self.ruta_interacciones):
            with open(self.ruta_interacciones) as archivo:
                self.interacciones = json.load(archivo)
            self.registrador.info(f"Se ha recuperado el archivo {self.ruta_interacciones}")
        else:
            self.interacciones = {}
            self._actualizar_archivo_interacciones()
            self.registrador.info(f"Se creado el archivo {self.ruta_interacciones}")

    def _configurar_bot(self):
        #"cantidad de mensajes"
        resultados = self.mensajes.findall(".//contenidos/mensaje")
        self.cantidad_mensajes = len(resultados)

        "saludo"
        consulta_saludo = self.mensajes.find('.//disparador[@tipo="saludo"]/..')
        if consulta_saludo is not None:
            self.saludo_id = consulta_saludo.get("id_mensaje")

        "mensaje_principal"
        consulta_mensaje_principal = self.mensajes.find('.//disparador[@tipo="mensaje_principal"]/..')
        if consulta_mensaje_principal is not None:
            self.mensaje_principal_id = consulta_mensaje_principal.get("id_mensaje")
        else:
            self.registrador.warn("No se ha encontrado un mensaje principal")

        self.registrador.info(f"El bot ha sido inicializado con éxito")
        

    def _actualizar_archivo_interacciones(self):
        with open(self.ruta_interacciones, "w") as archivo:
            json.dump(self.interacciones, archivo)

    def agregar_mensaje(self, contenido, id=None, lista_siguientes=None):
        mensaje = ET.SubElement(self.mensajes.find("contenidos"), "mensaje")
        mensaje.set("id", str(self.cantidad_mensajes))
        if id:
            resultado = self.mensajes.find(f'.//contenidos/mensaje[@id="{id}"]')
            mensaje = resultado
        nodo_contenido = ET.SubElement(mensaje, "contenido")
        nodo_contenido.text = contenido
        self.cantidad_mensajes += 1

        if lista_siguientes is not None:
            mensaje.set("lista_siguientes", str(lista_siguientes))

        self._guardar_mensajes()

    def definir_hijos(self, id_mensaje, hijos):
        mensaje = self.mensajes.find(f'.//contenidos/mensaje[@id="{id_mensaje}"]')
        for hijo in hijos:
            self.agregar_mensaje(id_mensaje, hijo)
        if mensaje:
            mensaje.set("hijos", str(hijos))
            self._guardar_mensajes()
        else:
            "codear"
            pass 

    def _guardar_mensajes(self):
        ET.ElementTree(self.mensajes).write(self.ruta_mensajes)

    def agregar_disparador(self, id_mensaje, tipo, entorno=None, condicion=None, contenido=None):
        nodo_mensaje = self.mensajes.find(f'.//disparadores/mensaje[@id="{id_mensaje}"]')
        if nodo_mensaje is None:
            nodo_mensaje = ET.SubElement(self.mensajes.find("disparadores"), "mensaje")
            nodo_mensaje.set("id_mensaje", str(id_mensaje))

        nodo_disparador = ET.SubElement(nodo_mensaje, "disparador")
        nodo_disparador.set("tipo", tipo)
        if entorno:
            nodo_disparador.set("entorno", entorno)

        if condicion:
            nodo_disparador.set("condicion", condicion)

        if tipo == "texto":
            nodo_disparador.text = contenido

        self._guardar_mensajes()

    def modificar_interaccion(self, usuario_id, ultimo_mensaje_id):
        interaccion = self.interacciones.setdefault(usuario_id, {})
        interaccion["ultimo_mensaje_id"] = ultimo_mensaje_id
        self._actualizar_archivo_interacciones()

    def contestar(self, mensaje, usuario_id):
        
        if usuario_id not in self.interacciones:        
            if self.saludo_id:
                self.enviar_mensaje(self.saludo_id, usuario_id)
            
            self.interacciones[usuario_id] = self.mensaje_principal_id
            self.enviar_mensaje(self.mensaje_principal_id, usuario_id)
        else:
            ultimo_mensaje_id= self.interacciones[usuario_id]
            id_hijos = self.mensajes.find(f'.//mensaje[@id="{ultimo_mensaje_id}"]').get("hijos")
            if id_hijos != None:
                id_hijos = json.loads(id_hijos)

                for id_hijo in id_hijos:
                    disparador = self.mensajes.find(f'.//mensaje[@id_mensaje="{id_hijo}"]/disparador[@entorno="local"]')
                    if disparador != None:
                        disparador = disparador.text
                
                        if disparador == mensaje:
                            self.interacciones[usuario_id] = id_hijo 
                            self.enviar_mensaje(id_hijo, usuario_id)
                            break
            else:
                "chequear excepción?"
                self.interacciones[usuario_id]


    def enviar_mensaje(self, id_mensaje, usuario_id):
        contenidos_a_enviar = self.mensajes.findall(f'.//mensaje[@id="{id_mensaje}"]/contenido')
        for contenido in contenidos_a_enviar:
            print(contenido.text)

