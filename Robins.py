import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List, Optional
from PIL import Image, ImageTk
# Intentar importar pygame para reproducción de audio (mp3). Si no está instalado, el juego seguirá funcionando sin audio.
# Usar importlib para evitar que linters/analizadores marquen la importación como no resuelta.
import importlib

pygame = None
PYGAME_AVAILABLE = False
try:
    pygame = importlib.import_module("pygame")
    PYGAME_AVAILABLE = True
except Exception:
    pygame = None
    PYGAME_AVAILABLE = False

# CLASES BASE (MANTIENEN LA LÓGICA ORIGINAL)

class Jugador:
    """Clase que representa al jugador y sus estadísticas"""
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.salud = 100
        self.reputacion = 50
        self.recursos = 3
        self.inventario = []
        self.decisiones = []
        self.nodo_actual = "inicio"

    def agregar_item(self, item: str):
        """Agregar un item al inventario"""
        if item not in self.inventario:
            self.inventario.append(item)

    def modificar_stat(self, stat: str, cambio: int):
        """Modificar una estadística del jugador"""
        if stat == "salud":
            self.salud = max(0, min(100, self.salud + cambio))
        elif stat == "reputacion":
            self.reputacion = max(0, min(100, self.reputacion + cambio))
        elif stat == "recursos":
            self.recursos = max(0, self.recursos + cambio)

    def guardar_decision(self, nodo: str, eleccion: str):
        """Guardar una decisión tomada"""
        self.decisiones.append({"nodo": nodo, "eleccion": eleccion})


class Personaje:
    """Clase para personajes no jugables (PNJ)"""
    def __init__(self, nombre: str, dialogo_inicial: str):
        self.nombre = nombre
        self.dialogo_inicial = dialogo_inicial
        self.dialogos = {}


class NodoHistoria:
    """Clase que representa un nodo de la historia"""
    def __init__(self, id: str, titulo: str, descripcion: str, imagen: str = ""):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.imagen = imagen
        self.opciones = []
        self.es_final = False

    def agregar_opcion(self, texto: str, nodo_siguiente: str,
                       stat: Optional[str] = None, cambio: int = 0,
                       stat2: Optional[str] = None, cambio2: int = 0,
                       item: Optional[str] = None):
        """Agregar una opción de decisión"""
        self.opciones.append({
            "texto": texto,
            "siguiente": nodo_siguiente,
            "stat": stat,
            "cambio": cambio,
            "stat2": stat2,
            "cambio2": cambio2,
            "item": item
        })

class JuegoAventuraBase:
    """Clase base con toda la lógica del juego (sin interfaz)"""
    def __init__(self):
        self.jugador = None
        self.dificultad = None
        self.historia = {}
        self.personajes = {}
        self.inicializar_personajes()
        self.inicializar_historias()
        self.inicializar_historias_nightwing()
        self.inicializar_historias_tim_drake()
        self.inicializar_historias_damian_wayne()


    def inicializar_personajes(self):
        """Crear los personajes del juego"""
        batman = Personaje("Batman", "La justicia de Gotham requiere más que fuerza bruta.")
        batman.dialogos = {
            "orgullo": "Estoy orgulloso de ti, Jason.",
            "decepcion": "Esperaba más de ti, Robin.",
            "preocupacion": "Ten cuidado ahí fuera.",
        }
        self.personajes["batman"] = batman

        alfred = Personaje("Alfred", "¿Té, Maestro Jason?")
        alfred.dialogos = {
            "consejo": "La diferencia entre un héroe y un villano a menudo es solo una decisión.",
        }
        self.personajes["alfred"] = alfred

        joker = Personaje("Joker", "¡Jajajaja! ¿Vino el pequeño pájaro a jugar?")
        self.personajes["joker"] = joker

######################################################################################################################################################33
    def inicializar_historias(self):
        """Crear todos los nodos de historia"""
        # MODO FÁCIL: EL SEGUNDO ROBIN (17 nodos)
        jason_inicio = NodoHistoria(
            "jason_facil_inicio",
            "CRIME ALLEY - EL ENCUENTRO",
            "Gotham City, hace años. Las calles oscuras de Crime Alley son tu hogar. "
            "Eres Jason Todd, un huérfano de 12 años que sobrevive robando para comer. "
            "Esta noche, mientras intentas robar las llantas del Batimóvil, una sombra "
            "se cierne sobre ti. Batman te observa, pero en sus ojos no ves ira, sino... "
            "¿curiosidad?",
            "crime_alley.png"
        )
        jason_inicio.agregar_opcion("Intentar huir corriendo", "jason_facil_huida", stat="recursos", cambio=-1)
        jason_inicio.agregar_opcion("Enfrentarlo con valentía", "jason_facil_confrontacion", stat="reputacion", cambio=10)
        jason_inicio.agregar_opcion("Explicar tu situación honestamente", "jason_facil_honestidad", stat="reputacion", cambio=15)
        self.historia["jason_facil_inicio"] = jason_inicio

        jason_huida = NodoHistoria(
            "jason_facil_huida",
            "LA PERSECUCIÓN",
            "Corres con todas tus fuerzas, pero Batman es demasiado rápido. Te alcanza en "
            "segundos, pero en lugar de entregarte a la policía, te ofrece comida y un lugar "
            "donde dormir. 'Tienes potencial,' dice. 'Pero estás desperdiciando tu valentía "
            "en las calles.'",
            "batman_chase.png"
        )
        jason_huida.agregar_opcion("Aceptar su ayuda con desconfianza", "jason_facil_entrenamiento", stat="recursos", cambio=2)
        jason_huida.agregar_opcion("Rechazar y seguir solo", "jason_facil_rechazo", stat="reputacion", cambio=-10)
        self.historia["jason_facil_huida"] = jason_huida

        jason_confrontacion = NodoHistoria(
            "jason_facil_confrontacion",
            "VALENTÍA RECONOCIDA",
            "Te plantas frente al Caballero Oscuro, llave inglesa en mano. Batman sonríe "
            "levemente bajo su capucha. 'No muchos tienen el coraje de enfrentarme,' dice. "
            "'Especialmente a tu edad. ¿Qué te parece si uso esa valentía para algo mejor?'",
            "jason_valiente.png"
        )
        jason_confrontacion.agregar_opcion("Aceptar inmediatamente", "jason_facil_entrenamiento", stat="reputacion", cambio=5)
        jason_confrontacion.agregar_opcion("Preguntar qué significa", "jason_facil_curiosidad", stat="recursos", cambio=1)
        self.historia["jason_facil_confrontacion"] = jason_confrontacion

        jason_honestidad = NodoHistoria(
            "jason_facil_honestidad",
            "LA VERDAD DUELE",
            "Le cuentas sobre tu madre adicta, sobre cómo murió, sobre las noches frías en "
            "las calles. Batman escucha en silencio. Cuando terminas, coloca una mano en tu "
            "hombro. 'Yo también perdí a mis padres aquí, en este mismo callejón. Déjame "
            "ayudarte a convertir tu dolor en propósito.'",
            "jason_triste.png"
        )
        jason_honestidad.agregar_opcion("Aceptar su propuesta", "jason_facil_entrenamiento",
                                  stat="reputacion", cambio=20, item="Esperanza Renovada")
        self.historia["jason_facil_honestidad"] = jason_honestidad

        jason_curiosidad = NodoHistoria(
            "jason_facil_curiosidad",
            "LAS PREGUNTAS CORRECTAS",
            "Batman te explica su misión: proteger Gotham de quienes lastiman a los inocentes. "
            "'Necesito un compañero,' dice. 'Alguien que entienda las calles como tú. ¿Estás "
            "listo para entrenar?' Tu corazón late con fuerza. Esta es tu oportunidad de cambiar "
            "todo.",
            "batman_explica.png"
        )
        jason_curiosidad.agregar_opcion("Aceptar con determinación", "jason_facil_entrenamiento", stat="reputacion", cambio=10)
        self.historia["jason_facil_curiosidad"] = jason_curiosidad

        jason_rechazo = NodoHistoria(
            "jason_facil_rechazo",
            "SOLO EN LAS CALLES",
            "Rechazas a Batman y sigues robando para sobrevivir. Meses después, mientras "
            "escapas de una pandilla, Batman aparece de nuevo. 'Última oportunidad, Jason. "
            "Puedes seguir sobreviviendo... o puedes vivir.' Esta vez, algo en ti ha cambiado.",
            "jason_solo.png"
        )
        jason_rechazo.agregar_opcion("Aceptar finalmente", "jason_facil_entrenamiento",
                               stat="salud", cambio=-20, stat2="recursos", cambio2=1)
        jason_rechazo.agregar_opcion("Rechazarlo definitivamente", "jason_facil_final_malo",
                               stat="reputacion", cambio=-30)
        self.historia["jason_facil_rechazo"] = jason_rechazo

        jason_entrenamiento = NodoHistoria(
            "jason_facil_entrenamiento",
            "LA CUEVA DEL MURCIÉLAGO",
            "La Batcueva te deja sin aliento. Tecnología avanzada, el Batimóvil, arsenales de "
            "equipo. Alfred, el mayordomo, te recibe con una sonrisa cálida y un plato de comida "
            "caliente. Los primeros meses son duros: entrenas combate, acrobacia, tecnología y "
            "detective work. Bruce es exigente pero paciente.",
            "batcave.png"
        )
        jason_entrenamiento.agregar_opcion("Enfocarte en combate cuerpo a cuerpo", "jason_facil_especialidad_combate",
                                      stat="salud", cambio=20, item="Técnicas de Combate")
        jason_entrenamiento.agregar_opcion("Estudiar tecnología y detectivismo", "jason_facil_especialidad_detective",
                                      stat="recursos", cambio=2, item="Kit de Detective")
        self.historia["jason_facil_entrenamiento"] = jason_entrenamiento

        jason_combate = NodoHistoria(
            "jason_facil_especialidad_combate",
            "EL GUERRERO NACE",
            "Te especializas en combate. Dick Grayson, el primer Robin, te visita para entrenar. "
            "'Eres más agresivo que yo,' observa. 'No es malo, pero recuerda: no se trata solo "
            "de ganar peleas.' Sus palabras resuenan mientras perfeccionas cada movimiento.",
            "entrenamiento_combate.png"
        )
        jason_combate.agregar_opcion("Continuar con el entrenamiento", "jason_facil_traje", stat="reputacion", cambio=10)
        self.historia["jason_facil_especialidad_combate"] = jason_combate

        jason_detective = NodoHistoria(
            "jason_facil_especialidad_detective",
            "LA MENTE DETECTIVESCA",
            "Pasas horas en el laboratorio de la Batcueva, estudiando ciencia forense, química "
            "y tecnología. Batman nota tu progreso: 'Tienes instinto natural para esto. Usas las "
            "calles de forma diferente a Dick. Eso es bueno.' Te sientes orgulloso.",
            "laboratorio.png"
        )
        jason_detective.agregar_opcion("Continuar preparándote", "jason_facil_traje", stat="recursos", cambio=2)
        self.historia["jason_facil_especialidad_detective"] = jason_detective

        jason_traje = NodoHistoria(
            "jason_facil_traje",
            "EL MOMENTO LLEGA",
            "Seis meses después, Batman te llama. Alfred sostiene un traje: rojo, amarillo y "
            "verde. El traje de Robin. 'No eres Dick Grayson,' dice Batman. 'Y no deberías serlo. "
            "Serás tu propio Robin. ¿Estás listo?' Tus manos tiemblan al tomar el traje.",
            "traje_robin.png"
        )
        jason_traje.agregar_opcion("Ponerte el traje con orgullo", "jason_facil_primera_mision",
                             stat="reputacion", cambio=25, item="Traje de Robin")
        self.historia["jason_facil_traje"] = jason_traje

        jason_primera_mision = NodoHistoria(
            "jason_facil_primera_mision",
            "PRIMERA NOCHE DE PATRULLA",
            "Las azoteas de Gotham se ven diferentes desde aquí arriba. El viento golpea tu capa "
            "mientras saltas junto a Batman. Tu comunicador crepita: robo en progreso en un banco. "
            "'Es tu decisión, Robin,' dice Batman. '¿Qué hacemos?'",
            "primera_patrulla.png"
        )
        jason_primera_mision.agregar_opcion("Entrada frontal y directa", "jason_facil_mision_directa", stat="salud", cambio=-10)
        jason_primera_mision.agregar_opcion("Infiltración silenciosa", "jason_facil_mision_sigilo", stat="recursos", cambio=1)
        self.historia["jason_facil_primera_mision"] = jason_primera_mision

        jason_mision_directa = NodoHistoria(
            "jason_facil_mision_directa",
            "GOLPE FRONTAL",
            "Rompes la puerta de una patada. Los criminales te disparan pero esquivas con las "
            "acrobacias que aprendiste. Batman entra detrás de ti, neutralizando amenazas. En "
            "minutos, todos están inconscientes. 'Efectivo,' dice Batman, 'pero ruidoso. Los "
            "rehenes estaban asustados.'",
            "accion_directa.png"
        )
        jason_mision_directa.agregar_opcion("Aprender de la experiencia", "jason_facil_crecimiento", stat="reputacion", cambio=5)
        self.historia["jason_facil_mision_directa"] = jason_mision_directa

        jason_mision_sigilo = NodoHistoria(
            "jason_facil_mision_sigilo",
            "SOMBRAS EN LA NOCHE",
            "Entras por el techo, moviéndote en silencio. Desactivas a cada criminal uno por uno "
            "desde las sombras. Los rehenes ni siquiera se dan cuenta de que los están rescatando "
            "hasta que todo termina. Batman asiente con aprobación: 'Bien hecho, Robin.'",
            "sigilo.png"
        )
        jason_mision_sigilo.agregar_opcion("Sentir el éxito", "jason_facil_crecimiento",
                                      stat="reputacion", cambio=15, item="Confianza de Batman")
        self.historia["jason_facil_mision_sigilo"] = jason_mision_sigilo

        jason_crecimiento = NodoHistoria(
            "jason_facil_crecimiento",
            "ROBIN, EL PROTECTOR",
            "Semanas se convierten en meses. Detienen a Dos Caras, Pingüino, Espantapájaros. "
            "Gotham comienza a conocer al nuevo Robin. Los periódicos hablan de ti. Eres más "
            "impulsivo que Dick, pero también más conectado con las calles. Una noche, una niña "
            "que rescataste te abraza llorando: 'Gracias, Robin.' En ese momento, sabes que "
            "encontraste tu propósito.",
            "robin_heroe.png"
        )
        jason_crecimiento.agregar_opcion("Continuar protegiendo Gotham", "jason_facil_final", stat="reputacion", cambio=20)
        self.historia["jason_facil_crecimiento"] = jason_crecimiento

        jason_final_facil = NodoHistoria(
            "jason_facil_final",
            "EL SEGUNDO ROBIN - FINAL",
            "Han pasado dos años. Ya no eres el niño asustado de Crime Alley. Eres Robin, "
            "compañero de Batman, protector de los inocentes. Batman te mira con orgullo en la "
            "Batcueva. 'No muchos podrían haber hecho lo que hiciste, Jason. Convertiste tu dolor "
            "en fuerza. Gotham es más segura contigo aquí.' Alfred coloca una mano en tu hombro. "
            "Esta es tu familia ahora. Este es tu hogar. Y tu historia... apenas comienza.",
            "final_robin.png"
        )
        jason_final_facil.es_final = True
        self.historia["jason_facil_final"] = jason_final_facil

        # NUEVO: Final malo - Jason rechaza ser Robin
        jason_final_malo = NodoHistoria(
            "jason_facil_final_malo",
            "EL LADRÓN DE GOTHAM - FINAL MALO",
            "Años pasan. Sigues en las calles, robando para sobrevivir. Te has vuelto más hábil, "
            "más peligroso, pero también más solo. Batman intentó salvarte, pero rechazaste su ayuda. "
            "Una noche, mientras huyes de la policía, ves a otro niño en Crime Alley, asustado y hambriento. "
            "Te recuerda a ti. Pero sigues corriendo. Esa fue tu elección. Gotham podría haber tenido un héroe, "
            "pero en su lugar, solo tiene otro criminal más. Tu historia termina donde comenzó: en la oscuridad.",
            "jason_ladron_final.png"
        )
        jason_final_malo.es_final = True
        self.historia["jason_facil_final_malo"] = jason_final_malo


        # MODO NORMAL: MUERTE EN LA FAMILIA (35 nodos extendidos)


        jason_inicio_normal = NodoHistoria(
            "jason_normal_inicio",
            "GOTHAM - DOS AÑOS DESPUÉS",
            "Eres Robin desde hace dos años. Has crecido más fuerte, más rápido, más letal. Pero "
            "últimamente, algo ha cambiado. Batman te ve demasiado violento, demasiado impulsivo. "
            "Acabas de romper el brazo de un criminal que suplicaba piedad. 'Jason, esto tiene que "
            "parar,' dice Batman. Pero él no entiende. No estuvo en las calles como tú.",
            "robin_oscuro.png"
        )
        jason_inicio_normal.agregar_opcion("Defender tus métodos", "jason_normal_defensa", stat="reputacion", cambio=-15)
        jason_inicio_normal.agregar_opcion("Prometer cambiar", "jason_normal_promesa", stat="reputacion", cambio=5)
        jason_inicio_normal.agregar_opcion("Ignorar a Batman", "jason_normal_rebelion", stat="reputacion", cambio=-25)
        self.historia["jason_normal_inicio"] = jason_inicio_normal

        # Rama 1: Defensa
        jason_defensa = NodoHistoria(
            "jason_normal_defensa",
            "EL ARGUMENTO",
            "'¡Ese tipo vendía drogas a niños!' gritas. 'La gente como él no merece piedad.' "
            "Batman te mira con decepción: 'Si cruzamos esa línea, nos convertimos en lo que "
            "combatimos.' Pero tú no estás seguro de estar de acuerdo.",
            "normal_argumento.png"
        )
        jason_defensa.agregar_opcion("Insistir en tu punto", "jason_normal_conflicto", stat="reputacion", cambio=-10)
        jason_defensa.agregar_opcion("Reflexionar sobre sus palabras", "jason_normal_reflexion", stat="reputacion", cambio=10)
        self.historia["jason_normal_defensa"] = jason_defensa

        # Rama 2: Promesa
        jason_promesa = NodoHistoria(
            "jason_normal_promesa",
            "INTENTANDO CAMBIAR",
            "Prometes ser menos brutal. Durante semanas lo intentas. Pero cada vez que ves a un criminal "
            "lastimar a alguien, algo dentro de ti hierve. Una noche, atrapas a un traficante golpeando "
            "a una niña. Tu puño se aprieta. Batman te observa desde las sombras.",
            "normal_promesa.png"
        )
        jason_promesa.agregar_opcion("Contenerte y arrestarlo", "jason_normal_contencion", stat="reputacion", cambio=15, stat2="salud", cambio2=-10)
        jason_promesa.agregar_opcion("Dejarte llevar por la ira", "jason_normal_ira", stat="reputacion", cambio=-20)
        self.historia["jason_normal_promesa"] = jason_promesa

        # Rama 3: Rebelión
        jason_rebelion = NodoHistoria(
            "jason_normal_rebelion",
            "EL CAMINO SOLITARIO",
            "Ignoras completamente a Batman. Sales de patrulla solo, usando métodos cada vez más violentos. "
            "Los criminales comienzan a temer al 'Robin Oscuro'. Pero algo se rompe entre tú y Bruce. "
            "Alfred intenta mediar, pero la brecha crece. Una noche, Batman te suspende temporalmente.",
            "normal_rebelion.png"
        )
        jason_rebelion.agregar_opcion("Aceptar la suspensión con resentimiento", "jason_normal_suspension", stat="reputacion", cambio=-15)
        jason_rebelion.agregar_opcion("Salir de patrulla de todos modos", "jason_normal_desobediencia", stat="salud", cambio=-20)
        self.historia["jason_normal_rebelion"] = jason_rebelion

        # Nodos de conflicto
        jason_conflicto = NodoHistoria(
            "jason_normal_conflicto",
            "LA RUPTURA",
            "La discusión escala. Batman te quita el traje de Robin temporalmente. 'Hasta que "
            "entiendas lo que significa este símbolo,' dice, señalando la 'R' en tu pecho. Te vas "
            "furioso a tu habitación. Esa noche, mientras no puedes dormir, recibes un mensaje "
            "encriptado en tu computadora.",
            "conflicto_batman.png"
        )
        jason_conflicto.agregar_opcion("Abrir el mensaje", "jason_normal_mensaje_joker", stat="recursos", cambio=-1)
        self.historia["jason_normal_conflicto"] = jason_conflicto

        jason_reflexion = NodoHistoria(
            "jason_normal_reflexion",
            "DUDAS INTERNAS",
            "Las palabras de Batman te persiguen. ¿Realmente estás ayudando a Gotham? ¿O estás usando "
            "la justicia como excusa para tu ira? Una noche, rescatas a un niño de una situación similar "
            "a la tuya hace años. Sus ojos aterrorizados te recuerdan quién eras. Quizás Batman tiene razón.",
            "normal_reflexion.png"
        )
        jason_reflexion.agregar_opcion("Hablar con Batman honestamente", "jason_normal_reconciliacion", stat="reputacion", cambio=20)
        jason_reflexion.agregar_opcion("Seguir luchando con tus demonios", "jason_normal_lucha_interna", stat="salud", cambio=-15)
        self.historia["jason_normal_reflexion"] = jason_reflexion

        jason_contencion = NodoHistoria(
            "jason_normal_contencion",
            "VICTORIA DOLOROSA",
            "Te contienes. Cada fibra de tu ser quiere golpearlo, pero lo arrestas sin violencia excesiva. "
            "La niña te agradece llorando. Batman se acerca: 'Sé lo difícil que fue eso, Jason. Estoy "
            "orgulloso de ti.' Pero la tensión en tu pecho no desaparece completamente.",
            "normal_contencion.png"
        )
        jason_contencion.agregar_opcion("Continuar mejorando", "jason_normal_progreso", stat="reputacion", cambio=15)
        self.historia["jason_normal_contencion"] = jason_contencion

        jason_ira = NodoHistoria(
            "jason_normal_ira",
            "EL MONSTRUO INTERIOR",
            "Lo golpeas. Una, dos, tres veces. Batman tiene que apartarte físicamente. 'Jason, ¡detente!' "
            "El criminal está asustado, sangrando. La niña que rescataste te mira con miedo. Batman "
            "te lleva de vuelta a la Batcueva en silencio. La decepción en su rostro es insoportable.",
            "normal_ira.png"
        )
        jason_ira.agregar_opcion("Disculparte sinceramente", "jason_normal_disculpa", stat="reputacion", cambio=-5)
        jason_ira.agregar_opcion("Justificar tus acciones", "jason_normal_justificacion", stat="reputacion", cambio=-25)
        self.historia["jason_normal_ira"] = jason_ira

        jason_suspension = NodoHistoria(
            "jason_normal_suspension",
            "TIEMPO PARA PENSAR",
            "Pasas días en la mansión, sin el traje. Dick Grayson viene a visitarte. 'Yo también tuve "
            "mis problemas con Bruce,' dice. 'Pero tienes que encontrar tu propio camino de ser Robin. "
            "No el de él, no el mío. El tuyo.' Sus palabras te dan algo en qué pensar.",
            "normal_suspension.png"
        )
        jason_suspension.agregar_opcion("Buscar tu identidad como héroe", "jason_normal_busqueda", stat="reputacion", cambio=10)
        self.historia["jason_normal_suspension"] = jason_suspension

        jason_desobediencia = NodoHistoria(
            "jason_normal_desobediencia",
            "ROBIN RENEGADO",
            "Sales esa noche de todos modos. Sin el respaldo de Batman, casi te matan enfrentando a una "
            "pandilla. Despiertas en la enfermería de la Batcueva. Alfred está ahí, con lágrimas en los ojos: "
            "'Casi te perdemos, muchacho.' Batman entra, su rostro es una máscara de control.",
            "normal_desobediencia.png"
        )
        jason_desobediencia.agregar_opcion("Reconocer tu error", "jason_normal_leccion_dura", stat="salud", cambio=-30, stat2="reputacion", cambio2=5)
        self.historia["jason_normal_desobediencia"] = jason_desobediencia

        jason_reconciliacion = NodoHistoria(
            "jason_normal_reconciliacion",
            "HONESTIDAD BRUTAL",
            "Hablas con Batman. Le cuentas sobre tu ira, tu miedo, tu sensación de no ser suficiente. "
            "Bruce se quita la capucha, y por primera vez en semanas, ves a Bruce Wayne, no a Batman. "
            "'Jason, tu pasión es tu fuerza, pero también tu debilidad. Juntos podemos canalizarla.' Se abrazan.",
            "normal_reconciliacion.png"
        )
        jason_reconciliacion.agregar_opcion("Entrenar juntos de nuevo", "jason_normal_nuevo_comienzo", stat="reputacion", cambio=25)
        self.historia["jason_normal_reconciliacion"] = jason_reconciliacion

        jason_lucha_interna = NodoHistoria(
            "jason_normal_lucha_interna",
            "EL PESO DEL MANTO",
            "Sigues patrullando, pero la duda te consume. Cada decisión es cuestionada. ¿Golpear o no golpear? "
            "¿Piedad o justicia? Una noche, enfrentando a un asaltante, dudas demasiado. Recibes un disparo en "
            "el hombro. Batman te salva, pero la herida es profunda, física y emocionalmente.",
            "normal_lucha_interna.png"
        )
        jason_lucha_interna.agregar_opcion("Recuperarte y buscar claridad", "jason_normal_recuperacion", stat="salud", cambio=-25)
        self.historia["jason_normal_lucha_interna"] = jason_lucha_interna

        jason_progreso = NodoHistoria(
            "jason_normal_progreso",
            "EL ROBIN EVOLUCIONADO",
            "Semanas de esfuerzo rinden frutos. Encuentras balance entre tu pasión y el control. Batman nota "
            "el cambio: 'Estás convirtiéndote en el héroe que siempre supe que podías ser.' Pero entonces, "
            "llega un mensaje encriptado a la Batcomputadora. Es sobre tu madre.",
            "normal_progreso.png"
        )
        jason_progreso.agregar_opcion("Investigar el mensaje juntos", "jason_normal_mensaje_conjunto", stat="recursos", cambio=1)
        self.historia["jason_normal_progreso"] = jason_progreso

        jason_disculpa = NodoHistoria(
            "jason_normal_disculpa",
            "PALABRAS SINCERAS",
            "'Lo siento, Bruce. Perdí el control.' Batman suspira profundamente. 'Jason, tu corazón está en "
            "el lugar correcto, pero tus métodos... necesitamos trabajar en esto juntos. Si no, alguien saldrá "
            "realmente lastimado algún día. Tal vez tú.' Te abraza. No todo está perdido.",
            "normal_disculpa.png"
        )
        jason_disculpa.agregar_opcion("Comprometerte a mejorar", "jason_normal_compromiso", stat="reputacion", cambio=10)
        self.historia["jason_normal_disculpa"] = jason_disculpa

        jason_justificacion = NodoHistoria(
            "jason_normal_justificacion",
            "LÍNEAS CRUZADAS",
            "'¡Él lo merecía!' gritas. Batman niega con la cabeza: 'Entonces ya no eres Robin. Ya no bajo "
            "mi protección.' Te quita el traje. Alfred protesta, pero Batman es firme. Sales de la Batcueva, "
            "solo. En tu habitación, encuentras un mensaje sobre tu madre en Etiopía.",
            "normal_justificacion.png"
        )
        jason_justificacion.agregar_opcion("Ir a Etiopía sin el traje", "jason_normal_etiopia_solo", stat="recursos", cambio=-3)
        self.historia["jason_normal_justificacion"] = jason_justificacion

        jason_busqueda = NodoHistoria(
            "jason_normal_busqueda",
            "REDEFINIENDO A ROBIN",
            "Estudias la historia de los Robins. Dick fue el acróbata, el líder nato. Tú eres diferente: más "
            "duro, más conectado con las calles, más dispuesto a hacer lo necesario. Quizás eso no es malo. "
            "Quizás Gotham necesita diferentes tipos de héroes. Batman te encuentra en la biblioteca: '¿Listo para volver?'",
            "normal_busqueda.png"
        )
        jason_busqueda.agregar_opcion("Volver con renovada determinación", "jason_normal_retorno", stat="reputacion", cambio=20)
        self.historia["jason_normal_busqueda"] = jason_busqueda

        jason_leccion_dura = NodoHistoria(
            "jason_normal_leccion_dura",
            "CASI FATAL",
            "'Lo siento,' murmuras. Batman se sienta junto a tu cama: 'Jason, casi te pierdo. No puedo... "
            "no puedo perder otro hijo.' Es la primera vez que le oyes decir 'hijo'. Alfred sonríe a través "
            "de sus lágrimas. Cuando te recuperes, las cosas serán diferentes. Mejor.",
            "normal_leccion_dura.png"
        )
        jason_leccion_dura.agregar_opcion("Sanar física y emocionalmente", "jason_normal_sanacion", stat="salud", cambio=20, stat2="reputacion", cambio2=15)
        self.historia["jason_normal_leccion_dura"] = jason_leccion_dura

        jason_nuevo_comienzo = NodoHistoria(
            "jason_normal_nuevo_comienzo",
            "MÁS FUERTES JUNTOS",
            "Los siguientes meses son los mejores desde que te convertiste en Robin. Trabajas en armonía con "
            "Batman. Tu agresividad canalizada, tu instinto de las calles combinado con su entrenamiento. Gotham "
            "nunca ha estado más segura. Pero la paz nunca dura en esta ciudad. Un mensaje llega sobre tu madre.",
            "normal_nuevo_comienzo.png"
        )
        jason_nuevo_comienzo.agregar_opcion("Investigar con Batman", "jason_normal_mensaje_conjunto", stat="reputacion", cambio=15)
        self.historia["jason_normal_nuevo_comienzo"] = jason_nuevo_comienzo

        jason_recuperacion = NodoHistoria(
            "jason_normal_recuperacion",
            "CICATRICES QUE SANAN",
            "Durante tu recuperación, hablas mucho con Alfred. Él te cuenta historias de Bruce joven, sus propias "
            "luchas con la ira y el dolor. 'Maestro Jason,' dice, 'la diferencia entre un héroe y un villano a "
            "menudo es solo una decisión. Una elección de levantarse cuando caemos.' Decides levantarte mejor.",
            "normal_recuperacion.png"
        )
        jason_recuperacion.agregar_opcion("Regresar al campo", "jason_normal_segunda_oportunidad", stat="salud", cambio=15, stat2="reputacion", cambio2=10)
        self.historia["jason_normal_recuperacion"] = jason_recuperacion

        jason_compromiso = NodoHistoria(
            "jason_normal_compromiso",
            "NUEVO PACTO",
            "Entrenas más duro que nunca. No solo físicamente, sino mentalmente. Meditación, control de ira, "
            "incluso terapia. Batman te apoya en cada paso. 'No se trata de eliminar tu fuego, Jason,' dice, "
            "'se trata de controlarlo.' Lentamente, encuentras balance. Pero llega un mensaje sobre tu madre.",
            "normal_compromiso.png"
        )
        jason_compromiso.agregar_opcion("Mostrarle el mensaje a Batman", "jason_normal_mensaje_conjunto", stat="recursos", cambio=1)
        self.historia["jason_normal_compromiso"] = jason_compromiso

        jason_retorno = NodoHistoria(
            "jason_normal_retorno",
            "ROBIN RENACE",
            "Vuelves a las calles con nueva determinación. Ya no eres el Robin que era solo rabia. Eres Robin "
            "que es pasión controlada, fuerza con propósito. Batman sonríe bajo su capucha cuando te ve en acción. "
            "'Bienvenido de vuelta, Robin.' Pero esa noche, llega un mensaje sobre tu madre en Etiopía.",
            "normal_retorno.png"
        )
        jason_retorno.agregar_opcion("Mostrar el mensaje a Batman inmediatamente", "jason_normal_mensaje_conjunto", stat="reputacion", cambio=10)
        self.historia["jason_normal_retorno"] = jason_retorno

        jason_sanacion = NodoHistoria(
            "jason_normal_sanacion",
            "MÁS FUERTE POR LAS HERIDAS",
            "Las cicatrices físicas sanan, pero las lecciones permanecen. Eres más cuidadoso ahora, pero no menos "
            "valiente. Más sabio, pero no menos apasionado. Batman te ve entrenar en la Batcueva: 'Casi te pierdo, "
            "Jason. Pero mira en quién te has convertido. Estoy orgulloso.' Entonces llega un mensaje encriptado.",
            "normal_sanacion.png"
        )
        jason_sanacion.agregar_opcion("Investigar con Batman", "jason_normal_mensaje_conjunto", stat="recursos", cambio=1)
        self.historia["jason_normal_sanacion"] = jason_sanacion

        jason_segunda_oportunidad = NodoHistoria(
            "jason_normal_segunda_oportunidad",
            "DE VUELTA EN ACCIÓN",
            "Tu primera noche de regreso, detienes a un grupo que asaltaba una farmacia. Pero esta vez, los arrestas "
            "sin violencia excesiva. Los empleados te agradecen. Batman observa desde un edificio: 'Bien hecho, Robin.' "
            "Sientes que finalmente encontraste tu camino. Pero entonces, el Joker escapa de Arkham con un mensaje para ti.",
            "normal_segunda_oportunidad.png"
        )
        jason_segunda_oportunidad.agregar_opcion("Investigar el mensaje del Joker", "jason_normal_mensaje_joker", stat="recursos", cambio=-1)
        self.historia["jason_normal_segunda_oportunidad"] = jason_segunda_oportunidad

        # El mensaje del Joker - punto de convergencia
        jason_mensaje_joker = NodoHistoria(
            "jason_normal_mensaje_joker",
            "EL ANZUELO",
            "El mensaje dice: 'Hola, pequeño pájaro. ¿Quieres saber quién mató realmente a tu "
            "madre? Tengo información. Ven a Etiopía. Solo tú. Si traes al murciélago, la "
            "información desaparece. - Un Amigo' Tu corazón late con fuerza. ¿Podría ser real?",
            "mensaje_joker.png"
        )
        jason_mensaje_joker.agregar_opcion("Decirle a Batman", "jason_normal_confianza", stat="reputacion", cambio=20)
        jason_mensaje_joker.agregar_opcion("Ir solo a Etiopía", "jason_normal_etiopia_solo", stat="recursos", cambio=-2)
        self.historia["jason_normal_mensaje_joker"] = jason_mensaje_joker

        jason_mensaje_conjunto = NodoHistoria(
            "jason_normal_mensaje_conjunto",
            "TRABAJO EN EQUIPO",
            "Investigan juntos. El mensaje menciona a tu madre. Batman encuentra pistas que llevan a Etiopía. "
            "'Podría ser el Joker,' advierte. 'Pero también podría ser información legítima. Iremos juntos. "
            "Si es una trampa, la enfrentaremos como equipo.' Preparas tu equipo.",
            "normal_mensaje_conjunto.png"
        )
        jason_mensaje_conjunto.agregar_opcion("Viajar a Etiopía con Batman", "jason_normal_preparacion_viaje", stat="recursos", cambio=2)
        self.historia["jason_normal_mensaje_conjunto"] = jason_mensaje_conjunto

        jason_preparacion_viaje = NodoHistoria(
            "jason_normal_preparacion_viaje",
            "LISTOS PARA LO PEOR",
            "Batman prepara contingencias. Rastreadores, comunicadores de emergencia, rutas de escape. 'Si algo sale mal,' "
            "dice, 'llamas de inmediato. Nada de heroísmos solitarios.' Asienten. En el avión, Batman coloca una mano en "
            "tu hombro: 'Pase lo que pase, saldremos de esto juntos.'",
            "normal_preparacion.png"
        )
        jason_preparacion_viaje.agregar_opcion("Llegar a Etiopía preparados", "jason_normal_etiopia_equipo", stat="reputacion", cambio=5)
        self.historia["jason_normal_preparacion_viaje"] = jason_preparacion_viaje

        jason_confianza = NodoHistoria(
            "jason_normal_confianza",
            "DECISIÓN CORRECTA",
            "Le muestras el mensaje a Batman. Él lo analiza: 'Es una trampa. Probablemente el "
            "Joker.' Tu sangre se congela. Batman asiente: 'Pero si hay una posibilidad de que la "
            "información sobre tu madre sea real... iremos juntos. Como equipo.'",
            "batman_jason.png"
        )
        jason_confianza.agregar_opcion("Viajar a Etiopía con Batman", "jason_normal_preparacion_viaje",
                                 stat="reputacion", cambio=15, item="Respaldo de Batman")
        self.historia["jason_normal_confianza"] = jason_confianza

        jason_etiopia_equipo = NodoHistoria(
            "jason_normal_etiopia_equipo",
            "BATMAN Y ROBIN EN ETIOPÍA",
            "Llegan juntos. Batman ha rastreado la señal a un complejo en las afueras. 'Mantén los ojos abiertos,' "
            "advierte. Entran sigilosamente. Dentro, encuentran evidencia de tráfico de armas, pero también... fotos "
            "de tu madre. Esto es más complicado de lo que pensaban. Entonces escuchas la risa del Joker.",
            "normal_etiopia_equipo.png"
        )
        jason_etiopia_equipo.agregar_opcion("Seguir el plan de Batman", "jason_normal_plan_batman", stat="reputacion", cambio=10)
        jason_etiopia_equipo.agregar_opcion("Ir hacia la risa impulsivamente", "jason_normal_impulso_peligroso", stat="salud", cambio=-30)
        self.historia["jason_normal_etiopia_equipo"] = jason_etiopia_equipo

        jason_plan_batman = NodoHistoria(
            "jason_normal_plan_batman",
            "DISCIPLINA BAJO PRESIÓN",
            "Sigues el plan de Batman. Se separan estratégicamente, cubriéndose mutuamente. Localizan al Joker en un "
            "laboratorio improvisado. Está preparando gas venenoso. 'Dos pájaros con una piedra,' ríe. Batman señala "
            "un plan de ataque. Trabajando juntos, tienen una oportunidad de salvarse y capturar al Joker.",
            "normal_plan_batman.png"
        )
        jason_plan_batman.agregar_opcion("Ejecutar el plan perfectamente", "jason_normal_final_salvado", stat="reputacion", cambio=20)
        self.historia["jason_normal_plan_batman"] = jason_plan_batman

        jason_impulso_peligroso = NodoHistoria(
            "jason_normal_impulso_peligroso",
            "EL ERROR CASI FATAL",
            "Ignoras a Batman y corres hacia la risa. 'Jason, ¡no!' grita Batman. Demasiado tarde. Caes en una trampa. "
            "Una red eléctrica te atrapa. El dolor es insoportable. Batman corre hacia ti, pero el Joker lo embosca. "
            "Ves a Batman pelear contra múltiples secuaces mientras pierdes la conciencia. Has puesto a ambos en grave peligro.",
            "normal_impulso_peligroso.png"
        )
        jason_impulso_peligroso.agregar_opcion("Despertar en la pesadilla", "jason_normal_consecuencias_graves", stat="salud", cambio=-40)
        self.historia["jason_normal_impulso_peligroso"] = jason_impulso_peligroso

        jason_consecuencias_graves = NodoHistoria(
            "jason_normal_consecuencias_graves",
            "PRECIO DEL IMPULSO",
            "Despiertas atado. El Joker está frente a ti. Batman está herido, también atado. 'Mira lo que hiciste, pajarito,' "
            "ríe el Joker. 'Por tu impulsividad, ahora ambos morirán.' Activa un temporizador de bomba. '5 minutos. ¿Puedes "
            "salvarlo? ¿O te salvarás a ti mismo?' Se va riendo. Batman te mira: 'Jason, cálmate. Podemos salir de esto.'",
            "normal_consecuencias_graves.png"
        )
        jason_consecuencias_graves.agregar_opcion("Trabajar con calma para liberarse", "jason_normal_escape_conjunto", stat="recursos", cambio=-2)
        jason_consecuencias_graves.agregar_opcion("Entrar en pánico e intentar liberarte solo", "jason_normal_final_batman_muere", stat="salud", cambio=-50)
        self.historia["jason_normal_consecuencias_graves"] = jason_consecuencias_graves

        jason_escape_conjunto = NodoHistoria(
            "jason_normal_escape_conjunto",
            "ESCAPE EN EQUIPO",
            "Trabajan juntos. Batman te guía para liberarte mientras él hace lo mismo. Con 2 minutos restantes, ambos están libres. "
            "Desactivan la bomba con 30 segundos de sobra. El Joker escapa, pero están vivos. Batman te mira: 'Aprendiste la lección. "
            "Eso es lo que importa.'",
            "normal_escape_conjunto.png"
        )
        jason_escape_conjunto.agregar_opcion("Regresar a Gotham más sabios", "jason_normal_final_salvado", stat="reputacion", cambio=25)
        self.historia["jason_normal_escape_conjunto"] = jason_escape_conjunto

        # Jason va solo a Etiopía
        jason_etiopia_solo = NodoHistoria(
            "jason_normal_etiopia_solo",
            "SOLO EN TIERRA EXTRANJERA",
            "Etiopía. El calor es sofocante. Sigues las coordenadas hasta un almacén abandonado. Tu instinto grita peligro, "
            "pero la posibilidad de respuestas sobre tu madre te impulsa. Entras. Es oscuro. Demasiado oscuro. Entonces, "
            "escuchas esa risa. Esa maldita risa. El Joker emerge de las sombras con una palanca.",
            "etiopia.png"
        )
        jason_etiopia_solo.agregar_opcion("Intentar escapar", "jason_normal_intento_escape", stat="salud", cambio=-30)
        jason_etiopia_solo.agregar_opcion("Enfrentarlo con valentía", "jason_normal_enfrentar_joker", stat="reputacion", cambio=-10)
        self.historia["jason_normal_etiopia_solo"] = jason_etiopia_solo

        jason_intento_escape = NodoHistoria(
            "jason_normal_intento_escape",
            "CORRIENDO POR TU VIDA",
            "Corres hacia la salida, pero el Joker ha bloqueado las puertas. Sus secuaces aparecen. Peleas valientemente, "
            "tumbas a varios, pero son demasiados. Un golpe en la cabeza te deja aturdido. Lo último que ves antes de perder "
            "la conciencia es la sonrisa grotesca del Joker acercándose con la palanca.",
            "normal_intento_escape.png"
        )
        jason_intento_escape.agregar_opcion("Despertar en el horror", "jason_normal_tortura", stat="salud", cambio=-30)
        self.historia["jason_normal_intento_escape"] = jason_intento_escape

        jason_enfrentar_joker = NodoHistoria(
            "jason_normal_enfrentar_joker",
            "ENFRENTANDO AL PAYASO",
            "'¡Joker!' gritas, lanzando un batarang. Él lo esquiva riéndose. 'Oh, qué valiente. Qué estúpido. Batsy te "
            "enseñó mejor que esto, ¿verdad?' Pelean. Eres bueno, pero él es impredecible y letal. Te hiere varias veces "
            "antes de que sus secuaces te sujeten. 'Ahora,' dice, 'comienza la verdadera diversión.'",
            "normal_enfrentar_joker.png"
        )
        jason_enfrentar_joker.agregar_opcion("Resistir", "jason_normal_tortura", stat="salud", cambio=-35)
        self.historia["jason_normal_enfrentar_joker"] = jason_enfrentar_joker

        jason_tortura = NodoHistoria(
            "jason_normal_tortura",
            "TORTURA PSICOLÓGICA",
            "El Joker te tortura, no solo físicamente sino mentalmente. Te muestra fotos falsas de Batman con un nuevo Robin. "
            "'Te reemplazó,' susurra. 'Eres descartable.' Sabes que miente, pero las dudas se cuelan. Horas, o quizás días, "
            "pasan. Mantienes tu cordura pensando en Alfred, en Bruce, en tu misión. Entonces, escuchas una explosión distante.",
            "normal_tortura.png"
        )
        jason_tortura.agregar_opcion("Esperar el rescate", "jason_normal_rescate_tardio", stat="salud", cambio=-20)
        self.historia["jason_normal_tortura"] = jason_tortura

        jason_rescate_tardio = NodoHistoria(
            "jason_normal_rescate_tardio",
            "DEMASIADO TARDE",
            "Batman irrumpe, pero el Joker ya activó las bombas. 'Elige, Batsy,' ríe. 'Tu hijo adoptivo o todos estos rehenes.' "
            "Batman te mira. Sabes lo que tienes que hacer. 'Salva a los rehenes, Bruce,' dices. 'Es lo que me enseñaste.' "
            "Batman duda, pero tú empujas el botón que libera a los rehenes. El edificio comienza a colapsar.",
            "normal_rescate_tardio.png"
        )
        jason_rescate_tardio.agregar_opcion("Aceptar tu destino", "jason_normal_final_tragico", stat="salud", cambio=-50)
        self.historia["jason_normal_rescate_tardio"] = jason_rescate_tardio

        # NUEVO: Final donde Batman muere
        jason_final_batman_muere = NodoHistoria(
            "jason_normal_final_batman_muere",
            "EL SACRIFICIO DEL CABALLERO OSCURO",
            "Entras en pánico, jalando tus ataduras violentamente. '¡Jason, espera!' grita Batman, pero no escuchas. "
            "En tu frenesí, activas accidentalmente una trampa secundaria. El techo comienza a colapsar. Batman se libera "
            "y te empuja fuera del área de impacto. Escombros caen sobre él. 'Bruce, ¡NO!' gritas. Corres hacia él, pero "
            "es demasiado tarde. Con su último aliento, dice: 'Protege... Gotham... hijo.' El edificio explota. Sobrevives, "
            "pero Batman no. Por tu impulsividad, Gotham perdió a su protector. Alfred te culpa. Dick te culpa. Tú te culpas. "
            "La culpa te consume. Gotham nunca te perdonará. Tú nunca te perdonarás.",
            "normal_batman_muere.png"
        )
        jason_final_batman_muere.es_final = True
        self.historia["jason_normal_final_batman_muere"] = jason_final_batman_muere

        # Finales del modo Normal
        jason_final_salvado = NodoHistoria(
            "jason_normal_final_salvado",
            "SALVADO A TIEMPO",
            "Batman y tú llegan juntos. Es una trampa del Joker, pero esta vez están preparados. Trabajan en perfecta "
            "sincronía, salvando rehenes y capturando al Joker. 'Hiciste lo correcto al confiar en mí,' dice Batman. "
            "'Siempre estaré aquí para ti, hijo.' Has aprendido que los héroes no tienen que estar solos. Regresan a "
            "Gotham, más fuertes como equipo. El Joker va a Arkham, y tú sigues siendo Robin, el protector de Gotham.",
            "final_salvado.png"
        )
        jason_final_salvado.es_final = True
        self.historia["jason_normal_final_salvado"] = jason_final_salvado

        jason_final_tragico = NodoHistoria(
            "jason_normal_final_tragico",
            "MUERTE EN LA FAMILIA - FINAL TRÁGICO",
            "El almacén explota. Batman llega segundos tarde. Entre los escombros, encuentra tu capa rota y manchada de "
            "sangre. El Joker ha ganado esta vez. Gotham llora la muerte de Robin. Pero algunas historias no terminan con "
            "la muerte... A veces, renacen en algo mucho más oscuro. La leyenda de Red Hood está por comenzar.",
            "final_tragico.png"
        )
        jason_final_tragico.es_final = True
        self.historia["jason_normal_final_tragico"] = jason_final_tragico


        # MODO DIFÍCIL: BAJO LA CAPUCHA ROJA (45+ nodos)


        jason_inicio_dificil = NodoHistoria(
            "jason_dificil_inicio",
            "EL REGRESO",
            "Años después de tu muerte. Has regresado de entre los muertos, resucitado por el Pozo de Lázaro. "
            "Ya no eres Jason Todd, el segundo Robin. Ahora eres Red Hood, y Gotham conocerá un tipo diferente de "
            "justicia. Batman cree que matar está mal. Tú aprendiste que a veces, es necesario.",
            "red_hood.png"
        )
        jason_inicio_dificil.agregar_opcion("Comenzar tu campaña contra el crimen", "jason_dificil_primera_victima", stat="reputacion", cambio=-20)
        jason_inicio_dificil.agregar_opcion("Buscar primero al Joker", "jason_dificil_buscar_joker", stat="salud", cambio=-10)
        jason_inicio_dificil.agregar_opcion("Confrontar a Batman primero", "jason_dificil_confrontacion_temprana", stat="reputacion", cambio=10)
        self.historia["jason_dificil_inicio"] = jason_inicio_dificil

        # Rama 1: Campaña contra el crimen
        jason_primera_victima = NodoHistoria(
            "jason_dificil_primera_victima",
            "LA PRIMERA VÍCTIMA",
            "Tu primera noche como Red Hood. Encuentras a un traficante de drogas vendiendo a niños. Lo acorralas en un "
            "callejón. 'Por favor, no me mates,' suplica. Tu dedo está en el gatillo. Esta es la línea que Batman nunca "
            "cruzó. ¿La cruzarás tú?",
            "dificil_primera_victima.png"
        )
        jason_primera_victima.agregar_opcion("Matarlo - enviar un mensaje", "jason_dificil_camino_oscuro", stat="reputacion", cambio=-30, stat2="recursos", cambio2=1)
        jason_primera_victima.agregar_opcion("Dejarlo inconsciente con una advertencia", "jason_dificil_camino_intermedio", stat="reputacion", cambio=-10)
        jason_primera_victima.agregar_opcion("Entregarlo a la policía", "jason_dificil_camino_luz", stat="reputacion", cambio=5)
        self.historia["jason_dificil_primera_victima"] = jason_primera_victima

        # Rama 2: Buscar al Joker
        jason_buscar_joker = NodoHistoria(
            "jason_dificil_buscar_joker",
            "LA OBSESIÓN",
            "Pasas semanas rastreando al Joker. Interrogas brutalmente a sus secuaces. Algunos hablan, otros no sobreviven. "
            "Cada pista te lleva más profundo en la locura de Gotham. Finalmente, encuentras su escondite actual: un viejo "
            "teatro abandonado. Entras solo, armado hasta los dientes.",
            "dificil_buscar_joker.png"
        )
        jason_buscar_joker.agregar_opcion("Entrar silenciosamente", "jason_dificil_infiltracion_teatro", stat="recursos", cambio=1)
        jason_buscar_joker.agregar_opcion("Entrada explosiva", "jason_dificil_entrada_explosiva", stat="salud", cambio=-15)
        self.historia["jason_dificil_buscar_joker"] = jason_buscar_joker

        # Rama 3: Confrontación temprana con Batman
        jason_confrontacion_temprana = NodoHistoria(
            "jason_dificil_confrontacion_temprana",
            "CARA A CARA - PRIMERA VEZ",
            "Te presentas en la Batcueva. Alfred casi se desmaya. Batman está en shock. Te quitas el casco lentamente. "
            "'Hola, Bruce,' dices. 'Sorpresa. No estoy muerto.' Batman se acerca, las lágrimas amenazan con salir. "
            "'Jason... ¿cómo?' 'Esa es una larga historia,' respondes. 'Y no toda feliz.'",
            "dificil_confrontacion_temprana.png"
        )
        jason_confrontacion_temprana.agregar_opcion("Contarle toda la verdad", "jason_dificil_verdad_completa", stat="reputacion", cambio=15)
        jason_confrontacion_temprana.agregar_opcion("Culparlo por tu muerte", "jason_dificil_culpar_batman", stat="reputacion", cambio=-20)
        jason_confrontacion_temprana.agregar_opcion("Irte sin explicaciones", "jason_dificil_partir_sin_palabras", stat="recursos", cambio=-1)
        self.historia["jason_dificil_confrontacion_temprana"] = jason_confrontacion_temprana

        # Desarrollo Rama 1: Camino oscuro
        jason_camino_oscuro = NodoHistoria(
            "jason_dificil_camino_oscuro",
            "EL EJECUTOR",
            "Aprietas el gatillo. El traficante cae. No sientes remordimiento. Dejas su cuerpo como mensaje: un casco rojo "
            "pintado en la pared con su sangre. 'Red Hood protege estos barrios ahora.' En días, el crimen violento en esa "
            "zona cae un 80%. Pero los criminales pequeños huyen aterrorizados. ¿Es esto justicia o terrorismo?",
            "dificil_camino_oscuro.png"
        )
        jason_camino_oscuro.agregar_opcion("Continuar la campaña letal", "jason_dificil_caza_jefes", stat="reputacion", cambio=-25, item="Reputación Temible")
        jason_camino_oscuro.agregar_opcion("Reconsiderar tus métodos", "jason_dificil_duda_oscura", stat="salud", cambio=-10)
        self.historia["jason_dificil_camino_oscuro"] = jason_camino_oscuro

        jason_camino_intermedio = NodoHistoria(
            "jason_dificil_camino_intermedio",
            "EL VIGILANTE GRIS",
            "Lo golpeas hasta dejarlo inconsciente. Le rompes las piernas. 'Nunca más venderás drogas,' dicas. Lo dejas "
            "para que la policía lo encuentre con una nota: 'Red Hood estuvo aquí.' No lo mataste, pero tampoco lo perdonaste. "
            "Caminas en la línea gris entre héroe y villano.",
            "dificil_camino_intermedio.png"
        )
        jason_camino_intermedio.agregar_opcion("Mantener este balance", "jason_dificil_equilibrio_gris", stat="reputacion", cambio=-5)
        jason_camino_intermedio.agregar_opcion("Ser más brutal", "jason_dificil_caza_jefes", stat="reputacion", cambio=-15)
        self.historia["jason_dificil_camino_intermedio"] = jason_camino_intermedio

        jason_camino_luz = NodoHistoria(
            "jason_dificil_camino_luz",
            "EL REDENTOR",
            "Lo entregas a la policía. Algunos cops te miran con sospecha, otros con gratitud. 'Red Hood, ¿eh?' dice un "
            "detective. 'Esperamos que seas diferente a los otros vigilantes.' Sales en silencio. Tal vez puedes ser "
            "Red Hood sin convertirte en lo que odias.",
            "dificil_camino_luz.png"
        )
        jason_camino_luz.agregar_opcion("Mantener este código", "jason_dificil_heroe_oscuro", stat="reputacion", cambio=10)
        self.historia["jason_dificil_camino_luz"] = jason_camino_luz

        # Desarrollo Rama 2: Teatro del Joker
        jason_infiltracion_teatro = NodoHistoria(
            "jason_dificil_infiltracion_teatro",
            "INFILTRACIÓN SILENCIOSA",
            "Entras por el techo. El teatro está lleno de trampas del Joker. Desactivas algunas, esquivas otras. Finalmente "
            "llegas al escenario principal. El Joker está ahí, de espaldas, pintando algo. 'Sabía que vendrías, pajarito,' "
            "dice sin voltear. 'O debería decir... Capucha Roja?'",
            "dificil_infiltracion_teatro.png"
        )
        jason_infiltracion_teatro.agregar_opcion("Dispararle en la espalda", "jason_dificil_disparo_traicionero", stat="reputacion", cambio=-30)
        jason_infiltracion_teatro.agregar_opcion("Enfrentarlo cara a cara", "jason_dificil_duelo_joker", stat="salud", cambio=-10)
        self.historia["jason_dificil_infiltracion_teatro"] = jason_infiltracion_teatro

        jason_entrada_explosiva = NodoHistoria(
            "jason_dificil_entrada_explosiva",
            "GOLPE DRAMÁTICO",
            "Lanzas granadas por las ventanas y entras mientras explotan. Los secuaces del Joker corren en pánico. El Joker "
            "aplaude desde el balcón. '¡Qué entrada! ¡Dramática! Me gusta.' Salta hacia ti. Comienza el caos.",
            "dificil_entrada_explosiva.png"
        )
        jason_entrada_explosiva.agregar_opcion("Pelear sin restricciones", "jason_dificil_pelea_brutal_joker", stat="salud", cambio=-20)
        self.historia["jason_dificil_entrada_explosiva"] = jason_entrada_explosiva

        # Desarrollo Rama 3: Confrontaciones con Batman
        jason_verdad_completa = NodoHistoria(
            "jason_dificil_verdad_completa",
            "LA HISTORIA COMPLETA",
            "Le cuentas todo. El Pozo de Lázaro, Ra's al Ghul, la locura temporal, el entrenamiento con Talia. Batman escucha "
            "en silencio. Cuando terminas, dice: 'Jason, siento no haberte salvado. Cada día desde entonces ha sido un infierno.' "
            "'No pudiste salvarme, Bruce. Pero puedes ayudarme ahora con el Joker.'",
            "dificil_verdad_completa.png"
        )
        jason_verdad_completa.agregar_opcion("Pedir su ayuda contra el Joker", "jason_dificil_alianza_batman", stat="reputacion", cambio=20)
        jason_verdad_completa.agregar_opcion("Pedirle que no interfiera", "jason_dificil_camino_solo_advertencia", stat="recursos", cambio=1)
        self.historia["jason_dificil_verdad_completa"] = jason_verdad_completa

        jason_culpar_batman = NodoHistoria(
            "jason_dificil_culpar_batman",
            "LA CULPA Y LA IRA",
            "'¡Me dejaste morir!' gritas. 'El Joker me mató y tú no hiciste nada. ¡Todavía respira!' Batman baja la cabeza. "
            "'No hay un día que no me arrepienta. Pero matar al Joker no te traerá paz.' 'No busco paz,' respondes. 'Busco "
            "justicia.' 'Eso es venganza,' dice Batman. 'Y no puedo permitirlo.'",
            "dificil_culpar_batman.png"
        )
        jason_culpar_batman.agregar_opcion("Declarar que lo harás de todos modos", "jason_dificil_ruptura_total", stat="reputacion", cambio=-25)
        jason_culpar_batman.agregar_opcion("Escuchar sus razones", "jason_dificil_debate_filosofico", stat="recursos", cambio=1)
        self.historia["jason_dificil_culpar_batman"] = jason_culpar_batman

        jason_partir_sin_palabras = NodoHistoria(
            "jason_dificil_partir_sin_palabras",
            "EL SILENCIO HABLA",
            "Te pones el casco y sales. 'Jason, espera,' grita Batman. No miras atrás. Alfred te alcanza en la salida. "
            "'Maestro Jason, por favor. Bruce te necesita. Gotham te necesita.' 'Gotham tendrá a Red Hood,' respondes. "
            "'No sé si eso es mejor o peor que Robin.'",
            "dificil_partir_sin_palabras.png"
        )
        jason_partir_sin_palabras.agregar_opcion("Continuar solo", "jason_dificil_campana_solitaria", stat="recursos", cambio=-2)
        self.historia["jason_dificil_partir_sin_palabras"] = jason_partir_sin_palabras

        # Continuación Rama 1: Caza de jefes del crimen
        jason_caza_jefes = NodoHistoria(
            "jason_dificil_caza_jefes",
            "CAZANDO PECES GORDOS",
            "Subes en la cadena. Black Mask, Pingüino, Dos Caras. Uno por uno, los confrontas. Algunos negocian, otros pelean. "
            "Todos aprenden a temer el casco rojo. Gotham cambia. El crimen organizado está aterrorizado. Pero Batman nota "
            "tu campaña. Es solo cuestión de tiempo antes de que te encuentre.",
            "dificil_caza_jefes.png"
        )
        jason_caza_jefes.agregar_opcion("Prepararte para enfrentar a Batman", "jason_dificil_preparar_encuentro", stat="recursos", cambio=2)
        jason_caza_jefes.agregar_opcion("Acelerar tu plan antes de que intervenga", "jason_dificil_acelerar_plan", stat="salud", cambio=-15)
        self.historia["jason_dificil_caza_jefes"] = jason_caza_jefes

        jason_duda_oscura = NodoHistoria(
            "jason_dificil_duda_oscura",
            "DUDAS EN LA OSCURIDAD",
            "Una noche, después de matar a otro criminal, ves a un niño mirándote con terror. Te recuerda a ti mismo de niño. "
            "'¿Eres un héroe o un monstruo?' pregunta. No tienes respuesta. Esa pregunta te persigue durante días. Quizás "
            "cruzaste demasiadas líneas. Quizás Batman tenía razón.",
            "dificil_duda_oscura.png"
        )
        jason_duda_oscura.agregar_opcion("Buscar redención", "jason_dificil_buscar_redencion", stat="reputacion", cambio=15)
        jason_duda_oscura.agregar_opcion("Ignorar las dudas y continuar", "jason_dificil_suprimir_dudas", stat="reputacion", cambio=-10)
        self.historia["jason_dificil_duda_oscura"] = jason_duda_oscura

        jason_equilibrio_gris = NodoHistoria(
            "jason_dificil_equilibrio_gris",
            "CAMINANDO LA LÍNEA",
            "Mantienes tu código: no matar a menos que sea absolutamente necesario, pero no mostrar piedad con los que lastiman "
            "inocentes. Gotham comienza a entenderte. No eres Batman, pero tampoco eres un villano. Eres algo nuevo. Algo "
            "que Gotham necesitaba pero no sabía que quería.",
            "dificil_equilibrio_gris.png"
        )
        jason_equilibrio_gris.agregar_opcion("Fortalecer tu código", "jason_dificil_codigo_propio", stat="reputacion", cambio=10, item="Código de Red Hood")
        jason_equilibrio_gris.agregar_opcion("Enfocarte en el Joker", "jason_dificil_enfoque_joker", stat="recursos", cambio=1)
        self.historia["jason_dificil_equilibrio_gris"] = jason_equilibrio_gris

        jason_heroe_oscuro = NodoHistoria(
            "jason_dificil_heroe_oscuro",
            "EL HÉROE QUE GOTHAM MERECE",
            "Proteges sin matar. Eres más brutal que Batman, pero mantienes la línea. Los criminales te temen, pero los "
            "inocentes te agradecen. Una noche, una madre te abraza después de que salvas a su hijo. 'Gracias, Red Hood.' "
            "Tal vez puedes ser el héroe que Jason Todd siempre quiso ser.",
            "dificil_heroe_oscuro.png"
        )
        jason_heroe_oscuro.agregar_opcion("Continuar este camino", "jason_dificil_heroe_redencion", stat="reputacion", cambio=20)
        jason_heroe_oscuro.agregar_opcion("Aún necesitas enfrentar al Joker", "jason_dificil_buscar_joker_redentor", stat="recursos", cambio=1)
        self.historia["jason_dificil_heroe_oscuro"] = jason_heroe_oscuro

        # Joker confrontaciones
        jason_disparo_traicionero = NodoHistoria(
            "jason_dificil_disparo_traicionero",
            "EL DISPARO SIN HONOR",
            "Disparas. El Joker cae... pero es un maniquí. 'Tsk, tsk,' dice su voz por los altavoces. 'Esperaba más de ti, "
            "Jason. Dispararme por la espalda? Qué decepción.' Gas venenoso comienza a llenar la habitación. Fue una trampa "
            "desde el principio.",
            "dificil_disparo_traicionero.png"
        )
        jason_disparo_traicionero.agregar_opcion("Buscar la salida rápidamente", "jason_dificil_escape_gas", stat="salud", cambio=-20)
        jason_disparo_traicionero.agregar_opcion("Buscar al Joker real", "jason_dificil_buscar_joker_gas", stat="salud", cambio=-30)
        self.historia["jason_dificil_disparo_traicionero"] = jason_disparo_traicionero

        jason_duelo_joker = NodoHistoria(
            "jason_dificil_duelo_joker",
            "CARA A CARA CON EL PAYASO",
            "El Joker se voltea. Su sonrisa se ensancha al verte. 'Jason Todd. Mi obra maestra. ¿Te gusta lo que te hice? "
            "Te convertí en... esto.' Señala tu casco rojo. 'Ya no eres el niño que maté. Eres algo mejor. Algo como yo.' "
            "'No soy nada como tú,' gruñes.",
            "dificil_duelo_joker.png"
        )
        jason_duelo_joker.agregar_opcion("Dispararle ahora", "jason_dificil_disparar_joker", stat="reputacion", cambio=-20)
        jason_duelo_joker.agregar_opcion("Llevarlo con Batman", "jason_dificil_capturar_joker", stat="reputacion", cambio=15)
        jason_duelo_joker.agregar_opcion("Golpearlo hasta casi matarlo", "jason_dificil_golpear_joker", stat="salud", cambio=-10)
        self.historia["jason_dificil_duelo_joker"] = jason_duelo_joker

        jason_pelea_brutal_joker = NodoHistoria(
            "jason_dificil_pelea_brutal_joker",
            "CAOS ABSOLUTO",
            "La pelea es brutal. El Joker usa gas, explosivos, cuchillos. Tú usas armas, puños, y rabia pura. El teatro "
            "se derrumba a su alrededor mientras pelean. Finalmente, lo tienes en el suelo, tu pistola apuntando a su cabeza. "
            "'Hazlo,' ríe. 'Demuestra que tenía razón sobre ti.'",
            "dificil_pelea_brutal_joker.png"
        )
        jason_pelea_brutal_joker.agregar_opcion("Matarlo y terminar con esto", "jason_dificil_matar_joker", stat="reputacion", cambio=-40)
        jason_pelea_brutal_joker.agregar_opcion("Perdonarle la vida", "jason_dificil_perdonar_joker", stat="reputacion", cambio=25)
        self.historia["jason_dificil_pelea_brutal_joker"] = jason_pelea_brutal_joker

        # Alianzas y conflictos con Batman
        jason_alianza_batman = NodoHistoria(
            "jason_dificil_alianza_batman",
            "ALIADOS INCÓMODOS",
            "Batman acepta ayudarte, pero con condiciones. 'No matar,' dice. 'Si trabajamos juntos, seguimos mis reglas.' "
            "'Tus reglas me fallaron una vez,' respondes. 'Lo sé,' admite. 'Pero son las únicas que tengo.' Forman una "
            "alianza incómoda para enfrentar al Joker.",
            "dificil_alianza_batman.png"
        )
        jason_alianza_batman.agregar_opcion("Aceptar sus términos por ahora", "jason_dificil_colaboracion", stat="reputacion", cambio=15)
        jason_alianza_batman.agregar_opcion("Tener un plan secreto", "jason_dificil_plan_secreto", stat="recursos", cambio=2)
        self.historia["jason_dificil_alianza_batman"] = jason_alianza_batman

        jason_camino_solo_advertencia = NodoHistoria(
            "jason_dificil_camino_solo_advertencia",
            "ADVIRTIENDO A BATMAN",
            "'No interfieras, Bruce,' dicas. 'El Joker es mío.' Batman niega con la cabeza. 'No puedo prometerte eso. "
            "Si vas a matarlo, tendré que detenerte.' 'Entonces estaremos en lados opuestos,' respondes. La tensión es "
            "palpable. El conflicto es inevitable.",
            "dificil_camino_solo_advertencia.png"
        )
        jason_camino_solo_advertencia.agregar_opcion("Prepararte para enfrentar a ambos", "jason_dificil_preparar_doble_conflicto", stat="recursos", cambio=2)
        self.historia["jason_dificil_camino_solo_advertencia"] = jason_camino_solo_advertencia

        jason_ruptura_total = NodoHistoria(
            "jason_dificil_ruptura_total",
            "LA SEPARACIÓN DEFINITIVA",
            "'Entonces somos enemigos,' dice Batman. 'Si es necesario,' respondes. 'No por mucho tiempo,' dice. 'Te detendré "
            "antes de que cruces esa línea.' Sales de la Batcueva sabiendo que la próxima vez que se encuentren, será como "
            "adversarios. El hijo contra el padre. Red Hood contra Batman.",
            "dificil_ruptura_total.png"
        )
        jason_ruptura_total.agregar_opcion("Continuar tu misión solo", "jason_dificil_campana_solitaria", stat="reputacion", cambio=-20)
        self.historia["jason_dificil_ruptura_total"] = jason_ruptura_total

        jason_debate_filosofico = NodoHistoria(
            "jason_dificil_debate_filosofico",
            "EL DEBATE ÉTICO",
            "Batman te explica su filosofía: 'Si mato al Joker, ¿dónde termina? ¿Qué me detiene de matar al siguiente? Y al "
            "siguiente? La línea existe por una razón.' Tú contraargumentas: 'Cuántas vidas más tiene que tomar el Joker antes "
            "de que tu línea importe menos que sus víctimas?' Ninguno convence al otro, pero entienden las perspectivas mutuas.",
            "dificil_debate_filosofico.png"
        )
        jason_debate_filosofico.agregar_opcion("Acordar estar en desacuerdo", "jason_dificil_acuerdo_desacuerdo", stat="reputacion", cambio=5)
        jason_debate_filosofico.agregar_opcion("Intentar convencerlo de tu forma", "jason_dificil_convencer_batman", stat="recursos", cambio=-1)
        self.historia["jason_dificil_debate_filosofico"] = jason_debate_filosofico

        # Desarrollos intermedios
        jason_preparar_encuentro = NodoHistoria(
            "jason_dificil_preparar_encuentro",
            "PREPARACIÓN TÁCTICA",
            "Sabes que Batman vendrá. Preparas contramedidas: trampas EMP para sus gadgets, rutas de escape, distracciones. "
            "No quieres lastimarlo, pero tampoco dejarás que te detenga. Una noche, mientras vigilas desde una azotea, "
            "sientes su presencia detrás de ti.",
            "dificil_preparar_encuentro.png"
        )
        jason_preparar_encuentro.agregar_opcion("Voltear y hablar", "jason_dificil_dialogo_azotea", stat="reputacion", cambio=5)
        jason_preparar_encuentro.agregar_opcion("Activar tu trampa de escape", "jason_dificil_escape_batman", stat="recursos", cambio=-1)
        self.historia["jason_dificil_preparar_encuentro"] = jason_preparar_encuentro

        jason_acelerar_plan = NodoHistoria(
            "jason_dificil_acelerar_plan",
            "ACELERANDO EL PLAN",
            "Decides acelerar. Golpeas tres operaciones criminales en una noche. Es descuidado, pero efectivo. Obtienes "
            "información sobre el paradero del Joker. Pero también te lastimas en el proceso. Batman llega justo cuando "
            "terminas con el último grupo. 'Jason, detente,' dice. 'Esto no eres tú.'",
            "dificil_acelerar_plan.png"
        )
        jason_acelerar_plan.agregar_opcion("Ignorarlo y seguir", "jason_dificil_ignorar_batman", stat="salud", cambio=-15)
        jason_acelerar_plan.agregar_opcion("Enfrentarlo ahora", "jason_dificil_duelo_batman", stat="reputacion", cambio=-10)
        self.historia["jason_dificil_acelerar_plan"] = jason_acelerar_plan

        jason_buscar_redencion = NodoHistoria(
            "jason_dificil_buscar_redencion",
            "BUSCANDO REDENCIÓN",
            "Decides cambiar. No más matar. Puedes ser Red Hood sin ser un asesino. Empiezas a trabajar con refugios para "
            "niños de la calle, proteges tu territorio sin matar. Batman nota el cambio. Una noche, aparece a tu lado en "
            "una azotea. 'Escuché que cambiaste tus métodos,' dice. 'Estoy intentándolo,' respondes.",
            "dificil_buscar_redencion.png"
        )
        jason_buscar_redencion.agregar_opcion("Pedir su guía", "jason_dificil_pedir_guia", stat="reputacion", cambio=25)
        jason_buscar_redencion.agregar_opcion("Seguir tu propio camino", "jason_dificil_redencion_solitaria", stat="recursos", cambio=1)
        self.historia["jason_dificil_buscar_redencion"] = jason_buscar_redencion

        jason_suprimir_dudas = NodoHistoria(
            "jason_dificil_suprimir_dudas",
            "SUPRIMIENDO LA HUMANIDAD",
            "Entierras las dudas profundamente. El casco rojo se vuelve tu identidad completa. Jason Todd está muerto. Solo "
            "queda Red Hood. Tus métodos se vuelven más fríos, más calculados. Efectivos, pero sin alma. Batman te rastrea "
            "con más urgencia. Te estás convirtiendo en lo que ambos juraron destruir.",
            "dificil_suprimir_dudas.png"
        )
        jason_suprimir_dudas.agregar_opcion("Continuar descendiendo", "jason_dificil_descenso_oscuridad", stat="reputacion", cambio=-30)
        self.historia["jason_dificil_suprimir_dudas"] = jason_suprimir_dudas

        jason_codigo_propio = NodoHistoria(
            "jason_dificil_codigo_propio",
            "EL CÓDIGO DE RED HOOD",
            "Formalizas tu código: Proteger a los inocentes. No matar a menos que no haya otra opción. Castigar a los que "
            "lastiman a los débiles. No es el código de Batman, pero es tuyo. Gotham comienza a respetarte. Incluso algunos "
            "cops trabajan contigo discretamente. Eres un antihéroe, pero un héroe al fin.",
            "dificil_codigo_propio.png"
        )
        jason_codigo_propio.agregar_opcion("Encontrar a Batman para mostrárselo", "jason_dificil_mostrar_codigo", stat="reputacion", cambio=15)
        jason_codigo_propio.agregar_opcion("Seguir operando independientemente", "jason_dificil_operacion_independiente", stat="recursos", cambio=2)
        self.historia["jason_dificil_codigo_propio"] = jason_codigo_propio

        jason_enfoque_joker = NodoHistoria(
            "jason_dificil_enfoque_joker",
            "OBSESIÓN RENOVADA",
            "Con tu código establecido, vuelves tu atención al Joker. Es la última pieza del rompecabezas. Rastrear al Joker "
            "consume tus días y noches. Finalmente, obtienes una pista: estará en los muelles esta noche moviendo químicos. "
            "Es tu oportunidad.",
            "dificil_enfoque_joker.png"
        )
        jason_enfoque_joker.agregar_opcion("Ir solo a los muelles", "jason_dificil_muelles_solo", stat="recursos", cambio=-1)
        jason_enfoque_joker.agregar_opcion("Informar a Batman primero", "jason_dificil_muelles_equipo", stat="reputacion", cambio=10)
        self.historia["jason_dificil_enfoque_joker"] = jason_enfoque_joker

        jason_buscar_joker_redentor = NodoHistoria(
            "jason_dificil_buscar_joker_redentor",
            "LA PRUEBA FINAL",
            "Has demostrado que puedes ser un héroe. Pero el Joker sigue libre. Es tu prueba final: ¿Podrás enfrentarlo sin "
            "caer en la oscuridad? Rastrear al Joker te lleva a Arkham Asylum. Ha orquestado un motín. Los lunáticos corren "
            "libres. Batman está lidiando con otros villanos. El Joker está en el centro, esperándote.",
            "dificil_buscar_joker_redentor.png"
        )
        jason_buscar_joker_redentor.agregar_opcion("Enfrentarlo solo", "jason_dificil_arkham_solo", stat="salud", cambio=-15)
        jason_buscar_joker_redentor.agregar_opcion("Esperar backup de Batman", "jason_dificil_arkham_equipo", stat="recursos", cambio=1)
        self.historia["jason_dificil_buscar_joker_redentor"] = jason_buscar_joker_redentor

        # Más confrontaciones y desarrollo
        jason_campana_solitaria = NodoHistoria(
            "jason_dificil_campana_solitaria",
            "EL LOBO SOLITARIO",
            "Operas completamente solo. Sin Batman, sin aliados. Solo tú contra el inframundo de Gotham. Es duro, solitario, "
            "peligroso. Pero también liberador. No respondes a nadie. Tus métodos, tus reglas. Pero la soledad comienza a "
            "pesarte. Incluso Red Hood necesita aliados.",
            "dificil_campana_solitaria.png"
        )
        jason_campana_solitaria.agregar_opcion("Buscar aliados inesperados", "jason_dificil_aliados_inesperados", stat="recursos", cambio=2)
        jason_campana_solitaria.agregar_opcion("Continuar solo hasta el final", "jason_dificil_solo_final", stat="reputacion", cambio=-15)
        self.historia["jason_dificil_campana_solitaria"] = jason_campana_solitaria

        jason_escape_gas = NodoHistoria(
            "jason_dificil_escape_gas",
            "ESCAPE POR POCO",
            "Corres hacia las ventanas, disparándoles. El gas te alcanza parcialmente. Toses violentamente mientras escapas "
            "al aire libre. El Joker escapa en el caos. Maldices. Casi lo tenías. Pero aprendiste algo: no puedes subestimarlo. "
            "Necesitas un mejor plan.",
            "dificil_escape_gas.png"
        )
        jason_escape_gas.agregar_opcion("Reagruparse y planear mejor", "jason_dificil_replanear", stat="salud", cambio=-15, stat2="recursos", cambio2=1)
        self.historia["jason_dificil_escape_gas"] = jason_escape_gas

        jason_buscar_joker_gas = NodoHistoria(
            "jason_dificil_buscar_joker_gas",
            "CORRIENDO EN EL VENENO",
            "Aguantas la respiración y buscas al Joker real. Lo encuentras escapando por una salida trasera. Lo persigues "
            "a través del gas. Tu visión se nubla, pero lo alcanzas. Lo tackleas. Ambos caen rodando. Cuando el gas se disipa, "
            "estás sobre él, tu pistola en su cara.",
            "dificil_buscar_joker_gas.png"
        )
        jason_buscar_joker_gas.agregar_opcion("Dispararle ahora", "jason_dificil_matar_joker", stat="salud", cambio=-25, stat2="reputacion", cambio2=-35)
        jason_buscar_joker_gas.agregar_opcion("Arrestarlo", "jason_dificil_arrestar_joker_teatro", stat="salud", cambio=-20, stat2="reputacion", cambio2=20)
        self.historia["jason_dificil_buscar_joker_gas"] = jason_buscar_joker_gas

        jason_disparar_joker = NodoHistoria(
            "jason_dificil_disparar_joker",
            "EL DISPARO DECISIVO",
            "Apuntas. Tu dedo está en el gatillo. El Joker sonríe. 'Hazlo. Sabes que quieres.' Batman's voz resuena en tu "
            "cabeza: 'Si lo matas, nunca podrás volver.' Tu dedo tiembla. Este es el momento que define quién eres realmente.",
            "dificil_disparar_joker.png"
        )
        jason_disparar_joker.agregar_opcion("Apretar el gatillo", "jason_dificil_matar_joker", stat="reputacion", cambio=-40)
        jason_disparar_joker.agregar_opcion("Bajar el arma", "jason_dificil_perdonar_joker", stat="reputacion", cambio=30)
        self.historia["jason_dificil_disparar_joker"] = jason_disparar_joker

        jason_capturar_joker = NodoHistoria(
            "jason_dificil_capturar_joker",
            "LA CAPTURA",
            "Lo golpeas, lo atas, lo amordazas. 'Te llevo con Batman,' dices. El Joker se ríe a través de la mordaza. Lo arrastras "
            "fuera del teatro. Batman llega justo cuando sales. Ve al Joker atado. Te mira sorprendido. 'Lo capturaste.' "
            "'No lo maté,' respondes. 'Eso significa algo, ¿verdad?'",
            "dificil_capturar_joker.png"
        )
        jason_capturar_joker.agregar_opcion("Entregárselo a Batman", "jason_dificil_entregar_joker", stat="reputacion", cambio=35)
        self.historia["jason_dificil_capturar_joker"] = jason_capturar_joker

        jason_golpear_joker = NodoHistoria(
            "jason_dificil_golpear_joker",
            "GOLPEÁNDOLO SIN PIEDAD",
            "Lo golpeas. Una y otra vez. Años de ira salen con cada puñetazo. El Joker ríe, luego tose sangre, luego apenas "
            "respira. Finalmente te detienes. Está vivo, apenas. Batman llega corriendo. 'Jason, ¡para!' Ya paraste. El Joker "
            "está destrozado pero respira. '¿Suficiente?' preguntas.",
            "dificil_golpear_joker.png"
        )
        jason_golpear_joker.agregar_opcion("Dejarlo así", "jason_dificil_dejar_vivo", stat="reputacion", cambio=10)
        jason_golpear_joker.agregar_opcion("Un último golpe fatal", "jason_dificil_golpe_final", stat="reputacion", cambio=-35)
        self.historia["jason_dificil_golpear_joker"] = jason_golpear_joker

        # Más ramificaciones
        jason_colaboracion = NodoHistoria(
            "jason_dificil_colaboracion",
            "TRABAJANDO JUNTOS",
            "Durante semanas, trabajan juntos. Es incómodo. Batman cuestiona tus métodos, tú cuestionas su indulgencia. Pero "
            "funcionan. Desmantelan operaciones criminales, salvan vidas. Poco a poco, reconstruyen confianza. Una noche, "
            "Batman dice: 'Estás haciendo un buen trabajo, Jason.' Es lo más cerca de un cumplido que obtendrás.",
            "dificil_colaboracion.png"
        )
        jason_colaboracion.agregar_opcion("Fortalecer la alianza", "jason_dificil_alianza_fuerte", stat="reputacion", cambio=20)
        jason_colaboracion.agregar_opcion("Mantenerse independiente", "jason_dificil_mantener_distancia", stat="recursos", cambio=1)
        self.historia["jason_dificil_colaboracion"] = jason_colaboracion

        jason_plan_secreto = NodoHistoria(
            "jason_dificil_plan_secreto",
            "EL PLAN OCULTO",
            "Trabajas con Batman, pero tienes tu propio plan. Si el Joker escapa de nuevo, lo matarás sin importar lo que Batman "
            "diga. Guardas un arma especial, munición especial, solo para él. Batman no sabe. Mejor así. La lealtad tiene límites.",
            "dificil_plan_secreto.png"
        )
        jason_plan_secreto.agregar_opcion("Esperar el momento correcto", "jason_dificil_momento_correcto", stat="recursos", cambio=2)
        self.historia["jason_dificil_plan_secreto"] = jason_plan_secreto

        jason_preparar_doble_conflicto = NodoHistoria(
            "jason_dificil_preparar_doble_conflicto",
            "CONTRA DOS ENEMIGOS",
            "Te preparas para enfrentar tanto al Joker como a Batman. Necesitas ser más inteligente que ambos. Estableces trampas, "
            "contingencias, rutas de escape. El showdown final se acerca. Una noche recibes un mensaje: el Joker tiene rehenes "
            "en un almacén. Es ahora o nunca.",
            "dificil_preparar_doble_conflicto.png"
        )
        jason_preparar_doble_conflicto.agregar_opcion("Ir al almacén", "jason_dificil_almacen_trampa", stat="recursos", cambio=-2)
        self.historia["jason_dificil_preparar_doble_conflicto"] = jason_preparar_doble_conflicto

        jason_acuerdo_desacuerdo = NodoHistoria(
            "jason_dificil_acuerdo_desacuerdo",
            "RESPETO MUTUO",
            "'Nunca estaremos de acuerdo en esto,' dice Batman. 'No,' respondes. 'Pero te respeto.' 'Y yo a ti,' admite. "
            "'Solo... no cruces esa línea, Jason. Por favor.' 'No puedo prometerlo,' dices honestamente. 'Lo sé,' responde tristemente.",
            "dificil_acuerdo_desacuerdo.png"
        )
        jason_acuerdo_desacuerdo.agregar_opcion("Mantener el respeto mutuo", "jason_dificil_respeto_mantenido", stat="reputacion", cambio=10)
        self.historia["jason_dificil_acuerdo_desacuerdo"] = jason_acuerdo_desacuerdo

        jason_convencer_batman = NodoHistoria(
            "jason_dificil_convencer_batman",
            "INTENTO DE PERSUASIÓN",
            "Intentas convencer a Batman con lógica, con emociones, con ejemplos. Pero es inamovible. 'He visto muchos héroes "
            "caer por matar una vez,' dice. 'No dejaré que seas uno de ellos.' No lo convences. Pero él tampoco te convence "
            "a ti. El impasse continúa.",
            "dificil_convencer_batman.png"
        )
        jason_convencer_batman.agregar_opcion("Aceptar que no cambiarán", "jason_dificil_aceptar_diferencias", stat="recursos", cambio=1)
        self.historia["jason_dificil_convencer_batman"] = jason_convencer_batman

        jason_dialogo_azotea = NodoHistoria(
            "jason_dificil_dialogo_azotea",
            "CONVERSACIÓN EN LAS ALTURAS",
            "Te volteas. Batman está ahí, sin amenazar. 'Vine a hablar, no a pelear,' dice. Ambos se sientan al borde de la azotea. "
            "Por un momento, no son Red Hood y Batman. Son Jason y Bruce. 'Te extrañé,' admite Bruce. 'Yo también,' respondes. "
            "La tensión se disuelve, aunque sea temporalmente.",
            "dificil_dialogo_azotea.png"
        )
        jason_dialogo_azotea.agregar_opcion("Abrirse emocionalmente", "jason_dificil_apertura_emocional", stat="reputacion", cambio=20)
        jason_dialogo_azotea.agregar_opcion("Mantener distancia emocional", "jason_dificil_distancia_emocional", stat="recursos", cambio=1)
        self.historia["jason_dificil_dialogo_azotea"] = jason_dialogo_azotea

        jason_escape_batman = NodoHistoria(
            "jason_dificil_escape_batman",
            "LA HUIDA PLANEADA",
            "Activas tu trampa: bombas de humo, señuelos holográficos, granadas EMP. En el caos, escapas. Batman te persigue pero "
            "pierdes tu rastro. 'Jason,' su voz suena triste por el comunicador que dejaste. 'No tiene que ser así.' Pero ya te fuiste.",
            "dificil_escape_batman.png"
        )
        jason_escape_batman.agregar_opcion("Continuar evitándolo", "jason_dificil_evasion_continua", stat="recursos", cambio=-1)
        self.historia["jason_dificil_escape_batman"] = jason_escape_batman

        jason_ignorar_batman = NodoHistoria(
            "jason_dificil_ignorar_batman",
            "PASANDO DE LARGO",
            "Lo ignoras completamente y saltas a la siguiente azotea. 'Jason, espera,' grita. No esperas. Él te persigue. La "
            "persecución se intensifica. Finalmente te alcanza y te bloquea. 'Tenemos que hablar,' dice firmemente. Ya no puedes huir.",
            "dificil_ignorar_batman.png"
        )
        jason_ignorar_batman.agregar_opcion("Pelear contra él", "jason_dificil_duelo_batman", stat="salud", cambio=-20)
        jason_ignorar_batman.agregar_opcion("Escuchar lo que tiene que decir", "jason_dificil_escuchar_batman", stat="reputacion", cambio=5)
        self.historia["jason_dificil_ignorar_batman"] = jason_ignorar_batman

        jason_duelo_batman = NodoHistoria(
            "jason_dificil_duelo_batman",
            "HIJO CONTRA PADRE",
            "Pelean en las azoteas de Gotham. Conoces sus movimientos, él conoce los tuyos. Es doloroso para ambos. Cada golpe "
            "duele más emocionalmente que físicamente. 'No quiero pelear contigo,' dice Batman esquivando. 'Entonces no interfieras,' "
            "respondes lanzando un gancho. La pelea termina en empate, ambos exhaustos. 'Esto no resuelve nada,' dice Batman.",
            "dificil_duelo.png"
        )
        jason_duelo_batman.agregar_opcion("Aceptar su ayuda", "jason_dificil_final_redencion", stat="reputacion", cambio=25)
        jason_duelo_batman.agregar_opcion("Rechazarlo y seguir solo", "jason_dificil_final_antiheroico", stat="reputacion", cambio=-10)
        self.historia["jason_dificil_duelo_batman"] = jason_duelo_batman

        jason_pedir_guia = NodoHistoria(
            "jason_dificil_pedir_guia",
            "PIDIENDO AYUDA",
            "'Bruce... necesito ayuda,' admites. Es lo más difícil que has dicho. Batman sonríe. 'Siempre la tuviste, Jason. "
            "Solo tenías que pedirla.' Comienzan a trabajar juntos. Él te guía sin controlarte. Respeta tu independencia pero "
            "ofrece consejo. Lentamente, reconstruyen su relación.",
            "dificil_pedir_guia.png"
        )
        jason_pedir_guia.agregar_opcion("Trabajar juntos contra el Joker", "jason_dificil_equipo_joker", stat="reputacion", cambio=20)
        self.historia["jason_dificil_pedir_guia"] = jason_pedir_guia

        jason_redencion_solitaria = NodoHistoria(
            "jason_dificil_redencion_solitaria",
            "REDENCIÓN EN SOLEDAD",
            "'Aprecio el gesto,' dices, 'pero necesito hacer esto a mi manera.' Batman asiente. 'Entiendo. Pero si me necesitas, "
            "estaré aquí.' Se va. Continúas tu camino de redención solo. Es más difícil, pero se siente más auténtico. Este es "
            "tu viaje, nadie más.",
            "dificil_redencion_solitaria.png"
        )
        jason_redencion_solitaria.agregar_opcion("Continuar mejorando", "jason_dificil_heroe_redencion", stat="reputacion", cambio=15)
        self.historia["jason_dificil_redencion_solitaria"] = jason_redencion_solitaria

        jason_descenso_oscuridad = NodoHistoria(
            "jason_dificil_descenso_oscuridad",
            "DESCENDIENDO AL ABISMO",
            "Te vuelves más frío, más cruel. Red Hood se convierte en una leyenda de terror. Incluso los héroes te evitan. "
            "Batman intenta detenerte repetidamente. Cada encuentro se vuelve más violento. Estás perdiendo tu humanidad. "
            "Una noche, después de matar a varios criminales, ves tu reflejo. Casi no te reconoces.",
            "dificil_descenso_oscuridad.png"
        )
        jason_descenso_oscuridad.agregar_opcion("Detenerte antes de perderte completamente", "jason_dificil_ultimo_momento", stat="reputacion", cambio=10)
        jason_descenso_oscuridad.agregar_opcion("Abrazar la oscuridad", "jason_dificil_final_oscuridad", stat="reputacion", cambio=-40)
        self.historia["jason_dificil_descenso_oscuridad"] = jason_descenso_oscuridad

        jason_mostrar_codigo = NodoHistoria(
            "jason_dificil_mostrar_codigo",
            "PRESENTANDO TU CÓDIGO",
            "Encuentras a Batman y le muestras tu código escrito. Él lo lee cuidadosamente. 'No es mi código,' dice finalmente. "
            "'Pero es honorable. Puedo respetarlo.' Es la aprobación más cercana que obtendrás. 'Entonces, ¿no interferirás?' "
            "preguntas. 'Mientras sigas esto,' toca el papel, 'trabajaremos juntos, no uno contra el otro.'",
            "dificil_mostrar_codigo.png"
        )
        jason_mostrar_codigo.agregar_opcion("Formar una alianza basada en el código", "jason_dificil_alianza_codigo", stat="reputacion", cambio=25, item="Alianza con Batman")
        self.historia["jason_dificil_mostrar_codigo"] = jason_mostrar_codigo

        jason_operacion_independiente = NodoHistoria(
            "jason_dificil_operacion_independiente",
            "EL OPERATIVO INDEPENDIENTE",
            "Operas según tu código pero independientemente de Batman. Gotham se acostumbra a dos vigilantes con diferentes "
            "métodos. A veces cooperan, a veces no. Funciona. No es perfectamente, pero funciona. El crimen baja. Los inocentes "
            "están más seguros. Eso es lo que importa.",
            "dificil_operacion_independiente.png"
        )
        jason_operacion_independiente.agregar_opcion("Mantener este status quo", "jason_dificil_equilibrio_final", stat="recursos", cambio=2)
        self.historia["jason_dificil_operacion_independiente"] = jason_operacion_independiente

        jason_muelles_solo = NodoHistoria(
            "jason_dificil_muelles_solo",
            "LOS MUELLES DE NOCHE",
            "Llegas a los muelles solo. Varios camiones están cargando químicos. Secuaces del Joker por todas partes. Y ahí, "
            "supervisando todo, está él. El Joker. Te ve y aplaude. 'Sabía que vendrías solo, pajarito. Tan predecible.' "
            "Esto es una trampa, pero ya estás aquí.",
            "dificil_muelles_solo.png"
        )
        jason_muelles_solo.agregar_opcion("Atacar directamente", "jason_dificil_ataque_muelles", stat="salud", cambio=-25)
        jason_muelles_solo.agregar_opcion("Usar sigilo", "jason_dificil_sigilo_muelles", stat="recursos", cambio=-1)
        self.historia["jason_dificil_muelles_solo"] = jason_muelles_solo

        jason_muelles_equipo = NodoHistoria(
            "jason_dificil_muelles_equipo",
            "RESPALDO EN LOS MUELLES",
            "Le informas a Batman. Llegan juntos a los muelles. 'Tomamos posiciones diferentes,' sugiere Batman. 'Cubrimos más "
            "terreno así.' Asienten. Se separan estratégicamente. El Joker está ahí, pero esta vez tienes respaldo. Eso hace "
            "toda la diferencia.",
            "dificil_muelles_equipo.png"
        )
        jason_muelles_equipo.agregar_opcion("Seguir el plan coordinado", "jason_dificil_coordinacion_perfecta", stat="reputacion", cambio=15)
        self.historia["jason_dificil_muelles_equipo"] = jason_muelles_equipo

        jason_arkham_solo = NodoHistoria(
            "jason_dificil_arkham_solo",
            "SOLO EN ARKHAM",
            "Entras a Arkham solo. Es el caos. Lunáticos por todas partes. Peleas a través de ellos. Dos Caras, Espantapájaros, "
            "Mad Hatter, todos intentan detenerte. Los atraviesas a todos. Finalmente llegas al centro. El Joker está esperando, "
            "sentado en una silla como si fuera un trono. 'Mi pajarito favorito,' sonríe.",
            "dificil_arkham_solo.png"
        )
        jason_arkham_solo.agregar_opcion("Confrontación final", "jason_dificil_confrontacion_arkham", stat="salud", cambio=-20)
        self.historia["jason_dificil_arkham_solo"] = jason_arkham_solo

        jason_arkham_equipo = NodoHistoria(
            "jason_dificil_arkham_equipo",
            "ASALTO A ARKHAM",
            "Esperas a Batman. Entran juntos. Trabajan en perfecta sincronía, como en los viejos tiempos. Cada uno maneja a los "
            "villanos que mejor conoce. En minutos, llegan al centro donde el Joker espera. 'Dos pájaros,' ríe. 'Qué sorpresa.' "
            "Pero esta vez, no tiene ventaja.",
            "dificil_arkham_equipo.png"
        )
        jason_arkham_equipo.agregar_opcion("Confrontación final juntos", "jason_dificil_confrontacion_final_equipo", stat="reputacion", cambio=20)
        self.historia["jason_dificil_arkham_equipo"] = jason_arkham_equipo

        jason_aliados_inesperados = NodoHistoria(
            "jason_dificil_aliados_inesperados",
            "ALIADOS EXTRAÑOS",
            "Formas alianzas inesperadas: Arsenal, Starfire, Bizarro. Los Outlaws. No son tradicionales, pero son leales. Juntos "
            "protegen las partes de Gotham que Batman no alcanza. Es caótico, pero funciona. Tienes una familia de nuevo. "
            "Una extraña, pero una familia.",
            "dificil_aliados_inesperados.png"
        )
        jason_aliados_inesperados.agregar_opcion("Liderar a los Outlaws", "jason_dificil_lider_outlaws", stat="reputacion", cambio=20, item="Los Outlaws")
        self.historia["jason_dificil_aliados_inesperados"] = jason_aliados_inesperados

        jason_solo_final = NodoHistoria(
            "jason_dificil_solo_final",
            "EL ÚLTIMO LOBO SOLITARIO",
            "Nunca buscas aliados. Operas completamente solo hasta el final. Es la vida que elegiste. Solitaria, peligrosa, "
            "pero libre. Gotham te conoce como el vigilante solitario. Algunos te llaman héroe, otros villano. No te importa. "
            "Sabes quién eres. Y eso es suficiente.",
            "dificil_solo_final.png"
        )
        jason_solo_final.agregar_opcion("Confrontar tu destino solo", "jason_dificil_final_antiheroico", stat="recursos", cambio=1)
        self.historia["jason_dificil_solo_final"] = jason_solo_final

        # Finales de acciones contra el Joker
        jason_matar_joker = NodoHistoria(
            "jason_dificil_matar_joker",
            "EL DISPARO FINAL",
            "Aprietas el gatillo. El Joker cae. Por un momento, hay silencio. Luego, su risa grabada comienza a reproducirse "
            "por los altavoces. Incluso en muerte, se burla. Batman llega segundos después. Ve el cuerpo. Te mira con tristeza "
            "infinita. 'Jason... ¿qué hiciste?' 'Lo que tenía que hacer,' respondes. Pero la victoria se siente hueca.",
            "dificil_matar_joker.png"
        )
        jason_matar_joker.agregar_opcion("Enfrentar las consecuencias", "jason_dificil_final_oscuridad", stat="reputacion", cambio=-50)
        self.historia["jason_dificil_matar_joker"] = jason_matar_joker

        jason_perdonar_joker = NodoHistoria(
            "jason_dificil_perdonar_joker",
            "PERDONAR AL IMPERDONABLE",
            "Bajas el arma. 'No voy a matarte,' dices. El Joker parece genuinamente sorprendido. 'Pero... ¿por qué?' pregunta. "
            "'Porque si te mato, ganas. Demuestras que soy como tú. Y no lo soy.' Batman llega y ve la escena. Orgullo brilla "
            "en sus ojos. 'Jason...' No necesita decir más. Has demostrado quién eres realmente.",
            "dificil_perdonar_joker.png"
        )
        jason_perdonar_joker.agregar_opcion("Llevar al Joker a Arkham", "jason_dificil_final_redencion", stat="reputacion", cambio=40)
        self.historia["jason_dificil_perdonar_joker"] = jason_perdonar_joker

        jason_entregar_joker = NodoHistoria(
            "jason_dificil_entregar_joker",
            "LA ENTREGA",
            "Le entregas al Joker a Batman. 'Lo capturaste sin matarlo,' dice Batman. 'Demuetra que eres más fuerte de lo que "
            "él nunca será.' El Joker es llevado a Arkham. Por primera vez en años, sientes paz. No necesitaste matarlo para "
            "vencerlo. Eso es verdadera victoria.",
            "dificil_entregar_joker.png"
        )
        jason_entregar_joker.agregar_opcion("Comenzar un nuevo capítulo", "jason_dificil_final_redencion", stat="reputacion", cambio=35)
        self.historia["jason_dificil_entregar_joker"] = jason_entregar_joker

        jason_dejar_vivo = NodoHistoria(
            "jason_dificil_dejar_vivo",
            "GOLPEADO PERO VIVO",
            "Lo dejaste vivo, apenas. Batman llama a una ambulancia. 'Estuvo cerca,' dice Batman. 'Demasiado cerca.' 'Pero no "
            "lo maté,' respondes. 'Lo sé,' dice Batman. 'Y eso significa todo.' El Joker sobrevive para ir a Arkham. No conseguiste "
            "tu venganza total, pero mantuviste tu humanidad. Es un balance difícil.",
            "dificil_dejar_vivo.png"
        )
        jason_dejar_vivo.agregar_opcion("Aceptar este resultado", "jason_dificil_final_antiheroico", stat="reputacion", cambio=15)
        self.historia["jason_dificil_dejar_vivo"] = jason_dejar_vivo

        jason_golpe_final = NodoHistoria(
            "jason_dificil_golpe_final",
            "EL GOLPE DEFINITIVO",
            "Un último puñetazo. El Joker deja de respirar. Batman grita 'No!' pero es tarde. Está muerto. Has cruzado la línea. "
            "Batman te mira con horror y decepción. 'Jason... no.' La policía llega. Batman te protege de ser arrestado, pero "
            "tu relación con él está destruida. Obtuviste tu venganza, pero perdiste todo lo demás.",
            "dificil_golpe_final.png"
        )
        jason_golpe_final.agregar_opcion("Vivir con las consecuencias", "jason_dificil_final_oscuridad", stat="reputacion", cambio=-45)
        self.historia["jason_dificil_golpe_final"] = jason_golpe_final

        # Más desarrollos de alianzas y conflictos
        jason_alianza_fuerte = NodoHistoria(
            "jason_dificil_alianza_fuerte",
            "ALIANZA FORTALECIDA",
            "La alianza se fortalece. No son solo Batman y Red Hood. Son Bruce y Jason. Padre e hijo. Trabajan tan bien que otros "
            "héroes notan. Dick Grayson sonríe viendo trabajar a ambos. 'Finalmente,' dice. La familia se está sanando.",
            "dificil_alianza_fuerte.png"
        )
        jason_alianza_fuerte.agregar_opcion("Enfrentar juntos al Joker", "jason_dificil_equipo_joker", stat="reputacion", cambio=20)
        self.historia["jason_dificil_alianza_fuerte"] = jason_alianza_fuerte

        jason_mantener_distancia = NodoHistoria(
            "jason_dificil_mantener_distancia",
            "ALIADOS, NO FAMILIA",
            "Trabajan bien juntos, pero mantienes distancia emocional. No es como antes. Probablemente nunca lo será. Pero es "
            "suficiente. Son aliados profesionales. Respeto mutuo sin el peso emocional. Para ti, funciona mejor así.",
            "dificil_mantener_distancia.png"
        )
        jason_mantener_distancia.agregar_opcion("Continuar esta dinámica", "jason_dificil_equilibrio_profesional", stat="recursos", cambio=1)
        self.historia["jason_dificil_mantener_distancia"] = jason_mantener_distancia

        jason_momento_correcto = NodoHistoria(
            "jason_dificil_momento_correcto",
            "ESPERANDO LA OPORTUNIDAD",
            "Trabajas con Batman mientras esperas tu oportunidad. Meses pasan. Entonces, el Joker escapa de nuevo. Esta es tu "
            "oportunidad. Pero Batman te rastrea. 'Sé lo que estás planeando,' dice. 'No lo hagas.' Pero has esperado demasiado "
            "para detenerte ahora.",
            "dificil_momento_correcto.png"
        )
        jason_momento_correcto.agregar_opcion("Traicionar a Batman y seguir el plan", "jason_dificil_traicion", stat="reputacion", cambio=-35)
        jason_momento_correcto.agregar_opcion("Reconsiderar en el último momento", "jason_dificil_reconsideracion", stat="reputacion", cambio=20)
        self.historia["jason_dificil_momento_correcto"] = jason_momento_correcto

        jason_almacen_trampa = NodoHistoria(
            "jason_dificil_almacen_trampa",
            "LA TRAMPA FINAL",
            "Llegas al almacén. Dentro están los rehenes. Y el Joker. Y Batman, también atado. Fue una trampa para ambos. "
            "'Tres pájaros con una piedra,' ríe el Joker. Bombas por todas partes. '10 minutos,' dice. 'Salven a quien puedan.' "
            "Se va riendo. Tienes que elegir: salvar a Batman, salvar a los rehenes, o perseguir al Joker.",
            "dificil_almacen_trampa.png"
        )
        jason_almacen_trampa.agregar_opcion("Salvar a Batman primero", "jason_dificil_salvar_batman", stat="reputacion", cambio=15)
        jason_almacen_trampa.agregar_opcion("Salvar a los rehenes primero", "jason_dificil_salvar_rehenes", stat="salud", cambio=-20)
        jason_almacen_trampa.agregar_opcion("Perseguir al Joker", "jason_dificil_perseguir_joker", stat="reputacion", cambio=-30)
        self.historia["jason_dificil_almacen_trampa"] = jason_almacen_trampa

        jason_respeto_mantenido = NodoHistoria(
            "jason_dificil_respeto_mantenido",
            "RESPETO A PESAR DE TODO",
            "Mantienen respeto mutuo a pesar de sus diferencias filosóficas. Cuando trabajan juntos, Gotham es más segura. "
            "Cuando trabajan separados, cubren más terreno. No es perfectamente, pero es funcional. Y lo más importante, "
            "siguen siendo familia. Eso nunca cambió realmente.",
            "dificil_respeto_mantenido.png"
        )
        jason_respeto_mantenido.agregar_opcion("Continuar con este entendimiento", "jason_dificil_equilibrio_final", stat="reputacion", cambio=15)
        self.historia["jason_dificil_respeto_mantenido"] = jason_respeto_mantenido

        jason_aceptar_diferencias = NodoHistoria(
            "jason_dificil_aceptar_diferencias",
            "DIFERENCIAS ACEPTADAS",
            "Aceptan que nunca estarán completamente de acuerdo. Y está bien. Pueden ser familia sin estar de acuerdo en todo. "
            "Pueden ser aliados sin compartir cada principio. La relación es complicada, pero real. Y eso es mejor que la "
            "alternativa: no tener relación alguna.",
            "dificil_aceptar_diferencias.png"
        )
        jason_aceptar_diferencias.agregar_opcion("Seguir adelante juntos", "jason_dificil_adelante_juntos", stat="reputacion", cambio=10)
        self.historia["jason_dificil_aceptar_diferencias"] = jason_aceptar_diferencias

        jason_apertura_emocional = NodoHistoria(
            "jason_dificil_apertura_emocional",
            "ABRIENDO EL CORAZÓN",
            "Le cuentas todo: el dolor, la rabia, la soledad, el sentimiento de abandono. Bruce también se abre: el trauma de "
            "tu muerte, la culpa que carga, el amor que nunca desapareció. Lloran juntos bajo las estrellas de Gotham. La sanación "
            "comienza esa noche. Verdaderamente.",
            "dificil_apertura_emocional.png"
        )
        jason_apertura_emocional.agregar_opcion("Reconstruir la relación", "jason_dificil_reconstruccion_familiar", stat="reputacion", cambio=30, item="Lazo Renovado")
        self.historia["jason_dificil_apertura_emocional"] = jason_apertura_emocional

        jason_distancia_emocional = NodoHistoria(
            "jason_dificil_distancia_emocional",
            "MANTENIENDO MUROS",
            "Hablan, pero mantienes muros emocionales. No estás listo para abrirte completamente. Bruce lo entiende. 'Cuando "
            "estés listo,' dice. Tal vez algún día lo estarás. Tal vez no. Por ahora, esto es lo mejor que puedes dar.",
            "dificil_distancia_emocional.png"
        )
        jason_distancia_emocional.agregar_opcion("Mantener esta distancia", "jason_dificil_distancia_mantenida", stat="recursos", cambio=1)
        self.historia["jason_dificil_distancia_emocional"] = jason_distancia_emocional

        jason_evasion_continua = NodoHistoria(
            "jason_dificil_evasion_continua",
            "EL JUEGO DEL GATO Y EL RATÓN",
            "Continúas evadiendo a Batman. Es un juego interminable. Él te rastrea, tú escapas. Semanas de esto. Ambos se cansan. "
            "Finalmente, en una azotea, simplemente se miran. 'Esto es ridículo,' dice Batman. 'Lo sé,' respondes. 'Entonces "
            "hablemos,' sugiere. Esta vez, aceptas.",
            "dificil_evasion_continua.png"
        )
        jason_evasion_continua.agregar_opcion("Finalmente hablar", "jason_dificil_dialogo_azotea", stat="reputacion", cambio=5)
        self.historia["jason_dificil_evasion_continua"] = jason_evasion_continua

        jason_escuchar_batman = NodoHistoria(
            "jason_dificil_escuchar_batman",
            "ESCUCHANDO CON ATENCIÓN",
            "'Jason, sé que no puedo detenerte físicamente,' dice Batman. 'Pero puedo pedirte que no te destruyas por venganza. "
            "El Joker no vale tu alma.' Lo escuchas. Realmente lo escuchas. Sus palabras pesan. Tal vez tiene un punto. Tal vez "
            "hay otra forma.",
            "dificil_escuchar_batman.png"
        )
        jason_escuchar_batman.agregar_opcion("Considerar sus palabras seriamente", "jason_dificil_consideracion_seria", stat="reputacion", cambio=15)
        jason_escuchar_batman.agregar_opcion("Agradecer pero seguir tu camino", "jason_dificil_agradecimiento_rechazo", stat="recursos", cambio=1)
        self.historia["jason_dificil_escuchar_batman"] = jason_escuchar_batman

        jason_equipo_joker = NodoHistoria(
            "jason_dificil_equipo_joker",
            "CAZANDO AL JOKER JUNTOS",
            "Rastrean al Joker juntos. Usan los recursos de Batman y tu conocimiento de las calles. En días, localizan su escondite. "
            "Planean meticulosamente. Esta vez no habrá errores. Esta vez, el Joker no escapará. Entran al amanecer, cuando menos "
            "lo espera.",
            "dificil_equipo_joker.png"
        )
        jason_equipo_joker.agregar_opcion("Ejecutar el plan", "jason_dificil_plan_perfecto", stat="reputacion", cambio=20)
        self.historia["jason_dificil_equipo_joker"] = jason_equipo_joker

        jason_ultimo_momento = NodoHistoria(
            "jason_dificil_ultimo_momento",
            "DETENIÉNDOSE AL BORDE",
            "Estás a punto de cruzar el punto de no retorno. Pero algo te detiene. Una memoria: Alfred sirviéndote té. Bruce "
            "enseñándote a atarte los zapatos. Dick haciendo chistes malos. Tu familia. Si te pierdes en la oscuridad, los "
            "pierdes a ellos. No vale la pena. Te detienes. Respiras. Empiezas el largo camino de regreso.",
            "dificil_ultimo_momento.png"
        )
        jason_ultimo_momento.agregar_opcion("Buscar redención", "jason_dificil_buscar_redencion", stat="reputacion", cambio=25)
        self.historia["jason_dificil_ultimo_momento"] = jason_ultimo_momento

        jason_alianza_codigo = NodoHistoria(
            "jason_dificil_alianza_codigo",
            "ALIANZA BASADA EN PRINCIPIOS",
            "Forman una alianza basada en tu código. Batman lo respeta, tú respetas su supervisión. No es perfecto, pero funciona. "
            "Gotham se beneficia de ambos estilos. Los criminales no saben qué esperar. La ciudad es más segura. Y ustedes están "
            "en buenos términos. Es un buen arreglo.",
            "dificil_alianza_codigo.png"
        )
        jason_alianza_codigo.agregar_opcion("Fortalecer esta alianza", "jason_dificil_alianza_fuerte", stat="reputacion", cambio=15)
        self.historia["jason_dificil_alianza_codigo"] = jason_alianza_codigo

        jason_equilibrio_final = NodoHistoria(
            "jason_dificil_equilibrio_final",
            "EL EQUILIBRIO PERFECTO",
            "Has encontrado tu equilibrio. Red Hood tiene su lugar en Gotham. No eres Batman, no eres villano. Eres algo único. "
            "Los criminales te temen, los inocentes te respetan, Batman te acepta. No es la vida que esperabas, pero es la vida "
            "que construiste. Y es suficiente.",
            "dificil_equilibrio_final.png"
        )
        jason_equilibrio_final.agregar_opcion("Continuar protegiendo Gotham", "jason_dificil_final_antiheroico", stat="reputacion", cambio=20)
        self.historia["jason_dificil_equilibrio_final"] = jason_equilibrio_final

        # Más confrontaciones finales
        jason_ataque_muelles = NodoHistoria(
            "jason_dificil_ataque_muelles",
            "ASALTO FRONTAL",
            "Cargas directamente. Los secuaces te disparan. Esquivas, ruedas, disparas de vuelta. Es caótico. Llegas al Joker "
            "cubierto de sangre (no toda tuya). Él aplaude. 'Impresionante. Pero predecible.' Presiona un botón. Los camiones "
            "explotan. Químicos se derraman al agua. Fuego por todas partes. Ambos están atrapados en el infierno.",
            "dificil_ataque_muelles.png"
        )
        jason_ataque_muelles.agregar_opcion("Pelear en el fuego", "jason_dificil_pelea_fuego", stat="salud", cambio=-30)
        self.historia["jason_dificil_ataque_muelles"] = jason_ataque_muelles

        jason_sigilo_muelles = NodoHistoria(
            "jason_dificil_sigilo_muelles",
            "CAZADOR EN LAS SOMBRAS",
            "Te mueves como un fantasma. Uno por uno, los secuaces caen en silencio. El Joker no nota hasta que es demasiado tarde. "
            "Estás detrás de él, tu pistola en su nuca. 'Fin del juego,' dices. Él ríe. 'Oh, Jason. El juego nunca termina.' "
            "Hace un último movimiento desesperado.",
            "dificil_sigilo_muelles.png"
        )
        jason_sigilo_muelles.agregar_opcion("Reaccionar rápidamente", "jason_dificil_reaccion_rapida", stat="recursos", cambio=1)
        self.historia["jason_dificil_sigilo_muelles"] = jason_sigilo_muelles

        jason_coordinacion_perfecta = NodoHistoria(
            "jason_dificil_coordinacion_perfecta",
            "TRABAJO EN EQUIPO PERFECTO",
            "Trabajan como una máquina perfectamente aceitada. Batman desde arriba, tú desde el suelo. Los secuaces caen en minutos. "
            "El Joker intenta escapar pero ambos lo acorralan. Está atrapado. No tiene salida. 'Ah, la familia reunida,' ríe nerviosamente.",
            "dificil_coordinacion_perfecta.png"
        )
        jason_coordinacion_perfecta.agregar_opcion("Capturarlo juntos", "jason_dificil_captura_conjunta", stat="reputacion", cambio=25)
        self.historia["jason_dificil_coordinacion_perfecta"] = jason_coordinacion_perfecta

        jason_confrontacion_arkham = NodoHistoria(
            "jason_dificil_confrontacion_arkham",
            "CONFRONTACIÓN EN ARKHAM",
            "Te paras frente al Joker. Solo ustedes dos. Como debía ser. 'Aquí estamos de nuevo,' dice. 'Tú y yo. Eterno.' "
            "'No más,' respondes. 'Esto termina hoy.' 'Oh, Jason,' suspira teatralmente. 'Esto nunca termina. Somos parte "
            "el uno del otro ahora. Yo te hice. Tú me das propósito.' Levanta los brazos. 'Entonces hazlo. Mátame. Prueba "
            "que tenía razón sobre ti.'",
            "dificil_confrontacion_arkham.png"
        )
        jason_confrontacion_arkham.agregar_opcion("Matarlo y terminar esto", "jason_dificil_matar_joker", stat="reputacion", cambio=-40)
        jason_confrontacion_arkham.agregar_opcion("Rechazar su narrativa", "jason_dificil_rechazar_narrativa", stat="reputacion", cambio=30)
        self.historia["jason_dificil_confrontacion_arkham"] = jason_confrontacion_arkham

        jason_confrontacion_final_equipo = NodoHistoria(
            "jason_dificil_confrontacion_final_equipo",
            "EL ÚLTIMO ACTO JUNTOS",
            "Batman y tú están frente al Joker. Padre e hijo, juntos. El Joker mira entre ambos. 'Qué conmovedor,' dice. "
            "'La familia reunida para mi ejecución.' 'No tu ejecución,' dice Batman. 'Tu arresto.' 'Por última vez,' agregas. "
            "El Joker intenta una última trampa, pero están preparados. Lo capturan juntos.",
            "dificil_confrontacion_final_equipo.png"
        )
        jason_confrontacion_final_equipo.agregar_opcion("Llevarlo a Arkham juntos", "jason_dificil_final_redencion", stat="reputacion", cambio=35)
        self.historia["jason_dificil_confrontacion_final_equipo"] = jason_confrontacion_final_equipo

        jason_lider_outlaws = NodoHistoria(
            "jason_dificil_lider_outlaws",
            "LÍDER DE LOS PROSCRITOS",
            "Los Outlaws te siguen lealmente. Protegen partes de Gotham que nadie más protege. No son la Liga de la Justicia, "
            "no son los Teen Titans. Son algo nuevo. Y funcionan. Batman no aprueba completamente, pero respeta lo que logran. "
            "Has encontrado tu lugar, no como Robin, no como villano, sino como Red Hood, líder de los rechazados.",
            "dificil_lider_outlaws.png"
        )
        jason_lider_outlaws.agregar_opcion("Continuar liderando", "jason_dificil_final_antiheroico", stat="reputacion", cambio=25)
        self.historia["jason_dificil_lider_outlaws"] = jason_lider_outlaws

        jason_arrestar_joker_teatro = NodoHistoria(
            "jason_dificil_arrestar_joker_teatro",
            "ARRESTO EN EL TEATRO",
            "Lo atas fuertemente. Llamas a la policía. El Joker tose sangre pero sonríe. 'No me mataste,' observa. 'Decepcionante.' "
            "'No,' respondes. 'Te demostré que estabas equivocado. No soy como tú. Nunca lo seré.' Su sonrisa vacila por primera vez. "
            "Has ganado de la forma correcta.",
            "dificil_arrestar_joker_teatro.png"
        )
        jason_arrestar_joker_teatro.agregar_opcion("Esperar a que llegue ayuda", "jason_dificil_arresto_exitoso", stat="reputacion", cambio=30)
        self.historia["jason_dificil_arrestar_joker_teatro"] = jason_arrestar_joker_teatro

        jason_replanear = NodoHistoria(
            "jason_dificil_replanear",
            "APRENDIENDO DE LOS ERRORES",
            "Vuelves a tu base herido pero más sabio. El Joker es más peligroso de lo que recordabas. Necesitas un mejor plan. "
            "Pasas semanas preparándote: estudiando sus patrones, preparando contramedidas, entrenando. Esta vez, cuando lo "
            "enfrentes, estarás listo.",
            "dificil_replanear.png"
        )
        jason_replanear.agregar_opcion("Preparar el plan definitivo", "jason_dificil_plan_definitivo", stat="recursos", cambio=3)
        self.historia["jason_dificil_replanear"] = jason_replanear

        jason_traicion = NodoHistoria(
            "jason_dificil_traicion",
            "LA TRAICIÓN",
            "Noqueias a Batman con gas somnífero. 'Lo siento, Bruce,' murmuras. 'Pero esto tengo que hacerlo.' Vas tras el Joker "
            "solo. Lo encuentras. Lo matas. Pero cuando regresas, Batman ya despertó. La decepción en sus ojos es peor que cualquier "
            "golpe. 'Traicionaste mi confianza,' dice simplemente. La relación está rota, quizás irreparablemente.",
            "dificil_traicion.png"
        )
        jason_traicion.agregar_opcion("Vivir con la traición", "jason_dificil_final_oscuridad", stat="reputacion", cambio=-50)
        self.historia["jason_dificil_traicion"] = jason_traicion

        jason_reconsideracion = NodoHistoria(
            "jason_dificil_reconsideracion",
            "EL CAMBIO DE CORAZÓN",
            "Estás a punto de traicionar a Batman, pero te detienes. Miras tu arma. Piensas en todo lo que Bruce te enseñó. "
            "'No puedo,' admites. 'No así.' Batman asiente con comprensión. 'Entonces encontremos otra forma. Juntos.' Buscan "
            "al Joker, pero esta vez, con el plan de capturarlo, no matarlo.",
            "dificil_reconsideracion.png"
        )
        jason_reconsideracion.agregar_opcion("Trabajar juntos honestamente", "jason_dificil_equipo_joker", stat="reputacion", cambio=25)
        self.historia["jason_dificil_reconsideracion"] = jason_reconsideracion

        jason_salvar_batman = NodoHistoria(
            "jason_dificil_salvar_batman",
            "SALVANDO AL PADRE",
            "Corres hacia Batman primero. Lo liberas. 'Los rehenes,' dice inmediatamente. 'Lo sé,' respondes. 'Pero te necesito "
            "vivo para salvarlos.' Juntos corren hacia los rehenes. Con 2 minutos restantes, liberan al último. Todos escapan "
            "justo cuando el edificio explota. El Joker escapó, pero todos viven. Eso es lo que importa.",
            "dificil_salvar_batman.png"
        )
        jason_salvar_batman.agregar_opcion("Perseguir al Joker después", "jason_dificil_persecucion_posterior", stat="recursos", cambio=-1)
        self.historia["jason_dificil_salvar_batman"] = jason_salvar_batman

        jason_salvar_rehenes = NodoHistoria(
            "jason_dificil_salvar_rehenes",
            "SALVANDO A LOS INOCENTES",
            "Ignoras a Batman y corres hacia los rehenes. 'Jason, ¡no!' grita. Pero ya estás liberando rehenes. Con 3 minutos "
            "restantes, liberas al último. Vuelves por Batman con 1 minuto. Lo liberas con 30 segundos. Apenas escapan. Ambos "
            "heridos, pero vivos. Batman te mira. 'Salvaste a los inocentes primero. Como un verdadero héroe.'",
            "dificil_salvar_rehenes.png"
        )
        jason_salvar_rehenes.agregar_opcion("Aceptar el cumplido", "jason_dificil_reconocimiento", stat="reputacion", cambio=25, stat2="salud", cambio2=-20)
        self.historia["jason_dificil_salvar_rehenes"] = jason_salvar_rehenes

        jason_perseguir_joker = NodoHistoria(
            "jason_dificil_perseguir_joker",
            "LA OBSESIÓN FATAL",
            "Ignoras todo y persigues al Joker. Batman grita tu nombre. Los rehenes gritan por ayuda. Pero solo ves al Joker "
            "escapando. Lo persigues. Detrás de ti, el edificio explota. Batman logra salir, pero no todos los rehenes. Capturas "
            "al Joker, pero a un costo terrible. La sangre de los inocentes está en tus manos.",
            "dificil_perseguir_joker.png"
        )
        jason_perseguir_joker.agregar_opcion("Enfrentar lo que hiciste", "jason_dificil_costo_terrible", stat="reputacion", cambio=-40, stat2="salud", cambio2=-30)
        self.historia["jason_dificil_perseguir_joker"] = jason_perseguir_joker

        jason_adelante_juntos = NodoHistoria(
            "jason_dificil_adelante_juntos",
            "AVANZANDO UNIDOS",
            "Deciden seguir adelante juntos, con todas sus diferencias y similitudes. No tratan de cambiarse mutuamente. Se aceptan "
            "como son. Batman será Batman. Red Hood será Red Hood. Y juntos, protegerán Gotham de formas que ninguno podría solo.",
            "dificil_adelante_juntos.png"
        )
        jason_adelante_juntos.agregar_opcion("Enfrentar juntos el futuro", "jason_dificil_final_antiheroico", stat="reputacion", cambio=20)
        self.historia["jason_dificil_adelante_juntos"] = jason_adelante_juntos

        jason_reconstruccion_familiar = NodoHistoria(
            "jason_dificil_reconstruccion_familiar",
            "RECONSTRUYENDO LA FAMILIA",
            "Con el tiempo, la familia se reconstruye. Cenas en la mansión Wayne. Entrenamientos en la Batcueva. Alfred sonriendo "
            "mientras sirve té. Dick haciendo chistes. Tim observando con admiración. Damian siendo... Damian. No es perfecto, "
            "pero es real. Es familia. Y finalmente, sientes que estás en casa.",
            "dificil_reconstruccion_familiar.png"
        )
        jason_reconstruccion_familiar.agregar_opcion("Disfrutar este momento", "jason_dificil_paz_encontrada", stat="reputacion", cambio=30)
        self.historia["jason_dificil_reconstruccion_familiar"] = jason_reconstruccion_familiar

        jason_distancia_mantenida = NodoHistoria(
            "jason_dificil_distancia_mantenida",
            "RESPETO A LA DISTANCIA",
            "Mantienen la distancia emocional. Trabajan juntos cuando es necesario, pero no más. Es una relación profesional más "
            "que familiar. Duele un poco, pero es seguro. No habrá más dolor si no te acercas demasiado. Es la protección que "
            "elegiste. Batman lo entiende, aunque le duela también.",
            "dificil_distancia_mantenida.png"
        )
        jason_distancia_mantenida.agregar_opcion("Continuar así", "jason_dificil_final_antiheroico", stat="recursos", cambio=1)
        self.historia["jason_dificil_distancia_mantenida"] = jason_distancia_mantenida

        jason_consideracion_seria = NodoHistoria(
            "jason_dificil_consideracion_seria",
            "CONSIDERANDO SERIAMENTE",
            "Las palabras de Batman resuenan durante días. Consultas con Alfred. Hablas con Dick. Incluso meditas en Crime Alley "
            "donde todo comenzó. Llegas a una conclusión: la venganza no te sanará. Pero la justicia sí. Y hay una diferencia. "
            "Decides buscar justicia, no venganza.",
            "dificil_consideracion_seria.png"
        )
        jason_consideracion_seria.agregar_opcion("Buscar justicia con Batman", "jason_dificil_equipo_joker", stat="reputacion", cambio=20)
        self.historia["jason_dificil_consideracion_seria"] = jason_consideracion_seria

        jason_agradecimiento_rechazo = NodoHistoria(
            "jason_dificil_agradecimiento_rechazo",
            "AGRADECIENDO PERO RECHAZANDO",
            "'Gracias por preocuparte, Bruce,' dices. 'Pero mi camino es mío.' Batman asiente tristemente. 'Esperaba que dijeras "
            "eso. Solo... ten cuidado, Jason. El camino de la venganza no tiene final feliz.' 'Tal vez,' respondes. 'Pero es mi "
            "camino para descubrirlo.' Te vas. Batman te deja ir, sabiendo que no puede detenerte.",
            "dificil_agradecimiento_rechazo.png"
        )
        jason_agradecimiento_rechazo.agregar_opcion("Seguir tu camino solo", "jason_dificil_camino_solitario_final", stat="recursos", cambio=-1)
        self.historia["jason_dificil_agradecimiento_rechazo"] = jason_agradecimiento_rechazo

        jason_plan_perfecto = NodoHistoria(
            "jason_dificil_plan_perfecto",
            "EL PLAN PERFECTO",
            "El plan se ejecuta perfectamente. Rastrean al Joker a una fábrica abandonada. Entran sincronizados. Batman desde arriba, "
            "tú desde abajo. El Joker no tiene oportunidad. En minutos está capturado. Mira entre ambos. 'Supongo que la familia "
            "que mata junta, se queda junta,' bromea. Ninguno de ustedes se ríe. Pero ambos sonríen. Ganaron. Juntos.",
            "dificil_plan_perfecto.png"
        )
        jason_plan_perfecto.agregar_opcion("Celebrar la victoria", "jason_dificil_final_redencion", stat="reputacion", cambio=35)
        self.historia["jason_dificil_plan_perfecto"] = jason_plan_perfecto

        jason_pelea_fuego = NodoHistoria(
            "jason_dificil_pelea_fuego",
            "INFIERNO EN LOS MUELLES",
            "Pelean rodeados de fuego y químicos tóxicos. Es el infierno literal. Cada golpe, cada disparo, cada movimiento podría "
            "ser el último. El Joker pelea con desesperación. Tú peleas con determinación. Finalmente, lo tienes contra una pared. "
            "El fuego se acerca. Tienes que decidir ahora: matarlo aquí o salvarlo.",
            "dificil_pelea_fuego.png"
        )
        jason_pelea_fuego.agregar_opcion("Dejarlo morir en el fuego", "jason_dificil_muerte_fuego", stat="reputacion", cambio=-35)
        jason_pelea_fuego.agregar_opcion("Salvarlo y arrestarlo", "jason_dificil_salvar_arrestar", stat="salud", cambio=-25, stat2="reputacion", cambio2=25)
        self.historia["jason_dificil_pelea_fuego"] = jason_pelea_fuego

        jason_reaccion_rapida = NodoHistoria(
            "jason_dificil_reaccion_rapida",
            "REFLEJOS PERFECTOS",
            "El Joker saca una navaja y se voltea. Pero estás listo. Disparas. La navaza cae. Él cae. No está muerto, solo herido. "
            "'Tan rápido,' dice tosiendo. 'Bruce te entrenó bien.' 'Él me enseñó muchas cosas,' respondes. 'Incluyendo cuándo no "
            "matar.' Llamas a la policía. El Joker va a Arkham. Vivo. Y tú probaste tu punto.",
            "dificil_reaccion_rapida.png"
        )
        jason_reaccion_rapida.agregar_opcion("Esperar al arresto", "jason_dificil_arresto_exitoso", stat="reputacion", cambio=30)
        self.historia["jason_dificil_reaccion_rapida"] = jason_reaccion_rapida

        jason_captura_conjunta = NodoHistoria(
            "jason_dificil_captura_conjunta",
            "CAPTURA EN EQUIPO",
            "Batman lo sujeta mientras tú lo atas. Trabajan en perfecta sincronía. El Joker ríe nerviosamente. 'Esto no es justo. "
            "Dos contra uno.' 'La vida no es justa,' dices. 'Tú me enseñaste eso.' Batman llama a la policía. El Joker va a Arkham. "
            "Esta vez, capturado por padre e hijo juntos. Hay poesía en eso.",
            "dificil_captura_conjunta.png"
        )
        jason_captura_conjunta.agregar_opcion("Celebrar la victoria juntos", "jason_dificil_victoria_conjunta", stat="reputacion", cambio=35)
        self.historia["jason_dificil_captura_conjunta"] = jason_captura_conjunta

        jason_rechazar_narrativa = NodoHistoria(
            "jason_dificil_rechazar_narrativa",
            "RECHAZANDO SU HISTORIA",
            "'No,' dices firmemente. 'No me hiciste. Me lastimaste. Me cambiaste. Pero no me definiste. Yo decidí quién soy. "
            "Y decidí no ser tú.' El Joker parece genuinamente sorprendido. Por primera vez, no tiene respuesta. Lo atas y lo "
            "entregas a las autoridades de Arkham. Has ganado, no solo la pelea, sino la batalla por tu identidad.",
            "dificil_rechazar_narrativa.png"
        )
        jason_rechazar_narrativa.agregar_opcion("Reclamar tu identidad", "jason_dificil_final_redencion", stat="reputacion", cambio=40)
        self.historia["jason_dificil_rechazar_narrativa"] = jason_rechazar_narrativa

        jason_equilibrio_profesional = NodoHistoria(
            "jason_dificil_equilibrio_profesional",
            "PROFESIONALES ANTE TODO",
            "Mantienen una relación estrictamente profesional. Funciona. Gotham se beneficia. Los criminales temen. Los inocentes "
            "están seguros. No hay drama emocional, no hay conflictos familiares. Solo dos profesionales haciendo su trabajo. "
            "Es eficiente. Es seguro. Es... suficiente. O al menos, te dices a ti mismo que lo es.",
            "dificil_equilibrio_profesional.png"
        )
        jason_equilibrio_profesional.agregar_opcion("Continuar profesionalmente", "jason_dificil_final_antiheroico", stat="recursos", cambio=1)
        self.historia["jason_dificil_equilibrio_profesional"] = jason_equilibrio_profesional

        jason_persecucion_posterior = NodoHistoria(
            "jason_dificil_persecucion_posterior",
            "LA PERSECUCIÓN CONTINÚA",
            "Con todos a salvo, persiguen al Joker juntos. Lo rastrean durante días. Finalmente lo acorralan en un callejón. "
            "No tiene salida. Mira entre ambos. 'Juntos de nuevo,' sonríe. 'Como debería ser.' 'Por última vez,' dice Batman. "
            "Lo capturan juntos. El círculo se cierra.",
            "dificil_persecucion_posterior.png"
        )
        jason_persecucion_posterior.agregar_opcion("Terminar esto", "jason_dificil_cierre_final", stat="reputacion", cambio=25)
        self.historia["jason_dificil_persecucion_posterior"] = jason_persecucion_posterior

        jason_reconocimiento = NodoHistoria(
            "jason_dificil_reconocimiento",
            "RECONOCIMIENTO GANADO",
            "Herido pero orgulloso, aceptas las palabras de Batman. 'Aprendí del mejor,' respondes. Batman sonríe. 'Y te convertiste "
            "en algo único. No una copia de mí, sino tu propia versión de héroe. Estoy orgulloso, Jason.' Por primera vez en años, "
            "sientes que está bien ser quien eres.",
            "dificil_reconocimiento.png"
        )
        jason_reconocimiento.agregar_opcion("Aceptar tu identidad", "jason_dificil_final_antiheroico", stat="reputacion", cambio=30)
        self.historia["jason_dificil_reconocimiento"] = jason_reconocimiento

        jason_costo_terrible = NodoHistoria(
            "jason_dificil_costo_terrible",
            "EL COSTO DE LA OBSESIÓN",
            "Tienes al Joker, pero a qué costo. Personas murieron porque elegiste venganza sobre salvación. Batman llega, ve los "
            "cuerpos, ve a ti con el Joker. 'Jason... ¿qué hiciste?' No tienes respuesta. Conseguiste tu venganza, pero perdiste "
            "tu alma. El Joker sonríe incluso mientras lo arrestan. Ganó de la peor manera posible.",
            "dificil_costo_terrible.png"
        )
        jason_costo_terrible.agregar_opcion("Vivir con la culpa", "jason_dificil_final_oscuridad", stat="reputacion", cambio=-50, stat2="salud", cambio2=-25)
        self.historia["jason_dificil_costo_terrible"] = jason_costo_terrible

        jason_paz_encontrada = NodoHistoria(
            "jason_dificil_paz_encontrada",
            "LA PAZ INTERIOR",
            "Has encontrado paz. No es perfecta, pero es real. Tienes familia, propósito, identidad. Red Hood tiene su lugar en "
            "Gotham. Jason Todd ha sanado. Aún hay trabajo por hacer, siempre lo habrá. Pero por primera vez desde tu muerte, "
            "sientes que todo estará bien.",
            "dificil_paz_encontrada.png"
        )
        jason_paz_encontrada.agregar_opcion("Abrazar el futuro", "jason_dificil_final_redencion", stat="reputacion", cambio=35)
        self.historia["jason_dificil_paz_encontrada"] = jason_paz_encontrada

        jason_camino_solitario_final = NodoHistoria(
            "jason_dificil_camino_solitario_final",
            "EL CAMINO SOLITARIO",
            "Sigues tu camino solo hasta el final. Sin Batman, sin familia, sin aliados. Solo tú y tu misión. Es solitario, pero "
            "es auténtico. Nadie más dicta tus elecciones. Proteges Gotham a tu manera. Algunos te llaman héroe, otros villano. "
            "No te importa. Sabes quién eres.",
            "dificil_camino_solitario_final.png"
        )
        jason_camino_solitario_final.agregar_opcion("Aceptar la soledad", "jason_dificil_final_antiheroico", stat="recursos", cambio=-2)
        self.historia["jason_dificil_camino_solitario_final"] = jason_camino_solitario_final

        jason_muerte_fuego = NodoHistoria(
            "jason_dificil_muerte_fuego",
            "MUERTE EN LLAMAS",
            "Lo dejas ahí. El fuego lo consume. Sus gritos resuenan. Escapas mientras el infierno se lo traga. Está muerto. "
            "Finalmente. Pero mientras te alejas, sientes vacío. Esperabas sentir paz, cierre, algo. Pero solo hay vacío. "
            "La venganza no te sanó. Solo te dejó más vacío que antes.",
            "dificil_muerte_fuego.png"
        )
        jason_muerte_fuego.agregar_opcion("Enfrentar el vacío", "jason_dificil_final_oscuridad", stat="reputacion", cambio=-45)
        self.historia["jason_dificil_muerte_fuego"] = jason_muerte_fuego

        jason_salvar_arrestar = NodoHistoria(
            "jason_dificil_salvar_arrestar",
            "SALVANDO AL ENEMIGO",
            "Lo cargas y escapan del fuego juntos. Ambos colapsan fuera, tosiendo. El Joker te mira confundido. '¿Por qué?' "
            "pregunta genuinamente. 'Porque no soy tú,' respondes. La policía llega. Lo arrestas. Estás quemado, herido, pero "
            "vivo. Y más importante, has demostrado quién eres realmente.",
            "dificil_salvar_arrestar.png"
        )
        jason_salvar_arrestar.agregar_opcion("Recuperarte del infierno", "jason_dificil_recuperacion_heroica", stat="salud", cambio=-25, stat2="reputacion", cambio2=35)
        self.historia["jason_dificil_salvar_arrestar"] = jason_salvar_arrestar

        jason_arresto_exitoso = NodoHistoria(
            "jason_dificil_arresto_exitoso",
            "ARRESTO EXITOSO",
            "La policía llega. El Joker es llevado a Arkham. Commissioner Gordon te mira. 'Gracias, Red Hood,' dice simplemente. "
            "Batman llega y te ve. No dice nada, pero asiente con aprobación. Has hecho lo correcto. El Joker está capturado, "
            "la justicia se sirve, y no cruzaste la línea. Es una victoria completa.",
            "dificil_arresto_exitoso.png"
        )
        jason_arresto_exitoso.agregar_opcion("Celebrar la justicia", "jason_dificil_final_redencion", stat="reputacion", cambio=35)
        self.historia["jason_dificil_arresto_exitoso"] = jason_arresto_exitoso

        jason_plan_definitivo = NodoHistoria(
            "jason_dificil_plan_definitivo",
            "EL PLAN DEFINITIVO",
            "Preparas el plan perfecto. Cada contingencia cubierta. Cada posible movimiento del Joker anticipado. Finalmente, "
            "estás listo. Rastrear al Joker a un depósito abandonado. Esta vez, no habrá errores. Esta vez, terminarás esto de "
            "una vez por todas. Entras con confianza total.",
            "dificil_plan_definitivo.png"
        )
        jason_plan_definitivo.agregar_opcion("Ejecutar el plan", "jason_dificil_ejecucion_perfecta", stat="recursos", cambio=2)
        self.historia["jason_dificil_plan_definitivo"] = jason_plan_definitivo

        jason_victoria_conjunta = NodoHistoria(
            "jason_dificil_victoria_conjunta",
            "VICTORIA JUNTOS",
            "En la azotea de la GCPD, mientras el Joker es llevado adentro, Batman y tú se miran. No necesitan palabras. Después "
            "de todo, has vuelto. No como Robin, sino como Red Hood. Y él te acepta. 'Buen trabajo, Jason,' dice finalmente. "
            "'Tú también, Bruce,' respondes. La familia está sanando.",
            "dificil_victoria_conjunta.png"
        )
        jason_victoria_conjunta.agregar_opcion("Comenzar de nuevo", "jason_dificil_final_redencion", stat="reputacion", cambio=40)
        self.historia["jason_dificil_victoria_conjunta"] = jason_victoria_conjunta

        jason_cierre_final = NodoHistoria(
            "jason_dificil_cierre_final",
            "EL CIERRE",
            "Con el Joker en Arkham, sientes algo que no has sentido en años: cierre. No es paz perfecta, pero es algo. Batman "
            "coloca una mano en tu hombro. 'Lo logramos,' dice. 'Juntos.' Miras hacia Gotham. Tu ciudad. La ciudad que proteges. "
            "No como Robin. Como Red Hood. Y eso está bien.",
            "dificil_cierre_final.png"
        )
        jason_cierre_final.agregar_opcion("Aceptar el cierre", "jason_dificil_final_antiheroico", stat="reputacion", cambio=30)
        self.historia["jason_dificil_cierre_final"] = jason_cierre_final

        jason_recuperacion_heroica = NodoHistoria(
            "jason_dificil_recuperacion_heroica",
            "RECUPERACIÓN DEL HÉROE",
            "Semanas en el hospital. Quemaduras graves pero sanarán. Batman te visita todos los días. Dick trae flores. Alfred "
            "trae comida casera. Incluso Damian gruñe algo que podría ser 'recuperate pronto'. Estás rodeado de familia. Y por "
            "primera vez, te permites sentirlo. Eres Red Hood, pero también eres Jason Todd. Y eso está bien.",
            "dificil_recuperacion_heroica.png"
        )
        jason_recuperacion_heroica.agregar_opcion("Sanar completamente", "jason_dificil_final_redencion", stat="salud", cambio=40, stat2="reputacion", cambio2=30)
        self.historia["jason_dificil_recuperacion_heroica"] = jason_recuperacion_heroica

        jason_ejecucion_perfecta = NodoHistoria(
            "jason_dificil_ejecucion_perfecta",
            "EJECUCIÓN PERFECTA",
            "El plan se ejecuta perfectamente. Cada trampa del Joker, anticipada. Cada escape, bloqueado. En menos de una hora, "
            "lo tienes capturado. Está en shock. 'Imposible,' murmura. 'Muy posible,' respondes. 'Aprendí de mis errores.' "
            "Lo entregas a las autoridades. Victoria total sin cruzar líneas. Has ganado en todos los sentidos.",
            "dificil_ejecucion_perfecta.png"
        )
        jason_ejecucion_perfecta.agregar_opcion("Disfrutar la victoria", "jason_dificil_final_redencion", stat="reputacion", cambio=40)
        self.historia["jason_dificil_ejecucion_perfecta"] = jason_ejecucion_perfecta


        # FINALES DEL MODO DIFÍCIL (3 finales)


        jason_final_redencion = NodoHistoria(
            "jason_dificil_final_redencion",
            "BAJO LA CAPUCHA ROJA - REDENCIÓN",
            "Has encontrado tu camino entre la oscuridad de Red Hood y la luz de Robin. Batman y tú llegan a un acuerdo: protegerás "
            "Gotham a tu manera, pero sin cruzar ciertas líneas. Es difícil, pero con su apoyo, puedes hacerlo. Has vuelto a casa. "
            "No como Robin, sino como Red Hood. La familia está completa de nuevo. Gotham tiene dos protectores diferentes pero "
            "igualmente dedicados. Y Jason Todd, después de años de oscuridad, ha encontrado su luz. La historia continúa, pero "
            "esta vez, con esperanza.",
            "final_redencion.png"
        )
        jason_final_redencion.es_final = True
        self.historia["jason_dificil_final_redencion"] = jason_final_redencion

        jason_final_oscuridad = NodoHistoria(
            "jason_dificil_final_oscuridad",
            "BAJO LA CAPUCHA ROJA - OSCURIDAD TOTAL",
            "Te alejas de Batman. Gotham ahora te teme tanto como a los criminales que cazas. Red Hood se convierte en leyenda: "
            "el vigilante que la justicia olvidó. Solo, violento, efectivo... pero perdido para siempre. Batman intenta detenerte "
            "repetidamente pero siempre escapas. La Bat-familia te considera perdido. Alfred llora por ti. Has obtenido tu venganza, "
            "has limpiado las calles a tu manera, pero el costo fue tu humanidad. Miras tu reflejo en el casco rojo y ya no reconoces "
            "al niño de Crime Alley. Jason Todd está verdaderamente muerto. Solo queda Red Hood. Y la oscuridad.",
            "final_oscuridad.png"
        )
        jason_final_oscuridad.es_final = True
        self.historia["jason_dificil_final_oscuridad"] = jason_final_oscuridad

        jason_final_antiheroico = NodoHistoria(
            "jason_dificil_final_antiheroico",
            "BAJO LA CAPUCHA ROJA - EL ANTIHÉROE",
            "No eres héroe ni villano. Eres Red Hood, algo en el medio. Gotham te necesita, aunque no lo admita. Batman desaprueba "
            "algunos de tus métodos, pero respeta tu determinación y tu código. Sigues tu propio camino, proteges a los inocentes "
            "a tu manera. Los criminales te temen, los débiles te respetan, la policía no sabe qué hacer contigo. Tienes aliados: "
            "los Outlaws, algunos miembros de la Bat-familia, contactos en las calles. No es la vida que imaginaste cuando eras "
            "Robin, pero es la vida que construiste. Eres Red Hood, el antihéroe de Gotham. Y para ti, para esta ciudad, es suficiente. "
            "La capucha roja no es una maldición, es una elección. Tu elección. Y la seguirás usando con orgullo.",
            "final_antiheroe.png"
        )
        jason_final_antiheroico.es_final = True
        self.historia["jason_dificil_final_antiheroico"] = jason_final_antiheroico











    def inicializar_historias_nightwing(self):
        """Crear todos los nodos de historia para Dick Grayson/Nightwing"""

        # La clase NodoHistoria se asume definida en otra parte con la siguiente estructura:
        # NodoHistoria(id, titulo, texto, imagen)
        # .agregar_opcion(texto, destino_id, stat, cambio, stat2, cambio2, item)

        # MODO FÁCIL: EL CHICO MARAVILLA (20 nodos)

        grayson_inicio = NodoHistoria(
            "grayson_facil_inicio",
            "HALY'S CIRCUS - LA TRAGEDIA",
            "El trueno y la lluvia golpean la carpa. Eres Dick Grayson, el más joven de los 'Flying Graysons', "
            "la joya de Haly's Circus. En lo alto, en el trapecio, sientes la adrenalina. Pero algo va mal. "
            "Escuchas un crujido. Las cuerdas se rompen. Tus padres caen. Es un sabotaje. "
            "Despiertas en una habitación de hospital. Un hombre alto y sombrío, Bruce Wayne, te observa.",
            "circus_tragedy.png"
        )
        grayson_inicio.agregar_opcion("Preguntar por el responsable del sabotaje", "grayson_facil_ira", stat="reputacion", cambio=-5)
        grayson_inicio.agregar_opcion("Aceptar la tutela de Bruce Wayne en silencio", "grayson_facil_manor", stat="recursos", cambio=1)
        grayson_inicio.agregar_opcion("Llorar la pérdida con Alfred (Enfermero)", "grayson_facil_consuelo", stat="salud", cambio=5)
        self.historia["grayson_facil_inicio"] = grayson_inicio

        grayson_ira = NodoHistoria(
            "grayson_facil_ira",
            "EL FUEGO INTERIOR",
            "Bruce te mira con comprensión. 'La policía está investigando, Dick. Prometo que se hará justicia.' "
            "Pero la justicia de la policía no es lo que quieres. Quieres *venganza*. Te mudas a la Mansión Wayne, "
            "pero Gotham te asfixia. No es el aire abierto del circo. Es una jaula de oro. "
            "Tu única meta es encontrar al responsable.",
            "dick_anger.png"
        )
        grayson_ira.agregar_opcion("Comenzar tu propia investigación", "grayson_facil_investigacion_secreta", stat="recursos", cambio=1)
        grayson_ira.agregar_opcion("Desahogar tu frustración entrenando en el gimnasio", "grayson_facil_entrenamiento_manor", stat="salud", cambio=10)
        self.historia["grayson_facil_ira"] = grayson_ira

        grayson_consuelo = NodoHistoria(
            "grayson_facil_consuelo",
            "EL HOGAR DE ALFRED",
            "Alfred, el mayordomo, te da un té caliente. 'El dolor es inevitable, Maestro Dick, pero el "
            "sufrimiento es una elección. Permítase sentir el dolor, y luego elija la luz.' "
            "Sus palabras son un bálsamo. Te mudas a la Mansión Wayne. Alfred es lo más cercano a una familia "
            "que te queda.",
            "alfred_comfort.png"
        )
        grayson_consuelo.agregar_opcion("Aceptar la ayuda de Alfred y centrarte en adaptarte", "grayson_facil_manor", stat="reputacion", cambio=10)
        self.historia["grayson_facil_consuelo"] = grayson_consuelo

        grayson_manor = NodoHistoria(
            "grayson_facil_manor",
            "LA MANSIÓN WAYNE",
            "La Mansión es gigantesca y vacía. Bruce Wayne es distante, siempre ocupado. Es como si él "
            "también estuviera lidiando con un dolor silencioso. Te sientes solo y aburrido. "
            "Un día, mientras exploras, encuentras una puerta oculta detrás de la chimenea de la oficina de Bruce. "
            "La curiosidad te vence.",
            "wayne_manor.png"
        )
        grayson_manor.agregar_opcion("Ignorar la puerta, respetar la privacidad de Bruce", "grayson_facil_entrenamiento_manor", stat="reputacion", cambio=5)
        grayson_manor.agregar_opcion("Investigar el mecanismo de la puerta", "grayson_facil_descubrimiento_cueva", stat="recursos", cambio=2)
        self.historia["grayson_facil_manor"] = grayson_manor

        grayson_investigacion_secreta = NodoHistoria(
            "grayson_facil_investigacion_secreta",
            "PISTAS SUBTERRÁNEAS",
            "Usas tus habilidades de observación de circo para encontrar información. Descubres que tu familia "
            "se negó a pagar una cuota de protección a un gánster local: Tony Zucco. "
            "Zucco organizó el sabotaje. Intentas contárselo a Bruce, pero está inusualmente ausente. "
            "Necesitas pruebas.",
            "dick_investigation.png"
        )
        grayson_investigacion_secreta.agregar_opcion("Buscar la oficina de Bruce en busca de 'archivos'", "grayson_facil_descubrimiento_cueva", stat="recursos", cambio=1)
        grayson_investigacion_secreta.agregar_opcion("Intentar infiltrarte en la base de Zucco por tu cuenta", "grayson_facil_intento_venganza", stat="salud", cambio=-10)
        self.historia["grayson_facil_investigacion_secreta"] = grayson_investigacion_secreta

        grayson_entrenamiento_manor = NodoHistoria(
            "grayson_facil_entrenamiento_manor",
            "LA ENERGÍA DEL ACROBATA",
            "Canalizas tu energía en el gimnasio, practicando tus movimientos acrobáticos. Es la única vez "
            "que te sientes libre. Alfred te observa, impresionado. 'Maestro Dick, usted tiene un don natural. "
            "Un día, ese talento podría salvarle la vida.'",
            "dick_training_acro.png"
        )
        grayson_entrenamiento_manor.agregar_opcion("Seguir practicando y esperar una oportunidad para ayudar", "grayson_facil_misterio_bruce", stat="salud", cambio=5)
        self.historia["grayson_facil_entrenamiento_manor"] = grayson_entrenamiento_manor

        grayson_intento_venganza = NodoHistoria(
            "grayson_facil_intento_venganza",
            "EL PRIMER GOLPE",
            "Te pones una máscara de carnaval y te diriges a los muelles, buscando a Zucco. Eres rápido, "
            "pero no tienes entrenamiento. Unos matones te atrapan fácilmente. Te golpean y te dejan "
            "en un callejón. Justo antes de perder la conciencia, una sombra te recoge. Es Batman.",
            "dick_alone_attack.png"
        )
        grayson_intento_venganza.agregar_opcion("Aceptar la ayuda de Batman a regañadientes", "grayson_facil_revelacion_forzada", stat="reputacion", cambio=10, stat2="salud", cambio2=-15)
        self.historia["grayson_facil_intento_venganza"] = grayson_intento_venganza

        grayson_misterio_bruce = NodoHistoria(
            "grayson_facil_misterio_bruce",
            "LAS NOCHES DE AUSENCIA",
            "Notas que Bruce siempre está ausente por la noche. Sus horarios son irregulares, y siempre "
            "vuelve agotado. Una noche, lo sigues. Viste cómo salía de la Mansión, pero no en su auto. "
            "Se dirigía hacia los viejos establos. Lo sigues a pie, usando tus habilidades de sigilo.",
            "bruce_mystery.png"
        )
        grayson_misterio_bruce.agregar_opcion("Seguirlo hasta el final", "grayson_facil_descubrimiento_cueva", stat="recursos", cambio=1)
        self.historia["grayson_facil_misterio_bruce"] = grayson_misterio_bruce

        grayson_descubrimiento_cueva = NodoHistoria(
            "grayson_facil_descubrimiento_cueva",
            "EL DESCENSO",
            "La puerta oculta cede o el camino hacia los establos te guía. Desciendes. El aire es frío, "
            "húmedo y huele a murciélago. El impacto visual te quita el aliento: la Batcueva. "
            "Tecnología, vehículos, y en el centro, el traje de Batman. Te das cuenta: Bruce Wayne "
            "es el Caballero Oscuro. Bruce te encuentra allí, con la capucha en la mano.",
            "batcave_reveal.png"
        )
        grayson_descubrimiento_cueva.agregar_opcion("Preguntar sobre Tony Zucco y tus padres", "grayson_facil_revelacion", stat="reputacion", cambio=15)
        grayson_descubrimiento_cueva.agregar_opcion("Preguntar por qué no te lo dijo antes", "grayson_facil_revelacion", stat="reputacion", cambio=5)
        self.historia["grayson_facil_descubrimiento_cueva"] = grayson_descubrimiento_cueva

        grayson_revelacion_forzada = NodoHistoria(
            "grayson_facil_revelacion_forzada",
            "LA CONFRONTACIÓN",
            "Despiertas en la enfermería de la Batcueva. ¡La Batcueva! Bruce está allí, sin su máscara. "
            "'Pudiste haber muerto, Dick,' dice, su voz llena de gravedad. 'La venganza te consumirá.' "
            "Pero él entiende el dolor. Te cuenta su propia historia. 'El sabotaje de Zucco fue mi fracaso. "
            "Déjame entrenarte para que no cometas el mismo error que yo... que ir solo.'",
            "batman_talk.png"
        )
        grayson_revelacion_forzada.agregar_opcion("Aceptar el entrenamiento para vengar a tus padres", "grayson_facil_entrenamiento_robin", stat="reputacion", cambio=10)
        self.historia["grayson_facil_revelacion_forzada"] = grayson_revelacion_forzada

        grayson_revelacion = NodoHistoria(
            "grayson_facil_revelacion",
            "EL HUECO DE BATMAN",
            "Bruce te cuenta su historia: el asesinato de sus padres en Crime Alley. Él te entiende mejor "
            "que nadie. 'No puedo permitir que caigas en la oscuridad,' te dice. 'Pero no estás solo. "
            "Necesito a alguien que pueda mirar a Gotham con esperanza, alguien que me recuerde la luz.' "
            "Él no te ofrece venganza, te ofrece *propósito*.",
            "batman_offer.png"
        )
        grayson_revelacion.agregar_opcion("Aceptar el entrenamiento y el propósito", "grayson_facil_entrenamiento_robin", stat="reputacion", cambio=20, item="Propósito Renovado")
        self.historia["grayson_facil_revelacion"] = grayson_revelacion

        grayson_entrenamiento_robin = NodoHistoria(
            "grayson_facil_entrenamiento_robin",
            "EL DÚO DINÁMICO NACE",
            "El entrenamiento es brutal, pero tienes un don natural para el combate y la agilidad. "
            "Bruce te enseña estrategia, Alfred te enseña primeros auxilios y tacto social. "
            "Pero la especialización es tuya. ¿Qué camino tomas?",
            "batman_and_dick_train.png"
        )
        grayson_entrenamiento_robin.agregar_opcion("Acrobacia y Agilidad: perfeccionar tus movimientos de circo", "grayson_facil_especialidad_acrobacia", stat="salud", cambio=15, item="Agilidad Superior")
        grayson_entrenamiento_robin.agregar_opcion("Detective Work y Tecnología: usar la Batcueva para encontrar a Zucco", "grayson_facil_especialidad_detective", stat="recursos", cambio=3, item="Lupa Forense")
        self.historia["grayson_facil_entrenamiento_robin"] = grayson_entrenamiento_robin

        grayson_especialidad_acrobacia = NodoHistoria(
            "grayson_facil_especialidad_acrobacia",
            "EL ARTE DEL MOVIMIENTO",
            "Te conviertes en un fantasma en el aire. Tu estilo es elegante, fluido, completamente diferente "
            "al de Bruce. 'Tu movimiento es tu arma más grande, Dick,' te dice. 'Te hace impredecible.' "
            "Te sientes listo. Sabes que puedes hacer la diferencia en las calles.",
            "dick_acrobatics.png"
        )
        grayson_especialidad_acrobacia.agregar_opcion("Espera el llamado de Batman", "grayson_facil_traje", stat="reputacion", cambio=10)
        self.historia["grayson_facil_especialidad_acrobacia"] = grayson_especialidad_acrobacia

        grayson_especialidad_detective = NodoHistoria(
            "grayson_facil_especialidad_detective",
            "EL OJO DEL DETECTIVE",
            "Trabajas con Bruce en la Batcomputadora. Analizas patrones de crimen y las finanzas de Zucco. "
            "Descubres una debilidad en su operación. 'Tu mente es aguda, Dick,' reconoce Batman. "
            "'Necesito esa perspectiva.' Tu venganza se convierte en una operación de justicia bien planeada.",
            "dick_detective.png"
        )
        grayson_especialidad_detective.agregar_opcion("Establece la emboscada a Zucco", "grayson_facil_traje", stat="recursos", cambio=2)
        self.historia["grayson_facil_especialidad_detective"] = grayson_especialidad_detective

        grayson_traje = NodoHistoria(
            "grayson_facil_traje",
            "EL MANTO DE ROBIN",
            "Bruce te llama a la plataforma central. Sobre una mesa está el traje: rojo, verde y amarillo. "
            "'Es un uniforme de circo,' dices, sonriendo. 'Eso es intencional,' responde Bruce. 'Es una "
            "declaración. Eres el símbolo de la esperanza y la luz, un Boy Wonder. ¿Listo para volar de nuevo?'",
            "robin_suit_dick.png"
        )
        grayson_traje.agregar_opcion("Ponerte el traje de Robin con alegría", "grayson_facil_primera_mision_z", stat="reputacion", cambio=25, item="Traje de Robin (Original)")
        self.historia["grayson_facil_traje"] = grayson_traje

        grayson_primera_mision_z = NodoHistoria(
            "grayson_facil_primera_mision_z",
            "LA CAZA DE ZUCCO",
            "La primera noche. Sobre los tejados de Gotham, eres libre de nuevo. Batman te guía hasta los muelles, "
            "donde Tony Zucco está cerrando un trato. 'Recuerda el código, Robin,' advierte Batman. 'Justicia, "
            "no venganza. Zucco es mío, pero tú te encargarás de la distracción y los matones.'",
            "robin_patrol_z.png"
        )
        grayson_primera_mision_z.agregar_opcion("Seguir el plan de Batman (Neutralizar a los matones con precisión)", "grayson_facil_plan_cumplido", stat="reputacion", cambio=10)
        grayson_primera_mision_z.agregar_opcion("Usar un movimiento de circo arriesgado para capturar a Zucco primero", "grayson_facil_impulso_z", stat="salud", cambio=-5)
        self.historia["grayson_facil_primera_mision_z"] = grayson_primera_mision_z

        grayson_plan_cumplido = NodoHistoria(
            "grayson_facil_plan_cumplido",
            "SINCRONÍA PERFECTA",
            "Te mueves con la gracia de un acróbata, inmovilizando a los matones con nunchakus y trucos de cuerda. "
            "Cuando terminas, Zucco está en el suelo, golpeado y esposado por Batman. 'Bien hecho, Robin. "
            "Precisión y control.' Miras a Zucco, el asesino de tus padres, ahora inofensivo. La venganza se "
            "siente vacía, pero la justicia... la justicia te llena de paz. Tony Zucco va a la cárcel.",
            "zッコ_captured.png"
        )
        grayson_plan_cumplido.agregar_opcion("Aceptar tu nuevo rol como Robin", "grayson_facil_crecimiento", stat="reputacion", cambio=15, item="Legado de los Graysons")
        self.historia["grayson_facil_plan_cumplido"] = grayson_plan_cumplido

        grayson_impulso_z = NodoHistoria(
            "grayson_facil_impulso_z",
            "EL TRUCO ARRIESGADO",
            "Ignoras a Batman y usas el Bat-gancho para balancearte directamente hacia Zucco. Lo derribas, "
            "pero sus matones te disparan mientras Batman está ocupado con los otros. Recibes un rasguño, "
            "pero Zucco escapa en medio de la confusión. Batman te ayuda a levantarte: 'Tu agilidad "
            "es incomparable, pero la estrategia es vital, Dick. Ahora Zucco se ha ido.'",
            "robin_impulse_z.png"
        )
        grayson_impulso_z.agregar_opcion("Pedir perdón y continuar la caza de Zucco", "grayson_facil_caza_extendida", stat="reputacion", cambio=-10, stat2="salud", cambio2=-5)
        self.historia["grayson_facil_impulso_z"] = grayson_impulso_z

        grayson_caza_extendida = NodoHistoria(
            "grayson_facil_caza_extendida",
            "LECCIONES APRENDIDAS",
            "Batman y tú pasan las siguientes semanas cazando a Zucco, que está escondido. Finalmente, "
            "lo encuentran intentando huir de Gotham. Esta vez, sigues cada orden de Batman. "
            "Zucco es capturado. 'El trabajo en equipo salva vidas, Dick,' te dice Batman. 'Lo hicimos juntos.' "
            "La satisfacción es real. Finalmente, paz.",
            "zッコ_captured_2.png"
        )
        grayson_caza_extendida.agregar_opcion("Regresar a Gotham como un Dúo Dinámico", "grayson_facil_crecimiento", stat="reputacion", cambio=15)
        self.historia["grayson_facil_caza_extendida"] = grayson_caza_extendida

        grayson_crecimiento = NodoHistoria(
            "grayson_facil_crecimiento",
            "ROBIN, EL SÍMBOLO",
            "El Dúo Dinámico es una realidad. Robin se convierte en un símbolo de esperanza, un contraste "
            "al miedo que infunde Batman. Las personas te ven y sonríen. En una ocasión, "
            "una niña te regala una flor de plástico: 'Gracias, Robin, por hacer que los malos teman a los colores.' "
            "Ya no eres solo un huérfano. Eres Robin, y encontraste un nuevo hogar.",
            "robin_symbol.png"
        )
        grayson_crecimiento.agregar_opcion("Continuar protegiendo Gotham como el Chico Maravilla", "grayson_facil_final", stat="reputacion", cambio=20)
        self.historia["grayson_facil_crecimiento"] = grayson_crecimiento

        grayson_final_facil = NodoHistoria(
            "grayson_facil_final",
            "EL PRIMER ROBIN - FINAL FÁCIL",
            "Los años pasan. Te graduaste como Robin, el socio perfecto de Batman. Tu estilo acrobático "
            "y tu optimismo son la luz que Gotham necesita. Has encontrado paz con la muerte de tus padres, "
            "canalizando tu dolor en justicia. Bruce te considera su hijo. Alfred te considera su nieto. "
            "Un día, Bruce te mira en el gimnasio: 'Estás listo para algo más, Dick. Listo para tu "
            "propio camino.' Sabes que un día, dejarás la 'R' y encontrarás un nuevo símbolo. "
            "Pero por ahora, eres el inigualable Chico Maravilla, la chispa de esperanza de Gotham. Tu historia "
            "como el Dúo Dinámico apenas comienza.",
            "final_robin_dick.png"
        )
        grayson_final_facil.es_final = True
        self.historia["grayson_facil_final"] = grayson_final_facil

        # MODO NORMAL: EL CAMINO SOLITARIO (NIGHTWING) (40 nodos)

        grayson_inicio_normal = NodoHistoria(
            "grayson_normal_inicio",
            "LA SOMBRA DEL MURCIÉLAGO",
            "Han pasado varios años como Robin. Eres un héroe por derecho propio, pero te sientes estancado. "
            "Las reglas de 'no matar' y 'no cruzar la línea' de Batman te frustran cada vez más. "
            "Bruce se ha vuelto más controlador, más silencioso. La tensión en la Batcueva es palpable. "
            "Acabas de atrapar a un criminal que has visto escapar de Arkham tres veces.",
            "robin_older.png"
        )
        grayson_inicio_normal.agregar_opcion("Confrontar a Batman sobre la futilidad de sus métodos", "grayson_normal_conflicto", stat="reputacion", cambio=-10)
        grayson_inicio_normal.agregar_opcion("Buscar consejo en Alfred, tu confidente", "grayson_normal_alfred_consejo", stat="salud", cambio=5)
        grayson_inicio_normal.agregar_opcion("Silenciar tus dudas y seguir sus órdenes", "grayson_normal_supresion", stat="reputacion", cambio=5)
        self.historia["grayson_normal_inicio"] = grayson_inicio_normal

        grayson_conflicto = NodoHistoria(
            "grayson_normal_conflicto",
            "LA RUPTURA IDEOLÓGICA",
            "Bruce se quita la capucha con furia. '¡Mis reglas son lo único que nos diferencia de ellos, Dick!' "
            "Argumentas que la reincidencia de los criminales es culpa de esa regla. El debate es acalorado. "
            "'Si no puedes respetar el código,' dice finalmente Bruce, 'entonces no puedes ser Robin.' "
            "Te quitas la 'R' y la dejas caer al suelo. Te vas de la Mansión. Eres libre... y solo.",
            "dick_leaving.png"
        )
        grayson_conflicto.agregar_opcion("Ir a Blüdhaven, una nueva ciudad que necesita un héroe", "grayson_normal_bludhaven_inicio", stat="recursos", cambio=-5)
        grayson_conflicto.agregar_opcion("Quedarte en Gotham, pero crear una nueva identidad (Nightwing)", "grayson_normal_nightwing_gotham", stat="reputacion", cambio=15, item="Nuevo Traje (Prototipo)")
        self.historia["grayson_normal_conflicto"] = grayson_conflicto

        grayson_alfred_consejo = NodoHistoria(
            "grayson_normal_alfred_consejo",
            "LA SABIDURÍA DEL MAYORDOMO",
            "Alfred te escucha en silencio mientras tomas el té. 'Maestro Dick, su padre adoptivo le ama. "
            "Pero el amor no siempre se traduce en el mismo camino. Usted es una luz, y las luces "
            "deben brillar en su propia órbita. Quizás su camino está fuera de Gotham, o quizás "
            "necesita un nuevo nombre para forjar su propia leyenda.'",
            "alfred_advice.png"
        )
        grayson_alfred_consejo.agregar_opcion("Buscar un nuevo nombre y ciudad", "grayson_normal_bludhaven_inicio", stat="recursos", cambio=1)
        grayson_alfred_consejo.agregar_opcion("Intentar mediar con Batman primero", "grayson_normal_intento_reconciliacion", stat="reputacion", cambio=10)
        self.historia["grayson_normal_alfred_consejo"] = grayson_alfred_consejo

        grayson_supresion = NodoHistoria(
            "grayson_normal_supresion",
            "ENCERRANDO LA LUZ",
            "Ignoras tu instinto. Sigues las órdenes de Batman al pie de la letra, pero cada noche se siente "
            "más fría. Tu sonrisa se desvanece. Batman nota tu cambio, tu falta de pasión. "
            "'Dick, ¿estás bien?' te pregunta, pero no puedes responder honestamente. Sientes que el traje "
            "de Robin te asfixia. Un día, una nueva ciudad, Blüdhaven, pide ayuda.",
            "robin_sad.png"
        )
        grayson_supresion.agregar_opcion("Ofrecerte a ayudar en Blüdhaven como Robin", "grayson_normal_bludhaven_inicio", stat="reputacion", cambio=5)
        grayson_supresion.agregar_opcion("Pedir un nuevo nombre/identidad a Batman", "grayson_normal_intento_reconciliacion", stat="recursos", cambio=1)
        self.historia["grayson_normal_supresion"] = grayson_supresion

        grayson_intento_reconciliacion = NodoHistoria(
            "grayson_normal_intento_reconciliacion",
            "LA DISCUSIÓN SILENCIOSA",
            "Hablas con Bruce. 'Necesito crecer, Bruce. Necesito mi propia identidad.' "
            "Bruce lo considera. 'Si te vas, te vas solo. Pero puedo ayudarte a financiar un nuevo traje. "
            "Ve a Blüdhaven, Dick. Prueba tu propia leyenda.' Aceptas. Es un adiós agridulce. "
            "Empacas tus cosas y Alfred te da un último abrazo.",
            "reconciliation_talk.png"
        )
        grayson_intento_reconciliacion.agregar_opcion("Ir a Blüdhaven con un nuevo traje y nombre (Nightwing)", "grayson_normal_bludhaven_inicio", stat="reputacion", cambio=15, item="Traje de Nightwing (Inicial)")
        self.historia["grayson_normal_intento_reconciliacion"] = grayson_intento_reconciliacion

        grayson_nightwing_gotham = NodoHistoria(
            "grayson_normal_nightwing_gotham",
            "NACIMIENTO DE NIGHTWING EN GOTHAM",
            "Te quedas en Gotham, pero el traje de Robin se queda en la Batcueva. Creas un nuevo traje, "
            "azul y negro, y adoptas el nombre que Superman te dio: Nightwing. "
            "Patrullas los distritos bajos de Gotham que Batman ignora. Eres más rápido, más libre, "
            "pero la sombra de Batman sigue presente. La gente te llama 'El Robin Azul'.",
            "nightwing_gotham.png"
        )
        grayson_nightwing_gotham.agregar_opcion("Continuar tu misión en Gotham, ignorando a Batman", "grayson_normal_gotham_independiente", stat="reputacion", cambio=10)
        grayson_nightwing_gotham.agregar_opcion("Decidir que necesitas un lugar realmente nuevo: Blüdhaven", "grayson_normal_bludhaven_inicio", stat="recursos", cambio=1)
        self.historia["grayson_normal_nightwing_gotham"] = grayson_nightwing_gotham

        grayson_bludhaven_inicio = NodoHistoria(
            "grayson_normal_bludhaven_inicio",
            "EL HÉROE DE BLÜDHAVEN",
            "Llegas a Blüdhaven. Una ciudad portuaria, más sucia y desesperada que Gotham. Aquí, nadie "
            "conoce a Batman, y el nombre de Robin no significa nada. Te alojas en un pequeño apartamento. "
            "Esta noche, mientras patrullas, ves a unos matones atacando a una pareja. Es tu primera "
            "oportunidad de ser el único héroe de la ciudad.",
            "bludhaven_first_night.png"
        )
        grayson_bludhaven_inicio.agregar_opcion("Usar un ataque acrobático para asustarlos y neutralizarlos rápidamente", "grayson_normal_blud_acrobacia", stat="reputacion", cambio=15)
        grayson_bludhaven_inicio.agregar_opcion("Usar tus palos de eskrima para someterlos con brutalidad y autoridad", "grayson_normal_blud_brutalidad", stat="salud", cambio=5)
        self.historia["grayson_normal_bludhaven_inicio"] = grayson_bludhaven_inicio

        grayson_blud_acrobacia = NodoHistoria(
            "grayson_normal_blud_acrobacia",
            "EL PÁJARO EN EL CIELO",
            "Te balanceas desde el techo con una voltereta triple, aterrizando en medio de ellos. "
            "Están desorientados. Usas tu agilidad para esquivar golpes y atar a los matones con una cuerda. "
            "La pareja te agradece, asombrada. '¿Quién eres?' preguntan. 'Soy Nightwing,' respondes. "
            "Una leyenda nace.",
            "nightwing_pose.png"
        )
        grayson_blud_acrobacia.agregar_opcion("Establecer tu reputación de héroe ágil", "grayson_normal_fama_bludhaven", stat="reputacion", cambio=20)
        self.historia["grayson_normal_blud_acrobacia"] = grayson_blud_acrobacia

        grayson_blud_brutalidad = NodoHistoria(
            "grayson_normal_blud_brutalidad",
            "UNA MANO DURA",
            "Usas tus palos de eskrima para romper huesos y dejar a los matones sangrando en el callejón. "
            "Son neutralizados, sí, pero la pareja rescatada te mira con miedo. 'Gracias...' murmura "
            "el hombre. Te das cuenta de que has cruzado la línea, aunque solo sea un poco. "
            "Te preguntas si te estás pareciendo demasiado a Bruce en sus peores días.",
            "nightwing_brutal.png"
        )
        grayson_blud_brutalidad.agregar_opcion("Reflexionar sobre tus métodos y buscar el equilibrio", "grayson_normal_fama_bludhaven", stat="salud", cambio=-5)
        self.historia["grayson_normal_blud_brutalidad"] = grayson_blud_brutalidad

        grayson_fama_bludhaven = NodoHistoria(
            "grayson_normal_fama_bludhaven",
            "NIGHTWING SE ELEVA",
            "Te conviertes rápidamente en el protector de Blüdhaven. La policía local te ve con desconfianza, "
            "pero la gente te idolatra. Eres el héroe que salta y sonríe, el que da esperanza. "
            "Has encontrado tu propia voz, tu propio camino. Pero tu pasado llama: el Joker escapa, "
            "y se dirige directamente a Blüdhaven. Sabe que te dolió dejar a Batman.",
            "nightwing_city_view.png"
        )
        grayson_fama_bludhaven.agregar_opcion("Llamar a Batman para advertirle (Trabajo en equipo)", "grayson_normal_joker_equipo", stat="reputacion", cambio=10)
        grayson_fama_bludhaven.agregar_opcion("Enfrentar al Joker solo para demostrar tu independencia", "grayson_normal_joker_solo", stat="recursos", cambio=-3)
        self.historia["grayson_normal_fama_bludhaven"] = grayson_fama_bludhaven

        grayson_gotham_independiente = NodoHistoria(
            "grayson_normal_gotham_independiente",
            "NACIMIENTO DE NIGHTWING EN GOTHAM",
            "Te quedas en Gotham, pero el traje de Robin se queda en la Batcueva. Creas un nuevo traje, "
            "azul y negro, y adoptas el nombre que Superman te dio: Nightwing. "
            "Patrullas los distritos bajos de Gotham que Batman ignora. Eres más rápido, más libre, "
            "pero la sombra de Batman sigue presente. La gente te llama 'El Robin Azul'.",
            "nightwing_gotham.png"
        )
        grayson_gotham_independiente.agregar_opcion("Continuar tu misión en Gotham, ignorando a Batman", "grayson_normal_gotham_independiente", stat="reputacion", cambio=10)
        grayson_gotham_independiente.agregar_opcion("Decidir que necesitas un lugar realmente nuevo: Blüdhaven", "grayson_normal_bludhaven_inicio", stat="recursos", cambio=1)
        self.historia["grayson_normal_gotham_independiente"] = grayson_gotham_independiente


        grayson_joker_equipo = NodoHistoria(
            "grayson_normal_joker_equipo",
            "LLAMADA DE AUXILIO A GOTHAM",
            "Llamas a Batman con el protocolo de emergencia, tragándote tu orgullo. 'El Joker está en Blüdhaven. "
            "Viene por mí. Ven a ayudar.' Batman llega a la ciudad. La gente te ve trabajar "
            "junto al Caballero Oscuro, pero nota tu reticencia. El Joker ataca el muelle. "
            "'¡El Chico Maravilla Azul no se atreve solo!' se burla el Joker.",
            "nightwing_and_batman.png"
        )
        grayson_joker_equipo.agregar_opcion("Trabajar en equipo y neutralizar al Joker de forma limpia", "grayson_normal_joker_capturado_equipo", stat="reputacion", cambio=15)
        grayson_joker_equipo.agregar_opcion("Demostrar tu valía tomando la delantera en el asalto", "grayson_normal_joker_conflicto_bruce", stat="salud", cambio=-10)
        self.historia["grayson_normal_joker_equipo"] = grayson_joker_equipo

        grayson_joker_solo = NodoHistoria(
            "grayson_normal_joker_solo",
            "EL ENCUENTRO SOLITARIO",
            "Te niegas a pedir ayuda. El Joker te encuentra en tu apartamento. '¡Dickie, creciste! ¡Qué pena "
            "que solo te fuiste a una versión más barata de Gotham!' El Joker ha llenado la plaza de "
            "Globos con veneno. El tiempo corre. Tienes que detenerlo tú solo, y no puedes fallar.",
            "nightwing_vs_joker.png"
        )
        grayson_joker_solo.agregar_opcion("Usar tu agilidad para desactivar los globos rápidamente antes de enfrentarlo", "grayson_normal_joker_capturado_solo_rapido", stat="recursos", cambio=5)
        grayson_joker_solo.agregar_opcion("Confrontarlo directamente y arriesgarte a que exploten los globos", "grayson_normal_joker_capturado_solo_lento", stat="salud", cambio=-20)
        self.historia["grayson_normal_joker_solo"] = grayson_joker_solo

        grayson_joker_capturado_equipo = NodoHistoria(
            "grayson_normal_joker_capturado_equipo",
            "EL TRABAJO BIEN HECHO",
            "Sigues las órdenes de Batman, moviéndote como si fueran uno solo. Atrapan al Joker y lo envían "
            "de vuelta a Arkham. Bruce te da una palmada en el hombro. 'Buen trabajo, Nightwing. "
            "Me alegro de que me hayas llamado.' Te sientes agradecido, pero la sombra sigue allí. "
            "Tu ciudad es Blüdhaven, no Gotham, y sus problemas son diferentes.",
            "joker_caged_batwing.png"
        )
        grayson_joker_capturado_equipo.agregar_opcion("Aceptar el agradecimiento y regresar a tus propias misiones", "grayson_normal_el_bloque", stat="reputacion", cambio=10)
        self.historia["grayson_normal_joker_capturado_equipo"] = grayson_joker_capturado_equipo

        grayson_joker_conflicto_bruce = NodoHistoria(
            "grayson_normal_joker_conflicto_bruce",
            "EL HÉROE QUE LUCHA POR SU INDEPENDENCIA",
            "Te lanzas primero, en una exhibición acrobática impresionante. Desvías la atención del Joker, "
            "permitiendo a Batman neutralizar la amenaza principal. El Joker se enfoca en ti. "
            "'¡El chico que quería ser un hombre! ¡Qué patético!' Te golpea, pero Batman interviene. "
            "El Joker es capturado, pero Bruce te regaña: 'Fue innecesario. Puso a Blüdhaven en peligro.'",
            "batman_scolding.png"
        )
        grayson_joker_conflicto_bruce.agregar_opcion("Disculparte y reafirmar tu independencia", "grayson_normal_el_bloque", stat="salud", cambio=-5, stat2="reputacion", cambio2=5)
        self.historia["grayson_normal_joker_conflicto_bruce"] = grayson_joker_conflicto_bruce

        grayson_joker_capturado_solo_rapido = NodoHistoria(
            "grayson_normal_joker_capturado_solo_rapido",
            "EL TRUCO DE LA DESACTIVACIÓN",
            "Usas una combinación de batarangs (o wingdings) y cuerdas para desactivar rápidamente los globos, "
            "evitando la catástrofe. El Joker te mira, genuinamente impresionado. "
            "'¡Tienes trucos nuevos, Dickie! ¡Pero Gotham te extraña!' Lo sometes. "
            "Demostraste que puedes manejarte solo. Blüdhaven te aclama.",
            "nightwing_solo_win.png"
        )
        grayson_joker_capturado_solo_rapido.agregar_opcion("Recibir el reconocimiento de la ciudad", "grayson_normal_el_bloque", stat="reputacion", cambio=25)
        self.historia["grayson_normal_joker_capturado_solo_rapido"] = grayson_joker_capturado_solo_rapido

        grayson_joker_capturado_solo_lento = NodoHistoria(
            "grayson_normal_joker_capturado_solo_lento",
            "UN COSTO ALTO POR LA INDEPENDENCIA",
            "Te enfrentas al Joker y lo golpeas con furia, pero él logra detonar unos cuantos globos antes de ser "
            "sometido. La toxina se dispersa, hiriendo a civiles y a ti mismo. Te recuperas, "
            "pero la gente de Blüdhaven te mira con resentimiento. Eres poderoso, sí, pero fallaste.",
            "nightwing_fail.png"
        )
        grayson_joker_capturado_solo_lento.agregar_opcion("Lidiar con las consecuencias de tus errores", "grayson_normal_el_bloque", stat="salud", cambio=-10, stat2="reputacion", cambio2=-5)
        self.historia["grayson_normal_joker_capturado_solo_lento"] = grayson_joker_capturado_solo_lento

        grayson_el_bloque = NodoHistoria(
            "grayson_normal_el_bloque",
            "BLÜDHAVEN: LA CORRUPCIÓN",
            "El Joker se ha ido, pero el crimen local resurge. Descubres que la policía de Blüdhaven, o **'El Bloque'**, "
            "está profundamente corrupta, dirigida por el jefe de policía, Dudley Soames, y financiada por "
            "una red de narcotraficantes. Te das cuenta de que no puedes trabajar con ellos. Debes derribar "
            "a la ley para salvar la ciudad.",
            "bludhaven_police.png"
        )
        grayson_el_bloque.agregar_opcion("Infiltrarte en la jefatura de policía y buscar pruebas (Sigilo)", "grayson_normal_infiltracion", stat="recursos", cambio=2)
        grayson_el_bloque.agregar_opcion("Exponer la corrupción de forma pública a través de medios de comunicación (Riesgo)", "grayson_normal_exposicion", stat="reputacion", cambio=10)
        grayson_el_bloque.agregar_opcion("Confrontar a Soames directamente en su oficina (Combate)", "grayson_normal_confrontacion_soames", stat="salud", cambio=5)
        self.historia["grayson_normal_el_bloque"] = grayson_el_bloque

        grayson_infiltracion = NodoHistoria(
            "grayson_normal_infiltracion",
            "EL ACROBATA NOCTURNO",
            "Usas tus habilidades de acróbata para entrar en la jefatura por el techo. El sigilo es tu aliado. "
            "Encuentras archivos que detallan el 'Plan Block', la operación de Soames. "
            "Un oficial te descubre y debes reducirlo sin ser detectado. Es un dilema ético.",
            "nightwing_stealth.png"
        )
        grayson_infiltracion.agregar_opcion("Reducirlo con un golpe aturdidor (No letal)", "grayson_normal_pruebas_obtenidas", stat="reputacion", cambio=15)
        grayson_infiltracion.agregar_opcion("Dejarlo inconsciente con más fuerza (Riesgo de daño permanente)", "grayson_normal_pruebas_obtenidas_brutal", stat="salud", cambio=-5)
        self.historia["grayson_normal_infiltracion"] = grayson_infiltracion

        grayson_exposicion = NodoHistoria(
            "grayson_normal_exposicion",
            "EL WHISTLEBLOWER",
            "Filtras tus sospechas a un periodista local. Funciona. La presión pública obliga a la alcaldía "
            "a investigar. Soames y 'El Bloque' se ponen a la defensiva. La ciudad es un polvorín. "
            "Tienes poco tiempo antes de que los corruptos destruyan la evidencia.",
            "nightwing_media.png"
        )
        grayson_exposicion.agregar_opcion("Presionar a Soames para que revele más información", "grayson_normal_confrontacion_soames", stat="recursos", cambio=1)
        self.historia["grayson_normal_exposicion"] = grayson_exposicion

        grayson_confrontacion_soames = NodoHistoria(
            "grayson_normal_confrontacion_soames",
            "FRENTE A FRENTE",
            "Te encuentras con Soames en su oficina. Es un hombre enorme y fuerte, con una sonrisa maliciosa. "
            "'El Robin que se escapó del gallinero,' se burla. 'Aquí no hay Batman para salvarte.' "
            "La pelea es brutal, no es un payaso. Es una lucha de fuerza contra agilidad. Tienes que ganar.",
            "nightwing_vs_soames.png"
        )
        grayson_confrontacion_soames.agregar_opcion("Usar tus palos de eskrima para desarmarlo y someterlo (Agilidad)", "grayson_normal_pruebas_obtenidas", stat="reputacion", cambio=10)
        grayson_confrontacion_soames.agregar_opcion("Usar explosivos de humo para inmovilizarlo (Tecnología)", "grayson_normal_pruebas_obtenidas", stat="recursos", cambio=1)
        self.historia["grayson_normal_confrontacion_soames"] = grayson_confrontacion_soames

        grayson_pruebas_obtenidas = NodoHistoria(
            "grayson_normal_pruebas_obtenidas",
            "LA CAÍDA DEL BLOQUE",
            "Obtienes las pruebas que necesitas. La evidencia es irrefutable. Soames es arrestado y la corrupción "
            "del 'Bloque' es expuesta. La ciudad respira aliviada. Te conviertes en el héroe oficial, "
            "el protector no oficial. Pero la caída del Bloque deja un vacío de poder.",
            "bludhaven_cleanup.png"
        )
        grayson_pruebas_obtenidas.agregar_opcion("Centrarte en el crimen organizado que llenará el vacío", "grayson_normal_nuevo_enemigo", stat="reputacion", cambio=20)
        grayson_pruebas_obtenidas.agregar_opcion("Buscar una nueva comisaria de policía de confianza", "grayson_normal_aliado_policial", stat="recursos", cambio=3)
        self.historia["grayson_normal_pruebas_obtenidas"] = grayson_pruebas_obtenidas

        grayson_pruebas_obtenidas_brutal = NodoHistoria(
            "grayson_normal_pruebas_obtenidas_brutal",
            "UN PRECIO POR LA JUSTICIA",
            "Obtienes las pruebas, pero las acciones brutales dejan un mal sabor de boca. La gente te teme, "
            "y tus métodos son cuestionados. Un oficial al que dejaste malherido testifica en tu contra, "
            "pero la evidencia de corrupción es más fuerte. El Bloque cae, pero tu reputación "
            "se ve empañada. El vacío de poder es grande.",
            "nightwing_questioned.png"
        )
        grayson_pruebas_obtenidas_brutal.agregar_opcion("Restaurar tu imagen pública con acciones positivas", "grayson_normal_nuevo_enemigo", stat="reputacion", cambio=-5)
        self.historia["grayson_normal_pruebas_obtenidas_brutal"] = grayson_pruebas_obtenidas_brutal

        grayson_aliado_policial = NodoHistoria(
            "grayson_normal_aliado_policial",
            "LA COMISARIA AMIGA",
            "Encuentras una oficial honesta, **Amy Rohrbach**, que se convierte en la nueva Comisaria. "
            "Ella te respeta y te promete colaboración, no sumisión. Tienes una aliada dentro de la ley. "
            "Esto alivia tu carga. El vacío de poder se llena, pero un nuevo enemigo se alza.",
            "rohrbach_ally.png"
        )
        grayson_aliado_policial.agregar_opcion("Prepararte para el próximo gran desafío (Blockbuster)", "grayson_normal_nuevo_enemigo", stat="reputacion", cambio=15, item="Contactos Policiales")
        self.historia["grayson_normal_aliado_policial"] = grayson_aliado_policial

        grayson_nuevo_enemigo = NodoHistoria(
            "grayson_normal_nuevo_enemigo",
            "EL ASCENSO DE BLOCKBUSTER",
            "El vacío de poder es llenado por el jefe criminal más grande de Blüdhaven: **Roland Desmond, alias Blockbuster**. "
            "Él es el verdadero poder detrás de la corrupción, Soames era solo un peón. Blockbuster es "
            "fuerte, inteligente, y ahora te ve como el principal obstáculo para su imperio. "
            "Ha puesto un precio a tu cabeza.",
            "blockbuster_reveal.png"
        )
        grayson_nuevo_enemigo.agregar_opcion("Atacar la base de operaciones de Blockbuster", "grayson_normal_blockbuster_confrontacion", stat="salud", cambio=5)
        grayson_nuevo_enemigo.agregar_opcion("Investigar su pasado y sus puntos débiles", "grayson_normal_blockbuster_investigacion", stat="recursos", cambio=2)
        self.historia["grayson_normal_nuevo_enemigo"] = grayson_nuevo_enemigo

        grayson_blockbuster_investigacion = NodoHistoria(
            "grayson_normal_blockbuster_investigacion",
            "EL ARCHIVO DE ROLAND DESMOND",
            "Usas tus recursos para investigar a Roland Desmond. Descubres que es un genio de los negocios "
            "con una mente brillante, pero sufre de problemas de salud relacionados con experimentos "
            "fallidos. Es fuerte y musculoso, pero su corazón es su debilidad. "
            "También tiene un hermano, Mark Desmond (el primer Blockbuster), que fue un experimento fallido.",
            "blockbuster_file.png"
        )
        grayson_blockbuster_investigacion.agregar_opcion("Usar esta información para idear un plan de ataque", "grayson_normal_blockbuster_plan", stat="recursos", cambio=5)
        self.historia["grayson_normal_blockbuster_investigacion"] = grayson_blockbuster_investigacion

        grayson_blockbuster_confrontacion = NodoHistoria(
            "grayson_normal_blockbuster_confrontacion",
            "PRIMERA SANGRE",
            "Te infiltras en uno de los almacenes de Blockbuster. Él te estaba esperando. "
            "Es un gigante de músculo, casi imparable. Te golpea fuerte, rompiendo tu traje. "
            "Tu agilidad apenas te salva. Logras escapar, herido. Es más fuerte de lo que esperabas.",
            "nightwing_hurt.png"
        )
        grayson_blockbuster_confrontacion.agregar_opcion("Volver a la Mansión Wayne para pedir un traje nuevo (Orgullo vs. Supervivencia)", "grayson_normal_llamada_bruce", stat="salud", cambio=-10)
        grayson_blockbuster_confrontacion.agregar_opcion("Reparar el traje con tus propios recursos en Blüdhaven", "grayson_normal_blockbuster_investigacion", stat="recursos", cambio=-3)
        self.historia["grayson_normal_blockbuster_confrontacion"] = grayson_blockbuster_confrontacion

        grayson_blockbuster_plan = NodoHistoria(
            "grayson_normal_blockbuster_plan",
            "EL PLAN DE ATAQUE",
            "Con la información de su corazón débil, diseñas un plan para inmovilizar a Blockbuster. "
            "Necesitas un lugar donde su fuerza bruta sea una desventaja. El lugar perfecto: "
            "la torre de comunicación de Blüdhaven, donde su infraestructura es frágil.",
            "nightwing_plan.png"
        )
        grayson_blockbuster_plan.agregar_opcion("Llevar la pelea a la torre de comunicación", "grayson_normal_blockbuster_final_fight", stat="reputacion", cambio=10, item="Trampa de Alta Frecuencia")
        self.historia["grayson_normal_blockbuster_plan"] = grayson_blockbuster_plan

        grayson_llamada_bruce = NodoHistoria(
            "grayson_normal_llamada_bruce",
            "EL PRECIO DE LA AYUDA",
            "Llamas a Alfred y le pides que te envíe un traje. Llega rápidamente, con una nota de Bruce: "
            "'Usa tu agilidad, no tu fuerza. Nightwing debe ser mejor que nosotros. No lo olvides.' "
            "El traje es mejor, negro y azul, reforzado. Has tragado tu orgullo, pero ahora tienes "
            "la ventaja tecnológica y el consejo de tu mentor.",
            "nightwing_new_suit.png"
        )
        grayson_llamada_bruce.agregar_opcion("Diseñar el plan con el nuevo traje", "grayson_normal_blockbuster_plan", stat="recursos", cambio=3, item="Traje de Nightwing (Reforzado)")
        self.historia["grayson_normal_llamada_bruce"] = grayson_llamada_bruce

        grayson_blockbuster_final_fight = NodoHistoria(
            "grayson_normal_blockbuster_final_fight",
            "EL ACROBATA CONTRA EL GIGANTE",
            "Atraes a Blockbuster a la torre de comunicación. La pelea es épica. Él destruye todo "
            "a su paso, pero tú usas las vigas y el cableado para esquivar. Lo llevas a la cima. "
            "Usas tu conocimiento de su corazón para aturdirlo con una descarga de alto voltaje controlada. "
            "Cae, derrotado, pero vivo. Su imperio se derrumba.",
            "nightwing_final_fight.png"
        )
        grayson_blockbuster_final_fight.agregar_opcion("Entregar a Blockbuster a la Comisaria Rohrbach", "grayson_normal_final_bueno", stat="reputacion", cambio=25)
        grayson_blockbuster_final_fight.agregar_opcion("Dejarlo caer desde la torre para terminar el problema de raíz (Oscuridad)", "grayson_normal_final_oscuro", stat="salud", cambio=-5, stat2="reputacion", cambio2=-20)
        self.historia["grayson_normal_blockbuster_final_fight"] = grayson_blockbuster_final_fight

        grayson_final_bueno = NodoHistoria(
            "grayson_normal_final_bueno",
            "EL PROTECTOR DE BLÜDHAVEN - FINAL NORMAL BUENO",
            "Blockbuster está preso. La ciudad está en paz. Eres el héroe que Blüdhaven no sabía que necesitaba. "
            "La policía (con Rohrbach a la cabeza) trabaja contigo, la gente te ama. Ya no eres la sombra de Batman, "
            "eres **Nightwing**, el pájaro que voló lejos para forjar su propio destino. Tu hogar es esta ciudad, "
            "y tu legado está asegurado. Sabes que siempre habrá crimen, pero ahora sabes que puedes manejarlo solo. "
            "Tu historia apenas comienza. Has encontrado tu luz.",
            "final_nightwing_hero.png"
        )
        grayson_final_bueno.es_final = True
        self.historia["grayson_normal_final_bueno"] = grayson_final_bueno

        grayson_final_oscuro = NodoHistoria(
            "grayson_normal_final_oscuro",
            "LA SOMBRA SE ALARGA - FINAL NORMAL OSCURO",
            "Dejas caer a Blockbuster. Murió al caer. El problema está resuelto para siempre. "
            "Pero el acto te pesa. ¿Te has convertido en lo que odias de Bruce, o peor? "
            "La Comisaria Rohrbach te mira con terror. El Joker tenía razón: la oscuridad de Gotham "
            "te ha seguido. El crimen se reduce, pero la gente te teme. "
            "Eres el héroe de Blüdhaven, sí, pero has cruzado una línea. Nightwing sigue en Blüdhaven, "
            "pero la luz se ha atenuado. ¿Podrás volver a la luz? (Continúa en modo difícil)",
            "final_nightwing_dark.png"
        )
        grayson_final_oscuro.es_final = True
        self.historia["grayson_normal_final_oscuro"] = grayson_final_oscuro

        # MODO DIFÍCIL: EL CAMINO DE LA AUTO-DESTRUCCIÓN (40 nodos)
        # COMIENZA AQUÍ - APROXIMADAMENTE LÍNEA 800

        grayson_inicio_dificil = NodoHistoria(
            "grayson_dificil_inicio",
            "BLÜDHAVEN: LA CAÍDA DE LA ESPERANZA",
            "Han pasado dos años. Has perdido la fe en la justicia de Blüdhaven. La corrupción es interminable, "
            "Blockbuster sigue regresando o sus secuaces toman su lugar. Te has vuelto cínico. "
            "Una noche, mientras luchas contra unos matones, usas una fuerza excesiva. "
            "Un grupo de niños te ve, y su cara no es de admiración, sino de miedo.",
            "nightwing_cynical.png"
        )
        grayson_inicio_dificil.agregar_opcion("Ignorar la mirada de los niños y seguir patrullando con dureza", "grayson_dificil_distanciamiento", stat="reputacion", cambio=-5)
        grayson_inicio_dificil.agregar_opcion("Reflexionar sobre tu comportamiento y llamar a Alfred (Luz)", "grayson_dificil_llamada_alfred", stat="salud", cambio=5)
        grayson_inicio_dificil.agregar_opcion("Doblar la apuesta: 'Si me temen, serán más obedientes'", "grayson_dificil_metodo_duro", stat="recursos", cambio=1)
        self.historia["grayson_dificil_inicio"] = grayson_inicio_dificil

        grayson_distanciamiento = NodoHistoria(
            "grayson_dificil_distanciamiento",
            "EL HOMBRE SOLITARIO",
            "Te alejas de tus aliados (Rohrbach, ocasionales llamadas a Bruce). Te sientes solo, "
            "consumido por la tarea. Un día, una carta llega a tu apartamento. Es una invitación anónima "
            "a una reunión en un antiguo casino: **La Cabaña**. La carta habla de una hermandad "
            "de élite de Blüdhaven que maneja los hilos de la ciudad.",
            "nightwing_alone.png"
        )
        grayson_distanciamiento.agregar_opcion("Aceptar la invitación e infiltrarte en La Cabaña (Riesgo)", "grayson_dificil_cabana_entrada", stat="recursos", cambio=2)
        grayson_distanciamiento.agregar_opcion("Rechazarla, la desconfianza es tu única aliada", "grayson_dificil_desconfianza", stat="salud", cambio=-5)
        self.historia["grayson_dificil_distanciamiento"] = grayson_distanciamiento

        grayson_llamada_alfred = NodoHistoria(
            "grayson_dificil_llamada_alfred",
            "LA VOZ DE LA CORDURA",
            "Llamas a Alfred. 'Maestro Dick, te escucho cansado. No te olvides de la gracia de tus padres. "
            "La oscuridad es fácil de caer en ella.' Te dice que Batman está en una misión en el extranjero "
            "y Gotham está vulnerable. Te ofrece un trato: 'Vuelve por un tiempo. Ayuda a tu hermano. "
            "Recuerda quién eres.'",
            "dick_alfred_call.png"
        )
        grayson_llamada_alfred.agregar_opcion("Regresar a Gotham temporalmente (Opción de redención)", "grayson_dificil_regreso_gotham", stat="reputacion", cambio=10)
        grayson_llamada_alfred.agregar_opcion("Seguir en Blüdhaven, pero más cauteloso", "grayson_dificil_distanciamiento", stat="salud", cambio=5)
        self.historia["grayson_dificil_llamada_alfred"] = grayson_llamada_alfred

        grayson_metodo_duro = NodoHistoria(
            "grayson_dificil_metodo_duro",
            "MANO DE HIERRO",
            "Comienzas a usar métodos más intimidantes. Atacas a los criminales a plena luz del día, "
            "dejas 'advertencias' visibles. La policía te teme. La Comisaria Rohrbach te confronta: "
            "'Nightwing, no eres Batman. No te conviertas en un tirano.' Ignoras sus advertencias. "
            "Tu reputación de justiciero extremo atrae la atención de La Cabaña.",
            "nightwing_intimidating.png"
        )
        grayson_metodo_duro.agregar_opcion("Aceptar la invitación de La Cabaña para usar su información", "grayson_dificil_cabana_entrada", stat="recursos", cambio=3)
        self.historia["grayson_dificil_metodo_duro"] = grayson_metodo_duro

        grayson_cabana_entrada = NodoHistoria(
            "grayson_dificil_cabana_entrada",
            "EL CASINO SECRETO",
            "Entras en La Cabaña, un casino subterráneo lleno de la élite corrupta de Blüdhaven. "
            "Un hombre con una máscara de búho te saluda: es **Saiko**, tu antiguo amigo del circo, "
            "ahora un asesino de la Corte de los Búhos. 'Dick Grayson,' susurra. 'La Cabaña te ofrece "
            "poder: únete a nosotros y juntos limpiaremos Blüdhaven sin las reglas de Batman.'",
            "saiko_reveal.png"
        )
        grayson_cabana_entrada.agregar_opcion("Rechazar la oferta y combatir a Saiko", "grayson_dificil_vs_saiko", stat="reputacion", cambio=15)
        grayson_cabana_entrada.agregar_opcion("Aceptar la oferta de forma encubierta para obtener información", "grayson_dificil_cabana_infiltracion", stat="recursos", cambio=5, item="Anillo de La Cabaña")
        self.historia["grayson_dificil_cabana_entrada"] = grayson_cabana_entrada

        grayson_desconfianza = NodoHistoria(
            "grayson_dificil_desconfianza",
            "PARANOIA",
            "Rechazas la invitación. Te encierras en tu apartamento, analizándolo todo. Te vuelves paranoico. "
            "Dejas de patrullar para investigar. Al no haber Nightwing, el crimen se dispara. "
            "Finalmente, te das cuenta de que al rechazar la pelea, has permitido que la oscuridad gane.",
            "nightwing_isolated.png"
        )
        grayson_desconfianza.agregar_opcion("Volver a patrullar con el doble de fuerza (Método Duro)", "grayson_dificil_metodo_duro", stat="salud", cambio=-10)
        self.historia["grayson_dificil_desconfianza"] = grayson_desconfianza

        grayson_regreso_gotham = NodoHistoria(
            "grayson_dificil_regreso_gotham",
            "EL HIJO PRÓDIGO",
            "Vuelves a Gotham. Es un alivio. Alfred te saluda con una sonrisa. Te pones el traje de Nightwing, "
            "pero patrullas con el Batwing. Te encuentras con Jason Todd (Red Hood). "
            "Él te mira y sonríe: 'Parece que tu camino es tan solitario como el mío, Dickie. "
            "¿Quién te rompió?'. Tu reunión es tensa.",
            "nightwing_and_redhood.png"
        )
        grayson_regreso_gotham.agregar_opcion("Pedirle ayuda a Jason con un problema de Blüdhaven (Blockbuster)", "grayson_dificil_jason_aliado", stat="reputacion", cambio=10)
        grayson_regreso_gotham.agregar_opcion("Seguir patrullando en Gotham y postergar Blüdhaven", "grayson_dificil_gotham_refugio", stat="recursos", cambio=1)
        self.historia["grayson_dificil_regreso_gotham"] = grayson_regreso_gotham

        # Continuación del MODO DIFÍCIL: EL CAMINO DE LA AUTO-DESTRUCCIÓN

        grayson_jason_aliado = NodoHistoria(
            "grayson_dificil_jason_aliado",
            "RED HOOD Y NIGHTWING: ALIADOS TENSOS",
            "Jason escucha tu problema de Blüdhaven. 'Un gigante del crimen... que mata a niños. "
            "Suena como algo que yo sí puedo arreglar.' Te ofrece ayuda. Aceptas, a regañadientes. "
            "Sus métodos son duros, pero efectivos. Patrullan juntos en Gotham por una noche. "
            "Te das cuenta de lo fácil que es cruzar la línea con un cómplice.",
            "nightwing_and_redhood_team.png"
        )
        grayson_jason_aliado.agregar_opcion("Pedirle que vaya contigo a Blüdhaven para capturar a Blockbuster", "grayson_dificil_equipo_redhood", stat="reputacion", cambio=5)
        grayson_jason_aliado.agregar_opcion("Volver a Blüdhaven solo, con las ideas de Jason en la cabeza", "grayson_dificil_metodo_duro", stat="salud", cambio=-5)
        self.historia["grayson_dificil_jason_aliado"] = grayson_jason_aliado

        grayson_gotham_refugio = NodoHistoria(
            "grayson_dificil_gotham_refugio",
            "GOTHAM: EL NIDO VACÍO",
            "Gotham es un refugio, pero te sientes un extraño. Te enteras de que un nuevo Robin (Tim Drake) "
            "está trabajando con Bruce. Te sientes reemplazado. Regresas a Blüdhaven sintiéndote "
            "más solo y más resentido. La carta de La Cabaña sigue en tu escritorio.",
            "nightwing_tim_shadow.png"
        )
        grayson_gotham_refugio.agregar_opcion("Aceptar la invitación de La Cabaña (El resentimiento te guía)", "grayson_dificil_cabana_entrada", stat="recursos", cambio=1)
        self.historia["grayson_dificil_gotham_refugio"] = grayson_gotham_refugio

        grayson_vs_saiko = NodoHistoria(
            "grayson_dificil_vs_saiko",
            "EL HUECO DE SAÏKO",
            "Rechazas la oferta. Saïko te ataca. Es tu doble: acróbata, artista marcial, pero sin piedad. "
            "'Eras el elegido para ser un Talón,' te dice. 'Pero elegiste la capa de murciélago.' "
            "La pelea es en el aire, entre vigas rotas. Usas tu habilidad para derribarlo, "
            "pero él escapa, dejando un mapa de Blüdhaven con puntos marcados: son las bases "
            "secretas de la Corte de los Búhos.",
            "nightwing_vs_saiko.png"
        )
        grayson_vs_saiko.agregar_opcion("Investigar el mapa de la Corte de los Búhos", "grayson_dificil_corte_investigacion", stat="recursos", cambio=5)
        grayson_vs_saiko.agregar_opcion("Ignorar el mapa y centrarte en Blockbuster", "grayson_dificil_metodo_duro", stat="reputacion", cambio=5)
        self.historia["grayson_dificil_vs_saiko"] = grayson_vs_saiko

        grayson_cabana_infiltracion = NodoHistoria(
            "grayson_dificil_cabana_infiltracion",
            "EL ESPÍA DE LA CORTE",
            "Aceptas unirte, a regañadientes. Saïko te da un Talón de la Corte y te pide que hagas 'trabajo sucio': "
            "capturar a un político honesto de Blüdhaven. Te has convertido en su Talón encubierto. "
            "Esto te da acceso a información de la Corte y de Blockbuster, quien es un subordinado de la Corte.",
            "nightwing_cabana_infiltrate.png"
        )
        grayson_cabana_infiltracion.agregar_opcion("Cumplir la misión de Saïko (Capturar al político)", "grayson_dificil_secuestro", stat="reputacion", cambio=-10)
        grayson_cabana_infiltracion.agregar_opcion("Advertir al político y usarlo para obtener más información (Doble agente)", "grayson_dificil_doble_agente", stat="recursos", cambio=3)
        self.historia["grayson_dificil_cabana_infiltracion"] = grayson_cabana_infiltracion

        grayson_corte_investigacion = NodoHistoria(
            "grayson_dificil_corte_investigacion",
            "EL SECRETO DE BLÜDHAVEN",
            "Usas el mapa y descubres que la Corte de los Búhos no solo opera en Gotham, sino que "
            "Blüdhaven es su base de operaciones más antigua y secreta. Blockbuster es solo su fachada. "
            "Encuentras un nido de Talons en hibernación. Sabes que esta es una amenaza global, no local.",
            "corte_de_buhos_bludhaven.png"
        )
        grayson_corte_investigacion.agregar_opcion("Contactar a Batman con esta información crucial (Admitir que no puedes solo)", "grayson_dificil_llamada_bruce_corte", stat="reputacion", cambio=10)
        grayson_corte_investigacion.agregar_opcion("Intentar detener a la Corte solo para demostrar tu valía (Orgullo)", "grayson_dificil_ataque_solo", stat="salud", cambio=-10)
        self.historia["grayson_dificil_corte_investigacion"] = grayson_corte_investigacion

        grayson_secuestro = NodoHistoria(
            "grayson_dificil_secuestro",
            "CRUZANDO EL LÍMITE",
            "Secuestras al político honesto, entregándolo a Saïko. Te sientes sucio. "
            "Saïko te sonríe: 'Ahora eres un verdadero Talón, Dick Grayson.' Te da la próxima orden: "
            "asesinar a Blockbuster y culpar a Batman, para crear caos en Blüdhaven.",
            "nightwing_kidnapping.png"
        )
        grayson_secuestro.agregar_opcion("Negarte a la orden de asesinato y combatir a Saïko", "grayson_dificil_vs_saiko_final", stat="reputacion", cambio=-15)
        grayson_secuestro.agregar_opcion("Aceptar el asesinato (Caída total)", "grayson_dificil_asesinato_blockbuster", stat="salud", cambio=-20)
        self.historia["grayson_dificil_secuestro"] = grayson_secuestro

        grayson_doble_agente = NodoHistoria(
            "grayson_dificil_doble_agente",
            "EL DOBLE AGENTE",
            "Te acercas al político y le explicas la verdad: estás infiltrado. Él acepta ayudarte. "
            "Usas al político como cebo para que Saïko revele más información sobre la red de la Corte. "
            "La operación es exitosa, obtienes los nombres de los líderes de la Corte. "
            "Saïko sospecha, pero no tiene pruebas.",
            "nightwing_double_agent.png"
        )
        grayson_doble_agente.agregar_opcion("Usar la información para atacar la Corte de los Búhos", "grayson_dificil_ataque_solo", stat="recursos", cambio=5)
        self.historia["grayson_dificil_doble_agente"] = grayson_doble_agente

        grayson_llamada_bruce_corte = NodoHistoria(
            "grayson_dificil_llamada_bruce_corte",
            "BATMAN A LA VANGUARDIA",
            "Llamas a Batman, y él llega con un equipo completo (Alfred, Tim, Batgirl). "
            "Admites que la Corte es demasiado para ti solo. Bruce te da una palmada en el hombro: "
            "'Siempre has sido más fuerte cuando pides ayuda, Dick.' Planeas el asalto a la base "
            "de hibernación de los Talons y a La Cabaña.",
            "batman_and_batfamily_corte.png"
        )
        grayson_llamada_bruce_corte.agregar_opcion("Liderar el asalto a La Cabaña (Redención)", "grayson_dificil_asalto_batfamilia", stat="reputacion", cambio=20)
        self.historia["grayson_dificil_llamada_bruce_corte"] = grayson_llamada_bruce_corte

        grayson_ataque_solo = NodoHistoria(
            "grayson_dificil_ataque_solo",
            "LA SOLEDAD DE LA GUERRA",
            "Atacas el nido de Talons solo. Eres Nightwing, el mejor acróbata, pero son Talons. "
            "Son letales. La lucha es desesperada. Estás rodeado. Saïko te encuentra en medio del "
            "caos. 'Tu ego te matará, Dick Grayson,' se burla, mientras te deja gravemente herido.",
            "nightwing_talons_attack.png"
        )
        grayson_ataque_solo.agregar_opcion("Escapar gravemente herido", "grayson_dificil_herido_y_solo", stat="salud", cambio=-30)
        self.historia["grayson_dificil_ataque_solo"] = grayson_ataque_solo

        grayson_herido_y_solo = NodoHistoria(
            "grayson_dificil_herido_y_solo",
            "EL PRECIO DE LA CABEZONERÍA",
            "Te arrastras de vuelta a tu apartamento. Estás en estado crítico. La Comisaria Rohrbach "
            "te encuentra. Ella puede llamar a un hospital (exponiendo tu identidad) o a Alfred. "
            "Tu vida está en sus manos. Te das cuenta de que al alejar a tus amigos, has perdido tu red de seguridad.",
            "rohrbach_nightwing_hurt.png"
        )
        grayson_herido_y_solo.agregar_opcion("Pedirle que llame a Alfred (Redención tardía)", "grayson_dificil_llamada_alfred", stat="reputacion", cambio=15)
        grayson_herido_y_solo.agregar_opcion("Pedirle que te deje morir (Final muy oscuro)", "grayson_dificil_final_muerte", stat="salud", cambio=-50)
        self.historia["grayson_dificil_herido_y_solo"] = grayson_herido_y_solo

        grayson_vs_saiko_final = NodoHistoria(
            "grayson_dificil_vs_saiko_final",
            "EL DUELO ACROBÁTICO",
            "Te niegas a asesinar. Luchas contra Saïko en un techo. La pelea es personal, llena de rabia "
            "y movimientos de circo. Saïko te dice que eres 'un error'. Lo derrotas, pero cuando "
            "está a punto de caer, te agarra el brazo y te dice: 'Si caemos, tú caes conmigo.' "
            "Tienes un momento para decidir si lo salvas o lo dejas ir.",
            "nightwing_vs_saiko_cliff.png"
        )
        grayson_vs_saiko_final.agregar_opcion("Salvar a Saïko y entregarlo (Moral)", "grayson_dificil_final_redencion", stat="reputacion", cambio=25)
        grayson_vs_saiko_final.agregar_opcion("Dejarlo caer (Cruzar la línea)", "grayson_dificil_final_oscuro", stat="salud", cambio=-10)
        self.historia["grayson_dificil_vs_saiko_final"] = grayson_vs_saiko_final

        grayson_asesinato_blockbuster = NodoHistoria(
            "grayson_dificil_asesinato_blockbuster",
            "EL ASESINO DE ALAS NOCTURNAS",
            "Sigues la orden de Saïko. Asesinas a Blockbuster con un arma de fuego y dejas una 'Batarang' "
            "para incriminar a Batman. El caos se desata en Blüdhaven. Te has convertido "
            "en un asesino. Saïko está feliz. 'Ahora, Dick Grayson, eres nuestro. El próximo es... Batman.'",
            "nightwing_murder.png"
        )
        grayson_asesinato_blockbuster.agregar_opcion("Seguir las órdenes de Saïko (Caída final)", "grayson_dificil_final_talon", stat="reputacion", cambio=-20)
        self.historia["grayson_dificil_asesinato_blockbuster"] = grayson_asesinato_blockbuster

        grayson_asalto_batfamilia = NodoHistoria(
            "grayson_dificil_asalto_batfamilia",
            "LA RECONCILIACIÓN",
            "Lideras el asalto con la Bat-familia. Es una sinfonía de trabajo en equipo. Capturan a Saïko, "
            "desactivan el nido de Talons y desmantelan La Cabaña. Blüdhaven está finalmente libre. "
            "Bruce te abraza. 'Bienvenido a casa, Dick.' Has encontrado el camino de vuelta, "
            "aceptando que tu fuerza reside en tus amigos, no en tu soledad.",
            "nightwing_batfamily_win.png"
        )
        grayson_asalto_batfamilia.agregar_opcion("Regresar a Blüdhaven con una nueva perspectiva (Redención)", "grayson_dificil_final_redencion", stat="reputacion", cambio=30)
        self.historia["grayson_dificil_asalto_batfamilia"] = grayson_asalto_batfamilia

        grayson_equipo_redhood = NodoHistoria(
            "grayson_dificil_equipo_redhood",
            "MÉTODO TODD: LA SOLUCIÓN RÁPIDA",
            "Jason y tú vais a Blüdhaven. Jason usa su fuerza bruta y armas letales para emboscar "
            "a Blockbuster y sus secuaces. Él lo inmoviliza y te pregunta: '¿Qué hacemos con él, Dickie?' "
            "Blockbuster está a tu merced, herido e indefenso. Jason se va, dejando la decisión final en tus manos.",
            "redhood_and_nightwing_decision.png"
        )
        grayson_equipo_redhood.agregar_opcion("Entregarlo a la policía de Rohrbach (Moral)", "grayson_dificil_final_antiheroe", stat="reputacion", cambio=15)
        grayson_equipo_redhood.agregar_opcion("Dejar que Jason regrese y lo termine (Caída moral)", "grayson_dificil_final_oscuro", stat="salud", cambio=-10)
        self.historia["grayson_dificil_equipo_redhood"] = grayson_equipo_redhood

        # FINALES MODO DIFÍCIL (Aproximadamente 1200 líneas)

        grayson_final_redencion = NodoHistoria(
            "grayson_dificil_final_redencion",
            "NIGHTWING: LA LUZ EN LA OSCURIDAD - FINAL REDENCIÓN",
            "Has pasado por la prueba de fuego de la soledad y la tentación. Aprendiste que tu fuerza no es tu "
            "independencia, sino tu capacidad de amar y confiar. La Bat-familia te ayudó a limpiar Blüdhaven. "
            "Vuelves a tu ciudad con un nuevo propósito. La policía y la gente te respetan, "
            "porque has demostrado que puedes fallar y levantarte. Eres Nightwing, y eres la luz que "
            "Gotham y Blüdhaven necesitan. Tu legado es el de la esperanza y la conexión. Tu camino "
            "está claro. (FIN)",
            "final_nightwing_redemption.png"
        )
        grayson_final_redencion.es_final = True
        self.historia["grayson_dificil_final_redencion"] = grayson_final_redencion

        grayson_final_oscuro = NodoHistoria(
            "grayson_dificil_final_oscuro",
            "LA CAÍDA DEL ACROBATA - FINAL OSCURO",
            "Dejaste que Saïko o Blockbuster murieran. Has cruzado el límite. La culpa te consume. "
            "Bruce te confronta, pero tú lo ignoras. Ya no eres Robin, y lo que es más aterrador, "
            "ya casi no eres Dick Grayson. Te has convertido en un vigilante frío, efectivo, pero sin corazón. "
            "La gente te teme. El crimen disminuye, pero la esperanza también. El final de tu camino "
            "es la soledad total, la sombra del murciélago se ha convertido en tu propia sombra. "
            "Vives en un tormento constante. Eres Nightwing, el asesino de Blüdhaven. (FIN)",
            "final_nightwing_darkest.png"
        )
        grayson_final_oscuro.es_final = True
        self.historia["grayson_dificil_final_oscuro"] = grayson_final_oscuro

        grayson_final_talon = NodoHistoria(
            "grayson_dificil_final_talon",
            "EL NUEVO TALÓN - FINAL DE SUMISIÓN",
            "Has asesinado a Blockbuster e incriminado a Batman. Saïko te recibe en La Cabaña. "
            "Te pone el uniforme de la Corte de los Búhos. Te han lavado el cerebro, has perdido tu voluntad. "
            "Eres el Talón perfecto: el acróbata de la Muerte. Te has convertido en el enemigo de tu familia. "
            "Te han quitado la 'R' y ahora el 'Pájaro'. Eres Dick Grayson, el Talón, y sirves a la Corte. "
            "Una marioneta letal de la oscuridad. (FIN)",
            "final_nightwing_talon.png"
        )
        grayson_final_talon.es_final = True
        self.historia["grayson_dificil_final_talon"] = grayson_final_talon

        grayson_final_muerte = NodoHistoria(
            "grayson_dificil_final_muerte",
            "EL HÉROE CAÍDO - FINAL TRÁGICO",
            "Te niegas a ser salvado. La Comisaria Rohrbach te deja. Mueres solo en tu apartamento. "
            "La noticia de tu muerte es un golpe para Blüdhaven y la Bat-familia. El Batimóvil llega "
            "a Blüdhaven tarde, solo para recoger tu cuerpo. Bruce mira tu rostro y llora. "
            "Tu legado es la tragedia de un héroe que no pudo aceptar ayuda. El único consuelo "
            "es que moriste como Nightwing, no como Talón, pero tu luz se apagó sola. (FIN)",
            "final_nightwing_dead.png"
        )
        grayson_final_muerte.es_final = True
        self.historia["grayson_dificil_final_muerte"] = grayson_final_muerte

        grayson_final_antiheroe = NodoHistoria(
            "grayson_dificil_final_antiheroe",
            "NIGHTWING: EL CAMINO PROPIO - FINAL ANTÍHÉROE",
            "Entregaste a Blockbuster, pero no sin antes darle una 'lección' junto a Jason. "
            "La policía te mira con respeto y miedo. No eres un Talón, pero tampoco eres Robin. "
            "Tienes tu propio código: justicia sin matar, pero sin escrúpulos con el dolor. "
            "Eres Nightwing, el vigilante de Blüdhaven que actúa en la sombra. Bruce lo desaprueba, "
            "pero te deja en paz. Has encontrado el equilibrio entre la luz y la sombra, "
            "el camino propio que nadie más puede juzgar. Eres la ley en Blüdhaven. (FIN)",
            "final_nightwing_antihero.png"
        )
        grayson_final_antiheroe.es_final = True
        self.historia["grayson_dificil_final_antiheroe"] = grayson_final_antiheroe







        # MODO FÁCIL: EL CHICO MARAVILLA - Nodos de relleno (Nodos 21-35)

        facil_relleno_1 = NodoHistoria(
            "facil_relleno_1",
            "EL PINGÜINO INTENTA ATACAR",
            "Durante una patrulla, el Pingüino intenta un robo de joyas en la Galería de Arte. Tu misión "
            "es proteger los rehenes. Batman se encarga del Pingüino. Tienes que asegurar el perímetro.",
            "robin_penguin_fight.png"
        )
        facil_relleno_1.agregar_opcion("Usar un movimiento de circo para desarmar a los secuaces sin violencia", "facil_relleno_2", stat="reputacion", cambio=5)
        facil_relleno_1.agregar_opcion("Usar un Bat-gancho para derribar a los secuaces y dejarlos inconscientes", "facil_relleno_2", stat="salud", cambio=5)
        self.historia["facil_relleno_1"] = facil_relleno_1

        facil_relleno_2 = NodoHistoria(
            "facil_relleno_2",
            "LA LECCIÓN DE ALFRED",
            "Regresas a la Batcueva. Batman te regaña por haber tomado un riesgo innecesario. Alfred "
            "te cura y te da un consejo: 'La valentía sin precaución es imprudencia, Maestro Dick.'",
            "alfred_lesson.png"
        )

        grayson_facil_relleno_3 = NodoHistoria(
            "grayson_facil_relleno_3",
            "EL HUEVO DE PASCUA DEL ACERTIJO",
            "El Acertijo ha dejado una serie de acertijos que conducen a una bomba. Batman está "
            "enfrascado en una lucha de ingenio en el centro de Gotham. Te envía un mensaje: "
            "'Necesito que resuelvas el siguiente enigma, Robin: "
            "'Soy el principio del final, el final de cada lugar. ¿Qué soy?'",
            "robin_riddle.png"
        )
        grayson_facil_relleno_3.agregar_opcion("La letra E", "grayson_facil_relleno_4", stat="reputacion", cambio=10)
        grayson_facil_relleno_3.agregar_opcion("El silencio", "grayson_facil_relleno_4", stat="reputacion", cambio=-5)
        grayson_facil_relleno_3.agregar_opcion("La tumba", "grayson_facil_relleno_4", stat="reputacion", cambio=-10)
        self.historia["grayson_facil_relleno_3"] = grayson_facil_relleno_3

        grayson_facil_relleno_4 = NodoHistoria(
            "grayson_facil_relleno_4",
            "BOMBA DESACTIVADA",
            "Tu respuesta (La E) era correcta. La siguiente pista te lleva a una estación de tren abandonada "
            "donde un grupo de personas está atrapado. Desactivas la bomba, salvando a los rehenes. "
            "El Acertijo queda frustrado. Batman te felicita por tu mente aguda.",
            "robin_win_riddle.png"
        )
        grayson_facil_relleno_4.agregar_opcion("Continuar la patrulla con confianza", "grayson_facil_relleno_5", stat="salud", cambio=5)
        self.historia["grayson_facil_relleno_4"] = grayson_facil_relleno_4

        grayson_facil_relleno_5 = NodoHistoria(
            "grayson_facil_relleno_5",
            "EL DILEMA DE DOS CARAS",
            "Dos Caras ha secuestrado a dos personas: un político corrupto que va a la cárcel "
            "y una doctora que está curando a los más pobres. Te obliga a elegir a quién salvar. "
            "'¿A quién salva la justicia de Batman, Chico Maravilla?'",
            "robin_twoface_dilemma.png"
        )
        grayson_facil_relleno_5.agregar_opcion("Salvar a la doctora (Opción ética)", "grayson_facil_relleno_6_moral", stat="reputacion", cambio=15)
        grayson_facil_relleno_5.agregar_opcion("Salvar al político (Opción de ley)", "grayson_facil_relleno_6_ley", stat="reputacion", cambio=-5)
        grayson_facil_relleno_5.agregar_opcion("Engañar a Dos Caras y salvar a ambos (Opción acrobática)", "grayson_facil_relleno_6_acro", stat="recursos", cambio=2)
        self.historia["grayson_facil_relleno_5"] = grayson_facil_relleno_5

        grayson_facil_relleno_6_moral = NodoHistoria(
            "grayson_facil_relleno_6_moral",
            "EL VALOR DE LA VIDA",
            "Salvas a la doctora. El político es capturado por Dos Caras. Batman te mira, "
            "pero no dice nada. Alfred te da la razón: 'Una vida que cura vale más que una que corrompe.' "
            "Aprendes que la justicia a veces debe ser compasiva.",
            "robin_moral_win.png"
        )
        grayson_facil_relleno_6_moral.agregar_opcion("Seguir patrullando con tu brújula moral intacta", "grayson_facil_relleno_7", stat="salud", cambio=10)
        self.historia["grayson_facil_relleno_6_moral"] = grayson_facil_relleno_6_moral

        grayson_facil_relleno_6_ley = NodoHistoria(
            "grayson_facil_relleno_6_ley",
            "EL PESO DE LA LEY",
            "Salvas al político, citando el debido proceso de Batman. La doctora es capturada. "
            "Te sientes vacío. El político corrupto te traiciona y se escapa. Batman te dice: "
            "'A veces la ley es un arma de doble filo. Tenías que haber confiado en tu instinto, Dick.'",
            "robin_law_loss.png"
        )
        grayson_facil_relleno_6_ley.agregar_opcion("Lidiar con la culpa y el fracaso", "grayson_facil_relleno_7", stat="reputacion", cambio=-10)
        self.historia["grayson_facil_relleno_6_ley"] = grayson_facil_relleno_6_ley

        grayson_facil_relleno_6_acro = NodoHistoria(
            "grayson_facil_relleno_6_acro",
            "EL TRUCO DEL CIRCO",
            "Usas un truco de trapecio improvisado para cambiar las cuerdas que sostenían a ambos, "
            "logrando salvar a los dos. Dos Caras grita de frustración. Batman sonríe bajo la capucha. "
            "'Impresionante, Robin. Siempre encontrando un tercer camino.'",
            "robin_acrobatic_win.png"
        )
        grayson_facil_relleno_6_acro.agregar_opcion("Celebrar la victoria con Alfred", "grayson_facil_relleno_7", stat="salud", cambio=15, stat2="reputacion", cambio2=5)
        self.historia["grayson_facil_relleno_6_acro"] = grayson_facil_relleno_6_acro

        grayson_facil_relleno_7 = NodoHistoria(
            "grayson_facil_relleno_7",
            "UNA LLAMADA DE REFUERZO",
            "Batman necesita ayuda en una misión contra el Espantapájaros, pero te pide que te quedes "
            "para proteger a una joven en peligro: **Barbara Gordon**. Es la hija del Comisario Gordon. "
            "Te aburres vigilando, pero aceptas. Barbara te observa con curiosidad.",
            "robin_and_barbara.png"
        )
        grayson_facil_relleno_7.agregar_opcion("Hacerle preguntas sobre su padre y la policía", "grayson_facil_relleno_8", stat="recursos", cambio=1)
        grayson_facil_relleno_7.agregar_opcion("Mostrarle trucos de circo (Romper el protocolo)", "grayson_facil_relleno_8", stat="reputacion", cambio=5)
        self.historia["grayson_facil_relleno_7"] = grayson_facil_relleno_7

        grayson_facil_relleno_8 = NodoHistoria(
            "grayson_facil_relleno_8",
            "LA AMISTAD CON BARBARA",
            "Barbara es inteligente y te conecta con el mundo real fuera de la Mansión Wayne. "
            "Ella se convierte en tu primer amigo real en Gotham. Te confiesa que admira a Batman. "
            "No le dices que sabes su secreto.",
            "dick_barbara_talk.png"
        )
        grayson_facil_relleno_8.agregar_opcion("Valorar tu amistad con Barbara", "grayson_facil_relleno_9", stat="salud", cambio=5, item="Amistad con Babs")
        self.historia["grayson_facil_relleno_8"] = grayson_facil_relleno_8

        facil_relleno_2.agregar_opcion("Tomar el consejo de Alfred y entrenar la paciencia", "facil_relleno_3", stat="recursos", cambio=1)
        self.historia["facil_relleno_2"] = facil_relleno_2

        facil_relleno_9 = NodoHistoria(
            "facil_relleno_9",
            "EL DEBUT DE BATGIRL (SECRETO)",
            "Mientras patrullas con Batman, ves a una figura nueva en los tejados. Lleva un traje morado "
            "y parece una experta en artes marciales. Te está ayudando, pero Batman la ignora. "
            "Es Batgirl (Barbara Gordon, sin que lo sepas). Ella te lanza un acertijo en la radio: '¿Cómo "
            "se llama el chico que siempre sonríe?'",
            "robin_and_batgirl.png"
        )
        facil_relleno_9.agregar_opcion("Responder con 'Dick Grayson' (Riesgo)", "facil_relleno_10_riesgo", stat="reputacion", cambio=5)
        facil_relleno_9.agregar_opcion("Responder con 'Robin' (Neutral)", "facil_relleno_10_neutral", stat="reputacion", cambio=1)
        self.historia["facil_relleno_9"] = facil_relleno_9

        facil_relleno_10_riesgo = NodoHistoria(
            "facil_relleno_10_riesgo",
            "MENSAJE SECRETO",
            "Ella se ríe por la radio: 'Buena respuesta, Chico Maravilla'. Batman te mira, "
            "'¿Quién era ese?' Ella te da la ubicación de una nueva guarida del Sombrerero Loco. "
            "Te das cuenta de que tienes una nueva aliada secreta que sabe tu identidad.",
            "batgirl_smile.png"
        )
        facil_relleno_10_riesgo.agregar_opcion("Mantener el secreto de Batgirl con Bruce", "facil_relleno_11", stat="salud", cambio=5)
        self.historia["facil_relleno_10_riesgo"] = facil_relleno_10_riesgo

        facil_relleno_10_neutral = NodoHistoria(
            "facil_relleno_10_neutral",
            "LA ALIADA EN LAS SOMBRAS",
            "Ella te da la ubicación. La atacas con Batman. Te sientes celoso de ella, "
            "pero a la vez intrigado. Batman no la menciona. Tu relación con él se vuelve "
            "ligeramente más tensa, ya que sientes que hay secretos que no te cuenta.",
            "batgirl_mystery.png"
        )
        facil_relleno_10_neutral.agregar_opcion("Confrontar a Batman sobre la nueva vigilante", "facil_relleno_11", stat="reputacion", cambio=-5)
        self.historia["facil_relleno_10_neutral"] = facil_relleno_10_neutral

        facil_relleno_11 = NodoHistoria(
            "facil_relleno_11",
            "LA SOMBRA DEL HOMBRE MURCIÉLAGO",
            "Un día, estás a punto de dar un golpe final a un criminal. Lo ves y piensas: "
            "'Este tipo volverá a hacer daño.' Sientes la tentación de golpearlo más fuerte. "
            "Pero recuerdas el código de Batman y la luz de Alfred.",
            "robin_moral_dilemma.png"
        )
        facil_relleno_11.agregar_opcion("Seguir el código: reducirlo sin violencia excesiva", "facil_relleno_12_moral", stat="reputacion", cambio=10)
        facil_relleno_11.agregar_opcion("Usar un poco más de fuerza para dejarlo fuera de combate por un mes", "facil_relleno_12_fuerza", stat="reputacion", cambio=-5)
        self.historia["facil_relleno_11"] = facil_relleno_11

        facil_relleno_12_moral = NodoHistoria(
            "facil_relleno_12_moral",
            "EL CAMINO CORRECTO",
            "Te contienes. Bruce te mira con aprobación. 'Bien hecho, Dick. Nunca olvides quién eres.' "
            "Te sientes bien contigo mismo. Has superado la tentación de la oscuridad.",
            "robin_integrity.png"
        )
        facil_relleno_12_moral.agregar_opcion("Continuar tu desarrollo como Robin", "facil_relleno_13", stat="salud", cambio=5)
        self.historia["facil_relleno_12_moral"] = facil_relleno_12_moral

        facil_relleno_12_fuerza = NodoHistoria(
            "facil_relleno_12_fuerza",
            "LA FRONTERA CRÍTICA",
            "Bruce te reprende duramente. 'No eres un verdugo, Dick. Eres mi socio.' "
            "La tensión es alta. Te das cuenta de que tus caminos están divergiendo. "
            "El traje de Robin se siente un poco más pesado ahora.",
            "batman_disappointed.png"
        )
        facil_relleno_12_fuerza.agregar_opcion("Pedir perdón y esforzarte más para seguir el código", "facil_relleno_13", stat="reputacion", cambio=-10)
        self.historia["facil_relleno_12_fuerza"] = facil_relleno_12_fuerza

        facil_relleno_13 = NodoHistoria(
            "facil_relleno_13",
            "EL HOMBRE QUE NO RÍE",
            "Regresas a la Batcueva. Te sientes frustrado por la rigidez de Batman. Le cuentas a Alfred "
            "sobre Batgirl. Alfred solo sonríe. 'Maestro Dick, el señor Wayne tiene sus razones, "
            "pero usted debe encontrar su propia risa. Su camino debe ser diferente.'",
            "alfred_advice_dick.png"
        )
        facil_relleno_13.agregar_opcion("Patrullar con Batgirl sin que Batman lo sepa (Independencia)", "facil_relleno_14", stat="reputacion", cambio=5)
        facil_relleno_13.agregar_opcion("Dejar de lado a Batgirl para ser leal a Bruce (Lealtad)", "facil_relleno_14", stat="reputacion", cambio=-5)
        self.historia["facil_relleno_13"] = facil_relleno_13

        facil_relleno_14 = NodoHistoria(
            "facil_relleno_14",
            "EL ASALTO DE MISTER FREEZE",
            "Mister Freeze ataca el Banco de Gotham. Patrullas solo (o con Batgirl). Es una lucha "
            "contra el frío extremo. Tienes que pensar rápido y usar tu agilidad para evitar los rayos de congelación. "
            "Batman está ocupado lidiando con su propia crisis.",
            "robin_vs_mr_freeze.png"
        )
        facil_relleno_14.agregar_opcion("Usar tus palos de eskrima para deshabilitar su arma congeladora (Combate)", "facil_relleno_15_exito", stat="reputacion", cambio=10)
        facil_relleno_14.agregar_opcion("Llevarlo a una sala de vapor caliente (Estrategia)", "facil_relleno_15_exito", stat="recursos", cambio=1)
        self.historia["facil_relleno_14"] = facil_relleno_14

        facil_relleno_15_exito = NodoHistoria(
            "facil_relleno_15_exito",
            "ROBIN, EL INGENIOSO",
            "Derrotas a Mr. Freeze. Has demostrado que puedes manejar a un villano de clase A por tu cuenta. "
            "Cuando Batman te encuentra, solo te da un asentimiento. 'Necesito que investigues un caso "
            "de corrupción en un orfanato. Mantente en las sombras.' Es una misión que te aburre. "
            "Quieres más.",
            "robin_solo_win.png"
        )
        facil_relleno_15_exito.agregar_opcion("Aceptar la misión aburrida (Obediencia)", "facil_relleno_16_sumision", stat="reputacion", cambio=5)
        facil_relleno_15_exito.agregar_opcion("Buscar una misión más desafiante por tu cuenta (Rebeldía)", "facil_relleno_16_rebeldia", stat="salud", cambio=5)
        self.historia["facil_relleno_15_exito"] = facil_relleno_15_exito

        facil_relleno_16_sumision = NodoHistoria(
            "facil_relleno_16_sumision",
            "EL SOMBRA DE GOTHAM",
            "Pasas una semana en el orfanato, aburrido. El caso se resuelve, pero sientes que pierdes "
            "tu tiempo. Te preguntas si Batman te está reteniendo intencionadamente.",
            "robin_bored.png"
        )
        facil_relleno_16_sumision.agregar_opcion("Enfrentar a Batman sobre tu rol", "facil_relleno_17_confrontacion", stat="reputacion", cambio=-5)
        self.historia["facil_relleno_16_sumision"] = facil_relleno_16_sumision

        facil_relleno_16_rebeldia = NodoHistoria(
            "facil_relleno_16_rebeldia",
            "BUSCANDO LA ADRENALINA",
            "Ignoras la orden y persigues un caso de tráfico de armas. Lo resuelves, pero pones "
            "en peligro la misión de Batman. Él te confronta. 'Hiciste un buen trabajo, pero desobedeciste.' "
            "El conflicto es inevitable.",
            "batman_robin_argument.png"
        )
        facil_relleno_16_rebeldia.agregar_opcion("Aceptar las consecuencias y reafirmar tu deseo de ser independiente", "facil_relleno_17_confrontacion", stat="reputacion", cambio=5)
        self.historia["facil_relleno_16_rebeldia"] = facil_relleno_16_rebeldia

        facil_relleno_17_confrontacion = NodoHistoria(
            "facil_relleno_17_confrontacion",
            "EL FIN DE ROBIN",
            "Le dices a Batman que necesitas ser más que un compañero. 'Necesito mi propia identidad. "
            "Mis propias reglas.' Batman te mira con tristeza. 'Si te vas, la puerta siempre estará abierta. "
            "Pero si te pones ese traje azul, ya no serás Robin.'",
            "robin_mask_off.png"
        )
        facil_relleno_17_confrontacion.agregar_opcion("Tomar la máscara de Robin y dejar la Batcueva", "normal_bludhaven_inicio", stat="salud", cambio=10) # Bucle a inicio de Nightwing
        self.historia["facil_relleno_17_confrontacion"] = facil_relleno_17_confrontacion

        facil_relleno_18 = NodoHistoria(
            "facil_relleno_18",
            "CRISIS: EL ESCAPE DE ARKHAM",
            "El Joker, Dos Caras, el Pingüino y el Acertijo han escapado de Arkham. Gotham está en caos. "
            "Batman te asigna la misión de rastrear y capturar al villano menos peligroso, **El Pingüino**, "
            "que está intentando tomar el control de los muelles.",
            "arkham_breakout_robin.png"
        )
        facil_relleno_18.agregar_opcion("Ir directamente a los muelles (Obediencia)", "facil_relleno_19_muelles", stat="reputacion", cambio=5)
        facil_relleno_18.agregar_opcion("Usar tu conocimiento de las calles para encontrar una pista del Joker (Rebeldía)", "facil_relleno_19_joker", stat="salud", cambio=5)
        self.historia["facil_relleno_18"] = facil_relleno_18

        facil_relleno_19_muelles = NodoHistoria(
            "facil_relleno_19_muelles",
            "LA TRAMPA DEL PINGÜINO",
            "En los muelles, el Pingüino te espera con una serie de paraguas trampa. Te has centrado "
            "demasiado en la misión de Batman. Tienes que usar tus habilidades de circo para esquivar "
            "las trampas y someterlo sin ayuda.",
            "robin_penguin_trapped.png"
        )
        facil_relleno_19_muelles.agregar_opcion("Desarmar los paraguas y capturar al Pingüino", "facil_relleno_20_captura", stat="reputacion", cambio=15)
        facil_relleno_19_muelles.agregar_opcion("Huir para pedir ayuda a Batman (Peligro)", "facil_relleno_20_captura", stat="salud", cambio=-5)
        self.historia["facil_relleno_19_muelles"] = facil_relleno_19_muelles

        facil_relleno_19_joker = NodoHistoria(
            "facil_relleno_19_joker",
            "VISIÓN DE TÚNEL",
            "Te centras en el Joker. Pierdes tiempo y no encuentras nada. El Pingüino escapa. "
            "Batman te reprende. 'Te di una orden, Robin. Un buen soldado sabe seguir la estrategia.' "
            "Te sientes decepcionado, pero tu instinto te dice que el Joker es el verdadero problema.",
            "batman_disappointed_joker.png"
        )
        facil_relleno_19_joker.agregar_opcion("Volver a seguir las órdenes de Batman", "facil_relleno_20_captura", stat="reputacion", cambio=-10)
        self.historia["facil_relleno_19_joker"] = facil_relleno_19_joker

        facil_relleno_20_captura = NodoHistoria(
            "facil_relleno_20_captura",
            "MISIÓN CUMPLIDA (O FALLIDA)",
            "El Pingüino es capturado y devuelto a Arkham. A pesar del éxito (o el fracaso), "
            "la Crisis continúa. Batman te dice que te centres en la protección civil. "
            "Mientras patrullas, ves a Batgirl (Barbara) luchando sola contra Dos Caras. "
            "Necesitas elegir: ¿la misión de Batman o ayudar a tu amiga?",
            "robin_two_face_batgirl.png"
        )
        facil_relleno_20_captura.agregar_opcion("Ayudar a Batgirl (Lealtad a un amigo)", "facil_relleno_21_ayuda", stat="salud", cambio=10)
        facil_relleno_20_captura.agregar_opcion("Ignorarla y seguir la orden de Batman (Lealtad al código)", "facil_relleno_21_ignora", stat="reputacion", cambio=5)
        self.historia["facil_relleno_20_captura"] = facil_relleno_20_captura

        facil_relleno_21_ayuda = NodoHistoria(
            "facil_relleno_21_ayuda",
            "EL HÉROE DE LA AMISTAD",
            "Ayudas a Batgirl a someter a Dos Caras. Ella te mira con gratitud. 'Sabía que vendrías, Dick.' "
            "Batman te regaña, pero la moral de la ciudad se dispara. Has demostrado que tu corazón "
            "es tu mejor arma. Te das cuenta de que no necesitas a Batman para ser un héroe.",
            "robin_batgirl_team.png"
        )
        facil_relleno_21_ayuda.agregar_opcion("Aceptar el regaño de Batman y seguir tu propio camino", "facil_relleno_22_independencia", stat="reputacion", cambio=15)
        self.historia["facil_relleno_21_ayuda"] = facil_relleno_21_ayuda

        facil_relleno_21_ignora = NodoHistoria(
            "facil_relleno_21_ignora",
            "EL SOLDADO OBEDIENTE",
            "Ignoras a Batgirl. Ella lucha sola y resulta herida, pero logra vencer a Dos Caras. "
            "Batman te felicita por tu disciplina. Pero cuando ves a Barbara, ella te da la espalda. "
            "Has salvado la misión, pero has perdido a tu amiga.",
            "barbara_turned_back.png"
        )
        facil_relleno_21_ignora.agregar_opcion("Intentar recuperar la amistad con Barbara (Remordimiento)", "facil_relleno_22_independencia", stat="salud", cambio=-10)
        self.historia["facil_relleno_21_ignora"] = facil_relleno_21_ignora

        facil_relleno_22_independencia = NodoHistoria(
            "facil_relleno_22_independencia",
            "LA SOMBRA SE ALARGA",
            "La Crisis termina. Todos vuelven a Arkham. El conflicto con Batman es evidente. "
            "Tu corazón te pide dejar Gotham. Barbara (Batgirl/Oráculo) te apoya. "
            "Necesitas tu propia ciudad. Te decides por Blüdhaven.",
            "robin_leaving_gotham.png"
        )
        facil_relleno_22_independencia.agregar_opcion("Prepararte para tu nueva vida como Nightwing", "normal_bludhaven_inicio", stat="reputacion", cambio=10) # Bucle a inicio Nightwing
        self.historia["facil_relleno_22_independencia"] = facil_relleno_22_independencia

        facil_relleno_23 = NodoHistoria(
            "facil_relleno_23",
            "EL LEGADO DE ROBIN",
            "Antes de irte, dejas una nota a Alfred y Bruce. Alfred te da un último regalo: "
            "un nuevo traje (el prototipo de Nightwing) que diseñó para ti. Bruce te deja la "
            "llave de un apartamento en Blüdhaven. 'Para que no tengas que robar llan...', "
            "la frase queda inconclusa, pero sabes que su intención es la de un padre.",
            "robin_nightwing_suit_gift.png"
        )
        facil_relleno_23.agregar_opcion("Abrazar a Alfred y prometerle que lo llamarás", "facil_relleno_24", stat="salud", cambio=10)
        facil_relleno_23.agregar_opcion("Dejar a Gotham en silencio, sin despedirte (Ruptura)", "facil_relleno_24", stat="reputacion", cambio=-5)
        self.historia["facil_relleno_23"] = facil_relleno_23

        facil_relleno_24 = NodoHistoria(
            "facil_relleno_24",
            "GOTHAM EN EL RETROVISOR",
            "Miras Gotham desde el puente. Eres Dick Grayson. Ya no eres Robin, pero aún no eres "
            "Nightwing. Sientes la emoción de la libertad y el peso de la responsabilidad. "
            "Tu destino te espera en la ciudad vecina: Blüdhaven. La radio anuncia un aumento "
            "de crimen en Blüdhaven, liderado por un gánster llamado Blockbuster.",
            "dick_grayson_leaving_gotham.png"
        )
        facil_relleno_24.agregar_opcion("Empezar tu nueva vida en Blüdhaven (Transición a Nightwing)", "normal_bludhaven_inicio", stat="recursos", cambio=5) # Transición final a Nightwing
        self.historia["facil_relleno_24"] = facil_relleno_24

        facil_relleno_25 = NodoHistoria(
            "facil_relleno_25",
            "EL ÚLTIMO ASALTO EN GOTHAM",
            "En tu última noche en Gotham, un criminal de poca monta intenta robar un orfanato. "
            "Es una pelea fácil, pero te hace reflexionar: ¿el crimen es solo la maldad, o también "
            "el resultado de la desesperación? Capturas al ladrón, pero te preguntas por su futuro.",
            "robin_last_gotham_fight.png"
        )
        facil_relleno_25.agregar_opcion("Dejar algo de dinero para la familia del ladrón (Compasión)", "facil_relleno_26", stat="reputacion", cambio=10)
        facil_relleno_25.agregar_opcion("Entregarlo a la policía sin piedad (Ley)", "facil_relleno_26", stat="reputacion", cambio=-5)
        self.historia["facil_relleno_25"] = facil_relleno_25

        facil_relleno_26 = NodoHistoria(
            "facil_relleno_26",
            "EL VALOR DE UN NOMBRE",
            "Te pones el traje azul y negro que Alfred te dio. Te miras al espejo y sonríes. "
            "'Nightwing.' Un nombre que significa libertad, luz y acrobacias. Es hora de llevar "
            "la luz a Blüdhaven, una ciudad que se ha acostumbrado a la oscuridad.",
            "nightwing_first_look.png"
        )
        facil_relleno_26.agregar_opcion("Cruzar el puente hacia Blüdhaven", "normal_bludhaven_inicio", stat="salud", cambio=5) # Transición final a Nightwing
        self.historia["facil_relleno_26"] = facil_relleno_26



        # MODO NORMAL: EL CAMINO SOLITARIO - Nodos de relleno (Nodos 41-60)

        normal_relleno_1 = NodoHistoria(
            "normal_relleno_1",
            "CRISIS DE VIVIENDA EN BLÜDHAVEN",
            "Los matones de Blockbuster están desalojando a familias enteras para construir un casino. "
            "La policía no actúa. Debes ayudar a las personas y exponer este crimen.",
            "nightwing_housing_crisis.png"
        )
        normal_relleno_1.agregar_opcion("Aterrorizar a los matones para que se vayan sin un enfrentamiento", "normal_relleno_2", stat="reputacion", cambio=5)
        normal_relleno_1.agregar_opcion("Filmar el desalojo para exponer a Blockbuster en redes sociales", "normal_relleno_2", stat="recursos", cambio=1)
        self.historia["normal_relleno_1"] = normal_relleno_1

        normal_relleno_2 = NodoHistoria(
            "normal_relleno_2",
            "UNA CITA CON UNA DETECTIVE",
            "Sales a cenar con la Detective de Blüdhaven, una mujer honesta. Ella te pide que confíes en la ley. "
            "Te enamoras de ella, pero no puedes decirle quién eres. El dilema te consume.",
            "dick_date_detective.png"
        )
        normal_relleno_2.agregar_opcion("Mantener la relación y la identidad en secreto", "normal_relleno_3", stat="salud", cambio=5)
        normal_relleno_2.agregar_opcion("Terminar la relación para protegerla", "normal_relleno_3", stat="reputacion", cambio=-5)
        self.historia["normal_relleno_2"] = normal_relleno_2

        grayson_normal_relleno_3 = NodoHistoria(
            "grayson_normal_relleno_3",
            "LA PELEA CON BLOCKBUSTER (SECUENCIA CORTA)",
            "Blockbuster está desmantelando un vecindario. Lo confrontas. La pelea es una carrera "
            "por la vida. Tienes que usar el entorno a tu favor para que su fuerza se vuelva contra él.",
            "nightwing_blockbuster_chase.png"
        )
        grayson_normal_relleno_3.agregar_opcion("Usar cuerdas explosivas para derribar un muro sobre él (Riesgo de daño colateral)", "grayson_normal_relleno_4_violento", stat="salud", cambio=5)
        grayson_normal_relleno_3.agregar_opcion("Conducirlo a las alcantarillas para limitar su movimiento (Agilidad)", "grayson_normal_relleno_4_agil", stat="recursos", cambio=1)
        self.historia["grayson_normal_relleno_3"] = grayson_normal_relleno_3

        grayson_normal_relleno_4_violento = NodoHistoria(
            "grayson_normal_relleno_4_violento",
            "DAÑO COLATERAL",
            "Logras aturdir a Blockbuster con la explosión, pero el muro daña una casa. "
            "La gente está molesta. Te das cuenta de que no puedes usar el mismo nivel de fuerza que él.",
            "nightwing_explosion_fail.png"
        )
        grayson_normal_relleno_4_violento.agregar_opcion("Pedir perdón y continuar la lucha", "grayson_normal_relleno_5", stat="reputacion", cambio=-5)
        self.historia["grayson_normal_relleno_4_violento"] = grayson_normal_relleno_4_violento

        grayson_normal_relleno_4_agil = NodoHistoria(
            "grayson_normal_relleno_4_agil",
            "VENTAJA DEL ENTORNO",
            "En las alcantarillas, Blockbuster no puede usar su fuerza. Lo inmovilizas con una red, "
            "pero un grupo de matones de Blockbuster te embosca. La pelea se vuelve una trampa.",
            "nightwing_sewer_trap.png"
        )
        grayson_normal_relleno_4_agil.agregar_opcion("Escapar por un túnel secreto y dejar a Blockbuster (Retirada estratégica)", "grayson_normal_relleno_5", stat="reputacion", cambio=5)
        grayson_normal_relleno_4_agil.agregar_opcion("Luchar contra los matones para capturar a Blockbuster de una vez (Peligro)", "grayson_normal_relleno_5", stat="salud", cambio=-10)
        self.historia["grayson_normal_relleno_4_agil"] = grayson_normal_relleno_4_agil

        grayson_normal_relleno_5 = NodoHistoria(
            "grayson_normal_relleno_5",
            "EL INFORME DE LA POLICÍA",
            "La Comisaria Rohrbach te llama. 'Hay un nuevo grupo en la ciudad, Nightwing. Se hacen "
            "llamar 'Los Reclamadores'. Son ex-empleados despedidos de una compañía de Blockbuster. "
            "Están atacando objetivos pequeños para llamar la atención de Blockbuster y de ti.'",
            "rohrbach_report.png"
        )
        grayson_normal_relleno_5.agregar_opcion("Ignorarlos, centrarte en Blockbuster", "grayson_normal_relleno_6", stat="reputacion", cambio=-5)
        grayson_normal_relleno_5.agregar_opcion("Intentar ayudarlos a encontrar un trabajo (Paz)", "grayson_normal_relleno_6", stat="salud", cambio=5)
        self.historia["grayson_normal_relleno_5"] = grayson_normal_relleno_5

        grayson_normal_relleno_6 = NodoHistoria(
            "grayson_normal_relleno_6",
            "EL ASALTO A LA TELEVISIÓN",
            "Los Reclamadores toman un estudio de televisión. Su líder, una mujer llamada 'Líder', "
            "exige a Blockbuster que les devuelva sus pensiones. La situación es de rehenes.",
            "nightwing_hostage_situation.png"
        )
        grayson_normal_relleno_6.agregar_opcion("Negociar con la Líder para que libere a los rehenes (Diplomacia)", "grayson_normal_relleno_7", stat="reputacion", cambio=15)
        grayson_normal_relleno_6.agregar_opcion("Asaltar el edificio y neutralizar a todos (Fuerza)", "grayson_normal_relleno_7", stat="salud", cambio=-5)
        self.historia["grayson_normal_relleno_6"] = grayson_normal_relleno_6

        grayson_normal_relleno_7 = NodoHistoria(
            "grayson_normal_relleno_7",
            "EL HÉROE DE LA CLASE TRABAJADORA",
            "Si negociaste: La Líder te escucha, confía en Nightwing. Si asaltaste: Te odian, pero los salvaste. "
            "En ambos casos, demuestras que te importa la gente común, no solo los grandes villanos. "
            "Tu reputación mejora como el héroe del pueblo.",
            "nightwing_populist_hero.png"
        )
        grayson_normal_relleno_7.agregar_opcion("Usar tus recursos para ayudar a Los Reclamadores de forma anónima", "grayson_normal_relleno_8", stat="recursos", cambio=-3)
        self.historia["grayson_normal_relleno_7"] = grayson_normal_relleno_7

        grayson_normal_relleno_8 = NodoHistoria(
            "grayson_normal_relleno_8",
            "EL COMPLOT SECRETO",
            "Mientras investigas un ataque de Blockbuster, encuentras un nexo de su operación "
            "con una figura de Gotham: **El Pingüino**. Blockbuster está comprando armas de alto poder "
            "de Gotham. Esto es un problema inter-ciudades. Necesitas investigar a fondo.",
            "nightwing_penguin_clue.png"
        )
        grayson_normal_relleno_8.agregar_opcion("Llamar a Bruce Wayne para que investigue al Pingüino en Gotham", "grayson_normal_relleno_9", stat="reputacion", cambio=5)
        grayson_normal_relleno_8.agregar_opcion("Viajar tú mismo a Gotham para infiltrarte en la base del Pingüino", "grayson_normal_relleno_9", stat="salud", cambio=-5)
        self.historia["grayson_normal_relleno_8"] = grayson_normal_relleno_8

        grayson_normal_relleno_9 = NodoHistoria(
            "grayson_normal_relleno_9",
            "LA CONEXIÓN GOTHAM",
            "Bruce confirma el nexo: el Pingüino está usando a Blockbuster para blanquear dinero. "
            "Es una operación masiva que une a las dos ciudades. Bruce te advierte: 'Ten cuidado, Dick. "
            "Estás en aguas profundas ahora. No te ahogues en sus problemas.'",
            "batman_warning_dick.png"
        )
        grayson_normal_relleno_9.agregar_opcion("Usar esta información para atacar el lado financiero de Blockbuster", "grayson_normal_relleno_10", stat="recursos", cambio=3)
        self.historia["grayson_normal_relleno_9"] = grayson_normal_relleno_9

        grayson_normal_relleno_10 = NodoHistoria(
            "grayson_normal_relleno_10",
            "EL FRAUDE FISCAL",
            "Atacas el corazón financiero de Blockbuster, exponiendo su fraude fiscal y sus vínculos "
            "con el Pingüino. Esto lo debilita, pero Blockbuster reacciona con furia. "
            "Planea un asalto directo a la policía de Blüdhaven, que lo traicionó. Es una guerra total.",
            "nightwing_financial_blow.png"
        )
        grayson_normal_relleno_10.agregar_opcion("Defender la Jefatura de Policía con Rohrbach", "grayson_normal_blockbuster_final_fight", stat="reputacion", cambio=10) # Bucle a la pelea final
        self.historia["grayson_normal_relleno_10"] = grayson_normal_relleno_10

        normal_relleno_11 = NodoHistoria(
            "normal_relleno_11",
            "BLOCKBUSTER: EL CONTRATAQUE",
            "Blockbuster está furioso por tu ataque financiero. Te tiende una trampa en un edificio en construcción. "
            "Te enfrentas a él y a su nuevo mercenario: **Deathstroke** (Slade Wilson). "
            "Deathstroke es rápido, metódico y te supera. Es la primera vez que te enfrentas a un villano de nivel élite.",
            "nightwing_vs_deathstroke.png"
        )
        normal_relleno_11.agregar_opcion("Concentrarte en escapar para planear un contraataque (Estrategia)", "normal_relleno_12_escape", stat="recursos", cambio=3)
        normal_relleno_11.agregar_opcion("Luchar contra Deathstroke hasta el final (Orgullo)", "normal_relleno_12_lucha", stat="salud", cambio=-20)
        self.historia["normal_relleno_11"] = normal_relleno_11

        normal_relleno_12_escape = NodoHistoria(
            "normal_relleno_12_escape",
            "LA ESTRATEGIA ES LA VICTORIA",
            "Usas una explosión de humo y tus movimientos acrobáticos para escapar. Deathstroke te persigue "
            "con una sonrisa. 'Buen movimiento, Chico Maravilla. Te veré pronto.' "
            "Te das cuenta de que necesitas ayuda para vencer a este mercenario.",
            "nightwing_deathstroke_chase.png"
        )
        normal_relleno_12_escape.agregar_opcion("Contactar a la Joven Liga de la Justicia (Red social de Dick)", "normal_relleno_13", stat="reputacion", cambio=5)
        normal_relleno_12_escape.agregar_opcion("Pedirle a Batman el archivo de Deathstroke (Recursos)", "normal_relleno_13", stat="recursos", cambio=1)
        self.historia["normal_relleno_12_escape"] = normal_relleno_12_escape

        normal_relleno_12_lucha = NodoHistoria(
            "normal_relleno_12_lucha",
            "LA HUMILLACIÓN",
            "Deathstroke te supera en cada movimiento. Te deja una herida grave. 'Tu agilidad es tu única ventaja, "
            "chico. Pero la estrategia es la mía.' Logras escapar, humillado y gravemente herido. "
            "La Comisaria Rohrbach te encuentra y te ayuda a cubrir tu rastro. Necesitas un plan.",
            "nightwing_hurt_deathstroke.png"
        )
        normal_relleno_12_lucha.agregar_opcion("Recuperarte y estudiar a Deathstroke", "normal_relleno_13", stat="salud", cambio=-5)
        self.historia["normal_relleno_12_lucha"] = normal_relleno_12_lucha

        normal_relleno_13 = NodoHistoria(
            "normal_relleno_13",
            "EL ARCHIVO DE SLADE WILSON",
            "Obtienes el archivo. Deathstroke es un mercenario de élite, conocido por su habilidad para "
            "predecir movimientos. Tu agilidad no será suficiente. Necesitas un arma que él no espera: "
            "un plan que use a Blüdhaven como tu campo de juego acrobático.",
            "deathstroke_file.png"
        )
        normal_relleno_13.agregar_opcion("Diseñar una trampa en los tejados de Blüdhaven", "normal_relleno_14", stat="recursos", cambio=5, item="Trampa de Techo")
        self.historia["normal_relleno_13"] = normal_relleno_13

        normal_relleno_14 = NodoHistoria(
            "normal_relleno_14",
            "LA REVANCHA CONTRA DEATHSTROKE",
            "Lo atraes a tu territorio. En los tejados, eres inigualable. Deathstroke intenta predecir "
            "tu próximo movimiento. Tú usas tu agilidad para hacer tres movimientos a la vez, "
            "haciendo imposible la predicción. Lo derrotas y lo entregas a Rohrbach. "
            "Te has graduado como héroe. Blockbuster está solo.",
            "nightwing_deathstroke_win.png"
        )
        normal_relleno_14.agregar_opcion("Prepararte para el enfrentamiento final con Blockbuster", "normal_blockbuster_final_fight", stat="reputacion", cambio=15) # Bucle a la pelea final
        self.historia["normal_relleno_14"] = normal_relleno_14


        normal_relleno_15 = NodoHistoria(
            "normal_relleno_15",
            "EL VACÍO DESPUÉS DE DEATHSTROKE",
            "Deathstroke está fuera de escena. Blockbuster está herido y sus finanzas comprometidas. "
            "Pero una nueva figura surge: **Gizmo**, un mercenario tecnológico que ha vendido "
            "un sistema de vigilancia de alta tecnología a lo que queda del 'Bloque' corrupto. "
            "Blüdhaven es ahora una ciudad espía.",
            "gizmo_tech_bludhaven.png"
        )
        normal_relleno_15.agregar_opcion("Intentar hackear el sistema de vigilancia desde tu apartamento (Riesgo)", "normal_relleno_16_hack", stat="recursos", cambio=5)
        normal_relleno_15.agregar_opcion("Atacar directamente la base de operaciones de Gizmo (Combate)", "normal_relleno_16_combate", stat="salud", cambio=-5)
        self.historia["normal_relleno_15"] = normal_relleno_15

        normal_relleno_16_hack = NodoHistoria(
            "normal_relleno_16_hack",
            "EL HACKEO DE ALAS NOCTURNAS",
            "Usas tus conocimientos de la tecnología de Wayne-Tech para hackear el sistema. "
            "Gizmo es bueno, pero tú eres el 'hijo' de Batman. Lo engañas, haciéndole creer "
            "que el sistema ha fallado, pero él detecta tu presencia y desactiva tu equipo.",
            "nightwing_hacked.png"
        )
        normal_relleno_16_hack.agregar_opcion("Pedir ayuda a Batgirl (Barbara Gordon) para la revancha", "normal_relleno_17_babs", stat="reputacion", cambio=10)
        normal_relleno_16_hack.agregar_opcion("Atacar a Gizmo mientras está en su punto ciego (Información temporal)", "normal_relleno_17_ataque", stat="recursos", cambio=1)
        self.historia["normal_relleno_16_hack"] = normal_relleno_16_hack

        normal_relleno_16_combate = NodoHistoria(
            "normal_relleno_16_combate",
            "LA PELEA CON GIZMO",
            "Atacas a Gizmo en un almacén. Él usa drones y trampas láser. La pelea es desigual. "
            "Logras deshabilitar un par de drones, pero su armamento te supera. Escapas herido, "
            "pero con la información de dónde está su centro de control.",
            "nightwing_vs_gizmo_drones.png"
        )
        normal_relleno_16_combate.agregar_opcion("Usar la información para atacar el centro de control", "normal_relleno_17_ataque", stat="salud", cambio=-10)
        self.historia["normal_relleno_16_combate"] = normal_relleno_16_combate

        normal_relleno_17_babs = NodoHistoria(
            "normal_relleno_17_babs",
            "ORÁCULO Y NIGHTWING",
            "Llamas a Barbara, que ahora es **Oráculo**, la red de información de Gotham. "
            "Ella te ayuda. Te da un código de acceso de emergencia para desactivar el sistema "
            "de Gizmo. 'Nunca olvides que tienes una familia,' te dice. Su ayuda es crucial.",
            "nightwing_and_oracle.png"
        )
        normal_relleno_17_babs.agregar_opcion("Lanzar el ataque con la ayuda de Oráculo", "normal_relleno_18_win", stat="reputacion", cambio=15)
        self.historia["normal_relleno_17_babs"] = normal_relleno_17_babs

        normal_relleno_17_ataque = NodoHistoria(
            "normal_relleno_17_ataque",
            "EL ATAQUE EN SOLITARIO",
            "Atacas el centro de control. Es una lucha brutal, pero logras destruir los servidores. "
            "Gizmo escapa. Has ganado la batalla de la tecnología, pero has perdido la oportunidad "
            "de capturarlo. La ciudad es libre de la vigilancia, pero la amenaza aún existe.",
            "nightwing_tech_destroy.png"
        )
        normal_relleno_17_ataque.agregar_opcion("Celebrar la victoria temporal y prepararte para el final", "normal_relleno_18_win", stat="salud", cambio=5)
        self.historia["normal_relleno_17_ataque"] = normal_relleno_17_ataque

        normal_relleno_18_win = NodoHistoria(
            "normal_relleno_18_win",
            "LA LIBERTAD DE BLÜDHAVEN",
            "La derrota de Gizmo y Deathstroke ha dejado a Blockbuster al descubierto. "
            "Él no tiene más aliados. Te reta a un enfrentamiento final. '¡Te haré tragar tu máscara, "
            "Chico Maravilla! ¡Ven a la Torre!'",
            "blockbuster_final_challenge.png"
        )
        normal_relleno_18_win.agregar_opcion("Aceptar el desafío final de Blockbuster", "normal_blockbuster_final_fight", stat="reputacion", cambio=10) # Bucle a la pelea final
        self.historia["normal_relleno_18_win"] = normal_relleno_18_win

        normal_relleno_19 = NodoHistoria(
            "normal_relleno_19",
            "LA RED DE TRÁFICO DE BLÜDHAVEN",
            "Blockbuster y el Pingüino han organizado una red de tráfico de personas en Blüdhaven. "
            "Descubres que la red se dirige al exterior. La Comisaria Rohrbach no puede actuar sola. "
            "Necesitas ayuda externa o cruzar la frontera de la ley para detener el barco.",
            "nightwing_human_trafficking.png"
        )
        normal_relleno_19.agregar_opcion("Llamar a Bruce Wayne para que use la Liga de la Justicia (Superar el orgullo)", "normal_relleno_20_liga", stat="reputacion", cambio=5)
        normal_relleno_19.agregar_opcion("Asaltar el barco tú solo, arriesgándote a usar fuerza letal", "normal_relleno_20_solo", stat="salud", cambio=-5)
        self.historia["normal_relleno_19"] = normal_relleno_19

        normal_relleno_20_liga = NodoHistoria(
            "normal_relleno_20_liga",
            "LA COOPERACIÓN ES LA VICTORIA",
            "Bruce se siente orgulloso de que le hayas llamado. La Liga de la Justicia detiene el barco "
            "sin un solo disparo. Blockbuster y el Pingüino sufren un golpe internacional. "
            "Tu reputación de héroe responsable se dispara. Aprendes que la soledad no es fuerza.",
            "nightwing_and_justice_league.png"
        )
        normal_relleno_20_liga.agregar_opcion("Aceptar el elogio y volver a tu misión en solitario", "normal_relleno_21_legado", stat="reputacion", cambio=15)
        self.historia["normal_relleno_20_liga"] = normal_relleno_20_liga

        normal_relleno_20_solo = NodoHistoria(
            "normal_relleno_20_solo",
            "EL PRECIO DE LA INDEPENDENCIA",
            "Asaltas el barco. La pelea es brutal. Tienes éxito, pero usas una fuerza excesiva "
            "y un par de matones resultan gravemente heridos. La gente te aclama, pero la prensa "
            "te llama 'el vigilante violento'. Tu código se ha roto por necesidad.",
            "nightwing_brutal_win.png"
        )
        normal_relleno_20_solo.agregar_opcion("Lidiar con la prensa y la culpa", "normal_relleno_21_legado", stat="reputacion", cambio=-10)
        self.historia["normal_relleno_20_solo"] = normal_relleno_20_solo

        normal_relleno_21_legado = NodoHistoria(
            "normal_relleno_21_legado",
            "LA ESTATUA DEL HÉROE",
            "El alcalde de Blüdhaven, para mejorar su imagen, aprueba la construcción de una estatua "
            "tuya en el centro de la ciudad. Esto te convierte en un símbolo, pero te sientes incómodo. "
            "La Comisaria Rohrbach te advierte: 'Ahora eres un objetivo más grande. Cuidado, Nightwing.'",
            "nightwing_statue.png"
        )
        normal_relleno_21_legado.agregar_opcion("Usar la estatua para enviar un mensaje a Blockbuster", "normal_relleno_22_mensaje", stat="recursos", cambio=3)
        self.historia["normal_relleno_21_legado"] = normal_relleno_21_legado

        normal_relleno_22_mensaje = NodoHistoria(
            "normal_relleno_22_mensaje",
            "EL DESAFÍO PÚBLICO",
            "Modificas la estatua en la noche para que apunte directamente a la torre de Blockbuster. "
            "Es un desafío público. Blockbuster está furioso y te reta a un duelo final en su torre. "
            "Es el final de tu camino solitario, o el principio de tu reinado.",
            "blockbuster_challenge_statue.png"
        )
        normal_relleno_22_mensaje.agregar_opcion("Aceptar el desafío final de Blockbuster", "normal_blockbuster_final_fight", stat="reputacion", cambio=10) # Bucle a la pelea final
        self.historia["normal_relleno_22_mensaje"] = normal_relleno_22_mensaje

        normal_blockbuster_final_fight = NodoHistoria(
            "normal_blockbuster_final_fight",
            "LA TORRE DE BLOCKBUSTER: DUELO FINAL",
            "Llegas a la torre, el centro del imperio criminal de Blockbuster. Él está furioso. "
            "La pelea es brutal, fuerza contra agilidad. Tienes que evitar su fuerza bruta y buscar "
            "sus puntos débiles, especialmente después de tu ataque financiero. Blockbuster no está solo. "
            "Un grupo de matones de élite te espera en la azotea.",
            "nightwing_vs_blockbuster_final.png"
        )
        normal_blockbuster_final_fight.agregar_opcion("Concentrarte en los matones primero, para aislar a Blockbuster (Estrategia)", "normal_final_estrategia", stat="recursos", cambio=5)
        normal_blockbuster_final_fight.agregar_opcion("Ir directo a Blockbuster, aceptando el daño (Riesgo total)", "normal_final_riesgo", stat="salud", cambio=-15)
        self.historia["normal_blockbuster_final_fight"] = normal_blockbuster_final_fight

        normal_final_estrategia = NodoHistoria(
            "normal_final_estrategia",
            "LA SINFONÍA ACROBÁTICA",
            "Usas tus palos de eskrima para deshabilitar rápidamente a los matones. Blockbuster se enfurece. "
            "La pelea se centra en tu agilidad. Lo guías a un lugar inestable de la torre: "
            "un cable de grúa que se rompe. Debes elegir entre someterlo o dejar que caiga al vacío.",
            "nightwing_blockbuster_climax.png"
        )
        normal_final_estrategia.agregar_opcion("Capturar a Blockbuster y entregarlo (Integridad)", "normal_final_redencion", stat="reputacion", cambio=30)
        normal_final_estrategia.agregar_opcion("Dejar que caiga (Oscuridad y eficiencia)", "normal_final_oscuro", stat="salud", cambio=-10)
        self.historia["normal_final_estrategia"] = normal_final_estrategia

        normal_final_riesgo = NodoHistoria(
            "normal_final_riesgo",
            "FUERZA CONTRA FUERZA",
            "Vas directo a Blockbuster. Su fuerza es abrumadora. Recibes un golpe brutal, "
            "pero logras usar un cable de acero para inmovilizarlo. Te has excedido en la fuerza, "
            "poniendo en riesgo tu vida. La Comisaria Rohrbach aparece y te grita: '¡No lo mates!'",
            "nightwing_final_blow_risk.png"
        )
        normal_final_riesgo.agregar_opcion("Entregarlo a Rohrbach (Integridad y ley)", "normal_final_redencion", stat="reputacion", cambio=15)
        normal_final_riesgo.agregar_opcion("Ignorar a Rohrbach y noquearlo permanentemente (Control)", "normal_final_antiheroe", stat="reputacion", cambio=5)
        self.historia["normal_final_riesgo"] = normal_final_riesgo

        normal_final_redencion = NodoHistoria(
            "normal_final_redencion",
            "NIGHTWING: EL CAMINO DE LA LUZ - FINAL REDENCIÓN",
            "Has derrotado a Blockbuster, demostrando que tu camino de Nightwing puede ser "
            "independiente sin perder la moralidad de Robin. Blüdhaven está libre. Bruce te mira "
            "con orgullo. Has creado tu propio código de honor y lo has defendido. Eres Nightwing, "
            "el héroe de la esperanza. Tu legado es un puente entre Gotham y la justicia. (FIN)",
            "final_normal_redemption.png"
        )
        normal_final_redencion.es_final = True
        self.historia["normal_final_redencion"] = normal_final_redencion

        normal_final_oscuro = NodoHistoria(
            "normal_final_oscuro",
            "EL VIGILANTE FRÍO - FINAL OSCURO",
            "Blockbuster ha muerto. Has cruzado la línea, aunque de forma indirecta. La culpa te consume. "
            "La Comisaria Rohrbach te desprecia. Blüdhaven es segura, pero vive bajo la sombra de "
            "un vigilante que castiga, no que inspira. Has elegido la eficiencia sobre la moralidad. "
            "Te conviertes en una leyenda oscura. El espectro de Batman te persigue. (FIN)",
            "final_normal_dark.png"
        )
        normal_final_oscuro.es_final = True
        self.historia["normal_final_oscuro"] = normal_final_oscuro

        normal_final_antiheroe = NodoHistoria(
            "normal_final_antiheroe",
            "NIGHTWING: EL DUEÑO DE BLÜDHAVEN - FINAL ANTÍHÉROE",
            "No eres un asesino, pero has dejado claro que estás por encima de la ley. Blockbuster está en coma. "
            "Rohrbach te permite seguir, porque eres el único que puede mantener el orden. "
            "Eres el amo de Blüdhaven. Bruce te advierte, pero no te detiene. Tienes tu propio código, "
            "una mezcla de Robin y Red Hood. Eres el único Nightwing. (FIN)",
            "final_normal_antihero.png"
        )
        normal_final_antiheroe.es_final = True
        self.historia["normal_final_antiheroe"] = normal_final_antiheroe

        normal_epilogo_5 = NodoHistoria(
            "normal_epilogo_5",
            "MISIÓN RECURRENTE: LA AMENAZA QUÍMICA",
            "Una pequeña pandilla inspirada en el Espantapájaros comienza a usar un gas de miedo "
            "modificado en los muelles. Tienes que desmantelar su laboratorio rápidamente "
            "antes de que el gas se propague por Blüdhaven. Necesitas un antídoto.",
            "nightwing_gas_attack.png"
        )
        normal_epilogo_5.agregar_opcion("Llamar a Oráculo para que te envíe la fórmula (Eficiencia)", "normal_epilogo_6", stat="recursos", cambio=5)
        normal_epilogo_5.agregar_opcion("Usar un Bat-cinturón de emergencia que te dio Alfred (Riesgo)", "normal_epilogo_6", stat="salud", cambio=-5)
        self.historia["normal_epilogo_5"] = normal_epilogo_5

        normal_epilogo_6 = NodoHistoria(
            "normal_epilogo_6",
            "EL HÉROE CIENTÍFICO",
            "Resuelves el problema químico. La pandilla es capturada. La gente de Blüdhaven "
            "te considera un héroe versátil: un acróbata, un detective y un científico. "
            "Sin embargo, el Comisionado Gordon te llama. 'Dick... he visto tus archivos. "
            "Ten cuidado con quién te rodeas.'",
            "nightwing_tech_lab.png"
        )
        normal_epilogo_6.agregar_opcion("Agradecer a Gordon y seguir tu camino", "normal_epilogo_7_amistad", stat="reputacion", cambio=5)
        normal_epilogo_6.agregar_opcion("Preguntarle sobre la Corte de los Búhos (Conexión)", "normal_epilogo_7_amistad", stat="recursos", cambio=1)
        self.historia["normal_epilogo_6"] = normal_epilogo_6

        normal_epilogo_7_amistad = NodoHistoria(
            "normal_epilogo_7_amistad",
            "LA AMISTAD CON BARBARA (CONSOLIDACIÓN)",
            "Barbara (Oráculo) y tú se reúnen en un techo. Ella está orgullosa de ti. "
            "Te da un microchip que contiene una lista de los mayores contactos criminales "
            "de Blockbuster que aún operan. Es la clave para desmantelar lo que queda del mal.",
            "nightwing_and_oracle_rooftop.png"
        )
        normal_epilogo_7_amistad.agregar_opcion("Usar la lista para una purga final de los secuaces", "normal_epilogo_8", stat="reputacion", cambio=10)
        self.historia["normal_epilogo_7_amistad"] = normal_epilogo_7_amistad

        normal_epilogo_8 = NodoHistoria(
            "normal_epilogo_8",
            "LA PURGA DE BLÜDHAVEN",
            "Pasas un mes limpiando la ciudad con la lista de Oráculo. Es un éxito rotundo. "
            "El crimen se reduce a niveles históricos. Te has convertido en el verdadero "
            "Guardián de Blüdhaven. La ciudad te ama y confía en ti.",
            "nightwing_bludhaven_clean.png"
        )
        normal_epilogo_8.agregar_opcion("Tomar un descanso bien merecido", "normal_epilogo_9_descanso", stat="salud", cambio=10)
        self.historia["normal_epilogo_8"] = normal_epilogo_8

        normal_epilogo_9_descanso = NodoHistoria(
            "normal_epilogo_9_descanso",
            "UN MOMENTO DE PAZ",
            "Sales a la luz del día. La gente te sonríe. Un niño lleva una camiseta de Nightwing. "
            "Te das cuenta de que tu trabajo ha tenido un impacto real. Bruce te llama y te invita "
            "a visitar Gotham para un aniversario de tu llegada. ¿Aceptas la invitación de vuelta a casa?",
            "dick_grayson_day_off.png"
        )
        normal_epilogo_9_descanso.agregar_opcion("Aceptar la invitación de Bruce (Reunificación)", "normal_epilogo_final", stat="reputacion", cambio=5) # Bucle al Epílogo Final
        self.historia["normal_epilogo_9_descanso"] = normal_epilogo_9_descanso



        # MODO DIFÍCIL: EL CAMINO DE LA AUTO-DESTRUCCIÓN


        dificil_relleno_1 = NodoHistoria(
            "dificil_relleno_1",
            "LA TENTACIÓN DE LA DROGA",
            "Una noche, encuentras un almacén de Blockbuster lleno de una nueva droga peligrosa. "
            "El criminal que la vende te ofrece una suma gigantesca para que 'mires a otro lado'. "
            "Tu situación financiera es mala. La tentación es real.",
            "nightwing_drug_temptation.png"
        )
        dificil_relleno_1.agregar_opcion("Destruir la droga y al criminal (Integridad)", "dificil_relleno_2", stat="reputacion", cambio=10)
        dificil_relleno_1.agregar_opcion("Aceptar el dinero y el silencio (Caída)", "dificil_relleno_2", stat="recursos", cambio=10, stat2="reputacion", cambio2=-20)
        self.historia["dificil_relleno_1"] = dificil_relleno_1

        grayson_dificil_relleno_2 = NodoHistoria(
            "grayson_dificil_relleno_2",
            "EL PRECIO DE LA INTEGRIDAD",
            "Si aceptaste el dinero: Te sientes mal, pero el dinero ayuda a mejorar tu equipo (recursos +10). "
            "Si destruiste: Blockbuster se entera y te odia aún más. La guerra es personal.",
            "nightwing_consequence.png"
        )
        grayson_dificil_relleno_2.agregar_opcion("Bloquear la operación de droga restante de Blockbuster", "grayson_dificil_relleno_3", stat="reputacion", cambio=5)
        self.historia["grayson_dificil_relleno_2"] = grayson_dificil_relleno_2

        grayson_dificil_relleno_3 = NodoHistoria(
            "grayson_dificil_relleno_3",
            "EL RECURSO DE LAS SOMBRAS",
            "Necesitas información interna. Saïko te contacta. Te pide que robes una lista de "
            "miembros del Departamento de Policía de Gotham que son leales a Gordon. "
            "A cambio, te dará la ubicación de la base de Blockbuster.",
            "saiko_offer_2.png"
        )
        grayson_dificil_relleno_3.agregar_opcion("Robar la lista y traicionar a Gordon (Caída Moral)", "grayson_dificil_relleno_4_traicion", stat="reputacion", cambio=-20)
        grayson_dificil_relleno_3.agregar_opcion("Robar la lista y alterarla antes de dársela (Doble Agente)", "grayson_dificil_relleno_4_agente", stat="recursos", cambio=5)
        grayson_dificil_relleno_3.agregar_opcion("Rechazar la oferta y buscar otra fuente de información", "grayson_dificil_relleno_4_rechazo", stat="salud", cambio=-5)
        self.historia["grayson_dificil_relleno_3"] = grayson_dificil_relleno_3

        grayson_dificil_relleno_4_traicion = NodoHistoria(
            "grayson_dificil_relleno_4_traicion",
            "LA TRAICIÓN A GORDON",
            "Le das la lista a Saïko. Él se burla: 'Incluso en tu rabia, eres predecible, Dick Grayson.' "
            "La Corte de los Búhos ahora tiene la información para dañar a Gordon. Tu acto de traición "
            "te persigue. Saïko te da la ubicación de Blockbuster: una plataforma petrolera abandonada.",
            "nightwing_traitor.png"
        )
        grayson_dificil_relleno_4_traicion.agregar_opcion("Ir a la plataforma petrolera", "grayson_dificil_plataforma_petrolera", stat="reputacion", cambio=-5)
        self.historia["grayson_dificil_relleno_4_traicion"] = grayson_dificil_relleno_4_traicion

        grayson_dificil_relleno_4_agente = NodoHistoria(
            "grayson_dificil_relleno_4_agente",
            "EL JUEGO DE ESPEJOS",
            "Robas la lista, pero la alteras, agregando nombres falsos y eliminando a los verdaderos leales. "
            "Saïko te da la ubicación de Blockbuster. Es una victoria, pero te has adentrado más "
            "en el juego de la desconfianza y la mentira. Te conviertes en tu propio maestro de la conspiración.",
            "nightwing_conspiracy.png"
        )
        grayson_dificil_relleno_4_agente.agregar_opcion("Ir a la plataforma petrolera", "grayson_dificil_plataforma_petrolera", stat="recursos", cambio=3)
        self.historia["grayson_dificil_relleno_4_agente"] = grayson_dificil_relleno_4_agente

        grayson_dificil_relleno_4_rechazo = NodoHistoria(
            "grayson_dificil_relleno_4_rechazo",
            "EL PRECIO DE LA MORALIDAD",
            "Rechazas la oferta. Saïko se enfurece y te envía a un Talón para que te enfrente. "
            "La pelea es brutal. Apenas sobrevives. Te das cuenta de que al ser moral, has perdido "
            "la ventaja de la información. Ahora dependes de la suerte.",
            "nightwing_vs_talon_2.png"
        )
        grayson_dificil_relleno_4_rechazo.agregar_opcion("Buscar la base de Blockbuster por ti mismo (Lucha de la información)", "grayson_dificil_plataforma_petrolera", stat="salud", cambio=-10)
        self.historia["grayson_dificil_relleno_4_rechazo"] = grayson_dificil_relleno_4_rechazo

        grayson_dificil_plataforma_petrolera = NodoHistoria(
            "grayson_dificil_plataforma_petrolera",
            "LA PLATA FORMA EN LLAMAS",
            "La plataforma petrolera abandonada de Blockbuster está en llamas. Es una trampa. "
            "Tienes que enfrentarte a Blockbuster rodeado de sus matones, en un entorno altamente peligroso. "
            "Hay una oportunidad: una válvula que si se abre, inundará la plataforma, "
            "pero también te atrapará.",
            "nightwing_oil_rig_fight.png"
        )
        grayson_dificil_plataforma_petrolera.agregar_opcion("Abrir la válvula y luchar en el agua (Riesgo total)", "grayson_dificil_final_water", stat="reputacion", cambio=10, stat2="salud", cambio2=-5)
        grayson_dificil_plataforma_petrolera.agregar_opcion("Luchar contra Blockbuster en la cubierta de fuego (Combate directo)", "grayson_dificil_final_fire", stat="salud", cambio=-10)
        self.historia["grayson_dificil_plataforma_petrolera"] = grayson_dificil_plataforma_petrolera


        dificil_final_water = NodoHistoria(
            "dificil_final_water",
            "INUNDACIÓN LETAL",
            "Abres la válvula. El agua inunda la plataforma, creando un caos. Blockbuster lucha "
            "en el agua, que se convierte en tu aliado. Lo inmovilizas y lo entregas a la policía, "
            "pero sus matones mueren ahogados en el caos. Tienes éxito, pero eres responsable de muertes.",
            "nightwing_water_fight_bloody.png"
        )
        dificil_final_water.agregar_opcion("Aceptar las consecuencias de tus métodos extremos", "dificil_final_oscuro", stat="salud", cambio=-10) # Bucle a Final Oscuro
        self.historia["dificil_final_water"] = dificil_final_water

        dificil_final_fire = NodoHistoria(
            "dificil_final_fire",
            "EN LA LLAMA",
            "Luchas contra Blockbuster en medio del fuego. Lo derrotas usando tus palos de eskrima "
            "electrificados para apuntar a su corazón débil. Blockbuster grita y el fuego se propaga. "
            "Lo dejas allí, a su suerte, con la plataforma a punto de explotar. Te vas, sin mirar atrás.",
            "nightwing_fire_escape.png"
        )
        dificil_final_fire.agregar_opcion("Dejar a Blockbuster a su destino (Muerte indirecta)", "dificil_final_oscuro", stat="reputacion", cambio=-20) # Bucle a Final Oscuro
        self.historia["dificil_final_fire"] = dificil_final_fire

        dificil_relleno_5 = NodoHistoria(
            "dificil_relleno_5",
            "LA MENTIRA DE LA COOPERACIÓN",
            "Si escogiste el 'Final Oscuro': Te sientes más efectivo, pero solo. Saïko te llama "
            "y te felicita por tu crueldad: 'Ahora estamos cerca, Dick. Pronto serás uno de nosotros.' "
            "Te ofrece una última prueba: unirte a él en un asalto a la base de Batman en Gotham.",
            "saiko_call_final.png"
        )
        dificil_relleno_5.agregar_opcion("Aceptar la misión y unirte a Saïko (Caída final)", "dificil_final_talon", stat="salud", cambio=-20) # Bucle a Final Talon
        dificil_relleno_5.agregar_opcion("Usar esta información para emboscar a Saïko", "dificil_emboscada_saiko", stat="reputacion", cambio=15)
        self.historia["dificil_relleno_5"] = dificil_relleno_5

        dificil_emboscada_saiko = NodoHistoria(
            "dificil_emboscada_saiko",
            "LA ULTIMA CARTA",
            "Le tiendes una trampa a Saïko en la antigua guarida de tus padres, el Haly's Circus. "
            "Es una trampa emocional. Saïko se enfurece. Luchan sobre el trapecio. "
            "Te das cuenta de que tu camino siempre ha sido diferente al de él. "
            "Saïko te pide que lo dejes caer: '¡Sé libre, Dick Grayson!'",
            "nightwing_saiko_circus_final.png"
        )
        dificil_emboscada_saiko.agregar_opcion("Salvar a Saïko y entregarlo (Redención)", "dificil_final_redencion", stat="reputacion", cambio=30) # Bucle a Final Redención
        dificil_emboscada_saiko.agregar_opcion("Dejarlo caer (Oscuridad)", "dificil_final_oscuro", stat="salud", cambio=-10) # Bucle a Final Oscuro
        self.historia["dificil_emboscada_saiko"] = dificil_emboscada_saiko

        dificil_relleno_6 = NodoHistoria(
            "dificil_relleno_6",
            "EL DILEMA DE LA BOMBA",
            "Si escogiste el 'Final Oscuro': Una bomba está a punto de explotar en un orfanato. "
            "Blockbuster la puso. Tienes tiempo para desactivarla o para huir y dejar que el mundo "
            "vea lo que la corrupción hace. Tu lado oscuro te pide que huyas.",
            "nightwing_bomb_dilemma.png"
        )
        dificil_relleno_6.agregar_opcion("Desactivar la bomba y salvar a los niños (Luz)", "dificil_relleno_7_luz", stat="reputacion", cambio=20)
        dificil_relleno_6.agregar_opcion("Dejar que la bomba explote para sembrar el pánico (Oscuridad)", "dificil_relleno_7_oscuridad", stat="reputacion", cambio=-25)
        self.historia["dificil_relleno_6"] = dificil_relleno_6

        dificil_relleno_7_luz = NodoHistoria(
            "dificil_relleno_7_luz",
            "UN RAYO DE ESPERANZA",
            "Salvas a los niños. El acto te redime un poco. La Comisaria Rohrbach te mira "
            "con respeto. 'Gracias, Nightwing. Todavía hay algo de bien en ti.' "
            "Sientes un destello de tu antiguo yo, que te guía a Saïko para una última confrontación.",
            "nightwing_children_safe.png"
        )
        dificil_relleno_7_luz.agregar_opcion("Buscar la confrontación final con Saïko (Oportunidad de Redención)", "dificil_emboscada_saiko", stat="salud", cambio=5) # Bucle a la Emboscada
        self.historia["dificil_relleno_7_luz"] = dificil_relleno_7_luz

        dificil_relleno_7_oscuridad = NodoHistoria(
            "dificil_relleno_7_oscuridad",
            "EL PRECIO DE LA INDIFERENCIA",
            "Huyes. La bomba explota. La ciudad está de rodillas. El caos es total. "
            "El Joker te llama y se ríe: '¡Ahora sí que eres divertido, Dickie!' "
            "Has perdido la oportunidad de ser un héroe. Ya no hay vuelta atrás.",
            "bludhaven_explosion.png"
        )
        dificil_relleno_7_oscuridad.agregar_opcion("Aceptar tu destino como el protector oscuro de la ciudad", "dificil_final_oscuro", stat="salud", cambio=-15) # Bucle a Final Oscuro
        self.historia["dificil_relleno_7_oscuridad"] = dificil_relleno_7_oscuridad

        dificil_relleno_8 = NodoHistoria(
            "dificil_relleno_8",
            "LA CAZA DE LA FAMILIA",
            "Si escogiste el 'Final Talon': Saïko te da tu primera misión real: rastrear y neutralizar "
            "a Batgirl (Oráculo) para que la Bat-familia quede ciega. Tienes que usar tus conocimientos "
            "sobre ella, la persona que una vez fue tu amiga, para derrotarla.",
            "talon_chasing_oracle.png"
        )
        dificil_relleno_8.agregar_opcion("Traicionar a Saïko y alertar a Oráculo", "dificil_relleno_9_traicion", stat="reputacion", cambio=30)
        dificil_relleno_8.agregar_opcion("Cumplir la misión de Saïko (Caída irredimible)", "dificil_final_talon", stat="salud", cambio=-20) # Bucle a Final Talon
        self.historia["dificil_relleno_8"] = dificil_relleno_8

        dificil_relleno_9_traicion = NodoHistoria(
            "dificil_relleno_9_traicion",
            "EL VUELO DEL ÁGUILA",
            "Le envías un mensaje a Oráculo. 'No confíes en el pájaro. Viene por ti.' "
            "Barbara se da cuenta de que es una trampa. Ella te ayuda a escapar. "
            "Has traicionado a Saïko y has elegido a tu familia. Es tu última oportunidad de redención.",
            "nightwing_helps_oracle.png"
        )
        dificil_relleno_9_traicion.agregar_opcion("Unirte a Oráculo y a la Bat-familia", "dificil_final_redencion", stat="reputacion", cambio=15) # Bucle a Final Redención
        self.historia["dificil_relleno_9_traicion"] = dificil_relleno_9_traicion

        dificil_relleno_10 = NodoHistoria(
            "dificil_relleno_10",
            "LA SOMBRA DEL HIJO ROJO",
            "Si escogiste el 'Final Oscuro' o el 'Final Antihéroe': Red Hood (Jason Todd) te encuentra "
            "en Blüdhaven. Te mira, y tú a él. Él usa métodos letales, tú usas métodos muy duros. "
            "'Nos parecemos, Dickie. Tú eres mi Robin. ¿Por qué no nos unimos? Con nuestros métodos, "
            "podríamos limpiar este infierno en una semana.'",
            "nightwing_and_redhood_dark.png"
        )
        dificil_relleno_10.agregar_opcion("Unirte a Red Hood para una noche de 'limpieza'", "dificil_relleno_11_jason", stat="reputacion", cambio=-15)
        dificil_relleno_10.agregar_opcion("Rechazarlo y reafirmar tu código (incluso si es duro)", "dificil_relleno_11_rechazo", stat="salud", cambio=5)
        self.historia["dificil_relleno_10"] = dificil_relleno_10

        dificil_relleno_11_jason = NodoHistoria(
            "dificil_relleno_11_jason",
            "LA NOCHE SANGRIENTA",
            "Patrullas con Jason. Es rápido, eficiente, pero letal. Lo ves matar a un criminal. "
            "La culpa te consume, pero el resultado es rápido. Sientes la adrenalina y la justificación. "
            "Bruce te llama. '¿Qué has hecho, Dick?'",
            "nightwing_and_redhood_kill.png"
        )
        dificil_relleno_11_jason.agregar_opcion("Colgar a Bruce y aceptar tu nuevo camino", "dificil_final_oscuro", stat="reputacion", cambio=-20) # Bucle a Final Oscuro
        dificil_relleno_11_jason.agregar_opcion("Llorar con Bruce y buscar la redención", "dificil_final_redencion", stat="salud", cambio=-10) # Bucle a Final Redención

        dificil_relleno_11_rechazo = NodoHistoria(
            "dificil_relleno_11_rechazo",
            "EL ÚLTIMO CÓDIGO",
            "Rechazas a Jason. 'No soy un asesino, Jason. Todavía no.' Él se ríe. 'Eres un tonto, Dickie.' "
            "Te has salvado de la caída total. Jason te da una pista sobre Blockbuster y se va. "
            "Te das cuenta de que al menos, aún hay una línea que no quieres cruzar.",
            "nightwing_rejects_redhood.png"
        )
        dificil_relleno_11_rechazo.agregar_opcion("Usar la pista de Jason para el enfrentamiento final", "normal_blockbuster_final_fight", stat="recursos", cambio=5) # Bucle a pelea final (para un final antihéroe)
        self.historia["dificil_relleno_11_rechazo"] = dificil_relleno_11_rechazo

        dificil_relleno_12 = NodoHistoria(
            "dificil_relleno_12",
            "EL ENCUENTRO CON BATMAN (CAMINO OSCURO)",
            "Si escogiste una ruta oscura: Batman te rastrea en Blüdhaven. Te confronta por tus métodos "
            "y tus mentiras. 'Te has convertido en todo lo que juramos combatir, Dick. Tienes que parar.' "
            "La pelea es inevitable. Tienes que decidir si lo sometes o si te sometes a él.",
            "nightwing_vs_batman_dark.png"
        )
        dificil_relleno_12.agregar_opcion("Derrotar a Batman (Caída total y traición)", "dificil_final_traicion_batman", stat="reputacion", cambio=-30)
        dificil_relleno_12.agregar_opcion("Dejar que Batman te someta (Redención tardía)", "dificil_final_redencion", stat="salud", cambio=5) # Bucle a la Redención
        self.historia["dificil_relleno_12"] = dificil_relleno_12

        dificil_final_traicion_batman = NodoHistoria(
            "dificil_final_traicion_batman",
            "EL CAMPEÓN DE LA CORTE",
            "Derrotas a Batman y lo dejas atado en un techo con una nota: 'Ya no soy tu hijo.' "
            "La Corte de los Búhos te aplaude. Saïko te recibe como su nuevo líder. "
            "Te has convertido en el Talón Supremo, el asesino de tu familia. El mal ha ganado. (FIN)",
            "final_nightwing_talon.png" # Usamos el mismo recurso de imagen para el final talon
        )
        dificil_final_traicion_batman.es_final = True
        self.historia["dificil_final_traicion_batman"] = dificil_final_traicion_batman

        dificil_relleno_13 = NodoHistoria(
            "dificil_relleno_13",
            "LA LLAMADA DE ALFRED (CAMINO REDENTOR)",
            "Si escogiste una ruta de redención: Alfred te llama. Está preocupado. 'Maestro Dick, "
            "no importa lo que haya pasado, siempre hay un camino de vuelta. El Señor Wayne te ama. "
            "No dejes que la oscuridad gane.' Te da la ubicación de un arma secreta de la Corte de los Búhos: "
            "un nido de Talones que puedes neutralizar para debilitar a Saïko.",
            "alfred_call_final_dificil.png"
        )
        dificil_relleno_13.agregar_opcion("Usar la información para asestar el golpe final a la Corte", "dificil_asalto_batfamilia", stat="reputacion", cambio=10) # Bucle a la redención
        self.historia["dificil_relleno_13"] = dificil_relleno_13

        dificil_relleno_14 = NodoHistoria(
            "dificil_relleno_14",
            "EL CANTO DE LA SIRENA",
            "Si has caído en el lado oscuro (puntuación de reputación muy baja): Saïko te llama "
            "para una reunión. Te ofrece el control total de Blüdhaven, una ciudad que ahora teme a "
            "su vigilante. 'Deja el traje de Nightwing. Ponte el negro. Te ofrezco la inmortalidad.' "
            "Es la última tentación.",
            "saiko_final_temptation.png"
        )
        dificil_relleno_14.agregar_opcion("Aceptar la oferta de Saïko y su poder", "dificil_final_talon", stat="salud", cambio=-20) # Bucle a Final Talon
        dificil_relleno_14.agregar_opcion("Rechazarlo y luchar hasta la muerte por lo que queda de tu alma", "dificil_relleno_15_lucha_final", stat="reputacion", cambio=25)
        self.historia["dificil_relleno_14"] = dificil_relleno_14

        dificil_relleno_15_lucha_final = NodoHistoria(
            "dificil_relleno_15_lucha_final",
            "EL DUELO POR EL ALMA",
            "Te enfrentas a Saïko por última vez. La pelea es una carrera de muerte. "
            "En un momento de la lucha, Saïko te quita la máscara y te llama: '¡Dick Grayson, "
            "tú eres un Talón! Acéptalo.' Te da un golpe demoledor.",
            "nightwing_vs_saiko_mask_off.png"
        )
        dificil_relleno_15_lucha_final.agregar_opcion("Usar un arma letal para someter a Saïko (Oscuridad total)", "dificil_final_oscuro", stat="salud", cambio=-10) # Bucle a Final Oscuro
        dificil_relleno_15_lucha_final.agregar_opcion("Usar un gas tranquilizante de Alfred para someterlo (Redención)", "dificil_final_redencion", stat="reputacion", cambio=30) # Bucle a Final Redención
        self.historia["dificil_relleno_15_lucha_final"] = dificil_relleno_15_lucha_final

        dificil_relleno_16 = NodoHistoria(
            "dificil_relleno_16",
            "LA BÚSQUEDA DE LA FAMILIA",
            "Si tienes una puntuación de salud alta (Redención en progreso): Te encuentras con "
            "Tim Drake (Robin) y Batgirl (Barbara) en una misión. Te invitan a unirte a ellos. "
            "Es un recordatorio de lo que perdiste. Te das cuenta de que no quieres ser como Saïko.",
            "nightwing_batfamily_redemption.png"
        )
        dificil_relleno_16.agregar_opcion("Unirte al equipo y confesar todo sobre la Corte", "dificil_asalto_batfamilia", stat="reputacion", cambio=15) # Bucle a la Redención
        dificil_relleno_16.agregar_opcion("Rechazar la oferta y continuar solo (Riesgo de caída)", "dificil_relleno_15_lucha_final", stat="salud", cambio=-5)
        self.historia["dificil_relleno_16"] = dificil_relleno_16



        dificil_consecuencia_1 = NodoHistoria(
            "dificil_consecuencia_1",
            "LA CULPA DEL ASESINO (FINAL OSCURO)",
            "Si escogiste el Final Oscuro (Muerte indirecta o directa): Te has convertido en "
            "el 'héroe' que mata para proteger. Tu salud mental se deteriora. Bruce te ha abandonado. "
            "Te encuentras solo y consumido por la culpa. El único contacto que tienes es Jason Todd, "
            "quien te felicita por 'finalmente entenderlo'.",
            "nightwing_dark_reflection.png"
        )
        dificil_consecuencia_1.agregar_opcion("Buscar ayuda psicológica anónima (Peligro de exposición)", "dificil_consecuencia_2_psico", stat="salud", cambio=10)
        dificil_consecuencia_1.agregar_opcion("Rechazar la ayuda y sumergirte en el trabajo (Caída)", "dificil_consecuencia_2_caida", stat="reputacion", cambio=-5)
        self.historia["dificil_consecuencia_1"] = dificil_consecuencia_1

        dificil_consecuencia_2_psico = NodoHistoria(
            "dificil_consecuencia_2_psico",
            "LA LUCHA INTERNA",
            "Buscas ayuda. El terapeuta te obliga a confrontar tus acciones. Te sientes un poco mejor, "
            "pero el precio de la paz es el riesgo de que tu secreto se revele. Te das cuenta de que "
            "tu vida como Nightwing está llegando a un punto de quiebre. Ya no puedes mantener la fachada.",
            "nightwing_therapy.png"
        )
        dificil_consecuencia_2_psico.agregar_opcion("Entregarte a la policía por tus crímenes (Sacrificio final)", "dificil_final_sacrificio", stat="reputacion", cambio=30)
        dificil_consecuencia_2_psico.agregar_opcion("Huir de Blüdhaven y desaparecer (Fin del Héroe)", "dificil_final_desaparicion", stat="salud", cambio=-10)
        self.historia["dificil_consecuencia_2_psico"] = dificil_consecuencia_2_psico

        dificil_consecuencia_2_caida = NodoHistoria(
            "dificil_consecuencia_2_caida",
            "EL ABISMO",
            "Te niegas a confrontar tu dolor. Te conviertes en un vigilante aún más brutal. "
            "Un día, accidentalmente hieres gravemente a un inocente. Te das cuenta de que has "
            "perdido el control. La policía te está cazando. No hay vuelta atrás.",
            "nightwing_accident_loss.png"
        )
        dificil_consecuencia_2_caida.agregar_opcion("Huir de la policía y convertirte en fugitivo", "dificil_final_desaparicion", stat="reputacion", cambio=-20)
        self.historia["dificil_consecuencia_2_caida"] = dificil_consecuencia_2_caida

        dificil_final_sacrificio = NodoHistoria(
            "dificil_final_sacrificio",
            "LA ÚLTIMA OFRENDA - FINAL SACRIFICIO",
            "Te entregas a la policía, confesando tus crímenes de vigilante. La Bat-familia te defiende, "
            "pero aceptas tu destino. Tu acto de sacrificio inspira a Blüdhaven a limpiar el crimen "
            "de forma legal. Aunque estás en prisión, has redimido tu alma y has salvado la ciudad. "
            "La luz de Dick Grayson brilla por última vez. (FIN)",
            "final_nightwing_sacrifice.png"
        )
        dificil_final_sacrificio.es_final = True
        self.historia["dificil_final_sacrificio"] = dificil_final_sacrificio

        dificil_final_desaparicion = NodoHistoria(
            "dificil_final_desaparicion",
            "EL FANTASMA DE NIGHTWING - FINAL DESAPARICIÓN",
            "Desapareces de la noche a la mañana. Dejas atrás la máscara y el traje, huyendo "
            "de la culpa y de la cacería policial. El mundo cree que Nightwing ha muerto. "
            "Vives como un fugitivo, una sombra. Has elegido tu vida sobre tu legado. "
            "El héroe ha muerto. Solo queda Dick Grayson. (FIN)",
            "final_nightwing_fugitive.png"
        )
        dificil_final_desaparicion.es_final = True
        self.historia["dificil_final_desaparicion"] = dificil_final_desaparicion


        relleno_cierre_1 = NodoHistoria(
            "relleno_cierre_1",
            "PREPARACIÓN PARA EL CIERRE",
            "Este nodo se usará para enlazar los finales del Modo Difícil con una estructura "
            "de cierre final en la última entrega, asegurando que todos los caminos lleven a una "
            "conclusión narrativa clara.",
            "placeholder_closure.png"
        )
        self.historia["relleno_cierre_1"] = relleno_cierre_1

        relleno_cierre_2 = NodoHistoria(
            "relleno_cierre_2",
            "CONSOLIDACIÓN NARRATIVA",
            "Asegurando que la transición de Robin a Nightwing (Modo Fácil a Normal) y "
            "las ramificaciones del Modo Difícil tengan la profundidad suficiente.",
            "placeholder_narrative.png"
        )
        self.historia["relleno_cierre_2"] = relleno_cierre_2

        relleno_cierre_3 = NodoHistoria(
            "relleno_cierre_3",
            "REVISIÓN DE ESTRUCTURA",
            "Verificando que los bucles de los finales (redencion, oscuro, talon, etc.) "
            "del Modo Difícil funcionen correctamente y no generen loops infinitos.",
            "placeholder_structure.png"
        )
        self.historia["relleno_cierre_3"] = relleno_cierre_3

        dificil_asalto_batfamilia = NodoHistoria(
            "dificil_asalto_batfamilia",
            "EL ASALTO A LA CORTE DE LOS BÚHOS",
            "Te has unido a la Bat-familia (Batman, Oráculo, Robin/Tim). Usas tu conocimiento interno "
            "para liderar un asalto final al nido principal de la Corte de los Búhos. La pelea "
            "es contra docenas de Talones, y el duelo final es contra Saïko. Es tu última oportunidad "
            "de demostrar que todavía eres Dick Grayson.",
            "nightwing_batfamily_final_assault.png"
        )
        dificil_asalto_batfamilia.agregar_opcion("Trabajar en equipo con la Bat-familia para derrotar a Saïko", "dificil_final_redencion", stat="reputacion", cambio=50)
        dificil_asalto_batfamilia.agregar_opcion("Ignorar al equipo y confrontar a Saïko solo (Riesgo de recaída)", "dificil_final_lucha_solo", stat="salud", cambio=-15)
        self.historia["dificil_asalto_batfamilia"] = dificil_asalto_batfamilia

        dificil_final_lucha_solo = NodoHistoria(
            "dificil_final_lucha_solo",
            "EL HÉROE SOLITARIO",
            "Te enfrentas a Saïko solo. Saïko te derrota, pero la Bat-familia aparece para salvarte. "
            "Te das cuenta de tu ego. La Bat-familia te perdona y Saïko es capturado. "
            "Aprendes la lección: la fuerza está en la familia, no en la soledad. Es una redención dolorosa.",
            "nightwing_saved_by_batman.png"
        )
        dificil_final_lucha_solo.agregar_opcion("Aceptar el rescate y la humillación", "dificil_final_redencion", stat="salud", cambio=5)
        self.historia["dificil_final_lucha_solo"] = dificil_final_lucha_solo

        dificil_final_redencion = NodoHistoria(
            "dificil_final_redencion",
            "NIGHTWING: EL REGRESO DEL HIJO PRÓDIGO - FINAL REDENCIÓN",
            "Has derrotado a Saïko y a la Corte de los Búhos con la ayuda de la Bat-familia. "
            "Tu alma está limpia. La Bat-familia te acoge de nuevo. Te quedas en Blüdhaven, "
            "pero ahora con el apoyo de tu familia. Has vencido la oscuridad interna y externa. "
            "Tu legado es la prueba de que incluso la persona más oscura puede encontrar la luz. "
            "El Boy Wonder ha madurado en el Héroe de la Esperanza. (FIN)",
            "final_dificil_redencion.png"
        )
        dificil_final_redencion.es_final = True
        self.historia["dificil_final_redencion"] = dificil_final_redencion

        dificil_final_talon = NodoHistoria(
            "dificil_final_talon",
            "EL TALÓN SUPREMO - FINAL CAÍDA",
            "Has traicionado a Batman y te has unido a Saïko/La Corte de los Búhos. Eres el nuevo "
            "líder de los Talones. Tu agilidad y tu conocimiento del código de Batman te convierten "
            "en el arma perfecta de la Corte. Has perdido tu identidad, tu moral y tu familia. "
            "Dick Grayson está muerto. Solo queda el Talón, una sombra inmortal al servicio de la oscuridad. "
            "Tu legado es la traición. El final es frío y eterno. (FIN)",
            "final_dificil_talon.png"
        )
        dificil_final_talon.es_final = True
        self.historia["dificil_final_talon"] = dificil_final_talon

        cierre_epilogo_1 = NodoHistoria(
            "cierre_epilogo_1",
            "NUEVOS COMIENZOS",
            "Independientemente del final, la historia de Nightwing continúa. El crimen en "
            "Blüdhaven siempre regresará, pero la ciudad ahora tiene un héroe a su altura. "
            "Si escogiste el camino de la luz, eres el Guardián. Si escogiste la oscuridad, "
            "eres la Sombra. El futuro está en tus manos, Dick Grayson.",
            "nightwing_epilogo_rooftop.png"
        )
        self.historia["cierre_epilogo_1"] = cierre_epilogo_1

        self.historia["grayson_normal_bludhaven_inicio"].agregar_opcion("Continuar la leyenda", "cierre_epilogo_1", stat="reputacion", cambio=0)








#####################################################################################################################################################




    def inicializar_historias_tim_drake(self):
        """Crear todos los nodos de historia para Tim Drake"""
        # MODO FÁCIL: EL CAMINO HACIA ROBIN (17 nodos)
        tim_inicio = NodoHistoria(
            "tim_facil_inicio",
            "EL JOVEN DETECTIVE",
            "Gotham City, presente. Eres Tim Drake, un brillante joven de 13 años con una mente "
            "analítica excepcional. Hace años, cuando tenías 9, asististe al circo Haly y viste "
            "a los Grayson Voladores caer. Pero lo que nadie sabe es que has descubierto algo "
            "increíble: Batman es Bruce Wayne, y el primer Robin era Dick Grayson. Y ahora, "
            "tras la muerte del segundo Robin, Jason Todd, has notado que Batman se vuelve "
            "cada vez más temerario y violento.",
            "crime_alley.png"
        )
        tim_inicio.agregar_opcion("Contactar a Dick Grayson", "tim_facil_contacto_dick", stat="recursos", cambio=1)
        tim_inicio.agregar_opcion("Investigar más sobre Batman", "tim_facil_investigacion", stat="recursos", cambio=2)
        tim_inicio.agregar_opcion("Acercarte directamente a Bruce Wayne", "tim_facil_acercamiento_bruce", stat="reputacion", cambio=-5)
        self.historia["tim_facil_inicio"] = tim_inicio

        tim_contacto_dick = NodoHistoria(
            "tim_facil_contacto_dick",
            "ENCUENTRO CON NIGHTWING",
            "Después de mucha investigación, localizas a Dick Grayson, ahora conocido como Nightwing, "
            "en Blüdhaven. Le explicas cómo descubriste su identidad y la de Batman. Al principio "
            "está sorprendido y desconfiado, pero tu análisis detallado lo impresiona. 'Batman "
            "necesita un Robin,' le dices. 'Para mantener su humanidad.'",
            "tim_encuentro_nightwing.png"
        )
        tim_contacto_dick.agregar_opcion("Pedirle que vuelva a ser Robin", "tim_facil_peticion_dick", stat="reputacion", cambio=5)
        tim_contacto_dick.agregar_opcion("Sugerir que tú podrías ser Robin", "tim_facil_sugerencia_robin", stat="reputacion", cambio=10)
        self.historia["tim_facil_contacto_dick"] = tim_contacto_dick

        tim_investigacion = NodoHistoria(
            "tim_facil_investigacion",
            "SIGUIENDO AL MURCIÉLAGO",
            "Durante semanas, sigues a Batman en sus patrullas nocturnas, documentando su comportamiento "
            "cada vez más agresivo. Una noche, casi mata a un criminal. Tus sospechas se confirman: "
            "sin un Robin que lo equilibre, Batman está perdiendo su camino. Necesitas actuar pronto.",
            "tim_siguiendo_a_batman.png"
        )
        tim_investigacion.agregar_opcion("Contactar a Dick Grayson con tus hallazgos", "tim_facil_contacto_dick", stat="reputacion", cambio=15)
        tim_investigacion.agregar_opcion("Intervenir en una patrulla de Batman", "tim_facil_intervencion", stat="salud", cambio=-10)
        self.historia["tim_facil_investigacion"] = tim_investigacion

        tim_acercamiento_bruce = NodoHistoria(
            "tim_facil_acercamiento_bruce",
            "CONFRONTANDO AL MURCIÉLAGO",
            "Te presentas en la Mansión Wayne y le dices a Bruce directamente que sabes que es Batman. "
            "Alfred está horrorizado. Bruce te mira con frialdad: 'No sé de qué hablas, joven.' Pero "
            "insistes, explicando tu razonamiento deductivo. Bruce te escucha, impresionado a su pesar.",
            "tim_confrontando_a_bruce.png"
        )
        tim_acercamiento_bruce.agregar_opcion("Explicar tu preocupación por su comportamiento", "tim_facil_preocupacion", stat="reputacion", cambio=10)
        tim_acercamiento_bruce.agregar_opcion("Ofrecerte como nuevo Robin", "tim_facil_ofrecimiento", stat="reputacion", cambio=-5)
        self.historia["tim_facil_acercamiento_bruce"] = tim_acercamiento_bruce

        tim_peticion_dick = NodoHistoria(
            "tim_facil_peticion_dick",
            "EL LEGADO CONTINÚA",
            "Le pides a Dick que vuelva a ser Robin. Él sonríe con tristeza: 'Ya no soy Robin, Tim. "
            "Soy Nightwing ahora. Mi tiempo con Batman terminó.' Pero ve tu determinación y añade: "
            "'Quizás Batman necesita un nuevo Robin. Alguien como tú.'",
            "tim_peticion_a_dick.png"
        )
        tim_peticion_dick.agregar_opcion("Considerar convertirte en Robin", "tim_facil_consideracion", stat="reputacion", cambio=15)
        self.historia["tim_facil_peticion_dick"] = tim_peticion_dick

        tim_sugerencia_robin = NodoHistoria(
            "tim_facil_sugerencia_robin",
            "UNA NUEVA PROPUESTA",
            "'Yo podría ser Robin,' dices con determinación. Dick te mira evaluativamente. 'No es un "
            "juego, Tim. Es peligroso.' Pero ve algo en ti, una chispa de potencial. 'Vamos a ver qué "
            "piensa Bruce,' dice finalmente. 'Pero no te hagas ilusiones.'",
            "tim_sugerencia_ser_robin.png"
        )
        tim_sugerencia_robin.agregar_opcion("Ir con Dick a ver a Batman", "tim_facil_encuentro_batman", stat="recursos", cambio=2)
        self.historia["tim_facil_sugerencia_robin"] = tim_sugerencia_robin

        tim_intervencion = NodoHistoria(
            "tim_facil_intervencion",
            "INTRUSIÓN PELIGROSA",
            "Sigues a Batman hasta un enfrentamiento con Dos Caras. La situación se complica cuando "
            "Batman y Nightwing, que estaba ayudando, caen en una trampa. Sin pensarlo dos veces, "
            "te pones un disfraz improvisado y entras en acción, usando tu ingenio para liberarlos.",
            "tim_intervencion_dos_caras.png"
        )
        tim_intervencion.agregar_opcion("Ayudar en la batalla", "tim_facil_prueba_fuego", stat="salud", cambio=-15, stat2="reputacion", cambio2=25)
        self.historia["tim_facil_intervencion"] = tim_intervencion

        tim_preocupacion = NodoHistoria(
            "tim_facil_preocupacion",
            "LA VERDAD INCÓMODA",
            "Le explicas a Bruce que has notado su comportamiento cada vez más violento desde la muerte "
            "de Jason. 'Batman necesita un Robin,' argumentas. 'Para recordarle por qué lucha.' Bruce "
            "guarda silencio, pero Alfred asiente imperceptiblemente. Has tocado una fibra sensible.",
            "tim_preocupacion_por_batman.png"
        )
        tim_preocupacion.agregar_opcion("Pedir ser entrenado", "tim_facil_peticion_entrenamiento", stat="reputacion", cambio=10)
        tim_preocupacion.agregar_opcion("Dar tiempo a Bruce para reflexionar", "tim_facil_tiempo_reflexion", stat="recursos", cambio=1)
        self.historia["tim_facil_preocupacion"] = tim_preocupacion

        tim_ofrecimiento = NodoHistoria(
            "tim_facil_ofrecimiento",
            "LA PROPUESTA AUDAZ",
            "'Quiero ser el nuevo Robin,' declaras. Bruce frunce el ceño: 'No. Nunca más.' Alfred "
            "interviene: 'Quizás deberíamos escuchar al joven, Maestro Bruce.' La tensión es palpable. "
            "Bruce te mira fijamente: 'Dame una razón por la que debería considerarlo.'",
            "tim_ofrecimiento_como_robin.png"
        )
        tim_ofrecimiento.agregar_opcion("Explicar tu teoría sobre Batman y Robin", "tim_facil_teoria", stat="reputacion", cambio=15)
        tim_ofrecimiento.agregar_opcion("Demostrar tus habilidades deductivas", "tim_facil_demostracion", stat="recursos", cambio=2)
        self.historia["tim_facil_ofrecimiento"] = tim_ofrecimiento

        tim_consideracion = NodoHistoria(
            "tim_facil_consideracion",
            "EL PESO DEL MANTO",
            "La idea de ser Robin te abruma. No eres un acróbata como Dick ni un luchador callejero como "
            "Jason. Eres un detective, un estratega. Dick ve tu duda: 'Robin no se trata de quién eres, "
            "sino de lo que representas. Y tú tienes lo más importante: el corazón.'",
            "tim_peso_del_manto.png"
        )
        tim_consideracion.agregar_opcion("Aceptar el desafío", "tim_facil_aceptacion", stat="reputacion", cambio=20)
        self.historia["tim_facil_consideracion"] = tim_consideracion

        tim_encuentro_batman = NodoHistoria(
            "tim_facil_encuentro_batman",
            "REUNIÓN EN LA BATCUEVA",
            "Dick te lleva a la Batcueva. Bruce está furioso al principio, pero Dick intercede: 'Escúchalo, "
            "Bruce. Es brillante.' Explicas tu teoría sobre por qué Batman necesita un Robin. Bruce guarda "
            "silencio, evaluándote. 'No es tan simple,' dice finalmente.",
            "tim_reunion_batcueva.png"
        )
        tim_encuentro_batman.agregar_opcion("Insistir en tu punto", "tim_facil_insistencia", stat="reputacion", cambio=5)
        tim_encuentro_batman.agregar_opcion("Aceptar su decisión", "tim_facil_aceptacion_decision", stat="reputacion", cambio=-5)
        self.historia["tim_facil_encuentro_batman"] = tim_encuentro_batman

        tim_prueba_fuego = NodoHistoria(
            "tim_facil_prueba_fuego",
            "EL RESCATE HEROICO",
            "Con ingenio y valentía, logras liberar a Batman y Nightwing de la trampa de Dos Caras. "
            "Juntos, derrotan a los criminales. Después, Batman te mira con una mezcla de asombro e "
            "irritación: 'Eso fue temerario... y valiente. ¿Quién eres?'",
            "tim_rescate_heroico.png"
        )
        tim_prueba_fuego.agregar_opcion("Revelar tu identidad y teoría", "tim_facil_revelacion", stat="reputacion", cambio=25)
        self.historia["tim_facil_prueba_fuego"] = tim_prueba_fuego

        tim_peticion_entrenamiento = NodoHistoria(
            "tim_facil_peticion_entrenamiento",
            "LA DECISIÓN DE BRUCE",
            "'Entréneme,' pides. 'No para reemplazar a Jason, sino para honrar lo que Robin significa.' "
            "Bruce parece conflictuado. Alfred interviene: 'Si me permite, Maestro Bruce, el joven tiene "
            "un punto válido.' Tras un largo silencio, Bruce asiente levemente.",
            "tim_peticion_entrenamiento.png"
        )
        tim_peticion_entrenamiento.agregar_opcion("Comenzar el entrenamiento", "tim_facil_entrenamiento", stat="salud", cambio=10, item="Oportunidad de Entrenamiento")
        self.historia["tim_facil_peticion_entrenamiento"] = tim_peticion_entrenamiento

        tim_tiempo_reflexion = NodoHistoria(
            "tim_facil_tiempo_reflexion",
            "PACIENCIA ESTRATÉGICA",
            "Decides dar tiempo a Bruce para procesar tus palabras. Días después, Alfred te contacta: "
            "'El Maestro Bruce desea hablar contigo.' Al regresar a la mansión, Bruce parece haber "
            "reflexionado. 'Quizás tengas razón,' admite. 'Pero ser Robin no es un juego.'",
            "tim_paciencia_estrategica.png"
        )
        tim_tiempo_reflexion.agregar_opcion("Expresar tu determinación", "tim_facil_determinacion", stat="reputacion", cambio=15)
        self.historia["tim_facil_tiempo_reflexion"] = tim_tiempo_reflexion

        tim_teoria = NodoHistoria(
            "tim_facil_teoria",
            "LA TEORÍA DEL EQUILIBRIO",
            "Le explicas a Bruce tu teoría: 'Batman y Robin son un equilibrio. Batman es la oscuridad "
            "necesaria, Robin es la luz que evita que esa oscuridad lo consuma todo. Sin Robin, Batman "
            "está perdiendo ese equilibrio.' Bruce te mira, impactado por la precisión de tu análisis.",
            "tim_teoria_equilibrio.png"
        )
        tim_teoria.agregar_opcion("Esperar su respuesta", "tim_facil_respuesta_bruce", stat="reputacion", cambio=20)
        self.historia["tim_facil_teoria"] = tim_teoria

        tim_demostracion = NodoHistoria(
            "tim_facil_demostracion",
            "EL JOVEN DETECTIVE",
            "Para demostrar tus habilidades, analizas un caso sin resolver en la computadora de la Batcueva. "
            "En minutos, identificas pistas que se pasaron por alto. Bruce observa en silencio. 'Impresionante,' "
            "admite finalmente. 'Pero ser Robin requiere más que inteligencia.'",
            "tim_demostracion_deductiva.png"
        )
        tim_demostracion.agregar_opcion("Pedir una oportunidad para probarte", "tim_facil_oportunidad", stat="reputacion", cambio=10)
        self.historia["tim_facil_demostracion"] = tim_demostracion

        tim_aceptacion = NodoHistoria(
            "tim_facil_aceptacion",
            "EL CAMINO ELEGIDO",
            "Decides aceptar el desafío. Dick sonríe: 'Vamos a ver a Bruce juntos. No será fácil convencerlo, "
            "pero creo que eres exactamente lo que Batman necesita ahora.' Te preparas para enfrentar al "
            "Caballero Oscuro, determinado a demostrar tu valía.",
            "tim_camino_elegido.png"
        )
        tim_aceptacion.agregar_opcion("Ir con Dick a la Batcueva", "tim_facil_encuentro_batman", stat="recursos", cambio=2)
        self.historia["tim_facil_aceptacion"] = tim_aceptacion

        tim_insistencia = NodoHistoria(
            "tim_facil_insistencia",
            "PERSISTENCIA",
            "'Batman necesita un Robin,' insistes. 'Y yo puedo serlo.' Bruce parece irritado, pero Dick "
            "interviene: 'Dale una oportunidad, Bruce. Mira lo que ha logrado solo.' Tras un tenso silencio, "
            "Bruce hace una oferta inesperada: 'Seis meses de entrenamiento. Luego decidiré.'",
            "tim_insistencia_y_oferta.png"
        )
        tim_insistencia.agregar_opcion("Aceptar sus términos", "tim_facil_entrenamiento", stat="salud", cambio=10, item="Oportunidad de Entrenamiento")
        self.historia["tim_facil_insistencia"] = tim_insistencia

        tim_aceptacion_decision = NodoHistoria(
            "tim_facil_aceptacion_decision",
            "RESPETO Y PACIENCIA",
            "Aceptas la decisión de Bruce, mostrando madurez. Esto parece impresionarlo más que tus argumentos. "
            "'No he dicho que no,' aclara. 'Solo que no es simple. Si realmente quieres esto, demuéstramelo.'",
            "tim_respeto_y_paciencia.png"
        )
        tim_aceptacion_decision.agregar_opcion("Preguntar cómo demostrarlo", "tim_facil_demostrar", stat="reputacion", cambio=10)
        self.historia["tim_facil_aceptacion_decision"] = tim_aceptacion_decision

        tim_revelacion = NodoHistoria(
            "tim_facil_revelacion",
            "LA VERDAD REVELADA",
            "'Soy Tim Drake,' revelas. 'Y sé que eres Bruce Wayne.' Les explicas cómo descubriste sus "
            "identidades y tu teoría sobre por qué Batman necesita un Robin. Batman y Nightwing intercambian "
            "miradas. 'Tiene potencial,' admite Nightwing. Batman asiente, reluctante pero impresionado.",
            "tim_verdad_revelada.png"
        )
        tim_revelacion.agregar_opcion("Pedir ser entrenado", "tim_facil_entrenamiento", stat="salud", cambio=10, item="Oportunidad de Entrenamiento")
        self.historia["tim_facil_revelacion"] = tim_revelacion

        tim_entrenamiento = NodoHistoria(
            "tim_facil_entrenamiento",
            "SEIS MESES DE PRUEBA",
            "Bruce acepta entrenarte, pero con condiciones estrictas: 'Seis meses. Sin excepciones. Sin "
            "patrullas hasta que yo lo diga.' El entrenamiento es brutal. A diferencia de Dick y Jason, "
            "no tienes habilidades acrobáticas naturales ni experiencia callejera. Pero tienes algo único: "
            "tu mente analítica y tu determinación inquebrantable.",
            "tim_seis_meses_prueba.png"
        )
        tim_entrenamiento.agregar_opcion("Enfocarte en habilidades detectivescas", "tim_facil_enfoque_detective", stat="recursos", cambio=3)
        tim_entrenamiento.agregar_opcion("Esforzarte en combate y acrobacias", "tim_facil_enfoque_combate", stat="salud", cambio=15)
        self.historia["tim_facil_entrenamiento"] = tim_entrenamiento

        tim_determinacion = NodoHistoria(
            "tim_facil_determinacion",
            "VOLUNTAD INQUEBRANTABLE",
            "'Entiendo los riesgos,' afirmas. 'Pero también entiendo lo que está en juego. Batman necesita "
            "un Robin, y estoy dispuesto a ser ese Robin.' Tu determinación parece resonar con Bruce. "
            "'Muy bien,' dice finalmente. 'Pero será bajo mis términos.'",
            "tim_voluntad_inquebrantable.png"
        )
        tim_determinacion.agregar_opcion("Aceptar sus condiciones", "tim_facil_entrenamiento", stat="salud", cambio=10, item="Oportunidad de Entrenamiento")
        self.historia["tim_facil_determinacion"] = tim_determinacion

        tim_respuesta_bruce = NodoHistoria(
            "tim_facil_respuesta_bruce",
            "LA DECISIÓN DEL MURCIÉLAGO",
            "Bruce guarda silencio por lo que parece una eternidad. Finalmente habla: 'Jason murió porque "
            "lo puse en peligro. No cometeré el mismo error.' Pero Alfred interviene: 'Con todo respeto, "
            "Maestro Bruce, quizás el error fue no prepararlo lo suficiente.' Bruce reflexiona y asiente.",
            "tim_decision_del_murcielago.png"
        )
        tim_respuesta_bruce.agregar_opcion("Agradecer la oportunidad", "tim_facil_entrenamiento", stat="reputacion", cambio=15, item="Oportunidad de Entrenamiento")
        self.historia["tim_facil_respuesta_bruce"] = tim_respuesta_bruce

        tim_oportunidad = NodoHistoria(
            "tim_facil_oportunidad",
            "LA PRUEBA FINAL",
            "'Dame una oportunidad para demostrar que puedo ser Robin,' pides. Bruce considera tu petición. "
            "'Hay un caso que no he podido resolver,' dice finalmente. 'Un nuevo criminal en Gotham. Si "
            "puedes ayudarme a atraparlo, consideraré entrenarte.'",
            "tim_prueba_final.png"
        )
        tim_oportunidad.agregar_opcion("Aceptar el desafío", "tim_facil_caso", stat="recursos", cambio=2)
        self.historia["tim_facil_oportunidad"] = tim_oportunidad

        tim_demostrar = NodoHistoria(
            "tim_facil_demostrar",
            "EL DESAFÍO DE BRUCE",
            "'¿Cómo puedo demostrarte que soy digno?' preguntas. Bruce considera: 'Hay un caso que no he "
            "podido resolver. Un nuevo criminal en Gotham. Demuéstrame que puedes pensar como yo.'",
            "tim_desafio_de_bruce.png"
        )
        tim_demostrar.agregar_opcion("Aceptar el desafío", "tim_facil_caso", stat="recursos", cambio=2)
        self.historia["tim_facil_demostrar"] = tim_demostrar

        tim_caso = NodoHistoria(
            "tim_facil_caso",
            "EL CASO SIN RESOLVER",
            "Bruce te da acceso a los archivos del caso. Un nuevo criminal ha estado robando tecnología "
            "avanzada. Pasas días analizando patrones, conectando pistas que parecían inconexas. Finalmente, "
            "identificas al culpable y su próximo objetivo. Bruce está genuinamente impresionado.",
            "tim_caso_sin_resolver.png"
        )
        tim_caso.agregar_opcion("Presentar tus hallazgos", "tim_facil_exito", stat="reputacion", cambio=25)
        self.historia["tim_facil_caso"] = tim_caso

        tim_enfoque_detective = NodoHistoria(
            "tim_facil_enfoque_detective",
            "EL ROBIN DETECTIVE",
            "Te enfocas en desarrollar tus habilidades detectivescas. Bruce nota tu talento natural: 'Tienes "
            "una mente analítica excepcional. Incluso mejor que la mía a tu edad.' Después de meses, dominas "
            "criminología, ciencia forense y tecnología avanzada. Eres diferente a los Robin anteriores.",
            "tim_robin_detective.png"
        )
        tim_enfoque_detective.agregar_opcion("Completar tu entrenamiento", "tim_facil_graduacion", stat="recursos", cambio=3, item="Habilidades Detectivescas")
        self.historia["tim_facil_enfoque_detective"] = tim_enfoque_detective

        tim_enfoque_combate = NodoHistoria(
            "tim_facil_enfoque_combate",
            "SUPERANDO LIMITACIONES",
            "Te esfuerzas al máximo en combate y acrobacias, áreas que no son tu fuerte natural. Bruce "
            "es un maestro exigente, pero reconoce tu determinación: 'Lo que te falta en talento natural, "
            "lo compensas con trabajo duro. Eso es más valioso.' Con el tiempo, te vuelves competente.",
            "tim_superando_limitaciones.png"
        )
        tim_enfoque_combate.agregar_opcion("Completar tu entrenamiento", "tim_facil_graduacion", stat="salud", cambio=20, item="Habilidades de Combate")
        self.historia["tim_facil_enfoque_combate"] = tim_enfoque_combate

        tim_exito = NodoHistoria(
            "tim_facil_exito",
            "LA CAPTURA",
            "Basándose en tu análisis, Batman atrapa al criminal. Tu teoría era correcta en cada detalle. "
            "De vuelta en la Batcueva, Bruce te mira con nuevo respeto: 'Impresionante trabajo, Tim. "
            "Quizás... quizás sí hay un lugar para ti aquí.'",
            "tim_captura_exitosa.png"
        )
        tim_exito.agregar_opcion("Agradecer la oportunidad", "tim_facil_entrenamiento", stat="reputacion", cambio=20, item="Oportunidad de Entrenamiento")
        self.historia["tim_facil_exito"] = tim_exito

        tim_graduacion = NodoHistoria(
            "tim_facil_graduacion",
            "EL NUEVO ROBIN",
            "Después de seis meses de entrenamiento intensivo, Bruce te llama a la Batcueva. Alfred está "
            "presente, sosteniendo una caja. 'Has demostrado tu valía,' dice Bruce. 'No eres Dick ni Jason. "
            "Eres Tim Drake. Y ahora...' Alfred abre la caja, revelando un traje de Robin rediseñado.",
            "tim_el_nuevo_robin.png"
        )
        tim_graduacion.agregar_opcion("Aceptar el manto de Robin", "tim_facil_aceptar_manto", stat="reputacion", cambio=25, item="Traje de Robin")
        self.historia["tim_facil_graduacion"] = tim_graduacion

        tim_aceptar_manto = NodoHistoria(
            "tim_facil_aceptar_manto",
            "EL TERCER ROBIN",
            "Te pones el traje de Robin, consciente del legado que representa. 'Este símbolo significa "
            "algo,' dice Bruce. 'Dick le dio esperanza. Jason, valentía. ¿Qué le darás tú?' Piensas un "
            "momento: 'Equilibrio,' respondes. Bruce asiente, satisfecho con tu respuesta.",
            "tim_el_tercer_robin.png"
        )
        tim_aceptar_manto.agregar_opcion("Salir a tu primera patrulla", "tim_facil_primera_patrulla", stat="salud", cambio=15)
        self.historia["tim_facil_aceptar_manto"] = tim_aceptar_manto

        tim_primera_patrulla = NodoHistoria(
            "tim_facil_primera_patrulla",
            "LA PRIMERA NOCHE",
            "Tu primera noche como Robin es surrealista. Saltas entre azoteas junto a Batman, observando "
            "Gotham desde una perspectiva completamente nueva. Tu comunicador crepita: hay un robo en "
            "progreso. Batman te mira: 'Es tu llamada, Robin. ¿Cómo procedemos?'",
            "tim_primera_noche.png"
        )
        tim_primera_patrulla.agregar_opcion("Sugerir un enfoque sigiloso", "tim_facil_enfoque_sigiloso", stat="recursos", cambio=2)
        tim_primera_patrulla.agregar_opcion("Proponer un plan estratégico", "tim_facil_plan_estrategico", stat="reputacion", cambio=15)
        self.historia["tim_facil_primera_patrulla"] = tim_primera_patrulla

        tim_enfoque_sigiloso = NodoHistoria(
            "tim_facil_enfoque_sigiloso",
            "SOMBRAS Y SILENCIO",
            "Sugieres infiltrarse silenciosamente. Batman asiente con aprobación. Juntos, se deslizan "
            "entre las sombras, neutralizando a los criminales uno por uno sin ser detectados. Tu "
            "enfoque metódico complementa perfectamente el estilo de Batman.",
            "tim_sombras_y_silencio.png"
        )
        tim_enfoque_sigiloso.agregar_opcion("Completar la misión", "tim_facil_exito_mision", stat="reputacion", cambio=15)
        self.historia["tim_facil_enfoque_sigiloso"] = tim_enfoque_sigiloso

        tim_plan_estrategico = NodoHistoria(
            "tim_facil_plan_estrategico",
            "LA MENTE ESTRATÉGICA",
            "Analizas rápidamente la situación y propones un plan detallado: 'Tú entras por el frente "
            "como distracción mientras yo desactivo su sistema de seguridad y neutralizo a los vigías.' "
            "Batman parece impresionado: 'Buen plan, Robin. Ejecutémoslo.'",
            "tim_mente_estrategica.png"
        )
        tim_plan_estrategico.agregar_opcion("Implementar el plan", "tim_facil_exito_mision", stat="reputacion", cambio=20)
        self.historia["tim_facil_plan_estrategico"] = tim_plan_estrategico

        tim_exito_mision = NodoHistoria(
            "tim_facil_exito_mision",
            "MISIÓN CUMPLIDA",
            "La misión es un éxito rotundo. Los criminales son capturados y las víctimas están a salvo. "
            "De vuelta en la azotea, Batman te mira con aprobación: 'Buen trabajo, Robin.' Por primera "
            "vez, notas que la oscuridad en Bruce parece haber retrocedido un poco. Tu teoría era correcta: "
            "Batman necesita un Robin.",
            "tim_mision_cumplida.png"
        )
        tim_exito_mision.agregar_opcion("Continuar como el tercer Robin", "tim_facil_final", stat="reputacion", cambio=25)
        self.historia["tim_facil_exito_mision"] = tim_exito_mision

        tim_facil_final = NodoHistoria(
            "tim_facil_final",
            "EL DETECTIVE MARAVILLA - FINAL",
            "Han pasado meses desde tu primera patrulla. Te has establecido como el tercer Robin, "
            "diferente a tus predecesores pero igualmente valioso. Tu mente analítica ha resuelto "
            "casos que desconcertaban incluso a Batman. Bruce te mira con orgullo en la Batcueva: "
            "'Tenías razón, Tim. Batman necesita un Robin. Y tú has demostrado ser exactamente el "
            "Robin que necesitaba.' Alfred sonríe, Dick te da un pulgar arriba durante su visita. "
            "Has encontrado tu lugar en esta extraña familia. Y tu historia... apenas comienza.",
            "tim_final_detective_maravilla.png"
        )
        tim_facil_final.es_final = True
        self.historia["tim_facil_final"] = tim_facil_final

        # MODO NORMAL: LOS JÓVENES TITANES Y LA TRAGEDIA FAMILIAR (35 nodos)
        tim_normal_inicio = NodoHistoria(
            "tim_normal_inicio",
            "EL LÍDER DE LOS TITANES",
            "Han pasado dos años desde que te convertiste en Robin. Ahora, a los 16 años, eres el líder "
            "de los Teen Titans, coordinando un equipo que incluye a Superboy, Wonder Girl, Kid Flash, "
            "e Impulse. Batman confía en tu capacidad estratégica, pero últimamente te sientes dividido: "
            "tus padres, Jack y Janet Drake, están planeando otra expedición arqueológica a Haití. "
            "Quieren que los acompañes, pero los Titans te necesitan para una misión crucial.",
            "tim_lider_titanes.png"
        )
        tim_normal_inicio.agregar_opcion("Priorizar la misión de los Titans", "tim_normal_mision_titans", stat="reputacion", cambio=10)
        tim_normal_inicio.agregar_opcion("Intentar acompañar a tus padres", "tim_normal_familia", stat="recursos", cambio=-2)
        tim_normal_inicio.agregar_opcion("Pedir a Batman consejo", "tim_normal_consejo_batman", stat="reputacion", cambio=5)
        self.historia["tim_normal_inicio"] = tim_normal_inicio

        tim_normal_mision_titans = NodoHistoria(
            "tim_normal_mision_titans",
            "DEBER ANTES QUE TODO",
            "Decides quedarte con los Titans. Tus padres están decepcionados pero comprenden. 'Siempre "
            "estás ocupado, Tim,' dice tu madre con tristeza. La misión es exitosa: neutralizas a H.I.V.E. "
            "y rescatas a varios rehenes. Superboy te felicita por tu liderazgo, pero no puedes quitarte "
            "la mirada decepcionada de tu madre de la cabeza.",
            "tim_deber_antes_que_todo.png"
        )
        tim_normal_mision_titans.agregar_opcion("Llamar a tus padres después", "tim_normal_llamada", stat="recursos", cambio=1)
        tim_normal_mision_titans.agregar_opcion("Concentrarte en la siguiente misión", "tim_normal_proxima_mision", stat="reputacion", cambio=10)
        self.historia["tim_normal_mision_titans"] = tim_normal_mision_titans

        tim_normal_familia = NodoHistoria(
            "tim_normal_familia",
            "ELECCIÓN FAMILIAR",
            "Decides acompañar a tus padres a Haití. Los Titans comprenden, Wonder Girl asume el liderazgo "
            "temporal. Durante el viaje, tus padres están felices de tenerte con ellos. 'Casi habíamos "
            "olvidado cómo es tener a nuestro hijo presente,' dice tu padre. Pero te llega un mensaje "
            "urgente: los Titans enfrentan una crisis sin ti.",
            "tim_eleccion_familiar.png"
        )
        tim_normal_familia.agregar_opcion("Quedarte con tus padres", "tim_normal_quedarse", stat="recursos", cambio=2)
        tim_normal_familia.agregar_opcion("Regresar de emergencia con los Titans", "tim_normal_regreso_urgente", stat="reputacion", cambio=15, stat2="recursos", cambio2=-3)
        self.historia["tim_normal_familia"] = tim_normal_familia

        tim_normal_consejo_batman = NodoHistoria(
            "tim_normal_consejo_batman",
            "LA SABIDURÍA DEL MENTOR",
            "Bruce te mira con una expresión que raramente muestra: conflicto. 'He sacrificado muchas "
            "relaciones personales por este trabajo, Tim. No cometas mis errores.' Alfred añade: 'La familia "
            "es importante, joven Tim. El trabajo de héroe estará siempre ahí.' Sus palabras te hacen reflexionar.",
            "tim_consejo_de_batman.png"
        )
        tim_normal_consejo_batman.agregar_opcion("Acompañar a tus padres", "tim_normal_familia", stat="recursos", cambio=2)
        tim_normal_consejo_batman.agregar_opcion("Quedarte pero mantener contacto cercano", "tim_normal_balance", stat="reputacion", cambio=5)
        self.historia["tim_normal_consejo_batman"] = tim_normal_consejo_batman

        tim_normal_llamada = NodoHistoria(
            "tim_normal_llamada",
            "CONEXIÓN DISTANTE",
            "Llamas a tus padres esa noche. Tu madre responde desde Haití, se escucha cansada pero emocionada "
            "por su trabajo. 'Te extrañamos, cariño. Ojalá estuvieras aquí.' Hablan por media hora sobre "
            "la expedición. Al colgar, sientes un nudo en el estómago. Algo no se siente bien.",
            "tim_conexion_distante.png"
        )
        tim_normal_llamada.agregar_opcion("Concentrarte en el trabajo de los Titans", "tim_normal_trabajo_titans", stat="reputacion", cambio=10)
        tim_normal_llamada.agregar_opcion("Investigar la expedición de tus padres", "tim_normal_investigacion_haiti", stat="recursos", cambio=2)
        self.historia["tim_normal_llamada"] = tim_normal_llamada

        tim_normal_proxima_mision = NodoHistoria(
            "tim_normal_proxima_mision",
            "EL LÍDER ENFOCADO",
            "Te sumerges en el trabajo con los Titans. Coordinan tres misiones simultáneas exitosamente. "
            "Kid Flash bromea: 'Eres como un mini-Batman con mejor personalidad.' Pero en medio de una "
            "reunión estratégica, recibes una llamada que paraliza tu mundo: tus padres han sido atacados en Haití.",
            "tim_lider_enfocado.png"
        )
        tim_normal_proxima_mision.agregar_opcion("Volar inmediatamente a Haití", "tim_normal_haiti_urgente", stat="recursos", cambio=-3)
        self.historia["tim_normal_proxima_mision"] = tim_normal_proxima_mision

        tim_normal_quedarse = NodoHistoria(
            "tim_normal_quedarse",
            "MOMENTO FAMILIAR",
            "Decides quedarte con tus padres. Es la primera vez en años que pasas tiempo real con ellos. "
            "Tu padre te muestra artefactos antiguos, tu madre te cuenta historias de civilizaciones perdidas. "
            "Por un momento, olvidas que eres Robin. Pero esa noche, la expedición es atacada por el Obeah Man.",
            "tim_momento_familiar.png"
        )
        tim_normal_quedarse.agregar_opcion("Defender a tus padres", "tim_normal_defensa", stat="salud", cambio=-15, stat2="reputacion", cambio2=20)
        self.historia["tim_normal_quedarse"] = tim_normal_quedarse

        tim_normal_regreso_urgente = NodoHistoria(
            "tim_normal_regreso_urgente",
            "EL HÉROE REGRESA",
            "Regresas de emergencia y ayudas a los Titans a resolver la crisis. La misión es un éxito, "
            "pero tus padres están heridos por tu partida repentina. Días después, recibes una llamada "
            "devastadora: tus padres fueron atacados en Haití. Tu madre está muerta. Tu padre en coma. "
            "Y tú no estabas allí.",
            "tim_heroe_regresa.png"
        )
        tim_normal_regreso_urgente.agregar_opcion("Volar a Haití inmediatamente", "tim_normal_llegada_tarde", stat="recursos", cambio=-3)
        self.historia["tim_normal_regreso_urgente"] = tim_normal_regreso_urgente

        tim_normal_balance = NodoHistoria(
            "tim_normal_balance",
            "INTENTANDO AMBOS MUNDOS",
            "Decides quedarte con los Titans pero mantienes llamadas diarias con tus padres. Durante dos "
            "semanas, parece funcionar. Pero una noche, no responden tu llamada habitual. Ni la siguiente. "
            "Algo está terriblemente mal. Batman te informa: hay reportes de un ataque a la expedición.",
            "tim_intentando_ambos_mundos.png"
        )
        tim_normal_balance.agregar_opcion("Volar a Haití de inmediato", "tim_normal_haiti_urgente", stat="recursos", cambio=-2)
        self.historia["tim_normal_balance"] = tim_normal_balance

        tim_normal_trabajo_titans = NodoHistoria(
            "tim_normal_trabajo_titans",
            "EL PESO DEL LIDERAZGO",
            "Los Titans enfrentan una semana intensa: tres misiones mayores consecutivas. Tu estrategia "
            "es impecable, pero estás exhausto. Superboy nota tu preocupación: '¿Todo bien, jefe?' "
            "Antes de que puedas responder, Batman te contacta con urgencia: tus padres están en peligro en Haití.",
            "tim_peso_del_liderazgo.png"
        )
        tim_normal_trabajo_titans.agregar_opcion("Partir inmediatamente", "tim_normal_haiti_urgente", stat="recursos", cambio=-2)
        self.historia["tim_normal_trabajo_titans"] = tim_normal_trabajo_titans

        tim_normal_investigacion_haiti = NodoHistoria(
            "tim_normal_investigacion_haiti",
            "INSTINTO DETECTIVE",
            "Usando tus habilidades detectivescas, investigas la expedición de tus padres. Descubres "
            "referencias al Obeah Man, un hechicero haitiano peligroso. Intentas advertirles, pero es "
            "demasiado tarde: la comunicación se corta. Batman confirma tus peores temores: han sido atacados.",
            "tim_instinto_detective.png"
        )
        tim_normal_investigacion_haiti.agregar_opcion("Volar a Haití para rescatarlos", "tim_normal_haiti_urgente", stat="recursos", cambio=-2)
        self.historia["tim_normal_investigacion_haiti"] = tim_normal_investigacion_haiti

        tim_normal_defensa = NodoHistoria(
            "tim_normal_defensa",
            "BATALLA DESESPERADA",
            "Como Robin, enfrentas al Obeah Man y sus secuaces. Logras defender a tus padres inicialmente, "
            "pero el hechicero es más poderoso de lo que esperabas. Tu madre es envenenada protegiéndote. "
            "Tu padre es herido gravemente. Logras ahuyentarlos, pero el daño está hecho. Tu madre muere "
            "en tus brazos, susurrando: 'Estoy orgullosa de ti, Tim.'",
            "tim_batalla_desesperada.png"
        )
        tim_normal_defensa.agregar_opcion("Llevar a tu padre al hospital", "tim_normal_hospital", stat="salud", cambio=-20, stat2="recursos", cambio2=-5)
        self.historia["tim_normal_defensa"] = tim_normal_defensa

        tim_normal_haiti_urgente = NodoHistoria(
            "tim_normal_haiti_urgente",
            "CARRERA CONTRA EL TIEMPO",
            "Usas recursos de Batman para volar a Haití inmediatamente. Superboy insiste en acompañarte. "
            "Al llegar al campamento, encuentran devastación. Tu madre yace sin vida, envenenada. Tu "
            "padre está gravemente herido, en estado crítico. El Obeah Man ya huyó. Llegaste demasiado tarde.",
            "tim_carrera_contra_tiempo.png"
        )
        tim_normal_haiti_urgente.agregar_opcion("Salvar a tu padre", "tim_normal_salvar_padre", stat="recursos", cambio=-3)
        tim_normal_haiti_urgente.agregar_opcion("Perseguir al Obeah Man", "tim_normal_venganza", stat="salud", cambio=-15)
        self.historia["tim_normal_haiti_urgente"] = tim_normal_haiti_urgente

        tim_normal_llegada_tarde = NodoHistoria(
            "tim_normal_llegada_tarde",
            "LA CULPA DEL AUSENTE",
            "Llegas a Haití para encontrar la escena del crimen. Tu madre está muerta. Tu padre en coma. "
            "Las autoridades locales te informan que el ataque fue hace dos días. Si hubieras venido con "
            "ellos, si hubieras estado allí... Superboy te pone una mano en el hombro: 'No es tu culpa, hermano.'",
            "tim_culpa_del_ausente.png"
        )
        tim_normal_llegada_tarde.agregar_opcion("Transportar a tu padre a Gotham", "tim_normal_gotham", stat="recursos", cambio=-3)
        self.historia["tim_normal_llegada_tarde"] = tim_normal_llegada_tarde

        tim_normal_hospital = NodoHistoria(
            "tim_normal_hospital",
            "VIGILIA EN EL HOSPITAL",
            "Tu padre, Jack Drake, está en coma en el hospital de Gotham. Los médicos dicen que sus "
            "posibilidades son inciertas. Pasas días en la sala de espera, dividido entre tu vigilia "
            "y tus responsabilidades como Robin. Batman te ofrece tiempo libre, pero tú insistes en trabajar.",
            "tim_vigilia_hospital.png"
        )
        tim_normal_hospital.agregar_opcion("Tomar tiempo para estar con tu padre", "tim_normal_tiempo_padre", stat="reputacion", cambio=-5, stat2="recursos", cambio2=2)
        tim_normal_hospital.agregar_opcion("Canalizar tu dolor en el trabajo", "tim_normal_trabajo_dolor", stat="salud", cambio=-10, stat2="reputacion", cambio2=15)
        self.historia["tim_normal_hospital"] = tim_normal_hospital

        tim_normal_salvar_padre = NodoHistoria(
            "tim_normal_salvar_padre",
            "PRIORIDAD ABSOLUTA",
            "Ignoras al Obeah Man y te enfocas en estabilizar a tu padre. Con ayuda de Superboy, lo "
            "transportan a Gotham. Los médicos logran salvarle la vida, pero queda en coma. Te quedas "
            "en el hospital, sosteniendo su mano, sintiendo el peso de haber perdido a tu madre y casi "
            "perder a tu padre también.",
            "tim_prioridad_absoluta.png"
        )
        tim_normal_salvar_padre.agregar_opcion("Esperar su recuperación", "tim_normal_vigilia", stat="recursos", cambio=2)
        self.historia["tim_normal_salvar_padre"] = tim_normal_salvar_padre

        tim_normal_venganza = NodoHistoria(
            "tim_normal_venganza",
            "LA TENTACIÓN OSCURA",
            "Furioso, persigues al Obeah Man. Superboy intenta detenerte: '¡Tim, tu padre necesita ayuda médica!'  "
            "Pero la rabia te consume. Encuentras al hechicero y lo enfrentas. Casi lo matas antes de que "
            "Superboy te detenga físicamente. 'Esto no eres tú,' te dice. Tienes razón. Regresas con tu padre.",
            "tim_tentacion_oscura.png"
        )
        tim_normal_venganza.agregar_opcion("Llevar a tu padre a Gotham", "tim_normal_gotham", stat="salud", cambio=-20, stat2="recursos", cambio2=-3)
        self.historia["tim_normal_venganza"] = tim_normal_venganza

        tim_normal_gotham = NodoHistoria(
            "tim_normal_gotham",
            "DE REGRESO EN GOTHAM",
            "Tu padre es trasladado a un hospital en Gotham. Bruce Wayne paga todos los gastos médicos. "
            "Alfred te prepara té mientras esperas noticias. Los médicos informan que Jack sobrevivirá, "
            "pero quedará temporalmente paralizado. Necesitará terapia física intensiva. Y tú acabas de perder a tu madre.",
            "tim_regreso_a_gotham.png"
        )
        tim_normal_gotham.agregar_opcion("Retirarte temporalmente como Robin", "tim_normal_retiro_temporal", stat="reputacion", cambio=-10)
        tim_normal_gotham.agregar_opcion("Continuar como Robin para honrar a tu madre", "tim_normal_honrar_madre", stat="salud", cambio=-10, stat2="reputacion", cambio2=15)
        self.historia["tim_normal_gotham"] = tim_normal_gotham

        tim_normal_tiempo_padre = NodoHistoria(
            "tim_normal_tiempo_padre",
            "PRIORIDAD FAMILIAR",
            "Decides tomar un descanso de los Titans para estar con tu padre. Wonder Girl asume el "
            "liderazgo temporal. Pasas semanas en el hospital, hablándole a tu padre inconsciente, "
            "contándole sobre tu vida como Robin. Una noche, milagrosamente, abre los ojos. 'Tim...,' susurra.",
            "tim_prioridad_familiar.png"
        )
        tim_normal_tiempo_padre.agregar_opcion("Estar presente durante su recuperación", "tim_normal_recuperacion", stat="recursos", cambio=3)
        self.historia["tim_normal_tiempo_padre"] = tim_normal_tiempo_padre

        tim_normal_trabajo_dolor = NodoHistoria(
            "tim_normal_trabajo_dolor",
            "EL ESCAPE DEL HÉROE",
            "Te lanzas de lleno al trabajo como Robin y líder de los Titans. Cada noche patrullas, cada "
            "día coordinas misiones. Tus compañeros están preocupados. 'No has dormido en tres días,' "
            "dice Wonder Girl. Batman te confronta: 'Esto no es saludable, Tim.' Pero no puedes parar: "
            "si paras, tendrás que sentir el dolor.",
            "tim_escape_del_heroe.png"
        )
        tim_normal_trabajo_dolor.agregar_opcion("Escuchar a Batman y tomar un descanso", "tim_normal_descanso", stat="salud", cambio=10)
        tim_normal_trabajo_dolor.agregar_opcion("Continuar trabajando hasta el agotamiento", "tim_normal_agotamiento", stat="salud", cambio=-25, stat2="reputacion", cambio2=10)
        self.historia["tim_normal_trabajo_dolor"] = tim_normal_trabajo_dolor

        tim_normal_vigilia = NodoHistoria(
            "tim_normal_vigilia",
            "SEMANAS DE ESPERA",
            "Semanas pasan en el hospital. Los Titans te visitan regularmente. Cassie (Wonder Girl) te "
            "trae comida. Conner (Superboy) intenta hacerte reír. Bart (Impulse) te cuenta historias para "
            "distraerte. Una tarde, los dedos de tu padre se mueven. Está despertando.",
            "tim_semanas_de_espera.png"
        )
        tim_normal_vigilia.agregar_opcion("Estar allí cuando despierte", "tim_normal_despertar", stat="recursos", cambio=3)
        self.historia["tim_normal_vigilia"] = tim_normal_vigilia

        tim_normal_retiro_temporal = NodoHistoria(
            "tim_normal_retiro_temporal",
            "PAUSA NECESARIA",
            "Le dices a Batman que necesitas tiempo. Él comprende. 'Toma todo el tiempo que necesites. "
            "La familia es lo primero.' Te retiras temporalmente como Robin. Durante semanas, solo eres "
            "Tim Drake, cuidando a tu padre en recuperación. Pero Gotham te llama, y eventualmente, "
            "tu padre despierta del coma.",
            "tim_pausa_necesaria.png"
        )
        tim_normal_retiro_temporal.agregar_opcion("Estar presente para su recuperación", "tim_normal_recuperacion", stat="recursos", cambio=2)
        self.historia["tim_normal_retiro_temporal"] = tim_normal_retiro_temporal

        tim_normal_honrar_madre = NodoHistoria(
            "tim_normal_honrar_madre",
            "LEGADO DE JANET DRAKE",
            "Decides continuar como Robin para honrar la memoria de tu madre. Ella siempre estuvo orgullosa "
            "de tu heroísmo, aunque nunca lo expresó abiertamente. Usas tu dolor como motivación, no para "
            "venganza, sino para ser mejor héroe. Batman nota tu fortaleza: 'Tu madre estaría orgullosa.'",
            "tim_legado_janet_drake.png"
        )
        tim_normal_honrar_madre.agregar_opcion("Continuar tu trabajo con los Titans", "tim_normal_liderazgo_renovado", stat="reputacion", cambio=20)
        self.historia["tim_normal_honrar_madre"] = tim_normal_honrar_madre

        tim_normal_recuperacion = NodoHistoria(
            "tim_normal_recuperacion",
            "EL LARGO CAMINO",
            "Tu padre despierta, pero la noticia de la muerte de tu madre lo devasta. Queda temporalmente "
            "paralizado de la cintura para abajo. Inicia terapia física intensiva. Su terapeuta, Dana Winters, "
            "es paciente y comprensiva. Con el tiempo, tu padre comienza a caminar de nuevo. Y tú estás "
            "allí en cada paso.",
            "tim_largo_camino_recuperacion.png"
        )
        tim_normal_recuperacion.agregar_opcion("Ser un hijo presente", "tim_normal_hijo_presente", stat="recursos", cambio=3)
        self.historia["tim_normal_recuperacion"] = tim_normal_recuperacion

        tim_normal_descanso = NodoHistoria(
            "tim_normal_descanso",
            "PROCESANDO EL DOLOR",
            "Finalmente te permites sentir. Es devastador. Lloras por primera vez desde el ataque. Alfred "
            "está allí, ofreciendo té y silencio comprensivo. Bruce comparte su propia experiencia con la "
            "pérdida. Lentamente, comienzas a sanar. Y cuando tu padre despierta, estás emocionalmente "
            "preparado para estar presente.",
            "tim_procesando_el_dolor.png"
        )
        tim_normal_descanso.agregar_opcion("Apoyar a tu padre", "tim_normal_despertar", stat="salud", cambio=15)
        self.historia["tim_normal_descanso"] = tim_normal_descanso

        tim_normal_agotamiento = NodoHistoria(
            "tim_normal_agotamiento",
            "EL PUNTO DE QUIEBRE",
            "Te trabajas hasta el colapso. Durante una misión, tu agotamiento casi causa una tragedia. "
            "Superboy tiene que salvarte. Batman te quita el traje: 'Suficiente. Vas a tomar un descanso "
            "aunque tenga que encerrarte en la Mansión Wayne.' Estás demasiado cansado para protestar. "
            "Alfred te lleva al hospital: tu padre acaba de despertar.",
            "tim_punto_de_quiebre.png"
        )
        tim_normal_agotamiento.agregar_opcion("Recuperarte y estar con tu padre", "tim_normal_despertar", stat="salud", cambio=10)
        self.historia["tim_normal_agotamiento"] = tim_normal_agotamiento

        tim_normal_despertar = NodoHistoria(
            "tim_normal_despertar",
            "EL DESPERTAR",
            "Tu padre despierta del coma. Sus primeras palabras: '¿Janet?' Tu silencio le dice todo. Llora "
            "en tu presencia, un hombre destrozado. Durante semanas, trabajas con él en terapia física. "
            "Se enamora de su terapeuta, Dana Winters. Lentamente, comienza a sanar. Pero la pregunta "
            "persiste en tu mente: ¿debiste haber estado allí?",
            "tim_el_despertar.png"
        )
        tim_normal_despertar.agregar_opcion("Cargar con la culpa silenciosamente", "tim_normal_culpa_silenciosa", stat="salud", cambio=-10)
        tim_normal_despertar.agregar_opcion("Hablar con tu padre sobre tus sentimientos", "tim_normal_honestidad", stat="recursos", cambio=2)
        self.historia["tim_normal_despertar"] = tim_normal_despertar

        tim_normal_liderazgo_renovado = NodoHistoria(
            "tim_normal_liderazgo_renovado",
            "LÍDER FORTALECIDO",
            "Regresas a los Titans con nueva determinación. Tu experiencia con la pérdida te hace un "
            "líder más empático y cuidadoso. Ya no solo piensas en la estrategia, sino en la seguridad "
            "emocional de tu equipo. Wonder Girl nota el cambio: 'Has madurado, Tim.' Tu padre también "
            "despierta durante este tiempo.",
            "tim_lider_fortalecido.png"
        )
        tim_normal_liderazgo_renovado.agregar_opcion("Equilibrar ser Robin y ser hijo", "tim_normal_equilibrio", stat="reputacion", cambio=15)
        self.historia["tim_normal_liderazgo_renovado"] = tim_normal_liderazgo_renovado

        tim_normal_hijo_presente = NodoHistoria(
            "tim_normal_hijo_presente",
            "RECONSTRUYENDO LA FAMILIA",
            "Por primera vez, eres un hijo verdaderamente presente. Asistes a cada sesión de terapia de "
            "tu padre. Lo ayudas en casa. Conoces a Dana Winters, quien se vuelve importante en sus vidas. "
            "Con el tiempo, tu padre te confiesa: 'Sé que has estado ocupado con algo, Tim. Algún día, "
            "quiero que me cuentes qué es.'",
            "tim_reconstruyendo_familia.png"
        )
        tim_normal_hijo_presente.agregar_opcion("Mantener tu secreto", "tim_normal_secreto", stat="recursos", cambio=2)
        tim_normal_hijo_presente.agregar_opcion("Considerar revelar tu identidad", "tim_normal_consideracion_revelacion", stat="recursos", cambio=1)
        self.historia["tim_normal_hijo_presente"] = tim_normal_hijo_presente

        tim_normal_culpa_silenciosa = NodoHistoria(
            "tim_normal_culpa_silenciosa",
            "EL PESO INVISIBLE",
            "Cargas con la culpa en silencio. '¿Y si hubiera estado allí?' es una pregunta que te atormenta. "
            "Tu padre nota tu distancia emocional pero no pregunta. Meses después, durante una conversación "
            "con Batman, él te dice: 'La culpa del sobreviviente es real. Créeme, lo sé. Pero tu madre no "
            "querría que te tortures.'",
            "tim_peso_invisible.png"
        )
        tim_normal_culpa_silenciosa.agregar_opcion("Buscar terapia para procesar", "tim_normal_terapia", stat="salud", cambio=15)
        tim_normal_culpa_silenciosa.agregar_opcion("Canalizar la culpa en ser mejor héroe", "tim_normal_mejor_heroe", stat="reputacion", cambio=15)
        self.historia["tim_normal_culpa_silenciosa"] = tim_normal_culpa_silenciosa

        tim_normal_honestidad = NodoHistoria(
            "tim_normal_honestidad",
            "CONVERSACIÓN SINCERA",
            "Una noche, te sinceras con tu padre sobre tu culpa. 'Debí haber estado allí.' Tu padre te "
            "toma la mano: 'Tim, tu madre murió porque un criminal la atacó, no porque tú no estuvieras. "
            "Ella siempre estuvo orgullosa de ti, de la persona que eres.' Sus palabras comienzan a sanar "
            "algo roto dentro de ti.",
            "tim_conversacion_sincera.png"
        )
        tim_normal_honestidad.agregar_opcion("Aceptar su perdón", "tim_normal_sanacion", stat="salud", cambio=20)
        self.historia["tim_normal_honestidad"] = tim_normal_honestidad

        tim_normal_equilibrio = NodoHistoria(
            "tim_normal_equilibrio",
            "EL ACTO DE EQUILIBRIO",
            "Intentas equilibrar ambas vidas: líder de los Titans y hijo presente. Es agotador pero "
            "gratificante. Tu padre comienza a caminar de nuevo. Se casa con Dana. Y un día, mientras "
            "organizas fotos familiares, encuentras una nota de tu madre: 'Estoy orgullosa del hombre "
            "en que te estás convirtiendo, Tim.'",
            "tim_acto_de_equilibrio.png"
        )
        tim_normal_equilibrio.agregar_opcion("Continuar equilibrando ambas vidas", "tim_normal_vida_doble", stat="recursos", cambio=3)
        self.historia["tim_normal_equilibrio"] = tim_normal_equilibrio

        tim_normal_secreto = NodoHistoria(
            "tim_normal_secreto",
            "LA DOBLE VIDA CONTINÚA",
            "Decides mantener tu identidad secreta. Es más seguro para tu padre, especialmente después "
            "de lo que pasó con tu madre. Pero vivir esta doble vida se vuelve más difícil. Tu padre "
            "nota tus ausencias, tus moretones inexplicables. Una noche, te sigue y descubre la verdad.",
            "tim_doble_vida_continua.png"
        )
        tim_normal_secreto.agregar_opcion("Enfrentar el descubrimiento", "tim_normal_descubrimiento", stat="recursos", cambio=-2)
        self.historia["tim_normal_secreto"] = tim_normal_secreto

        tim_normal_consideracion_revelacion = NodoHistoria(
            "tim_normal_consideracion_revelacion",
            "PENSANDO EN LA VERDAD",
            "Consideras contarle a tu padre la verdad. Batman te advierte: 'Conocer tu identidad lo pondría "
            "en peligro.' Pero Alfred disiente: 'O podría darle paz mental, Maestro Bruce. El señor Drake "
            "ya perdió a su esposa. Merece honestidad de su hijo.' La decisión es tuya.",
            "tim_pensando_en_la_verdad.png"
        )
        tim_normal_consideracion_revelacion.agregar_opcion("Revelar tu identidad", "tim_normal_revelacion", stat="recursos", cambio=-2)
        tim_normal_consideracion_revelacion.agregar_opcion("Mantener el secreto por ahora", "tim_normal_secreto", stat="recursos", cambio=1)
        self.historia["tim_normal_consideracion_revelacion"] = tim_normal_consideracion_revelacion

        tim_normal_terapia = NodoHistoria(
            "tim_normal_terapia",
            "SANACIÓN PROFESIONAL",
            "Aceptas terapia. Es difícil hablar sobre la culpa, sobre la pérdida, sobre la doble vida. "
            "Pero ayuda. Lentamente, comienzas a perdonarte. Tu terapeuta te dice: 'No puedes salvar a "
            "todos, Tim. Ni siquiera Batman puede. Pero puedes honrar la memoria de tu madre siendo la "
            "mejor versión de ti mismo.'",
            "tim_sanacion_profesional.png"
        )
        tim_normal_terapia.agregar_opcion("Continuar tu camino de sanación", "tim_normal_sanacion", stat="salud", cambio=20)
        self.historia["tim_normal_terapia"] = tim_normal_terapia

        tim_normal_mejor_heroe = NodoHistoria(
            "tim_normal_mejor_heroe",
            "EXCELENCIA NACIDA DEL DOLOR",
            "Canalizas tu culpa en ser el mejor Robin posible. Entrenas más duro, estudias más, planificas "
            "mejor. Los Titans notan tu intensidad. Batman te advierte sobre el agotamiento, pero tú insistes: "
            "'Tengo que ser mejor. Para honrarla.' Con el tiempo, te conviertes en uno de los mejores "
            "estrategas que los Titans han tenido.",
            "tim_excelencia_nacida_del_dolor.png"
        )
        tim_normal_mejor_heroe.agregar_opcion("Encontrar balance eventualmente", "tim_normal_balance_encontrado", stat="reputacion", cambio=20)
        self.historia["tim_normal_mejor_heroe"] = tim_normal_mejor_heroe

        tim_normal_sanacion = NodoHistoria(
            "tim_normal_sanacion",
            "EL CAMINO DE LA SANACIÓN",
            "Con tiempo, terapia y apoyo de tu familia (tanto la de sangre como la Bat-Familia), comienzas "
            "a sanar. La culpa no desaparece completamente, pero aprendes a vivir con ella. Tu padre se "
            "recupera casi completamente. Se casa con Dana. Y tú sigues siendo Robin, pero uno más sabio "
            "y compasivo.",
            "tim_camino_de_sanacion.png"
        )
        tim_normal_sanacion.agregar_opcion("Regresar completamente a los Titans", "tim_normal_regreso_titans", stat="reputacion", cambio=20)
        self.historia["tim_normal_sanacion"] = tim_normal_sanacion

        tim_normal_vida_doble = NodoHistoria(
            "tim_normal_vida_doble",
            "MALABARISMO CONSTANTE",
            "Meses pasan equilibrando ambas vidas. Tu padre se casa con Dana en una ceremonia pequeña. "
            "Eres su padrino. Los Titans te necesitan cada vez más. Batman confía más en ti. Pero la "
            "tensión crece: tu padre nota que algo está pasando. Una noche, encuentra una de tus noticias "
            "sobre Robin en tu habitación.",
            "tim_malabarismo_constante.png"
        )
        tim_normal_vida_doble.agregar_opcion("Admitir la verdad antes que la descubra", "tim_normal_revelacion", stat="recursos", cambio=-1)
        tim_normal_vida_doble.agregar_opcion("Esperar y ver qué hace", "tim_normal_descubrimiento", stat="recursos", cambio=-2)
        self.historia["tim_normal_vida_doble"] = tim_normal_vida_doble

        tim_normal_descubrimiento = NodoHistoria(
            "tim_normal_descubrimiento",
            "EL SECRETO REVELADO",
            "Tu padre te confronta con evidencia: fotos tuyas como Robin, horarios que coinciden. 'Eres "
            "Robin,' dice, no como pregunta sino como declaración. Su expresión es de horror y traición. "
            "'¿Cuánto tiempo? ¿Sabía tu madre?' La conversación que sigue es una de las más difíciles de tu vida.",
            "tim_secreto_revelado.png"
        )
        tim_normal_descubrimiento.agregar_opcion("Explicar todo honestamente", "tim_normal_explicacion", stat="recursos", cambio=2)
        self.historia["tim_normal_descubrimiento"] = tim_normal_descubrimiento

        tim_normal_revelacion = NodoHistoria(
            "tim_normal_revelacion",
            "LA VERDAD VOLUNTARIA",
            "Decides contarle a tu padre la verdad. Lo llevas a un lugar privado y le revelas: 'Papá, "
            "soy Robin.' Su rostro pasa por shock, incredulidad, miedo. 'Casi te pierdo cuando perdí a "
            "tu madre. Y ahora me dices que te pones en peligro cada noche?' Está furioso y asustado.",
            "tim_verdad_voluntaria.png"
        )
        tim_normal_revelacion.agregar_opcion("Defender tu elección", "tim_normal_defensa_eleccion", stat="reputacion", cambio=10)
        tim_normal_revelacion.agregar_opcion("Prometer consideración retirarte", "tim_normal_promesa", stat="recursos", cambio=-2)
        self.historia["tim_normal_revelacion"] = tim_normal_revelacion

        tim_normal_balance_encontrado = NodoHistoria(
            "tim_normal_balance_encontrado",
            "EQUILIBRIO INTERNO",
            "Eventualmente encuentras un balance saludable. Tu intensidad se modera sin perder tu efectividad. "
            "Superboy comenta: 'Es bueno tenerte de vuelta, hermano. El viejo tú nos estaba preocupando.' "
            "Tu padre también nota el cambio positivo en ti. Pero un evento catastrófico se aproxima.",
            "tim_equilibrio_interno.png"
        )
        tim_normal_balance_encontrado.agregar_opcion("Continuar como Robin equilibrado", "tim_normal_crisis_aproxima", stat="salud", cambio=10)
        self.historia["tim_normal_balance_encontrado"] = tim_normal_balance_encontrado

        tim_normal_regreso_titans = NodoHistoria(
            "tim_normal_regreso_titans",
            "EL LÍDER REGRESA",
            "Regresas a tiempo completo con los Titans. Tu experiencia con la pérdida te hace un líder "
            "más completo. Ya no eres solo el estratega; eres el corazón del equipo. Wonder Girl te cede "
            "formalmente el liderazgo de nuevo: 'Nunca dejaste de ser nuestro líder, Tim.' Pero nuevas "
            "amenazas se acercan.",
            "tim_lider_regresa.png"
        )
        tim_normal_regreso_titans.agregar_opcion("Enfrentar nuevos desafíos", "tim_normal_crisis_aproxima", stat="reputacion", cambio=15)
        self.historia["tim_normal_regreso_titans"] = tim_normal_regreso_titans

        tim_normal_explicacion = NodoHistoria(
            "tim_normal_explicacion",
            "LA CONVERSACIÓN DIFÍCIL",
            "Le explicas todo a tu padre: cómo descubriste la identidad de Batman, cómo insististe en "
            "convertirte en Robin, por qué lo haces. 'Batman necesitaba un Robin, papá. Para mantener su "
            "humanidad. Y yo... yo necesito hacer el bien.' Tu padre escucha, procesando. Finalmente dice: "
            "'Ya perdí a tu madre. No puedo perderte a ti también.'",
            "tim_conversacion_dificil.png"
        )
        tim_normal_explicacion.agregar_opcion("Prometer ser más cuidadoso", "tim_normal_promesa_cuidado", stat="recursos", cambio=2)
        tim_normal_explicacion.agregar_opcion("Negarte a dejar de ser Robin", "tim_normal_negativa", stat="recursos", cambio=-3)
        self.historia["tim_normal_explicacion"] = tim_normal_explicacion

        tim_normal_defensa_eleccion = NodoHistoria(
            "tim_normal_defensa_eleccion",
            "DEFENDIENDO EL LEGADO",
            "'No puedo dejar de ser Robin, papá,' dices firmemente. 'Sé que es peligroso. Pero salvo vidas. "
            "Hago la diferencia.' Tu padre te mira con lágrimas: '¿Y qué hay de mi vida? ¿De tenerte en ella?' "
            "Es un argumento válido que no tiene respuesta fácil.",
            "tim_defendiendo_el_legado.png"
        )
        tim_normal_defensa_eleccion.agregar_opcion("Buscar un compromiso", "tim_normal_compromiso", stat="recursos", cambio=1)
        self.historia["tim_normal_defensa_eleccion"] = tim_normal_defensa_eleccion

        tim_normal_promesa = NodoHistoria(
            "tim_normal_promesa",
            "LA PROMESA DIFÍCIL",
            "Para tranquilizar a tu padre, prometes considerar retirarte. Es una mentira piadosa; sabes "
            "que no puedes dejar de ser Robin. Durante semanas, mantienes la apariencia de normalidad, "
            "pero sigues patrullando en secreto. Tu padre eventualmente descubre la mentira. La confianza "
            "entre ustedes se fractura.",
            "tim_promesa_dificil.png"
        )
        tim_normal_promesa.agregar_opcion("Admitir la mentira y pedir perdón", "tim_normal_disculpa", stat="recursos", cambio=-2)
        self.historia["tim_normal_promesa"] = tim_normal_promesa

        tim_normal_crisis_aproxima = NodoHistoria(
            "tim_normal_crisis_aproxima",
            "CALMA ANTES DE LA TORMENTA",
            "Por un tiempo, todo parece estable. Eres líder efectivo de los Titans. Tu padre está recuperado "
            "y feliz con Dana. Has procesado la muerte de tu madre. Pero en Gotham, algo oscuro se mueve. "
            "Batman te contacta con una advertencia: hay contratos de asesinato contra varias personas "
            "relacionadas con la comunidad de héroes. Incluido tu padre.",
            "tim_calma_antes_tormenta.png"
        )
        tim_normal_crisis_aproxima.agregar_opcion("Proteger a tu padre inmediatamente", "tim_normal_proteccion", stat="recursos", cambio=-2)
        tim_normal_crisis_aproxima.agregar_opcion("Investigar la amenaza primero", "tim_normal_investigacion_amenaza", stat="recursos", cambio=2)
        self.historia["tim_normal_crisis_aproxima"] = tim_normal_crisis_aproxima

        tim_normal_promesa_cuidado = NodoHistoria(
            "tim_normal_promesa_cuidado",
            "COMPROMISO Y CUIDADO",
            "'Te prometo que seré más cuidadoso, papá,' dices sinceramente. 'Trabajaré con Batman para "
            "minimizar riesgos. Pero no puedo dejar de hacer esto.' Tu padre suspira, resignado: 'Al menos "
            "dime que tienes un buen seguro de vida.' Es su forma de aceptar tu elección, aunque le duela.",
            "tim_compromiso_y_cuidado.png"
        )
        tim_normal_promesa_cuidado.agregar_opcion("Mantener a tu padre informado", "tim_normal_transparencia", stat="recursos", cambio=3)
        self.historia["tim_normal_promesa_cuidado"] = tim_normal_promesa_cuidado

        tim_normal_negativa = NodoHistoria(
            "tim_normal_negativa",
            "LA RUPTURA",
            "Te niegas rotundamente a dejar de ser Robin. Tu padre, desesperado, te da un ultimátum: "
            "'O dejas de ser Robin, o te vas de esta casa.' Es el peor tipo de conflicto. Batman te ofrece "
            "quedarte en la Mansión Wayne. Alfred prepara una habitación. La relación con tu padre está "
            "severamente dañada.",
            "tim_la_ruptura.png"
        )
        tim_normal_negativa.agregar_opcion("Mudarte con Bruce temporalmente", "tim_normal_mudanza", stat="recursos", cambio=-3)
        self.historia["tim_normal_negativa"] = tim_normal_negativa

        tim_normal_compromiso = NodoHistoria(
            "tim_normal_compromiso",
            "ENCONTRANDO TERRENO COMÚN",
            "Propones un compromiso: 'Seré más cuidadoso. Te mantendré informado cuando pueda. Y prometo "
            "que si alguna vez es demasiado, lo reconsideraré.' Tu padre lo piensa. Dana interviene: 'Jack, "
            "él está tratando de encontrar un punto medio.' Finalmente, tu padre acepta, aunque con reservas.",
            "tim_encontrando_terreno_comun.png"
        )
        tim_normal_compromiso.agregar_opcion("Honrar el compromiso", "tim_normal_honor_compromiso", stat="recursos", cambio=3)
        self.historia["tim_normal_compromiso"] = tim_normal_compromiso

        tim_normal_disculpa = NodoHistoria(
            "tim_normal_disculpa",
            "PIDIENDO PERDÓN",
            "Admites que mentiste: 'Lo siento, papá. No debí mentirte. Es solo que... no puedo dejar de "
            "ser Robin. Es parte de quién soy.' Tu padre está herido pero eventualmente suspira: 'Al menos "
            "sé honesto conmigo, Tim. Incluso si no me gusta lo que haces, merezco la verdad.' Lentamente, "
            "reconstruyen la confianza.",
            "tim_pidiendo_perdon.png"
        )
        tim_normal_disculpa.agregar_opcion("Ser honesto de ahora en adelante", "tim_normal_transparencia", stat="recursos", cambio=2)
        self.historia["tim_normal_disculpa"] = tim_normal_disculpa

        tim_normal_proteccion = NodoHistoria(
            "tim_normal_proteccion",
            "GUARDIÁN VIGILANTE",
            "Inmediatamente, colocas a tu padre y Dana bajo protección. Batman asigna seguridad. Tu padre "
            "está confundido: '¿Qué está pasando, Tim?' Le explicas sobre la amenaza. Si conoce tu identidad, "
            "entiende. Si no, inventa una historia creíble. Pero la amenaza es real: el Capitán Boomerang "
            "está en camino.",
            "tim_guardian_vigilante.png"
        )
        tim_normal_proteccion.agregar_opcion("Quedarte con tu padre personalmente", "tim_normal_guardia_personal", stat="salud", cambio=-10)
        tim_normal_proteccion.agregar_opcion("Confiar en la seguridad de Batman", "tim_normal_confianza_seguridad", stat="recursos", cambio=1)
        self.historia["tim_normal_proteccion"] = tim_normal_proteccion

        tim_normal_investigacion_amenaza = NodoHistoria(
            "tim_normal_investigacion_amenaza",
            "EL DETECTIVE INVESTIGA",
            "Decides investigar primero. Usando tus habilidades detectivescas, rastreas el origen de los "
            "contratos. Descubres que el Capitán Boomerang ha sido contratado para eliminar a familiares "
            "de héroes. Tu padre está en la lista. Tienes horas, quizás minutos. Vuelas hacia tu casa.",
            "tim_detective_investiga_amenaza.png"
        )
        tim_normal_investigacion_amenaza.agregar_opcion("Llegar antes que Boomerang", "tim_normal_carrera", stat="recursos", cambio=-2)
        self.historia["tim_normal_investigacion_amenaza"] = tim_normal_investigacion_amenaza

        tim_normal_transparencia = NodoHistoria(
            "tim_normal_transparencia",
            "HONESTIDAD RENOVADA",
            "Mantienes a tu padre informado (dentro de lo razonable) sobre tu trabajo como Robin. No cada "
            "detalle, pero lo suficiente para que sepa que estás bien. Esta transparencia fortalece su "
            "relación. Tu padre incluso bromea: 'Al menos ahora sé por qué llegas tarde a cenar.' Pero "
            "una noche, llegas a casa y encuentras algo terrible.",
            "tim_honestidad_renovada.png"
        )
        tim_normal_transparencia.agregar_opcion("Enfrentar la escena", "tim_normal_tragedia", stat="salud", cambio=-25)
        self.historia["tim_normal_transparencia"] = tim_normal_transparencia

        tim_normal_mudanza = NodoHistoria(
            "tim_normal_mudanza",
            "VIVIENDO EN LA MANSIÓN WAYNE",
            "Te mudas temporalmente a la Mansión Wayne. Alfred te trata como a otro hijo. Bruce es comprensivo "
            "pero te anima a reconciliarte con tu padre. 'La familia es importante, Tim. Incluso cuando no "
            "están de acuerdo.' Semanas después, tu padre te llama. Antes de que puedas contestar, Batman "
            "intercepta: hay una amenaza contra tu padre.",
            "tim_viviendo_en_mansion_wayne.png"
        )
        tim_normal_mudanza.agregar_opcion("Ir a proteger a tu padre", "tim_normal_reconciliacion_forzada", stat="recursos", cambio=-2)
        self.historia["tim_normal_mudanza"] = tim_normal_mudanza

        tim_normal_honor_compromiso = NodoHistoria(
            "tim_normal_honor_compromiso",
            "MANTENIENDO LA PALABRA",
            "Honras tu compromiso. Eres más cuidadoso en patrullas, informas a tu padre cuando puedes. "
            "La relación mejora significativamente. Dana te agradece por esforzarte. Tu padre admite: 'No "
            "me gusta, pero respeto que estés tratando.' Pero la paz no dura: una noche, una amenaza real "
            "llega a tu puerta.",
            "tim_manteniendo_la_palabra.png"
        )
        tim_normal_honor_compromiso.agregar_opcion("Enfrentar la amenaza", "tim_normal_tragedia", stat="salud", cambio=-20)
        self.historia["tim_normal_honor_compromiso"] = tim_normal_honor_compromiso

        tim_normal_guardia_personal = NodoHistoria(
            "tim_normal_guardia_personal",
            "EL GUARDIÁN",
            "Te quedas en casa, vigilando personalmente. Tu padre nota tu tensión. Esa noche, el Capitán "
            "Boomerang ataca. Pero estás preparado. Como Robin, lo interceptas antes de que pueda alcanzar "
            "a tu padre. La batalla es feroz. Boomerang es más peligroso de lo que esperabas, pero logras "
            "neutralizarlo. Tu padre está a salvo... esta vez.",
            "tim_el_guardian.png"
        )
        tim_normal_guardia_personal.agregar_opcion("Explicar a tu padre qué pasó", "tim_normal_explicacion_ataque", stat="reputacion", cambio=10)
        self.historia["tim_normal_guardia_personal"] = tim_normal_guardia_personal

        tim_normal_confianza_seguridad = NodoHistoria(
            "tim_normal_confianza_seguridad",
            "FE EN EL SISTEMA",
            "Confías en la seguridad que Batman instaló. Te quedas patrullando Gotham, coordinando con "
            "otros héroes para proteger múltiples objetivos. Pero esa noche, recibes un llamado de emergencia: "
            "la seguridad en tu casa fue violada. El Capitán Boomerang pasó las defensas. Vuelas hacia "
            "allí, pero sabes que podrías llegar tarde.",
            "tim_fe_en_el_sistema.png"
        )
        tim_normal_confianza_seguridad.agregar_opcion("Volar a máxima velocidad", "tim_normal_velocidad_maxima", stat="salud", cambio=-15)
        self.historia["tim_normal_confianza_seguridad"] = tim_normal_confianza_seguridad

        tim_normal_carrera = NodoHistoria(
            "tim_normal_carrera",
            "CONTRA RELOJ",
            "Vuelas hacia tu casa a máxima velocidad. Llegas justo cuando el Capitán Boomerang está "
            "acercándose. Tu padre aún no sabe del peligro. Tienes segundos para decidir: ¿interceptar "
            "a Boomerang afuera o proteger a tu padre adentro?",
            "tim_contra_reloj.png"
        )
        tim_normal_carrera.agregar_opcion("Interceptar a Boomerang afuera", "tim_normal_intercepcion", stat="salud", cambio=-10)
        tim_normal_carrera.agregar_opcion("Proteger a tu padre adentro", "tim_normal_escudo_humano", stat="salud", cambio=-20)
        self.historia["tim_normal_carrera"] = tim_normal_carrera

        tim_normal_tragedia = NodoHistoria(
            "tim_normal_tragedia",
            "LA NOCHE MÁS OSCURA",
            "Llegas a casa para encontrar la puerta abierta. Tu corazón se hunde. Adentro, encuentras "
            "señales de lucha. Tu padre está en el suelo, gravemente herido. Dana llama a emergencias. "
            "El Capitán Boomerang también está muerto: tu padre, con un arma que alguien le envió misteriosamente, "
            "logró defenderse. Pero las heridas de tu padre son mortales.",
            "tim_noche_mas_oscura.png"
        )
        tim_normal_tragedia.agregar_opcion("Estar con tu padre en sus últimos momentos", "tim_normal_despedida", stat="salud", cambio=-30)
        self.historia["tim_normal_tragedia"] = tim_normal_tragedia

        tim_normal_reconciliacion_forzada = NodoHistoria(
            "tim_normal_reconciliacion_forzada",
            "REUNIÓN DE EMERGENCIA",
            "Llegas a la casa de tu padre justo a tiempo. El Capitán Boomerang está a punto de atacar. "
            "Como Robin, lo interceptas. La batalla es brutal. Tu padre ve todo: su hijo como Robin, "
            "luchando por salvarlo. Logras derrotar a Boomerang. Tu padre te mira, procesando todo: "
            "'Realmente eres Robin. Realmente arriesgas tu vida así cada noche.'",
            "tim_reunion_de_emergencia.png"
        )
        tim_normal_reconciliacion_forzada.agregar_opcion("Hablar con tu padre después", "tim_normal_reconciliacion", stat="reputacion", cambio=15)
        self.historia["tim_normal_reconciliacion_forzada"] = tim_normal_reconciliacion_forzada

# CONTINUACIÓN MODO NORMAL - PARTE 2

        tim_normal_explicacion_ataque = NodoHistoria(
            "tim_normal_explicacion_ataque",
            "LA VERDAD AL DESCUBIERTO",
            "Si tu padre no conocía tu identidad, ahora lo sabe. Si ya lo sabía, esto solidifica su "
            "comprensión de los peligros reales. 'Casi te pierdo peleando por mí,' dice con lágrimas. "
            "'Pero también veo por qué lo haces. Salvaste mi vida, Tim.' Es el comienzo de una nueva "
            "comprensión entre ustedes.",
            "tim_verdad_al_descubierto.png"
        )
        tim_normal_explicacion_ataque.agregar_opcion("Reconstruir la relación", "tim_normal_nueva_relacion", stat="recursos", cambio=3)
        self.historia["tim_normal_explicacion_ataque"] = tim_normal_explicacion_ataque

        tim_normal_velocidad_maxima = NodoHistoria(
            "tim_normal_velocidad_maxima",
            "DEMASIADO TARDE",
            "Llegas lo más rápido posible, pero no es suficiente. Encuentras a tu padre en el suelo, "
            "mortalmente herido. El Capitán Boomerang también está muerto: tu padre logró defenderse "
            "con un arma que le fue enviada misteriosamente. Pero el precio fue alto. Dana está en shock. "
            "Tu padre te ve llegar como Robin y susurra: 'Tim... sabía que eras especial.'",
            "tim_demasiado_tarde.png"
        )
        tim_normal_velocidad_maxima.agregar_opcion("Sostener a tu padre", "tim_normal_despedida", stat="salud", cambio=-30)
        self.historia["tim_normal_velocidad_maxima"] = tim_normal_velocidad_maxima

        tim_normal_intercepcion = NodoHistoria(
            "tim_normal_intercepcion",
            "BATALLA EN LA CALLE",
            "Interceptas al Capitán Boomerang afuera antes de que pueda entrar. La batalla es feroz. "
            "Boomerang es un asesino experimentado, pero tú peleas con la desesperación de proteger a "
            "tu familia. Logras derrotarlo, pero mientras tanto, recibes un mensaje: había un segundo "
            "asesino. Tu padre está herido.",
            "tim_batalla_en_la_calle.png"
        )
        tim_normal_intercepcion.agregar_opcion("Correr adentro", "tim_normal_dentro_casa", stat="salud", cambio=-15)
        self.historia["tim_normal_intercepcion"] = tim_normal_intercepcion

        tim_normal_escudo_humano = NodoHistoria(
            "tim_normal_escudo_humano",
            "PROTECCIÓN FINAL",
            "Entras y te posicionas entre el Capitán Boomerang y tu padre. Cuando Boomerang lanza sus "
            "boomerangs letales, tú los interceptas con tu cuerpo, salvando a tu padre. Estás gravemente "
            "herido, pero Boomerang huye al darse cuenta de que Batman viene en camino. Tu padre te sostiene: "
            "'No, Tim. No tú también.'",
            "tim_proteccion_final.png"
        )
        tim_normal_escudo_humano.agregar_opcion("Recuperarte en el hospital", "tim_normal_hospital_tim", stat="salud", cambio=-25)
        self.historia["tim_normal_escudo_humano"] = tim_normal_escudo_humano

        tim_normal_despedida = NodoHistoria(
            "tim_normal_despedida",
            "ADIÓS A JACK DRAKE",
            "Sostienes a tu padre mientras esperas la ambulancia. Sabes que no llegará a tiempo. 'Lo siento, "
            "papá. Lo siento mucho.' Él toca tu rostro: 'No lo sientas. Estoy orgulloso de ti, Tim. De "
            "lo que eres, de lo que haces. Cuida de Dana. Y sigue siendo el héroe que eres.' Son sus "
            "últimas palabras. Jack Drake muere en tus brazos.",
            "tim_adios_a_jack_drake.png"
        )
        tim_normal_despedida.agregar_opcion("Procesar la pérdida", "tim_normal_duelo_doble", stat="salud", cambio=-35)
        self.historia["tim_normal_despedida"] = tim_normal_despedida

        tim_normal_reconciliacion = NodoHistoria(
            "tim_normal_reconciliacion",
            "ENTENDIMIENTO MUTUO",
            "Después del ataque, tú y tu padre tienen la conversación más honesta de sus vidas. Él entiende "
            "ahora lo que significa ser Robin, los riesgos reales. 'No me gusta,' admite. 'Pero veo que "
            "es parte de quién eres. Y acabas de salvar mi vida.' La relación se fortalece de manera "
            "que no creías posible.",
            "tim_entendimiento_mutuo.png"
        )
        tim_normal_reconciliacion.agregar_opcion("Continuar como Robin con su bendición", "tim_normal_bendicion", stat="reputacion", cambio=20)
        self.historia["tim_normal_reconciliacion"] = tim_normal_reconciliacion

        tim_normal_nueva_relacion = NodoHistoria(
            "tim_normal_nueva_relacion",
            "FAMILIA REDEFINIDA",
            "Tu relación con tu padre entra en una nueva fase. Él acepta tu vida como Robin, aunque le "
            "preocupa. Te hace prometer que serás cuidadoso. Dana se convierte en tu aliada, ayudando a "
            "cubrir tus ausencias. Por primera vez, sientes que tienes una verdadera familia que te apoya "
            "completamente en ambos aspectos de tu vida.",
            "tim_familia_redefinida.png"
        )
        tim_normal_nueva_relacion.agregar_opcion("Disfrutar de esta paz", "tim_normal_paz_temporal", stat="recursos", cambio=3)
        self.historia["tim_normal_nueva_relacion"] = tim_normal_nueva_relacion

        tim_normal_dentro_casa = NodoHistoria(
            "tim_normal_dentro_casa",
            "LLEGANDO ADENTRO",
            "Corres adentro para encontrar a tu padre herido pero vivo. Dana ha llamado a emergencias. "
            "El segundo asesino huyó cuando escuchó la batalla afuera. Tu padre está consciente: 'Tim... "
            "¿eres Robin?' No puedes mentir más. Asientes. Él sonríe débilmente: 'Siempre lo supe en el "
            "fondo. Mi hijo, el héroe.'",
            "tim_llegando_adentro.png"
        )
        tim_normal_dentro_casa.agregar_opcion("Llevarlo al hospital", "tim_normal_recuperacion_padre", stat="recursos", cambio=2)
        self.historia["tim_normal_dentro_casa"] = tim_normal_dentro_casa

        tim_normal_hospital_tim = NodoHistoria(
            "tim_normal_hospital_tim",
            "EL HÉROE HERIDO",
            "Despiertas en el hospital. Tu padre está a tu lado, ileso gracias a tu sacrificio. 'Casi "
            "te pierdo,' dice con lágrimas. 'Igual que perdí a tu madre. No puedo... no puedo pasar por "
            "eso otra vez.' Pero ve tu determinación y suspira: 'Pero tampoco puedo pedirte que dejes de "
            "ser quien eres.'",
            "tim_heroe_herido.png"
        )
        tim_normal_hospital_tim.agregar_opcion("Prometer ser más cuidadoso", "tim_normal_promesa_renovada", stat="salud", cambio=15)
        self.historia["tim_normal_hospital_tim"] = tim_normal_hospital_tim

        tim_normal_duelo_doble = NodoHistoria(
            "tim_normal_duelo_doble",
            "HUÉRFANO",
            "En menos de un año, has perdido a ambos padres. La culpa te consume: '¿Por qué no estuve "
            "allí? ¿Por qué no pude salvarlos?' Batman te encuentra en la Batcueva, destrozado. 'Sé lo "
            "que sientes, Tim. Créeme, lo sé.' Te ofrece quedarte en la Mansión Wayne. Alfred te prepara "
            "tu antigua habitación. Eres, en todo menos el nombre, huérfano.",
            "tim_huerfano.png"
        )
        tim_normal_duelo_doble.agregar_opcion("Aceptar el apoyo de la Bat-Familia", "tim_normal_bat_familia", stat="recursos", cambio=2)
        tim_normal_duelo_doble.agregar_opcion("Aislarte en tu dolor", "tim_normal_aislamiento", stat="salud", cambio=-20)
        self.historia["tim_normal_duelo_doble"] = tim_normal_duelo_doble

        tim_normal_bendicion = NodoHistoria(
            "tim_normal_bendicion",
            "LA BENDICIÓN PATERNA",
            "Tu padre te da su bendición para continuar como Robin. 'Solo prométeme que serás cuidadoso. "
            "Y que vendrás a cenar los domingos.' Es un acuerdo perfecto. Por primera vez, no tienes que "
            "esconder quién eres de tu familia. Dana incluso aprende primeros auxilios básicos 'por si acaso'. "
            "La vida parece perfecta... hasta que no lo es.",
            "tim_bendicion_paterna.png"
        )
        tim_normal_bendicion.agregar_opcion("Disfrutar del equilibrio", "tim_normal_equilibrio_perfecto", stat="reputacion", cambio=20)
        self.historia["tim_normal_bendicion"] = tim_normal_bendicion

        tim_normal_paz_temporal = NodoHistoria(
            "tim_normal_paz_temporal",
            "MOMENTO DE FELICIDAD",
            "Disfrutas de meses de paz relativa. Tu padre apoya tu trabajo como Robin. Los Titans están "
            "en su mejor momento. Batman confía plenamente en ti. Incluso encuentras tiempo para ser un "
            "adolescente normal ocasionalmente. Pero en Gotham, la paz nunca dura. Una noche, todo cambia.",
            "tim_momento_de_felicidad.png"
        )
        tim_normal_paz_temporal.agregar_opcion("Enfrentar la nueva crisis", "tim_normal_crisis_final", stat="reputacion", cambio=10)
        self.historia["tim_normal_paz_temporal"] = tim_normal_paz_temporal

        tim_normal_recuperacion_padre = NodoHistoria(
            "tim_normal_recuperacion_padre",
            "SANACIÓN MUTUA",
            "Tu padre se recupera de sus heridas. La experiencia los acerca como nunca. Él ahora entiende "
            "verdaderamente lo que significa ser Robin. 'Cada noche que sales, voy a preocuparme,' admite. "
            "'Pero también sé que estás haciendo el bien. Solo... ten cuidado.' Es todo lo que puedes "
            "pedir de un padre.",
            "tim_sanacion_mutua.png"
        )
        tim_normal_recuperacion_padre.agregar_opcion("Fortalecer el vínculo familiar", "tim_normal_vinculo_fuerte", stat="recursos", cambio=3)
        self.historia["tim_normal_recuperacion_padre"] = tim_normal_recuperacion_padre

        tim_normal_promesa_renovada = NodoHistoria(
            "tim_normal_promesa_renovada",
            "NUEVA PROMESA",
            "'Seré más cuidadoso, papá. Lo prometo.' Y esta vez, es una promesa que intentas mantener. "
            "Eres más estratégico, menos temerario. Tu padre aprecia el esfuerzo. La relación se fortalece "
            "a través de esta experiencia cercana a la muerte. Pero en el fondo, ambos saben que el peligro "
            "nunca realmente desaparece.",
            "tim_nueva_promesa.png"
        )
        tim_normal_promesa_renovada.agregar_opcion("Vivir con el peligro constante", "tim_normal_vida_peligrosa", stat="reputacion", cambio=10)
        self.historia["tim_normal_promesa_renovada"] = tim_normal_promesa_renovada

        tim_normal_bat_familia = NodoHistoria(
            "tim_normal_bat_familia",
            "ACOGIDO POR LOS WAYNE",
            "La Bat-Familia se convierte en tu familia principal. Bruce es un padre figura, aunque nunca "
            "reemplazará a Jack. Alfred es tu confidente. Dick te visita regularmente. Incluso Barbara "
            "Gordon te ofrece apoyo. Dana también se queda en tu vida, manteniendo viva la memoria de tu "
            "padre. Lentamente, muy lentamente, comienzas a sanar.",
            "tim_acogido_por_los_wayne.png"
        )
        tim_normal_bat_familia.agregar_opcion("Canalizar el dolor en ser mejor Robin", "tim_normal_robin_mejorado", stat="reputacion", cambio=25)
        self.historia["tim_normal_bat_familia"] = tim_normal_bat_familia

        tim_normal_aislamiento = NodoHistoria(
            "tim_normal_aislamiento",
            "EN LA OSCURIDAD",
            "Te aíslas de todos, incluso de la Bat-Familia. Los Titans están preocupados. Batman intenta "
            "alcanzarte, pero lo rechazas. El dolor te consume. Una noche, en una patrulla especialmente "
            "peligrosa, casi te matan por descuido. Superboy te encuentra y te lleva de vuelta a la Torre. "
            "'No puedes hacer esto solo, hermano,' te dice.",
            "tim_en_la_oscuridad.png"
        )
        tim_normal_aislamiento.agregar_opcion("Finalmente aceptar ayuda", "tim_normal_aceptar_ayuda", stat="salud", cambio=10)
        self.historia["tim_normal_aislamiento"] = tim_normal_aislamiento

        tim_normal_equilibrio_perfecto = NodoHistoria(
            "tim_normal_equilibrio_perfecto",
            "EL BALANCE IDEAL",
            "Por meses, logras el equilibrio perfecto entre ser Robin y ser hijo. Tu padre asiste a algunas "
            "de tus graduaciones en la Torre Titans (con identidad secreta protegida). Cenas los domingos "
            "en familia. Batman comenta: 'Lo estás manejando mejor que yo nunca lo hice.' Pero la felicidad "
            "atrae la tragedia en Gotham.",
            "tim_balance_ideal.png"
        )
        tim_normal_equilibrio_perfecto.agregar_opcion("Prepararte para lo inevitable", "tim_normal_preparacion", stat="reputacion", cambio=15)
        self.historia["tim_normal_equilibrio_perfecto"] = tim_normal_equilibrio_perfecto

        tim_normal_crisis_final = NodoHistoria(
            "tim_normal_crisis_final",
            "LA CRISIS DE IDENTIDAD",
            "Una nueva ola de crímenes golpea Gotham. Contratos de asesinato contra familias de héroes. "
            "Tu padre está en la lista. Batman implementa protección, pero hay demasiados objetivos. Debes "
            "elegir: ¿coordinar la defensa de todos como líder estratégico, o proteger personalmente a tu padre?",
            "tim_crisis_de_identidad.png"
        )
        tim_normal_crisis_final.agregar_opcion("Proteger a tu padre personalmente", "tim_normal_eleccion_padre", stat="recursos", cambio=-2)
        tim_normal_crisis_final.agregar_opcion("Coordinar la defensa general", "tim_normal_eleccion_heroe", stat="reputacion", cambio=15)
        self.historia["tim_normal_crisis_final"] = tim_normal_crisis_final

        tim_normal_vinculo_fuerte = NodoHistoria(
            "tim_normal_vinculo_fuerte",
            "LAZO INQUEBRANTABLE",
            "Tu vínculo con tu padre se fortalece de maneras inesperadas. Él te ayuda con casos desde "
            "una perspectiva civil. Dana se convierte en tu aliada. Por primera vez, sientes que tu vida "
            "doble no es una carga sino algo que tu familia apoya activamente. Es casi perfecto. Pero "
            "Gotham no permite la perfección por mucho tiempo.",
            "tim_lazo_inquebrantable.png"
        )
        tim_normal_vinculo_fuerte.agregar_opcion("Disfrutar mientras dure", "tim_normal_felicidad_breve", stat="recursos", cambio=3)
        self.historia["tim_normal_vinculo_fuerte"] = tim_normal_vinculo_fuerte

        tim_normal_vida_peligrosa = NodoHistoria(
            "tim_normal_vida_peligrosa",
            "PELIGRO CONSTANTE",
            "Aprendes a vivir con el peligro constante. Tu padre también. Es la realidad de amar a un "
            "héroe. Pero cada noche que regresas sano, él respira aliviado. Cada cena dominical es una "
            "celebración silenciosa de que ambos siguen vivos. Es una existencia tensa pero llena de amor. "
            "Hasta que una noche, el peligro se materializa.",
            "tim_peligro_constante.png"
        )
        tim_normal_vida_peligrosa.agregar_opcion("Enfrentar el peligro final", "tim_normal_confrontacion_final", stat="salud", cambio=-15)
        self.historia["tim_normal_vida_peligrosa"] = tim_normal_vida_peligrosa

        tim_normal_robin_mejorado = NodoHistoria(
            "tim_normal_robin_mejorado",
            "FORJADO EN TRAGEDIA",
            "Canalizas tu dolor en ser el mejor Robin posible. No por venganza, sino por honor a tus padres. "
            "Te conviertes en un estratega aún más brillante. Batman dice que eres el mejor Robin desde "
            "Dick Grayson, quizás incluso mejor en algunos aspectos. Los Titans te siguen sin cuestionar. "
            "Has convertido tu tragedia en fortaleza.",
            "tim_forjado_en_tragedia.png"
        )
        tim_normal_robin_mejorado.agregar_opcion("Liderar a los Titans al futuro", "tim_normal_final_heroe", stat="reputacion", cambio=30)
        self.historia["tim_normal_robin_mejorado"] = tim_normal_robin_mejorado

        tim_normal_aceptar_ayuda = NodoHistoria(
            "tim_normal_aceptar_ayuda",
            "ABRIENDO LAS PUERTAS",
            "Finalmente aceptas la ayuda de tus amigos y familia. Superboy te abraza: 'Sobre tiempo, hermano.' "
            "Wonder Girl organiza una sesión grupal improvisada. Batman comparte su propia experiencia con "
            "la pérdida. Alfred hace té. Lentamente, la oscuridad retrocede. No desaparece, pero se vuelve "
            "manejable.",
            "tim_abriendo_las_puertas.png"
        )
        tim_normal_aceptar_ayuda.agregar_opcion("Comenzar el proceso de sanación", "tim_normal_sanacion_real", stat="salud", cambio=20)
        self.historia["tim_normal_aceptar_ayuda"] = tim_normal_aceptar_ayuda

        tim_normal_preparacion = NodoHistoria(
            "tim_normal_preparacion",
            "PREPARÁNDOSE PARA LO PEOR",
            "Sabes que la felicidad en Gotham es temporal. Preparas planes de contingencia para proteger "
            "a tu padre. Batman aprueba tu precaución. Instalas sistemas de seguridad avanzados. Entrenas "
            "a tu padre en defensa básica. Pero cuando la amenaza real llega, descubres que ninguna cantidad "
            "de preparación es suficiente contra el destino.",
            "tim_preparandose_para_lo_peor.png"
        )
        tim_normal_preparacion.agregar_opcion("Enfrentar la amenaza", "tim_normal_amenaza_real", stat="recursos", cambio=2)
        self.historia["tim_normal_preparacion"] = tim_normal_preparacion

        tim_normal_eleccion_padre = NodoHistoria(
            "tim_normal_eleccion_padre",
            "LA ELECCIÓN DEL HIJO",
            "Eliges proteger a tu padre personalmente. Los otros objetivos tendrán que arreglárselas con "
            "la seguridad estándar. Te quedas en tu casa, vigilante. Esa noche, el Capitán Boomerang ataca. "
            "Pero estás preparado. Lo derrotas antes de que pueda hacerle daño a tu padre. Más tarde, "
            "Batman te informa: otros no tuvieron tanta suerte esa noche.",
            "tim_eleccion_del_hijo.png"
        )
        tim_normal_eleccion_padre.agregar_opcion("Lidiar con la culpa del sobreviviente", "tim_normal_culpa_heroe", stat="salud", cambio=-15)
        self.historia["tim_normal_eleccion_padre"] = tim_normal_eleccion_padre

        tim_normal_eleccion_heroe = NodoHistoria(
            "tim_normal_eleccion_heroe",
            "LA ELECCIÓN DEL HÉROE",
            "Eliges coordinar la defensa general. Es lo que un verdadero héroe haría, dice Batman. Coordinas "
            "equipos de protección para docenas de objetivos. Salvas muchas vidas esa noche. Pero no puedes "
            "estar en todas partes. Cuando todo termina, recibes una llamada de Dana: tu padre fue atacado. "
            "Sobrevivió, pero apenas.",
            "tim_eleccion_del_heroe.png"
        )
        tim_normal_eleccion_heroe.agregar_opcion("Ir con tu padre", "tim_normal_hospital_padre", stat="recursos", cambio=-2)
        self.historia["tim_normal_eleccion_heroe"] = tim_normal_eleccion_heroe

        tim_normal_felicidad_breve = NodoHistoria(
            "tim_normal_felicidad_breve",
            "MOMENTOS ROBADOS",
            "Disfrutas cada momento con tu padre, sabiendo que en Gotham, nada bueno dura para siempre. "
            "Cenas familiares, conversaciones nocturnas, bromas compartidas. Son meses preciosos. Tu padre "
            "te dice: 'Eres mi orgullo, Tim. Tanto como Robin como mi hijo.' Dos semanas después, llega "
            "la amenaza que has temido.",
            "tim_momentos_robados.png"
        )
        tim_normal_felicidad_breve.agregar_opcion("Enfrentar lo inevitable", "tim_normal_inevitable", stat="salud", cambio=-20)
        self.historia["tim_normal_felicidad_breve"] = tim_normal_felicidad_breve

        tim_normal_confrontacion_final = NodoHistoria(
            "tim_normal_confrontacion_final",
            "LA NOCHE DEL JUICIO",
            "El Capitán Boomerang llega a tu casa. Pero esta vez estás preparado. La batalla es feroz. "
            "Proteges a tu padre con todo lo que tienes. En el momento crítico, tu padre usa el arma de "
            "defensa que le diste, disparando a Boomerang. El asesino cae, pero no antes de lanzar un último "
            "boomerang. Tu elección: ¿proteger a tu padre o esquivar?",
            "tim_noche_del_juicio.png"
        )
        tim_normal_confrontacion_final.agregar_opcion("Proteger a tu padre", "tim_normal_sacrificio", stat="salud", cambio=-30)
        tim_normal_confrontacion_final.agregar_opcion("Confiar en el chaleco de tu padre", "tim_normal_confianza", stat="recursos", cambio=2)
        self.historia["tim_normal_confrontacion_final"] = tim_normal_confrontacion_final

        tim_normal_final_heroe = NodoHistoria(
            "tim_normal_final_heroe",
            "EL LÍDER FORJADO EN PÉRDIDA - FINAL",
            "Años después, eres reconocido como uno de los mejores líderes que los Teen Titans han tenido. "
            "Has perdido a ambos padres, pero sus lecciones viven en ti. Tu madre te enseñó curiosidad "
            "y valentía. Tu padre, al final, te enseñó que es posible aceptar a alguien completamente, "
            "incluso cuando no entiendes sus elecciones. Eres Tim Drake, Robin, líder, detective, héroe. "
            "Y aunque la pérdida ha marcado tu vida, también te ha hecho más fuerte, más sabio, más empático. "
            "Batman te mira con orgullo: 'Tus padres estarían orgullosos.' Y sabes que tiene razón.",
            "tim_final_lider_forjado_en_perdida.png"
        )
        tim_normal_final_heroe.es_final = True
        self.historia["tim_normal_final_heroe"] = tim_normal_final_heroe

        tim_normal_sanacion_real = NodoHistoria(
            "tim_normal_sanacion_real",
            "EL CAMINO HACIA LA LUZ",
            "Con apoyo, comienzas a sanar verdaderamente. No olvidas a tus padres; aprended a vivir con "
            "su memoria de manera saludable. Los honras siendo el mejor héroe que puedes ser, pero también "
            "permitiéndote ser humano, ser vulnerable. Los Titans se convierten en tu familia elegida. "
            "Y lentamente, encuentras paz.",
            "tim_camino_hacia_la_luz.png"
        )
        tim_normal_sanacion_real.agregar_opcion("Continuar como Robin sanado", "tim_normal_final_equilibrado", stat="salud", cambio=20)
        self.historia["tim_normal_sanacion_real"] = tim_normal_sanacion_real

        tim_normal_amenaza_real = NodoHistoria(
            "tim_normal_amenaza_real",
            "CUANDO LA PREPARACIÓN NO BASTA",
            "A pesar de toda tu preparación, la amenaza es más compleja de lo esperado. Múltiples asesinos "
            "atacan simultáneamente. Logras salvar a tu padre, pero el costo es alto: estás gravemente "
            "herido. Tu padre te sostiene: 'Valió la pena, Tim. Valió la pena tenerte como hijo.' Sobrevives, "
            "pero las cicatrices (físicas y emocionales) permanecen.",
            "tim_cuando_preparacion_no_basta.png"
        )
        tim_normal_amenaza_real.agregar_opcion("Recuperarte y continuar", "tim_normal_cicatrices", stat="salud", cambio=10)
        self.historia["tim_normal_amenaza_real"] = tim_normal_amenaza_real

        tim_normal_culpa_heroe = NodoHistoria(
            "tim_normal_culpa_heroe",
            "EL PRECIO DEL HEROÍSMO",
            "Salvaste a tu padre, pero otros murieron esa noche. La culpa te persigue: '¿Debí haber "
            "coordinado la defensa general?' Batman te dice: 'Salvaste a tu padre. Esa fue tu elección. "
            "No puedes salvarlos a todos.' Pero las palabras no alivian completamente el peso. Vives con "
            "esta decisión, sabiendo que elegiste familia sobre deber.",
            "tim_precio_del_heroismo.png"
        )
        tim_normal_culpa_heroe.agregar_opcion("Aceptar tu elección", "tim_normal_aceptacion_eleccion", stat="recursos", cambio=2)
        self.historia["tim_normal_culpa_heroe"] = tim_normal_culpa_heroe

        tim_normal_hospital_padre = NodoHistoria(
            "tim_normal_hospital_padre",
            "EN EL HOSPITAL OTRA VEZ",
            "Tu padre está en el hospital, estable pero traumatizado. Te mira: 'Hiciste lo correcto, Tim. "
            "Salvaste a muchos esta noche.' Pero ambos saben que casi lo pierdes. La conversación que sigue "
            "es dolorosa pero necesaria: sobre el costo del heroísmo, sobre familia, sobre elecciones imposibles.",
            "tim_en_el_hospital_otra_vez.png"
        )
        tim_normal_hospital_padre.agregar_opcion("Tener la conversación difícil", "tim_normal_conversacion_dificil", stat="recursos", cambio=2)
        self.historia["tim_normal_hospital_padre"] = tim_normal_hospital_padre

        tim_normal_inevitable = NodoHistoria(
            "tim_normal_inevitable",
            "LO QUE SIEMPRE SUPISTE",
            "La amenaza llega como sabías que llegaría. El Capitán Boomerang, cumpliendo un contrato. Haces "
            "todo lo que puedes, luchas con todo lo que tienes. Y esta vez... esta vez es suficiente. Derrotas "
            "a Boomerang. Tu padre está a salvo. Ambos sobreviven. Pero la experiencia los cambia para siempre.",
            "tim_lo_que_siempre_supiste.png"
        )
        tim_normal_inevitable.agregar_opcion("Lidiar con el trauma compartido", "tim_normal_trauma", stat="salud", cambio=-10)
        self.historia["tim_normal_inevitable"] = tim_normal_inevitable

        tim_normal_sacrificio = NodoHistoria(
            "tim_normal_sacrificio",
            "EL ÚLTIMO ESCUDO",
            "Te interpones entre el boomerang y tu padre. El impacto es devastador. Caes, gravemente herido. "
            "Tu padre grita, Boomerang está muerto por su disparo. Batman llega momentos después. Sobrevives "
            "por poco. Meses de recuperación te esperan. Pero tu padre está vivo. Y al final, eso es lo único "
            "que importa.",
            "tim_ultimo_escudo.png"
        )
        tim_normal_sacrificio.agregar_opcion("Recuperarte junto a tu padre", "tim_normal_final_sacrificio", stat="salud", cambio=15)
        self.historia["tim_normal_sacrificio"] = tim_normal_sacrificio

        tim_normal_confianza = NodoHistoria(
            "tim_normal_confianza",
            "FE EN LA PREPARACIÓN",
            "Confías en el chaleco antibalas que le diste a tu padre. Esquivas el boomerang. Tu padre recibe "
            "el impacto pero el chaleco lo protege. Boomerang muere por el disparo de tu padre. Han sobrevivido "
            "juntos, como equipo. Tu padre te abraza: 'Lo logramos, hijo. Juntos.' Es un momento de validación: "
            "tu preparación funcionó.",
            "tim_fe_en_la_preparacion.png"
        )
        tim_normal_confianza.agregar_opcion("Celebrar la supervivencia", "tim_normal_final_supervivencia", stat="reputacion", cambio=20)
        self.historia["tim_normal_confianza"] = tim_normal_confianza

        tim_normal_final_equilibrado = NodoHistoria(
            "tim_normal_final_equilibrado",
            "EQUILIBRIO ENCONTRADO - FINAL",
            "Después de años de lucha, dolor y crecimiento, encuentras un verdadero equilibrio. Has perdido "
            "a tus padres, pero su legado vive en ti. Janet te dio curiosidad intelectual. Jack te dio "
            "aceptación y comprensión. Eres líder de los Teen Titans, socio de confianza de Batman, y sobre "
            "todo, eres Tim Drake. Ya no el niño que descubrió el secreto de Batman, sino un héroe por derecho "
            "propio. Las cicatrices de la pérdida te han hecho más empático, más sabio. Wonder Girl dice: "
            "'Eres el mejor líder que hemos tenido.' Batman añade: 'Eres más que mi socio, Tim. Eres familia.' "
            "Y finalmente, lo crees.",
            "tim_final_equilibrio_encontrado.png"
        )
        tim_normal_final_equilibrado.es_final = True
        self.historia["tim_normal_final_equilibrado"] = tim_normal_final_equilibrado

        tim_normal_cicatrices = NodoHistoria(
            "tim_normal_cicatrices",
            "MARCADO PERO NO ROTO",
            "Las cicatrices físicas sanan con tiempo. Las emocionales toman más. Pero tu padre está vivo, "
            "y eso hace que valga la pena. Tu relación se profundiza a través del trauma compartido. Él "
            "entiende ahora, visceralmente, lo que significa ser Robin. 'Cada cicatriz es una historia de "
            "salvación,' te dice. Y tiene razón.",
            "tim_marcado_pero_no_roto.png"
        )
        tim_normal_cicatrices.agregar_opcion("Continuar con las cicatrices como recordatorio", "tim_normal_final_cicatrices", stat="reputacion", cambio=15)
        self.historia["tim_normal_cicatrices"] = tim_normal_cicatrices

        tim_normal_aceptacion_eleccion = NodoHistoria(
            "tim_normal_aceptacion_eleccion",
            "LA ELECCIÓN ACEPTADA",
            "Con tiempo, aceptas tu elección. Elegiste a tu padre. Es algo que Batman nunca pudo hacer: "
            "elegir familia sobre el deber más amplio. Algunos lo verían como debilidad. Tú lo ves como "
            "humanidad. Y esa humanidad es lo que te hace diferente a Batman, lo que te hace Tim Drake.",
            "tim_eleccion_aceptada.png"
        )
        tim_normal_aceptacion_eleccion.agregar_opcion("Abrazar tu humanidad", "tim_normal_final_humano", stat="recursos", cambio=3)
        self.historia["tim_normal_aceptacion_eleccion"] = tim_normal_aceptacion_eleccion

        tim_normal_conversacion_dificil = NodoHistoria(
            "tim_normal_conversacion_dificil",
            "VERDADES DOLOROSAS",
            "La conversación en el hospital es brutalmente honesta. Tu padre admite que cada noche teme "
            "perder a su único hijo. Tú admites que temes fallarle como fallaste (en tu mente) a tu madre. "
            "Lloran juntos. Pero también llegan a un entendimiento: el amor significa aceptar los riesgos "
            "que la otra persona elige tomar.",
            "tim_verdades_dolorosas.png"
        )
        tim_normal_conversacion_dificil.agregar_opcion("Fortalecer el vínculo a través de la honestidad", "tim_normal_final_honesto", stat="recursos", cambio=3)
        self.historia["tim_normal_conversacion_dificil"] = tim_normal_conversacion_dificil

        tim_normal_trauma = NodoHistoria(
            "tim_normal_trauma",
            "TRAUMA COMPARTIDO",
            "Ambos están traumatizados por la experiencia. Tu padre tiene pesadillas. Tú te vuelves hipervigilante. "
            "Pero juntos, buscan terapia. Es un proceso lento. Dana los apoya. La Bat-Familia también. "
            "Aprenden que el trauma compartido puede acercarlos o destruirlos. Eligen lo primero.",
            "tim_trauma_compartido.png"
        )
        tim_normal_trauma.agregar_opcion("Sanar juntos", "tim_normal_final_sanacion_juntos", stat="salud", cambio=15)
        self.historia["tim_normal_trauma"] = tim_normal_trauma

        tim_normal_final_sacrificio = NodoHistoria(
            "tim_normal_final_sacrificio",
            "EL LEGADO DEL SACRIFICIO - FINAL",
            "Meses después, te has recuperado casi completamente. Las cicatrices permanecen, pero también "
            "el orgullo de tu padre. 'Diste tu vida por mí,' te dice una noche. 'Eso es lo que significa "
            "ser héroe. No solo salvar extraños, sino sacrificarse por quienes amas.' Tu relación con tu "
            "padre nunca ha sido más fuerte. Regresas a los Titans con una nueva perspectiva: el heroísmo "
            "no solo se trata de tácticas y estrategia, sino de amor y sacrificio. Batman nota el cambio: "
            "'Casi te pierdo, Tim. Pero lo que regresó es un héroe aún más completo.' Tu madre estaría "
            "orgullosa. Tu padre lo está. Y tú, finalmente, estás en paz con tus elecciones.",
            "tim_final_legado_del_sacrificio.png"
        )
        tim_normal_final_sacrificio.es_final = True
        self.historia["tim_normal_final_sacrificio"] = tim_normal_final_sacrificio

        tim_normal_final_supervivencia = NodoHistoria(
            "tim_normal_final_supervivencia",
            "SUPERVIVIENTES JUNTOS - FINAL",
            "Han sobrevivido juntos a lo imposible. Tu padre ahora es más que un apoyo pasivo; es parte "
            "de tu red de seguridad. Entiende el peligro y lo acepta. Dana también se une al esfuerzo, "
            "aprendiendo primeros auxilios avanzados. Tu familia se convierte en un activo único que otros "
            "héroes envidian: un sistema de apoyo que realmente comprende. Los Titans notan tu tranquilidad "
            "renovada. Batman comenta: 'Encontraste algo que yo nunca pude: balance verdadero.' Años después, "
            "cuando entrenas a un nuevo héroe joven, le dices: 'El heroísmo no significa sacrificar tu vida "
            "personal. Significa encontrar la manera de honrar ambas.' Es una lección que aprendiste a través "
            "del fuego. Y es la que define tu legado como Robin.",
            "tim_final_supervivientes_juntos.png"
        )
        tim_normal_final_supervivencia.es_final = True
        self.historia["tim_normal_final_supervivencia"] = tim_normal_final_supervivencia

        tim_normal_final_cicatrices = NodoHistoria(
            "tim_normal_final_cicatrices",
            "FORJADO EN BATALLA - FINAL",
            "Las cicatrices se convierten en parte de tu identidad. Cada una cuenta una historia: de protección, "
            "de sacrificio, de amor. Tu padre lleva sus propias cicatrices emocionales. Juntos, son recordatorios "
            "de lo que han superado. Los Titans te ven de manera diferente ahora: ya no eres solo el estratega "
            "brillante, sino el guerrero que ha sangrado por lo que ama. Batman te confía misiones más peligrosas, "
            "sabiendo que has sido probado de maneras que él nunca fue. Una noche, Dick Grayson te visita: "
            "'Sabes, Tim, cada Robin tiene su definición. Yo fui el acróbata. Jason fue el luchador callejero. "
            "Pero tú... tú eres el que encontró la manera de ser héroe sin perder su humanidad.' Es el mejor "
            "cumplido que podrías recibir.",
            "tim_final_forjado_en_batalla.png"
        )
        tim_normal_final_cicatrices.es_final = True
        self.historia["tim_normal_final_cicatrices"] = tim_normal_final_cicatrices

        tim_normal_final_humano = NodoHistoria(
            "tim_normal_final_humano",
            "LA HUMANIDAD DE ROBIN - FINAL",
            "Al final, tu mayor fortaleza no es tu intelecto o tus habilidades detectivescas, sino tu humanidad. "
            "Elegiste a tu padre sobre el deber más amplio, y aunque algunos murieron esa noche, muchos más "
            "sobrevivieron gracias a tu coordinación. Batman eventualmente te dice: 'Hiciste algo que yo nunca "
            "he podido hacer, Tim. Elegiste ser humano primero, héroe segundo. Y paradójicamente, eso te hace "
            "mejor héroe.' Tu padre vive, orgulloso de ti. Los Titans te siguen sin dudar. Y tú has aprendido "
            "la lección más difícil: que ser héroe no significa ser perfecto, significa hacer las elecciones "
            "difíciles y vivir con ellas. Años después, cuando un joven héroe te pregunta cómo manejas la culpa, "
            "le respondes: 'No la manejas. La cargas. Pero la cargas con amor, no con vergüenza.' Es sabiduría "
            "comprada con dolor. Pero es sabiduría real.",
            "tim_final_humanidad_de_robin.png"
        )
        tim_normal_final_humano.es_final = True
        self.historia["tim_normal_final_humano"] = tim_normal_final_humano

        tim_normal_final_honesto = NodoHistoria(
            "tim_normal_final_honesto",
            "VERDAD Y CONFIANZA - FINAL",
            "La honestidad radical con tu padre se convierte en el fundamento de tu relación. Ya no hay secretos, "
            "no hay mentiras piadosas. Él sabe cuándo estás herido. Tú sabes cuándo él está asustado. Esta "
            "transparencia es agotadora pero también liberadora. Dana comenta: 'Nunca he visto una relación "
            "padre-hijo tan honesta.' Batman lo nota también: 'La mayoría de los héroes viven en secreto. Tú "
            "has encontrado una manera de vivir en verdad.' No es perfecto. Tu padre todavía se preocupa cada "
            "noche. Tú todavía cargas culpa por las veces que no pudiste estar presente. Pero la confianza "
            "entre ustedes es inquebrantable. Y cuando finalmente te gradúas de Robin a algo más, tu padre "
            "está allí, lágrimas en los ojos: 'Sea cual sea el nombre que elijas, Tim, siempre serás mi héroe.' "
            "Es todo lo que necesitas escuchar.",
            "tim_final_verdad_y_confianza.png"
        )
        tim_normal_final_honesto.es_final = True
        self.historia["tim_normal_final_honesto"] = tim_normal_final_honesto

        tim_normal_final_sanacion_juntos = NodoHistoria(
            "tim_normal_final_sanacion_juntos",
            "SANADOS POR EL TIEMPO - FINAL",
            "La sanación no es lineal ni rápida. Hay días malos donde tu padre no puede dormir y tú no puedes "
            "concentrarte. Hay noches donde ambos reviven el ataque en pesadillas. Pero también hay días buenos, "
            "que gradualmente superan a los malos. La terapia ayuda. El apoyo de Dana y la Bat-Familia ayuda. "
            "Pero lo que más ayuda es simplemente estar presentes el uno para el otro. Años después, tu padre "
            "te confiesa: 'Ese ataque fue la peor noche de mi vida. Pero también me dio algo: certeza absoluta "
            "de que mi hijo es un héroe verdadero.' Tú respondes: 'Y me dio certeza de que tengo un padre que "
            "vale la pena proteger.' Los Titans notan que eres más paciente ahora, más comprensivo con las "
            "luchas de los demás. Batman dice: 'El trauma te rompió, Tim. Pero te reconstruiste más fuerte.' "
            "No es la historia que elegirías. Pero es tu historia. Y has aprendido a llevarla con gracia.",
            "tim_final_sanados_por_el_tiempo.png"
        )
        tim_normal_final_sanacion_juntos.es_final = True
        self.historia["tim_normal_final_sanacion_juntos"] = tim_normal_final_sanacion_juntos

# MODO DIFÍCIL: RED ROBIN - LA BÚSQUEDA DE BRUCE WAYNE (45 nodos)
        tim_dificil_inicio = NodoHistoria(
            "tim_dificil_inicio",
            "LA MUERTE DEL MURCIÉLAGO",
            "Gotham City, después de Final Crisis. Lo imposible ha sucedido: Bruce Wayne está muerto. "
            "Cayó luchando contra Darkseid, salvando el multiverso. La Bat-Familia está de luto. Se "
            "realizó un funeral. Dick Grayson ha asumido el manto de Batman. Y tú, Tim Drake, a los "
            "19 años, te encuentras en la Batcueva, mirando el traje vacío de Bruce. Pero algo no "
            "encaja. Hay detalles que no tienen sentido. Evidencia que otros ignoran. Y en tu corazón, "
            "sabes una verdad que nadie más acepta: Bruce Wayne está vivo.",
            "tim_muerte_del_murcielago.png"
)
        tim_dificil_inicio.agregar_opcion("Compartir tus dudas con Dick", "tim_dificil_dudas_dick", stat="reputacion", cambio=-5)
        tim_dificil_inicio.agregar_opcion("Investigar solo en silencio", "tim_dificil_investigacion_solitaria", stat="recursos", cambio=2)
        tim_dificil_inicio.agregar_opcion("Buscar el consejo de Alfred", "tim_dificil_consejo_alfred", stat="recursos", cambio=1)
        self.historia["tim_dificil_inicio"] = tim_dificil_inicio

        tim_dificil_dudas_dick = NodoHistoria(
            "tim_dificil_dudas_dick",
            "EL NUEVO BATMAN NO CREE",
            "Le presentas tus dudas a Dick Grayson. Él te mira con compasión y preocupación: 'Tim, "
            "todos estamos pasando por el duelo de manera diferente. Pero Bruce está muerto. Lo vimos.' "
            "Intentas explicar las inconsistencias en la evidencia, pero Dick te interrumpe: 'Estás en "
            "negación. Es comprensible. Pero tienes que aceptarlo y seguir adelante.'",
            "tim_nuevo_batman_no_cree.png"
)
        tim_dificil_dudas_dick.agregar_opcion("Insistir en tu teoría", "tim_dificil_insistencia", stat="reputacion", cambio=-10)
        tim_dificil_dudas_dick.agregar_opcion("Fingir aceptación", "tim_dificil_fingir", stat="reputacion", cambio=5)
        self.historia["tim_dificil_dudas_dick"] = tim_dificil_dudas_dick

        tim_dificil_investigacion_solitaria = NodoHistoria(
            "tim_dificil_investigacion_solitaria",
            "EL DETECTIVE SOLITARIO",
            "Decides investigar solo. Durante semanas, analizas cada detalle de la 'muerte' de Bruce. "
            "Los patrones de omega en su cuerpo, las inconsistencias temporales, los registros de Darkseid. "
            "Todo apunta a algo más que muerte: desplazamiento temporal. Pero no tienes pruebas concretas, "
            "solo intuición de detective. Y la intuición no es suficiente para convencer a nadie.",
            "tim_detective_solitario.png"
)
        tim_dificil_investigacion_solitaria.agregar_opcion("Buscar evidencia más concreta", "tim_dificil_busqueda_evidencia", stat="recursos", cambio=3)
        tim_dificil_investigacion_solitaria.agregar_opcion("Compartir hallazgos con la familia", "tim_dificil_compartir_hallazgos", stat="reputacion", cambio=-5)
        self.historia["tim_dificil_investigacion_solitaria"] = tim_dificil_investigacion_solitaria

        tim_dificil_consejo_alfred = NodoHistoria(
            "tim_dificil_consejo_alfred",
            "LA FE DE ALFRED",
            "Alfred te sirve té en silencio mientras le explicas tus teorías. A diferencia de Dick, él "
            "no te interrumpe. Cuando terminas, suspira: 'Master Timothy, he servido a los Wayne toda mi "
            "vida. Y si hay algo que he aprendido es esto: nunca subestimar a un Wayne. Si usted cree que "
            "el Maestro Bruce vive, entonces investigar es su deber.' Es el único apoyo que recibirás.",
            "tim_fe_de_alfred.png"
)
        tim_dificil_consejo_alfred.agregar_opcion("Agradecerle y comenzar la búsqueda", "tim_dificil_inicio_busqueda", stat="recursos", cambio=2)
        self.historia["tim_dificil_consejo_alfred"] = tim_dificil_consejo_alfred

        tim_dificil_insistencia = NodoHistoria(
            "tim_dificil_insistencia",
            "LA CONFRONTACIÓN",
            "Insistes en tu teoría, presentando cada pieza de evidencia. Dick se frustra: 'Tim, esto no "
            "es saludable. Estás obsesionándote. Bruce está muerto y necesitas aceptarlo.' Damian, el hijo "
            "biológico de Bruce, interviene burlonamente: 'Drake está claramente en negación. Patético.' "
            "La tensión en la Batcueva es palpable.",
            "tim_confrontacion_dick.png"
)
        tim_dificil_insistencia.agregar_opcion("Retirarte y buscar solo", "tim_dificil_retiro", stat="reputacion", cambio=-15)
        tim_dificil_insistencia.agregar_opcion("Pedir a Dick que confíe en ti", "tim_dificil_pedir_confianza", stat="reputacion", cambio=-5)
        self.historia["tim_dificil_insistencia"] = tim_dificil_insistencia

        tim_dificil_fingir = NodoHistoria(
            "tim_dificil_fingir",
            "LA MÁSCARA DEL DUELO",
            "Finges aceptar que Bruce está muerto. Dick parece aliviado: 'Me alegra que lo entiendas, Tim. "
            "Ahora podemos seguir adelante juntos.' Pero en tu mente, ya estás planeando tu búsqueda en "
            "secreto. Si la familia no te apoyará, lo harás solo. Siempre lo has hecho cuando fue necesario.",
            "tim_mascara_del_duelo.png"
)
        tim_dificil_fingir.agregar_opcion("Investigar en secreto", "tim_dificil_investigacion_secreta", stat="recursos", cambio=2)
        self.historia["tim_dificil_fingir"] = tim_dificil_fingir

        tim_dificil_busqueda_evidencia = NodoHistoria(
            "tim_dificil_busqueda_evidencia",
            "RASTROS EN EL TIEMPO",
            "Profundizas en tu investigación. Encuentras anomalías temporales en los registros de la Justice "
            "League. Rastros de energía omega que no deberían existir si Bruce simplemente murió. Es evidencia "
            "circunstancial, pero es algo. Necesitas más. Necesitas pruebas que incluso Dick no pueda ignorar.",
            "tim_rastros_en_el_tiempo.png"
)
        tim_dificil_busqueda_evidencia.agregar_opcion("Buscar tecnología de los New Gods", "tim_dificil_new_gods", stat="recursos", cambio=3)
        tim_dificil_busqueda_evidencia.agregar_opcion("Consultar con expertos temporales", "tim_dificil_expertos", stat="recursos", cambio=2)
        self.historia["tim_dificil_busqueda_evidencia"] = tim_dificil_busqueda_evidencia

        tim_dificil_compartir_hallazgos = NodoHistoria(
            "tim_dificil_compartir_hallazgos",
            "RECHAZADO",
            "Compartes tus hallazgos con la Bat-Familia en una reunión. Dick escucha pacientemente. Barbara "
            "Gordon analiza tus datos. Damian se burla. Al final, Dick dice suavemente: 'Tim, esto es "
            "confirmation bias. Estás viendo patrones porque quieres verlos. Bruce está muerto. Lo siento.' "
            "Estás solo en tu creencia.",
            "tim_rechazado_por_familia.png"
)
        tim_dificil_compartir_hallazgos.agregar_opcion("Continuar solo", "tim_dificil_retiro", stat="reputacion", cambio=-10)
        self.historia["tim_dificil_compartir_hallazgos"] = tim_dificil_compartir_hallazgos

        tim_dificil_inicio_busqueda = NodoHistoria(
            "tim_dificil_inicio_busqueda",
            "LA BÚSQUEDA COMIENZA",
            "Con la bendición silenciosa de Alfred, comienzas tu búsqueda. Pero un día, Dick te llama a la "
            "Batcueva. Tiene noticias: 'Tim, he tomado una decisión. Voy a ser Batman, como Bruce hubiera "
            "querido. Y necesito un Robin a mi lado.' Tu corazón salta. Pero entonces añade: 'Damian será "
            "mi Robin. Tú ya no eres un aprendiz, Tim. Eres un igual. Ya no necesitas ser Robin.'",
            "tim_inicio_busqueda.png"
)
        tim_dificil_inicio_busqueda.agregar_opcion("Aceptar con gracia", "tim_dificil_aceptacion_gracia", stat="reputacion", cambio=5)
        tim_dificil_inicio_busqueda.agregar_opcion("Expresar tu dolor", "tim_dificil_expresar_dolor", stat="reputacion", cambio=-5)
        tim_dificil_inicio_busqueda.agregar_opcion("Marcharte en silencio", "tim_dificil_marchar_silencio", stat="reputacion", cambio=-10)
        self.historia["tim_dificil_inicio_busqueda"] = tim_dificil_inicio_busqueda

        tim_dificil_retiro = NodoHistoria(
            "tim_dificil_retiro",
            "EL RETIRO DEL ROBIN",
            "Te retiras de la Batcueva sabiendo que estás solo. Días después, Dick te contacta con una "
            "noticia que confirma tu aislamiento: 'Tim, he decidido que Damian será mi Robin. Tú ya no "
            "necesitas ese manto. Eres más que eso ahora.' Se supone que es un cumplido, pero se siente "
            "como un rechazo. Ya no eres Robin. Ya no tienes el apoyo de la familia. Pero tienes una misión.",
            "tim_retiro_del_robin.png"
        )
        tim_dificil_retiro.agregar_opcion("Abandonar Gotham para buscar a Bruce", "tim_dificil_abandono_gotham", stat="reputacion", cambio=-15)
        self.historia["tim_dificil_retiro"] = tim_dificil_retiro

        tim_dificil_pedir_confianza = NodoHistoria(
            "tim_dificil_pedir_confianza",
            "LA CONFIANZA NEGADA",
            "'Dick, confía en mí,' suplicas. 'He sido Robin por años. He resuelto casos que tú no pudiste. "
            "Si digo que Bruce está vivo, al menos investígalo.' Dick suspira: 'No es sobre confianza, Tim. "
            "Es sobre aceptar la realidad. Y la realidad es que Bruce murió.' Damian añade: 'Quizás Drake "
            "debería retirarse si no puede manejar la verdad.'",
            "tim_confianza_negada.png"
        )
        tim_dificil_pedir_confianza.agregar_opcion("Buscar solo", "tim_dificil_retiro", stat="reputacion", cambio=-10)
        self.historia["tim_dificil_pedir_confianza"] = tim_dificil_pedir_confianza

        tim_dificil_investigacion_secreta = NodoHistoria(
            "tim_dificil_investigacion_secreta",
            "DOBLE VIDA",
            "Por semanas, mantienes la apariencia de haber aceptado la muerte de Bruce mientras investigas "
            "en secreto. Usas recursos de la Batcueva cuando nadie mira. Pero Dick eventualmente nota "
            "discrepancias. Te confronta: 'Tim, ¿qué estás haciendo?' No puedes seguir mintiendo.",
            "tim_doble_vida_investigacion.png"
        )
        tim_dificil_investigacion_secreta.agregar_opcion("Admitir la verdad", "tim_dificil_admitir_verdad", stat="reputacion", cambio=-10)
        tim_dificil_investigacion_secreta.agregar_opcion("Seguir mintiendo", "tim_dificil_seguir_mintiendo", stat="reputacion", cambio=-15)
        self.historia["tim_dificil_investigacion_secreta"] = tim_dificil_investigacion_secreta

        tim_dificil_new_gods = NodoHistoria(
            "tim_dificil_new_gods",
            "TECNOLOGÍA DE LOS NEW GODS",
            "Investigas la tecnología New God, específicamente las Vigas Omega de Darkseid. Descubres que "
            "estas no simplemente matan: pueden desplazar objetos en el tiempo. Es la primera evidencia real "
            "que apoye tu teoría. Pero necesitas más. Necesitas rastrear hacia dónde fue desplazado Bruce.",
            "tim_tecnologia_new_gods.png"
        )
        tim_dificil_new_gods.agregar_opcion("Buscar expertos en viajes temporales", "tim_dificil_expertos", stat="recursos", cambio=2)
        self.historia["tim_dificil_new_gods"] = tim_dificil_new_gods

        tim_dificil_expertos = NodoHistoria(
            "tim_dificil_expertos",
            "CONSULTA CON EXPERTOS",
            "Consultas con Rip Hunter y otros expertos temporales. Confirman que tu teoría es posible: Bruce "
            "podría estar atrapado en la corriente temporal. Pero localizar a alguien en el tiempo sin "
            "coordenadas exactas es casi imposible. Necesitas más evidencia, más rastros. Y solo hay un "
            "lugar donde buscar: donde Bruce estuvo por última vez.",
            "tim_consulta_expertos_temporales.png"
        )
        tim_dificil_expertos.agregar_opcion("Viajar al sitio de la batalla final", "tim_dificil_sitio_batalla", stat="recursos", cambio=3)
        self.historia["tim_dificil_expertos"] = tim_dificil_expertos

        tim_dificil_aceptacion_gracia = NodoHistoria(
            "tim_dificil_aceptacion_gracia",
            "GRACIA BAJO PRESIÓN",
            "Aceptas con gracia: 'Entiendo, Dick. Damian será un buen Robin para ti.' Dick parece aliviado. "
            "Pero por dentro, tu corazón está roto. Has sido Robin por años, y ahora ese manto le pertenece "
            "al hijo biológico de Bruce. Te sientes reemplazado. Pero no dejas que Dick lo vea. Tienes una "
            "misión más importante: encontrar a Bruce.",
            "tim_aceptacion_con_gracia.png"
        )
        tim_dificil_aceptacion_gracia.agregar_opcion("Dejar Gotham en buenos términos", "tim_dificil_partir_bien", stat="reputacion", cambio=5)
        self.historia["tim_dificil_aceptacion_gracia"] = tim_dificil_aceptacion_gracia

        tim_dificil_expresar_dolor = NodoHistoria(
            "tim_dificil_expresar_dolor",
            "HERIDA ABIERTA",
            "'¿Me estás reemplazando?' preguntas, sin poder ocultar el dolor. Dick parece sorprendido: 'No "
            "es un reemplazo, Tim. Es una evolución. Tú has superado ser Robin.' Pero no se siente así. Se "
            "siente como rechazo. Como si ya no fueras necesario. Damian sonríe con satisfacción. La "
            "conversación termina mal.",
            "tim_herida_abierta.png"
        )
        tim_dificil_expresar_dolor.agregar_opcion("Dejar la Batcueva", "tim_dificil_abandono_gotham", stat="reputacion", cambio=-10)
        self.historia["tim_dificil_expresar_dolor"] = tim_dificil_expresar_dolor

        tim_dificil_marchar_silencio = NodoHistoria(
            "tim_dificil_marchar_silencio",
            "PARTIDA SILENCIOSA",
            "Sin decir palabra, te das la vuelta y te marchas. Dick te llama: '¡Tim, espera!' Pero no te "
            "detienes. Ya no eres Robin. Ya no tienes un lugar aquí. Pero tienes algo que Dick no tiene: "
            "la certeza de que Bruce Wayne está vivo. Y vas a demostrarlo, con o sin el apoyo de la familia.",
            "tim_partida_silenciosa.png"
        )
        tim_dificil_marchar_silencio.agregar_opcion("Abandonar Gotham", "tim_dificil_abandono_gotham", stat="reputacion", cambio=-15)
        self.historia["tim_dificil_marchar_silencio"] = tim_dificil_marchar_silencio

        tim_dificil_abandono_gotham = NodoHistoria(
            "tim_dificil_abandono_gotham",
            "ADIÓS A GOTHAM",
            "Empacas tus cosas y te preparas para abandonar Gotham. Alfred te encuentra: 'Master Timothy, "
            "¿a dónde irá?' Le explicas tu plan de buscar a Bruce globalmente. Alfred asiente y te entrega "
            "un paquete: 'Un nuevo traje. Si va a buscar al Maestro Bruce, necesitará una nueva identidad.' "
            "Es el traje de Red Robin. 'Ya no es Robin,' dice Alfred. 'Ahora es algo más.'",
            "tim_adios_a_gotham.png"
        )
        tim_dificil_abandono_gotham.agregar_opcion("Adoptar la identidad de Red Robin", "tim_dificil_red_robin", stat="reputacion", cambio=10, item="Traje de Red Robin")
        self.historia["tim_dificil_abandono_gotham"] = tim_dificil_abandono_gotham

        tim_dificil_admitir_verdad = NodoHistoria(
            "tim_dificil_admitir_verdad",
            "LA VERDAD REVELADA",
            "Admites que has estado investigando la 'muerte' de Bruce. Dick está decepcionado: 'Tim, pensé "
            "que habías aceptado la realidad.' Intentas explicar tus hallazgos, pero él te interrumpe: "
            "'Suficiente. Si no puedes aceptar que Bruce está muerto, quizás necesitas tiempo fuera de Gotham.' "
            "Es efectivamente un exilio.",
            "tim_verdad_revelada_a_dick.png"
        )
        tim_dificil_admitir_verdad.agregar_opcion("Aceptar el exilio", "tim_dificil_exilio", stat="reputacion", cambio=-15)
        self.historia["tim_dificil_admitir_verdad"] = tim_dificil_admitir_verdad

        tim_dificil_seguir_mintiendo = NodoHistoria(
            "tim_dificil_seguir_mintiendo",
            "MENTIRAS QUE SEPARAN",
            "Sigues mintiendo, pero Dick no es tonto. Te confronta con evidencia de tu investigación secreta: "
            "'No puedo confiar en ti si me mientes, Tim.' La relación está severamente dañada. Dick te pide "
            "que abandones la Batcueva hasta que 'estés listo para ser honesto'. Has perdido su confianza.",
            "tim_mentiras_que_separan.png"
        )
        tim_dificil_seguir_mintiendo.agregar_opcion("Dejar la Batcueva", "tim_dificil_abandono_gotham", stat="reputacion", cambio=-20)
        self.historia["tim_dificil_seguir_mintiendo"] = tim_dificil_seguir_mintiendo

        tim_dificil_sitio_batalla = NodoHistoria(
            "tim_dificil_sitio_batalla",
            "EL CAMPO DE BATALLA FINAL",
            "Viajas al sitio donde Bruce supuestamente murió. Con equipo especializado, detectas rastros "
            "residuales de energía omega. Pero hay algo más: firmas temporales que apuntan a múltiples "
            "períodos de tiempo. Bruce no murió. Fue dispersado a través del tiempo. Tienes tu prueba. "
            "Pero cuando regresas a compartirla, Dick ha tomado su decisión sobre Damian.",
            "tim_campo_batalla_final.png"
        )
        tim_dificil_sitio_batalla.agregar_opcion("Confrontar a Dick con la evidencia", "tim_dificil_confrontacion_evidencia", stat="reputacion", cambio=-5)
        self.historia["tim_dificil_sitio_batalla"] = tim_dificil_sitio_batalla

        tim_dificil_partir_bien = NodoHistoria(
            "tim_dificil_partir_bien",
            "DESPEDIDA CIVILIZADA",
            "Te despides de la Bat-Familia en buenos términos. Dick te abraza: 'Siempre serás parte de esta "
            "familia, Tim.' Barbara te desea suerte. Incluso Damian ofrece un asentimiento de respeto (a su "
            "manera). Solo Alfred sabe la verdad de tu misión. 'Encuéntrelo, Master Timothy,' susurra. 'Y "
            "tráigalo a casa.'",
            "tim_despedida_civilizada.png"
        )
        tim_dificil_partir_bien.agregar_opcion("Comenzar la búsqueda global", "tim_dificil_red_robin", stat="recursos", cambio=2, item="Traje de Red Robin")
        self.historia["tim_dificil_partir_bien"] = tim_dificil_partir_bien

        tim_dificil_exilio = NodoHistoria(
            "tim_dificil_exilio",
            "EXILIADO DE CASA",
            "Dejas Gotham, exiliado por la familia que alguna vez te acogió. La ironía no se te escapa: "
            "Bruce te aceptó cuando nadie más lo hizo, y ahora que intentas salvarlo, su familia te rechaza. "
            "Pero no importa. Tu misión es clara. Alfred te contacta en secreto y te envía el traje de Red "
            "Robin: 'Una nueva identidad para una nueva misión.'",
            "tim_exiliado_de_casa.png"
        )
        tim_dificil_exilio.agregar_opcion("Abrazar el exilio y la nueva identidad", "tim_dificil_red_robin", stat="reputacion", cambio=-10, item="Traje de Red Robin")
        self.historia["tim_dificil_exilio"] = tim_dificil_exilio

        tim_dificil_confrontacion_evidencia = NodoHistoria(
            "tim_dificil_confrontacion_evidencia",
            "EVIDENCIA IGNORADA",
            "Confrontas a Dick con tu evidencia: rastros de energía omega, firmas temporales, todo. Dick "
            "la estudia seriamente. Por un momento, crees que te creerá. Pero entonces dice: 'Es interesante, "
            "Tim. Pero no es concluyente. Podría ser solo energía residual. No puedo basar decisiones en "
            "especulación.' Tu evidencia no fue suficiente.",
            "tim_evidencia_ignorada.png"
        )
        tim_dificil_confrontacion_evidencia.agregar_opcion("Buscar evidencia más fuerte solo", "tim_dificil_abandono_gotham", stat="reputacion", cambio=-10)
        self.historia["tim_dificil_confrontacion_evidencia"] = tim_dificil_confrontacion_evidencia

        tim_dificil_red_robin = NodoHistoria(
            "tim_dificil_red_robin",
            "EL NACIMIENTO DE RED ROBIN",
            "Te pones el traje de Red Robin por primera vez. Ya no eres el compañero de Batman. Eres tu "
            "propio héroe, con tu propia misión. El traje es similar al de Robin pero más oscuro, más maduro. "
            "Representa lo que eres ahora: un detective independiente en una búsqueda solitaria. Tu primera "
            "parada: Europa, donde las últimas pistas sobre Bruce apuntan.",
            "tim_nacimiento_red_robin.png"
        )
        tim_dificil_red_robin.agregar_opcion("Viajar a Europa", "tim_dificil_europa", stat="recursos", cambio=3)
        self.historia["tim_dificil_red_robin"] = tim_dificil_red_robin

        tim_dificil_europa = NodoHistoria(
            "tim_dificil_europa",
            "RASTROS EN EUROPA",
            "Tu búsqueda te lleva por Europa: París, Praga, Estambul. Sigues pistas minúsculas que otros "
            "pasarían por alto. Una firma de energía aquí, un testimonio extraño allá. Los Titans intentan "
            "contactarte, preocupados. Dick envía mensajes que ignoras. Estás completamente enfocado en tu "
            "misión. Y entonces, en un café en Praga, alguien te observa: un ninja de la Liga de Asesinos.",
            "tim_rastros_en_europa.png"
        )
        tim_dificil_europa.agregar_opcion("Seguir al ninja", "tim_dificil_seguir_ninja", stat="recursos", cambio=2)
        tim_dificil_europa.agregar_opcion("Confrontar al ninja", "tim_dificil_confrontar_ninja", stat="salud", cambio=-10)
        self.historia["tim_dificil_europa"] = tim_dificil_europa

        tim_dificil_seguir_ninja = NodoHistoria(
            "tim_dificil_seguir_ninja",
            "LA SOMBRA DE LA LIGA",
            "Sigues discretamente al ninja a través de las calles de Praga. Te conduce a un edificio antiguo. "
            "Adentro, escuchas una conversación en árabe. Reconoces la voz: Ra's al Ghul. Está aquí, en "
            "Europa. Y está hablando sobre Bruce Wayne. '...el Detective no está muerto,' dice Ra's. 'Pero "
            "tampoco importa. Su legado será destruido de todas formas.'",
            "tim_sombra_de_la_liga.png"
        )
        tim_dificil_seguir_ninja.agregar_opcion("Infiltrarte para escuchar más", "tim_dificil_infiltracion", stat="recursos", cambio=3)
        tim_dificil_seguir_ninja.agregar_opcion("Confrontar a Ra's directamente", "tim_dificil_confrontar_ras", stat="salud", cambio=-15)
        self.historia["tim_dificil_seguir_ninja"] = tim_dificil_seguir_ninja

        tim_dificil_confrontar_ninja = NodoHistoria(
            "tim_dificil_confrontar_ninja",
            "EMBOSCADA",
            "Confrontas al ninja, exigiendo saber por qué te sigue. Él sonríe y ataca. Es un combatiente "
            "experto de la Liga de Asesinos. La batalla es brutal. Logras derrotarlo, pero no antes de que "
            "envíe una señal. Más ninjas están en camino. El ninja derrotado susurra: 'Ra's al Ghul sabe "
            "que estás buscando al Detective. Y tiene sus propios planes.'",
            "tim_emboscada_ninja.png"
        )
        tim_dificil_confrontar_ninja.agregar_opcion("Huir antes de que lleguen refuerzos", "tim_dificil_huida", stat="salud", cambio=-5)
        tim_dificil_confrontar_ninja.agregar_opcion("Interrogar al ninja", "tim_dificil_interrogatorio", stat="recursos", cambio=2)
        self.historia["tim_dificil_confrontar_ninja"] = tim_dificil_confrontar_ninja

        tim_dificil_infiltracion = NodoHistoria(
            "tim_dificil_infiltracion",
            "ESCUCHANDO EN LAS SOMBRAS",
            "Te infiltras silenciosamente, usando tus habilidades de sigilo perfeccionadas bajo Batman. "
            "Escuchas la conversación completa de Ra's: está planeando destruir el legado de Batman atacando "
            "a todos sus seres queridos simultáneamente. Alfred, Dick, Damian, Barbara, Lucius Fox, incluso "
            "Selina Kyle. Todos serán asesinados en una noche. Y luego, robará Wayne Enterprises.",
            "tim_escuchando_en_las_sombras.png"
        )
        tim_dificil_infiltracion.agregar_opcion("Grabar la conversación como evidencia", "tim_dificil_grabacion", stat="recursos", cambio=3)
        tim_dificil_infiltracion.agregar_opcion("Atacar a Ra's ahora", "tim_dificil_ataque_prematuro", stat="salud", cambio=-20)
        self.historia["tim_dificil_infiltracion"] = tim_dificil_infiltracion

        tim_dificil_confrontar_ras = NodoHistoria(
            "tim_dificil_confrontar_ras",
            "FRENTE A FRENTE CON EL DEMONIO",
            "Irrumpes en la reunión. Ra's al Ghul te mira sin sorpresa: 'Ah, Timothy Drake. Te estaba "
            "esperando.' Los ninjas te rodean, pero Ra's levanta una mano deteniéndolos. 'El hijo adoptivo del Detective. Dime, ¿realmente "
            "crees que Bruce Wayne está vivo?' Hay un desafío en su voz, pero también curiosidad genuina.",
            "tim_frente_a_frente_demonio.png"
        )
        tim_dificil_confrontar_ras.agregar_opcion("Afirmar tu creencia", "tim_dificil_afirmar_creencia", stat="reputacion", cambio=10)
        tim_dificil_confrontar_ras.agregar_opcion("Exigir saber sus planes", "tim_dificil_exigir_planes", stat="salud", cambio=-10)
        self.historia["tim_dificil_confrontar_ras"] = tim_dificil_confrontar_ras

        tim_dificil_huida = NodoHistoria(
            "tim_dificil_huida",
            "RETIRO TÁCTICO",
            "Huyes antes de que lleguen los refuerzos. Has confirmado lo peor: Ra's al Ghul está involucrado, "
            "y tiene planes para el legado de Batman. Necesitas advertir a la Bat-Familia, pero ¿te creerán? "
            "Has sido exiliado, considerado en negación. Pero no tienes opción. Demasiadas vidas están en "
            "riesgo.",
            "tim_retiro_tactico.png"
        )
        tim_dificil_huida.agregar_opcion("Contactar a Dick con la advertencia", "tim_dificil_advertencia_dick", stat="reputacion", cambio=-5)
        tim_dificil_huida.agregar_opcion("Regresar a Gotham personalmente", "tim_dificil_regreso_gotham", stat="recursos", cambio=2)
        self.historia["tim_dificil_huida"] = tim_dificil_huida

        tim_dificil_interrogatorio = NodoHistoria(
            "tim_dificil_interrogatorio",
            "EXTRAYENDO INFORMACIÓN",
            "Interrogas al ninja usando técnicas que aprendiste de Batman. Él resiste inicialmente, pero "
            "finalmente habla: 'Ra's al Ghul planea atacar a toda la familia del Detective simultáneamente. "
            "Una noche. Múltiples objetivos. Incluso el Detective no podría protegerlos a todos.' El plan "
            "es brillante en su crueldad. Necesitas actuar rápido.",
            "tim_extrayendo_informacion.png"
        )
        tim_dificil_interrogatorio.agregar_opcion("Volar a Gotham para advertir", "tim_dificil_regreso_gotham", stat="recursos", cambio=2)
        self.historia["tim_dificil_interrogatorio"] = tim_dificil_interrogatorio

        tim_dificil_grabacion = NodoHistoria(
            "tim_dificil_grabacion",
            "EVIDENCIA CONCRETA",
            "Grabas toda la conversación de Ra's. Es evidencia concreta de su plan. Pero mientras te retiras, "
            "pisas una tabla suelta. El crujido alerta a los ninjas. '¡Intruso!' gritan. Tienes segundos "
            "para escapar con la grabación. Los ninjas te persiguen por las calles de Praga.",
            "tim_evidencia_concreta.png"
        )
        tim_dificil_grabacion.agregar_opcion("Huir con la evidencia", "tim_dificil_escape_evidencia", stat="salud", cambio=-10)
        tim_dificil_grabacion.agregar_opcion("Luchar para proteger la grabación", "tim_dificil_lucha_proteger", stat="salud", cambio=-15)
        self.historia["tim_dificil_grabacion"] = tim_dificil_grabacion

        tim_dificil_ataque_prematuro = NodoHistoria(
            "tim_dificil_ataque_prematuro",
            "ERROR TÁCTICO",
            "Atacas a Ra's, impulsado por la urgencia. Es un error. Ra's es uno de los mejores combatientes "
            "del mundo, con siglos de experiencia. Te derrota fácilmente, aunque no sin esfuerzo. 'Impulsivo,' "
            "dice Ra's. 'El Detective te habría enseñado mejor. Quizás su muerte fue una misericordia si "
            "este es el legado que dejó.' Sus palabras duelen más que los golpes.",
            "tim_error_tactico.png"
        )
        tim_dificil_ataque_prematuro.agregar_opcion("Sobrevivir al interrogatorio de Ra's", "tim_dificil_interrogatorio_ras", stat="salud", cambio=-20)
        self.historia["tim_dificil_ataque_prematuro"] = tim_dificil_ataque_prematuro

        tim_dificil_afirmar_creencia = NodoHistoria(
            "tim_dificil_afirmar_creencia",
            "FE INQUEBRANTABLE",
            "'Bruce Wayne está vivo,' afirmas con convicción. 'Lo sé con la misma certeza con que sé mi "
            "propio nombre.' Ra's te estudia intensamente, luego sonríe: 'Interesante. Yo también creo que "
            "el Detective vive. Pero a diferencia de ti, no me importa. Su legado morirá de todas formas.' "
            "Explica su plan de asesinar a todos los seres queridos de Bruce.",
            "tim_fe_inquebrantable.png"
        )
        tim_dificil_afirmar_creencia.agregar_opcion("Desafiar a Ra's", "tim_dificil_desafio", stat="reputacion", cambio=15)
        tim_dificil_afirmar_creencia.agregar_opcion("Intentar negociar", "tim_dificil_negociacion", stat="recursos", cambio=2)
        self.historia["tim_dificil_afirmar_creencia"] = tim_dificil_afirmar_creencia

        tim_dificil_exigir_planes = NodoHistoria(
            "tim_dificil_exigir_planes",
            "EXIGENCIAS ARROGANTES",
            "'¿Qué planeas hacer, Ra's?' exiges. Él se ríe: 'Qué arrogante. ¿Por qué te lo diría?' Los "
            "ninjas te atacan. Luchas valientemente, pero estás superado en número. Ra's observa con interés "
            "mientras peleas. 'Tienes el espíritu del Detective,' admite. 'Lástima que no tengas su prudencia.' "
            "Logras escapar, pero gravemente herido.",
            "tim_exigencias_arrogantes.png"
        )
        tim_dificil_exigir_planes.agregar_opcion("Retirarte y recuperarte", "tim_dificil_recuperacion", stat="salud", cambio=-15)
        self.historia["tim_dificil_exigir_planes"] = tim_dificil_exigir_planes

        tim_dificil_advertencia_dick = NodoHistoria(
            "tim_dificil_advertencia_dick",
            "LA ADVERTENCIA IGNORADA",
            "Contactas a Dick frenéticamente: 'Ra's al Ghul planea atacar a toda la familia. Múltiples "
            "objetivos. Necesitas implementar protocolos de seguridad ahora.' Dick suspira: 'Tim, ¿de verdad? "
            "¿Esto es sobre tu búsqueda obsesiva de Bruce?' Intentas explicar, pero él no te escucha. "
            "'Llámame cuando estés listo para aceptar la realidad,' dice y cuelga.",
            "tim_advertencia_ignorada.png"
        )
        tim_dificil_advertencia_dick.agregar_opcion("Proteger a la familia solo", "tim_dificil_proteccion_solitaria", stat="recursos", cambio=-3)
        tim_dificil_advertencia_dick.agregar_opcion("Buscar ayuda de los Titans", "tim_dificil_ayuda_titans", stat="reputacion", cambio=10)
        self.historia["tim_dificil_advertencia_dick"] = tim_dificil_advertencia_dick

        tim_dificil_regreso_gotham = NodoHistoria(
            "tim_dificil_regreso_gotham",
            "DE VUELTA EN GOTHAM",
            "Regresas a Gotham después de semanas ausente. La ciudad se siente diferente sin ser Robin. "
            "Intentas contactar a Dick, pero él está patrullando con Damian. Barbara Gordon acepta reunirse "
            "contigo. Le explicas el plan de Ra's. Ella te escucha, pero hay escepticismo en sus ojos: "
            "'Tim, ¿tienes pruebas concretas o solo teorías?'",
            "tim_de_vuelta_en_gotham.png"
        )
        tim_dificil_regreso_gotham.agregar_opcion("Presentar tu evidencia", "tim_dificil_presentar_evidencia", stat="reputacion", cambio=5)
        tim_dificil_regreso_gotham.agregar_opcion("Pedir que confíe en ti", "tim_dificil_pedir_confianza_barbara", stat="reputacion", cambio=-5)
        self.historia["tim_dificil_regreso_gotham"] = tim_dificil_regreso_gotham

        tim_dificil_escape_evidencia = NodoHistoria(
            "tim_dificil_escape_evidencia",
            "PERSECUCIÓN NOCTURNA",
            "Corres por las calles de Praga con los ninjas pisándote los talones. Usas cada truco que Batman "
            "te enseñó: callejones, azoteas, cambios de dirección repentinos. La grabación está a salvo en "
            "tu traje. Logras perderlos y escapar de la ciudad. Tienes la evidencia que necesitas, pero "
            "ahora Ra's sabe que sabes. El reloj está corriendo.",
            "tim_persecucion_nocturna.png"
        )
        tim_dificil_escape_evidencia.agregar_opcion("Enviar la evidencia a la Bat-Familia", "tim_dificil_enviar_evidencia", stat="recursos", cambio=2)
        tim_dificil_escape_evidencia.agregar_opcion("Regresar a Gotham personalmente", "tim_dificil_regreso_urgente", stat="recursos", cambio=3)
        self.historia["tim_dificil_escape_evidencia"] = tim_dificil_escape_evidencia

        tim_dificil_lucha_proteger = NodoHistoria(
            "tim_dificil_lucha_proteger",
            "LUCHANDO POR LA VERDAD",
            "Te enfrentas a múltiples ninjas para proteger la grabación. Estás superado en número pero no "
            "en determinación. Peleas con todo lo que tienes, recordando cada lección de Bruce. Los ninjas "
            "son expertos, pero tú eres Red Robin, entrenado por el mejor. Logras derrotarlos, aunque quedas "
            "gravemente herido. La grabación está a salvo.",
            "tim_luchando_por_la_verdad.png"
        )
        tim_dificil_lucha_proteger.agregar_opcion("Buscar tratamiento médico", "tim_dificil_tratamiento", stat="salud", cambio=10)
        tim_dificil_lucha_proteger.agregar_opcion("Ignorar las heridas y continuar", "tim_dificil_ignorar_heridas", stat="salud", cambio=-10)
        self.historia["tim_dificil_lucha_proteger"] = tim_dificil_lucha_proteger

        tim_dificil_interrogatorio_ras = NodoHistoria(
            "tim_dificil_interrogatorio_ras",
            "EN MANOS DEL DEMONIO",
            "Ra's te interroga, pero no con tortura física. Usa táctica psicológica: 'Dime, Timothy, ¿por "
            "qué buscas al Detective? ¿Es lealtad o simplemente no puedes aceptar que te abandonó?' Sus "
            "palabras son como cuchillos. 'Él eligió morir en lugar de regresar contigo. ¿Qué dice eso?' "
            "Tienes que resistir.",
            "tim_en_manos_del_demonio.png"
        )
        tim_dificil_interrogatorio_ras.agregar_opcion("Resistir psicológicamente", "tim_dificil_resistencia_mental", stat="salud", cambio=-15)
        tim_dificil_interrogatorio_ras.agregar_opcion("Contraatacar verbalmente", "tim_dificil_contraataque_verbal", stat="reputacion", cambio=10)
        self.historia["tim_dificil_interrogatorio_ras"] = tim_dificil_interrogatorio_ras

        tim_dificil_desafio = NodoHistoria(
            "tim_dificil_desafio",
            "EL DESAFÍO DE RED ROBIN",
            "'No permitiré que destruyas el legado de Bruce,' declaras. Ra's sonríe con aprobación: 'Ah, "
            "ahí está. El fuego del Detective. Dime, Red Robin, ¿cómo planeas detenerme? ¿Tú solo contra "
            "toda la Liga de Asesinos?' Tiene razón. No puedes derrotarlo por la fuerza. Necesitas ser más "
            "inteligente. Necesitas ser el detective que Bruce te entrenó para ser.",
            "tim_desafio_de_red_robin.png"
        )
        tim_dificil_desafio.agregar_opcion("Buscar aliados", "tim_dificil_buscar_aliados", stat="recursos", cambio=2)
        tim_dificil_desafio.agregar_opcion("Planear una estrategia en solitario", "tim_dificil_estrategia_solitaria", stat="recursos", cambio=3)
        self.historia["tim_dificil_desafio"] = tim_dificil_desafio

        tim_dificil_negociacion = NodoHistoria(
            "tim_dificil_negociacion",
            "NEGOCIANDO CON EL DIABLO",
            "Intentas negociar: 'Ra's, si Bruce está vivo como ambos creemos, atacar a su familia solo "
            "garantizará su venganza.' Ra's considera esto: 'Un punto válido. Pero el Detective ha tenido "
            "siglos para vengarse de mí por otros crímenes. Uno más no hará diferencia.' La negociación "
            "falla. Ra's no puede ser razonado.",
            "tim_negociando_con_el_diablo.png"
        )
        tim_dificil_negociacion.agregar_opcion("Retirarte y planear defensa", "tim_dificil_planear_defensa", stat="recursos", cambio=2)
        self.historia["tim_dificil_negociacion"] = tim_dificil_negociacion

        tim_dificil_recuperacion = NodoHistoria(
            "tim_dificil_recuperacion",
            "SANANDO EN SOLEDAD",
            "Buscas refugio en un lugar seguro y tratas tus heridas. Estás solo, herido, y contra un ejército. "
            "Pero no es la primera vez que has estado en desventaja. Analizas la situación estratégicamente: "
            "Ra's planea ataques simultáneos. No puedes estar en todos lados. Necesitas coordinar una defensa. "
            "Necesitas aliados. Necesitas que la familia te escuche.",
            "tim_sanando_en_soledad.png"
        )
        tim_dificil_recuperacion.agregar_opcion("Contactar a los Titans", "tim_dificil_ayuda_titans", stat="reputacion", cambio=10)
        tim_dificil_recuperacion.agregar_opcion("Forzar a la Bat-Familia a escuchar", "tim_dificil_forzar_escucha", stat="reputacion", cambio=-5)
        self.historia["tim_dificil_recuperacion"] = tim_dificil_recuperacion

        tim_dificil_proteccion_solitaria = NodoHistoria(
            "tim_dificil_proteccion_solitaria",
            "EL GUARDIÁN SOLITARIO",
            "Decides proteger a la familia solo. Es imposible, lo sabes. Pero eres Red Robin. Has hecho lo "
            "imposible antes. Comienzas a mapear todos los objetivos: Alfred en la Mansión Wayne, Dick y Damian "
            "patrullando, Barbara en su torre, Lucius en Wayne Enterprises. Necesitas estar en cinco lugares "
            "a la vez. Es matemáticamente imposible. Pero tienes que intentarlo.",
            "tim_guardian_solitario.png"
        )
        tim_dificil_proteccion_solitaria.agregar_opcion("Priorizar los objetivos más vulnerables", "tim_dificil_priorizar", stat="recursos", cambio=2)
        tim_dificil_proteccion_solitaria.agregar_opcion("Intentar proteger a todos", "tim_dificil_intentar_todo", stat="salud", cambio=-20)
        self.historia["tim_dificil_proteccion_solitaria"] = tim_dificil_proteccion_solitaria

        tim_dificil_ayuda_titans = NodoHistoria(
            "tim_dificil_ayuda_titans",
            "LOS TITANS RESPONDEN",
            "Contactas a los Teen Titans: Superboy, Wonder Girl, Kid Flash. Ellos no dudan: 'Estamos contigo, "
            "Tim,' dice Conner. 'Siempre.' Les explicas el plan de Ra's. Cassie organiza un equipo táctico. "
            "Bart comienza a mapear rutas. Por primera vez en semanas, no estás solo. Pero aún necesitas "
            "coordinar una defensa perfecta contra la Liga de Asesinos.",
            "tim_titans_responden.png"
        )
        tim_dificil_ayuda_titans.agregar_opcion("Planear la defensa coordinada", "tim_dificil_defensa_coordinada", stat="reputacion", cambio=15)
        self.historia["tim_dificil_ayuda_titans"] = tim_dificil_ayuda_titans

        tim_dificil_presentar_evidencia = NodoHistoria(
            "tim_dificil_presentar_evidencia",
            "EVIDENCIA SOBRE LA MESA",
            "Presentas toda tu evidencia a Barbara: grabaciones, testimonios de ninjas, análisis del plan. "
            "Ella la estudia cuidadosamente. Su expresión se vuelve seria: 'Esto es... esto es real, Tim. "
            "Necesito contactar a Dick inmediatamente.' Finalmente, alguien te cree. Pero Dick tarda en "
            "responder. El tiempo se agota.",
            "tim_evidencia_sobre_la_mesa.png"
        )
        tim_dificil_presentar_evidencia.agregar_opcion("Esperar la respuesta de Dick", "tim_dificil_esperar_dick", stat="recursos", cambio=1)
        tim_dificil_presentar_evidencia.agregar_opcion("Comenzar defensas sin esperar", "tim_dificil_sin_esperar", stat="reputacion", cambio=10)
        self.historia["tim_dificil_presentar_evidencia"] = tim_dificil_presentar_evidencia

        tim_dificil_pedir_confianza_barbara = NodoHistoria(
            "tim_dificil_pedir_confianza_barbara",
    "APELANDO A LA CONFIANZA",
    "'Barbara, hemos trabajado juntos por años. Conoces mi historial. ¿Cuándo te he fallado?' "
    "Ella suspira: 'Nunca, Tim. Pero todos estamos preocupados por ti. Esta obsesión con Bruce...' "
    "'No es obsesión,' interrumpes. 'Es fe. Y necesito que confíes en mí una vez más.' Ella debate "
    "internamente, luego asiente: 'Está bien. ¿Qué necesitas?'",
    "tim_apelando_a_la_confianza.png"
)
        tim_dificil_pedir_confianza_barbara.agregar_opcion("Explicar el plan de defensa", "tim_dificil_explicar_plan", stat="reputacion", cambio=10)
        self.historia["tim_dificil_pedir_confianza_barbara"] = tim_dificil_pedir_confianza_barbara

        tim_dificil_enviar_evidencia = NodoHistoria(
            "tim_dificil_enviar_evidencia",
            "MENSAJE DIGITAL",
            "Envías la grabación y toda tu evidencia a la Bat-Familia digitalmente. Es un archivo masivo "
            "con análisis detallado, líneas de tiempo, todo. Incluyes una nota: 'Sé que no me creen sobre "
            "Bruce. Pero esto es diferente. Ra's al Ghul planea matar a todos. Por favor, implementen "
            "protocolos de seguridad. -Tim' Ahora solo puedes esperar que lo tomen en serio.",
            "tim_mensaje_digital.png"
        )
        tim_dificil_enviar_evidencia.agregar_opcion("Volar a Gotham de todas formas", "tim_dificil_regreso_urgente", stat="recursos", cambio=2)
        self.historia["tim_dificil_enviar_evidencia"] = tim_dificil_enviar_evidencia

        tim_dificil_regreso_urgente = NodoHistoria(
            "tim_dificil_regreso_urgente",
            "VUELO A GOTHAM",
            "Vuelas a Gotham en el primer avión disponible. Durante el vuelo, intentas contactar a todos: "
            "Dick, Barbara, Alfred. Nadie responde. O están ocupados o te están ignorando. El avión parece "
            "moverse demasiado lento. Cada minuto cuenta. Cuando finalmente aterrizas en Gotham, ya es de "
            "noche. La noche del ataque podría ser esta.",
            "tim_vuelo_a_gotham.png"
        )
        tim_dificil_regreso_urgente.agregar_opcion("Ir directo a la Mansión Wayne", "tim_dificil_mansion_wayne", stat="recursos", cambio=2)
        tim_dificil_regreso_urgente.agregar_opcion("Contactar a Barbara primero", "tim_dificil_contacto_barbara", stat="reputacion", cambio=5)
        self.historia["tim_dificil_regreso_urgente"] = tim_dificil_regreso_urgente

        tim_dificil_tratamiento = NodoHistoria(
            "tim_dificil_tratamiento",
            "ATENCIÓN MÉDICA",
            "Buscas atención médica en una clínica discreta que los héroes usan. El doctor te cose y venda. "
            "'Necesitas descansar,' dice. Pero no tienes tiempo para descanso. Tan pronto como puedes moverte, "
            "te marchas. Las heridas duelen, pero la misión es más importante. Tienes que advertir a la familia "
            "antes de que sea demasiado tarde.",
            "tim_atencion_medica.png"
        )
        tim_dificil_tratamiento.agregar_opcion("Continuar la misión", "tim_dificil_continuar_herido", stat="salud", cambio=-5)
        self.historia["tim_dificil_tratamiento"] = tim_dificil_tratamiento

        tim_dificil_ignorar_heridas = NodoHistoria(
            "tim_dificil_ignorar_heridas",
            "DETERMINACIÓN SOBRE SALUD",
            "Ignoras tus heridas y continúas. El dolor es intenso, pero lo has experimentado antes. Bruce te "
            "enseñó a trabajar a través del dolor. Cada movimiento duele, pero no puedes parar. Demasiadas "
            "vidas dependen de ti. Vendar rápidamente las heridas peores y continúas. La adrenalina te mantiene "
            "en movimiento, pero sabes que esto tiene un costo.",
            "tim_determinacion_sobre_salud.png"
        )
        tim_dificil_ignorar_heridas.agregar_opcion("Empujar más allá de los límites", "tim_dificil_mas_alla_limites", stat="salud", cambio=-15)
        self.historia["tim_dificil_ignorar_heridas"] = tim_dificil_ignorar_heridas

        tim_dificil_resistencia_mental = NodoHistoria(
            "tim_dificil_resistencia_mental",
            "FORTALEZA PSICOLÓGICA",
            "Resistes los ataques psicológicos de Ra's. 'Bruce no me abandonó,' dices firmemente. 'Y lo "
            "encontraré. Pero primero, detendré tus planes.' Ra's parece impresionado: 'Tienes la mente del "
            "Detective. Fuerte, inquebrantable. Lástima que estés del lado equivocado.' Eventualmente, te "
            "liberas de sus captores y escapas.",
            "tim_fortaleza_psicologica.png"
        )
        tim_dificil_resistencia_mental.agregar_opcion("Escapar y advertir a la familia", "tim_dificil_escape_advertencia", stat="salud", cambio=-10)
        self.historia["tim_dificil_resistencia_mental"] = tim_dificil_resistencia_mental

        tim_dificil_contraataque_verbal = NodoHistoria(
            "tim_dificil_contraataque_verbal",
            "GUERRA DE PALABRAS",
            "'Dices que Bruce me abandonó,' respondes. 'Pero al menos él inspira lealtad. Tú solo inspiras "
            "miedo. Por eso necesitas un ejército para lograr lo que un hombre con un símbolo logra solo.' "
            "Ra's se ríe genuinamente: 'Ah, tienes su ingenio también. Quizás eres más Detective de lo que "
            "pensé.' Te libera: 'Corre a advertirles. Haz la misión más interesante.'",
            "tim_guerra_de_palabras.png"
        )
        tim_dificil_contraataque_verbal.agregar_opcion("Aprovechar la libertad", "tim_dificil_aprovech ar_libertad", stat="reputacion", cambio=15)
        self.historia["tim_dificil_contraataque_verbal"] = tim_dificil_contraataque_verbal

        tim_dificil_buscar_aliados = NodoHistoria(
            "tim_dificil_buscar_aliados",
            "REUNIENDO FUERZAS",
            "No puedes hacer esto solo. Comienzas a contactar aliados: los Teen Titans, Batgirl (Stephanie "
            "Brown), incluso Red Hood (Jason Todd). La respuesta es mixta. Los Titans están contigo sin "
            "dudarlo. Stephanie está confundida pero dispuesta. Jason se ríe: 'El cerebrito finalmente "
            "acepta que necesita ayuda. Está bien, estoy dentro.'",
            "tim_reuniendo_fuerzas.png"
        )
        tim_dificil_buscar_aliados.agregar_opcion("Organizar el equipo de defensa", "tim_dificil_organizar_equipo", stat="reputacion", cambio=20)
        self.historia["tim_dificil_buscar_aliados"] = tim_dificil_buscar_aliados

        tim_dificil_estrategia_solitaria = NodoHistoria(
            "tim_dificil_estrategia_solitaria",
            "EL PLAN MAESTRO",
            "Te encierras durante horas, planificando. Mapeas cada objetivo de Ra's, cada posible ruta de "
            "ataque, cada activo de la Liga de Asesinos. Es un rompecabezas gigante, y necesitas resolverlo "
            "perfectamente. Comienzas a ver patrones, debilidades en el plan de Ra's. Si puedes anticipar "
            "cada movimiento, podrías coordinarlo todo tú solo. Pero será ajustado.",
            "tim_plan_maestro.png"
        )
        tim_dificil_estrategia_solitaria.agregar_opcion("Implementar el plan solo", "tim_dificil_implementar_solo", stat="recursos", cambio=3)
        self.historia["tim_dificil_estrategia_solitaria"] = tim_dificil_estrategia_solitaria

        tim_dificil_planear_defensa = NodoHistoria(
            "tim_dificil_planear_defensa",
            "ARQUITECTO DE LA DEFENSA",
            "Comienzas a planear una defensa exhaustiva. Identificas todos los objetivos probables: Alfred, "
            "Dick, Damian, Barbara, Lucius, Selina, Jim Gordon. Mapeas las fortalezas y debilidades de cada "
            "ubicación. Necesitas sistemas de seguridad, vigilancia, y respaldo. Es un trabajo masivo para "
            "una persona. Pero empiezas de todos modos.",
            "tim_arquitecto_de_la_defensa.png"
        )
        tim_dificil_planear_defensa.agregar_opcion("Buscar ayuda para implementar", "tim_dificil_buscar_ayuda_implementar", stat="recursos", cambio=2)
        self.historia["tim_dificil_planear_defensa"] = tim_dificil_planear_defensa

        tim_dificil_forzar_escucha = NodoHistoria(
            "tim_dificil_forzar_escucha",
            "IRRUMPIENDO EN LA BATCUEVA",
            "Irrumpes en la Batcueva donde Dick y Damian están entrenando. 'Necesitan escucharme. Ahora.' "
            "Dick se molesta: 'Tim, te pedí que te tomaras tiempo...' 'Ra's al Ghul va a matar a todos,' "
            "interrumpes. 'Esta noche. Y si no me escuchan, su sangre estará en sus manos.' El tono detiene "
            "a Dick. 'Tienes cinco minutos,' dice.",
            "tim_irrumpiendo_en_batcueva.png"
        )
        tim_dificil_forzar_escucha.agregar_opcion("Presentar tu caso rápidamente", "tim_dificil_caso_rapido", stat="reputacion", cambio=5)
        self.historia["tim_dificil_forzar_escucha"] = tim_dificil_forzar_escucha

        # Continuación del modo difícil de Tim Drake - Red Robin
        # Agregar estos nodos después de tim_dificil_priorizar

        tim_dificil_priorizar = NodoHistoria(
            "tim_dificil_priorizar",
            "DECISIONES IMPOSIBLES",
            "Decides priorizar. Alfred es el más vulnerable en la Mansión Wayne. Lucius tiene seguridad "
            "corporativa pero necesita refuerzo. Barbara puede defenderse mejor que la mayoría. Haces "
            "cálculos fríos sobre quién tiene más probabilidades de sobrevivir sin tu ayuda. Son decisiones "
            "que nunca quisiste tomar. Pero alguien tiene que hacerlas.",
            "tim_decisiones_imposibles.png"
        )
        tim_dificil_priorizar.agregar_opcion("Proteger a Alfred primero", "tim_dificil_proteger_alfred", stat="recursos", cambio=2)
        tim_dificil_priorizar.agregar_opcion("Establecer perímetro en Wayne Enterprises", "tim_dificil_wayne_enterprises", stat="recursos", cambio=3)
        self.historia["tim_dificil_priorizar"] = tim_dificil_priorizar

        tim_dificil_intentar_todo = NodoHistoria(
            "tim_dificil_intentar_todo",
            "SOBRECARGA HEROICA",
            "Intentas proteger a todos simultáneamente. Estableces trampas en la Mansión Wayne, luego corres "
            "a Wayne Enterprises, luego a la torre de Barbara. Estás en constante movimiento, agotándote. "
            "Detectas el primer ataque contra Alfred justo a tiempo y lo repeles. Pero mientras lo haces, "
            "los asesinos atacan a Lucius. No puedes estar en dos lugares a la vez. Estás fallando.",
            "tim_sobrecarga_heroica.png"
        )
        tim_dificil_intentar_todo.agregar_opcion("Llamar a los Titans desesperadamente", "tim_dificil_llamada_desesperada", stat="salud", cambio=-15)
        tim_dificil_intentar_todo.agregar_opcion("Continuar solo y esperar lo mejor", "tim_dificil_game_over", stat="salud", cambio=-30)
        self.historia["tim_dificil_intentar_todo"] = tim_dificil_intentar_todo

        tim_dificil_defensa_coordinada = NodoHistoria(
            "tim_dificil_defensa_coordinada",
            "EL TABLERO DE AJEDREZ",
            "Con los Titans a tu lado, organizas una defensa perfecta. Superboy protege a Alfred. Wonder Girl "
            "está con Lucius. Kid Flash patrulla múltiples ubicaciones a velocidad. Tú coordinas todo desde "
            "un centro de comando móvil, monitoreando cada objetivo. Cuando la Liga de Asesinos ataca, están "
            "listos. Cada ninja es interceptado. Es una ejecución táctica perfecta.",
            "tim_tablero_de_ajedrez.png"
        )
        tim_dificil_defensa_coordinada.agregar_opcion("Enfrentar a Ra's personalmente", "tim_dificil_enfrentamiento_ras", stat="reputacion", cambio=20)
        self.historia["tim_dificil_defensa_coordinada"] = tim_dificil_defensa_coordinada

        tim_dificil_esperar_dick = NodoHistoria(
            "tim_dificil_esperar_dick",
            "EL RELOJ CORRE",
            "Esperas la respuesta de Dick, pero los minutos se convierten en horas. Finalmente, te contacta: "
            "'Tim, revisé tu evidencia. Es... convincente. Estoy implementando protocolos de seguridad ahora.' "
            "Pero ha pasado demasiado tiempo. Los asesinos ya están en posición. Necesitas coordinar con Dick "
            "rápidamente o algunos objetivos quedarán desprotegidos.",
            "tim_reloj_corre.png"
        )
        tim_dificil_esperar_dick.agregar_opcion("Coordinar con Dick", "tim_dificil_coordinacion_dick", stat="reputacion", cambio=15)
        self.historia["tim_dificil_esperar_dick"] = tim_dificil_esperar_dick

        tim_dificil_sin_esperar = NodoHistoria(
            "tim_dificil_sin_esperar",
            "ACCIÓN INMEDIATA",
            "No esperas la aprobación de Dick. Comienzas a implementar defensas inmediatamente con la ayuda "
            "de Barbara. Ella coordina con los contactos de GCPD para proteger a Jim Gordon. Tú estableces "
            "sistemas de seguridad en la Mansión Wayne. Cuando Dick finalmente responde, ya has hecho el "
            "trabajo pesado. 'Debiste confiar en mí desde el principio,' le dices.",
            "tim_accion_inmediata.png"
        )
        tim_dificil_sin_esperar.agregar_opcion("Preparar la confrontación final", "tim_dificil_preparacion_final", stat="reputacion", cambio=10)
        self.historia["tim_dificil_sin_esperar"] = tim_dificil_sin_esperar

        tim_dificil_explicar_plan = NodoHistoria(
            "tim_dificil_explicar_plan",
            "LA ESTRATEGIA REVELADA",
            "Le explicas tu plan completo a Barbara: 'Ra's atacará simultáneamente. Necesitamos dividir "
            "recursos. Titans aquí, Bat-Familia allá. Yo coordinaré desde el centro.' Barbara analiza el "
            "plan: 'Es brillante, Tim. Complejo, pero factible. Necesitaré convencer a Dick rápidamente.' "
            "Juntos, presentan el plan a la familia. Esta vez, Dick escucha.",
            "tim_estrategia_revelada.png"
        )
        tim_dificil_explicar_plan.agregar_opcion("Implementar con el apoyo familiar", "tim_dificil_apoyo_familiar", stat="reputacion", cambio=20)
        self.historia["tim_dificil_explicar_plan"] = tim_dificil_explicar_plan

        tim_dificil_mansion_wayne = NodoHistoria(
            "tim_dificil_mansion_wayne",
            "REGRESO A CASA",
            "Llegas a la Mansión Wayne. Alfred te recibe: 'Master Timothy, ha regresado.' Le adviertes del "
            "peligro inminente. Alfred simplemente asiente: 'Entonces debemos prepararnos.' Juntos, activan "
            "los sistemas de defensa de la mansión que Bruce instaló. Pero sabes que no será suficiente contra "
            "toda la Liga de Asesinos. Necesitas más ayuda.",
            "tim_regreso_a_casa.png"
)
        tim_dificil_mansion_wayne.agregar_opcion("Fortificar la mansión", "tim_dificil_fortificar", stat="recursos", cambio=3)
        tim_dificil_mansion_wayne.agregar_opcion("Evacuar a Alfred", "tim_dificil_evacuar_alfred", stat="recursos", cambio=2)
        self.historia["tim_dificil_mansion_wayne"] = tim_dificil_mansion_wayne

        tim_dificil_contacto_barbara = NodoHistoria(
            "tim_dificil_contacto_barbara",
            "LA ALIANZA CON ORACLE",
            "Contactas a Barbara (Oracle) desde el aeropuerto. Ella responde inmediatamente: 'Tim, recibí "
            "tu archivo. Lo he estado analizando. Es... preocupante.' '¿Me crees?' preguntas. 'Sí,' dice "
            "simplemente. 'Necesitamos coordinar. Ven a mi torre.' Finalmente, tienes un aliado en Gotham.",
            "tim_alianza_con_oracle.png"
        )
        tim_dificil_contacto_barbara.agregar_opcion("Ir a la torre de Barbara", "tim_dificil_torre_barbara", stat="reputacion", cambio=10)
        self.historia["tim_dificil_contacto_barbara"] = tim_dificil_contacto_barbara

        tim_dificil_continuar_herido = NodoHistoria(
            "tim_dificil_continuar_herido",
            "HERIDO PERO DECIDIDO",
            "Continúas tu misión a pesar de las heridas. Cada movimiento duele, pero el dolor te mantiene "
            "enfocado. Logras llegar a Gotham y comenzar las defensas, aunque tu efectividad está disminuida. "
            "Durante una confrontación con ninjas, tus heridas casi te cuestan la vida. Superboy llega justo "
            "a tiempo para salvarte. 'Tim, necesitas descansar,' dice. 'Después,' respondes.",
            "tim_herido_pero_decidido.png"
        )
        tim_dificil_continuar_herido.agregar_opcion("Aceptar ayuda médica de Superboy", "tim_dificil_ayuda_medica", stat="salud", cambio=10)
        self.historia["tim_dificil_continuar_herido"] = tim_dificil_continuar_herido

        tim_dificil_mas_alla_limites = NodoHistoria(
            "tim_dificil_mas_alla_limites",
            "LÍMITES ROTOS",
            "Empujas tu cuerpo más allá de todo límite razonable. La adrenalina y la determinación pura te "
            "mantienen en movimiento. Logras establecer defensas básicas, pero tu cuerpo finalmente colapsa. "
            "Te despiertas en la enfermería de los Titans con Superboy y Wonder Girl mirándote preocupados. "
            "'Casi mueres, Tim,' dice Cassie. 'Valió la pena,' murmuras. 'La familia está a salvo.'",
            "tim_limites_rotos.png"
        )
        tim_dificil_mas_alla_limites.agregar_opcion("Recuperarte con los Titans", "tim_dificil_recuperacion_titans", stat="salud", cambio=15)
        self.historia["tim_dificil_mas_alla_limites"] = tim_dificil_mas_alla_limites

        tim_dificil_escape_advertencia = NodoHistoria(
            "tim_dificil_escape_advertencia",
            "ESCAPE CON PROPÓSITO",
            "Escapas de Ra's con información vital sobre sus planes y cronograma. Ahora sabes exactamente "
            "cuándo atacará: en 48 horas. Es tiempo suficiente para preparar defensas si actúas rápido. "
            "Contactas a todos tus aliados, esta vez con detalles específicos que hacen tu advertencia "
            "imposible de ignorar. La carrera contra el tiempo ha comenzado.",
            "tim_escape_con_proposito.png"
        )
        tim_dificil_escape_advertencia.agregar_opcion("Organizar la defensa final", "tim_dificil_defensa_final", stat="recursos", cambio=3)
        self.historia["tim_dificil_escape_advertencia"] = tim_dificil_escape_advertencia

        tim_dificil_aprovechar_libertad = NodoHistoria(
            "tim_dificil_aprovechar_libertad",
            "LIBERTAD TÁCTICA",
            "Ra's te dejó ir deliberadamente, confiando en que harás la misión más interesante. Aprovechas "
            "esta libertad para preparar una trampa elaborada. Si Ra's quiere un desafío, lo tendrá. Pero "
            "será un desafío diseñado específicamente para exponer cada debilidad en su plan. Comienzas a "
            "contactar no solo a la Bat-Familia, sino a toda la comunidad de héroes de Gotham.",
            "tim_libertad_tactica.png"
        )
        tim_dificil_aprovechar_libertad.agregar_opcion("Construir una red de defensores", "tim_dificil_red_defensores", stat="reputacion", cambio=15)
        self.historia["tim_dificil_aprovechar_libertad"] = tim_dificil_aprovechar_libertad

        tim_dificil_organizar_equipo = NodoHistoria(
            "tim_dificil_organizar_equipo",
            "EL LÍDER EMERGE",
            "Organizas tu equipo como un general preparando para batalla. Superboy tiene fuerza bruta para "
            "proteger objetivos clave. Wonder Girl tiene habilidad de combate para enfrentar asesinos elite. "
            "Kid Flash tiene velocidad para responder a múltiples amenazas. Red Hood tiene la crueldad necesaria "
            "para luchar contra la Liga. Y tú tienes el cerebro para coordinar todo. 'Así es como se hace,' "
            "piensas. 'Con amigos.'",
            "tim_lider_emerge.png"
        )
        tim_dificil_organizar_equipo.agregar_opcion("Ejecutar el plan de defensa", "tim_dificil_ejecucion_plan", stat="reputacion", cambio=20)
        self.historia["tim_dificil_organizar_equipo"] = tim_dificil_organizar_equipo

        tim_dificil_implementar_solo = NodoHistoria(
            "tim_dificil_implementar_solo",
            "EL LOBO SOLITARIO",
            "Intentas implementar tu plan solo, pero rápidamente te das cuenta de la imposibilidad. Estás "
            "estableciendo defensas en la Mansión Wayne cuando recibes alerta de un ataque en Wayne Enterprises. "
            "Corres allí, pero entonces Barbara informa de asesinos en su torre. No puedes estar en todos "
            "lados. Estás fallando, y lo sabes. Necesitas ayuda, pero tu orgullo te lo impide.",
            "tim_lobo_solitario.png"
        )
        tim_dificil_implementar_solo.agregar_opcion("Tragarte el orgullo y pedir ayuda", "tim_dificil_pedir_ayuda_final", stat="reputacion", cambio=10)
        tim_dificil_implementar_solo.agregar_opcion("Continuar solo hasta el colapso", "tim_dificil_colapso", stat="salud", cambio=-25)
        self.historia["tim_dificil_implementar_solo"] = tim_dificil_implementar_solo

        tim_dificil_buscar_ayuda_implementar = NodoHistoria(
            "tim_dificil_buscar_ayuda_implementar",
            "HUMILDAD Y SABIDURÍA",
            "Reconoces que necesitas ayuda. Contactas a Stephanie Brown (Batgirl): '¿Recuerdas cuando me "
            "dijiste que mi problema es que pienso que puedo hacer todo solo? Tenías razón. Necesito ayuda.' "
            "Ella responde inmediatamente: 'Estoy en camino.' Luego contactas a Cassie, Conner, Bart. Todos "
            "responden. Esta vez, no estás solo.",
            "tim_humildad_sabiduria.png"
        )
        tim_dificil_buscar_ayuda_implementar.agregar_opcion("Coordinar el equipo completo", "tim_dificil_coordinacion_completa", stat="reputacion", cambio=20)
        self.historia["tim_dificil_buscar_ayuda_implementar"] = tim_dificil_buscar_ayuda_implementar

        tim_dificil_caso_rapido = NodoHistoria(
            "tim_dificil_caso_rapido",
            "CINCO MINUTOS PARA CONVENCER",
            "Presentas tu caso con precisión quirúrgica: 'Ra's al Ghul está en Europa. Confirmé su presencia. "
            "Planea ataques simultáneos contra ocho objetivos esta noche. Alfred, Barbara, Lucius, Commissioner "
            "Gordon, Selina, y ustedes dos. Tengo evidencia, testimonios, y un cronograma. ¿Van a escuchar "
            "o van a arriesgar vidas por orgullo?' El silencio es tenso. Dick mira la evidencia.",
            "tim_cinco_minutos.png"
        )
        tim_dificil_caso_rapido.agregar_opcion("Esperar el veredicto de Dick", "tim_dificil_veredicto_dick", stat="reputacion", cambio=5)
        self.historia["tim_dificil_caso_rapido"] = tim_dificil_caso_rapido

        tim_dificil_proteger_alfred = NodoHistoria(
            "tim_dificil_proteger_alfred",
            "EL CORAZÓN DE LA FAMILIA",
            "Priorizas a Alfred porque él es el corazón de la Bat-Familia. Sin él, la familia se desmorona. "
            "Estableces defensas elaboradas en la Mansión Wayne. Cuando los ninjas atacan, están listos para "
            "una mansión desprotegida. En su lugar, encuentran trampas, sistemas de seguridad militares, y "
            "un Red Robin muy motivado. Repeles el ataque, pero escuchas de ataques en otros lugares.",
            "tim_corazon_familia.png"
        )
        tim_dificil_proteger_alfred.agregar_opcion("Responder a otros ataques", "tim_dificil_respuesta_multiple", stat="salud", cambio=-10)
        self.historia["tim_dificil_proteger_alfred"] = tim_dificil_proteger_alfred

        tim_dificil_wayne_enterprises = NodoHistoria(
            "tim_dificil_wayne_enterprises",
            "PROTEGIENDO EL LEGADO",
            "Estableces perímetro en Wayne Enterprises. Lucius Fox te recibe: 'Mr. Drake, me alegra verlo.' "
            "Le explicas la situación. Lucius, pragmático como siempre, activa protocolos de seguridad "
            "corporativos y te da acceso a tecnología de Wayne Enterprises. Juntos, convierten el edificio "
            "en una fortaleza. Cuando los ninjas atacan, no están preparados para la tecnología de Batman.",
            "tim_protegiendo_legado.png"
        )
        tim_dificil_wayne_enterprises.agregar_opcion("Defender el edificio", "tim_dificil_defensa_edificio", stat="recursos", cambio=3)
        self.historia["tim_dificil_wayne_enterprises"] = tim_dificil_wayne_enterprises

        tim_dificil_llamada_desesperada = NodoHistoria(
            "tim_dificil_llamada_desesperada",
            "S.O.S.",
            "Haces una llamada desesperada a los Titans: 'Necesito ayuda. Ahora. Múltiples ubicaciones en "
            "Gotham bajo ataque.' Superboy responde: 'En camino.' Wonder Girl: 'Dos minutos.' Kid Flash: "
            "'Ya estoy ahí.' Tus amigos llegan como la caballería. Juntos, logran repeler los ataques y "
            "salvar a todos. Después, Conner te abraza: 'Siempre pide ayuda más temprano, Tim.'",
            "tim_sos.png"
        )
        tim_dificil_llamada_desesperada.agregar_opcion("Enfrentar a Ra's con respaldo", "tim_dificil_respaldo_titans", stat="reputacion", cambio=15)
        self.historia["tim_dificil_llamada_desesperada"] = tim_dificil_llamada_desesperada

        tim_dificil_game_over = NodoHistoria(
            "tim_dificil_game_over",
            "GAME OVER: EL PRECIO DEL ORGULLO",
            "Intentas hacerlo todo solo. Es demasiado. Los ataques vienen simultáneamente. Salvas a Alfred "
            "pero Lucius es herido gravemente. Proteges Wayne Enterprises pero los asesinos llegan a la torre "
            "de Barbara. Cada éxito viene con una falla en otro lugar. Cuando el polvo se asienta, has salvado "
            "algunas vidas pero perdido otras. Dick te confronta: 'Si hubieras pedido ayuda desde el principio...' "
            "No puede terminar la oración. Has fallado. La lección es clara: ningún héroe puede hacerlo todo solo.",
            "tim_game_over_orgullo.png"
        )
        # Este es un final malo sin opciones adicionales
        self.historia["tim_dificil_game_over"] = tim_dificil_game_over

        tim_dificil_enfrentamiento_ras = NodoHistoria(
            "tim_dificil_enfrentamiento_ras",
            "EL DETECTIVE VS EL DEMONIO",
            "Con todos los objetivos protegidos, confrontas a Ra's al Ghul personalmente. Él te espera en "
            "un edificio abandonado, rodeado de sus ninjas derrotados. 'Impresionante, Timothy Drake,' dice. "
            "'Anticipaste cada movimiento. Protegiste a todos. Coordinaste recursos perfectamente. Dime, "
            "¿cómo lo lograste?' Sonríes: 'Simple. Hice algo que tú nunca harías. Pedí ayuda.'",
            "tim_detective_vs_demonio.png"
        )
        tim_dificil_enfrentamiento_ras.agregar_opcion("Duelar con Ra's", "tim_dificil_duelo_final", stat="salud", cambio=-15)
        tim_dificil_enfrentamiento_ras.agregar_opcion("Revelación estratégica", "tim_dificil_revelacion", stat="reputacion", cambio=25)
        self.historia["tim_dificil_enfrentamiento_ras"] = tim_dificil_enfrentamiento_ras

        tim_dificil_coordinacion_dick = NodoHistoria(
            "tim_dificil_coordinacion_dick",
            "FAMILIA UNIDA",
            "Coordinas con Dick, quien finalmente confía en ti. 'Tim, lamento no haberte creído antes,' "
            "dice. 'Pero ahora estamos juntos en esto.' Trabajan como la perfecta máquina que son: Dick y "
            "Damian protegen el lado este de Gotham, tú y los Titans el oeste. Barbara coordina desde su "
            "torre. Es la Bat-Familia operando a máxima capacidad. Los asesinos no tienen oportunidad.",
            "tim_familia_unida.png"
        )
        tim_dificil_coordinacion_dick.agregar_opcion("Victoria familiar", "tim_dificil_victoria_familiar", stat="reputacion", cambio=25)
        self.historia["tim_dificil_coordinacion_dick"] = tim_dificil_coordinacion_dick

        tim_dificil_preparacion_final = NodoHistoria(
            "tim_dificil_preparacion_final",
            "LA CALMA ANTES DE LA TORMENTA",
            "Has preparado todo lo que puedes. Sistemas de seguridad, equipos coordinados, planes de contingencia. "
            "Ahora solo esperas. Alfred te sirve té: 'Master Timothy, independientemente del resultado, sepa "
            "que el Maestro Bruce estaría orgulloso.' Esas palabras te dan fuerza. Cuando los asesinos finalmente "
            "atacan, están caminando hacia una trampa perfectamente preparada.",
            "tim_calma_antes_tormenta.png"
        )
        tim_dificil_preparacion_final.agregar_opcion("Ejecutar la defensa perfecta", "tim_dificil_defensa_perfecta", stat="reputacion", cambio=20)
        self.historia["tim_dificil_preparacion_final"] = tim_dificil_preparacion_final

        tim_dificil_apoyo_familiar = NodoHistoria(
            "tim_dificil_apoyo_familiar",
            "REDENCIÓN Y RESPETO",
            "Con el apoyo de la Bat-Familia completa, implementan tu plan perfectamente. Dick se disculpa: "
            "'Tim, debí confiar en ti desde el principio. Eres un Detective, como Bruce.' Damian incluso "
            "gruñe una aprobación. Barbara coordina magistralmente. Cuando Ra's ataca, encuentra no solo "
            "resistencia sino una familia unida que anticipó cada movimiento. Es tu momento de triunfo.",
            "tim_redencion_respeto.png"
        )
        tim_dificil_apoyo_familiar.agregar_opcion("Confrontación final con Ra's", "tim_dificil_confrontacion_final", stat="reputacion", cambio=30)
        self.historia["tim_dificil_apoyo_familiar"] = tim_dificil_apoyo_familiar

        # Continuaré con más nodos...

        tim_dificil_fortificar = NodoHistoria(
            "tim_dificil_fortificar",
            "FORTALEZA WAYNE",
            "Trabajas con Alfred para convertir la Mansión Wayne en una fortaleza impenetrable. Activan "
            "sistemas de defensa que Bruce instaló para exactamente este tipo de situación. Sensores perimetrales, "
            "barreras reforzadas, rutas de escape secretas. Alfred comenta: 'El Maestro Bruce siempre planeaba "
            "para lo peor.' La mansión está lista. Ahora solo falta esperar a los asesinos.",
            "tim_fortaleza_wayne.png"
        )
        tim_dificil_fortificar.agregar_opcion("Emboscar a los atacantes", "tim_dificil_emboscada", stat="recursos", cambio=3)
        self.historia["tim_dificil_fortificar"] = tim_dificil_fortificar

        tim_dificil_evacuar_alfred = NodoHistoria(
            "tim_dificil_evacuar_alfred",
            "LA EVACUACIÓN",
            "Decides que la mejor defensa es evacuar a Alfred a una ubicación segura. Él protesta: 'Master "
            "Timothy, no abandonaré la casa Wayne.' 'No es abandono, Alfred. Es estrategia,' respondes. "
            "Lo llevas a un refugio seguro que solo tú conoces, luego regresas para enfrentar a los asesinos "
            "en tus propios términos. Sin rehenes, tienes más libertad táctica.",
            "tim_evacuacion_alfred.png"
        )
        tim_dificil_evacuar_alfred.agregar_opcion("Regresar y tender trampa", "tim_dificil_trampa_mansion", stat="recursos", cambio=2)
        self.historia["tim_dificil_evacuar_alfred"] = tim_dificil_evacuar_alfred

        tim_dificil_torre_barbara = NodoHistoria(
            "tim_dificil_torre_barbara",
            "CENTRO DE OPERACIONES",
            "La torre de Barbara se convierte en tu centro de operaciones. Ella tiene sistemas de vigilancia "
            "de toda la ciudad. Juntos, mapean cada ubicación de la Liga de Asesinos en Gotham. 'Son más "
            "de los que pensábamos,' dice Barbara. 'Ra's trajo un ejército.' Pero con información completa, "
            "pueden planear defensas precisas. Es ventaja del detective sobre fuerza bruta.",
            "tim_centro_operaciones.png"
        )
        tim_dificil_torre_barbara.agregar_opcion("Coordinar defensa desde la torre", "tim_dificil_comando_central", stat="reputacion", cambio=15)
        self.historia["tim_dificil_torre_barbara"] = tim_dificil_torre_barbara

        tim_dificil_ayuda_medica = NodoHistoria(
            "tim_dificil_ayuda_medica",
            "SANANDO CON AMIGOS",
            "Aceptas la ayuda médica de Superboy, quien te lleva a la enfermería de los Titans. Wonder Girl "
            "trata tus heridas mientras Bart hace guardia. 'No puedes salvar a nadie si estás muerto,' dice "
            "Cassie. Tienes razón. En pocas horas, estás recuperado lo suficiente para continuar. Y esta vez, "
            "no estarás solo. Los Titans insisten en ayudarte.",
            "tim_sanando_con_amigos.png"
        )
        tim_dificil_ayuda_medica.agregar_opcion("Regresar a la misión con los Titans", "tim_dificil_mision_titans", stat="salud", cambio=15)
        self.historia["tim_dificil_ayuda_medica"] = tim_dificil_ayuda_medica

        tim_dificil_recuperacion_titans = NodoHistoria(
            "tim_dificil_recuperacion_titans",
            "LECCIONES APRENDIDAS",
            "Te recuperas rodeado de los Titans. Conner te dice: 'Tim, eres el cerebro del equipo. Pero "
            "incluso el cerebro necesita un cuerpo funcional.' Cassie añade: 'Y no puedes hacer todo solo. "
            "Por eso tenemos un equipo.' Es una lección que Bruce nunca aprendió completamente. Pero tú sí. "
            "Cuando estás recuperado, regresas a Gotham con un ejército de amigos.",
            "tim_lecciones_aprendidas.png"
        )
        tim_dificil_recuperacion_titans.agregar_opcion("Liderar a los Titans en Gotham", "tim_dificil_liderar_titans", stat="reputacion", cambio=20)
        self.historia["tim_dificil_recuperacion_titans"] = tim_dificil_recuperacion_titans

        tim_dificil_defensa_final = NodoHistoria(
            "tim_dificil_defensa_final",
            "LA NOCHE DEL ASEDIO",
            "La noche del ataque llega. Has preparado todo: cada objetivo protegido, cada aliado en posición, "
            "cada contingencia planeada. Cuando los asesinos atacan simultáneamente, encuentran resistencia "
            "coordinada en cada ubicación. Superboy repele el ataque a Alfred. Wonder Girl protege a Lucius. "
            "Kid Flash evacúa a Gordon. Y tú coordinas todo, anticipando cada movimiento de Ra's.",
            "tim_noche_del_asedio.png"
        )
        tim_dificil_defensa_final.agregar_opcion("Buscar a Ra's durante el caos", "tim_dificil_buscar_ras", stat="recursos", cambio=3)
        self.historia["tim_dificil_defensa_final"] = tim_dificil_defensa_final

        tim_dificil_red_defensores = NodoHistoria(
            "tim_dificil_red_defensores",
            "LA RED SE EXTIENDE",
            "No te limitas a la Bat-Familia. Contactas a Huntress, Black Canary, Question, y otros héroes "
            "de Gotham. Explicas la situación y cada uno acepta proteger un objetivo. Ra's planeaba atacar "
            "una ciudad dividida. En su lugar, encuentra una comunidad de héroes unida. 'Esto es lo que "
            "Bruce construyó,' piensas. 'No solo un símbolo, sino una red.'",
            "tim_red_defensores.png"
        )
        tim_dificil_red_defensores.agregar_opcion("Coordinar la red completa", "tim_dificil_coordinacion_total", stat="reputacion", cambio=25)
        self.historia["tim_dificil_red_defensores"] = tim_dificil_red_defensores

        tim_dificil_ejecucion_plan = NodoHistoria(
            "tim_dificil_ejecucion_plan",
            "EJECUCIÓN PERFECTA",
            "El plan se ejecuta como un reloj suizo. Cada miembro del equipo cumple su rol perfectamente. "
            "Los asesinos son repelidos en cada ubicación antes de que puedan causar daño real. Ra's observa "
            "desde la distancia, su plan desmoronándose. Envía un mensaje: 'Bien jugado, Detective. Pero "
            "esto no ha terminado.' Has ganado esta batalla, pero la guerra continúa.",
            "tim_ejecucion_perfecta.png"
        )
        tim_dificil_ejecucion_plan.agregar_opcion("Rastrear a Ra's", "tim_dificil_rastrear_ras", stat="recursos", cambio=3)
        self.historia["tim_dificil_ejecucion_plan"] = tim_dificil_ejecucion_plan

        tim_dificil_pedir_ayuda_final = NodoHistoria(
            "tim_dificil_pedir_ayuda_final",
            "TRAGANDO ORGULLO",
            "Te tragas el orgullo y haces las llamadas. 'Superboy, Wonder Girl, Kid Flash, los necesito. "
            "Ahora.' La respuesta es inmediata y sin dudas. 'En camino,' dice Conner. En minutos, tu equipo "
            "está contigo. Juntos, coordinan una defensa que convierte tu plan imposible en ejecutable. "
            "Has aprendido la lección más importante: pedir ayuda no es debilidad, es sabiduría.",
            "tim_tragando_orgullo.png"
        )
        tim_dificil_pedir_ayuda_final.agregar_opcion("Defender juntos", "tim_dificil_defensa_equipo", stat="reputacion", cambio=20)
        self.historia["tim_dificil_pedir_ayuda_final"] = tim_dificil_pedir_ayuda_final

        tim_dificil_colapso = NodoHistoria(
            "tim_dificil_colapso",
            "EL COLAPSO INEVITABLE",
            "Te niegas a pedir ayuda hasta que es demasiado tarde. Tu cuerpo finalmente colapsa por agotamiento "
            "y heridas. Los Titans te encuentran inconsciente rodeado de ninjas derrotados. Salvaste algunos "
            "objetivos, pero otros fueron alcanzados. Cuando despiertas en el hospital, Dick está ahí: 'Tim, "
            "casi mueres. Y por qué? Por orgullo?' No tienes respuesta. Has aprendido una lección dolorosa.",
            "tim_colapso_inevitable.png"
        )
        tim_dificil_colapso.agregar_opcion("Enfrentar las consecuencias", "tim_dificil_consecuencias", stat="reputacion", cambio=-20)
        self.historia["tim_dificil_colapso"] = tim_dificil_colapso

        tim_dificil_coordinacion_completa = NodoHistoria(
            "tim_dificil_coordinacion_completa",
            "EL COORDINADOR MAESTRO",
            "Coordinas el equipo completo con precisión militar. Cada persona sabe exactamente dónde estar "
            "y cuándo. Estableces canales de comunicación, protocolos de emergencia, y rutas de evacuación. "
            "Cuando Barbara ve tu plan completo, dice: 'Tim, esto es... esto es trabajo de Batman. Nivel "
            "de Batman.' Es el mayor cumplido que podrías recibir.",
            "tim_coordinador_maestro.png"
        )
        tim_dificil_coordinacion_completa.agregar_opcion("Ejecutar la operación", "tim_dificil_operacion_perfecta", stat="reputacion", cambio=25)
        self.historia["tim_dificil_coordinacion_completa"] = tim_dificil_coordinacion_completa

        tim_dificil_veredicto_dick = NodoHistoria(
            "tim_dificil_veredicto_dick",
            "EL VEREDICTO",
            "Dick estudia tu evidencia en silencio. Damian comenta: 'Es circunstancial en el mejor de los "
            "casos.' Pero Dick levanta una mano silenciándolo. Finalmente dice: 'Tim, tu evidencia es sólida. "
            "Y más importante, confío en tu instinto. Si dices que Ra's planea esto, te creo. ¿Qué necesitas?' "
            "La validación llega como una ola de alivio. Finalmente, no estás solo.",
            "tim_veredicto_dick.png"
        )
        tim_dificil_veredicto_dick.agregar_opcion("Planear defensa conjunta", "tim_dificil_defensa_conjunta", stat="reputacion", cambio=20)
        self.historia["tim_dificil_veredicto_dick"] = tim_dificil_veredicto_dick

        tim_dificil_respuesta_multiple = NodoHistoria(
            "tim_dificil_respuesta_multiple",
            "DIVIDIDO Y DÉBIL",
            "Intentas responder a múltiples ataques, corriendo de ubicación en ubicación. Salvas a uno, "
            "pero mientras lo haces, otro es atacado. Es una batalla perdida. Finalmente, exhausto y herido, "
            "te das cuenta de que necesitas ayuda. Haces la llamada a los Titans. Llegan rápidamente y "
            "juntos logran estabilizar la situación, pero ha habido bajas. Aprendes que ser héroe también "
            "significa saber cuándo pedir refuerzos.",
            "tim_respuesta_multiple.png"
        )
        tim_dificil_respuesta_multiple.agregar_opcion("Reagrupar con los Titans", "tim_dificil_reagrupar", stat="salud", cambio=-15)
        self.historia["tim_dificil_respuesta_multiple"] = tim_dificil_respuesta_multiple

        tim_dificil_defensa_edificio = NodoHistoria(
            "tim_dificil_defensa_edificio",
            "FORTALEZA CORPORATIVA",
            "Wayne Enterprises se convierte en un campo de batalla. Los ninjas infiltran el edificio por "
            "múltiples puntos, pero tú y Lucius han preparado cada piso con defensas. Usas gadgets de Batman, "
            "tecnología experimental, y tu propio ingenio. La batalla es brutal pero la ganas. Cuando el "
            "último ninja cae, Lucius dice: 'Mr. Drake, definitivamente es digno del apellido Wayne.'",
            "tim_fortaleza_corporativa.png"
        )
        tim_dificil_defensa_edificio.agregar_opcion("Asegurar el edificio y moverse", "tim_dificil_asegurar_moverse", stat="recursos", cambio=2)
        self.historia["tim_dificil_defensa_edificio"] = tim_dificil_defensa_edificio

        tim_dificil_respaldo_titans = NodoHistoria(
            "tim_dificil_respaldo_titans",
            "CON RESPALDO",
            "Con los Titans respaldándote, confrontas a Ra's al Ghul. Él está en un almacén con sus ninjas "
            "elite restantes. 'Trajiste amigos,' observa Ra's. 'Qué... inesperado.' Sonríes: 'Es la diferencia "
            "entre tú y yo, Ra's. Tú inspiras miedo. Yo inspiro lealtad. Por eso mis amigos están aquí por "
            "elección, mientras los tuyos están aquí por obligación.'",
            "tim_con_respaldo.png"
        )
        tim_dificil_respaldo_titans.agregar_opcion("Batalla final con respaldo", "tim_dificil_batalla_respaldo", stat="salud", cambio=-10)
        self.historia["tim_dificil_respaldo_titans"] = tim_dificil_respaldo_titans

        tim_dificil_duelo_final = NodoHistoria(
            "tim_dificil_duelo_final",
            "EL DUELO DEL DETECTIVE",
            "Aceptas el duelo con Ra's. Sabes que es superior físicamente, pero tienes ventajas que él no "
            "espera. Durante la pelea, usas cada truco que Bruce te enseñó. No intentas superarlo en fuerza "
            "o velocidad. En su lugar, lo superas en estrategia, anticipando sus movimientos, usando el "
            "ambiente a tu favor. La batalla es larga y brutal, pero eventualmente, Ra's retrocede.",
            "tim_duelo_del_detective.png"
        )
        tim_dificil_duelo_final.agregar_opcion("Momento de verdad con Ra's", "tim_dificil_momento_verdad", stat="salud", cambio=-20)
        self.historia["tim_dificil_duelo_final"] = tim_dificil_duelo_final

        tim_dificil_revelacion = NodoHistoria(
            "tim_dificil_revelacion",
            "LA REVELACIÓN ESTRATÉGICA",
            "'Quieres saber cómo te derroté?' preguntas a Ra's. 'No fue con puños. Fue con esto.' Muestras "
            "documentos: transferencias legales que Lucius completó mientras Ra's estaba distraído. Wayne "
            "Enterprises ahora está legalmente protegida bajo tu nombre temporalmente. 'No puedes robar lo "
            "que no puedes tocar legalmente. Y mientras planeabas asesinatos, yo jugaba ajedrez corporativo.'",
            "tim_revelacion_estrategica.png"
        )
        tim_dificil_revelacion.agregar_opcion("La reacción de Ra's", "tim_dificil_reaccion_ras", stat="reputacion", cambio=30)
        self.historia["tim_dificil_revelacion"] = tim_dificil_revelacion

        tim_dificil_victoria_familiar = NodoHistoria(
            "tim_dificil_victoria_familiar",
            "VICTORIA EN FAMILIA",
            "Con la Bat-Familia unida, los ataques de Ra's fallan completamente. Cada objetivo está protegido. "
            "Cada asesino es capturado o repelido. Al final de la noche, la familia se reúne en la Batcueva. "
            "Dick te abraza: 'Tim, salvaste a todos. Lo siento por no haber confiado en ti antes.' Damian "
            "incluso ofrece un respeto gruñido. Alfred sirve té: 'El Maestro Bruce estaría orgulloso.'",
            "tim_victoria_familiar.png"
        )
        tim_dificil_victoria_familiar.agregar_opcion("Momento de reconciliación", "tim_dificil_reconciliacion", stat="reputacion", cambio=30)
        self.historia["tim_dificil_victoria_familiar"] = tim_dificil_victoria_familiar

        tim_dificil_defensa_perfecta = NodoHistoria(
            "tim_dificil_defensa_perfecta",
            "DEFENSA IMPECABLE",
            "Tu defensa es perfecta. Cada ataque es anticipado y neutralizado. Los ninjas se retiran en "
            "confusión cuando cada plan falla. Barbara te contacta: 'Tim, acabas de coordinar la operación "
            "defensiva más compleja que he visto. Y funcionó perfectamente.' Has demostrado que eres más "
            "que Robin. Eres un estratega maestro por derecho propio.",
            "tim_defensa_impecable.png"
        )
        tim_dificil_defensa_perfecta.agregar_opcion("Confrontar a Ra's victorioso", "tim_dificil_confrontacion_victoriosa", stat="reputacion", cambio=25)
        self.historia["tim_dificil_defensa_perfecta"] = tim_dificil_defensa_perfecta

        tim_dificil_confrontacion_final = NodoHistoria(
            "tim_dificil_confrontacion_final",
            "FRENTE AL DEMONIO DERROTADO",
            "Encuentras a Ra's en su punto de retirada. Su plan ha fallado completamente. Te mira con una "
            "mezcla de respeto y frustración: 'Timothy Drake. Subestimé no tu habilidad, sino tu capacidad "
            "de inspirar lealtad. El Detective te enseñó bien.' Haces una pausa. 'Ra's, tú y yo sabemos que "
            "Bruce está vivo. ¿Por qué atacar su legado si crees que regresará?'",
            "tim_confrontacion_final.png"
        )
        tim_dificil_confrontacion_final.agregar_opcion("Escuchar la respuesta de Ra's", "tim_dificil_respuesta_final_ras", stat="reputacion", cambio=25)
        self.historia["tim_dificil_confrontacion_final"] = tim_dificil_confrontacion_final

        tim_dificil_emboscada = NodoHistoria(
            "tim_dificil_emboscada",
            "LA EMBOSCADA PERFECTA",
            "Los ninjas entran a la Mansión Wayne esperando una mansión desprotegida. En su lugar, encuentran "
            "una trampa elaborada. Has estudiado sus tácticas, anticipado sus puntos de entrada, y preparado "
            "contramedidas específicas. Uno por uno, caen en tus trampas. Cuando el último ninja está "
            "inconsciente, te paras victorioso. 'Bruce estaría orgulloso,' piensas.",
            "tim_emboscada_perfecta.png"
        )
        tim_dificil_emboscada.agregar_opcion("Interrogar a los ninjas", "tim_dificil_interrogar_ninjas", stat="recursos", cambio=3)
        self.historia["tim_dificil_emboscada"] = tim_dificil_emboscada

        tim_dificil_trampa_mansion = NodoHistoria(
            "tim_dificil_trampa_mansion",
            "CASA TRAMPA",
            "Con Alfred a salvo, conviertes la Mansión Wayne en una trampa mortal (no letal, por supuesto). "
            "Cada habitación tiene sorpresas. Cuando los ninjas entran, es como un juego mortal de 'Operación'. "
            "Cables de disparo, redes ocultas, gas somnífero, todo no letal pero efectivo. Los capturas a "
            "todos sin una sola muerte. Batman aprobaría tus métodos.",
            "tim_casa_trampa.png"
        )
        tim_dificil_trampa_mansion.agregar_opcion("Usar ninjas como información", "tim_dificil_informacion_ninjas", stat="recursos", cambio=3)
        self.historia["tim_dificil_trampa_mansion"] = tim_dificil_trampa_mansion

        tim_dificil_comando_central = NodoHistoria(
            "tim_dificil_comando_central",
            "ORACLE Y RED ROBIN",
            "Trabajando con Barbara desde su torre, se convierten en un equipo perfecto. Ella maneja "
            "vigilancia y comunicaciones, tú coordinas respuestas tácticas. Es como un tablero de ajedrez "
            "en vivo donde ves cada pieza. Cuando los ataques comienzan, los neutralizas antes de que "
            "escalen. 'Trabajamos bien juntos,' dice Barbara. 'Siempre lo hemos hecho,' respondes.",
            "tim_comando_central.png"
        )
        tim_dificil_comando_central.agregar_opcion("Victoria coordinada", "tim_dificil_victoria_coordinada", stat="reputacion", cambio=20)
        self.historia["tim_dificil_comando_central"] = tim_dificil_comando_central

        tim_dificil_mision_titans = NodoHistoria(
            "tim_dificil_mision_titans",
            "TITANS UNIDOS",
            "Regresas a la misión con los Titans completamente respaldándote. No es solo sobre proteger "
            "objetivos ahora; es sobre enviar un mensaje a Ra's al Ghul: no estás solo. Juntos, coordinan "
            "una operación que es mitad defensa, mitad contraataque. Los ninjas de Ra's se encuentran no "
            "solo con resistencia, sino con un equipo de superhéroes de élite.",
            "tim_titans_unidos.png"
        )
        tim_dificil_mision_titans.agregar_opcion("Tomar la ofensiva", "tim_dificil_ofensiva", stat="reputacion", cambio=20)
        self.historia["tim_dificil_mision_titans"] = tim_dificil_mision_titans

        tim_dificil_liderar_titans = NodoHistoria(
            "tim_dificil_liderar_titans",
            "EL LÍDER NATO",
            "Lideras a los Titans en Gotham con confianza renovada. Conner comenta: 'Tim, siempre has sido "
            "un líder. Solo necesitabas creerlo.' Cassie añade: 'Y no tienes que ser Batman para serlo.' "
            "Tienen razón. Eres Red Robin, y eso es suficiente. Bajo tu liderazgo, los Titans operan como "
            "una máquina bien aceitada, protegiendo cada objetivo con precisión quirúrgica.",
            "tim_lider_nato.png"
        )
        tim_dificil_liderar_titans.agregar_opcion("Operación Titans perfecta", "tim_dificil_operacion_titans", stat="reputacion", cambio=25)
        self.historia["tim_dificil_liderar_titans"] = tim_dificil_liderar_titans

        tim_dificil_buscar_ras = NodoHistoria(
            "tim_dificil_buscar_ras",
            "LA CAZA DEL DEMONIO",
            "Mientras la defensa se ejecuta perfectamente, te escabulles para buscar a Ra's al Ghul. Sabes "
            "que no estará en el frente de batalla; estará observando, evaluando, planeando su próximo "
            "movimiento. Usando tus habilidades de detective, rastreas sus posibles ubicaciones. Lo encuentras "
            "en un edificio con vista a Gotham, observando el fracaso de su plan con expresión indescifrable.",
            "tim_caza_del_demonio.png"
        )
        tim_dificil_buscar_ras.agregar_opcion("Confrontación en las alturas", "tim_dificil_alturas", stat="salud", cambio=-10)
        self.historia["tim_dificil_buscar_ras"] = tim_dificil_buscar_ras

        tim_dificil_coordinacion_total = NodoHistoria(
            "tim_dificil_coordinacion_total",
            "RED DE HÉROES",
            "Coordinas una red de héroes que abarca toda Gotham. No es solo la Bat-Familia o los Titans; "
            "es toda la comunidad heroica de la ciudad. Huntress, Black Canary, Question, Batwoman, todos "
            "responden a tu llamado. Ra's planeaba atacar una ciudad; en su lugar, ataca una comunidad "
            "unida. Su ejército de asesinos se enfrenta a un ejército de héroes.",
            "tim_red_de_heroes.png"
        )
        tim_dificil_coordinacion_total.agregar_opcion("La batalla por Gotham", "tim_dificil_batalla_gotham", stat="reputacion", cambio=30)
        self.historia["tim_dificil_coordinacion_total"] = tim_dificil_coordinacion_total

        tim_dificil_rastrear_ras = NodoHistoria(
            "tim_dificil_rastrear_ras",
            "EL RASTRO DEL DEMONIO",
            "Rastreas a Ra's usando métodos que aprendiste de Batman. Cada asesino capturado proporciona "
            "una pieza del rompecabezas. Barbara ayuda con análisis de datos. Eventualmente, triangulas su "
            "ubicación: un edificio corporativo abandonado en el distrito financiero. Es apropiado: planeaba "
            "robar Wayne Enterprises, y ahora se esconde en una torre corporativa vacía.",
            "tim_rastro_del_demonio.png"
        )
        tim_dificil_rastrear_ras.agregar_opcion("Infiltrar la ubicación de Ra's", "tim_dificil_infiltracion_final", stat="recursos", cambio=3)
        self.historia["tim_dificil_rastrear_ras"] = tim_dificil_rastrear_ras

        tim_dificil_defensa_equipo = NodoHistoria(
            "tim_dificil_defensa_equipo",
            "FUERZA COMBINADA",
            "Con tu equipo reunido, la defensa es impenetrable. Cada miembro juega su rol perfectamente. "
            "Superboy usa fuerza, Wonder Girl usa habilidad, Kid Flash usa velocidad, y tú usas cerebro. "
            "Es la combinación perfecta. Los ninjas de Ra's son derrotados metódicamente. Al final de la "
            "noche, ningún objetivo ha sido alcanzado. Es victoria completa.",
            "tim_fuerza_combinada.png"
        )
        tim_dificil_defensa_equipo.agregar_opcion("Celebración y próximos pasos", "tim_dificil_celebracion", stat="reputacion", cambio=20)
        self.historia["tim_dificil_defensa_equipo"] = tim_dificil_defensa_equipo

        tim_dificil_consecuencias = NodoHistoria(
            "tim_dificil_consecuencias",
            "FINAL AMARGO: LECCIONES DOLOROSAS",
            "Enfrentas las consecuencias de tu orgullo. Algunos objetivos fueron alcanzados. Hubo heridos, "
            "quizás muertos. Dick te mira decepcionado: 'Si hubieras pedido ayuda desde el principio...' "
            "Tiene razón. Aprendiste ser detective de Batman, pero no aprendiste la lección más importante: "
            "ningún héroe puede hacerlo todo solo. Es una lección que pagarás con culpa el resto de tu vida. "
            "Red Robin continuará, pero con cicatrices emocionales que nunca sanarán completamente.",
            "tim_final_amargo.png"
        )
        # Final malo sin más opciones
        self.historia["tim_dificil_consecuencias"] = tim_dificil_consecuencias

        tim_dificil_operacion_perfecta = NodoHistoria(
            "tim_dificil_operacion_perfecta",
            "OPERACIÓN: ÉXITO TOTAL",
            "La operación se ejecuta sin un solo error. Cada equipo cumple su objetivo. Cada objetivo está "
            "protegido. Cada asesino es capturado o repelido. Cuando Barbara compila el informe final, es "
            "perfecto: cero bajas de tu lado, todos los objetivos a salvo, plan de Ra's completamente frustrado. "
            "'Tim,' dice Barbara, 'esto es... esto es obra maestra de estrategia. Nivel de Bruce Wayne.'",
            "tim_operacion_exitototal.png"
        )
        tim_dificil_operacion_perfecta.agregar_opcion("El reconocimiento final", "tim_dificil_reconocimiento", stat="reputacion", cambio=35)
        self.historia["tim_dificil_operacion_perfecta"] = tim_dificil_operacion_perfecta

        tim_dificil_defensa_conjunta = NodoHistoria(
            "tim_dificil_defensa_conjunta",
            "BAT-FAMILIA UNIDA",
            "Planeas la defensa con Dick, trabajando juntos como los hermanos que son. Dick aporta experiencia "
            "de combate y liderazgo. Tú aportas análisis estratégico y planificación detallada. Juntos, crean "
            "un plan que ninguno podría haber creado solo. Damian incluso contribuye con conocimiento de la "
            "Liga de Asesinos. Por primera vez en meses, la familia está verdaderamente unida.",
            "tim_bat_familia_unida.png"
        )
        tim_dificil_defensa_conjunta.agregar_opcion("Ejecutar plan familiar", "tim_dificil_plan_familiar", stat="reputacion", cambio=25)
        self.historia["tim_dificil_defensa_conjunta"] = tim_dificil_defensa_conjunta

        tim_dificil_reagrupar = NodoHistoria(
            "tim_dificil_reagrupar",
            "REAGRUPANDO FUERZAS",
            "Te reagrupas con los Titans después de la batalla caótica. Estás herido pero vivo. Algunos "
            "objetivos fueron alcanzados, pero la mayoría están a salvo. No es victoria perfecta, pero es "
            "victoria. Conner te dice: 'Tim, la próxima vez, llámanos primero, pelea después.' Tiene razón. "
            "Has aprendido una lección valiosa sobre pedir ayuda a tiempo.",
            "tim_reagrupando_fuerzas.png"
        )
        tim_dificil_reagrupar.agregar_opcion("Planear contraataque", "tim_dificil_contraataque", stat="recursos", cambio=2)
        self.historia["tim_dificil_reagrupar"] = tim_dificil_reagrupar

        tim_dificil_asegurar_moverse = NodoHistoria(
            "tim_dificil_asegurar_moverse",
            "OBJETIVO ASEGURADO",
            "Aseguras Wayne Enterprises con Lucius. Él te entrega un paquete: 'Documentos de transferencia "
            "temporal. Si algo me pasa, las acciones controladoras van a ti temporalmente, no a Ra's.' Es "
            "un movimiento brillante. Incluso si Ra's tiene éxito en algo, no obtendrá Wayne Enterprises. "
            "Con un objetivo asegurado, te mueves al siguiente, sabiendo que el legado financiero de Bruce "
            "está protegido.",
            "tim_objetivo_asegurado.png"
        )
        tim_dificil_asegurar_moverse.agregar_opcion("Moverse a la Mansión Wayne", "tim_dificil_moverse_mansion", stat="recursos", cambio=2)
        self.historia["tim_dificil_asegurar_moverse"] = tim_dificil_asegurar_moverse

        tim_dificil_batalla_respaldo = NodoHistoria(
            "tim_dificil_batalla_respaldo",
            "BATALLA CON HERMANOS",
            "La batalla contra Ra's y sus ninjas elite es intensa, pero con los Titans respaldándote, no "
            "estás solo. Superboy enfrenta a los ninjas más fuertes. Wonder Girl neutraliza las armas. Kid "
            "Flash desorienta al enemigo con velocidad. Y tú te enfrentas a Ra's directamente, no para "
            "superarlo físicamente, sino para mantenerlo distraído mientras tus amigos desmantelan su operación.",
            "tim_batalla_hermanos.png"
        )
        tim_dificil_batalla_respaldo.agregar_opcion("Victoria de equipo", "tim_dificil_victoria_equipo", stat="salud", cambio=-15)
        self.historia["tim_dificil_batalla_respaldo"] = tim_dificil_batalla_respaldo

        tim_dificil_momento_verdad = NodoHistoria(
            "tim_dificil_momento_verdad",
            "EL MOMENTO DE LA VERDAD",
            "Después de la batalla, Ra's te mira con respeto genuino. Estás herido y sangrando, pero de pie. "
            "Él también está herido. 'Timothy Drake,' dice Ra's, 'has ganado algo que doy raramente: mi respeto. "
            "Desde este día, te llamaré como llamo solo a dos personas en este mundo: Detective.' Es el mayor "
            "honor que Ra's al Ghul puede otorgar, y lo sabes.",
            "tim_momento_de_la_verdad.png"
        )
        tim_dificil_momento_verdad.agregar_opcion("Aceptar el título", "tim_dificil_titulo_detective", stat="reputacion", cambio=40)
        self.historia["tim_dificil_momento_verdad"] = tim_dificil_momento_verdad

        tim_dificil_reaccion_ras = NodoHistoria(
            "tim_dificil_reaccion_ras",
            "EL RESPETO DEL DEMONIO",
            "Ra's al Ghul se ríe, genuinamente impresionado. 'Jugaste ajedrez mientras yo jugaba damas. "
            "Protegiste vidas mientras asegurabas activos. Coordinaste defensas mientras ejecutabas maniobras "
            "legales.' Se acerca y extiende su mano. 'Detective,' dice simplemente. Es el título que solo "
            "da a aquellos que considera iguales intelectuales. Solo dos personas lo han tenido: Bruce Wayne "
            "y ahora tú.",
            "tim_respeto_del_demonio.png"
        )
        tim_dificil_reaccion_ras.agregar_opcion("El título de Detective", "tim_dificil_titulo_ganado", stat="reputacion", cambio=40)
        self.historia["tim_dificil_reaccion_ras"] = tim_dificil_reaccion_ras

        tim_dificil_reconciliacion = NodoHistoria(
            "tim_dificil_reconciliacion",
            "FAMILIA RESTAURADA",
            "En la Batcueva, la familia se reúne. Dick te abraza: 'Tim, nunca debí dudar de ti. Eres tanto "
            "detective como cualquiera de nosotros.' Barbara sonríe: 'Mejor que algunos.' Incluso Damian "
            "murmura: 'Drake... hiciste bien.' Alfred es el último en hablar: 'Master Timothy, el Maestro "
            "Bruce estaría inmensamente orgulloso. No solo salvaste a la familia, sino que demostraste que "
            "has superado ser Robin. Eres Red Robin ahora. Tu propio héroe.'",
            "tim_familia_restaurada.png"
        )
        tim_dificil_reconciliacion.agregar_opcion("Mirar hacia el futuro", "tim_dificil_futuro", stat="reputacion", cambio=35)
        self.historia["tim_dificil_reconciliacion"] = tim_dificil_reconciliacion

        tim_dificil_confrontacion_victoriosa = NodoHistoria(
            "tim_dificil_confrontacion_victoriosa",
            "VICTORIOSO Y VALIDADO",
            "Confrontas a Ra's después de tu victoria perfecta. Él te espera, curiosamente sin enojo. 'Timothy "
            "Drake, lograste algo extraordinario. Derrotaste a la Liga de Asesinos sin matar a uno solo. "
            "Protegiste ocho objetivos simultáneamente. Y lo hiciste no con fuerza superior, sino con estrategia "
            "y coordinación.' Se inclina ligeramente. 'Detective. Ahora entiendo por qué el Batman te eligió.'",
            "tim_confrontacion_victoriosa.png"
        )
        tim_dificil_confrontacion_victoriosa.agregar_opcion("El reconocimiento final", "tim_dificil_reconocimiento_ras", stat="reputacion", cambio=35)
        self.historia["tim_dificil_confrontacion_victoriosa"] = tim_dificil_confrontacion_victoriosa

        tim_dificil_respuesta_final_ras = NodoHistoria(
            "tim_dificil_respuesta_final_ras",
            "LA FILOSOFÍA DEL DEMONIO",
            "Ra's suspira: 'Porque si el Detective regresa y encuentra su legado destruido, sentirá el mismo "
            "dolor que he sentido por siglos. Pero tú... tú lo protegiste.' Se levanta para irse. 'Ganaste "
            "esta ronda, Detective. Sí, Detective. Ese es tu título ahora. Has ganado lo que pocos logran: "
            "mi respeto permanente.' Se va, dejándote con la victoria y el título.",
            "tim_filosofia_del_demonio.png"
        )
        tim_dificil_respuesta_final_ras.agregar_opcion("Regresar victorioso", "tim_dificil_regreso_victorioso", stat="reputacion", cambio=35)
        self.historia["tim_dificil_respuesta_final_ras"] = tim_dificil_respuesta_final_ras

        tim_dificil_interrogar_ninjas = NodoHistoria(
            "tim_dificil_interrogar_ninjas",
            "INTERROGATORIO EFECTIVO",
            "Interrogas a los ninjas capturados usando técnicas de Batman. Obtienes información valiosa: "
            "ubicaciones de otros equipos, cronogramas de ataque, y lo más importante, la ubicación de Ra's "
            "al Ghul. Armado con esta información, puedes pasar de defensiva a ofensiva. No solo protegerás "
            "objetivos; neutralizarás la amenaza en su origen.",
            "tim_interrogatorio_efectivo.png"
        )
        tim_dificil_interrogar_ninjas.agregar_opcion("Ir tras Ra's directamente", "tim_dificil_cazar_ras", stat="recursos", cambio=3)
        self.historia["tim_dificil_interrogar_ninjas"] = tim_dificil_interrogar_ninjas

        tim_dificil_informacion_ninjas = NodoHistoria(
            "tim_dificil_informacion_ninjas",
            "INTELIGENCIA VALIOSA",
            "Los ninjas capturados proporcionan inteligencia vital. Descubres que Ra's tiene un centro de "
            "comando en Gotham desde donde coordina todo. Si puedes neutralizar ese centro, desmantelarás "
            "toda la operación. Contactas a los Titans: 'Tengo la ubicación. Vamos a terminar esto esta noche.'",
            "tim_inteligencia_valiosa.png"
        )
        tim_dificil_informacion_ninjas.agregar_opcion("Ataque al centro de comando", "tim_dificil_ataque_comando", stat="recursos", cambio=3)
        self.historia["tim_dificil_informacion_ninjas"] = tim_dificil_informacion_ninjas

        tim_dificil_victoria_coordinada = NodoHistoria(
            "tim_dificil_victoria_coordinada",
            "COORDINACIÓN PERFECTA",
            "La coordinación entre tú y Barbara es perfecta. Es como si compartieran una mente. Ella ve todo, "
            "tú respondes a todo. Los asesinos no tienen oportunidad contra este nivel de coordinación. Al "
            "final, Barbara dice: 'Tim, esto fue... trabajo de nivel Batman. No, mejor. Batman trabaja solo. "
            "Tú trabajaste con equipo. Eso es más difícil y más efectivo.'",
            "tim_coordinacion_perfecta.png"
        )
        tim_dificil_victoria_coordinada.agregar_opcion("Buscar a Ra's juntos", "tim_dificil_busqueda_conjunta", stat="reputacion", cambio=25)
        self.historia["tim_dificil_victoria_coordinada"] = tim_dificil_victoria_coordinada

        tim_dificil_ofensiva = NodoHistoria(
            "tim_dificil_ofensiva",
            "CONTRAATAQUE TITÁN",
            "No te limitas a defender; tomas la ofensiva. Con los Titans, atacas las bases de operaciones de "
            "los asesinos en Gotham. Es audaz y efectivo. Los asesinos se encuentran luchando defensivamente "
            "en su propio territorio. Superboy destruye arsenales de armas. Wonder Girl captura líderes de "
            "escuadrones. Kid Flash intercepta comunicaciones. Y tú coordinas todo como un general en batalla.",
            "tim_contraataque_titan.png"
        )
        tim_dificil_ofensiva.agregar_opcion("Presionar hasta Ra's", "tim_dificil_presionar_ras", stat="salud", cambio=-10)
        self.historia["tim_dificil_ofensiva"] = tim_dificil_ofensiva

        tim_dificil_operacion_titans = NodoHistoria(
            "tim_dificil_operacion_titans",
            "OPERACIÓN TITÁN: ÉXITO",
            "Bajo tu liderazgo, los Titans ejecutan una operación perfecta. Cada miembro brilla en su rol. "
            "Conner usa su fuerza con precisión. Cassie lidera subequipos con confianza. Bart proporciona "
            "reconocimiento a velocidad. Y tú tejes todo junto en una sinfonía de heroísmo. Al final, todos "
            "los objetivos están seguros. Ra's al Ghul ha sido completamente derrotado.",
            "tim_operacion_titan_exito.png"
        )
        tim_dificil_operacion_titans.agregar_opcion("Confrontación final con Ra's", "tim_dificil_ultima_confrontacion", stat="reputacion", cambio=30)
        self.historia["tim_dificil_operacion_titans"] = tim_dificil_operacion_titans

        tim_dificil_alturas = NodoHistoria(
            "tim_dificil_alturas",
            "EN LAS ALTURAS DE GOTHAM",
            "Encuentras a Ra's en la azotea del edificio más alto de Gotham. El viento sopla fuertemente. "
            "Gotham se extiende debajo de ustedes, una ciudad que ambos han tratado de proteger (o controlar) "
            "de diferentes maneras. 'Detective Timothy Drake,' dice Ra's. 'Viniste solo. Valiente o tonto.' "
            "'Inteligente,' respondes. 'Sabía que querías hablar, no pelear. Si quisieras pelear, no estarías "
            "aquí solo.'",
            "tim_en_las_alturas.png"
        )
        tim_dificil_alturas.agregar_opcion("La conversación final", "tim_dificil_conversacion_final", stat="reputacion", cambio=30)
        self.historia["tim_dificil_alturas"] = tim_dificil_alturas

        tim_dificil_batalla_gotham = NodoHistoria(
            "tim_dificil_batalla_gotham",
            "LA BATALLA POR GOTHAM",
            "Es una batalla como Gotham nunca ha visto. No es Batman contra un villano. Es una comunidad "
            "entera de héroes defendiendo su ciudad contra un ejército de asesinos. Las calles se convierten "
            "en zonas de batalla. Pero tus héroes no pelean con brutalidad; pelean con precisión. Cada asesino "
            "es neutralizado, capturado, no asesinado. Al final, la Liga de Asesinos se retira. Gotham permanece.",
            "tim_batalla_por_gotham.png"
        )
        tim_dificil_batalla_gotham.agregar_opcion("Victoria de la comunidad", "tim_dificil_victoria_comunidad", stat="reputacion", cambio=40)
        self.historia["tim_dificil_batalla_gotham"] = tim_dificil_batalla_gotham

        tim_dificil_infiltracion_final = NodoHistoria(
            "tim_dificil_infiltracion_final",
            "INFILTRACIÓN FINAL",
            "Te infiltras en el edificio donde Ra's se esconde. Usas todas tus habilidades de sigilo. Los "
            "ninjas guardianes no te detectan. Llegas a la oficina principal donde Ra's está sentado, esperando. "
            "'Sabía que vendrías,' dice sin voltear. 'El Detective siempre termina lo que comienza.' Se voltea "
            "y sonríe. 'Hablemos, tú y yo. Detective a Detective.'",
            "tim_infiltracion_final.png"
        )
        tim_dificil_infiltracion_final.agregar_opcion("La conversación de Detectives", "tim_dificil_conversacion_detectives", stat="reputacion", cambio=30)
        self.historia["tim_dificil_infiltracion_final"] = tim_dificil_infiltracion_final

        tim_dificil_celebracion = NodoHistoria(
            "tim_dificil_celebracion",
            "CELEBRACIÓN MERECIDA",
            "Los Titans celebran la victoria. Conner te levanta en sus hombros. Cassie sonríe con orgullo. "
            "Bart corre círculos alrededor de todos. Es un momento de alegría pura. Has salvado a todos, "
            "derrotado a Ra's al Ghul, y probado tu valía como héroe independiente. Ya no eres Robin. Eres "
            "Red Robin, y ese título tiene tanto peso como Batman.",
            "tim_celebracion_merecida.png"
        )
        tim_dificil_celebracion.agregar_opcion("Próximos pasos", "tim_dificil_proximos_pasos", stat="reputacion", cambio=25)
        self.historia["tim_dificil_celebracion"] = tim_dificil_celebracion

        tim_dificil_reconocimiento = NodoHistoria(
            "tim_dificil_reconocimiento",
            "RECONOCIMIENTO UNIVERSAL",
            "La comunidad heroica completa reconoce tu éxito. La Liga de la Justicia envía felicitaciones. "
            "Los Titans te eligen oficialmente como líder. La Bat-Familia te acoge de vuelta con respeto "
            "completo. Incluso el Comisionado Gordon dice: 'Red Robin es bienvenido en Gotham tanto como "
            "Batman.' Has logrado algo extraordinario: crear tu propia identidad heroica fuera de la sombra "
            "de Batman.",
            "tim_reconocimiento_universal.png"
        )
        tim_dificil_reconocimiento.agregar_opcion("FINAL HEROICO: El Detective", "tim_dificil_final_heroico", stat="reputacion", cambio=50)
        self.historia["tim_dificil_reconocimiento"] = tim_dificil_reconocimiento

        tim_dificil_plan_familiar = NodoHistoria(
            "tim_dificil_plan_familiar",
            "FAMILIA EN ACCIÓN",
            "El plan familiar se ejecuta con precisión militar. Dick y Damian toman el sector este. Tú y "
            "Barbara coordinan desde el centro. Alfred (después de mucha insistencia) acepta refugio seguro. "
            "La familia trabaja como una unidad perfecta, cada uno complementando las fortalezas de los otros. "
            "Es hermoso ver. Esto es lo que Bruce construyó: no solo un símbolo, sino una familia.",
            "tim_familia_en_accion.png"
        )
        tim_dificil_plan_familiar.agregar_opcion("Victoria familiar completa", "tim_dificil_victoria_total", stat="reputacion", cambio=30)
        self.historia["tim_dificil_plan_familiar"] = tim_dificil_plan_familiar

        tim_dificil_contraataque = NodoHistoria(
            "tim_dificil_contraataque",
            "PLANEANDO EL CONTRAATAQUE",
            "Después de reagrupar, planeas un contraataque. Ya no se trata solo de defender; es momento de "
            "neutralizar la amenaza permanentemente. Con la ayuda de los Titans y la información de los ninjas "
            "capturados, identificas todas las células de la Liga en Gotham. En una noche coordinada, las "
            "desmantelan todas simultáneamente. Ra's al Ghul pierde su ejército en Gotham.",
            "tim_planeando_contraataque.png"
        )
        tim_dificil_contraataque.agregar_opcion("Confrontar a Ra's derrotado", "tim_dificil_ras_derrotado", stat="reputacion", cambio=25)
        self.historia["tim_dificil_contraataque"] = tim_dificil_contraataque

        tim_dificil_moverse_mansion = NodoHistoria(
            "tim_dificil_moverse_mansion",
            "PROTEGIENDO EL HOGAR",
            "Te mueves a la Mansión Wayne, el corazón emocional de la Bat-Familia. Alfred te recibe: 'Sabía "
            "que vendría, Master Timothy.' Juntos, fortifican la mansión. Cuando los asesinos llegan, encuentran "
            "no una casa sino una fortaleza. La batalla es intensa pero victoriosa. Al final, tú y Alfred "
            "están de pie entre ninjas inconscientes. 'Bien hecho, señor,' dice Alfred, sirviéndote té.",
            "tim_protegiendo_el_hogar.png"
        )
        tim_dificil_moverse_mansion.agregar_opcion("Todos los objetivos asegurados", "tim_dificil_objetivos_asegurados", stat="reputacion", cambio=25)
        self.historia["tim_dificil_moverse_mansion"] = tim_dificil_moverse_mansion

        tim_dificil_victoria_equipo = NodoHistoria(
            "tim_dificil_victoria_equipo",
            "VICTORIA DE EQUIPO",
            "Con los Titans, derrotan a Ra's y sus fuerzas. Es una victoria de equipo en el sentido más puro. "
            "Cada uno contribuyó igualmente. Cuando Ra's se retira, te mira: 'Detective Drake, la próxima "
            "vez que nos encontremos, será bajo circunstancias diferentes. Has ganado mi respeto permanente.' "
            "Se va, derrotado pero no destruido. Los Titans te rodean celebrando. Has probado que el trabajo "
            "en equipo supera al genio solitario.",
            "tim_victoria_de_equipo.png"
        )
        tim_dificil_victoria_equipo.agregar_opcion("Regreso triunfal", "tim_dificil_regreso_triunfal", stat="reputacion", cambio=30)
        self.historia["tim_dificil_victoria_equipo"] = tim_dificil_victoria_equipo

        tim_dificil_titulo_detective = NodoHistoria(
            "tim_dificil_titulo_detective",
            "EL TÍTULO GANADO",
            "Aceptas el título de Detective de Ra's al Ghul. No es solo un título; es reconocimiento de que "
            "has alcanzado el mismo nivel intelectual que Bruce Wayne. Solo tres personas en el mundo han "
            "recibido este título de Ra's: Bruce, tú, y nadie más. Cuando regresas a la Bat-Familia y les "
            "cuentas, Dick te abraza: 'Tim, siempre supimos que eras brillante. Pero esto... Ra's al Ghul "
            "no da ese título a la ligera.'",
            "tim_titulo_ganado.png"
        )
        tim_dificil_titulo_detective.agregar_opcion("FINAL ÉPICO: Detective Red Robin", "tim_dificil_final_epico", stat="reputacion", cambio=50, item="Título de Detective")
        self.historia["tim_dificil_titulo_detective"] = tim_dificil_titulo_detective

        tim_dificil_titulo_ganado = NodoHistoria(
            "tim_dificil_titulo_ganado",
            "DETECTIVE RECONOCIDO",
            "El título de Detective de Ra's al Ghul es algo que pocos logran. Es reconocimiento de brillantez "
            "intelectual al nivel de Bruce Wayne. Cuando la Bat-Familia se entera, hay silencio. Luego Dick "
            "habla: 'Tim, Ra's ha vivido siglos y solo ha dado ese título a dos personas: Bruce y tú. Eso "
            "dice todo.' Alfred añade: 'El Maestro Bruce siempre supo que era especial, Master Timothy. "
            "Ahora el mundo lo sabe.'",
            "tim_detective_reconocido.png"
        )
        tim_dificil_titulo_ganado.agregar_opcion("FINAL LEGENDARIO: El Tercer Detective", "tim_dificil_final_legendario", stat="reputacion", cambio=50, item="Título de Detective")
        self.historia["tim_dificil_titulo_ganado"] = tim_dificil_titulo_ganado

        tim_dificil_futuro = NodoHistoria(
            "tim_dificil_futuro",
            "MIRANDO ADELANTE",
            "Con la familia restaurada y Ra's derrotado, miras hacia el futuro. Aún crees que Bruce está vivo "
            "en algún lugar del tiempo. Pero ahora tienes el apoyo de la familia para buscarlo. Dick dice: "
            "'Tim, si crees que Bruce está vivo, investigaremos juntos. Pero esta vez, como familia.' Es "
            "todo lo que necesitabas escuchar. Tu búsqueda continúa, pero ya no estás solo.",
            "tim_mirando_adelante.png"
        )
        tim_dificil_futuro.agregar_opcion("FINAL ESPERANZADOR: La Búsqueda Continúa", "tim_dificil_final_esperanzador", stat="reputacion", cambio=40)
        self.historia["tim_dificil_futuro"] = tim_dificil_futuro

        tim_dificil_reconocimiento_ras = NodoHistoria(
            "tim_dificil_reconocimiento_ras",
            "EL RECONOCIMIENTO DEL INMORTAL",
            "Ra's al Ghul se acerca y, sorprendentemente, se inclina ante ti. 'Detective Timothy Drake. He "
            "vivido siglos. He enfrentado a los más grandes estrategas de la historia. Y tú te encuentras "
            "entre ellos. Tu victoria hoy no fue de fuerza, sino de mente. Coordinaste lo imposible. Por "
            "eso, te doy el título que solo he dado a uno más: Detective.' Es validación suprema.",
            "tim_reconocimiento_del_inmortal.png"
        )
        tim_dificil_reconocimiento_ras.agregar_opcion("FINAL GLORIOSO: El Segundo Detective", "tim_dificil_final_glorioso", stat="reputacion", cambio=50, item="Título de Detective")
        self.historia["tim_dificil_reconocimiento_ras"] = tim_dificil_reconocimiento_ras

        tim_dificil_regreso_victorioso = NodoHistoria(
            "tim_dificil_regreso_victorioso",
            "HÉROE VICTORIOSO",
            "Regresas a Gotham victorioso. Has derrotado a Ra's al Ghul, salvado a la Bat-Familia, y ganado "
            "el título de Detective. La ciudad te recibe como héroe. Los Titans te celebran. La Bat-Familia "
            "te abraza. Y en algún lugar, sabes que Bruce Wayne, donde quiera que esté en el tiempo, estaría "
            "orgulloso. Has superado ser Robin. Eres Red Robin, Detective, y héroe por derecho propio.",
            "tim_heroe_victorioso.png"
        )
        tim_dificil_regreso_victorioso.agregar_opcion("FINAL TRIUNFAL: Red Robin Ascendente", "tim_dificil_final_triunfal", stat="reputacion", cambio=45)
        self.historia["tim_dificil_regreso_victorioso"] = tim_dificil_regreso_victorioso

        tim_dificil_cazar_ras = NodoHistoria(
            "tim_dificil_cazar_ras",
            "LA CAZA FINAL",
            "Con la información de los ninjas, cazas a Ra's directamente. Es audaz, quizás temerario. Pero "
            "estás cansado de ser reactivo. Es momento de terminar esto. Encuentras a Ra's en su escondite "
            "temporal. Está solo, esperándote. 'Detective Drake,' dice con sonrisa. 'Viniste a mí. Valiente. "
            "Muy bien. Hablemos, héroe a villano, Detective a Detective.'",
            "tim_caza_final.png"
        )
        tim_dificil_cazar_ras.agregar_opcion("El diálogo final", "tim_dificil_dialogo_final", stat="reputacion", cambio=30)
        self.historia["tim_dificil_cazar_ras"] = tim_dificil_cazar_ras

        tim_dificil_ataque_comando = NodoHistoria(
            "tim_dificil_ataque_comando",
            "ASALTO AL COMANDO",
            "Lideras un asalto coordinado al centro de comando de Ra's. Los Titans, Bat-Familia, y otros "
            "héroes de Gotham atacan simultáneamente. Es la operación ofensiva más grande que has coordinado. "
            "El centro cae rápidamente bajo la presión combinada. Ra's escapa, pero su operación en Gotham "
            "está completamente desmantelada. Has ganado no solo esta batalla, sino la guerra completa.",
            "tim_asalto_al_comando.png"
        )
        tim_dificil_ataque_comando.agregar_opcion("Victoria definitiva", "tim_dificil_victoria_definitiva", stat="reputacion", cambio=35)
        self.historia["tim_dificil_ataque_comando"] = tim_dificil_ataque_comando

        tim_dificil_busqueda_conjunta = NodoHistoria(
            "tim_dificil_busqueda_conjunta",
            "DETECTIVE Y ORACLE",
            "Tú y Barbara buscan a Ra's juntos. Tu detective en campo, ella detective digital. Juntos, son "
            "imparables. Rastreas a Ra's hasta su última ubicación. Barbara hackea sus comunicaciones. Cuando "
            "lo confrontan, Ra's sonríe: 'Detective Drake y Oracle. Un equipo formidable. Casi tan formidable "
            "como Batman y Oracle. Quizás más, porque ustedes reconocen que necesitan mutuamente.'",
            "tim_detective_y_oracle.png"
        )
        tim_dificil_busqueda_conjunta.agregar_opcion("Confrontación dual", "tim_dificil_confrontacion_dual", stat="reputacion", cambio=30)
        self.historia["tim_dificil_busqueda_conjunta"] = tim_dificil_busqueda_conjunta

        tim_dificil_presionar_ras = NodoHistoria(
            "tim_dificil_presionar_ras",
            "PRESIÓN IMPLACABLE",
            "Presionas implacablemente hasta llegar a Ra's al Ghul. Cada base destruida, cada ninja capturado, "
            "cada operación desmantelada. Finalmente, acorralas a Ra's en su último refugio. Está solo, sin "
            "ejército, sin recursos. Te mira con mezcla de respeto y frustración: 'Detective Drake, me has "
            "derrotado completamente. Algo que pocos han logrado. Acepto mi derrota... por ahora.'",
            "tim_presion_implacable.png"
        )
        tim_dificil_presionar_ras.agregar_opcion("Victoria absoluta", "tim_dificil_victoria_absoluta", stat="reputacion", cambio=40)
        self.historia["tim_dificil_presionar_ras"] = tim_dificil_presionar_ras

        tim_dificil_defensa_conjunta.agregar_opcion("Ejecutar plan familiar", "tim_dificil_plan_familiar", stat="reputacion", cambio=25)
        self.historia["tim_dificil_defensa_conjunta"] = tim_dificil_defensa_conjunta

        tim_dificil_ultima_confrontacion = NodoHistoria(
            "tim_dificil_ultima_confrontacion",
            "LA ÚLTIMA CONFRONTACIÓN",
            "Confrontas a Ra's al Ghul por última vez. Su plan ha fallado completamente. Su ejército está "
            "derrotado. Su estrategia, desmantelada. Te mira con respeto absoluto: 'Timothy Drake, Red Robin, "
            "Detective. Has superado a un inmortal con siglos de experiencia. ¿Cómo?' Sonríes: 'Simple. Tú "
            "peleaste para destruir. Yo peleé para proteger. Y la protección siempre supera a la destrucción "
            "cuando tienes el equipo correcto.'",
            "tim_ultima_confrontacion.png"
        )
        tim_dificil_ultima_confrontacion.agregar_opcion("FINAL MAGISTRAL: El Protector", "tim_dificil_final_magistral", stat="reputacion", cambio=50)
        self.historia["tim_dificil_ultima_confrontacion"] = tim_dificil_ultima_confrontacion

        tim_dificil_conversacion_final = NodoHistoria(
            "tim_dificil_conversacion_final",
            "CONVERSACIÓN EN LAS ALTURAS",
            "Hablas con Ra's en las alturas de Gotham. Él explica: 'Atacé el legado de Wayne porque si él "
            "regresa y encuentra todo destruido, conocerá mi dolor. Pero tú lo protegiste. Dime, Detective "
            "Drake, ¿realmente crees que Bruce Wayne vive?' 'Sí,' respondes sin dudar. Ra's asiente: 'Yo "
            "también. Y cuando regrese, dile que enfrentó a un sucesor digno en ti.'",
            "tim_conversacion_en_alturas.png"
        )
        tim_dificil_conversacion_final.agregar_opcion("FINAL REFLEXIVO: Dignos Sucesores", "tim_dificil_final_reflexivo", stat="reputacion", cambio=40)
        self.historia["tim_dificil_conversacion_final"] = tim_dificil_conversacion_final

        tim_dificil_victoria_comunidad = NodoHistoria(
            "tim_dificil_victoria_comunidad",
            "LA VICTORIA DE GOTHAM",
            "La batalla termina con victoria para Gotham. No fue victoria de un héroe, sino de una comunidad. "
            "Cada héroe que participó contribuyó. Al final de la noche, todos se reúnen en la Batcueva. "
            "Batman (Dick) habla: 'Esto es lo que Bruce siempre quiso. No un héroe solitario, sino una "
            "comunidad que se protege mutuamente. Y Tim, tú coordinaste todo.' Hay aplausos. Has ganado no "
            "solo una batalla, sino el respeto de toda la comunidad heroica de Gotham.",
            "tim_victoria_de_gotham.png"
        )
        tim_dificil_victoria_comunidad.agregar_opcion("FINAL INSPIRADOR: El Coordinador", "tim_dificil_final_inspirador", stat="reputacion", cambio=45)
        self.historia["tim_dificil_victoria_comunidad"] = tim_dificil_victoria_comunidad

        tim_dificil_conversacion_detectives = NodoHistoria(
            "tim_dificil_conversacion_detectives",
            "DETECTIVE A DETECTIVE",
            "Hablas con Ra's como iguales. Él pregunta: '¿Cómo derrotaste mi plan, Detective Drake?' Explicas "
            "meticulosamente: cada anticipación, cada coordinación, cada movimiento estratégico. Ra's escucha "
            "fascinado. Cuando terminas, aplaude lentamente: 'Brillante. Absolutamente brillante. No usaste "
            "fuerza superior. Usaste inteligencia superior y coordinación perfecta. Eso es... eso es digno "
            "del título Detective.'",
            "tim_detective_a_detective.png"
        )
        tim_dificil_conversacion_detectives.agregar_opcion("FINAL INTELECTUAL: Batalla de Mentes", "tim_dificil_final_intelectual", stat="reputacion", cambio=45)
        self.historia["tim_dificil_conversacion_detectives"] = tim_dificil_conversacion_detectives

        tim_dificil_proximos_pasos = NodoHistoria(
            "tim_dificil_proximos_pasos",
            "EL CAMINO ADELANTE",
            "Después de la celebración, te sientas con los Titans. 'Entonces,' dice Conner, '¿cuál es el "
            "próximo paso? ¿Seguirás buscando a Bruce?' Asientes: 'Sí. Pero esta vez, no solo. Con amigos, "
            "con familia, con apoyo. He aprendido que ser héroe no significa hacerlo todo solo.' Cassie sonríe: "
            "'Entonces cuenta con nosotros. Siempre.' Es el comienzo de una nueva era para Red Robin.",
            "tim_camino_adelante.png"
        )
        tim_dificil_proximos_pasos.agregar_opcion("FINAL PROMETEDOR: Nueva Era", "tim_dificil_final_prometedor", stat="reputacion", cambio=40)
        self.historia["tim_dificil_proximos_pasos"] = tim_dificil_proximos_pasos

        tim_dificil_victoria_total = NodoHistoria(
            "tim_dificil_victoria_total",
            "VICTORIA TOTAL FAMILIAR",
            "La victoria es total y completa. Cada objetivo protegido, cada asesino capturado, cada plan "
            "frustrado. La Bat-Familia se reúne en la Batcueva, exhausta pero triunfante. Alfred sirve té "
            "para todos. Dick te abraza: 'Tim, lo logramos. Juntos.' Damian incluso ofrece un puño para "
            "chocar. Es un momento de unidad familiar perfecta. Esto es lo que Bruce construyó: no solo "
            "símbolos, sino familia.",
            "tim_victoria_total_familiar.png"
        )
        tim_dificil_victoria_total.agregar_opcion("FINAL EMOTIVO: Familia Unida", "tim_dificil_final_emotivo", stat="reputacion", cambio=45)
        self.historia["tim_dificil_victoria_total"] = tim_dificil_victoria_total

        tim_dificil_ras_derrotado = NodoHistoria(
            "tim_dificil_ras_derrotado",
            "EL DEMONIO CAÍDO",
            "Confrontas a Ra's al Ghul después de desmantelar completamente su operación. Está derrotado pero "
            "no quebrado. 'Detective Drake,' dice, 'me has enseñado una lección valiosa. La fuerza bruta no "
            "es suficiente contra estrategia perfecta y trabajo en equipo. Bruce Wayne te entrenó bien. Mejor "
            "que bien. Te convirtió en su igual.' Se retira, prometiendo que volverán a encontrarse algún "
            "día. Pero hoy, la victoria es tuya.",
            "tim_demonio_caido.png"
        )
        tim_dificil_ras_derrotado.agregar_opcion("FINAL ESTRATÉGICO: Maestro Táctico", "tim_dificil_final_estrategico", stat="reputacion", cambio=45)
        self.historia["tim_dificil_ras_derrotado"] = tim_dificil_ras_derrotado

        tim_dificil_objetivos_asegurados = NodoHistoria(
            "tim_dificil_objetivos_asegurados",
            "TODOS A SALVO",
            "Todos los objetivos están asegurados. Alfred a salvo. Lucius protegido. Barbara segura. Dick y "
            "Damian victoriosos. Incluso objetivos secundarios como Selina y Gordon están bien. Es una victoria "
            "perfecta, sin bajas. Cuando la Bat-Familia se reúne, Barbara compila el informe: 'Cero bajas "
            "nuestras. Todos los objetivos protegidos. Plan de Ra's completamente frustrado. Tim, esto es... "
            "esto es perfección operativa.'",
            "tim_todos_a_salvo.png"
        )
        tim_dificil_objetivos_asegurados.agregar_opcion("FINAL PERFECTO: Sin Bajas", "tim_dificil_final_perfecto", stat="reputacion", cambio=50)
        self.historia["tim_dificil_objetivos_asegurados"] = tim_dificil_objetivos_asegurados

        tim_dificil_regreso_triunfal = NodoHistoria(
            "tim_dificil_regreso_triunfal",
            "TRIUNFO DEL EQUIPO",
            "Regresan a Gotham triunfantes. Los Titans te llevan en sus hombros literalmente. La ciudad los "
            "recibe como héroes. Reportes de noticias hablan del 'nuevo héroe Red Robin que coordinó la "
            "defensa más efectiva en la historia de Gotham'. Dick te espera en la Batcueva: 'Tim, viste lo "
            "que yo no pude ver. Confiaste en tus amigos cuando yo dudaba. Eres mejor héroe de lo que yo "
            "fui a tu edad.'",
            "tim_triunfo_del_equipo.png"
        )
        tim_dificil_regreso_triunfal.agregar_opcion("FINAL VICTORIOSO: Héroe Consolidado", "tim_dificil_final_victorioso", stat="reputacion", cambio=45)
        self.historia["tim_dificil_regreso_triunfal"] = tim_dificil_regreso_triunfal

        tim_dificil_dialogo_final = NodoHistoria(
            "tim_dificil_dialogo_final",
            "EL DIÁLOGO DE LOS DETECTIVES",
            "'¿Por qué viniste solo?' pregunta Ra's. 'Porque quería entender,' respondes. 'Entender por qué "
            "un hombre que respeta a Bruce Wayne atacaría su legado.' Ra's suspira: 'Porque el respeto y el "
            "odio no son opuestos, Detective. Ambos surgen de la misma pasión.' Hablan durante horas, dos "
            "mentes brillantes discutiendo filosofía, estrategia, y el legado de Batman. Al final, Ra's dice: "
            "'Detective Drake, eres digno del título. Nos encontraremos nuevamente.'",
            "tim_dialogo_de_detectives.png"
        )
        tim_dificil_dialogo_final.agregar_opcion("FINAL FILOSÓFICO: Entendimiento Mutuo", "tim_dificil_final_filosofico", stat="reputacion", cambio=40)
        self.historia["tim_dificil_dialogo_final"] = tim_dificil_dialogo_final

        tim_dificil_victoria_definitiva = NodoHistoria(
            "tim_dificil_victoria_definitiva",
            "VICTORIA SIN APELACIÓN",
            "La victoria es definitiva y total. Ra's al Ghul no solo fue derrotado; su operación completa en "
            "Gotham fue desmantelada. Tomará años reconstruir lo que perdió en una noche. Cuando la comunidad "
            "heroica se reúne para celebrar, Superman aparece: 'Red Robin, la Liga de la Justicia te ofrece "
            "membresía cuando estés listo.' Es reconocimiento al más alto nivel. Has pasado de aprendiz a "
            "candidato de la Liga.",
            "tim_victoria_sin_apelacion.png"
        )
        tim_dificil_victoria_definitiva.agregar_opcion("FINAL ASCENDENTE: Camino a la Liga", "tim_dificil_final_ascendente", stat="reputacion", cambio=50)
        self.historia["tim_dificil_victoria_definitiva"] = tim_dificil_victoria_definitiva

        tim_dificil_confrontacion_dual = NodoHistoria(
            "tim_dificil_confrontacion_dual",
            "DÚO IMPARABLE",
            "Tú y Barbara confrontan a Ra's juntos. Es una confrontación intelectual más que física. Ra's "
            "intenta manipular, pero Barbara anticipa cada movimiento digital. Intentas engañar, pero tú "
            "anticipas cada trampa física. Juntos, son imparables. Ra's eventualmente ríe: 'Detective Drake "
            "y Oracle. Si Batman hubiera tenido esta asociación desde el principio, yo nunca habría ganado "
            "una sola batalla contra él.'",
            "tim_duo_imparable.png"
        )
        tim_dificil_confrontacion_dual.agregar_opcion("FINAL COLABORATIVO: Asociación Perfecta", "tim_dificil_final_colaborativo", stat="reputacion", cambio=45)
        self.historia["tim_dificil_confrontacion_dual"] = tim_dificil_confrontacion_dual

        tim_dificil_victoria_absoluta = NodoHistoria(
            "tim_dificil_victoria_absoluta",
            "ABSOLUTA Y TOTAL",
            "La victoria es absoluta. Ra's al Ghul está completamente derrotado. Su ejército dispersado. Sus "
            "planes frustrados. Sus recursos confiscados. Cuando la prensa pregunta cómo lo lograste, respondes "
            "simplemente: 'Con amigos, con familia, y con la creencia de que proteger siempre supera a destruir.' "
            "Se convierte en una cita famosa. Red Robin es ahora un nombre reconocido mundialmente, no como "
            "el compañero de Batman, sino como héroe por derecho propio.",
            "tim_victoria_absoluta_total.png"
        )
        tim_dificil_victoria_absoluta.agregar_opcion("FINAL GLOBAL: Reconocimiento Mundial", "tim_dificil_final_global", stat="reputacion", cambio=50)
        self.historia["tim_dificil_victoria_absoluta"] = tim_dificil_victoria_absoluta



# ==================== FINALES ====================

        tim_dificil_defensa_conjunta.agregar_opcion("Ejecutar plan familiar", "tim_dificil_plan_familiar", stat="reputacion", cambio=25)
        self.historia["tim_dificil_defensa_conjunta"] = tim_dificil_defensa_conjunta

        tim_dificil_final_heroico = NodoHistoria(
            "tim_dificil_final_heroico",
            "FINAL HEROICO: EL DETECTIVE",
            "Has logrado lo imposible. Derrotaste a Ra's al Ghul, salvaste a la Bat-Familia, y ganaste el "
            "respeto de toda la comunidad heroica. Más importante, probaste que eres más que Robin. Eres Red "
            "Robin, Detective, coordinador de héroes, y estratega maestro. Ra's al Ghul te dio el título de "
            "Detective, un honor dado solo a dos personas en la historia. La Bat-Familia te acepta como igual. "
            "Los Titans te siguen como líder. Y Bruce Wayne, donde quiera que esté en el tiempo, estaría "
            "orgulloso del héroe en que te has convertido. Tu búsqueda de Bruce continúa, pero ahora con el "
            "apoyo de todos. Ya no eres el aprendiz que dudaba de sí mismo. Eres el Detective Red Robin, y "
            "tu leyenda apenas comienza.",
            "tim_final_heroico_detective.png"
        )
        self.historia["tim_dificil_final_heroico"] = tim_dificil_final_heroico

        tim_dificil_final_epico = NodoHistoria(
            "tim_dificil_final_epico",
            "FINAL ÉPICO: DETECTIVE RED ROBIN",
            "La leyenda de Red Robin se extiende por el mundo. No solo derrotaste a Ra's al Ghul; ganaste su "
            "respeto absoluto y el título de Detective, un honor que solo Bruce Wayne había recibido antes. "
            "Eres el segundo Detective en la historia según Ra's al Ghul, el inmortal que ha vivido siglos. "
            "La Bat-Familia te reconoce no como ex-Robin, sino como igual de Batman. Los Titans te eligen "
            "oficialmente como líder permanente. La Liga de la Justicia te observa con interés. Has probado "
            "que no necesitas el manto de Batman para ser grande. Red Robin es su propia leyenda. Tu búsqueda "
            "de Bruce Wayne continúa con renovado vigor y apoyo completo. Y cuando Bruce regrese, encontrará "
            "no un aprendiz esperándolo, sino un Detective que protegió su legado contra el enemigo más peligroso. "
            "Timothy Drake ha ascendido. Red Robin ha llegado. El Detective está listo.",
            "tim_final_epico_detective_red_robin.png"
        )
        self.historia["tim_dificil_final_epico"] = tim_dificil_final_epico

        tim_dificil_final_legendario = NodoHistoria(
            "tim_dificil_final_legendario",
            "FINAL LEGENDARIO: EL TERCER DETECTIVE",
            "Tu nombre será recordado en la historia de héroes. Timothy Drake, Red Robin, el Tercer Detective. "
            "Ra's al Ghul, quien ha vivido por siglos, te otorgó el título de Detective, un honor dado solo "
            "a tres personas en toda la historia: Bruce Wayne, tú, y nadie más vivo. No solo derrotaste al "
            "Demonio en combate estratégico; lo derrotaste en el juego intelectual que él domina. Protegiste "
            "el legado de Batman cuando nadie más creía que valía la pena. Coordinaste la defensa más compleja "
            "en la historia de Gotham. Uniste a la Bat-Familia cuando estaba fragmentada. Lideraste a los "
            "Titans a victoria perfecta. Y todo mientras mantenías tu creencia inquebrantable de que Bruce "
            "Wayne vive. Tu leyenda rivaliza con la de Batman mismo. Porque donde Batman es el símbolo solitario, "
            "Red Robin es el líder que demuestra que juntos somos más fuertes. La búsqueda de Bruce continúa, "
            "pero ahora todo el mundo heroico te apoya. Eres Detective Red Robin, y tu leyenda será eterna.",
            "tim_final_legendario_tercer_detective.png"
        )
        self.historia["tim_dificil_final_legendario"] = tim_dificil_final_legendario

        tim_dificil_final_esperanzador = NodoHistoria(
            "tim_dificil_final_esperanzador",
            "FINAL ESPERANZADOR: LA BÚSQUEDA CONTINÚA",
            "Has salvado a la familia y derrotado a Ra's al Ghul. Pero más importante, has restaurado la unidad "
            "de la Bat-Familia. Dick ahora cree en tu teoría sobre Bruce. Barbara te apoya completamente. "
            "Incluso Damian muestra respeto. Alfred nunca dejó de creer en ti. Juntos como familia, continúan "
            "la búsqueda de Bruce Wayne. Ya no es la misión solitaria de un hijo adoptivo en negación. Es "
            "la misión de una familia que cree en su patriarca. Red Robin lidera la búsqueda con los recursos "
            "completos de la Bat-Familia respaldándolo. Los Titans ofrecen ayuda cuando sea necesaria. La "
            "comunidad heroica está al tanto. Bruce Wayne será encontrado. No porque un detective solitario "
            "se negó a rendirse, sino porque una familia completa se negó a dejarlo atrás. Tu fe ha sido "
            "vindicada. Tu búsqueda ha sido validada. Y el final feliz está más cerca que nunca. Red Robin "
            "vuela hacia el futuro con esperanza renovada y familia unida.",
            "tim_final_esperanzador_busqueda.png"
        )
        self.historia["tim_dificil_final_esperanzador"] = tim_dificil_final_esperanzador

        tim_dificil_final_glorioso = NodoHistoria(
            "tim_dificil_final_glorioso",
            "FINAL GLORIOSO: EL SEGUNDO DETECTIVE",
            "Ra's al Ghul te ha nombrado Detective, el segundo en recibir este título después de Bruce Wayne. "
            "Es reconocimiento que trasciende heroísmo simple. Es declaración de que tu intelecto rivaliza "
            "con los más grandes estrategas de la historia. La noticia se extiende por la comunidad heroica. "
            "Batman (Dick Grayson) declara públicamente: 'Tim Drake es Detective, y ese título tiene tanto "
            "peso como Batman.' La Liga de la Justicia te invita a consultas estratégicas. Gobiernos te "
            "contactan para asesorías de seguridad. Pero tú permaneces enfocado: encontrar a Bruce Wayne. "
            "Con el título de Detective, tu búsqueda tiene credibilidad global. Puertas que estaban cerradas "
            "se abren. Información que era inaccesible fluye. Y más importante, has probado a todos, especialmente "
            "a ti mismo, que eres digno del legado de Batman. No como sucesor, sino como igual. Red Robin, "
            "el Detective, continúa su misión con el respeto del mundo entero detrás de él.",
            "tim_final_glorioso_segundo_detective.png"
        )
        self.historia["tim_dificil_final_glorioso"] = tim_dificil_final_glorioso

        tim_dificil_final_triunfal = NodoHistoria(
            "tim_dificil_final_triunfal",
            "FINAL TRIUNFAL: RED ROBIN ASCENDENTE",
            "Tu victoria sobre Ra's al Ghul marca el comienzo de una nueva era. Red Robin ya no es visto como "
            "ex-Robin o aspirante a Batman. Es visto como líder heroico por derecho propio. Los Titans te "
            "eligen líder oficial permanente. La Bat-Familia te acepta como miembro senior. Gotham te reconoce "
            "como protector legítimo. Has ascendido de aprendiz a maestro, de compañero a líder, de seguidor "
            "a innovador. Tu estilo de heroísmo - coordinación, trabajo en equipo, estrategia sobre fuerza - "
            "se convierte en modelo para nuevos héroes. Las academias de entrenamiento estudian tus tácticas. "
            "Jóvenes héroes te idolatran. Y lo más importante, has mantenido tu humanidad. No te volviste "
            "oscuro como Batman. Permaneciste esperanzado, confiaste en amigos, y demostraste que la luz puede "
            "derrotar a la oscuridad. Bruce Wayne, cuando regrese, encontrará un legado no solo protegido, "
            "sino mejorado. Red Robin asciende, y el futuro nunca fue más brillante.",
            "tim_final_triunfal_ascendente.png"
        )
        self.historia["tim_dificil_final_triunfal"] = tim_dificil_final_triunfal

        tim_dificil_final_reflexivo = NodoHistoria(
            "tim_dificil_final_reflexivo",
            "FINAL REFLEXIVO: DIGNOS SUCESORES",
            "Tu conversación con Ra's al Ghul en las alturas de Gotham te dejó pensando. Ambos creen que Bruce "
            "vive. Ambos respetan su legado. Pero mientras Ra's buscaba destruirlo por dolor, tú lo protegiste "
            "por amor. Esa diferencia define todo. Regresas a la Bat-Familia cambiado. No solo eres más fuerte "
            "o más hábil; eres más sabio. Has aprendido que el legado de Batman no es sobre un hombre, sino "
            "sobre los valores que ese hombre representa. Justicia, protección, familia. Y has aprendido que "
            "puedes honrar esos valores sin convertirte en Batman. Red Robin es tu identidad, tu legado, tu "
            "contribución a la leyenda. Cuando Bruce regrese, encontrará que dejó un aprendiz pero regresa "
            "a un igual. Alguien que no solo aprendió sus lecciones, sino que las mejoró. Timothy Drake ha "
            "evolucionado. Y en esa evolución, el legado de Batman se fortalece. Los sucesores dignos no "
            "solo heredan; innovan. Y tú has innovado brillantemente.",
            "tim_final_reflexivo_sucesores.png"
        )
        self.historia["tim_dificil_final_reflexivo"] = tim_dificil_final_reflexivo

        tim_dificil_final_inspirador = NodoHistoria(
            "tim_dificil_final_inspirador",
            "FINAL INSPIRADOR: EL COORDINADOR",
            "Tu mayor logro no fue derrotar a Ra's al Ghul en combate. Fue demostrar el poder de la comunidad. "
            "Coordinaste docenas de héroes, cada uno con diferentes habilidades, personalidades, y métodos. "
            "Los uniste con un propósito común: proteger Gotham. Y funcionó perfectamente. Otros héroes toman "
            "nota. Tu modelo de coordinación heroica se adopta en otras ciudades. Equipos que antes operaban "
            "independientemente ahora se comunican. Héroes que se veían como competidores ahora se ven como "
            "colegas. Has inspirado un movimiento. La 'Red Robin Network' se vuelve término común - sistema "
            "de coordinación heroica basado en tu modelo. Bruce Wayne construyó un símbolo. Tú construiste "
            "una red. Y esa red es más fuerte que cualquier símbolo individual. Cuando futuras generaciones "
            "estudien la Edad de Oro del heroísmo, tu nombre estará al frente. No como el compañero de Batman, "
            "sino como el arquitecto de coordinación heroica moderna. El Coordinador. Red Robin.",
            "tim_final_inspirador_coordinador.png"
        )
        self.historia["tim_dificil_final_inspirador"] = tim_dificil_final_inspirador

        tim_dificil_final_intelectual = NodoHistoria(
            "tim_dificil_final_intelectual",
            "FINAL INTELECTUAL: BATALLA DE MENTES",
            "Tu victoria sobre Ra's al Ghul no fue victoria de músculos, sino de mente. Fue batalla intelectual "
            "al más alto nivel. Dos estrategas maestros jugando ajedrez con vidas humanas como piezas. Y tú "
            "ganaste. No solo ganaste; dominaste tan completamente que Ra's reconoció tu superioridad intelectual. "
            "Este reconocimiento resuena en círculos académicos y estratégicos. Universidades te invitan a dar "
            "conferencias sobre teoría estratégica. Militares consultan tus tácticas. Agencias de inteligencia "
            "estudian tus métodos. Pero tú permaneces humilde. 'No fui más inteligente que Ra's,' explicas. "
            "'Simplemente tenía mejor equipo. La inteligencia colectiva siempre supera al genio individual.' "
            "Es lección que el mundo necesita. En una era de héroes solitarios, demostraste que la colaboración es "
            "la verdadera fortaleza. Tu legado intelectual rivaliza con tus logros heroicos. Detective Red "
            "Robin, el estratega que probó que pensar juntos es más poderoso que pensar solo.",
            "tim_final_intelectual_mentes.png"
        )
        self.historia["tim_dificil_final_intelectual"] = tim_dificil_final_intelectual

        tim_dificil_final_prometedor = NodoHistoria(
            "tim_dificil_final_prometedor",
            "FINAL PROMETEDOR: NUEVA ERA",
            "Has salvado Gotham, derrotado a Ra's, y unido a la Bat-Familia. Pero lo más importante es lo "
            "que viene después. Con los Titans respaldándote completamente, comienzas una nueva era de heroísmo. "
            "Red Robin se convierte en líder oficial de los Titans, pero también en miembro honorario de la "
            "Bat-Familia. Operas globalmente, siguiendo pistas de Bruce Wayne, pero también respondiendo a "
            "amenazas mundiales. Es una vida balanceada que Batman nunca logró. Tienes familia, tienes amigos, "
            "tienes propósito. Y no estás solo. Cada misión con aliados. Cada victoria compartida. Cada carga "
            "aligerada por apoyo. Es el futuro del heroísmo. Bruce Wayne fue el lobo solitario. Tú eres el "
            "líder de la manada. Y esa manada es leal, fuerte, y lista para enfrentar cualquier amenaza. La "
            "búsqueda de Bruce continúa, pero ahora es parte de una misión mayor: proteger el mundo mientras "
            "preparas su regreso. Red Robin lidera una nueva era, y el futuro nunca fue más prometedor.",
            "tim_final_prometedor_nueva_era.png"
        )
        self.historia["tim_dificil_final_prometedor"] = tim_dificil_final_prometedor



        tim_dificil_final_emotivo = NodoHistoria(
            "tim_dificil_final_emotivo",
            "FINAL EMOTIVO: FAMILIA UNIDA",
            "Al final, todo se reduce a familia. No sangre, sino elección. Dick te eligió como hermano. Barbara "
            "te eligió como amigo. Alfred te eligió como nieto honorary. Incluso Damian, a su manera difícil, "
            "te acepta. Y Bruce te eligió desde el principio, cuando viste a un niño brillante que dedujo la "
            "identidad de Batman y decidió convertirlo en héroe. Esa familia estuvo fragmentada cuando Bruce "
            "'murió'. Cada uno lidiando con el duelo solo. Pero tu negación inquebrantable, tu búsqueda solitaria, "
            "tu victoria contra Ra's - todo eso los reunió. Ahora son familia nuevamente. Unida. Fuerte. Lista "
            "para encontrar a Bruce Wayne juntos. En la Batcueva, todos juntos, Alfred sirve té. Dick te abraza. "
            "Barbara sonríe. Damian asiente. Y tú sientes lo que no has sentido en meses: pertenencia. Eres "
            "Red Robin, pero más importante, eres Timothy Drake, miembro de la Bat-Familia. Y nunca estarás "
            "solo nuevamente. Esta es la victoria más importante de todas.",
            "tim_final_emotivo_familia.png"
)
        self.historia["tim_dificil_final_emotivo"] = tim_dificil_final_emotivo

        tim_dificil_final_estrategico = NodoHistoria(
            "tim_dificil_final_estrategico",
            "FINAL ESTRATÉGICO: MAESTRO TÁCTICO",
            "Tu derrota de Ra's al Ghul se estudia en academias militares y escuelas de estrategia alrededor "
            "del mundo. No fue victoria de fuerza, sino de planificación perfecta. Anticipaste cada movimiento. "
            "Coordinaste recursos limitados contra enemigo superior. Convertiste debilidades en fortalezas. "
            "Usaste psicología tanto como táctica. Es caso de estudio perfecto en maestría estratégica. "
            "Pero lo que te distingue no es solo que ganaste. Es que ganaste sin bajas, sin cruzar líneas "
            "éticas, sin sacrificar valores. Demostraste que es posible ser estratega brillante y héroe moral "
            "simultáneamente. Bruce Wayne fue detective brillante, pero a veces su brillantez venía con costo "
            "moral. Tú encontraste balance. Tu legado es probar que estrategia y moralidad no son opuestas; "
            "se complementan. Red Robin, Maestro Táctico, el estratega que nunca comprometió valores para "
            "lograr victoria. Es legado que durará generaciones.",
            "tim_final_estrategico_tactico.png"
)
        self.historia["tim_dificil_final_estrategico"] = tim_dificil_final_estrategico

        tim_dificil_final_perfecto = NodoHistoria(
            "tim_dificil_final_perfecto",
            "FINAL PERFECTO: SIN BAJAS",
            "Lo imposible se hizo realidad: victoria perfecta sin una sola baja. Cada objetivo protegido. Cada "
            "asesino capturado vivo. Cada plan frustrado sin violencia excesiva. Es logro que ni Batman mismo "
            "logró consistentemente. Cuando los reporteros preguntan cómo lo hiciste, respondes: 'Planificación "
            "meticulosa, coordinación perfecta, y nunca olvidar que proteger vida es más importante que derrotar "
            "enemigos.' Se convierte en mantra para nueva generación de héroes. La comunidad heroica te estudia. "
            "Jóvenes aspirantes a héroes memorizan tus tácticas. Veteranos respetan tu método. Has redefinido "
            "lo que significa ser héroe. No es sobre golpear más fuerte o ser más rápido. Es sobre ser más "
            "inteligente, más coordinado, y nunca perder de vista el valor de cada vida. Red Robin, el héroe "
            "perfecto, quien probó que es posible ganar sin bajas. Bruce Wayne estaría más que orgulloso. "
            "Estaría asombrado. Has superado al maestro.",
            "tim_final_perfecto_sin_bajas.png"
)
        self.historia["tim_dificil_final_perfecto"] = tim_dificil_final_perfecto

        tim_dificil_final_victorioso = NodoHistoria(
            "tim_dificil_final_victorioso",
            "FINAL VICTORIOSO: HÉROE CONSOLIDADO",
            "Tu victoria sobre Ra's al Ghul consolida tu estatus como héroe de primer nivel. Ya no hay dudas. "
            "Ya no hay 'ex-Robin' o 'aprendiz de Batman'. Eres Red Robin, héroe consolidado con credenciales "
            "impecables. Derrotaste a uno de los enemigos más peligrosos de Batman. Salvaste la Bat-Familia "
            "completa. Coordinaste defensa perfecta de Gotham. Y lo hiciste con estilo propio, no imitando a "
            "Batman. La Liga de la Justicia te ofrece membresía asociada. Los Titans te confirman como líder. "
            "Gotham te acepta como protector legítimo. Y lo más importante, tú te aceptas a ti mismo. Ya no "
            "hay duda interna. Ya no hay cuestionamiento. Eres héroe, detective, líder, estratega. Eres Red "
            "Robin, y ese nombre tiene peso propio. La búsqueda de Bruce Wayne continúa, pero ahora desde "
            "posición de fortaleza. No eres niño buscando padre desaparecido. Eres héroe consolidado honrando "
            "legado de mentor. Y cuando Bruce regrese, te encontrará no como aprendiz, sino como colega.",
            "tim_final_victorioso_consolidado.png"
)
        self.historia["tim_dificil_final_victorioso"] = tim_dificil_final_victorioso

        tim_dificil_final_filosofico = NodoHistoria(
            "tim_dificil_final_filosofico",
            "FINAL FILOSÓFICO: ENTENDIMIENTO MUTUO",
            "Tu conversación con Ra's al Ghul cambió tu perspectiva. Viste que incluso los enemigos más grandes "
            "tienen motivaciones comprensibles. Ra's atacó por dolor, no por maldad pura. Esa comprensión no "
            "excusa sus acciones, pero humaniza la lucha. Regresas a la Bat-Familia con nueva sabiduría: "
            "'No todos los enemigos son monstruos. Algunos son personas rotas que eligieron caminos oscuros.' "
            "Esta filosofía te diferencia de Batman. Bruce veía el mundo en blanco y negro. Tú ves matices. "
            "Y esos matices te hacen héroe más efectivo. Puedes negociar donde Bruce pelearía. Puedes entender "
            "donde Bruce juzgaría. Puedes encontrar soluciones pacíficas donde Bruce usaría fuerza. No eres "
            "ingenuo; conoces cuando pelear. Pero siempre intentas entender primero. Red Robin, el filósofo "
            "héroe, quien entiende que verdadera victoria no es derrotar enemigos, sino entender por qué existen "
            "enemigos. Es lección que cambiará heroísmo para siempre.",
            "tim_final_filosofico_entendimiento.png"
)
        self.historia["tim_dificil_final_filosofico"] = tim_dificil_final_filosofico

        tim_dificil_final_ascendente = NodoHistoria(
            "tim_dificil_final_ascendente",
            "FINAL ASCENDENTE: CAMINO A LA LIGA",
            "La oferta de Superman es clara: 'Red Robin, la Liga de la Justicia necesita mentes como la tuya. "
            "Cuando estés listo, hay un lugar para ti.' Es reconocimiento supremo. De aprendiz de Batman a "
            "candidato de la Liga de la Justicia. El camino ha sido largo y doloroso. Perdiste el manto de "
            "Robin. Fuiste rechazado por la familia. Viajaste solo por el mundo. Enfrentaste a Ra's al Ghul. "
            "Pero cada desafío te forjó más fuerte. Ahora estás en la cúspide de grandeza heroica. Pocos "
            "héroes llegan a la Liga de la Justicia antes de los 25 años. Tú lo lograste a los 19. No por "
            "poderes, sino por cerebro. No por fuerza, sino por estrategia. No por ser invencible, sino por "
            "hacer lo imposible trabajando con otros. Aceptas la oferta con condición: 'Primero encontraré "
            "a Bruce Wayne. Luego me uniré a la Liga.' Superman sonríe: 'Lealtad como esa es exactamente por "
            "qué te queremos.' Red Robin asciende, y el cielo ya no es el límite.",
            "tim_final_ascendente_liga.png"
)
        self.historia["tim_dificil_final_ascendente"] = tim_dificil_final_ascendente

        tim_dificil_final_colaborativo = NodoHistoria(
            "tim_dificil_final_colaborativo",
            "FINAL COLABORATIVO: ASOCIACIÓN PERFECTA",
            "Tu asociación con Barbara Gordon se vuelve legendaria. Detective y Oracle, mente táctica y mente "
            "digital, trabajando en sincronía perfecta. Juntos, son imparables. Resuelven casos que otros "
            "consideran imposibles. Coordinan operaciones que requieren precisión milimétrica. Y lo más "
            "importante, se complementan perfectamente. Donde tú ves tácticas físicas, ella ve soluciones "
            "digitales. Donde ella identifica patrones en datos, tú identificas patrones en comportamiento. "
            "Otras asociaciones heroicas toman nota. Equipos que antes operaban con jerarquía clara ahora "
            "adoptan modelo de asociación igualitaria. 'El Modelo Red Robin-Oracle' se enseña en academias "
            "de héroes: dos expertos diferentes trabajando como iguales hacia objetivo común. No líder y "
            "seguidor, sino socios. Bruce Wayne trabajó con Barbara, pero siempre como Batman líder y Oracle "
            "apoyo. Tú trabajas con ella como iguales. Y esa igualdad es tu fortaleza. Red Robin y Oracle, "
            "la asociación perfecta que redefinió trabajo en equipo heroico.",
            "tim_final_colaborativo_oracle.png"
)
        self.historia["tim_dificil_final_colaborativo"] = tim_dificil_final_colaborativo

        tim_dificil_final_global = NodoHistoria(
            "tim_dificil_final_global",
            "FINAL GLOBAL: RECONOCIMIENTO MUNDIAL",
            "Tu victoria sobre Ra's al Ghul resuena globalmente. No fue batalla local de Gotham. Fue victoria "
            "contra organización internacional (la Liga de Asesinos) que amenazaba ciudad estadounidense. "
            "Gobiernos toman nota. Naciones Unidas te invita a consultoría de seguridad. Interpol solicita "
            "asesoría sobre amenazas globales. De repente, Red Robin no es solo héroe de Gotham o Estados "
            "Unidos. Es figura heroica global. Viajas por el mundo, no solo buscando a Bruce, sino ayudando "
            "a establecer redes de héroes en otros países. El 'Modelo Red Robin' de coordinación heroica se "
            "adopta en Europa, Asia, África. Cada continente desarrolla su propia red de héroes coordinados. "
            "Y todos te reconocen como arquitecto del sistema. En pocos meses, pasaste de ser 'ex-Robin' a "
            "ser 'Red Robin, coordinador global de héroes'. Es ascenso meteórico basado puramente en resultados. "
            "Bruce Wayne fue símbolo de Gotham. Tú eres símbolo global. Y tu leyenda apenas comienza.",
            "tim_final_global_mundial.png"
)
        self.historia["tim_dificil_final_global"] = tim_dificil_final_global

        tim_dificil_final_magistral = NodoHistoria(
            "tim_dificil_final_magistral",
            "FINAL MAGISTRAL: EL PROTECTOR",
            "Tu cita a Ra's al Ghul se vuelve famosa: 'Tú peleaste para destruir. Yo peleé para proteger. Y "
            "la protección siempre supera a la destrucción cuando tienes el equipo correcto.' Es filosofía "
            "que define nueva era de heroísmo. No se trata de ser más fuerte o más peligroso que villanos. "
            "Se trata de ser mejor protector. Y proteger no es trabajo solitario; requiere comunidad. "
            "Estableces formalmente la 'Red Robin Protection Network' - sistema global de héroes coordinados "
            "enfocados en protección preventiva en lugar de castigo reactivo. Es revolucionario. Crimen "
            "disminuye en ciudades que adoptan el sistema. Vidas se salvan. Comunidades se fortalecen. Y todo "
            "porque rechazaste modelo de héroe solitario vengativo. Bruce Wayne fue vengador. Tú eres protector. "
            "Y resulta que proteger es más efectivo que vengar. Cuando Bruce Wayne regrese y vea lo que "
            "construiste, comprenderá que su legado no solo sobrevivió; evolucionó. Red Robin, El Protector, "
            "el héroe que probó que amor supera a miedo.",
            "tim_final_magistral_protector.png"
)
        self.historia["tim_dificil_final_magistral"] = tim_dificil_final_magistral

        tim_dificil_priorizar = NodoHistoria(
            "tim_dificil_priorizar",
            "DECISIONES IMPOSIBLES",
            "Decides priorizar. Alfred es el más vulnerable en la Mansión Wayne. Lucius tiene seguridad "
            "corporativa pero necesita refuerzo. Barbara puede defenderse mejor que la mayoría. Haces "
            "cálculos fríos sobre quién tiene más probabilidades de sobrevivir sin tu ayuda. Son decisiones "
            "que nunca quisiste tomar. Pero alguien tiene que hacerlas.",
            "tim_decisiones_imposibles.png"
)
        tim_dificil_priorizar.agregar_opcion("Proteger a Alfred primero", "tim_dificil_proteger_alfred", stat="recursos", cambio=2)
        tim_dificil_priorizar.agregar_opcion("Establecer perímetro en Wayne Enterprises", "tim_dificil_wayne_enterprises", stat="recursos", cambio=3)
        self.historia["tim_dificil_priorizar"] = tim_dificil_priorizar

        tim_dificil_intentar_todo = NodoHistoria(
            "tim_dificil_intentar_todo",
            "SOBRECARGA HEROICA",
            "Intentas proteger a todos simultáneamente. Estableces trampas en la Mansión Wayne, luego corres "
            "a Wayne Enterprises, luego a la torre de Barbara. Estás en constante movimiento, agotándote. "
            "Detectas el primer ataque contra Alfred justo a tiempo y lo repeles. Pero mientras lo haces, "
            "los asesinos atacan a Lucius. No puedes estar en dos lugares a la vez. Estás fallando.",
            "tim_sobrecarga_heroica.png"
)
        tim_dificil_intentar_todo.agregar_opcion("Llamar a los Titans desesperadamente", "tim_dificil_llamada_desesperada", stat="salud", cambio=-15)
        tim_dificil_intentar_todo.agregar_opcion("Continuar solo y esperar lo mejor", "tim_dificil_game_over", stat="salud", cambio=-30)
        self.historia["tim_dificil_intentar_todo"] = tim_dificil_intentar_todo

        tim_dificil_defensa_coordinada = NodoHistoria(
            "tim_dificil_defensa_coordinada",
            "EL TABLERO DE AJEDREZ",
            "Con los Titans a tu lado, organizas una defensa perfecta. Superboy protege a Alfred. Wonder Girl "
            "está con Lucius. Kid Flash patrulla múltiples ubicaciones a velocidad. Tú coordinas todo desde "
            "un centro de comando móvil, monitoreando cada objetivo. Cuando la Liga de Asesinos ataca, están "
            "listos. Cada ninja es interceptado. Es una ejecución táctica perfecta.",
            "tim_tablero_de_ajedrez.png"
)
        tim_dificil_defensa_coordinada.agregar_opcion("Enfrentar a Ra's personalmente", "tim_dificil_enfrentamiento_ras", stat="reputacion", cambio=20)
        self.historia["tim_dificil_defensa_coordinada"] = tim_dificil_defensa_coordinada

        tim_dificil_esperar_dick = NodoHistoria(
            "tim_dificil_esperar_dick",
            "EL RELOJ CORRE",
            "Esperas la respuesta de Dick, pero los minutos se convierten en horas. Finalmente, te contacta: "
            "'Tim, revisé tu evidencia. Es... convincente. Estoy implementando protocolos de seguridad ahora.' "
            "Pero ha pasado demasiado tiempo. Los asesinos ya están en posición. Necesitas coordinar con Dick "
            "rápidamente o algunos objetivos quedarán desprotegidos.",
            "tim_reloj_corre.png"
)
        tim_dificil_esperar_dick.agregar_opcion("Coordinar con Dick", "tim_dificil_coordinacion_dick", stat="reputacion", cambio=15)
        self.historia["tim_dificil_esperar_dick"] = tim_dificil_esperar_dick

        tim_dificil_sin_esperar = NodoHistoria(
            "tim_dificil_sin_esperar",
            "ACCIÓN INMEDIATA",
            "No esperas la aprobación de Dick. Comienzas a implementar defensas inmediatamente con la ayuda "
            "de Barbara. Ella coordina con los contactos de GCPD para proteger a Jim Gordon. Tú estableces "
            "sistemas de seguridad en la Mansión Wayne. Cuando Dick finalmente responde, ya has hecho el "
            "trabajo pesado. 'Debiste confiar en mí desde el principio,' le dices.",
            "tim_accion_inmediata.png"
)
        tim_dificil_sin_esperar.agregar_opcion("Preparar la confrontación final", "tim_dificil_preparacion_final", stat="reputacion", cambio=10)
        self.historia["tim_dificil_sin_esperar"] = tim_dificil_sin_esperar

        tim_dificil_explicar_plan = NodoHistoria(
            "tim_dificil_explicar_plan",
            "LA ESTRATEGIA REVELADA",
            "Le explicas tu plan completo a Barbara: 'Ra's atacará simultáneamente. Necesitamos dividir "
            "recursos. Titans aquí, Bat-Familia allá. Yo coordinaré desde el centro.' Barbara analiza el "
            "plan: 'Es brillante, Tim. Complejo, pero factible. Necesitaré convencer a Dick rápidamente.' "
            "Juntos, presentan el plan a la familia. Esta vez, Dick escucha.",
            "tim_estrategia_revelada.png"
)
        tim_dificil_explicar_plan.agregar_opcion("Implementar con el apoyo familiar", "tim_dificil_apoyo_familiar", stat="reputacion", cambio=20)
        self.historia["tim_dificil_explicar_plan"] = tim_dificil_explicar_plan

        tim_dificil_mansion_wayne = NodoHistoria(
            "tim_dificil_mansion_wayne",
            "REGRESO A CASA",
            "Llegas a la Mansión Wayne. Alfred te recibe: 'Master Timothy, ha regresado.' Le adviertes del "
            "peligro inminente. Alfred simplemente asiente: 'Entonces debemos prepararnos.' Juntos, activan "
            "los sistemas de defensa de la mansión que Bruce instaló. Pero sabes que no será suficiente contra "
            "toda la Liga de Asesinos. Necesitas más ayuda.",
            "tim_regreso_a_casa.png"
)
        tim_dificil_mansion_wayne.agregar_opcion("Fortificar la mansión", "tim_dificil_fortificar", stat="recursos", cambio=3)
        tim_dificil_mansion_wayne.agregar_opcion("Evacuar a Alfred", "tim_dificil_evacuar_alfred", stat="recursos", cambio=2)
        self.historia["tim_dificil_mansion_wayne"] = tim_dificil_mansion_wayne

        tim_dificil_contacto_barbara = NodoHistoria(
            "tim_dificil_contacto_barbara",
            "LA ALIANZA CON ORACLE",
            "Contactas a Barbara (Oracle) desde el aeropuerto. Ella responde inmediatamente: 'Tim, recibí "
            "tu archivo. Lo he estado analizando. Es... preocupante.' '¿Me crees?' preguntas. 'Sí,' dice "
            "simplemente. 'Necesitamos coordinar. Ven a mi torre.' Finalmente, tienes un aliado en Gotham.",
            "tim_alianza_con_oracle.png"
)
        tim_dificil_contacto_barbara.agregar_opcion("Ir a la torre de Barbara", "tim_dificil_torre_barbara", stat="reputacion", cambio=10)
        self.historia["tim_dificil_contacto_barbara"] = tim_dificil_contacto_barbara

        tim_dificil_continuar_herido = NodoHistoria(
            "tim_dificil_continuar_herido",
            "HERIDO PERO DECIDIDO",
            "Continúas tu misión a pesar de las heridas. Cada movimiento duele, pero el dolor te mantiene "
            "enfocado. Logras llegar a Gotham y comenzar las defensas, aunque tu efectividad está disminuida. "
            "Durante una confrontación con ninjas, tus heridas casi te cuestan la vida. Superboy llega justo "
            "a tiempo para salvarte. 'Tim, necesitas descansar,' dice. 'Después,' respondes.",
            "tim_herido_pero_decidido.png"
        )
        tim_dificil_continuar_herido.agregar_opcion("Aceptar ayuda médica de Superboy", "tim_dificil_ayuda_medica", stat="salud", cambio=10)
        self.historia["tim_dificil_continuar_herido"] = tim_dificil_continuar_herido

        tim_dificil_mas_alla_limites = NodoHistoria(
            "tim_dificil_mas_alla_limites",
            "LÍMITES ROTOS",
            "Empujas tu cuerpo más allá de todo límite razonable. La adrenalina y la determinación pura te "
            "mantienen en movimiento. Logras establecer defensas básicas, pero tu cuerpo finalmente colapsa. "
            "Te despiertas en la enfermería de los Titans con Superboy y Wonder Girl mirándote preocupados. "
            "'Casi mueres, Tim,' dice Cassie. 'Valió la pena,' murmuras. 'La familia está a salvo.'",
            "tim_limites_rotos.png"
        )
        tim_dificil_mas_alla_limites.agregar_opcion("Recuperarte con los Titans", "tim_dificil_recuperacion_titans", stat="salud", cambio=15)
        self.historia["tim_dificil_mas_alla_limites"] = tim_dificil_mas_alla_limites

        tim_dificil_escape_advertencia = NodoHistoria(
            "tim_dificil_escape_advertencia",
            "ESCAPE CON PROPÓSITO",
            "Escapas de Ra's con información vital sobre sus planes y cronograma. Ahora sabes exactamente "
            "cuándo atacará: en 48 horas. Es tiempo suficiente para preparar defensas si actúas rápido. "
            "Contactas a todos tus aliados, esta vez con detalles específicos que hacen tu advertencia "
            "imposible de ignorar. La carrera contra el tiempo ha comenzado.",
            "tim_escape_con_proposito.png"
        )
        tim_dificil_escape_advertencia.agregar_opcion("Organizar la defensa final", "tim_dificil_defensa_final", stat="recursos", cambio=3)
        self.historia["tim_dificil_escape_advertencia"] = tim_dificil_escape_advertencia

        tim_dificil_aprovechar_libertad = NodoHistoria(
            "tim_dificil_aprovechar_libertad",
            "LIBERTAD TÁCTICA",
            "Ra's te dejó ir deliberadamente, confiando en que harás la misión más interesante. Aprovechas "
            "esta libertad para preparar una trampa elaborada. Si Ra's quiere un desafío, lo tendrá. Pero "
            "será un desafío diseñado específicamente para exponer cada debilidad en su plan. Comienzas a "
            "contactar no solo a la Bat-Familia, sino a toda la comunidad de héroes de Gotham.",
            "tim_libertad_tactica.png"
        )
        tim_dificil_aprovechar_libertad.agregar_opcion("Construir una red de defensores", "tim_dificil_red_defensores", stat="reputacion", cambio=15)
        self.historia["tim_dificil_aprovechar_libertad"] = tim_dificil_aprovechar_libertad

        tim_dificil_organizar_equipo = NodoHistoria(
            "tim_dificil_organizar_equipo",
            "EL LÍDER EMERGE",
            "Organizas tu equipo como un general preparando para batalla. Superboy tiene fuerza bruta para "
            "proteger objetivos clave. Wonder Girl tiene habilidad de combate para enfrentar asesinos elite. "
            "Kid Flash tiene velocidad para responder a múltiples amenazas. Red Hood tiene la crueldad necesaria "
            "para luchar contra la Liga. Y tú tienes el cerebro para coordinar todo. 'Así es como se hace,' "
            "piensas. 'Con amigos.'",
            "tim_lider_emerge.png"
        )
        tim_dificil_organizar_equipo.agregar_opcion("Ejecutar el plan de defensa", "tim_dificil_ejecucion_plan", stat="reputacion", cambio=20)
        self.historia["tim_dificil_organizar_equipo"] = tim_dificil_organizar_equipo

        tim_dificil_implementar_solo = NodoHistoria(
            "tim_dificil_implementar_solo",
            "EL LOBO SOLITARIO",
            "Intentas implementar tu plan solo, pero rápidamente te das cuenta de la imposibilidad. Estás "
            "estableciendo defensas en la Mansión Wayne cuando recibes alerta de un ataque en Wayne Enterprises. "
            "Corres allí, pero entonces Barbara informa de asesinos en su torre. No puedes estar en todos "
            "lados. Estás fallando, y lo sabes. Necesitas ayuda, pero tu orgullo te lo impide.",
            "tim_lobo_solitario.png"
        )
        tim_dificil_implementar_solo.agregar_opcion("Tragarte el orgullo y pedir ayuda", "tim_dificil_pedir_ayuda_final", stat="reputacion", cambio=10)
        tim_dificil_implementar_solo.agregar_opcion("Continuar solo hasta el colapso", "tim_dificil_colapso", stat="salud", cambio=-25)
        self.historia["tim_dificil_implementar_solo"] = tim_dificil_implementar_solo

        tim_dificil_buscar_ayuda_implementar = NodoHistoria(
            "tim_dificil_buscar_ayuda_implementar",
            "HUMILDAD Y SABIDURÍA",
            "Reconoces que necesitas ayuda. Contactas a Stephanie Brown (Batgirl): '¿Recuerdas cuando me "
            "dijiste que mi problema es que pienso que puedo hacer todo solo? Tenías razón. Necesito ayuda.' "
            "Ella responde inmediatamente: 'Estoy en camino.' Luego contactas a Cassie, Conner, Bart. Todos "
            "responden. Esta vez, no estás solo.",
            "tim_humildad_sabiduria.png"
        )
        tim_dificil_buscar_ayuda_implementar.agregar_opcion("Coordinar el equipo completo", "tim_dificil_coordinacion_completa", stat="reputacion", cambio=20)
        self.historia["tim_dificil_buscar_ayuda_implementar"] = tim_dificil_buscar_ayuda_implementar

        tim_dificil_caso_rapido = NodoHistoria(
            "tim_dificil_caso_rapido",
            "CINCO MINUTOS PARA CONVENCER",
            "Presentas tu caso con precisión quirúrgica: 'Ra's al Ghul está en Europa. Confirmé su presencia. "
            "Planea ataques simultáneos contra ocho objetivos esta noche. Alfred, Barbara, Lucius, Commissioner "
            "Gordon, Selina, y ustedes dos. Tengo evidencia, testimonios, y un cronograma. ¿Van a escuchar "
            "o van a arriesgar vidas por orgullo?' El silencio es tenso. Dick mira la evidencia.",
            "tim_cinco_minutos.png"
        )
        tim_dificil_caso_rapido.agregar_opcion("Esperar el veredicto de Dick", "tim_dificil_veredicto_dick", stat="reputacion", cambio=5)
        self.historia["tim_dificil_caso_rapido"] = tim_dificil_caso_rapido

        tim_dificil_proteger_alfred = NodoHistoria(
            "tim_dificil_proteger_alfred",
            "EL CORAZÓN DE LA FAMILIA",
            "Priorizas a Alfred porque él es el corazón de la Bat-Familia. Sin él, la familia se desmorona. "
            "Estableces defensas elaboradas en la Mansión Wayne. Cuando los ninjas atacan, están listos para "
            "una mansión desprotegida. En su lugar, encuentran trampas, sistemas de seguridad militares, y "
            "un Red Robin muy motivado. Repeles el ataque, pero escuchas de ataques en otros lugares.",
            "tim_corazon_familia.png"
        )
        tim_dificil_proteger_alfred.agregar_opcion("Responder a otros ataques", "tim_dificil_respuesta_multiple", stat="salud", cambio=-10)
        self.historia["tim_dificil_proteger_alfred"] = tim_dificil_proteger_alfred

        tim_dificil_wayne_enterprises = NodoHistoria(
            "tim_dificil_wayne_enterprises",
            "PROTEGIENDO EL LEGADO",
            "Estableces perímetro en Wayne Enterprises. Lucius Fox te recibe: 'Mr. Drake, me alegra verlo.' "
            "Le explicas la situación. Lucius, pragmático como siempre, activa protocolos de seguridad "
            "corporativos y te da acceso a tecnología de Wayne Enterprises. Juntos, convierten el edificio "
            "en una fortaleza. Cuando los ninjas atacan, no están preparados para la tecnología de Batman.",
            "tim_protegiendo_legado.png"
        )
        tim_dificil_wayne_enterprises.agregar_opcion("Defender el edificio", "tim_dificil_defensa_edificio", stat="recursos", cambio=3)
        self.historia["tim_dificil_wayne_enterprises"] = tim_dificil_wayne_enterprises

        tim_dificil_llamada_desesperada = NodoHistoria(
            "tim_dificil_llamada_desesperada",
            "S.O.S.",
            "Haces una llamada desesperada a los Titans: 'Necesito ayuda. Ahora. Múltiples ubicaciones en "
            "Gotham bajo ataque.' Superboy responde: 'En camino.' Wonder Girl: 'Dos minutos.' Kid Flash: "
            "'Ya estoy ahí.' Tus amigos llegan como la caballería. Juntos, logran repeler los ataques y "
            "salvar a todos. Después, Conner te abraza: 'Siempre pide ayuda más temprano, Tim.'",
            "tim_sos.png"
        )
        tim_dificil_llamada_desesperada.agregar_opcion("Enfrentar a Ra's con respaldo", "tim_dificil_respaldo_titans", stat="reputacion", cambio=15)
        self.historia["tim_dificil_llamada_desesperada"] = tim_dificil_llamada_desesperada

        tim_dificil_game_over = NodoHistoria(
            "tim_dificil_game_over",
            "GAME OVER: EL PRECIO DEL ORGULLO",
            "Intentas hacerlo todo solo. Es demasiado. Los ataques vienen simultáneamente. Salvas a Alfred "
            "pero Lucius es herido gravemente. Proteges Wayne Enterprises pero los asesinos llegan a la torre "
            "de Barbara. Cada éxito viene con una falla en otro lugar. Cuando el polvo se asienta, has salvado "
            "algunas vidas pero perdido otras. Dick te confronta: 'Si hubieras pedido ayuda desde el principio...' "
            "No puede terminar la oración. Has fallado. La lección es clara: ningún héroe puede hacerlo todo solo.",
            "tim_game_over_orgullo.png"
        )
        # Este es un final malo sin opciones adicionales
        self.historia["tim_dificil_game_over"] = tim_dificil_game_over

        tim_dificil_enfrentamiento_ras = NodoHistoria(
            "tim_dificil_enfrentamiento_ras",
            "EL DETECTIVE VS EL DEMONIO",
            "Con todos los objetivos protegidos, confrontas a Ra's al Ghul personalmente. Él te espera en "
            "un edificio abandonado, rodeado de sus ninjas derrotados. 'Impresionante, Timothy Drake,' dice. "
            "'Anticipaste cada movimiento. Protegiste a todos. Coordinaste recursos perfectamente. Dime, "
            "¿cómo lo lograste?' Sonríes: 'Simple. Hice algo que tú nunca harías. Pedí ayuda.'",
            "tim_detective_vs_demonio.png"
        )
        tim_dificil_enfrentamiento_ras.agregar_opcion("Duelar con Ra's", "tim_dificil_duelo_final", stat="salud", cambio=-15)
        tim_dificil_enfrentamiento_ras.agregar_opcion("Revelación estratégica", "tim_dificil_revelacion", stat="reputacion", cambio=25)
        self.historia["tim_dificil_enfrentamiento_ras"] = tim_dificil_enfrentamiento_ras

        tim_dificil_coordinacion_dick = NodoHistoria(
            "tim_dificil_coordinacion_dick",
            "FAMILIA UNIDA",
            "Coordinas con Dick, quien finalmente confía en ti. 'Tim, lamento no haberte creído antes,' "
            "dice. 'Pero ahora estamos juntos en esto.' Trabajan como la perfecta máquina que son: Dick y "
            "Damian protegen el lado este de Gotham, tú y los Titans el oeste. Barbara coordina desde su "
            "torre. Es la Bat-Familia operando a máxima capacidad. Los asesinos no tienen oportunidad.",
            "tim_familia_unida.png"
        )
        tim_dificil_coordinacion_dick.agregar_opcion("Victoria familiar", "tim_dificil_victoria_familiar", stat="reputacion", cambio=25)
        self.historia["tim_dificil_coordinacion_dick"] = tim_dificil_coordinacion_dick

        tim_dificil_preparacion_final = NodoHistoria(
            "tim_dificil_preparacion_final",
            "LA CALMA ANTES DE LA TORMENTA",
            "Has preparado todo lo que puedes. Sistemas de seguridad, equipos coordinados, planes de contingencia. "
            "Ahora solo esperas. Alfred te sirve té: 'Master Timothy, independientemente del resultado, sepa "
            "que el Maestro Bruce estaría orgulloso.' Esas palabras te dan fuerza. Cuando los asesinos finalmente "
            "atacan, están caminando hacia una trampa perfectamente preparada.",
            "tim_calma_antes_tormenta.png"
        )
        tim_dificil_preparacion_final.agregar_opcion("Ejecutar la defensa perfecta", "tim_dificil_defensa_perfecta", stat="reputacion", cambio=20)
        self.historia["tim_dificil_preparacion_final"] = tim_dificil_preparacion_final

        tim_dificil_apoyo_familiar = NodoHistoria(
            "tim_dificil_apoyo_familiar",
            "REDENCIÓN Y RESPETO",
            "Con el apoyo de la Bat-Familia completa, implementan tu plan perfectamente. Dick se disculpa: "
            "'Tim, debí confiar en ti desde el principio. Eres un Detective, como Bruce.' Damian incluso "
            "gruñe una aprobación. Barbara coordina magistralmente. Cuando Ra's ataca, encuentra no solo "
            "resistencia sino una familia unida que anticipó cada movimiento. Es tu momento de triunfo.",
            "tim_redencion_respeto.png"
        )
        tim_dificil_apoyo_familiar.agregar_opcion("Confrontación final con Ra's", "tim_dificil_confrontacion_final", stat="reputacion", cambio=30)
        self.historia["tim_dificil_apoyo_familiar"] = tim_dificil_apoyo_familiar

# Continuaré con más nodos...

        tim_dificil_fortificar = NodoHistoria(
            "tim_dificil_fortificar",
            "FORTALEZA WAYNE",
            "Trabajas con Alfred para convertir la Mansión Wayne en una fortaleza impenetrable. Activan "
            "sistemas de defensa que Bruce instaló para exactamente este tipo de situación. Sensores perimetrales, "
            "barreras reforzadas, rutas de escape secretas. Alfred comenta: 'El Maestro Bruce siempre planeaba "
            "para lo peor.' La mansión está lista. Ahora solo falta esperar a los asesinos.",
            "tim_fortaleza_wayne.png"
        )
        tim_dificil_fortificar.agregar_opcion("Emboscar a los atacantes", "tim_dificil_emboscada", stat="recursos", cambio=3)
        self.historia["tim_dificil_fortificar"] = tim_dificil_fortificar

        tim_dificil_evacuar_alfred = NodoHistoria(
            "tim_dificil_evacuar_alfred",
            "LA EVACUACIÓN",
            "Decides que la mejor defensa es evacuar a Alfred a una ubicación segura. Él protesta: 'Master "
            "Timothy, no abandonaré la casa Wayne.' 'No es abandono, Alfred. Es estrategia,' respondes. "
            "Lo llevas a un refugio seguro que solo tú conoces, luego regresas para enfrentar a los asesinos "
            "en tus propios términos. Sin rehenes, tienes más libertad táctica.",
            "tim_evacuacion_alfred.png"
        )
        tim_dificil_evacuar_alfred.agregar_opcion("Regresar y tender trampa", "tim_dificil_trampa_mansion", stat="recursos", cambio=2)
        self.historia["tim_dificil_evacuar_alfred"] = tim_dificil_evacuar_alfred

        tim_dificil_torre_barbara = NodoHistoria(
            "tim_dificil_torre_barbara",
            "CENTRO DE OPERACIONES",
            "La torre de Barbara se convierte en tu centro de operaciones. Ella tiene sistemas de vigilancia "
            "de toda la ciudad. Juntos, mapean cada ubicación de la Liga de Asesinos en Gotham. 'Son más "
            "de los que pensábamos,' dice Barbara. 'Ra's trajo un ejército.' Pero con información completa, "
            "pueden planear defensas precisas. Es ventaja del detective sobre fuerza bruta.",
            "tim_centro_operaciones.png"
        )
        tim_dificil_torre_barbara.agregar_opcion("Coordinar defensa desde la torre", "tim_dificil_comando_central", stat="reputacion", cambio=15)
        self.historia["tim_dificil_torre_barbara"] = tim_dificil_torre_barbara

        tim_dificil_ayuda_medica = NodoHistoria(
            "tim_dificil_ayuda_medica",
            "SANANDO CON AMIGOS",
            "Aceptas la ayuda médica de Superboy, quien te lleva a la enfermería de los Titans. Wonder Girl "
            "trata tus heridas mientras Bart hace guardia. 'No puedes salvar a nadie si estás muerto,' dice "
            "Cassie. Tienes razón. En pocas horas, estás recuperado lo suficiente para continuar. Y esta vez, "
            "no estarás solo. Los Titans insisten en ayudarte.",
            "tim_sanando_con_amigos.png"
        )
        tim_dificil_ayuda_medica.agregar_opcion("Regresar a la misión con los Titans", "tim_dificil_mision_titans", stat="salud", cambio=15)
        self.historia["tim_dificil_ayuda_medica"] = tim_dificil_ayuda_medica

        tim_dificil_recuperacion_titans = NodoHistoria(
            "tim_dificil_recuperacion_titans",
            "LECCIONES APRENDIDAS",
            "Te recuperas rodeado de los Titans. Conner te dice: 'Tim, eres el cerebro del equipo. Pero "
            "incluso el cerebro necesita un cuerpo funcional.' Cassie añade: 'Y no puedes hacer todo solo. "
            "Por eso tenemos un equipo.' Es una lección que Bruce nunca aprendió completamente. Pero tú sí. "
            "Cuando estás recuperado, regresas a Gotham con un ejército de amigos.",
            "tim_lecciones_aprendidas.png"
        )
        tim_dificil_recuperacion_titans.agregar_opcion("Liderar a los Titans en Gotham", "tim_dificil_liderar_titans", stat="reputacion", cambio=20)
        self.historia["tim_dificil_recuperacion_titans"] = tim_dificil_recuperacion_titans

        tim_dificil_defensa_final = NodoHistoria(
            "tim_dificil_defensa_final",
            "LA NOCHE DEL ASEDIO",
            "La noche del ataque llega. Has preparado todo: cada objetivo protegido, cada aliado en posición, "
            "cada contingencia planeada. Cuando los asesinos atacan simultáneamente, encuentran resistencia "
            "coordinada en cada ubicación. Superboy repele el ataque a Alfred. Wonder Girl protege a Lucius. "
            "Kid Flash evacúa a Gordon. Y tú coordinas todo, anticipando cada movimiento de Ra's.",
            "tim_noche_del_asedio.png"
        )
        tim_dificil_defensa_final.agregar_opcion("Buscar a Ra's durante el caos", "tim_dificil_buscar_ras", stat="recursos", cambio=3)
        self.historia["tim_dificil_defensa_final"] = tim_dificil_defensa_final

        tim_dificil_red_defensores = NodoHistoria(
            "tim_dificil_red_defensores",
            "LA RED SE EXTIENDE",
            "No te limitas a la Bat-Familia. Contactas a Huntress, Black Canary, Question, y otros héroes "
            "de Gotham. Explicas la situación y cada uno acepta proteger un objetivo. Ra's planeaba atacar "
            "una ciudad dividida. En su lugar, encuentra una comunidad de héroes unida. 'Esto es lo que "
            "Bruce construyó,' piensas. 'No solo un símbolo, sino una red.'",
            "tim_red_defensores.png"
        )
        tim_dificil_red_defensores.agregar_opcion("Coordinar la red completa", "tim_dificil_coordinacion_total", stat="reputacion", cambio=25)
        self.historia["tim_dificil_red_defensores"] = tim_dificil_red_defensores

        tim_dificil_ejecucion_plan = NodoHistoria(
            "tim_dificil_ejecucion_plan",
            "EJECUCIÓN PERFECTA",
            "El plan se ejecuta como un reloj suizo. Cada miembro del equipo cumple su rol perfectamente. "
            "Los asesinos son repelidos en cada ubicación antes de que puedan causar daño real. Ra's observa "
            "desde la distancia, su plan desmoronándose. Envía un mensaje: 'Bien jugado, Detective. Pero "
            "esto no ha terminado.' Has ganado esta batalla, pero la guerra continúa.",
            "tim_ejecucion_perfecta.png"
        )
        tim_dificil_ejecucion_plan.agregar_opcion("Rastrear a Ra's", "tim_dificil_rastrear_ras", stat="recursos", cambio=3)
        self.historia["tim_dificil_ejecucion_plan"] = tim_dificil_ejecucion_plan

        tim_dificil_pedir_ayuda_final = NodoHistoria(
            "tim_dificil_pedir_ayuda_final",
            "TRAGANDO ORGULLO",
            "Te tragas el orgullo y haces las llamadas. 'Superboy, Wonder Girl, Kid Flash, los necesito. "
            "Ahora.' La respuesta es inmediata y sin dudas. 'En camino,' dice Conner. En minutos, tu equipo "
            "está contigo. Juntos, coordinan una defensa que convierte tu plan imposible en ejecutable. "
            "Has aprendido la lección más importante: pedir ayuda no es debilidad, es sabiduría.",
            "tim_tragando_orgullo.png"
        )
        tim_dificil_pedir_ayuda_final.agregar_opcion("Defender juntos", "tim_dificil_defensa_equipo", stat="reputacion", cambio=20)
        self.historia["tim_dificil_pedir_ayuda_final"] = tim_dificil_pedir_ayuda_final

        tim_dificil_colapso = NodoHistoria(
            "tim_dificil_colapso",
            "EL COLAPSO INEVITABLE",
            "Te niegas a pedir ayuda hasta que es demasiado tarde. Tu cuerpo finalmente colapsa por agotamiento "
            "y heridas. Los Titans te encuentran inconsciente rodeado de ninjas derrotados. Salvaste algunos "
            "objetivos, pero otros fueron alcanzados. Cuando despiertas en el hospital, Dick está ahí: 'Tim, "
            "casi mueres. Y por qué? Por orgullo?' No tienes respuesta. Has aprendido una lección dolorosa.",
            "tim_colapso_inevitable.png"
        )
        tim_dificil_colapso.agregar_opcion("Enfrentar las consecuencias", "tim_dificil_consecuencias", stat="reputacion", cambio=-20)
        self.historia["tim_dificil_colapso"] = tim_dificil_colapso

        tim_dificil_coordinacion_completa = NodoHistoria(
            "tim_dificil_coordinacion_completa",
            "EL COORDINADOR MAESTRO",
            "Coordinas el equipo completo con precisión militar. Cada persona sabe exactamente dónde estar "
            "y cuándo. Estableces canales de comunicación, protocolos de emergencia, y rutas de evacuación. "
            "Cuando Barbara ve tu plan completo, dice: 'Tim, esto es... esto es trabajo de Batman. Nivel "
            "de Batman.' Es el mayor cumplido que podrías recibir.",
            "tim_coordinador_maestro.png"
        )
        tim_dificil_coordinacion_completa.agregar_opcion("Ejecutar la operación", "tim_dificil_operacion_perfecta", stat="reputacion", cambio=25)
        self.historia["tim_dificil_coordinacion_completa"] = tim_dificil_coordinacion_completa

        tim_dificil_veredicto_dick = NodoHistoria(
            "tim_dificil_veredicto_dick",
            "EL VEREDICTO",
            "Dick estudia tu evidencia en silencio. Damian comenta: 'Es circunstancial en el mejor de los "
            "casos.' Pero Dick levanta una mano silenciándolo. Finalmente dice: 'Tim, tu evidencia es sólida. "
            "Y más importante, confío en tu instinto. Si dices que Ra's planea esto, te creo. ¿Qué necesitas?' "
            "La validación llega como una ola de alivio. Finalmente, no estás solo.",
            "tim_veredicto_dick.png"
        )
        tim_dificil_veredicto_dick.agregar_opcion("Planear defensa conjunta", "tim_dificil_defensa_conjunta", stat="reputacion", cambio=20)
        self.historia["tim_dificil_veredicto_dick"] = tim_dificil_veredicto_dick

        tim_dificil_respuesta_multiple = NodoHistoria(
            "tim_dificil_respuesta_multiple",
            "DIVIDIDO Y DÉBIL",
            "Intentas responder a múltiples ataques, corriendo de ubicación en ubicación. Salvas a uno, "
            "pero mientras lo haces, otro es atacado. Es una batalla perdida. Finalmente, exhausto y herido, "
            "te das cuenta de que necesitas ayuda. Haces la llamada a los Titans. Llegan rápidamente y "
            "juntos logran estabilizar la situación, pero ha habido bajas. Aprendes que ser héroe también "
            "significa saber cuándo pedir refuerzos.",
            "tim_respuesta_multiple.png"
        )
        tim_dificil_respuesta_multiple.agregar_opcion("Reagrupar con los Titans", "tim_dificil_reagrupar", stat="salud", cambio=-15)
        self.historia["tim_dificil_respuesta_multiple"] = tim_dificil_respuesta_multiple

        tim_dificil_defensa_edificio = NodoHistoria(
            "tim_dificil_defensa_edificio",
            "FORTALEZA CORPORATIVA",
            "Wayne Enterprises se convierte en un campo de batalla. Los ninjas infiltran el edificio por "
            "múltiples puntos, pero tú y Lucius han preparado cada piso con defensas. Usas gadgets de Batman, "
            "tecnología experimental, y tu propio ingenio. La batalla es brutal pero la ganas. Cuando el "
            "último ninja cae, Lucius dice: 'Mr. Drake, definitivamente es digno del apellido Wayne.'",
            "tim_fortaleza_corporativa.png"
        )
        tim_dificil_defensa_edificio.agregar_opcion("Asegurar el edificio y moverse", "tim_dificil_asegurar_moverse", stat="recursos", cambio=2)
        self.historia["tim_dificil_defensa_edificio"] = tim_dificil_defensa_edificio

        tim_dificil_respaldo_titans = NodoHistoria(
            "tim_dificil_respaldo_titans",
            "CON RESPALDO",
            "Con los Titans respaldándote, confrontas a Ra's al Ghul. Él está en un almacén con sus ninjas "
            "elite restantes. 'Trajiste amigos,' observa Ra's. 'Qué... inesperado.' Sonríes: 'Es la diferencia "
            "entre tú y yo, Ra's. Tú inspiras miedo. Yo inspiro lealtad. Por eso mis amigos están aquí por "
            "elección, mientras los tuyos están aquí por obligación.'",
            "tim_con_respaldo.png"
        )
        tim_dificil_respaldo_titans.agregar_opcion("Batalla final con respaldo", "tim_dificil_batalla_respaldo", stat="salud", cambio=-10)
        self.historia["tim_dificil_respaldo_titans"] = tim_dificil_respaldo_titans

        tim_dificil_duelo_final = NodoHistoria(
            "tim_dificil_duelo_final",
            "EL DUELO DEL DETECTIVE",
            "Aceptas el duelo con Ra's. Sabes que es superior físicamente, pero tienes ventajas que él no "
            "espera. Durante la pelea, usas cada truco que Bruce te enseñó. No intentas superarlo en fuerza "
            "o velocidad. En su lugar, lo superas en estrategia, anticipando sus movimientos, usando el "
            "ambiente a tu favor. La batalla es larga y brutal, pero eventualmente, Ra's retrocede.",
            "tim_duelo_del_detective.png"
        )
        tim_dificil_duelo_final.agregar_opcion("Momento de verdad con Ra's", "tim_dificil_momento_verdad", stat="salud", cambio=-20)
        self.historia["tim_dificil_duelo_final"] = tim_dificil_duelo_final

        tim_dificil_revelacion = NodoHistoria(
            "tim_dificil_revelacion",
            "LA REVELACIÓN ESTRATÉGICA",
            "'Quieres saber cómo te derroté?' preguntas a Ra's. 'No fue con puños. Fue con esto.' Muestras "
            "documentos: transferencias legales que Lucius completó mientras Ra's estaba distraído. Wayne "
            "Enterprises ahora está legalmente protegida bajo tu nombre temporalmente. 'No puedes robar lo "
            "que no puedes tocar legalmente. Y mientras planeabas asesinatos, yo jugaba ajedrez corporativo.'",
            "tim_revelacion_estrategica.png"
        )
        tim_dificil_revelacion.agregar_opcion("La reacción de Ra's", "tim_dificil_reaccion_ras", stat="reputacion", cambio=30)
        self.historia["tim_dificil_revelacion"] = tim_dificil_revelacion

        tim_dificil_victoria_familiar = NodoHistoria(
            "tim_dificil_victoria_familiar",
            "VICTORIA EN FAMILIA",
            "Con la Bat-Familia unida, los ataques de Ra's fallan completamente. Cada objetivo está protegido. "
            "Cada asesino es capturado o repelido. Al final de la noche, la familia se reúne en la Batcueva. "
            "Dick te abraza: 'Tim, salvaste a todos. Lo siento por no haber confiado en ti antes.' Damian "
            "incluso ofrece un respeto gruñido. Alfred sirve té: 'El Maestro Bruce estaría orgulloso.'",
            "tim_victoria_familiar.png"
        )
        tim_dificil_victoria_familiar.agregar_opcion("Momento de reconciliación", "tim_dificil_reconciliacion", stat="reputacion", cambio=30)
        self.historia["tim_dificil_victoria_familiar"] = tim_dificil_victoria_familiar

        tim_dificil_defensa_perfecta = NodoHistoria(
            "tim_dificil_defensa_perfecta",
            "DEFENSA IMPECABLE",
            "Tu defensa es perfecta. Cada ataque es anticipado y neutralizado. Los ninjas se retiran en "
            "confusión cuando cada plan falla. Barbara te contacta: 'Tim, acabas de coordinar la operación "
            "defensiva más compleja que he visto. Y funcionó perfectamente.' Has demostrado que eres más "
            "que Robin. Eres un estratega maestro por derecho propio.",
            "tim_defensa_impecable.png"
        )
        tim_dificil_defensa_perfecta.agregar_opcion("Confrontar a Ra's victorioso", "tim_dificil_confrontacion_victoriosa", stat="reputacion", cambio=25)
        self.historia["tim_dificil_defensa_perfecta"] = tim_dificil_defensa_perfecta

        tim_dificil_confrontacion_final = NodoHistoria(
            "tim_dificil_confrontacion_final",
            "FRENTE AL DEMONIO DERROTADO",
            "Encuentras a Ra's en su punto de retirada. Su plan ha fallado completamente. Te mira con una "
            "mezcla de respeto y frustración: 'Timothy Drake. Subestimé no tu habilidad, sino tu capacidad "
            "de inspirar lealtad. El Detective te enseñó bien.' Haces una pausa. 'Ra's, tú y yo sabemos que "
            "Bruce está vivo. ¿Por qué atacar su legado si crees que regresará?'",
            "tim_confrontacion_final.png"
        )
        tim_dificil_confrontacion_final.agregar_opcion("Escuchar la respuesta de Ra's", "tim_dificil_respuesta_final_ras", stat="reputacion", cambio=25)
        self.historia["tim_dificil_confrontacion_final"] = tim_dificil_confrontacion_final

        tim_dificil_emboscada = NodoHistoria(
            "tim_dificil_emboscada",
            "LA EMBOSCADA PERFECTA",
            "Los ninjas entran a la Mansión Wayne esperando una mansión desprotegida. En su lugar, encuentran "
            "una trampa elaborada. Has estudiado sus tácticas, anticipado sus puntos de entrada, y preparado "
            "contramedidas específicas. Uno por uno, caen en tus trampas. Cuando el último ninja está "
            "inconsciente, te paras victorioso. 'Bruce estaría orgulloso,' piensas.",
            "tim_emboscada_perfecta.png"
        )
        tim_dificil_emboscada.agregar_opcion("Interrogar a los ninjas", "tim_dificil_interrogar_ninjas", stat="recursos", cambio=3)
        self.historia["tim_dificil_emboscada"] = tim_dificil_emboscada

        tim_dificil_trampa_mansion = NodoHistoria(
            "tim_dificil_trampa_mansion",
            "CASA TRAMPA",
            "Con Alfred a salvo, conviertes la Mansión Wayne en una trampa mortal (no letal, por supuesto). "
            "Cada habitación tiene sorpresas. Cuando los ninjas entran, es como un juego mortal de 'Operación'. "
            "Cables de disparo, redes ocultas, gas somnífero, todo no letal pero efectivo. Los capturas a "
            "todos sin una sola muerte. Batman aprobaría tus métodos.",
            "tim_casa_trampa.png"
        )
        tim_dificil_trampa_mansion.agregar_opcion("Usar ninjas como información", "tim_dificil_informacion_ninjas", stat="recursos", cambio=3)
        self.historia["tim_dificil_trampa_mansion"] = tim_dificil_trampa_mansion

        tim_dificil_comando_central = NodoHistoria(
            "tim_dificil_comando_central",
            "ORACLE Y RED ROBIN",
            "Trabajando con Barbara desde su torre, se convierten en un equipo perfecto. Ella maneja "
            "vigilancia y comunicaciones, tú coordinas respuestas tácticas. Es como un tablero de ajedrez "
            "en vivo donde ves cada pieza. Cuando los ataques comienzan, los neutralizas antes de que "
            "escalen. 'Trabajamos bien juntos,' dice Barbara. 'Siempre lo hemos hecho,' respondes.",
            "tim_comando_central.png"
        )
        tim_dificil_comando_central.agregar_opcion("Victoria coordinada", "tim_dificil_victoria_coordinada", stat="reputacion", cambio=20)
        self.historia["tim_dificil_comando_central"] = tim_dificil_comando_central

        tim_dificil_mision_titans = NodoHistoria(
            "tim_dificil_mision_titans",
            "TITANS UNIDOS",
            "Regresas a la misión con los Titans completamente respaldándote. No es solo sobre proteger "
            "objetivos ahora; es sobre enviar un mensaje a Ra's al Ghul: no estás solo. Juntos, coordinan "
            "una operación que es mitad defensa, mitad contraataque. Los ninjas de Ra's se encuentran no "
            "solo con resistencia, sino con un equipo de superhéroes de élite.",
            "tim_titans_unidos.png"
        )
        tim_dificil_mision_titans.agregar_opcion("Tomar la ofensiva", "tim_dificil_ofensiva", stat="reputacion", cambio=20)
        self.historia["tim_dificil_mision_titans"] = tim_dificil_mision_titans

        tim_dificil_liderar_titans = NodoHistoria(
            "tim_dificil_liderar_titans",
            "EL LÍDER NATO",
            "Lideras a los Titans en Gotham con confianza renovada. Conner comenta: 'Tim, siempre has sido "
            "un líder. Solo necesitabas creerlo.' Cassie añade: 'Y no tienes que ser Batman para serlo.' "
            "Tienen razón. Eres Red Robin, y eso es suficiente. Bajo tu liderazgo, los Titans operan como "
            "una máquina bien aceitada, protegiendo cada objetivo con precisión quirúrgica.",
            "tim_lider_nato.png"
        )
        tim_dificil_liderar_titans.agregar_opcion("Operación Titans perfecta", "tim_dificil_operacion_titans", stat="reputacion", cambio=25)
        self.historia["tim_dificil_liderar_titans"] = tim_dificil_liderar_titans

        tim_dificil_buscar_ras = NodoHistoria(
            "tim_dificil_buscar_ras",
            "LA CAZA DEL DEMONIO",
            "Mientras la defensa se ejecuta perfectamente, te escabulles para buscar a Ra's al Ghul. Sabes "
            "que no estará en el frente de batalla; estará observando, evaluando, planeando su próximo "
            "movimiento. Usando tus habilidades de detective, rastreas sus posibles ubicaciones. Lo encuentras "
            "en un edificio con vista a Gotham, observando el fracaso de su plan con expresión indescifrable.",
            "tim_caza_del_demonio.png"
        )
        tim_dificil_buscar_ras.agregar_opcion("Confrontación en las alturas", "tim_dificil_alturas", stat="salud", cambio=-10)
        self.historia["tim_dificil_buscar_ras"] = tim_dificil_buscar_ras

        tim_dificil_coordinacion_total = NodoHistoria(
            "tim_dificil_coordinacion_total",
            "RED DE HÉROES",
            "Coordinas una red de héroes que abarca toda Gotham. No es solo la Bat-Familia o los Titans; "
            "es toda la comunidad heroica de la ciudad. Huntress, Black Canary, Question, Batwoman, todos "
            "responden a tu llamado. Ra's planeaba atacar una ciudad; en su lugar, ataca una comunidad "
            "unida. Su ejército de asesinos se enfrenta a un ejército de héroes.",
            "tim_red_de_heroes.png"
        )
        tim_dificil_coordinacion_total.agregar_opcion("La batalla por Gotham", "tim_dificil_batalla_gotham", stat="reputacion", cambio=30)
        self.historia["tim_dificil_coordinacion_total"] = tim_dificil_coordinacion_total

        tim_dificil_rastrear_ras = NodoHistoria(
            "tim_dificil_rastrear_ras",
            "EL RASTRO DEL DEMONIO",
            "Rastreas a Ra's usando métodos que aprendiste de Batman. Cada asesino capturado proporciona "
            "una pieza del rompecabezas. Barbara ayuda con análisis de datos. Eventualmente, triangulas su "
            "ubicación: un edificio corporativo abandonado en el distrito financiero. Es apropiado: planeaba "
            "robar Wayne Enterprises, y ahora se esconde en una torre corporativa vacía.",
            "tim_rastro_del_demonio.png"
        )
        tim_dificil_rastrear_ras.agregar_opcion("Infiltrar la ubicación de Ra's", "tim_dificil_infiltracion_final", stat="recursos", cambio=3)
        self.historia["tim_dificil_rastrear_ras"] = tim_dificil_rastrear_ras

        tim_dificil_defensa_equipo = NodoHistoria(
            "tim_dificil_defensa_equipo",
            "FUERZA COMBINADA",
            "Con tu equipo reunido, la defensa es impenetrable. Cada miembro juega su rol perfectamente. "
            "Superboy usa fuerza, Wonder Girl usa habilidad, Kid Flash usa velocidad, y tú usas cerebro. "
            "Es la combinación perfecta. Los ninjas de Ra's son derrotados metódicamente. Al final de la "
            "noche, ningún objetivo ha sido alcanzado. Es victoria completa.",
            "tim_fuerza_combinada.png"
        )
        tim_dificil_defensa_equipo.agregar_opcion("Celebración y próximos pasos", "tim_dificil_celebracion", stat="reputacion", cambio=20)
        self.historia["tim_dificil_defensa_equipo"] = tim_dificil_defensa_equipo

        tim_dificil_consecuencias = NodoHistoria(
            "tim_dificil_consecuencias",
            "FINAL AMARGO: LECCIONES DOLOROSAS",
            "Enfrentas las consecuencias de tu orgullo. Algunos objetivos fueron alcanzados. Hubo heridos, "
            "quizás muertos. Dick te mira decepcionado: 'Si hubieras pedido ayuda desde el principio...' "
            "Tiene razón. Aprendiste ser detective de Batman, pero no aprendiste la lección más importante: "
            "ningún héroe puede hacerlo todo solo. Es una lección que pagarás con culpa el resto de tu vida. "
            "Red Robin continuará, pero con cicatrices emocionales que nunca sanarán completamente.",
            "tim_final_amargo.png"
        )
        # Final malo sin más opciones
        self.historia["tim_dificil_consecuencias"] = tim_dificil_consecuencias

        tim_dificil_operacion_perfecta = NodoHistoria(
            "tim_dificil_operacion_perfecta",
            "OPERACIÓN: ÉXITO TOTAL",
            "La operación se ejecuta sin un solo error. Cada equipo cumple su objetivo. Cada objetivo está "
            "protegido. Cada asesino es capturado o repelido. Cuando Barbara compila el informe final, es "
            "perfecto: cero bajas de tu lado, todos los objetivos a salvo, plan de Ra's completamente frustrado. "
            "'Tim,' dice Barbara, 'esto es... esto es obra maestra de estrategia. Nivel de Bruce Wayne.'",
            "tim_operacion_exitototal.png"
        )
        tim_dificil_operacion_perfecta.agregar_opcion("El reconocimiento final", "tim_dificil_reconocimiento", stat="reputacion", cambio=35)
        self.historia["tim_dificil_operacion_perfecta"] = tim_dificil_operacion_perfecta

        tim_dificil_defensa_conjunta = NodoHistoria(
            "tim_dificil_defensa_conjunta",
            "BAT-FAMILIA UNIDA",
            "Planeas la defensa con Dick, trabajando juntos como los hermanos que son. Dick aporta experiencia "
            "de combate y liderazgo. Tú aportas análisis estratégico y planificación detallada. Juntos, crean "
            "un plan que ninguno podría haber creado solo. Damian incluso contribuye con conocimiento de la "
            "Liga de Asesinos. Por primera vez en meses, la familia está verdaderamente unida.",
            "tim_bat_familia_unida.png"
        )
        tim_dificil_defensa_conjunta.agregar_opcion("Ejecutar plan familiar", "tim_dificil_plan_familiar", stat="reputacion", cambio=25)
        self.historia["tim_dificil_defensa_conjunta"] = tim_dificil_defensa_conjunta

        tim_dificil_reagrupar = NodoHistoria(
            "tim_dificil_reagrupar",
            "REAGRUPANDO FUERZAS",
            "Te reagrupas con los Titans después de la batalla caótica. Estás herido pero vivo. Algunos "
            "objetivos fueron alcanzados, pero la mayoría están a salvo. No es victoria perfecta, pero es "
            "victoria. Conner te dice: 'Tim, la próxima vez, llámanos primero, pelea después.' Tiene razón. "
            "Has aprendido una lección valiosa sobre pedir ayuda a tiempo.",
            "tim_reagrupando_fuerzas.png"
        )
        tim_dificil_reagrupar.agregar_opcion("Planear contraataque", "tim_dificil_contraataque", stat="recursos", cambio=2)
        self.historia["tim_dificil_reagrupar"] = tim_dificil_reagrupar

        tim_dificil_asegurar_moverse = NodoHistoria(
            "tim_dificil_asegurar_moverse",
            "OBJETIVO ASEGURADO",
            "Aseguras Wayne Enterprises con Lucius. Él te entrega un paquete: 'Documentos de transferencia "
            "temporal. Si algo me pasa, las acciones controladoras van a ti temporalmente, no a Ra's.' Es "
            "un movimiento brillante. Incluso si Ra's tiene éxito en algo, no obtendrá Wayne Enterprises. "
            "Con un objetivo asegurado, te mueves al siguiente, sabiendo que el legado financiero de Bruce "
            "está protegido.",
            "tim_objetivo_asegurado.png"
        )
        tim_dificil_asegurar_moverse.agregar_opcion("Moverse a la Mansión Wayne", "tim_dificil_moverse_mansion", stat="recursos", cambio=2)
        self.historia["tim_dificil_asegurar_moverse"] = tim_dificil_asegurar_moverse

        tim_dificil_batalla_respaldo = NodoHistoria(
            "tim_dificil_batalla_respaldo",
            "BATALLA CON HERMANOS",
            "La batalla contra Ra's y sus ninjas elite es intensa, pero con los Titans respaldándote, no "
            "estás solo. Superboy enfrenta a los ninjas más fuertes. Wonder Girl neutraliza las armas. Kid "
            "Flash desorienta al enemigo con velocidad. Y tú te enfrentas a Ra's directamente, no para "
            "superarlo físicamente, sino para mantenerlo distraído mientras tus amigos desmantelan su operación.",
            "tim_batalla_hermanos.png"
        )
        tim_dificil_batalla_respaldo.agregar_opcion("Victoria de equipo", "tim_dificil_victoria_equipo", stat="salud", cambio=-15)
        self.historia["tim_dificil_batalla_respaldo"] = tim_dificil_batalla_respaldo

        tim_dificil_momento_verdad = NodoHistoria(
            "tim_dificil_momento_verdad",
            "EL MOMENTO DE LA VERDAD",
            "Después de la batalla, Ra's te mira con respeto genuino. Estás herido y sangrando, pero de pie. "
            "Él también está herido. 'Timothy Drake,' dice Ra's, 'has ganado algo que doy raramente: mi respeto. "
            "Desde este día, te llamaré como llamo solo a dos personas en este mundo: Detective.' Es el mayor "
            "honor que Ra's al Ghul puede otorgar, y lo sabes.",
            "tim_momento_de_la_verdad.png"
        )
        tim_dificil_momento_verdad.agregar_opcion("Aceptar el título", "tim_dificil_titulo_detective", stat="reputacion", cambio=40)
        self.historia["tim_dificil_momento_verdad"] = tim_dificil_momento_verdad

        tim_dificil_reaccion_ras = NodoHistoria(
            "tim_dificil_reaccion_ras",
            "EL RESPETO DEL DEMONIO",
            "Ra's al Ghul se ríe, genuinamente impresionado. 'Jugaste ajedrez mientras yo jugaba damas. "
            "Protegiste vidas mientras asegurabas activos. Coordinaste defensas mientras ejecutabas maniobras "
            "legales.' Se acerca y extiende su mano. 'Detective,' dice simplemente. Es el título que solo "
            "da a aquellos que considera iguales intelectuales. Solo dos personas lo han tenido: Bruce Wayne "
            "y ahora tú.",
            "tim_respeto_del_demonio.png"
        )
        tim_dificil_reaccion_ras.agregar_opcion("El título de Detective", "tim_dificil_titulo_ganado", stat="reputacion", cambio=40)
        self.historia["tim_dificil_reaccion_ras"] = tim_dificil_reaccion_ras

        tim_dificil_reconciliacion = NodoHistoria(
            "tim_dificil_reconciliacion",
            "FAMILIA RESTAURADA",
            "En la Batcueva, la familia se reúne. Dick te abraza: 'Tim, nunca debí dudar de ti. Eres tanto "
            "detective como cualquiera de nosotros.' Barbara sonríe: 'Mejor que algunos.' Incluso Damian "
            "murmura: 'Drake... hiciste bien.' Alfred es el último en hablar: 'Master Timothy, el Maestro "
            "Bruce estaría inmensamente orgulloso. No solo salvaste a la familia, sino que demostraste que "
            "has superado ser Robin. Eres Red Robin ahora. Tu propio héroe.'",
            "tim_familia_restaurada.png"
        )
        tim_dificil_reconciliacion.agregar_opcion("Mirar hacia el futuro", "tim_dificil_futuro", stat="reputacion", cambio=35)
        self.historia["tim_dificil_reconciliacion"] = tim_dificil_reconciliacion

        tim_dificil_confrontacion_victoriosa = NodoHistoria(
            "tim_dificil_confrontacion_victoriosa",
            "VICTORIOSO Y VALIDADO",
            "Confrontas a Ra's después de tu victoria perfecta. Él te espera, curiosamente sin enojo. 'Timothy "
            "Drake, lograste algo extraordinario. Derrotaste a la Liga de Asesinos sin matar a uno solo. "
            "Protegiste ocho objetivos simultáneamente. Y lo hiciste no con fuerza superior, sino con estrategia "
            "y coordinación.' Se inclina ligeramente. 'Detective. Ahora entiendo por qué el Batman te eligió.'",
            "tim_confrontacion_victoriosa.png"
        )
        tim_dificil_confrontacion_victoriosa.agregar_opcion("El reconocimiento final", "tim_dificil_reconocimiento_ras", stat="reputacion", cambio=35)
        self.historia["tim_dificil_confrontacion_victoriosa"] = tim_dificil_confrontacion_victoriosa

        tim_dificil_respuesta_final_ras = NodoHistoria(
            "tim_dificil_respuesta_final_ras",
            "LA FILOSOFÍA DEL DEMONIO",
            "Ra's suspira: 'Porque si el Detective regresa y encuentra su legado destruido, sentirá el mismo "
            "dolor que he sentido por siglos. Pero tú... tú lo protegiste.' Se levanta para irse. 'Ganaste "
            "esta ronda, Detective. Sí, Detective. Ese es tu título ahora. Has ganado lo que pocos logran: "
            "mi respeto permanente.' Se va, dejándote con la victoria y el título.",
            "tim_filosofia_del_demonio.png"
        )
        tim_dificil_respuesta_final_ras.agregar_opcion("Regresar victorioso", "tim_dificil_regreso_victorioso", stat="reputacion", cambio=35)
        self.historia["tim_dificil_respuesta_final_ras"] = tim_dificil_respuesta_final_ras

        tim_dificil_interrogar_ninjas = NodoHistoria(
            "tim_dificil_interrogar_ninjas",
            "INTERROGATORIO EFECTIVO",
            "Interrogas a los ninjas capturados usando técnicas de Batman. Obtienes información valiosa: "
            "ubicaciones de otros equipos, cronogramas de ataque, y lo más importante, la ubicación de Ra's "
            "al Ghul. Armado con esta información, puedes pasar de defensiva a ofensiva. No solo protegerás "
            "objetivos; neutralizarás la amenaza en su origen.",
            "tim_interrogatorio_efectivo.png"
        )
        tim_dificil_interrogar_ninjas.agregar_opcion("Ir tras Ra's directamente", "tim_dificil_cazar_ras", stat="recursos", cambio=3)
        self.historia["tim_dificil_interrogar_ninjas"] = tim_dificil_interrogar_ninjas

        tim_dificil_informacion_ninjas = NodoHistoria(
            "tim_dificil_informacion_ninjas",
            "INTELIGENCIA VALIOSA",
            "Los ninjas capturados proporcionan inteligencia vital. Descubres que Ra's tiene un centro de "
            "comando en Gotham desde donde coordina todo. Si puedes neutralizar ese centro, desmantelarás "
            "toda la operación. Contactas a los Titans: 'Tengo la ubicación. Vamos a terminar esto esta noche.'",
            "tim_inteligencia_valiosa.png"
        )
        tim_dificil_informacion_ninjas.agregar_opcion("Ataque al centro de comando", "tim_dificil_ataque_comando", stat="recursos", cambio=3)
        self.historia["tim_dificil_informacion_ninjas"] = tim_dificil_informacion_ninjas

        tim_dificil_victoria_coordinada = NodoHistoria(
            "tim_dificil_victoria_coordinada",
            "COORDINACIÓN PERFECTA",
            "La coordinación entre tú y Barbara es perfecta. Es como si compartieran una mente. Ella ve todo, "
            "tú respondes a todo. Los asesinos no tienen oportunidad contra este nivel de coordinación. Al "
            "final, Barbara dice: 'Tim, esto fue... trabajo de nivel Batman. No, mejor. Batman trabaja solo. "
            "Tú trabajaste con equipo. Eso es más difícil y más efectivo.'",
            "tim_coordinacion_perfecta.png"
        )
        tim_dificil_victoria_coordinada.agregar_opcion("Buscar a Ra's juntos", "tim_dificil_busqueda_conjunta", stat="reputacion", cambio=25)
        self.historia["tim_dificil_victoria_coordinada"] = tim_dificil_victoria_coordinada

        tim_dificil_ofensiva = NodoHistoria(
            "tim_dificil_ofensiva",
            "CONTRAATAQUE TITÁN",
            "No te limitas a defender; tomas la ofensiva. Con los Titans, atacas las bases de operaciones de "
            "los asesinos en Gotham. Es audaz y efectivo. Los asesinos se encuentran luchando defensivamente "
            "en su propio territorio. Superboy destruye arsenales de armas. Wonder Girl captura líderes de "
            "escuadrones. Kid Flash intercepta comunicaciones. Y tú coordinas todo como un general en batalla.",
            "tim_contraataque_titan.png"
        )
        tim_dificil_ofensiva.agregar_opcion("Presionar hasta Ra's", "tim_dificil_presionar_ras", stat="salud", cambio=-10)
        self.historia["tim_dificil_ofensiva"] = tim_dificil_ofensiva

        tim_dificil_operacion_titans = NodoHistoria(
            "tim_dificil_operacion_titans",
            "OPERACIÓN TITÁN: ÉXITO",
            "Bajo tu liderazgo, los Titans ejecutan una operación perfecta. Cada miembro brilla en su rol. "
            "Conner usa su fuerza con precisión. Cassie lidera subequipos con confianza. Bart proporciona "
            "reconocimiento a velocidad. Y tú tejes todo junto en una sinfonía de heroísmo. Al final, todos "
            "los objetivos están seguros. Ra's al Ghul ha sido completamente derrotado.",
            "tim_operacion_titan_exito.png"
        )
        tim_dificil_operacion_titans.agregar_opcion("Confrontación final con Ra's", "tim_dificil_ultima_confrontacion", stat="reputacion", cambio=30)
        self.historia["tim_dificil_operacion_titans"] = tim_dificil_operacion_titans

        tim_dificil_alturas = NodoHistoria(
            "tim_dificil_alturas",
            "EN LAS ALTURAS DE GOTHAM",
            "Encuentras a Ra's en la azotea del edificio más alto de Gotham. El viento sopla fuertemente. "
            "Gotham se extiende debajo de ustedes, una ciudad que ambos han tratado de proteger (o controlar) "
            "de diferentes maneras. 'Detective Timothy Drake,' dice Ra's. 'Viniste solo. Valiente o tonto.' "
            "'Inteligente,' respondes. 'Sabía que querías hablar, no pelear. Si quisieras pelear, no estarías "
            "aquí solo.'",
            "tim_en_las_alturas.png"
        )
        tim_dificil_alturas.agregar_opcion("La conversación final", "tim_dificil_conversacion_final", stat="reputacion", cambio=30)
        self.historia["tim_dificil_alturas"] = tim_dificil_alturas

        tim_dificil_batalla_gotham = NodoHistoria(
            "tim_dificil_batalla_gotham",
            "LA BATALLA POR GOTHAM",
            "Es una batalla como Gotham nunca ha visto. No es Batman contra un villano. Es una comunidad "
            "entera de héroes defendiendo su ciudad contra un ejército de asesinos. Las calles se convierten "
            "en zonas de batalla. Pero tus héroes no pelean con brutalidad; pelean con precisión. Cada asesino "
            "es neutralizado, capturado, no asesinado. Al final, la Liga de Asesinos se retira. Gotham permanece.",
            "tim_batalla_por_gotham.png"
        )
        tim_dificil_batalla_gotham.agregar_opcion("Victoria de la comunidad", "tim_dificil_victoria_comunidad", stat="reputacion", cambio=40)
        self.historia["tim_dificil_batalla_gotham"] = tim_dificil_batalla_gotham

        tim_dificil_infiltracion_final = NodoHistoria(
            "tim_dificil_infiltracion_final",
            "INFILTRACIÓN FINAL",
            "Te infiltras en el edificio donde Ra's se esconde. Usas todas tus habilidades de sigilo. Los "
            "ninjas guardianes no te detectan. Llegas a la oficina principal donde Ra's está sentado, esperando. "
            "'Sabía que vendrías,' dice sin voltear. 'El Detective siempre termina lo que comienza.' Se voltea "
            "y sonríe. 'Hablemos, tú y yo. Detective a Detective.'",
            "tim_infiltracion_final.png"
        )
        tim_dificil_infiltracion_final.agregar_opcion("La conversación de Detectives", "tim_dificil_conversacion_detectives", stat="reputacion", cambio=30)
        self.historia["tim_dificil_infiltracion_final"] = tim_dificil_infiltracion_final

        tim_dificil_celebracion = NodoHistoria(
            "tim_dificil_celebracion",
            "CELEBRACIÓN MERECIDA",
            "Los Titans celebran la victoria. Conner te levanta en sus hombros. Cassie sonríe con orgullo. "
            "Bart corre círculos alrededor de todos. Es un momento de alegría pura. Has salvado a todos, "
            "derrotado a Ra's al Ghul, y probado tu valía como héroe independiente. Ya no eres Robin. Eres "
            "Red Robin, y ese título tiene tanto peso como Batman.",
            "tim_celebracion_merecida.png"
        )
        tim_dificil_celebracion.agregar_opcion("Próximos pasos", "tim_dificil_proximos_pasos", stat="reputacion", cambio=25)
        self.historia["tim_dificil_celebracion"] = tim_dificil_celebracion

        tim_dificil_reconocimiento = NodoHistoria(
            "tim_dificil_reconocimiento",
            "RECONOCIMIENTO UNIVERSAL",
            "La comunidad heroica completa reconoce tu éxito. La Liga de la Justicia envía felicitaciones. "
            "Los Titans te eligen oficialmente como líder. La Bat-Familia te acoge de vuelta con respeto "
            "completo. Incluso el Comisionado Gordon dice: 'Red Robin es bienvenido en Gotham tanto como "
            "Batman.' Has logrado algo extraordinario: crear tu propia identidad heroica fuera de la sombra "
            "de Batman.",
            "tim_reconocimiento_universal.png"
        )
        tim_dificil_reconocimiento.agregar_opcion("FINAL HEROICO: El Detective", "tim_dificil_final_heroico", stat="reputacion", cambio=50)
        self.historia["tim_dificil_reconocimiento"] = tim_dificil_reconocimiento

        tim_dificil_plan_familiar = NodoHistoria(
            "tim_dificil_plan_familiar",
            "FAMILIA EN ACCIÓN",
            "El plan familiar se ejecuta con precisión militar. Dick y Damian toman el sector este. Tú y "
            "Barbara coordinan desde el centro. Alfred (después de mucha insistencia) acepta refugio seguro. "
            "La familia trabaja como una unidad perfecta, cada uno complementando las fortalezas de los otros. "
            "Es hermoso ver. Esto es lo que Bruce construyó: no solo un símbolo, sino una familia.",
            "tim_familia_en_accion.png"
        )
        tim_dificil_plan_familiar.agregar_opcion("Victoria familiar completa", "tim_dificil_victoria_total", stat="reputacion", cambio=30)
        self.historia["tim_dificil_plan_familiar"] = tim_dificil_plan_familiar

        tim_dificil_contraataque = NodoHistoria(
            "tim_dificil_contraataque",
            "PLANEANDO EL CONTRAATAQUE",
            "Después de reagrupar, planeas un contraataque. Ya no se trata solo de defender; es momento de "
            "neutralizar la amenaza permanentemente. Con la ayuda de los Titans y la información de los ninjas "
            "capturados, identificas todas las células de la Liga en Gotham. En una noche coordinada, las "
            "desmantelan todas simultáneamente. Ra's al Ghul pierde su ejército en Gotham.",
            "tim_planeando_contraataque.png"
        )
        tim_dificil_contraataque.agregar_opcion("Confrontar a Ra's derrotado", "tim_dificil_ras_derrotado", stat="reputacion", cambio=25)
        self.historia["tim_dificil_contraataque"] = tim_dificil_contraataque

        tim_dificil_moverse_mansion = NodoHistoria(
            "tim_dificil_moverse_mansion",
            "PROTEGIENDO EL HOGAR",
            "Te mueves a la Mansión Wayne, el corazón emocional de la Bat-Familia. Alfred te recibe: 'Sabía "
            "que vendría, Master Timothy.' Juntos, fortifican la mansión. Cuando los asesinos llegan, encuentran "
            "no una casa sino una fortaleza. La batalla es intensa pero victorosa. Al final, tú y Alfred "
            "están de pie entre ninjas inconscientes. 'Bien hecho, señor,' dice Alfred, sirviéndote té.",
            "tim_protegiendo_el_hogar.png"
        )
        tim_dificil_moverse_mansion.agregar_opcion("Todos los objetivos asegurados", "tim_dificil_objetivos_asegurados", stat="reputacion", cambio=25)
        self.historia["tim_dificil_moverse_mansion"] = tim_dificil_moverse_mansion

        tim_dificil_victoria_equipo = NodoHistoria(
            "tim_dificil_victoria_equipo",
            "VICTORIA DE EQUIPO",
            "Con los Titans, derrotan a Ra's y sus fuerzas. Es una victoria de equipo en el sentido más puro. "
            "Cada uno contribuyó igualmente. Cuando Ra's se retira, te mira: 'Detective Drake, la próxima "
            "vez que nos encontremos, será bajo circunstancias diferentes. Has ganado mi respeto permanente.' "
            "Se va, derrotado pero no destruido. Los Titans te rodean celebrando. Has probado que el trabajo "
            "en equipo supera al genio solitario.",
            "tim_victoria_de_equipo.png"
        )
        tim_dificil_victoria_equipo.agregar_opcion("Regreso triunfal", "tim_dificil_regreso_triunfal", stat="reputacion", cambio=30)
        self.historia["tim_dificil_victoria_equipo"] = tim_dificil_victoria_equipo

        tim_dificil_titulo_detective = NodoHistoria(
            "tim_dificil_titulo_detective",
            "EL TÍTULO GANADO",
            "Aceptas el título de Detective de Ra's al Ghul. No es solo un título; es reconocimiento de que "
            "has alcanzado el mismo nivel intelectual que Bruce Wayne. Solo tres personas en el mundo han "
            "recibido este título de Ra's: Bruce, tú, y nadie más. Cuando regresas a la Bat-Familia y les "
            "cuentas, Dick te abraza: 'Tim, siempre supimos que eras brillante. Pero esto... Ra's al Ghul "
            "no da ese título a la ligera.'",
            "tim_titulo_ganado.png"
        )
        tim_dificil_titulo_detective.agregar_opcion("FINAL ÉPICO: Detective Red Robin", "tim_dificil_final_epico", stat="reputacion", cambio=50, item="Título de Detective")
        self.historia["tim_dificil_titulo_detective"] = tim_dificil_titulo_detective

        tim_dificil_titulo_ganado = NodoHistoria(
            "tim_dificil_titulo_ganado",
            "DETECTIVE RECONOCIDO",
            "El título de Detective de Ra's al Ghul es algo que pocos logran. Es reconocimiento de brillantez "
            "intelectual al nivel de Bruce Wayne. Cuando la Bat-Familia se entera, hay silencio. Luego Dick "
            "habla: 'Tim, Ra's ha vivido siglos y solo ha dado ese título a dos personas: Bruce y tú. Eso "
            "dice todo.' Alfred añade: 'El Maestro Bruce siempre supo que era especial, Master Timothy. "
            "Ahora el mundo lo sabe.'",
            "tim_detective_reconocido.png"
        )
        tim_dificil_titulo_ganado.agregar_opcion("FINAL LEGENDARIO: El Tercer Detective", "tim_dificil_final_legendario", stat="reputacion", cambio=50, item="Título de Detective")
        self.historia["tim_dificil_titulo_ganado"] = tim_dificil_titulo_ganado

        tim_dificil_futuro = NodoHistoria(
            "tim_dificil_futuro",
            "MIRANDO ADELANTE",
            "Con la familia restaurada y Ra's derrotado, miras hacia el futuro. Aún crees que Bruce está vivo "
            "en algún lugar del tiempo. Pero ahora tienes el apoyo de la familia para buscarlo. Dick dice: "
            "'Tim, si crees que Bruce está vivo, investigaremos juntos. Pero esta vez, como familia.' Es "
            "todo lo que necesitabas escuchar. Tu búsqueda continúa, pero ya no estás solo.",
            "tim_mirando_adelante.png"
        )
        tim_dificil_futuro.agregar_opcion("FINAL ESPERANZADOR: La Búsqueda Continúa", "tim_dificil_final_esperanzador", stat="reputacion", cambio=40)
        self.historia["tim_dificil_futuro"] = tim_dificil_futuro

        tim_dificil_reconocimiento_ras = NodoHistoria(
            "tim_dificil_reconocimiento_ras",
            "EL RECONOCIMIENTO DEL INMORTAL",
            "Ra's al Ghul se acerca y, sorprendentemente, se inclina ante ti. 'Detective Timothy Drake. He "
            "vivido siglos. He enfrentado a los más grandes estrategas de la historia. Y tú te encuentras "
            "entre ellos. Tu victoria hoy no fue de fuerza, sino de mente. Coordinaste lo imposible. Por "
            "eso, te doy el título que solo he dado a uno más: Detective.' Es validación suprema.",
            "tim_reconocimiento_del_inmortal.png"
        )
        tim_dificil_reconocimiento_ras.agregar_opcion("FINAL GLORIOSO: El Segundo Detective", "tim_dificil_final_glorioso", stat="reputacion", cambio=50, item="Título de Detective")
        self.historia["tim_dificil_reconocimiento_ras"] = tim_dificil_reconocimiento_ras

        tim_dificil_regreso_victorioso = NodoHistoria(
            "tim_dificil_regreso_victorioso",
            "HÉROE VICTORIOSO",
            "Regresas a Gotham victorioso. Has derrotado a Ra's al Ghul, salvado a la Bat-Familia, y ganado "
            "el título de Detective. La ciudad te recibe como héroe. Los Titans te celebran. La Bat-Familia "
            "te abraza. Y en algún lugar, sabes que Bruce Wayne, donde quiera que esté en el tiempo, estaría "
            "orgulloso. Has superado ser Robin. Eres Red Robin, Detective, y héroe por derecho propio.",
            "tim_heroe_victorioso.png"
        )
        tim_dificil_regreso_victorioso.agregar_opcion("FINAL TRIUNFAL: Red Robin Ascendente", "tim_dificil_final_triunfal", stat="reputacion", cambio=45)
        self.historia["tim_dificil_regreso_victorioso"] = tim_dificil_regreso_victorioso

        tim_dificil_cazar_ras = NodoHistoria(
            "tim_dificil_cazar_ras",
            "LA CAZA FINAL",
            "Con la información de los ninjas, cazas a Ra's directamente. Es audaz, quizás temerario. Pero "
            "estás cansado de ser reactivo. Es momento de terminar esto. Encuentras a Ra's en su escondite "
            "temporal. Está solo, esperándote. 'Detective Drake,' dice con sonrisa. 'Viniste a mí. Valiente. "
            "Muy bien. Hablemos, héroe a villano, Detective a Detective.'",
            "tim_caza_final.png"
        )
        tim_dificil_cazar_ras.agregar_opcion("El diálogo final", "tim_dificil_dialogo_final", stat="reputacion", cambio=30)
        self.historia["tim_dificil_cazar_ras"] = tim_dificil_cazar_ras

        tim_dificil_ataque_comando = NodoHistoria(
            "tim_dificil_ataque_comando",
            "ASALTO AL COMANDO",
            "Lideras un asalto coordinado al centro de comando de Ra's. Los Titans, Bat-Familia, y otros "
            "héroes de Gotham atacan simultáneamente. Es la operación ofensiva más grande que has coordinado. "
            "El centro cae rápidamente bajo la presión combinada. Ra's escapa, pero su operación en Gotham "
            "está completamente desmantelada. Has ganado no solo esta batalla, sino la guerra completa.",
            "tim_asalto_al_comando.png"
        )
        tim_dificil_ataque_comando.agregar_opcion("Victoria definitiva", "tim_dificil_victoria_definitiva", stat="reputacion", cambio=35)
        self.historia["tim_dificil_ataque_comando"] = tim_dificil_ataque_comando

        tim_dificil_busqueda_conjunta = NodoHistoria(
            "tim_dificil_busqueda_conjunta",
            "DETECTIVE Y ORACLE",
            "Tú y Barbara buscan a Ra's juntos. Tu detective en campo, ella detective digital. Juntos, son "
            "imparables. Rastreas a Ra's hasta su última ubicación. Barbara hackea sus comunicaciones. Cuando "
            "lo confrontan, Ra's sonríe: 'Detective Drake y Oracle. Un equipo formidable. Casi tan formidable "
            "como Batman y Oracle. Quizás más, porque ustedes reconocen que necesitan mutuamente.'",
            "tim_detective_y_oracle.png"
        )
        tim_dificil_busqueda_conjunta.agregar_opcion("Confrontación dual", "tim_dificil_confrontacion_dual", stat="reputacion", cambio=30)
        self.historia["tim_dificil_busqueda_conjunta"] = tim_dificil_busqueda_conjunta

        tim_dificil_presionar_ras = NodoHistoria(
            "tim_dificil_presionar_ras",
            "PRESIÓN IMPLACABLE",
            "Presionas implacablemente hasta llegar a Ra's al Ghul. Cada base destruida, cada ninja capturado, "
            "cada operación desmantelada. Finalmente, acorralas a Ra's en su último refugio. Está solo, sin "
            "ejército, sin recursos. Te mira con mezcla de respeto y frustración: 'Detective Drake, me has "
            "derrotado completamente. Algo que pocos han logrado. Acepto mi derrota... por ahora.'",
            "tim_presion_implacable.png"
        )
        tim_dificil_presionar_ras.agregar_opcion("Victoria absoluta", "tim_dificil_victoria_absoluta", stat="reputacion", cambio=40)
        self.historia["tim_dificil_presionar_ras"] = tim_dificil_presionar_ras

        tim_dificil_ultima_confrontacion = NodoHistoria(
            "tim_dificil_ultima_confrontacion",
            "LA ÚLTIMA CONFRONTACIÓN",
            "Confrontas a Ra's al Ghul por última vez. Su plan ha fallado completamente. Su ejército está "
            "derrotado. Su estrategia, desmantelada. Te mira con respeto absoluto: 'Timothy Drake, Red Robin, "
            "Detective. Has superado a un inmortal con siglos de experiencia. ¿Cómo?' Sonríes: 'Simple. Tú "
            "peleaste para destruir. Yo pelee para proteger. Y la protección siempre supera a la destrucción "
            "cuando tienes el equipo correcto.'",
            "tim_ultima_confrontacion.png"
        )
        tim_dificil_ultima_confrontacion.agregar_opcion("FINAL MAGISTRAL: El Protector", "tim_dificil_final_magistral", stat="reputacion", cambio=50)
        self.historia["tim_dificil_ultima_confrontacion"] = tim_dificil_ultima_confrontacion

        tim_dificil_conversacion_final = NodoHistoria(
            "tim_dificil_conversacion_final",
            "CONVERSACIÓN EN LAS ALTURAS",
            "Hablas con Ra's en las alturas de Gotham. Él explica: 'Atacé el legado de Wayne porque si él "
            "regresa y encuentra todo destruido, conocerá mi dolor. Pero tú lo protegiste. Dime, Detective "
            "Drake, ¿realmente crees que Bruce Wayne vive?' 'Sí,' respondes sin dudar. Ra's asiente: 'Yo "
            "también. Y cuando regrese, dile que enfrentó a un sucesor digno en ti.'",
            "tim_conversacion_en_alturas.png"
        )
        tim_dificil_conversacion_final.agregar_opcion("FINAL REFLEXIVO: Dignos Sucesores", "tim_dificil_final_reflexivo", stat="reputacion", cambio=40)
        self.historia["tim_dificil_conversacion_final"] = tim_dificil_conversacion_final



#############################################################################################################################################################################


    def inicializar_historias_damian_wayne(self):
        """Crear todos los nodos de historia para Damian Wayne"""
        # MODO FÁCIL: DE LA LIGA DE ASESINOS A ROBIN (12-15 nodos)
        damian_inicio = NodoHistoria(
            "damian_facil_inicio",
            "LA LLEGADA DEL HEREDERO",
            "Has sido criado en la Liga de Asesinos, entrenado desde tu nacimiento para ser el arma perfecta. Eres Damian Wayne, hijo de Bruce Wayne y Talia al Ghul. Ahora, tu madre te ha llevado a Gotham para que conozcas a tu padre. 'El Detective necesita un heredero,' te dijo. Llegas a la Mansión Wayne, no como un niño, sino como un guerrero listo para reclamar su derecho de nacimiento.",
            "damian_llegada.png"
        )
        damian_inicio.agregar_opcion("Presentarte con arrogancia a Bruce", "damian_facil_conflicto_bruce", stat="reputacion", cambio=-10)
        damian_inicio.agregar_opcion("Observar en silencio, analizando a tu 'familia'", "damian_facil_observacion", stat="recursos", cambio=1)
        self.historia["damian_facil_inicio"] = damian_inicio

        damian_observacion = NodoHistoria(
            "damian_facil_observacion",
            "EL ANALISTA SILENCIOSO",
            "Observas a Bruce, a Alfred, y a Tim Drake (el actual Robin). Ves sus debilidades, sus lazos emocionales. Bruce te mira con una mezcla de sorpresa y preocupación. 'Así que... eres mi hijo,' dice finalmente. 'Demuéstralo,' respondes fríamente.",
            "damian_observa.png"
        )
        damian_observacion.agregar_opcion("Desafiar a Tim Drake por el manto de Robin", "damian_facil_conflicto_tim", stat="reputacion", cambio=-15)
        self.historia["damian_facil_observacion"] = damian_observacion

        damian_conflicto_bruce = NodoHistoria(
            "damian_facil_conflicto_bruce",
            "CONFLICTO CON EL PADRE",
            "'Soy Damian Wayne, tu heredero,' declaras. 'He venido a tomar mi lugar.' Bruce frunce el ceño. 'No es algo que se toma, Damian. Se gana.' Tu arrogancia choca inmediatamente con su estoicismo. La tensión es palpable desde el primer momento.",
            "damian_conflicto_bruce.png"
        )
        damian_conflicto_bruce.agregar_opcion("Insistir en que eres superior a los otros 'Robins'", "damian_facil_conflicto_tim", stat="reputacion", cambio=-10)
        self.historia["damian_facil_conflicto_bruce"] = damian_conflicto_bruce

        damian_conflicto_tim = NodoHistoria(
            "damian_facil_conflicto_tim",
            "RIVALIDAD INMEDIATA",
            "Desafías a Tim Drake en la Batcueva. 'Ese traje me pertenece, Drake. No eres digno.' La pelea es rápida y brutal. Usas técnicas letales que sorprenden a Tim. Dick Grayson (Nightwing) interviene para separarlos. '¡Basta, Damian! Aquí no hacemos las cosas así.'",
            "damian_vs_tim.png"
        )
        damian_conflicto_tim.agregar_opcion("Argumentar que tus métodos son más efectivos", "damian_facil_metodos_letales", stat="reputacion", cambio=-15)
        damian_conflicto_tim.agregar_opcion("Aceptar la intervención de Dick a regañadientes", "damian_facil_entrenamiento_forzado", stat="reputacion", cambio=5)
        self.historia["damian_facil_conflicto_tim"] = damian_conflicto_tim

        damian_metodos_letales = NodoHistoria(
            "damian_facil_metodos_letales",
            "LA LÍNEA QUE NO SE CRUZA",
            "Una noche, sales de patrulla sin permiso. Encuentras a un criminal, 'Spook', a punto de matar a alguien. Lo desarmas con una espada. 'La justicia de mi abuelo es permanente,' dices, listo para ejecutarlo. Batman aparece y te detiene. '¡En mi ciudad no matamos!'",
            "damian_letal.png"
        )
        damian_metodos_letales.agregar_opcion("Obedecer y entregar al criminal", "damian_facil_entrenamiento_forzado", stat="reputacion", cambio=10)
        damian_metodos_letales.agregar_opcion("Discutir con Batman sobre la necesidad de matar", "damian_facil_entrenamiento_forzado", stat="reputacion", cambio=-5)
        self.historia["damian_facil_metodos_letales"] = damian_metodos_letales

        damian_entrenamiento_forzado = NodoHistoria(
            "damian_facil_entrenamiento_forzado",
            "ENTRENAMIENTO IMPUESTO",
            "Bruce te confina en la Mansión Wayne. 'Si vas a vivir bajo mi techo, seguirás mis reglas. Y la primera regla es: no matar.' Comienza un entrenamiento intensivo para 'desaprender' los métodos de la Liga. Dick y Alfred te supervisan. Es frustrante, pero poco a poco, empiezas a entender.",
            "damian_entrenamiento.png"
        )
        damian_entrenamiento_forzado.agregar_opcion("Esforzarte en el entrenamiento para demostrar tu valía", "damian_facil_mision_supervisada", stat="salud", cambio=10)
        damian_entrenamiento_forzado.agregar_opcion("Resistirte al entrenamiento, creyendo que sabes más", "damian_facil_mision_supervisada", stat="reputacion", cambio=-10)
        self.historia["damian_facil_entrenamiento_forzado"] = damian_entrenamiento_forzado

        damian_mision_supervisada = NodoHistoria(
            "damian_facil_mision_supervisada",
            "PRIMERA MISIÓN COMO... ¿ROBIN?",
            "Batman decide ponerte a prueba. Te da un traje de Robin modificado. 'Irás conmigo esta noche. Seguirás mis órdenes al pie de la letra.' La misión es detener un robo de armas. Es tu oportunidad de demostrar que puedes controlarte.",
            "damian_primera_mision.png"
        )
        damian_mision_supervisada.agregar_opcion("Seguir el plan de Batman sin cuestionar", "damian_facil_respeto_ganado", stat="reputacion", cambio=15)
        damian_mision_supervisada.agregar_opcion("Usar una táctica 'más eficiente' pero arriesgada", "damian_facil_dilema_etico", stat="salud", cambio=-10)
        self.historia["damian_facil_mision_supervisada"] = damian_mision_supervisada

        damian_dilema_etico = NodoHistoria(
            "damian_facil_dilema_etico",
            "DILEMA ÉTICO",
            "Ignoras una orden directa y usas una granada de humo para incapacitar a todos los criminales a la vez, incluyendo a uno que estaba a punto de rendirse. Es efectivo, pero Batman te reprende: 'La justicia no es solo eficiencia, Damian. Es también compasión.'",
            "damian_dilema.png"
        )
        damian_dilema_etico.agregar_opcion("Aprender la lección sobre la compasión", "damian_facil_respeto_ganado", stat="reputacion", cambio=10)
        self.historia["damian_facil_dilema_etico"] = damian_dilema_etico

        damian_respeto_ganado = NodoHistoria(
            "damian_facil_respeto_ganado",
            "PRIMEROS SIGNOS DE RESPETO",
            "A pesar de tu arrogancia, tu habilidad es innegable. Siguiendo las reglas (a tu manera), logras detener el robo. Dick te observa desde la distancia y le dice a Bruce: 'Tiene potencial. Es un Wayne, después de todo.' Sientes un pequeño atisbo de orgullo.",
            "damian_respeto.png"
        )
        damian_respeto_ganado.agregar_opcion("Continuar patrullando con Batman", "damian_facil_choque_tim", stat="reputacion", cambio=10)
        self.historia["damian_facil_respeto_ganado"] = damian_respeto_ganado

        damian_choque_tim = NodoHistoria(
            "damian_facil_choque_tim",
            "EL CHOQUE DE LOS ROBINS",
            "Durante una investigación en la Batcueva, tienes un desacuerdo con Tim sobre una pista. 'Tu análisis es lento y sentimental, Drake,' dices. 'Mi instinto es más rápido.' Terminan resolviendo el caso juntos, combinando tu instinto con su análisis. A regañadientes, admites que su método tiene mérito.",
            "damian_tim_rivalidad.png"
        )
        damian_choque_tim.agregar_opcion("Reconocer (a tu manera) la habilidad de Tim", "damian_facil_aceptacion_familia", stat="reputacion", cambio=10)
        damian_choque_tim.agregar_opcion("Insistir en que tu método fue superior", "damian_facil_aceptacion_familia", stat="reputacion", cambio=-5)
        self.historia["damian_facil_choque_tim"] = damian_choque_tim

        damian_aceptacion_familia = NodoHistoria(
            "damian_facil_aceptacion_familia",
            "ACEPTACIÓN PAULATINA",
            "Poco a poco, la Batfamilia comienza a aceptarte. Alfred te enseña a cuidar de los animales de la mansión (a los que muestras un afecto sorprendente). Dick te enseña acrobacias sin la rigidez de la Liga. Incluso Tim comparte contigo notas de casos. No es la Liga de Asesinos. Es... diferente. Es una familia.",
            "damian_familia.png"
        )
        damian_aceptacion_familia.agregar_opcion("Aprender a trabajar en equipo", "damian_facil_trabajo_equipo", stat="reputacion", cambio=15, item="Lazo Familiar")
        self.historia["damian_facil_aceptacion_familia"] = damian_aceptacion_familia

        damian_trabajo_equipo = NodoHistoria(
            "damian_facil_trabajo_equipo",
            "LA IMPORTANCIA DEL EQUIPO",
            "En una misión contra el Espantapájaros, quedas atrapado y expuesto a su gas del miedo. Ves a tu madre y a Ra's al Ghul decepcionados de ti. Pero entonces, Batman (Dick Grayson, ya que Bruce está ausente) te saca de allí. 'No estás solo, Damian,' te dice. 'Somos un equipo.' La lección finalmente cala hondo.",
            "damian_equipo.png"
        )
        damian_trabajo_equipo.agregar_opcion("Aceptar tu lugar como Robin", "damian_facil_final", stat="reputacion", cambio=20)
        self.historia["damian_facil_trabajo_equipo"] = damian_trabajo_equipo

        damian_final = NodoHistoria(
            "damian_facil_final",
            "EL HIJO DEL MURCIÉLAGO - FINAL",
            "Has recorrido un largo camino desde la Liga de Asesinos. Ya no eres solo el heredero de sangre; eres Robin, el hijo de Batman. Bruce te mira un día en la Batcueva, no con la severidad de un mentor, sino con el orgullo de un padre. 'Estoy orgulloso de ti, Damian. Has honrado el manto de Robin.' Te paras al lado de tu padre, listo para proteger Gotham. Has encontrado tu verdadero hogar y tu verdadero propósito. Tu historia como el Robin definitivo apenas comienza.",
            "damian_final_robin.png"
        )
        damian_final.es_final = True
        self.historia["damian_facil_final"] = damian_final

        # MODO NORMAL: ROBIN Y JÓVENES TITANES (25-28 nodos)
        damian_normal_inicio = NodoHistoria(
            "damian_normal_inicio",
            "UN NUEVO BATMAN, UN NUEVO ROBIN",
            "Bruce Wayne ha muerto. El mundo lo llora. Gotham está en caos. Dick Grayson, tu 'hermano' mayor, ha asumido el manto de Batman. Te observa con preocupación. 'Gotham necesita un Robin,' dice. 'Y tú eres el único que puede serlo. Pero será bajo mis reglas.' Es una oferta y una advertencia.",
            "damian_dick_batman.png"
        )
        damian_normal_inicio.agregar_opcion("Aceptar el manto como tu derecho de nacimiento", "damian_normal_conflicto_dick", stat="reputacion", cambio=-5)
        damian_normal_inicio.agregar_opcion("Aceptar, pero con desdén hacia el 'falso' Batman", "damian_normal_conflicto_dick", stat="reputacion", cambio=-10)
        self.historia["damian_normal_inicio"] = damian_normal_inicio

        damian_normal_conflicto_dick = NodoHistoria(
            "damian_normal_conflicto_dick",
            "PATRULLA CON EL 'HERMANO MAYOR'",
            "Tu primera patrulla con Dick como Batman es tensa. Él es más acrobático, más hablador. Menos... Batman. Cuando acorralas a un criminal, le rompes el brazo sin dudarlo. Dick te detiene. '¡Damian, no! ¡No hacemos esto!' Su tono es diferente al de tu padre. Más frustrado, menos autoritario.",
            "damian_dick_patrol.png"
        )
        damian_normal_conflicto_dick.agregar_opcion("Argumentar que tus métodos son más eficientes", "damian_normal_tension_familia", stat="reputacion", cambio=-15)
        damian_normal_conflicto_dick.agregar_opcion("Obedecer a regañadientes, murmurando sobre su debilidad", "damian_normal_tension_familia", stat="reputacion", cambio=5)
        self.historia["damian_normal_conflicto_dick"] = damian_normal_conflicto_dick

        damian_normal_tension_familia = NodoHistoria(
            "damian_normal_tension_familia",
            "TENSIÓN EN LA BATCUEVA",
            "De vuelta en la Batcueva, la tensión con Dick es palpable. Alfred intenta mediar. Tim Drake (ahora Red Robin) te mira con desaprobación. 'No puedes ser Robin si actúas como un asesino,' dice Tim. 'Tú ya no eres Robin, Drake. Cállate,' respondes. Dick interviene: 'Suficiente. Damian, necesitas aprender a trabajar en equipo. Te unirás a los Jóvenes Titanes.'",
            "damian_batfamily_tension.png"
        )
        damian_normal_tension_familia.agregar_opcion("Rechazarlo rotundamente. 'No necesito niñeras.'", "damian_normal_titanes_forzado", stat="reputacion", cambio=-20)
        damian_normal_tension_familia.agregar_opcion("Aceptar con arrogancia. 'Les enseñaré cómo se hace.'", "damian_normal_titanes_intro", stat="reputacion", cambio=5)
        self.historia["damian_normal_tension_familia"] = damian_normal_tension_familia

        damian_normal_titanes_forzado = NodoHistoria(
            "damian_normal_titanes_forzado",
            "DECISIÓN DE BATMAN",
            "'No fue una sugerencia,' dice Dick, su voz firme como la de Batman. 'Es una orden. Necesitas aprender a confiar en otros y a que otros confíen en ti. Irás a la Torre de los Titanes.' Te sientes humillado y furioso, pero la orden de Batman es la orden de Batman, incluso si es Grayson.",
            "damian_forced.png"
        )
        damian_normal_titanes_forzado.agregar_opcion("Ir a la Torre de los Titanes de mala gana", "damian_normal_titanes_intro", stat="reputacion", cambio=-10)
        self.historia["damian_normal_titanes_forzado"] = damian_normal_titanes_forzado

        damian_normal_titanes_intro = NodoHistoria(
            "damian_normal_titanes_intro",
            "BIENVENIDO A LOS JÓVENES TITANES",
            "Llegas a la Torre de los Titanes. El equipo actual, liderado por Wonder Girl (Cassie Sandsmark), te recibe con una mezcla de curiosidad y cautela. Superboy (Kon-El) te mira con desconfianza. Kid Flash (Bart Allen) intenta romper el hielo con un chiste. 'Así que este es el famoso hijo de Batman,' dice Cassie. 'Demuéstranos lo que tienes.'",
            "damian_titans_intro.png"
        )
        damian_normal_titanes_intro.agregar_opcion("Mostrar tus habilidades en la sala de entrenamiento", "damian_normal_primera_mision_titanes", stat="reputacion", cambio=10)
        damian_normal_titanes_intro.agregar_opcion("Criticar sus protocolos de seguridad", "damian_normal_tension_liderazgo", stat="reputacion", cambio=-10)
        self.historia["damian_normal_titanes_intro"] = damian_normal_titanes_intro

        damian_normal_tension_liderazgo = NodoHistoria(
            "damian_normal_tension_liderazgo",
            "CHOQUE DE LIDERAZGO",
            "'Sus defensas son patéticas,' declaras. 'Cualquier asesino de la Liga podría infiltrarse aquí.' Cassie frunce el ceño. 'Somos un equipo, Damian. No un ejército. Quizás podrías enseñarnos en lugar de criticar.' Tu actitud ya está causando fricción. Superboy te empuja ligeramente: 'Relájate, chico murciélago.'",
            "damian_titans_tension.png"
        )
        damian_normal_tension_liderazgo.agregar_opcion("Retroceder y ofrecerte a mejorar la seguridad", "damian_normal_primera_mision_titanes", stat="reputacion", cambio=5)
        damian_normal_tension_liderazgo.agregar_opcion("Desafiar el liderazgo de Wonder Girl", "damian_normal_primera_mision_titanes", stat="reputacion", cambio=-15)
        self.historia["damian_normal_tension_liderazgo"] = damian_normal_tension_liderazgo

        damian_normal_primera_mision_titanes = NodoHistoria(
            "damian_normal_primera_mision_titanes",
            "MISIÓN: EL CULTO DE LA COBRA",
            "La primera misión es contra el Culto de la Cobra. Planean liberar un arma biológica. Wonder Girl lidera, pero tú ves fallas en su plan. 'Tu estrategia es demasiado directa,' le dices. 'Deberíamos usar sigilo.' Ella duda, pero te da una oportunidad para demostrar tu punto.",
            "damian_titans_mission.png"
        )
        damian_normal_primera_mision_titanes.agregar_opcion("Ejecutar un plan de sigilo impecable", "damian_normal_exito_sigilo", stat="reputacion", cambio=15, item="Respeto de los Titanes")
        damian_normal_primera_mision_titanes.agregar_opcion("Tu plan de sigilo falla y necesitan improvisar", "damian_normal_fallo_sigilo", stat="salud", cambio=-10)
        self.historia["damian_normal_primera_mision_titanes"] = damian_normal_primera_mision_titanes

        damian_normal_exito_sigilo = NodoHistoria(
            "damian_normal_exito_sigilo",
            "EL ESTRATEGA SILENCIOSO",
            "Tu plan funciona a la perfección. Te infiltras en la base del culto, neutralizas a los guardias y desactivas el arma biológica antes de que el resto del equipo entre. Cassie está impresionada. 'Ok, Wayne. Tienes talento.' Has ganado un poco de respeto, pero también has demostrado que prefieres trabajar solo.",
            "damian_stealth_win.png"
        )
        damian_normal_exito_sigilo.agregar_opcion("Aceptar el cumplido a tu manera ('Era obvio')", "damian_normal_sombra_liga", stat="reputacion", cambio=5)
        self.historia["damian_normal_exito_sigilo"] = damian_normal_exito_sigilo

        damian_normal_fallo_sigilo = NodoHistoria(
            "damian_normal_fallo_sigilo",
            "IMPROVISACIÓN FORZADA",
            "Tu plan de sigilo falla cuando te encuentras con un asesino que no estaba en los planos: un agente de la Liga de Asesinos. La alarma suena. La misión se convierte en un caos. Los Titanes tienen que luchar para salir. Superboy te salva de un disparo. '¡Creí que tenías todo bajo control!' grita.",
            "damian_stealth_fail.png"
        )
        damian_normal_fallo_sigilo.agregar_opcion("Admitir tu error y trabajar en equipo para escapar", "damian_normal_sombra_liga", stat="reputacion", cambio=10)
        damian_normal_fallo_sigilo.agregar_opcion("Culpar al agente de la Liga por la falla", "damian_normal_sombra_liga", stat="reputacion", cambio=-10)
        self.historia["damian_normal_fallo_sigilo"] = damian_normal_fallo_sigilo

        damian_normal_sombra_liga = NodoHistoria(
            "damian_normal_sombra_liga",
            "LA SOMBRA DE LA LIGA",
            "La presencia de un agente de la Liga de Asesinos te perturba. ¿Por qué estaba allí? ¿Te están vigilando? De vuelta en la Torre, investigas y descubres que el agente era un renegado. Pero la experiencia te deja paranoico. Luchas con tu legado: ¿eres un héroe o un asesino reformado?",
            "damian_league_shadow.png"
        )
        damian_normal_sombra_liga.agregar_opcion("Compartir tus preocupaciones con Dick", "damian_normal_charla_dick", stat="reputacion", cambio=10)
        damian_normal_sombra_liga.agregar_opcion("Guardar tus miedos para ti mismo", "damian_normal_visita_talia", stat="salud", cambio=-10)
        self.historia["damian_normal_sombra_liga"] = damian_normal_sombra_liga

        damian_normal_charla_dick = NodoHistoria(
            "damian_normal_charla_dick",
            "CONSEJO FRATERNAL",
            "Hablas con Dick sobre tus miedos. Él te escucha pacientemente. 'Damian, no eres tu abuelo. No eres tu madre. Eres un Wayne. Y eso significa que eliges quién eres. Cada día.' Sus palabras, aunque simples, te dan algo de paz. Quizás este 'falso' Batman no es tan inútil después de todo.",
            "damian_dick_talk.png"
        )
        damian_normal_charla_dick.agregar_opcion("Agradecerle y volver con los Titanes", "damian_normal_camaraderia", stat="salud", cambio=10)
        self.historia["damian_normal_charla_dick"] = damian_normal_charla_dick

        damian_normal_visita_talia = NodoHistoria(
            "damian_normal_visita_talia",
            "LA VISITA DE LA MADRE",
            "Una noche, tu madre, Talia al Ghul, aparece en la Torre de los Titanes. 'Hijo mío,' dice. 'Veo que juegas a ser un héroe con estos niños. Es decepcionante. El legado de los Al Ghul te espera. Vuelve a casa.' Te ofrece poder, un ejército, un imperio. Todo lo que tienes que hacer es abandonar a los Titanes y a la memoria de tu padre.",
            "damian_talia_visit.png"
        )
        damian_normal_visita_talia.agregar_opcion("Rechazar su oferta firmemente", "damian_normal_rechazo_talia", stat="reputacion", cambio=20, item="Independencia")
        damian_normal_visita_talia.agregar_opcion("Considerar su oferta, tentado por el poder", "damian_normal_traicion_liga", stat="reputacion", cambio=-25)
        self.historia["damian_normal_visita_talia"] = damian_normal_visita_talia

        damian_normal_rechazo_talia = NodoHistoria(
            "damian_normal_rechazo_talia",
            "RECHAZO AL LEGADO OSCURO",
            "'Mi padre me dio un nuevo legado,' respondes. 'Y lo honraré. No soy un Al Ghul. Soy un Wayne. Soy Robin.' Talia te mira con frialdad. 'Has elegido tu bando, Damian. No esperes misericordia de la Liga.' Desaparece, dejándote con una amenaza velada y una nueva determinación.",
            "damian_talia_reject.png"
        )
        damian_normal_rechazo_talia.agregar_opcion("Informar a los Titanes sobre la amenaza", "damian_normal_camaraderia", stat="reputacion", cambio=15)
        self.historia["damian_normal_rechazo_talia"] = damian_normal_rechazo_talia

        damian_normal_traicion_liga = NodoHistoria(
            "damian_normal_traicion_liga",
            "LA TRAICIÓN",
            "La oferta de Talia te tienta. Con la Liga, podrías imponer verdadera justicia. Aceptas en secreto. Talia te da una misión: sabotear a los Titanes desde adentro. Durante una misión, desactivas sus comunicaciones, dejándolos vulnerables. Pero cuando ves a Superboy protegiendo a Wonder Girl, dudas. ¿Es esto realmente lo que quieres?",
            "damian_betrayal.png"
        )
        damian_normal_traicion_liga.agregar_opcion("Abortar la traición y ayudar a los Titanes", "damian_normal_eleccion_dificil", stat="reputacion", cambio=10)
        damian_normal_traicion_liga.agregar_opcion("Completar la misión para la Liga", "damian_normal_final_oscuro", stat="reputacion", cambio=-50)
        self.historia["damian_normal_traicion_liga"] = damian_normal_traicion_liga

        damian_normal_eleccion_dificil = NodoHistoria(
            "damian_normal_eleccion_dificil",
            "LA ELECCIÓN DIFÍCIL",
            "En el último segundo, reactivas las comunicaciones y ayudas a los Titanes a repeler el ataque. Les confiesas la visita de Talia y tu momento de debilidad. Están furiosos, especialmente Superboy. '¿Cómo podemos confiar en ti ahora?' pregunta. Has roto la confianza del equipo.",
            "damian_hard_choice.png"
        )
        damian_normal_eleccion_dificil.agregar_opcion("Aceptar su desconfianza y trabajar para recuperarla", "damian_normal_crisis_personal", stat="reputacion", cambio=-20)
        self.historia["damian_normal_eleccion_dificil"] = damian_normal_eleccion_dificil

        damian_normal_camaraderia = NodoHistoria(
            "damian_normal_camaraderia",
            "MOMENTOS DE CAMARADERÍA",
            "A pesar de las tensiones, comienzas a encontrar tu lugar. Bart te enseña a jugar videojuegos (eres terrible). Cassie te habla de mitología griega (te parece fascinante). Incluso tienes una conversación casi civilizada con Tim Drake durante una visita a la Batcueva. 'Grayson te está haciendo bien,' admite Tim. 'No te equivoques, Drake. Yo le estoy haciendo bien a él,' respondes, pero hay una pizca de broma en tu voz.",
            "damian_camaraderie.png"
        )
        damian_normal_camaraderia.agregar_opcion("Continuar construyendo lazos con el equipo", "damian_normal_crisis_personal", stat="salud", cambio=15)
        self.historia["damian_normal_camaraderia"] = damian_normal_camaraderia

        damian_normal_crisis_personal = NodoHistoria(
            "damian_normal_crisis_personal",
            "CRISIS DE IDENTIDAD",
            "La amenaza de tu madre y la desconfianza (o creciente confianza) de tus amigos te sumen en una crisis. ¿Quién eres? ¿El heredero del Demonio o el hijo del Murciélago? ¿Líder o asesino? Una noche, en la azotea de la Torre, miras a Gotham y te sientes perdido. Dick te encuentra allí. 'Ser Robin no es fácil,' dice. 'Pero no tienes que hacerlo solo.'",
            "damian_identity_crisis.png"
        )
        damian_normal_crisis_personal.agregar_opcion("Aceptar su apoyo y redefinir tu misión", "damian_normal_batalla_clave", stat="reputacion", cambio=20)
        damian_normal_crisis_personal.agregar_opcion("Alejarte, insistiendo en que puedes manejarlo solo", "damian_normal_batalla_clave", stat="reputacion", cambio=-10)
        self.historia["damian_normal_crisis_personal"] = damian_normal_crisis_personal

        damian_normal_batalla_clave = NodoHistoria(
            "damian_normal_batalla_clave",
            "BATALLA CLAVE: DEATHSTROKE",
            "La Liga de Asesinos, bajo órdenes de Talia, contrata a Deathstroke para eliminar a los Titanes y 'recuperarte'. Es la prueba definitiva. Deathstroke es un estratega maestro y un combatiente letal. Los Titanes luchan, pero él los supera tácticamente. Solo tú, con tu entrenamiento de la Liga, puedes anticipar sus movimientos.",
            "damian_vs_deathstroke.png"
        )
        damian_normal_batalla_clave.agregar_opcion("Liderar a los Titanes usando tu conocimiento de la Liga", "damian_normal_final_normal", stat="reputacion", cambio=30, item="Liderazgo Probado")
        damian_normal_batalla_clave.agregar_opcion("Enfrentar a Deathstroke solo para proteger a los demás", "damian_normal_final_sacrificio", stat="salud", cambio=-40, stat2="reputacion", cambio2=25)
        self.historia["damian_normal_batalla_clave"] = damian_normal_batalla_clave

        damian_normal_final_normal = NodoHistoria(
            "damian_normal_final_normal",
            "HÉROE CONFIABLE - FINAL",
            "Tomas el liderazgo. '¡Escúchenme si quieren vivir!' gritas. Usando tu conocimiento de las tácticas de la Liga, coordinas un contraataque brillante. Superboy es la fuerza bruta, Wonder Girl la defensa, Kid Flash la distracción, y tú eres el cerebro. Juntos, derrotan a Deathstroke. Los Titanes te miran con nuevo respeto. Dick llega y ve la escena. 'Estoy orgulloso, Robin.' Has demostrado que eres un líder, un héroe. Imperfecto, sí, pero confiable. Has encontrado tu propio camino, no como el heredero de Al Ghul ni como la sombra de Wayne, sino como Damian, el Robin que lidera a los Titanes.",
            "damian_leader.png"
        )
        damian_normal_final_normal.es_final = True
        self.historia["damian_normal_final_normal"] = damian_normal_final_normal

        damian_normal_final_sacrificio = NodoHistoria(
            "damian_normal_final_sacrificio",
            "EL SACRIFICIO DE ROBIN - FINAL",
            "Para proteger a los Titanes, te enfrentas a Deathstroke en un duelo uno a uno. Es una batalla brutal. Logras herirlo y obligarlo a retirarse, pero quedas gravemente herido. Los Titanes te rodean, horrorizados y agradecidos. 'Salvaste nuestras vidas, Damian,' dice Cassie. Has demostrado con acciones, no con palabras, que tu lealtad está con ellos. Te has convertido en un verdadero héroe, dispuesto a sacrificarte por tus amigos. Tu recuperación será larga, pero te has ganado un lugar permanente en el corazón de los Titanes y en el legado de Robin.",
            "damian_sacrifice.png"
        )
        damian_normal_final_sacrificio.es_final = True
        self.historia["damian_normal_final_sacrificio"] = damian_normal_final_sacrificio

        damian_normal_final_oscuro = NodoHistoria(
            "damian_normal_final_oscuro",
            "EL HEREDERO DEL DEMONIO - FINAL",
            "Completas la traición. Los Titanes son derrotados y capturados por la Liga de Asesinos. Talia te sonríe. 'Bien hecho, hijo mío. Has aceptado tu verdadero destino.' Te paras junto a ella, mirando a tus antiguos 'amigos' encadenados. Sientes un vacío, pero lo entierras bajo el orgullo de tu linaje. Has elegido el poder sobre la amistad, el legado de Al Ghul sobre el de Wayne. El mundo tiene un nuevo y temible enemigo. Tu camino como Robin ha terminado. Tu camino como el heredero del Demonio acaba de comenzar.",
            "damian_heir_of_demon.png"
        )
        damian_normal_final_oscuro.es_final = True
        self.historia["damian_normal_final_oscuro"] = damian_normal_final_oscuro

        # MODO DIFÍCIL: CRISIS Y RUPTURA (30-33 nodos)
        damian_dificil_inicio = NodoHistoria(
            "damian_dificil_inicio",
            "LA MUERTE DE UN PILAR",
            "Gotham está de luto. Alfred Pennyworth, el corazón de la Batfamilia, ha sido asesinado por Bane. Estabas allí. Lo viste suceder. Viste a tu padre, Bruce, fallar en protegerlo. El dolor se mezcla con una furia helada. En la Batcueva, el silencio es un grito. Bruce está destrozado, pero tú... tú estás roto de una manera diferente. La justicia de Batman ya no es suficiente.",
            "alfred_death.png"
        )
        damian_dificil_inicio.agregar_opcion("Culpar a Bruce por su debilidad", "damian_dificil_confrontacion_bruce", stat="reputacion", cambio=-20)
        damian_dificil_inicio.agregar_opcion("Canalizar tu dolor en una venganza silenciosa", "damian_dificil_metodos_cuestionables", stat="salud", cambio=-15)
        self.historia["damian_dificil_inicio"] = damian_dificil_inicio

        damian_dificil_confrontacion_bruce = NodoHistoria(
            "damian_dificil_confrontacion_bruce",
            "ACUSACIÓN",
            "'¡Tú lo dejaste morir!' le gritas a Bruce. '¡Tu código moral mató a Alfred! Si me hubieras dejado matarlo, Alfred estaría vivo.' Bruce, con el rostro marcado por el dolor, te mira. 'No hables de lo que no entiendes, Damian. La violencia solo engendra más violencia.' '¡Y tu inacción engendra tumbas!' respondes. La brecha entre ustedes es ahora un abismo.",
            "damian_bruce_argue.png"
        )
        damian_dificil_confrontacion_bruce.agregar_opcion("Abandonar la Batcueva, declarando que sus métodos son un fracaso", "damian_dificil_ruptura", stat="reputacion", cambio=-25)
        damian_dificil_confrontacion_bruce.agregar_opcion("Seguir tus propios métodos en secreto", "damian_dificil_metodos_cuestionables", stat="reputacion", cambio=-10)
        self.historia["damian_dificil_confrontacion_bruce"] = damian_dificil_confrontacion_bruce

        damian_dificil_metodos_cuestionables = NodoHistoria(
            "damian_dificil_metodos_cuestionables",
            "LA JUSTICIA DE DAMIAN",
            "Comienzas a operar por tu cuenta. Capturas a los secuaces de Bane, uno por uno. Los llevas a una guarida secreta y usas las técnicas de interrogatorio de la Liga de Asesinos. No los matas, pero los dejas al borde de la muerte para obtener información. Es brutal, es eficiente, y es todo lo que Batman odia.",
            "damian_torture.png"
        )
        damian_dificil_metodos_cuestionables.agregar_opcion("Continuar con tus métodos, obteniendo resultados", "damian_dificil_descubrimiento_bruce", stat="recursos", cambio=5)
        damian_dificil_metodos_cuestionables.agregar_opcion("Dudar de tus acciones al ver el terror en sus ojos", "damian_dificil_duda_moral", stat="salud", cambio=5)
        self.historia["damian_dificil_metodos_cuestionables"] = damian_dificil_metodos_cuestionables

        damian_dificil_descubrimiento_bruce = NodoHistoria(
            "damian_dificil_descubrimiento_bruce",
            "DESCUBIERTO",
            "Batman te encuentra. La escena en tu guarida es macabra. Criminales atados, heridos, aterrorizados. '¿Qué has hecho, Damian?' pregunta, su voz un susurro helado. 'Lo que tú no tienes el valor de hacer,' respondes. 'Obtener justicia real.' La confrontación es inevitable y violenta.",
            "damian_bruce_confrontation.png"
        )
        damian_dificil_descubrimiento_bruce.agregar_opcion("Luchar contra Batman para defender tus métodos", "damian_dificil_ruptura", stat="salud", cambio=-20, stat2="reputacion", cambio2=-30)
        damian_dificil_descubrimiento_bruce.agregar_opcion("Argumentar que tus métodos son necesarios", "damian_dificil_confrontacion_bruce", stat="reputacion", cambio=-15)
        self.historia["damian_dificil_descubrimiento_bruce"] = damian_dificil_descubrimiento_bruce

        damian_dificil_ruptura = NodoHistoria(
            "damian_dificil_ruptura",
            "RUPTURA Y ABANDONO",
            "La pelea con tu padre es física y emocional. Él es más fuerte, pero tú eres más despiadado. Al final, te desarma. 'Se acabó, Damian. El traje de Robin... ya no es tuyo.' Te arranca la 'R' del pecho. 'Entonces no quiero nada de ti,' dices. Abandonas la Batcueva, la Mansión Wayne y el nombre de Robin. Estás solo.",
            "damian_leaves.png"
        )
        damian_dificil_ruptura.agregar_opcion("Iniciar un viaje en solitario para forjar tu propio camino", "damian_dificil_viaje_solitario", stat="recursos", cambio=-5, item="Identidad Rota")
        self.historia["damian_dificil_ruptura"] = damian_dificil_ruptura

        damian_dificil_viaje_solitario = NodoHistoria(
            "damian_dificil_viaje_solitario",
            "EL VIAJE DEL EXILIADO",
            "Viajas por el mundo, sin rumbo fijo. Usas tus habilidades para sobrevivir, a veces como mercenario, a veces como justiciero anónimo. Cada ciudad es un recordatorio de lo que perdiste. En tus sueños, ves a Alfred, decepcionado. La soledad es una carga pesada. Un día, en un mercado de Marrakech, te encuentras con tu madre, Talia.",
            "damian_solo_travel.png"
        )
        damian_dificil_viaje_solitario.agregar_opcion("Confrontarla con ira", "damian_dificil_conflicto_talia", stat="reputacion", cambio=-10)
        damian_dificil_viaje_solitario.agregar_opcion("Escuchar lo que tiene que decir", "damian_dificil_dialogo_talia", stat="reputacion", cambio=5)
        self.historia["damian_dificil_viaje_solitario"] = damian_dificil_viaje_solitario

        damian_dificil_conflicto_talia = NodoHistoria(
            "damian_dificil_conflicto_talia",
            "CONFLICTO MATERNO",
            "'Me abandonaste con un idealista débil,' le dices. 'Su código mató a Alfred.' Talia te mira con una mezcla de orgullo y pena. 'El Detective siempre fue débil, hijo mío. Pero tú... tú tienes mi fuerza. La Liga de Asesinos te espera. Es tu derecho de nacimiento.'",
            "damian_talia_argue.png"
        )
        damian_dificil_conflicto_talia.agregar_opcion("Rechazar su oferta y el legado de Al Ghul", "damian_dificil_rechazo_liga", stat="reputacion", cambio=15)
        damian_dificil_conflicto_talia.agregar_opcion("Aceptar su oferta, buscando poder y venganza", "damian_dificil_aceptacion_liga", stat="reputacion", cambio=-20)
        self.historia["damian_dificil_conflicto_talia"] = damian_dificil_conflicto_talia
        # Alias para evitar error de nodo no encontrado
        self.historia["damian_dificil_dialogo_talia"] = damian_dificil_conflicto_talia

        damian_dificil_rechazo_liga = NodoHistoria(
            "damian_dificil_rechazo_liga",
            "RECHAZO FINAL",
            "'No soy un Al Ghul. Y ya no soy un Wayne,' declaras. 'Soy algo nuevo.' Dejas a tu madre, rechazando tanto el murciélago como el demonio. Tu viaje ahora es verdaderamente solitario. Buscas respuestas sobre tu propio destino, investigando antiguas profecías de la Liga que hablaban de un 'hijo de dos mundos'.",
            "damian_rejects_all.png"
        )
        damian_dificil_rechazo_liga.agregar_opcion("Investigar las profecías en un monasterio tibetano", "damian_dificil_investigacion_destino", stat="recursos", cambio=3)
        self.historia["damian_dificil_rechazo_liga"] = damian_dificil_rechazo_liga

        damian_dificil_aceptacion_liga = NodoHistoria(
            "damian_dificil_aceptacion_liga",
            "EL HEREDERO DEL DEMONIO",
            "Aceptas la oferta de Talia. Te reincorporas a la Liga de Asesinos, no como un niño, sino como un comandante. Lideras misiones con una eficiencia letal que incluso impresiona a tu madre. Pero cada vida que tomas, cada acto de crueldad, te aleja más del recuerdo de Alfred y de la parte de ti que era Robin.",
            "damian_league_commander.png"
        )
        damian_dificil_aceptacion_liga.agregar_opcion("Liderar un asalto a una base de Bane", "damian_dificil_venganza_liga", stat="recursos", cambio=10)
        damian_dificil_aceptacion_liga.agregar_opcion("Dudar de tu decisión al ver la brutalidad de la Liga", "damian_dificil_crisis_existencial", stat="salud", cambio=-10)
        self.historia["damian_dificil_aceptacion_liga"] = damian_dificil_aceptacion_liga

        damian_dificil_investigacion_destino = NodoHistoria(
            "damian_dificil_investigacion_destino",
            "EL MONASTERIO SILENCIOSO",
            "En un monasterio en lo alto del Himalaya, encuentras textos antiguos. Hablan de un niño nacido de la unión del Murciélago y el Demonio, destinado a traer equilibrio o destrucción total. No da respuestas, solo más preguntas. ¿Eres un salvador o un destructor? La crisis existencial te golpea con toda su fuerza.",
            "damian_monastery.png"
        )
        damian_dificil_investigacion_destino.agregar_opcion("Meditar para encontrar tu propio camino", "damian_dificil_meditacion", stat="salud", cambio=15)
        damian_dificil_investigacion_destino.agregar_opcion("Buscar a un antiguo enemigo de tu padre para un debate moral", "damian_dificil_alianza_oscura", stat="reputacion", cambio=-5)
        self.historia["damian_dificil_investigacion_destino"] = damian_dificil_investigacion_destino

        damian_dificil_crisis_existencial = NodoHistoria(
            "damian_dificil_crisis_existencial",
            "CRISIS EXISTENCIAL",
            "La brutalidad de la Liga te repugna. No es la justicia eficiente que imaginabas, es sadismo. Te das cuenta de que has cambiado un código que no te gustaba por uno que odias. En secreto, planeas tu escape. Pero, ¿a dónde ir? Ya no tienes hogar. Eres un fantasma entre dos mundos.",
            "damian_crisis.png"
        )
        damian_dificil_crisis_existencial.agregar_opcion("Escapar y buscar redención", "damian_dificil_viaje_solitario", stat="reputacion", cambio=10)
        damian_dificil_crisis_existencial.agregar_opcion("Confrontar a Talia sobre la moralidad de la Liga", "damian_dificil_conflicto_talia", stat="reputacion", cambio=-5)
        self.historia["damian_dificil_crisis_existencial"] = damian_dificil_crisis_existencial

        damian_dificil_alianza_oscura = NodoHistoria(
            "damian_dificil_alianza_oscura",
            "ALIANZA INESPERADA",
            "Buscas a Jason Todd, Red Hood. Él entiende la ira, la muerte y el regreso. Lo encuentras en Gotham. 'Así que el pequeño demonio finalmente se rompió,' dice Jason. '¿Qué quieres?' Le explicas tu dilema. Él se ríe. 'Bienvenido al club, chico. La línea entre justicia y venganza es más delgada de lo que el viejo te hizo creer.'",
            "damian_jason_teamup.png"
        )
        damian_dificil_alianza_oscura.agregar_opcion("Aceptar su 'tutoría' como antihéroe", "damian_dificil_tutoria_jason", stat="reputacion", cambio=-15, item="Tácticas de Red Hood")
        damian_dificil_alianza_oscura.agregar_opcion("Rechazar sus métodos letales", "damian_dificil_debate_moral", stat="reputacion", cambio=10)
        self.historia["damian_dificil_alianza_oscura"] = damian_dificil_alianza_oscura

        damian_dificil_batalla_final = NodoHistoria(
            "damian_dificil_batalla_final",
            "LA BATALLA POR EL ALMA DE DAMIAN",
            "Tu camino te lleva a una encrucijada final. Talia y la Liga de Asesinos han lanzado un ataque a gran escala contra Gotham, viéndote como un traidor. Al mismo tiempo, Batman (Bruce) intenta detenerte, creyendo que eres una amenaza. Estás atrapado en medio, luchando contra ambos bandos. Debes decidir quién eres de una vez por todas.",
            "damian_final_battle.png"
        )
        damian_dificil_batalla_final.agregar_opcion("Luchar junto a Batman para proteger Gotham (Redención)", "damian_dificil_final_redencion", stat="reputacion", cambio=40)
        damian_dificil_batalla_final.agregar_opcion("Derrotar a ambos y forjar tu propio camino (Antihéroe)", "damian_dificil_final_antiheroe", stat="salud", cambio=-25, stat2="reputacion", cambio2=-20)
        damian_dificil_batalla_final.agregar_opcion("Reclamar el liderazgo de la Liga y remodelarla (Independiente)", "damian_dificil_final_independiente", stat="recursos", cambio=15, stat2="reputacion", cambio2=5)
        self.historia["damian_dificil_batalla_final"] = damian_dificil_batalla_final

        # FINALES MODO DIFÍCIL
        damian_dificil_final_redencion = NodoHistoria(
            "damian_dificil_final_redencion",
            "EL REGRESO DEL HIJO - FINAL",
            "Eliges proteger Gotham. Luchas codo a codo con tu padre, una sinfonía de combate que ninguno de los dos esperaba. Juntos, repelen a la Liga. Después de la batalla, en una azotea bajo la lluvia, Bruce te mira. 'Alfred estaría orgulloso,' dice. No necesitas más. Vuelves a la Batfamilia, no como el niño arrogante, sino como un hombre que ha visto la oscuridad y ha elegido la luz. Aceptas un nuevo manto, no el de Robin, sino uno propio. Has vuelto a casa.",
            "damian_final_redemption.png"
        )
        damian_dificil_final_redencion.es_final = True
        self.historia["damian_dificil_final_redencion"] = damian_dificil_final_redencion

        damian_dificil_final_antiheroe = NodoHistoria(
            "damian_dificil_final_antiheroe",
            "EL VIGILANTE GRIS - FINAL",
            "Usas tu genio táctico para que la Liga y la Batfamilia se neutralicen entre sí. En el caos resultante, te estableces como el nuevo poder en el inframundo de Gotham. No eres un héroe, no eres un villano. Eres un mal necesario. Controlas el crimen con mano de hierro, usando métodos letales cuando es necesario. Dick y Tim intentan detenerte, pero siempre estás un paso por delante. Te has convertido en un antihéroe oscuro, el rey de una Gotham más 'segura', pero mucho más temerosa. Estás solo, pero en control.",
            "damian_final_antihero.png"
        )
        damian_dificil_final_antiheroe.es_final = True
        self.historia["damian_dificil_final_antiheroe"] = damian_dificil_final_antiheroe

        damian_dificil_final_independiente = NodoHistoria(
            "damian_dificil_final_independiente",
            "EL NUEVO DEMONIO - FINAL",
            "En la batalla final, desafías a Talia por el liderazgo de la Liga de Asesinos. La derrotas en un combate singular. 'La Liga necesita un nuevo propósito,' declaras. 'No más destrucción sin sentido.' Comienzas a remodelar la Liga, convirtiéndola en una fuerza para un tipo de justicia global y despiadada. No eres tu abuelo ni tu madre. Eres algo nuevo. Un líder independiente que camina por la delgada línea entre la tiranía y la salvación. El mundo ahora tiene que lidiar con un nuevo y poderoso jugador en el tablero.",
            "damian_final_independent.png"
        )
        damian_dificil_final_independiente.es_final = True
        self.historia["damian_dificil_final_independiente"] = damian_dificil_final_independiente

        # Nodos intermedios para conectar las ramas
        self.historia["damian_dificil_duda_moral"] = NodoHistoria("damian_dificil_duda_moral", "DUDA MORAL", "El terror en los ojos de tus víctimas te recuerda a los débiles que juraste proteger. ¿Te estás convirtiendo en lo que cazas? La duda te corroe.", "damian_moral_doubt.png")
        self.historia["damian_dificil_duda_moral"].agregar_opcion("Buscar consejo en alguien inesperado", "damian_dificil_alianza_oscura", stat="salud", cambio=10)
        self.historia["damian_dificil_duda_moral"].agregar_opcion("Ignorar la duda y seguir adelante", "damian_dificil_descubrimiento_bruce", stat="salud", cambio=-10)

        self.historia["damian_dificil_venganza_liga"] = NodoHistoria("damian_dificil_venganza_liga", "VENGANZA FRÍA", "Lideras un asalto de la Liga contra la última fortaleza de Bane. Es una masacre. Obtienes tu venganza por Alfred, pero el sabor es amargo. La violencia no te ha traído paz, solo más sangre en tus manos.", "damian_revenge.png")
        self.historia["damian_dificil_venganza_liga"].agregar_opcion("Cuestionar el camino de la Liga", "damian_dificil_crisis_existencial", stat="salud", cambio=-15)

        self.historia["damian_dificil_meditacion"] = NodoHistoria("damian_dificil_meditacion", "CLARIDAD INTERIOR", "Pasas semanas en meditación silenciosa. Te enfrentas a tus demonios: tu ira, tu arrogancia, tu dolor. Llegas a una conclusión: no tienes que elegir entre ser un Wayne o un Al Ghul. Puedes ser ambos. Puedes tomar lo mejor de cada legado y forjar algo nuevo.", "damian_meditation.png")
        self.historia["damian_dificil_meditacion"].agregar_opcion("Regresar al mundo con un nuevo propósito", "damian_dificil_batalla_final", stat="salud", cambio=20, stat2="reputacion", cambio2=10)

        self.historia["damian_dificil_tutoria_jason"] = NodoHistoria("damian_dificil_tutoria_jason", "LECCIONES DE RED HOOD", "Jason te enseña su versión de la justicia. Patrullan juntos. Es brutal, es rápido. 'La regla número uno, pequeño D,' dice Jason, 'es que los monstruos no merecen segundas oportunidades.' Aprendes a ser más letal, más eficiente. Pero, ¿a qué costo?", "damian_jason_lesson.png")
        self.historia["damian_dificil_tutoria_jason"].agregar_opcion("Adoptar completamente sus métodos", "damian_dificil_batalla_final", stat="reputacion", cambio=-20)
        self.historia["damian_dificil_tutoria_jason"].agregar_opcion("Rechazar la matanza, pero adoptar la brutalidad", "damian_dificil_batalla_final", stat="reputacion", cambio=-10)

        self.historia["damian_dificil_debate_moral"] = NodoHistoria("damian_dificil_debate_moral", "DEBATE MORAL", "Rechazas los métodos de Jason. 'Matar nos hace iguales a ellos,' argumentas. 'No,' responde Jason, 'nos hace efectivos. Bruce vive en un cuento de hadas. Nosotros vivimos en el mundo real.' El debate te obliga a solidificar tus propias creencias. ¿Dónde trazas la línea?", "damian_jason_debate.png")
        self.historia["damian_dificil_debate_moral"].agregar_opcion("Decidir que la línea de no matar es absoluta", "damian_dificil_batalla_final", stat="reputacion", cambio=15)
        self.historia["damian_dificil_debate_moral"].agregar_opcion("Decidir que la línea es... flexible", "damian_dificil_batalla_final", stat="reputacion", cambio=-5)























































class JuegoAventuraGUI:
    """Interfaz grÃ¡fica del juego usando Tkinter"""
    # ...resto del cÃ³digo...

    # Colores de la paleta Red Hood
    COLOR_FONDO = "#000000"           # Negro
    COLOR_ROJO_OSCURO = "#8B1A1A"     # Rojo oscuro (45% transparencia simulada)
    COLOR_ROJO_MEDIO = "#B22222"      # Rojo medio (65% transparencia simulada)
    COLOR_ROJO_BRILLANTE = "#DF2531"  # Rojo brillante
    COLOR_TEXTO = "#FFFFFF"           # Blanco
    COLOR_TEXTO_SECUNDARIO = "#CCCCCC"

    def __init__(self, root):
        self.root = root
        self.root.title("RED HOOD: Juego de Aventura")
        self.root.geometry("1000x700")
        self.root.configure(bg=self.COLOR_FONDO)

        # Centrar ventana
        self.centrar_ventana()

        # Juego base
        self.juego = JuegoAventuraBase()

        # Variables
        self.imagenes_cache = {}
        # Inicializar audio (intenta reproducir musica de fondo si pygame estÃ¡ disponible)
        self.inicializar_audio()
        # Asegurar que al cerrar la ventana se detenga el audio correctamente
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Crear frames principales
        self.crear_menu_principal()

    def centrar_ventana(self):
        """Centrar la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    # ------------------- Audio (opcional, usa pygame si estÃ¡ disponible) -------------------
    def inicializar_audio(self):
        """Intentar inicializar el sistema de audio y cargar la pista de fondo.
        Si pygame no estÃ¡ disponible o el archivo no existe, desactiva el audio silenciosamente.
        """
        # Ruta relativa al proyecto
        self.audio_file = os.path.join("audio", "Neo-NoirCityscape(Instrumental)_FULL_SONG_MusicGPT.mp3")
        self.audio_enabled = False

        if not PYGAME_AVAILABLE:
            # pygame no estÃ¡ instalado; no hacemos nada
            return

        try:
            # Inicializar el mezclador
            pygame.mixer.init()
            if os.path.exists(self.audio_file):
                try:
                    pygame.mixer.music.load(self.audio_file)
                    self.audio_enabled = True
                    # Reproducir en bucle
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print(f"No se pudo cargar/reproducir el audio: {e}")
                    self.audio_enabled = False
            else:
                print(f"Archivo de audio no encontrado: {self.audio_file}")
        except Exception as e:
            print(f"Error inicializando audio (pygame): {e}")
            self.audio_enabled = False

    def detener_audio(self):
        """Detener y limpiar el sistema de audio si estÃ¡ activo."""
        if PYGAME_AVAILABLE and self.audio_enabled:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception:
                pass

    def on_close(self):
        """Manejar cierre de ventana: detener audio y destruir ventana."""
        try:
            self.detener_audio()
        finally:
            try:
                self.root.destroy()
            except Exception:
                # Fallback: salir del programa
                try:
                    self.root.quit()
                except Exception:
                    pass
    # ----------------------------------------------------------------------------------------

    def limpiar_ventana(self):
        """Limpiar todos los widgets de la ventana"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def cargar_imagen(self, nombre_archivo, ancho=400, alto=300):
        """Cargar una imagen (o mostrar placeholder si no existe)"""
        try:
            # Intentar cargar imagen desde carpeta 'imagenes/'
            ruta = os.path.join("imagenes", nombre_archivo)
            if os.path.exists(ruta):
                img = Image.open(ruta)
                img = img.resize((ancho, alto), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            else:
                # Crear imagen placeholder
                return self.crear_placeholder(ancho, alto, nombre_archivo)
        except Exception as e:
            return self.crear_placeholder(ancho, alto, f"Error: {e}")

    def crear_placeholder(self, ancho, alto, texto):
        """Crear imagen placeholder cuando no existe la imagen"""
        img = Image.new('RGB', (ancho, alto), color=self.COLOR_ROJO_OSCURO)
        # AquÃ­ podrÃ­as agregar texto a la imagen usando ImageDraw
        return ImageTk.PhotoImage(img)

    def crear_menu_principal(self):
        """Crear el menÃº principal"""
        self.limpiar_ventana()

        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.COLOR_FONDO)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # TÃ­tulo
        titulo_frame = tk.Frame(main_frame, bg=self.COLOR_FONDO)
        titulo_frame.pack(pady=30)

        titulo = tk.Label(
            titulo_frame,
            text="RED HOOD",
            font=("Arial Black", 48, "bold"),
            fg=self.COLOR_ROJO_BRILLANTE,
            bg=self.COLOR_FONDO
        )
        titulo.pack()

        subtitulo = tk.Label(
            titulo_frame,
            text="JUEGO DE AVENTURA EN TEXTO",
            font=("Arial", 18),
            fg=self.COLOR_TEXTO,
            bg=self.COLOR_FONDO
        )
        subtitulo.pack(pady=5)

        # Botones del menÃº
        botones_frame = tk.Frame(main_frame, bg=self.COLOR_FONDO)
        botones_frame.pack(pady=40)

        btn_nueva = tk.Button(
            botones_frame,
            text="NUEVA PARTIDA",
            font=("Arial", 16, "bold"),
            bg=self.COLOR_ROJO_BRILLANTE,
            fg=self.COLOR_TEXTO,
            activebackground=self.COLOR_ROJO_MEDIO,
            activeforeground=self.COLOR_TEXTO,
            width=20,
            height=2,
            cursor="hand2",
            command=self.nueva_partida
        )
        btn_nueva.pack(pady=10)

        btn_cargar = tk.Button(
            botones_frame,
            text="CARGAR PARTIDA",
            font=("Arial", 16, "bold"),
            bg=self.COLOR_ROJO_MEDIO,
            fg=self.COLOR_TEXTO,
            activebackground=self.COLOR_ROJO_OSCURO,
            activeforeground=self.COLOR_TEXTO,
            width=20,
            height=2,
            cursor="hand2",
            command=self.cargar_partida
        )
        btn_cargar.pack(pady=10)

        btn_creditos = tk.Button(
            botones_frame,
            text="CRÃ‰DITOS",
            font=("Arial", 16, "bold"),
            bg=self.COLOR_ROJO_OSCURO,
            fg=self.COLOR_TEXTO,
            activebackground=self.COLOR_ROJO_MEDIO,
            activeforeground=self.COLOR_TEXTO,
            width=20,
            height=2,
            cursor="hand2",
            command=self.mostrar_creditos
        )
        btn_creditos.pack(pady=10)

        btn_salir = tk.Button(
            botones_frame,
            text="SALIR",
            font=("Arial", 14),
            bg=self.COLOR_FONDO,
            fg=self.COLOR_TEXTO_SECUNDARIO,
            activebackground=self.COLOR_ROJO_OSCURO,
            activeforeground=self.COLOR_TEXTO,
            width=20,
            height=1,
            cursor="hand2",
            command=self.on_close
        )
        btn_salir.pack(pady=20)

        # Footer
        footer = tk.Label(
            main_frame,
            text="Basado en los personajes de DC Comics",
            font=("Arial", 10),
            fg=self.COLOR_TEXTO_SECUNDARIO,
            bg=self.COLOR_FONDO
        )
        footer.pack(side='bottom', pady=10)

###segundo bloque de codigo final

    def nueva_partida(self):
        """Muestra la pantalla de selecciÃ³n de personaje."""
        self.limpiar_ventana()

        frame = tk.Frame(self.root, bg=self.COLOR_FONDO)
        frame.pack(expand=True, fill='both', padx=20, pady=20)

        tk.Label(
            frame,
            text="SELECCIONA UN PERSONAJE",
            font=("Arial", 24, "bold"),
            fg=self.COLOR_ROJO_BRILLANTE,
            bg=self.COLOR_FONDO
        ).pack(pady=20)

        personajes_frame = tk.Frame(frame, bg=self.COLOR_FONDO)
        personajes_frame.pack(pady=20)

        personajes = [
            ("Red Hood", "#C00000", lambda: self.personaje_seleccionado("RedHood")),
            ("Nightwing", "#00529B", lambda: self.personaje_seleccionado("Nightwing")),
            ("Red Robin", "#319C00", lambda: self.personaje_seleccionado("RedRobin")),
            ("Robin", "#FFD700", lambda: self.personaje_seleccionado("Robin"))
        ]

        for i, (nombre, color, comando) in enumerate(personajes):
            btn = tk.Button(
                personajes_frame,
                text=nombre,
                font=("Arial", 16, "bold"),
                bg=color,
                fg=self.COLOR_TEXTO if nombre != "Robin" else self.COLOR_FONDO,
                width=15,
                height=3,
                cursor="hand2",
                command=comando
            )
            btn.grid(row=0, column=i, padx=15, pady=10)

        tk.Button(
            frame,
            text="â† Volver",
            font=("Arial", 12),
            bg=self.COLOR_FONDO,
            fg=self.COLOR_TEXTO_SECUNDARIO,
            cursor="hand2",
            command=self.crear_menu_principal
        ).pack(pady=40)

    def personaje_seleccionado(self, personaje):
        """Maneja la selecciÃ³n de un personaje y muestra la dificultad."""
        if personaje == "RedHood":
            self.juego.personaje_actual = "jason"
            self.mostrar_seleccion_dificultad("Jason Todd", "RED HOOD")
        elif personaje == "Nightwing":
            self.juego.personaje_actual = "dick"
            self.mostrar_seleccion_dificultad("Dick Grayson", "NIGHTWING")
        elif personaje == "RedRobin":
            self.juego.personaje_actual = "tim"
            self.mostrar_seleccion_dificultad("Tim Drake", "RED ROBIN")
        elif personaje == "Robin":
            self.juego.personaje_actual = "damian"
            self.mostrar_seleccion_dificultad("Damian Wayne", "ROBIN")

    def mostrar_seleccion_dificultad(self, nombre_personaje, titulo_personaje):
        """Muestra la pantalla para seleccionar la dificultad de la historia."""
        self.limpiar_ventana()

        frame = tk.Frame(self.root, bg=self.COLOR_FONDO)
        frame.pack(expand=True, fill='both', padx=20, pady=20)

        tk.Label(frame, text=f"NUEVA PARTIDA: {titulo_personaje}", font=("Arial", 24, "bold"), fg=self.COLOR_ROJO_BRILLANTE, bg=self.COLOR_FONDO).pack(pady=20)

        tk.Label(frame, text="Nombre del personaje:", font=("Arial", 14), fg=self.COLOR_TEXTO, bg=self.COLOR_FONDO).pack(pady=10)

        nombre_entry = tk.Entry(frame, font=("Arial", 14), bg=self.COLOR_ROJO_OSCURO, fg=self.COLOR_TEXTO, insertbackground=self.COLOR_TEXTO, width=30)
        nombre_entry.pack(pady=10)
        nombre_entry.insert(0, nombre_personaje)

        tk.Label(frame, text="\nSelecciona tu historia:", font=("Arial", 16, "bold"), fg=self.COLOR_TEXTO, bg=self.COLOR_FONDO).pack(pady=20)

        dificultades_frame = tk.Frame(frame, bg=self.COLOR_FONDO)
        dificultades_frame.pack(pady=20)

        # Textos de dificultad dinÃ¡micos segÃºn el personaje
        textos_dificultad_jason = {
            "jason": [
                "ðŸŸ¢ FÃCIL\nEl Segundo Robin\n~48 nodos | 25-35 min\n3 finales",
                "ðŸŸ¡ NORMAL\nMuerte en la Familia\n~45 nodos | 20-30 min\n3 finales",
                "ðŸ”´ DIFÃCIL\nBajo la Capucha Roja\n~150+ nodos | 60-90 min\n3 finales"
            ],
            "dick": [
                "ðŸŸ¢ FÃCIL\nEl Primer Robin\n~50 nodos | 25-35 min\n3 finales",
                "ðŸŸ¡ NORMAL\nNightwing\n~42 nodos | 20-30 min\n3 finales",
                "ðŸ”´ DIFÃCIL\nLÃ­Corte de los Buhos\n~53 nodos | 30-45 min\n5 finales"
            ],
            "tim": [
                "ðŸŸ¢ FÃCIL\nEl Detective\n~52 nodos | 25-35 min\n3 finales",
                "ðŸŸ¡ NORMAL\nRed Robin\n~40 nodos | 20-30 min\n3 finales",
                "ðŸ”´ DIFÃCIL\nLÃ­Busqueda de Bruce\n~50+ nodos | 30-45 min\n3 finales"
            ],
            "damian": [
                "ðŸŸ¢ FÃCIL\nEl Heredero\n~54 nodos | 30-40 min\n3 finales",
                "ðŸŸ¡ NORMAL\nLa Lucha Interna\n~50 nodos | 25-35 min\n4 finales",
                "ðŸ”´ DIFÃCIL\nLÃ­Muerte de Alfred\n~57 nodos | 35-50 min\n4 finales"
            ]
        }

        textos_dificultad = textos_dificultad_jason.get(self.juego.personaje_actual, textos_dificultad_jason["jason"])

        dificultades = [
            {
                "texto": textos_dificultad[0],
                "color_bg": self.COLOR_ROJO_OSCURO,
                "dificultad_id": "facil"
            },
            {
                "texto": textos_dificultad[1],
                "color_bg": self.COLOR_ROJO_MEDIO,
                "dificultad_id": "normal"
            },
            {
                "texto": textos_dificultad[2],
                "color_bg": self.COLOR_ROJO_BRILLANTE,
                "dificultad_id": "dificil"
            }
        ]

        for i, dif in enumerate(dificultades):
            btn = tk.Button(
                dificultades_frame,
                text=dif["texto"],
                font=("Arial", 11),
                bg=dif["color_bg"],
                fg=self.COLOR_TEXTO,
                width=30,
                height=6,
                cursor="hand2",
                wraplength=250,
                justify="center",
                command=lambda d=dif["dificultad_id"], n=nombre_entry: self.iniciar_juego(n.get(), d)
            )
            btn.grid(row=0, column=i, padx=10, pady=10)

        tk.Button(
            frame,
            text="â† Volver",
            font=("Arial", 12),
            bg=self.COLOR_FONDO,
            fg=self.COLOR_TEXTO_SECUNDARIO,
            cursor="hand2",
            command=self.nueva_partida
        ).pack(pady=20)

    def iniciar_juego(self, nombre, dificultad):
        """Iniciar el juego con la dificultad seleccionada"""
        if not nombre.strip():
            nombre = "HÃ©roe"

        self.juego.jugador = Jugador(nombre.strip())
        self.juego.dificultad = dificultad

        # Determinar nodo inicial adaptÃ¡ndose a los prefijos reales de los nodos
        # Mapear el identificador de personaje a su prefijo de nodos existente
        prefijos_por_personaje = {
            "jason": "jason",     # Red Hood
            "dick": "grayson",    # Nightwing usa prefijo 'grayson_'
            "tim": "tim",         # Placeholder si se agrega historia de Tim
            "damian": "damian"    # Placeholder si se agrega historia de Damian
        }
        prefijo = prefijos_por_personaje.get(self.juego.personaje_actual, self.juego.personaje_actual)
        nodo_inicial = f"{prefijo}_{dificultad}_inicio"

        self.juego.jugador.nodo_actual = nodo_inicial

        # Mostrar pantalla de juego
        self.mostrar_nodo(nodo_inicial)

    def cargar_partida(self):
        """Cargar una partida guardada"""
        if self.juego.cargar_partida():
            messagebox.showinfo("Ã‰xito", "Partida cargada correctamente")
            self.mostrar_nodo(self.juego.jugador.nodo_actual)
        else:
            messagebox.showerror("Error", "No se encontrÃ³ ninguna partida guardada")

    def mostrar_creditos(self):
        """Mostrar pantalla de crÃ©ditos"""
        self.limpiar_ventana()

        frame = tk.Frame(self.root, bg=self.COLOR_FONDO)
        frame.pack(expand=True, fill='both', padx=20, pady=20)

        tk.Label(
            frame,
            text="CRÃ‰DITOS",
            font=("Arial", 24, "bold"),
            fg=self.COLOR_ROJO_BRILLANTE,
            bg=self.COLOR_FONDO
        ).pack(pady=20)

        creditos_text = """
RED HOOD: JUEGO DE AVENTURA EN TEXTO

Basado en los personajes de DC Comics
Inspirado en el lore de Jason Todd / Red Hood

CARACTERÃSTICAS:
â€¢ Sistema de decisiones con consecuencias
â€¢ GestiÃ³n de inventario y recursos
â€¢ Persistencia de datos (guardado/cargado)
â€¢ Tres niveles de dificultad
â€¢ MÃºltiples finales
â€¢ Narrativa interactiva ramificada

TECNOLOGÃA:
â€¢ Lenguaje: Python 3.x
â€¢ GUI: Tkinter
â€¢ Bibliotecas: PIL/Pillow, json

PALETA DE COLORES:
â€¢ Rojo brillante (#DF2531)
â€¢ Rojo medio (#B22222)
â€¢ Rojo oscuro (#8B1A1A)
â€¢ Blanco (#FFFFFF)
â€¢ Negro (#000000)

Â¡Gracias por jugar!
        """

        text_widget = scrolledtext.ScrolledText(
            frame,
            font=("Arial", 12),
            bg=self.COLOR_ROJO_OSCURO,
            fg=self.COLOR_TEXTO,
            width=60,
            height=20,
            wrap=tk.WORD
        )
        text_widget.pack(pady=20)
        text_widget.insert('1.0', creditos_text)
        text_widget.config(state='disabled')

        tk.Button(
            frame,
            text="â† Volver",
            font=("Arial", 12),
            bg=self.COLOR_FONDO,
            fg=self.COLOR_TEXTO_SECUNDARIO,
            cursor="hand2",
            command=self.crear_menu_principal
        ).pack(pady=10)

    def mostrar_nodo(self, nodo_id):
        """Mostrar un nodo de la historia"""
        if nodo_id not in self.juego.historia:
            messagebox.showerror("Error", f"Nodo '{nodo_id}' no encontrado")
            self.crear_menu_principal()
            return

        nodo = self.juego.historia[nodo_id]
        self.limpiar_ventana()

        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.COLOR_FONDO)
        main_frame.pack(expand=True, fill='both')

        # Panel superior: Stats del jugador
        self.crear_panel_stats(main_frame)

        # Frame de contenido
        content_frame = tk.Frame(main_frame, bg=self.COLOR_FONDO)
        content_frame.pack(expand=True, fill='both', padx=20, pady=10)

        # Ãrea de imagen (izquierda)
        imagen_frame = tk.Frame(content_frame, bg=self.COLOR_ROJO_OSCURO, width=400, height=300)
        imagen_frame.pack(side='left', padx=10, pady=10)
        imagen_frame.pack_propagate(False)

        # Cargar y mostrar imagen
        if nodo.imagen:
            img = self.cargar_imagen(nodo.imagen, 400, 300)
            self.imagenes_cache[nodo_id] = img  # Mantener referencia

            imagen_label = tk.Label(imagen_frame, image=img, bg=self.COLOR_ROJO_OSCURO)
            imagen_label.pack(expand=True)
        else:
            tk.Label(
                imagen_frame,
                text="[Sin imagen]",
                font=("Arial", 14),
                fg=self.COLOR_TEXTO_SECUNDARIO,
                bg=self.COLOR_ROJO_OSCURO
            ).pack(expand=True)

        # Ãrea de texto (derecha)
        texto_frame = tk.Frame(content_frame, bg=self.COLOR_FONDO)
        texto_frame.pack(side='left', expand=True, fill='both', padx=10)

        # TÃ­tulo del nodo
        tk.Label(
            texto_frame,
            text=nodo.titulo,
            font=("Arial", 20, "bold"),
            fg=self.COLOR_ROJO_BRILLANTE,
            bg=self.COLOR_FONDO,
            wraplength=500,
            justify='left'
        ).pack(anchor='w', pady=10)

        # DescripciÃ³n del nodo
        desc_text = scrolledtext.ScrolledText(
            texto_frame,
            font=("Arial", 12),
            bg=self.COLOR_ROJO_OSCURO,
            fg=self.COLOR_TEXTO,
            wrap=tk.WORD,
            height=12,
            width=50
        )
        desc_text.pack(fill='both', expand=True, pady=10)
        desc_text.insert('1.0', nodo.descripcion)
        desc_text.config(state='disabled')

        # Panel de opciones (abajo)
        if nodo.es_final:
            self.mostrar_pantalla_final(main_frame, nodo)
        else:
            self.crear_panel_opciones(main_frame, nodo)

    def crear_panel_stats(self, parent):
        """Crear panel de estadÃ­sticas del jugador"""
        stats_frame = tk.Frame(parent, bg=self.COLOR_ROJO_OSCURO, height=80)
        stats_frame.pack(fill='x', padx=10, pady=10)
        stats_frame.pack_propagate(False)

        # Nombre
        tk.Label(
            stats_frame,
            text=f"ðŸ‘¤ {self.juego.jugador.nombre}",
            font=("Arial", 14, "bold"),
            fg=self.COLOR_TEXTO,
            bg=self.COLOR_ROJO_OSCURO
        ).pack(side='left', padx=20, pady=10)

        # Stats
        stats_container = tk.Frame(stats_frame, bg=self.COLOR_ROJO_OSCURO)
        stats_container.pack(side='left', expand=True, padx=20)

        # Salud
        tk.Label(
            stats_container,
            text=f"â¤ï¸ Salud: {self.juego.jugador.salud}/100",
            font=("Arial", 12),
            fg=self.COLOR_TEXTO,
            bg=self.COLOR_ROJO_OSCURO
        ).grid(row=0, column=0, padx=10, sticky='w')

        # ReputaciÃ³n
        tk.Label(
            stats_container,
            text=f"â­ ReputaciÃ³n: {self.juego.jugador.reputacion}/100",
            font=("Arial", 12),
            fg=self.COLOR_TEXTO,
            bg=self.COLOR_ROJO_OSCURO
        ).grid(row=0, column=1, padx=10, sticky='w')

        # Recursos
        tk.Label(
            stats_container,
            text=f"ðŸ’Ž Recursos: {self.juego.jugador.recursos}",
            font=("Arial", 12),
            fg=self.COLOR_TEXTO,
            bg=self.COLOR_ROJO_OSCURO
        ).grid(row=0, column=2, padx=10, sticky='w')

        # Inventario
        inv_text = f"ðŸŽ’ Inventario: {len(self.juego.jugador.inventario)} items"
        tk.Label(
            stats_container,
            text=inv_text,
            font=("Arial", 12),
            fg=self.COLOR_TEXTO,
            bg=self.COLOR_ROJO_OSCURO
        ).grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky='w')

        # Botones de acciÃ³n
        btn_frame = tk.Frame(stats_frame, bg=self.COLOR_ROJO_OSCURO)
        btn_frame.pack(side='right', padx=20)

        tk.Button(
            btn_frame,
            text="ðŸ’¾ Guardar",
            font=("Arial", 10),
            bg=self.COLOR_ROJO_MEDIO,
            fg=self.COLOR_TEXTO,
            cursor="hand2",
            command=self.guardar_juego
        ).pack(side='left', padx=5)

        tk.Button(
            btn_frame,
            text="ðŸ“Š Stats",
            font=("Arial", 10),
            bg=self.COLOR_ROJO_MEDIO,
            fg=self.COLOR_TEXTO,
            cursor="hand2",
            command=self.mostrar_inventario
        ).pack(side='left', padx=5)

        tk.Button(
            btn_frame,
            text="ðŸ  MenÃº",
            font=("Arial", 10),
            bg=self.COLOR_FONDO,
            fg=self.COLOR_TEXTO,
            cursor="hand2",
            command=self.volver_menu_confirmacion
        ).pack(side='left', padx=5)

    def crear_panel_opciones(self, parent, nodo):
        """Crear panel de opciones de decisiÃ³n"""
        opciones_frame = tk.Frame(parent, bg=self.COLOR_FONDO)
        opciones_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(
            opciones_frame,
            text="Â¿QUÃ‰ DECIDES?",
            font=("Arial", 16, "bold"),
            fg=self.COLOR_ROJO_BRILLANTE,
            bg=self.COLOR_FONDO
        ).pack(pady=10)

        # Crear botones para cada opciÃ³n
        for i, opcion in enumerate(nodo.opciones, 1):
            btn = tk.Button(
                opciones_frame,
                text=f"{i}. {opcion['texto']}",
                font=("Arial", 12),
                bg=self.COLOR_ROJO_MEDIO,
                fg=self.COLOR_TEXTO,
                activebackground=self.COLOR_ROJO_BRILLANTE,
                activeforeground=self.COLOR_TEXTO,
                wraplength=900,
                justify='left',
                cursor="hand2",
                command=lambda opt=opcion: self.elegir_opcion(nodo, opt)
            )
            btn.pack(fill='x', pady=5, padx=50)

    def elegir_opcion(self, nodo, opcion):
        """Procesar la elecciÃ³n del jugador"""
        # Aplicar cambios de stats
        # Con la refactorizaciÃ³n sugerida, esto serÃ­a mÃ¡s limpio:
        cambios = []
        for efecto in opcion.get("efectos", []):
            if efecto.get("tipo") == "stat":
                stat = efecto["stat"]
                cambio = efecto["cambio"]
                self.juego.jugador.modificar_stat(stat, cambio)
                simbolo = "+" if cambio > 0 else ""
                cambios.append(f"{stat.capitalize()}: {simbolo}{cambio}")
            elif efecto.get("tipo") == "item":
                item = efecto["item"]
                self.juego.jugador.agregar_item(item)
                cambios.append(f"Obtenido: {item}")

        # Guardar decisiÃ³n
        self.juego.jugador.guardar_decision(nodo.id, opcion['texto'])

        # Actualizar nodo actual
        self.juego.jugador.nodo_actual = opcion['siguiente']

        # Mostrar cambios si hay
        if cambios:
            messagebox.showinfo("Consecuencias", "\n".join(cambios))

        # Ir al siguiente nodo
        self.mostrar_nodo(opcion['siguiente'])

    def mostrar_pantalla_final(self, parent, nodo):
        """Mostrar pantalla de final del juego"""
        final_frame = tk.Frame(parent, bg=self.COLOR_FONDO)
        final_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(
            final_frame,
            text="ðŸ FIN DE LA HISTORIA ðŸ",
            font=("Arial", 20, "bold"),
            fg=self.COLOR_ROJO_BRILLANTE,
            bg=self.COLOR_FONDO
        ).pack(pady=10)

        # EstadÃ­sticas finales
        stats_text = f"""
Decisiones tomadas: {len(self.juego.jugador.decisiones)}
Salud final: {self.juego.jugador.salud}/100
ReputaciÃ³n final: {self.juego.jugador.reputacion}/100
Recursos finales: {self.juego.jugador.recursos}
Items obtenidos: {len(self.juego.jugador.inventario)}
        """

        tk.Label(
            final_frame,
            text=stats_text,
            font=("Arial", 12),
            fg=self.COLOR_TEXTO,
            bg=self.COLOR_FONDO,
            justify='left'
        ).pack(pady=10)

        # Botones
        btn_frame = tk.Frame(final_frame, bg=self.COLOR_FONDO)
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="ðŸ”„ Nueva Partida",
            font=("Arial", 14, "bold"),
            bg=self.COLOR_ROJO_BRILLANTE,
            fg=self.COLOR_TEXTO,
            cursor="hand2",
            width=20,
            command=self.nueva_partida
        ).pack(side='left', padx=10)

        tk.Button(
            btn_frame,
            text="ðŸ  MenÃº Principal",
            font=("Arial", 14, "bold"),
            bg=self.COLOR_ROJO_MEDIO,
            fg=self.COLOR_TEXTO,
            cursor="hand2",
            width=20,
            command=self.crear_menu_principal
        ).pack(side='left', padx=10)

    def guardar_juego(self):
        """Guardar el progreso del juego"""
        if self.juego.guardar_partida():
            messagebox.showinfo("Guardado", "Partida guardada exitosamente")
        else:
            messagebox.showerror("Error", "No se pudo guardar la partida")

    def mostrar_inventario(self):
        """Mostrar ventana de inventario completo"""
        ventana = tk.Toplevel(self.root)
        ventana.title("EstadÃ­sticas e Inventario")
        ventana.geometry("500x400")
        ventana.configure(bg=self.COLOR_FONDO)

        tk.Label(
            ventana,
            text="ðŸ“Š ESTADÃSTICAS E INVENTARIO",
            font=("Arial", 16, "bold"),
            fg=self.COLOR_ROJO_BRILLANTE,
            bg=self.COLOR_FONDO
        ).pack(pady=10)

        # Texto con stats
        text_widget = scrolledtext.ScrolledText(
            ventana,
            font=("Arial", 11),
            bg=self.COLOR_ROJO_OSCURO,
            fg=self.COLOR_TEXTO,
            width=50,
            height=15
        )
        text_widget.pack(padx=20, pady=10)

        info = f"""
JUGADOR: {self.juego.jugador.nombre}

ESTADÃSTICAS:
â¤ï¸  Salud: {self.juego.jugador.salud}/100
â­ ReputaciÃ³n: {self.juego.jugador.reputacion}/100
ðŸ’Ž Recursos: {self.juego.jugador.recursos}

INVENTARIO ({len(self.juego.jugador.inventario)} items):
"""
        for item in self.juego.jugador.inventario:
            info += f"  â€¢ {item}\n"

        info += f"\nDECISIONES TOMADAS: {len(self.juego.jugador.decisiones)}\n"
        info += f"DIFICULTAD: {self.juego.dificultad.upper()}\n"

        text_widget.insert('1.0', info)
        text_widget.config(state='disabled')

        tk.Button(
            ventana,
            text="Cerrar",
            font=("Arial", 12),
            bg=self.COLOR_ROJO_MEDIO,
            fg=self.COLOR_TEXTO,
            cursor="hand2",
            command=ventana.destroy
        ).pack(pady=10)

    def volver_menu_confirmacion(self):
        """Confirmar antes de volver al menÃº principal"""
        respuesta = messagebox.askyesno(
            "Confirmar",
            "Â¿Seguro que quieres volver al menÃº principal?\n"
            "AsegÃºrate de haber guardado tu progreso."
        )
        if respuesta:
            self.crear_menu_principal()

def main():
    """FunciÃ³n principal para ejecutar el juego"""
    root = tk.Tk()
    app = JuegoAventuraGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()






