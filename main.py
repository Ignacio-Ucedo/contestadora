import bot
import time

def main():
    b = bot.Bot()
    # b.agregar_o_modificar_mensaje(1,"asdfasdf\nasdfasdfa\nasfasdfs\nasdfasdfa\nasdfasfsdaf" )
    # b.agregar_disparador(1,"texto", "global")
    while True:
        entrada_usuario = input("usuario: ")
        b.contestar(entrada_usuario, 1)


main()