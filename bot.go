package main

import (
	"encoding/xml"
	"fmt"
	"log"
	"os"

	"github.com/antchfx/xmlquery"
)

type Bot struct {
	EstadosConversacion map[int]int
	nodoMensajes        *xmlquery.Node
}

func CrearBot() *Bot {
	_, err := os.Stat("mensajesAutomaticos.xml")
	if os.IsNotExist(err) {
		data := Mensajes{
			Mensajes: []Mensaje{},
		}
		crearXML(data)
	}

	xmlFile, _ := os.Open("mensajesAutomaticos.xml")
	doc, err := xmlquery.Parse(xmlFile)
	if err != nil {
		log.Fatal("Error parseando el documento XML:", err)
	}
	contestadora := &Bot{
		EstadosConversacion: make(map[int]int),
		nodoMensajes:        doc,
	}

	return contestadora
}

func (b *Bot) contestar(mensaje string, id_conversacion int) {
	_, ok := b.EstadosConversacion[id_conversacion]
	if !ok {
		b.EstadosConversacion[id_conversacion] = 0

	}
	query := fmt.Sprintf("//mensaje[id=%s]/cuerpo", fmt.Sprint(b.EstadosConversacion[id_conversacion]))
	result := xmlquery.FindOne(b.nodoMensajes, query)
	str := result.InnerText()
	println(str)

	b.EstadosConversacion[id_conversacion] = 1
}

// Mensaje representa la estructura de un mensaje
type Mensaje struct {
	XMLName    xml.Name `xml:"mensaje"`
	ID_Estadio int      `xml:"id"`
	Cuerpo     string   `xml:"cuerpo"`
}

// Mensajes representa la estructura base con una lista de mensajes
type Mensajes struct {
	XMLName  xml.Name  `xml:"mensajes"`
	Mensajes []Mensaje `xml:"mensaje"`
}

func crearXML(mensajes Mensajes) error {

	xmlFile, err := os.Create("mensajesAutomaticos.xml")
	if err != nil {
		return err
	}
	defer xmlFile.Close()

	encoder := xml.NewEncoder(xmlFile)
	encoder.Indent("", "  ")

	err = encoder.Encode(mensajes)
	if err != nil {
		return err
	}

	return nil
}

func AniadirMensaje(contenido string, idEstadio int) {
	xmlFile, err := os.Open("mensajesAutomaticos.xml")
	if err != nil {
		fmt.Println("Error abriendo el archivo XML:", err)
		return
	}
	defer xmlFile.Close()

	var mensajes Mensajes
	decoder := xml.NewDecoder(xmlFile)
	err = decoder.Decode(&mensajes)
	if err != nil {
		fmt.Println("Error decodificando XML:", err)
		return
	}

	nuevoMensaje := Mensaje{ID_Estadio: idEstadio, Cuerpo: contenido}
	mensajes.Mensajes = append(mensajes.Mensajes, nuevoMensaje)

}

func main() {
	// b := CrearBot()
	// b.contestar("hola", 0)
	// b.contestar("hola", 0)

	xmlFile, _ := os.Open("prueba.xml")
	doc, err := xmlquery.Parse(xmlFile)
	if err != nil {
		log.Fatal("Error parseando el documento XML:", err)
	}
	query := "/musica/musicos/musico[(@id = /musica/bandas/banda/fechas[not(@disolucion)]/../integrantes/integrante/@id)]"
	result := xmlquery.FindOne(doc, query)
	// result = result.FirstChild
	fmt.Println(result.InnerText())

}
