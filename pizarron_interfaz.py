import tkinter as tk

class Pizarron(tk.Canvas):

    def __init__(self, master, interfaz_padre=None, **kwargs):
    #--------------------------------------------------------elementos del disenio--------------------------------------------
        
        super().__init__(master, bg="#222222", **kwargs)
        self.bind("<Motion>", self.en_movimiento_mouse) 
        self.bind("<ButtonPress-1>", self.presionar_clic_izq)
        self.bind("<B1-Motion>", self.arrastre_clic_izq)
        self.bind("<ButtonRelease-1>", self.soltar_clic_izq)
        self.bind("<ButtonPress-3>", self.presionar_clic_der)  
        self.bind("<B3-Motion>", self.arrastre_clic_der)       
        self.bind("<ButtonRelease-3>", self.soltar_clic_der)       
        self.bind("<MouseWheel>", self.rueda_mouse)            
        self.bind("<Button-4>", self.rueda_mouse)             
        self.bind("<Button-5>", self.rueda_mouse)             
        self.master=master #el canvas padre, el que lo contiene
        #si se inicia dentro de la interfaz de desarrollo 
        #[CONEXION INTERFAZ]:
        if interfaz_padre != None:
            self.interfaz_padre = interfaz_padre
            # self.bot = interfaz_padre.bot
        self.cursor_x = None #ubicación x del cursor
        self.cursor_y = None #ubicación x del cursor
        self.escala_zoom = 1
        self.tarjetas_mensaje = [] #lista de tarjetas de mensaje
        self.padres_hijos = {} #diccionario para registrar las conexiones entre una tarjeta padre y una lista de hijos

        #barra de herramientas
        self.barra_herramientas = tk.Frame(self, bg="#d9cead", bd=1, relief="raised")
        self.barra_herramientas.pack(side="top", fill="x")  

        # Botón 1
        self.boton1 = tk.Button(self.barra_herramientas, text="Agregar Mensaje", bg="#d9cead", command=self.funcion_boton1)
        self.boton1.pack(side="left",)

        # Botón 2
        self.boton2 = tk.Button(self.barra_herramientas, text="Botón 2", bg= "#d9cead", command=self.funcion_boton2)
        self.boton2.pack(side="left")

        # Botón 3
        self.boton3 = tk.Button(self.barra_herramientas, text="Botón 3", bg="#d9cead",command=self.funcion_boton3)
        self.boton3.pack(side="left")
        
        self.tarjeta_a_borrar = None
        # Manejo de las flechas
        self.flechas = {}  #diccionario[flecha](list[origen,destino])
        self.tarjeta_a_flechas = {} #diccionario[tarjeta](list[flecha1,flecha2,...,flecha_n])
        self.flecha_actual = None
        self.inicio_flecha_x = None
        self.inicio_flecha_y = None
        self.bind("<Button-1>", self.iniciar_dibujo_flecha)
        self.area_tolerancia = 20 # a gusto

        #carga de mensajes


    #------------------------------------------------de movimiento general--------------------------------------------------------
    
    def en_movimiento_mouse(self, evento):
        self.cursor_x = self.canvasx(evento.x)
        self.cursor_y = self.canvasy(evento.y)
        if not self._puntero_en_zona_vacia():
            self._cambiar_cursor_a_puntero_dedo()
        else:
            self._revertir_cursor_a_defecto()
        self._iluminar_tarjetas_alrededor(self.area_tolerancia)


    def presionar_clic_izq(self, evento):
        self.cursor_x = self.canvasx(evento.x)
        self.cursor_y = self.canvasy(evento.y)

    def arrastre_clic_izq(self, evento):
        self.cursor_x = self.canvasx(evento.x)
        self.cursor_y = self.canvasy(evento.y)
        self._iluminar_tarjetas_alrededor(self.area_tolerancia)
        self._dibujar_flecha(evento)
        if not self.flecha_actual and self._puntero_en_zona_vacia():
            self.scan_dragto(evento.x, evento.y, gain=1)
            self._cambiar_cursor_a_puntero_manito()


    def soltar_clic_izq(self, evento):
        if hasattr(self, "tarjeta_origen"):
            self._detener_dibujo_flecha(evento)

    def presionar_clic_der(self, evento):  
        pass

    def arrastre_clic_der(self, evento):   
        self.cursor_x = self.canvasx(evento.x)
        self.cursor_y = self.canvasy(evento.y)
        self._cambiar_cursor_a_puntero_eliminacion()
        mouse_en_tarjeta=False
        for tarjeta in self.tarjetas_mensaje:
            x1, y1, x2, y2 = self.bbox(tarjeta.rect_id)
            mouse_en_tarjeta = x1 <= self.cursor_x <= x2 and y1<=self.cursor_y <= y2
            if mouse_en_tarjeta:
                self.tarjeta_a_borrar = tarjeta
                break
        if not mouse_en_tarjeta and self.tarjeta_a_borrar != None:
            self._borrar_tarjeta()

    def soltar_clic_der(self, evento):
        self._revertir_cursor_a_defecto()
        self.tarjeta_a_borrar = None

    def rueda_mouse(self, evento):
        self.cursor_x = self.canvasx(evento.x)
        self.cursor_y = self.canvasy(evento.y)
        if evento.num == 4 or evento.delta == 120:  
            factor_escalado = 1.1
            self.scale("all", self.canvasx(evento.x), self.canvasy(evento.y), factor_escalado, factor_escalado)  # Zoom in
            self.escala_zoom = self.escala_zoom*1.1
        elif evento.num == 5 or evento.delta == -120:  
            factor_escalado =0.9 
            self.scale("all", self.canvasx(evento.x), self.canvasy(evento.y), factor_escalado, factor_escalado)  # Zoom out
            self.escala_zoom = self.escala_zoom*0.9

        for tarjeta in self.tarjetas_mensaje:
            tarjeta.actualizar_tamanio_texto_por_zoom(factor_escalado)

    #----------------------------------------------------flechas---------------------------------------------------------

    def iniciar_dibujo_flecha(self, evento):
        for tarjeta in self.tarjetas_mensaje:

            if self._mouse_en_zona_tolerante(self.area_tolerancia, tarjeta):
                self.inicio_flecha_x = self.canvasx(evento.x)
                self.inicio_flecha_y = self.canvasy(evento.y)
                self.tarjeta_origen = tarjeta
                return
        if not self.flecha_actual:
            #inicio del movimiento del pizarron
            self.scan_mark(evento.x, evento.y)
        
    def _dibujar_flecha(self, evento):
        if self.inicio_flecha_x is not None and self.inicio_flecha_y is not None:
            fin_x = self.canvasx(evento.x)
            fin_y = self.canvasy(evento.y)
            if self.flecha_actual:
                self.delete(self.flecha_actual)
            self.flecha_actual = self.create_line(self.inicio_flecha_x, self.inicio_flecha_y, fin_x, fin_y, arrow=tk.LAST, fill='#7ad1ff')
        
    def _detener_dibujo_flecha(self, evento):
        # Verificar si la punta de la flecha está dentro del área de tolerancia de alguna tarjeta
        # punta_flecha_x, punta_flecha_y = self.canvasx(evento.x), self.canvasy(evento.y)
        punta_flecha_en_otra_tarjeta = False
        for tarjeta in self.tarjetas_mensaje:
            if tarjeta != self.tarjeta_origen:

                if self._mouse_en_zona_tolerante(self.area_tolerancia, tarjeta):
                    # Verificar si la tarjeta es diferente a la tarjeta desde la que se inició el dibujo
                    if self.tarjeta_origen not in self.padres_hijos:
                        self.padres_hijos[self.tarjeta_origen] = []
                    lista_hijos = self.padres_hijos[self.tarjeta_origen]
                    if tarjeta not in lista_hijos:
                        lista_hijos.append(tarjeta)
                        punta_flecha_en_otra_tarjeta = True
                        tarjeta_destino = tarjeta
                    break

        # Si la punta de la flecha está en una tarjeta
        if punta_flecha_en_otra_tarjeta:
            self.flechas[self.flecha_actual] = [self.tarjeta_origen, tarjeta_destino]

            #registro la flecha en su origen y su destino en self tarjeta a flechas
            if self.tarjeta_origen not in self.tarjeta_a_flechas:
                self.tarjeta_a_flechas[self.tarjeta_origen] = [self.flecha_actual]
            else:
                self.tarjeta_a_flechas[self.tarjeta_origen].append(self.flecha_actual)

            if tarjeta_destino not in self.tarjeta_a_flechas:
                self.tarjeta_a_flechas[tarjeta_destino] = [self.flecha_actual]
            else:
                self.tarjeta_a_flechas[tarjeta_destino].append(self.flecha_actual)

        # Borramos la flecha si no está en una tarjeta
        elif self.flecha_actual:
            self.delete(self.flecha_actual)

        self.inicio_flecha_x = None
        self.inicio_flecha_y = None
        self.flecha_actual = None

    def actualizar_posicion_flechas(self, tarjeta_en_movimiento, dx, dy):
        for flecha in self.tarjeta_a_flechas[tarjeta_en_movimiento]:
            par_origen_destino = self.flechas[flecha]
            if tarjeta_en_movimiento == par_origen_destino[0]: #hay que mover origen
                origen_x, origen_y, punta_x, punta_y = self.coords(flecha)
                nuevo_origen_x =  origen_x+ dx  # Calcula la nueva posición de origen en función del movimiento del ratón
                nuevo_origen_y =  origen_y+ dy  # Calcula la nueva posición de origen en función del movimiento del ratón
                self.coords(flecha, nuevo_origen_x, nuevo_origen_y, punta_x, punta_y)
            else: #hay que mover destino
                origen_x, origen_y, punta_x, punta_y = self.coords(flecha)
                nueva_punta_x = punta_x + dx  # Calcula la nueva posición de la punta en función del movimiento del ratón
                nueva_punta_y = punta_y+ dy  # Calcula la nueva posición de la punta en función del movimiento del ratón
                self.coords(flecha, origen_x, origen_y, nueva_punta_x, nueva_punta_y)

    def conectar_tarjetas_por_flecha(self, padre, hijo):
        _, _, x1, y1 = self.bbox(padre.rect_id)
        x2, y2, _, _ = self.bbox(hijo.rect_id)
        flecha_id = self.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill='#7ad1ff')
        self.flechas[flecha_id] = [padre,hijo]
        if padre in self.tarjeta_a_flechas:
            self.tarjeta_a_flechas[padre].append(flecha_id)
        else:
            self.tarjeta_a_flechas[padre] = [flecha_id]

        if hijo in self.tarjeta_a_flechas:
            self.tarjeta_a_flechas[hijo].append(flecha_id)
        else:
            self.tarjeta_a_flechas[hijo] = [flecha_id]
        
    #---------------------------------------------------botones barra de herramientas----------------------------------------

    def funcion_boton1(self):
        self.agregar_tarjeta_mensaje(25,25, {'contenidos':['texto'], 'id_mensaje': self.interfaz_padre.bot.cantidad_mensajes})

    def funcion_boton2(self):
        print("Botón 2 presionado")

    def funcion_boton3(self):
        print("Botón 3 presionado")

    def agregar_tarjeta_mensaje(self, x, y, datos_mensaje):
        tarjeta = TarjetaDeMensaje(self, x, y, datos_mensaje)
        self.tarjetas_mensaje.append(tarjeta)


