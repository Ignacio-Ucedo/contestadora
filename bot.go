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
}

func CrearBot() *Bot {
	contestadora := &Bot{
		EstadosConversacion: make(map[int]int),
	}
	// // Crear estructura base de mensajes
	// data := Mensajes{
	// 	Mensajes: []Mensaje{},
	// }
	// escribirXML(data)
	return contestadora
}

func (b *Bot) contestar(mensaje string, id_conversacion int) {
	_, ok := b.EstadosConversacion[id_conversacion]
	xmlFile, err := os.Open("mensajesAutomaticos.xml")
	doc, err := xmlquery.Parse(xmlFile)
	if err != nil {
		log.Fatal("Error parseando el documento XML:", err)
	}
	query := "//mensaje[id=0]/cuerpo"
	result := xmlquery.FindOne(doc, query)

	if !ok {
		b.EstadosConversacion[id_conversacion] = 0
		str := result.InnerText()
		println(str)
	}
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

func escribirXML(mensajes Mensajes) error {

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

	// Guardar la estructura actualizada en el archivo XML
	err = escribirXML(mensajes)
}

func main() {
	b := CrearBot()
	b.contestar("hola", 0)
	// AniadirMensaje("asdfasdfasdf", 3)
	// AniadirMensaje("asdfasdfasdf", 3)
	// AniadirMensaje("asdfasdfasdf", 3)
	// AniadirMensaje("asdfasdfasdf", 3)
	// AniadirMensaje("asdfasdfasdf", 3)
	// AniadirMensaje("asdfasdfasdf", 3)
}
