import bot
import time

def main():
    b = bot.Bot("mensajes_automaticos.xml", "interacciones.json")
    # b.agregar_mensaje("hola")
    # b.agregar_disparador(1,"mensaje_principal")
    # b.agregar_mensaje("Este es un menu")
    # b.agregar_disparador(2, "texto", "local", "exacto", "1")
    # b.agregar_disparador(3, "texto", "local", "exacto", "2")
    # b.agregar_disparador(4, "texto", "local", "exacto", "3")
    # b.agregar_disparador(1, "texto", "local", "incluido", "chau")
    # b.definir_hijos(1, [2,3,4])
    # b.contestar("hola", 1)
    # b.contestar("3", 1)

    while True:
        entrada_usuario = input("usuario: ")
        b.contestar(entrada_usuario, 1)



main()