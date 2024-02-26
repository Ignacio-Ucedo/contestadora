def procesar_string(string, funcion, parametro):
    try:
        resultado_evaluado = string.format(funcion(parametro))
    except KeyError:
        resultado_evaluado = string
        
    return resultado_evaluado


def imprimir_datos(cantidad):
    return "dato 1 dato 2 dato 3"
string_original = "hola estos son los datos {0} estos fueron los  datos"
funcion_parametro = imprimir_datos
valor_parametro = 3

# Procesar el string
string_procesado = procesar_string(string_original, funcion_parametro, valor_parametro)
print(type(funcion_parametro))