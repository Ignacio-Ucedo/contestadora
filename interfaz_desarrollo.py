import tkinter as tk
from tkinter import messagebox
from bot import Bot
from pizarron_interfaz import Pizarron
import time
import json

class InterfazDesarrollo:
    def __init__(self, master):
        self.master = master
        self.master.title("Entorno de pruebas")
        self.master.configure(bg="#333333")  
        self.master.geometry("1000x500")  # Establecer el tamaño inicial de la ventana
        self.bot = Bot()  
        self.bot.interfaz = self

        self.frame_contenedor = tk.PanedWindow(master, bg="#333333", orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED)
        self.frame_contenedor.pack(fill=tk.BOTH, expand=True)

        self.frame_mensajes = tk.Frame(self.frame_contenedor, bg="#1c1c1b")  # Ajustar el ancho aquí
        self.frame_contenedor.add(self.frame_mensajes, stretch="always")
        self.frame_contenedor.update_idletasks()  # Actualizar para que el frame se ajuste

        self.lbl_titulo_mensajes = tk.Label(self.frame_mensajes, text="Mensajes automáticos", font=("Helvetica", 18, "bold"), fg="white", bg="#333333")
        self.lbl_titulo_mensajes.pack(side=tk.TOP, pady=20)

        # Crear el pizarrón 
        self.pizarron = Pizarron(self.frame_mensajes, self)
        self.pizarron.pack(expand=True, fill="both", padx=20, pady=20)
        self.frame_chat= tk.Frame(self.frame_contenedor, bg="#333333")  
        self.frame_contenedor.add(self.frame_chat, stretch="always")

        self.lbl_titulo_chat = tk.Label(self.frame_chat, text="Chat", font=("Helvetica", 18, "bold"), fg="white", bg="#333333")
        self.lbl_titulo_chat.pack(side=tk.TOP, pady=20)

        self.btn_agregar_o_modificar_mensajes = tk.Button(self.frame_chat, text="Agregar o modificar mensaje", font=("Helvetica", 12), command=self.agregar_o_modificar_mensaje_desde_interfaz, bg="#666666", fg="white")

        self.btn_agregar_o_modificar_mensajes.pack(pady=10)

        self.chat = tk.Frame(self.frame_chat, bg="#333333", bd=0, padx=20, pady=20)  # Sin borde
        self.chat.pack(fill=tk.BOTH, expand=True)

        self.chat_texto = tk.Text(self.chat, font=("Helvetica", 12), height=2, bg="#222222", fg="white", spacing3=10, highlightbackground="#333333", bd=0, padx= 10, pady=10)  # Sin borde
        self.chat_texto.pack(expand=True, fill=tk.BOTH)
        self.chat_texto.configure(state="disabled")

        self.chat_texto.tag_configure("usuario", foreground="#7ad1ff")  
        self.chat_texto.tag_configure("bot", foreground="#e0937b")  

        self.input_frame = tk.Frame(self.chat, bg="#333333", bd=0)  # Sin borde
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10,0))  

        self.entrada_texto = tk.Text(self.input_frame, height=1, font=("Helvetica", 12), bg="#222222", fg="white", highlightbackground="#333333", padx=10, pady=10)
        self.entrada_texto.grid(row=0, column=0, sticky="ew")
        self.entrada_texto.bind("<Return>", self.enviar_mensaje_a_bot)
        self.entrada_texto.config(insertbackground="white")
        self.entrada_texto.focus_set()

        self.btn_enviar = tk.Button(self.input_frame, text="Enviar", font=("Helvetica", 12), command=self.enviar_mensaje_a_bot, bg="#7ad1ff", fg="black", bd=0)  # Sin borde
        self.btn_enviar.grid(row=0, column=1, padx= 10, sticky="e")

        self.input_frame.grid_columnconfigure(0, weight=1)  # Configurar la columna del marco de entrada para expandirse

        #--------------------------------------agregamiento de mensajes / carga del bot en la interfaz----------------------
        # self.cargar_mensajes_en_pizarron()


        self.master.bind("<Control-w>", self.cerrar_ventana)

    def agregar_o_modificar_mensaje_desde_interfaz(self):
        try:
            self.bot.agregar_o_modificar_mensaje()
            messagebox.showinfo("Info", "Mensaje agregado o modificado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar mensajes: {str(e)}")

    def contestar_iu_desarrollo(self, mensaje):
        timestamp = time.strftime("%H:%M:%S", time.localtime())  
        etiqueta = f"bot {timestamp}: "  
        self.chat_texto.configure(state="normal")
        self.chat_texto.insert("end", etiqueta , "bot") 
        self.chat_texto.insert("end", mensaje + '\n') 
        self.chat_texto.configure(state="disabled")
        self.chat_texto.see("end")  # Ajustar para mostrar el final del texto

    def enviar_mensaje_a_bot(self, event=None):
        self.master.after(1, self.procesar_entrada)  
        return 'break'  

    def procesar_entrada(self):
        texto_ingresado = self.entrada_texto.get("1.0", "end").strip()  
        if texto_ingresado:  
            timestamp = time.strftime("%H:%M:%S", time.localtime()) 
            etiqueta = f"usuario {timestamp}: "  
            self.chat_texto.configure(state="normal")
            self.chat_texto.insert("end", etiqueta , "usuario")   
            self.chat_texto.insert("end",texto_ingresado+ '\n')   
            self.chat_texto.configure(state="disabled")
            self.chat_texto.see("end")  # Ajustar para mostrar el final del texto
            self.bot.contestar(texto_ingresado, 0)
            self.entrada_texto.delete("1.0", "end")  
            self.entrada_texto.event_generate("<BackSpace>")  
    
    def cerrar_ventana(self, event):
        self.master.destroy()

#------------------------------------------------de conexión al bot------------------------
    def _solicitar_datos_de_mensaje(self, id_mensaje):
        return self.bot._datos_de_mensaje(id_mensaje)

    def cargar_mensajes_en_pizarron(self):
        cantidad_mensajes = self.bot.cantidad_mensajes
        #agregación de tarjetas
        for id_mensaje in range(cantidad_mensajes):
            datos_mensaje = self._solicitar_datos_de_mensaje(id_mensaje)
            self.pizarron.agregar_tarjeta_mensaje(25,25,datos_mensaje)

        #conexión de flechas
        for id_mensaje in range(cantidad_mensajes):
            datos_mensaje = self._solicitar_datos_de_mensaje(id_mensaje)
            if 'hijos' in datos_mensaje:
                hijos = json.loads(datos_mensaje['hijos'])
                for hijo in hijos:
                    self.pizarron._conectar_tarjetas_por_id(id_mensaje, hijo)

#------------------------------------------------------------------------------------------   
    @classmethod
    def ejecutar(cls):
        raiz = tk.Tk()
        raiz.configure(bg="#333333")  
        interfaz = cls(raiz)
        interfaz.cargar_mensajes_en_pizarron()
        raiz.mainloop()