#--------------------------------------------------utilidades------------------------------------------
    def _borrar_tarjeta(self):
        #acá se borra todo
        if self.tarjeta_a_borrar in self.tarjeta_a_flechas:#si tiene flechas involucradas
            for flecha in self.tarjeta_a_flechas[self.tarjeta_a_borrar]:
                par_origen_destino = self.flechas[flecha] 
                tarjeta_origen = par_origen_destino[0]
                tarjeta_destino= par_origen_destino[1]
                if tarjeta_origen == self.tarjeta_a_borrar:
                    self.tarjeta_a_flechas[tarjeta_destino].remove(flecha) #borro el elemento flecha de su complementario en tarjeta a flechas
                    if len(self.tarjeta_a_flechas[tarjeta_destino]) == 0: #si era su única flecha asociada
                        del self.tarjeta_a_flechas[tarjeta_destino]
                else:
                    self.tarjeta_a_flechas[tarjeta_origen].remove(flecha) #borro el elemento flecha de su complementario en tarjeta a flechas
                    if len(self.tarjeta_a_flechas[tarjeta_origen]) == 0: #si era su única flecha asociada
                        del self.tarjeta_a_flechas[tarjeta_origen]
                del self.flechas[flecha] #borro el par origen destino del diccionario de flechas
                self.delete(flecha) #la borro del canvas
            del self.tarjeta_a_flechas[self.tarjeta_a_borrar] #luego del for borro la lista entera de tarjeta a flechas
        self.tarjetas_mensaje.remove(self.tarjeta_a_borrar) #la borro de la lista de tarjetas
        self.tarjeta_a_borrar.eliminar_tarjeta() #acá se borra del canvas la tarjeta
        self.tarjeta_a_borrar = None

    def _iluminar_tarjetas_alrededor(self, tolerancia):
        for tarjeta in self.tarjetas_mensaje:
            if self._mouse_en_zona_tolerante(tolerancia, tarjeta):
                self.itemconfig(tarjeta.rect_id,  outline="lightblue", width =3)  
                # self._cambiar_cursor_a_puntero_dedo()
            else:
                self.itemconfig(tarjeta.rect_id, outline="black", width = 0)
                # self._revertir_cursor_a_defecto()


    def _mouse_en_zona_tolerante(self, tolerancia, tarjeta):
            x1, y1, x2, y2 = self.bbox(tarjeta.rect_id)
            borde_izquierdo = x1 - tolerancia <= self.cursor_x <= x1 and y1 - tolerancia <= self.cursor_y <= y2 + tolerancia
            borde_derecho = x2 <= self.cursor_x <= x2 + tolerancia and y1 - tolerancia <= self.cursor_y <= y2 + tolerancia
            borde_arriba = x1 - tolerancia <= self.cursor_x <= x2 + tolerancia and y1 - tolerancia <= self.cursor_y <= y1 
            borde_abajo = x1 - tolerancia <= self.cursor_x <= x2 + tolerancia and y2 <= self.cursor_y <= y2 + tolerancia
            if borde_izquierdo or borde_derecho or borde_arriba or borde_abajo:
                return True
            else:
                return False

    def _cambiar_cursor_a_puntero_dedo(self):
        self.master.config(cursor="hand2")

    def _cambiar_cursor_a_puntero_manito(self):
        self.master.config(cursor="hand1")

    def _cambiar_cursor_a_puntero_eliminacion(self):
        self.master.config(cursor="X_cursor")

    def _revertir_cursor_a_defecto(self):
        self.master.config(cursor="")

    def _puntero_en_zona_vacia(self):
        for tarjeta in self.tarjetas_mensaje:
            x1, y1, x2, y2 = self.bbox(tarjeta.rect_id)
            mouse_en_tarjeta = x1 <= self.cursor_x <= x2 and y1<=self.cursor_y <= y2
            if mouse_en_tarjeta:
                return False
        return True

