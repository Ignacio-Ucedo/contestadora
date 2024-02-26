import xml.etree.ElementTree as ET
import os
import json
import logging
import re

class Bot: 

    """
    Clase que representa al bot con funcionalidades referidas a la creación, modificación 
    y comportamiento de los mensajes automáticos.
    """

    def __init__(self, ruta_mensajes = None, ruta_interacciones = None):
        """
        Inicializa una instancia de la clase Bot.

        Parámetros:
        - ruta_mensajes (str, opcional): Ruta al archivo XML que contiene los mensajes del bot.
        Si no se pasa, se utiliza una por defecto.
        - ruta_interacciones (str, opcional): Ruta al archivo JSON que contiene las interacciones del bot.
        Si no se pasa, se utiliza una por defecto.
        """
        self.registrador = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO ,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        if ruta_mensajes == None:
            ruta_por_defecto_mensajes = "mensajes_automaticos.xml"
            self.ruta_mensajes = ruta_por_defecto_mensajes
        else:
            self.ruta_mensajes = ruta_mensajes

        if ruta_interacciones == None:
            ruta_por_defecto_interacciones = "interacciones.json"
            self.ruta_interacciones = ruta_por_defecto_interacciones
        else:
            self.ruta_interacciones = ruta_interacciones

        try:
            self._cargar_archivo_mensajes()
            self._cargar_interacciones()

            #conexión a interfaz de prueba:
            # self.interfaz = interfaz_de_prueba

            self._configurar_bot()
        except Exception as e:
            self.registrador.error(f"Error al inicializar el bot: {str(e)}")


#-----------------------------------------------privados----------------------------------------------


    def _cargar_archivo_mensajes(self):
        """
        Carga en el bot los mensajes del XML.
        """
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
        """
        Carga en el bot las interacciones del JSON
        """
        if os.path.exists(self.ruta_interacciones):
            with open(self.ruta_interacciones) as archivo:
                self.interacciones = json.load(archivo)
            self.registrador.info(f"Se ha recuperado el archivo {self.ruta_interacciones}")
        else:
            self.interacciones = {}
            self._actualizar_archivo_interacciones()
            self.registrador.info(f"Se creado el archivo {self.ruta_interacciones}")

    def _configurar_bot(self):
        """
        Configura el bot utilizando la información cargada desde los archivos XML y JSON.
        """
        #cantidad de mensajes
        resultados = self.mensajes.findall(".//contenidos/mensaje")
        self.cantidad_mensajes = len(resultados)

        #saludo
        consulta_saludo = self.mensajes.find('.//disparador[@tipo="saludo"]/..')
        if consulta_saludo is not None:
            self.saludo_id = consulta_saludo.get("id_mensaje")

        #mensaje_principal
        consulta_mensaje_principal = self.mensajes.find('.//disparador[@tipo="mensaje_principal"]/..')
        if consulta_mensaje_principal is not None:
            self.mensaje_principal_id = consulta_mensaje_principal.get("id_mensaje")
        else:
            self.registrador.warn("No se ha encontrado un mensaje principal")
        
        #los disparadores globales comienzan activos por defecto
        if self._hay_globales():
            self.globales_activados = True
            self.mensajes_con_global = self.mensajes.findall('.//disparador[@entorno="global"]/..')

        self.registrador.info(f"El bot ha sido inicializado con éxito")
        
    def _hay_globales(self):
        consulta = self.mensajes.find('.//disparador[@entorno="global"]')
        return consulta != None

    def _actualizar_archivo_interacciones(self):
        """
        Carga en el archivo JSON las interacciones del bot.
        """
        with open(self.ruta_interacciones, "w") as archivo:
            json.dump(self.interacciones, archivo)

    def _guardar_mensajes(self):
        ET.ElementTree(self.mensajes).write(self.ruta_mensajes)


