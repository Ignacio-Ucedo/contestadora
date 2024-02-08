import bot

def main():
    b = bot.Bot()
    b.agregar_mensaje("hola")
    b.agregar_disparador(0,"saludo")
    b.agregar_mensaje("Este es un menu")
    b.agregar_disparador(1, "texto", "local", "exacto", "hola")
    b.agregar_disparador(1, "texto", "local", "incluido", "chau")

main()