#--------------------------------------------de conexión al bot-------------------------------------
    def _solicitar_datos_de_mensaje(self, id_mensaje):
        return self.interfaz_padre._solicitar_datos_de_mensaje(id_mensaje)

    def _conectar_tarjetas_por_id(self, id_padre, id_hijo):
        for tarjeta in self.tarjetas_mensaje:
            if id_padre == tarjeta.id_mensaje:
                tarjeta_padre = tarjeta
            elif id_hijo == tarjeta.id_mensaje:
                tarjeta_hijo = tarjeta

        self.conectar_tarjetas_por_flecha(tarjeta_padre, tarjeta_hijo)

#-------------------------------------------------tarjetas de mensaje --------------------------------------------------

class TarjetaDeMensaje:
    def __init__(self, canvas, x, y, datos_mensaje,  **kwargs):
        self.canvas = canvas
        self.texto = datos_mensaje['contenidos'][0]
        self.ancho_tarjeta = 100 * self.canvas.escala_zoom
        self.alto_tarjeta = 100 * self.canvas.escala_zoom
        self.margen = 10 * self.canvas.escala_zoom
        self.rect_id = canvas.create_rectangle(x, y, x + self.ancho_tarjeta, y + self.alto_tarjeta, fill="#d9cead", width=0)

        # texto:
        self.ancho_texto =  self.ancho_tarjeta - (self.margen*2)# Ancho neto máximo permitido para el texto
        self.alto_texto = self.alto_tarjeta - (self.margen*2) # alto neto máximo para el texto
        texto_origen_x = x + self.margen
        texto_origen_y = y + self.margen 
        self.tamano_texto = 8* self.canvas.escala_zoom
        self.text_id = canvas.create_text(texto_origen_x, texto_origen_y, text="", font = ("TkDefaultFont", round(self.tamano_texto)), anchor="nw",  **kwargs)
        self.establecer_previsualizacion_texto(self.texto)
        self.canvas.itemconfig(self.text_id, state='disabled')

        #bindings
        self.canvas.tag_bind(self.rect_id, "<ButtonPress-1>", self.iniciar_arrastre)
        self.canvas.tag_bind(self.rect_id, "<B1-Motion>", self.arrastre)
        self.canvas.tag_bind(self.rect_id, "<ButtonRelease-1>", self.mostrar_configuracion_mensaje)
        self.datos_arrastre = {"x": 0, "y": 0}
        self.se_realizo_arrastre = False  # Variable para controlar si se realizó un arrastre

        #datos del mensaje 
        self.datos_mensaje = datos_mensaje
        self.id_mensaje = int(datos_mensaje['id_mensaje'])

    def establecer_previsualizacion_texto(self, texto):
        #horrible pero bueno. No encontré otra manera para que no se desborde el texto de la tarjeta.
        caracteres_por_linea = 11 #arbitrario por tipografía y tamañp tarjeta
        lineas_por_tarjeta = 7 #arbitrario por tipografía y tamaño tarjeta
        previsualizacion = ""

        palabras = texto.split()
    
        caracteres_actuales = 0
        linea_actual = 1 
    
        # Itera sobre cada palabra en el texto
        for palabra in palabras:
            # Calcula la longitud de la palabra y agrega un espacio
            longitud_palabra = len(palabra)
        
            # Si agregar la palabra no excede el límite de caracteres por línea
            if caracteres_actuales + longitud_palabra +1 <= caracteres_por_linea:
                previsualizacion += palabra + " "
                caracteres_actuales += longitud_palabra + 1 #+1 por el espacio
            # Si la palabra no entra en la linea
            elif linea_actual<=lineas_por_tarjeta:
                if longitud_palabra <= caracteres_por_linea:#si solamente no tiene espacio en la actual 
                    previsualizacion += "\n"
                    linea_actual+= 1
                    caracteres_actuales = longitud_palabra +1 #+1 por el espacio
                    previsualizacion += palabra + " "
                else:#si nunca va entrar en ninguna 
                    restante = palabra[caracteres_por_linea-caracteres_actuales:]
                    palabras.insert(palabras.index(palabra) + 1,restante) 
                    palabra = palabra[:caracteres_por_linea-caracteres_actuales]
                    previsualizacion += palabra + '\n' 
                    linea_actual+=1
                    caracteres_actuales = 0
                # Si ya se alcanzó el límite de líneas por tarjeta, detén la iteración
            else:
                break
            
        # Configura el texto en el canvas
        self.canvas.itemconfig(self.text_id, text=previsualizacion)

    def actualizar_tamanio_texto_por_zoom(self, factor_de_escalado):
        self.tamano_texto = self.tamano_texto*factor_de_escalado 
        self.canvas.itemconfig(self.text_id, font=("TkDefaultFont", round(self.tamano_texto)))
        
    def iniciar_arrastre(self, evento):
        self.datos_arrastre["x"] = evento.x
        self.datos_arrastre["y"] = evento.y
        self.canvas._revertir_cursor_a_defecto()

    def arrastre(self, evento):
        self.se_realizo_arrastre = True  # Se establece a True cuando se realiza un arrastre
        rect_x, rect_y, rect_width, rect_height = self.canvas.coords(self.rect_id)
        rel_x = self.canvas.canvasx(evento.x)- rect_x # coordenadas relativas a la tarjeta
        rel_y = self.canvas.canvasy(evento.y) - rect_y # coordenadas relativas a la tarjeta
        ancho_tarjeta = rect_width-rect_x
        alto_tarjeta = rect_height-rect_y

        if 1 < rel_x < (ancho_tarjeta-1) and 1 < rel_y < (alto_tarjeta -1):
            # print(f"{time.time()}estoy dentro arrastrando")
            dx = evento.x - self.datos_arrastre["x"] #cambio en x
            dy = evento.y - self.datos_arrastre["y"] #cambio en y
            self.canvas.move(self.rect_id, dx, dy)
            self.canvas.move(self.text_id, dx, dy)
            if self in self.canvas.tarjeta_a_flechas: #si tiene flechas involucradas
                self.canvas.actualizar_posicion_flechas(self, dx, dy)

        self.datos_arrastre["x"] = evento.x
        self.datos_arrastre["y"] = evento.y

    def mostrar_configuracion_mensaje(self, evento):
        if hasattr(self.canvas, "interfaz_padre"): #si el pizarrón está dentro de la interfaz del bot:
            datos = self._solicitar_datos_de_mensaje(self.datos_mensaje["id_mensaje"])
            for clave, valor in datos.items():
                print(f"{clave}: {valor}")
            if not self.se_realizo_arrastre:  # Solo muestra el cartel si no se ha realizado un arrastre
                # Crear el cartel emergente
                popup = tk.Toplevel()
                popup.geometry("200x100+{}+{}".format(evento.x_root, evento.y_root))
                label = tk.Label(popup, text=self.datos_mensaje)
                label.pack(padx=10, pady=10)

            # Restablecer la variable para el siguiente evento
            self.se_realizo_arrastre = False
            
    def _solicitar_datos_de_mensaje(self, id_mensaje):
        return self.canvas._solicitar_datos_de_mensaje(id_mensaje)
    def eliminar_tarjeta(self):
        self.canvas.delete(self.rect_id)
        self.canvas.delete(self.text_id)