#-------------------------------------------públicos-------------------------------------------------


    def agregar_o_modificar_mensaje(self, id=None, contenido = None, titulo=None, lista_siguientes=None):
        """
        Agrega o modifica un mensaje del bot.

        Parámetros:
        - id (int, opcional): Identificador único del mensaje. Se pasa en caso de que se quiera agregar
        contenido o definir la lista de siguientes a un mensaje EXISTENTE.
        - contenido (str, opcional): Contenido del mensaje.    
        - titulo: 
        - lista_siguientes (list[int], opcional): Lista de identificadores de mensajes siguientes.

        """
        if id == None or id == self.cantidad_mensajes:
            "mensaje nuevo"
            mensaje = ET.SubElement(self.mensajes.find("contenidos"), "mensaje")
            mensaje.set("id_mensaje", str(self.cantidad_mensajes))
            self.cantidad_mensajes += 1
        else:
            "mensaje existente"
            resultado = self.mensajes.find(f'.//contenidos/mensaje[@id="{id}"]')
            mensaje = resultado
        
        if contenido != None:
            nodo_contenido = ET.SubElement(mensaje, "contenido")
            nodo_contenido.text = contenido
            mensaje.set("titulo", titulo)

        if lista_siguientes != None:
            mensaje.set("siguientes", str(lista_siguientes))
            for id_siguiente in lista_siguientes:
                self.agregar_o_modificar_mensaje(id_siguiente)

        self._guardar_mensajes()


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
        
        #se envía saludo si tiene
        if usuario_id not in self.interacciones:        
            if self.saludo_id:
                self._enviar_mensaje(self.saludo_id, usuario_id)
                self.contestar(mensaje, usuario_id)
                return
        #tiene globales 
        elif hasattr(self, 'mensajes_con_global') and self.globales_activados:
            for mensaje_con_global in self.mensajes_con_global:
                disparadores_globales_del_mensaje = mensaje_con_global.findall('./disparador[@entorno="global"]')
                for disparador in disparadores_globales_del_mensaje:
                    condicion= disparador.get('condicion')
                    disparador_texto= disparador.text

                    id_mensaje = mensaje_con_global.get('id_mensaje')
                    #si tiene el atributo:

                    if condicion == "contiene":
                        if disparador_texto.lower() in mensaje.lower():
                            self._enviar_mensaje(id_mensaje)                                          
                            return
                    else:
                        if mensaje == disparador_texto:
                            self._enviar_mensaje(id_mensaje)
                            return
       
        #si no tiene globales o están desactivados o no encontró mensaje para enviar
            #si es su primer mensaje (sin contar el saludo)
        if  (hasattr(self, "saludo_id") and self.saludo_id == self.interacciones[usuario_id]) or (usuario_id not in self.interacciones):
            self._enviar_mensaje(self.mensaje_principal_id, usuario_id)
            return

        ultimo_mensaje_id = self.interacciones[usuario_id]
        nodo_ultimo_mensaje = self.mensajes.find(f'.//contenidos/mensaje[@id_mensaje="{ultimo_mensaje_id}"]')
        id_hijos = nodo_ultimo_mensaje.get("hijos")
        if id_hijos != None:
            id_hijos = json.loads(id_hijos)

            for id_hijo in id_hijos:
                disparadores_hijo = self.mensajes.findall(f'.//mensaje[@id_mensaje="{id_hijo}"]/disparador[@entorno="local"]')
                for disparador in disparadores_hijo:
                    condicion = disparador.get("condicion")
                    disparador_texto= disparador.text

                    if condicion == "contiene":
                        if disparador_texto.lower() in mensaje.lower():
                            self._enviar_mensaje(id_hijo)                                          
                            return
                    else:
                        if mensaje == disparador_texto:
                            self._enviar_mensaje(id_hijo)
                            return
        if  "excepcion" in nodo_ultimo_mensaje.attrib:
           id_excepcion = nodo_ultimo_mensaje.get("excepcion")
           self._enviar_mensaje(id_excepcion)
    
    def _procesar_interactivo(self, mensaje, contenido):
         patron = r"{([^\{\}]+)}"
         resultados = re.findall(patron, contenido.text)
         print(resultados)
         for funcion in resultados:
             resultado_funcion = getattr(self, funcion)(mensaje)
             if isinstance(resultado_funcion, list):
                 string_lista = ""
                 n = 1
                 for resultado in resultado_funcion:
                     if resultado != None:
                      string_lista += "\n"
                      string_lista += str(n) + "-" + resultado
                      n += 1
                      

                 texto = contenido.text
                 funcion = "{" + funcion + "}"
                 nuevo_texto = texto.replace(funcion, string_lista)

         return nuevo_texto

    def imprimir_hijos(self, mensaje):
             titulos = []
             hijos = mensaje.get("hijos")
             hijos_lista = json.loads(hijos)
             for hijo in hijos_lista:
                nodo_hijo = self.mensajes.find(f'.//contenidos/mensaje[@id_mensaje="{hijo}"]')
                titulo_hijo = nodo_hijo.get("titulo")
                titulos.append(titulo_hijo)
             return titulos


                 
             
             


        


    def _enviar_mensaje(self, id_mensaje, usuario_id=None):
        mensaje= self.mensajes.find(f'./contenidos/mensaje[@id_mensaje="{id_mensaje}"]')
        if mensaje != None:
            if "globales_activados" in mensaje.attrib:
                self.globales_activados = not self.globales_activados
            contenidos_a_enviar = mensaje.findall('./contenido')
            for contenido in contenidos_a_enviar:
                respuesta= contenido.text
                if "tipo" in contenido.attrib and contenido.attrib["tipo"] == "interactivo":
                    respuesta = self._procesar_interactivo(mensaje, contenido)
                    
                self.interfaz.contestar_iu_desarrollo(respuesta)
                self.registrador.info("Se envió un mensaje")
            self.interacciones[usuario_id] = id_mensaje

   



#-------------------------------------conexion a interfaz-------------------------------------
    def _datos_de_mensaje(self, id_mensaje):
        resultado_xml = self.mensajes.findall(f'.//mensaje[@id_mensaje="{id_mensaje}"]')
        datos = {}

        for mensaje in resultado_xml:
            # Iterar sobre los atributos del mensaje y guardarlos en el diccionario
            for atributo, valor in mensaje.attrib.items():
                datos[atributo] = valor

            # Obtener los contenidos y guardarlos en una lista bajo la clave "contenidos"
            contenidos = [contenido.text.strip() for contenido in mensaje.findall(".//contenido")]
            if contenidos:
                datos["contenidos"] = contenidos

            # Obtener los disparadores y guardarlos en una lista de diccionarios
            disparadores = []
            for disparador in mensaje.findall(".//disparador"):
                # disparador_dict = {disparador.tag: disparador.attrib}
                disparador_dict = {}
                for atributo, valor in disparador.attrib.items():
                    disparador_dict[atributo]=valor
                contenido_disparador = disparador.text.strip() if disparador.text else None
                if contenido_disparador:
                    disparador_dict["contenido_disparador"] = contenido_disparador
                disparadores.append(disparador_dict)
            if disparadores:
                datos["disparadores"] = disparadores

        return datos
