from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap
from resources import ImageCache
from audio_manager import AudioManager
import json
import os
import sys
from pathlib import Path

# Importar clases del Robins.py original
sys.path.insert(0, str(Path(__file__).parent.parent))
from Robins import JuegoAventuraBase, Jugador

class MainController:
    """Controlador principal que separa la UI de la logica del juego (MVC).
    Implementa efectos visuales basicos (typewriter, hover, transiciones sencillas) y conecta botones del .ui.
    """
    def __init__(self, ui):
        self.ui = ui
        self.game_base = JuegoAventuraBase()  # Tu sistema original de Robins.py
        self.jugador = None  # Se creara al iniciar juego
        self.image_cache = ImageCache()
        self.audio = AudioManager()

        # Widget refs
        self.stacked = self.ui.findChild(QtWidgets.QStackedWidget, 'stackedMain')
        self.start_page = self.ui.findChild(QtWidgets.QWidget, 'startPage')
        self.menu_page = self.ui.findChild(QtWidgets.QWidget, 'menuPage')
        self.game_page = self.ui.findChild(QtWidgets.QWidget, 'gamePage')
        
        # Start page buttons
        self.newGameButton = self.ui.findChild(QtWidgets.QPushButton, 'newGameButton')
        self.loadGameButton = self.ui.findChild(QtWidgets.QPushButton, 'loadGameButton')
        self.creditsButtonStart = self.ui.findChild(QtWidgets.QPushButton, 'creditsButtonStart')
        self.settingsButton = self.ui.findChild(QtWidgets.QPushButton, 'settingsButton')
        self.exitButtonStart = self.ui.findChild(QtWidgets.QPushButton, 'exitButtonStart')

        # bottom bar buttons
        self.saveButton = self.ui.findChild(QtWidgets.QPushButton, 'saveButton')
        self.menuButton = self.ui.findChild(QtWidgets.QPushButton, 'menuButton')

        # menu cards
        self.cardJason = self.ui.findChild(QtWidgets.QPushButton, 'cardJason')
        self.cardDick = self.ui.findChild(QtWidgets.QPushButton, 'cardDick')
        self.cardTim = self.ui.findChild(QtWidgets.QPushButton, 'cardTim')
        self.cardDamian = self.ui.findChild(QtWidgets.QPushButton, 'cardDamian')
        
        # menu character images
        self.imageJason = self.ui.findChild(QtWidgets.QLabel, 'imageJason')
        self.imageDick = self.ui.findChild(QtWidgets.QLabel, 'imageDick')
        self.imageTim = self.ui.findChild(QtWidgets.QLabel, 'imageTim')
        self.imageDamian = self.ui.findChild(QtWidgets.QLabel, 'imageDamian')
        
        # Configurar imagenes de personajes
        self.setup_character_images()

        # side and center
        self.healthBar = self.ui.findChild(QtWidgets.QProgressBar, 'healthBar')
        self.repBar = self.ui.findChild(QtWidgets.QProgressBar, 'repBar')
        self.resBar = self.ui.findChild(QtWidgets.QProgressBar, 'resBar')
        self.sceneLabel = self.ui.findChild(QtWidgets.QLabel, 'sceneLabel')
        self.descText = self.ui.findChild(QtWidgets.QTextEdit, 'descText')
        self.optionsWidget = self.ui.findChild(QtWidgets.QWidget, 'optionsWidget')
        
        # Color del personaje actual (para hover de botones)
        self.current_character_color = '#DC143C'  # Rojo por defecto

        # connect signals
        # Start page
        self.newGameButton.clicked.connect(self.show_character_selection)
        self.loadGameButton.clicked.connect(self.load_saved_game)
        self.creditsButtonStart.clicked.connect(self.show_credits)
        self.settingsButton.clicked.connect(self.show_settings)
        self.exitButtonStart.clicked.connect(self.exit_game)
        
        # Character selection
        self.cardJason.clicked.connect(lambda: self.select_character('Jason Todd'))
        self.cardDick.clicked.connect(lambda: self.select_character('Dick Grayson'))
        self.cardTim.clicked.connect(lambda: self.select_character('Tim Drake'))
        self.cardDamian.clicked.connect(lambda: self.select_character('Damian Wayne'))
        
        # Bottom bar
        self.saveButton.clicked.connect(self.save_game)
        self.menuButton.clicked.connect(self.show_start_page)

        # typewriter
        self._type_timer = QTimer()
        self._type_timer.setInterval(14)
        self._type_timer.timeout.connect(self._type_step)
        self._type_buffer = ''
        self._type_index = 0

        # load UI from state
        self.stacked.setCurrentWidget(self.start_page)
        self.refresh_ui()
        
        # Iniciar musica de fondo cinematica
        self.audio.play_music('audio/CinematicSuspenseInstrumental_FULL_SONG_MusicGPT.mp3')

    def refresh_ui(self):
        # populate stats desde jugador de Robins.py
        if self.jugador:
            self.healthBar.setValue(self.jugador.salud)
            self.repBar.setValue(self.jugador.reputacion)
            self.resBar.setValue(self.jugador.recursos)
            # Actualizar titulo de la ventana con el nombre del personaje
            self.ui.setWindowTitle(f"ROBINS - {self.jugador.nombre}")
            self.stacked.setCurrentWidget(self.game_page)
            self.load_scene()
        else:
            self.ui.setWindowTitle("ROBINS - Juego de Aventura")
            self.stacked.setCurrentWidget(self.start_page)
    
    def show_start_page(self):
        """Muestra la pagina de inicio principal"""
        self.stacked.setCurrentWidget(self.start_page)
    
    def show_character_selection(self):
        """Muestra la pagina de seleccion de personajes"""
        self.audio.play('audio/click.wav')
        self.stacked.setCurrentWidget(self.menu_page)
    
    def load_saved_game(self):
        """Carga una partida guardada"""
        save_file = 'partida_guardada.json'
        if not os.path.exists(save_file):
            QtWidgets.QMessageBox.warning(
                self.ui,
                'No hay partida guardada',
                'No se encontro ninguna partida guardada.\n\nInicia una nueva partida primero.'
            )
            return
        
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Recrear jugador
            self.jugador = Jugador(save_data['nombre'])
            self.jugador.salud = save_data['salud']
            self.jugador.reputacion = save_data['reputacion']
            self.jugador.recursos = save_data['recursos']
            self.jugador.inventario = save_data['inventario']
            self.jugador.decisiones = save_data['decisiones']
            self.jugador.nodo_actual = save_data['nodo_actual']
            
            self.game_base.jugador = self.jugador
            self.game_base.dificultad = save_data.get('dificultad', 'Normal')
            
            self.audio.play('audio/click.wav')
            self.refresh_ui()
            
            QtWidgets.QMessageBox.information(
                self.ui,
                'Partida cargada',
                f'✅ Partida de {self.jugador.nombre} cargada exitosamente.'
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.ui,
                'Error al cargar',
                f'No se pudo cargar la partida:\n\n{str(e)}'
            )
    
    def show_settings(self):
        """Muestra el dialogo de configuracion de musica"""
        dialog = QtWidgets.QDialog(self.ui)
        dialog.setWindowTitle("Configuracion")
        dialog.setModal(True)
        dialog.setMinimumSize(400, 300)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Titulo
        title = QtWidgets.QLabel("<h2>⚙️ Configuracion</h2>")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Configuracion de musica
        music_group = QtWidgets.QGroupBox("Musica y Sonido")
        music_layout = QtWidgets.QVBoxLayout()
        
        # Control de volumen musica
        vol_label = QtWidgets.QLabel("Volumen de Musica:")
        music_layout.addWidget(vol_label)
        
        volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        volume_slider.setMinimum(0)
        volume_slider.setMaximum(100)
        volume_slider.setValue(self.audio.music_volume * 100)
        volume_slider.valueChanged.connect(lambda v: self.audio.set_music_volume(v / 100))
        music_layout.addWidget(volume_slider)
        
        # Volumen value label
        vol_value = QtWidgets.QLabel(f"{int(self.audio.music_volume * 100)}%")
        vol_value.setAlignment(QtCore.Qt.AlignCenter)
        volume_slider.valueChanged.connect(lambda v: vol_value.setText(f"{v}%"))
        music_layout.addWidget(vol_value)
        
        # Control de efectos de sonido
        sfx_label = QtWidgets.QLabel("Volumen de Efectos:")
        music_layout.addWidget(sfx_label)
        
        sfx_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sfx_slider.setMinimum(0)
        sfx_slider.setMaximum(100)
        sfx_slider.setValue(self.audio.sfx_volume * 100)
        sfx_slider.valueChanged.connect(lambda v: self.audio.set_sfx_volume(v / 100))
        music_layout.addWidget(sfx_slider)
        
        sfx_value = QtWidgets.QLabel(f"{int(self.audio.sfx_volume * 100)}%")
        sfx_value.setAlignment(QtCore.Qt.AlignCenter)
        sfx_slider.valueChanged.connect(lambda v: sfx_value.setText(f"{v}%"))
        music_layout.addWidget(sfx_value)
        
        music_group.setLayout(music_layout)
        layout.addWidget(music_group)
        
        # Boton cerrar
        close_btn = QtWidgets.QPushButton("Cerrar")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QGroupBox {
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #DC143C;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF1744;
            }
        """)
        
        self.audio.play('audio/click.wav')
        dialog.exec()

    def setup_character_images(self):
        """Carga las imagenes arriba de cada boton de personaje"""
        character_images = {
            'Jason Todd': ('Imagenes/redhoodportada.png', self.imageJason),
            'Dick Grayson': ('Imagenes/graysonportada.png', self.imageDick),
            'Tim Drake': ('Imagenes/redrobinportada.png', self.imageTim),
            'Damian Wayne': ('Imagenes/robinportada.png', self.imageDamian)
        }
        
        for char_name, (img_path, label_widget) in character_images.items():
            if label_widget and os.path.exists(img_path):
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    # Escalar imagen al tamano fijo (250x250)
                    scaled_pixmap = pixmap.scaled(
                        250, 250,
                        QtCore.Qt.KeepAspectRatio,
                        QtCore.Qt.SmoothTransformation
                    )
                    label_widget.setPixmap(scaled_pixmap)
        
        # Estilos personalizados para cada boton
        self.setup_character_button_styles()
    
    def setup_character_button_styles(self):
        """Configura estilos unicos para cada boton de personaje"""
        # Colores caracteristicos de cada Robin
        button_styles = {
            self.cardJason: {
                'color': '#DC143C',  # Rojo Crimson (Red Hood)
                'name': 'Jason Todd',
                'subtitle': 'RED HOOD'
            },
            self.cardDick: {
                'color': '#1E90FF',  # Azul Dodger (Nightwing)
                'name': 'Dick Grayson',
                'subtitle': 'NIGHTWING'
            },
            self.cardTim: {
                'color': '#228B22',  # Verde Forest (Red Robin)
                'name': 'Tim Drake',
                'subtitle': 'RED ROBIN'
            },
            self.cardDamian: {
                'color': '#FFD700',  # Amarillo Dorado (Robin)
                'name': 'Damian Wayne',
                'subtitle': 'ROBIN'
            }
        }
        
        for button, config in button_styles.items():
            if button:
                color = config['color']
                button.setMinimumHeight(65)
                button.setMaximumHeight(65)
                button.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #2a2a2a,
                            stop:1 #1a1a1a);
                        color: {color};
                        border: 3px solid {color};
                        border-radius: 12px;
                        padding: 12px;
                        font-size: 18px;
                        font-weight: bold;
                        text-align: center;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {color},
                            stop:1 rgba({self._hex_to_rgb(color)}, 0.7));
                        color: white;
                        border: 3px solid white;
                        font-size: 19px;
                        
                    }}
                    QPushButton:pressed {{
                        background-color: {color};
                        border: 4px solid white;
                        color: black;
                    }}
                """)

    def select_character(self, character_name):
        """Muestra un dialogo para seleccionar dificultad y luego inicia el juego"""
        # Crear dialogo de seleccion de dificultad
        dialog = QtWidgets.QDialog(self.ui)
        dialog.setWindowTitle(f"Selecciona Dificultad - {character_name}")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Titulo
        title_label = QtWidgets.QLabel(f"<h2>{character_name}</h2><p>Selecciona la dificultad:</p>")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Textos de dificultad segun personaje
        dificultades_info = {
            "Jason Todd": {
                "Facil": "🟢 FACIL\nEl Segundo Robin\n~48 nodos | 25-35 min\n3 finales",
                "Normal": "🟡 NORMAL\nMuerte en la Familia\n~45 nodos | 20-30 min\n3 finales",
                "Dificil": "🔴 DIFICIL\nBajo la Capucha Roja\n~150+ nodos | 60-90 min\n3 finales"
            },
            "Dick Grayson": {
                "Facil": "🟢 FACIL\nEl Primer Robin\n~50 nodos | 25-35 min\n3 finales",
                "Normal": "🟡 NORMAL\nNightwing\n~42 nodos | 20-30 min\n3 finales",
                "Dificil": "🔴 DIFICIL\nCorte de los Buhos\n~53 nodos | 30-45 min\n5 finales"
            },
            "Tim Drake": {
                "Facil": "🟢 FACIL\nEl Detective\n~52 nodos | 25-35 min\n3 finales",
                "Normal": "🟡 NORMAL\nRed Robin\n~40 nodos | 20-30 min\n3 finales",
                "Dificil": "🔴 DIFICIL\nBusqueda de Bruce\n~50+ nodos | 30-45 min\n3 finales"
            },
            "Damian Wayne": {
                "Facil": "🟢 FACIL\nEl Heredero\n~54 nodos | 30-40 min\n3 finales",
                "Normal": "🟡 NORMAL\nLa Lucha Interna\n~50 nodos | 25-35 min\n4 finales",
                "Dificil": "🔴 DIFICIL\nMuerte de Alfred\n~57 nodos | 35-50 min\n4 finales"
            }
        }
        
        info = dificultades_info.get(character_name, dificultades_info["Jason Todd"])
        
        # Botones de dificultad
        for diff_name, diff_text in info.items():
            btn = QtWidgets.QPushButton(diff_text)
            btn.setMinimumHeight(100)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 12px;
                    padding: 10px;
                    text-align: center;
                    background-color: #2a2a2a;
                    color: white;
                    border: 2px solid #444;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                    border-color: #666;
                }
            """)
            btn.clicked.connect(lambda checked=False, d=diff_name: self._start_with_difficulty(character_name, d, dialog))
            layout.addWidget(btn)
        
        # Boton cancelar
        cancel_btn = QtWidgets.QPushButton("← Volver")
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)
        
        dialog.exec()
    
    def _start_with_difficulty(self, character_name, difficulty, dialog):
        """Inicia el juego con el personaje y dificultad seleccionados"""
        dialog.accept()
        self.start_game(character_name, difficulty)
    
    def start_game_with_difficulty(self, difficulty):
        """Metodo obsoleto - ya no se usa"""
        pass
    def start_game(self, character_name, difficulty):
        """Inicia un nuevo juego con el personaje seleccionado usando Robins.py original"""
        # Crear jugador con el sistema original de Robins.py
        self.jugador = Jugador(character_name)
        self.game_base.jugador = self.jugador
        self.game_base.dificultad = difficulty
        
        # Establecer color del personaje para hover de botones
        character_colors = {
            'Jason Todd': '#DC143C',      # Rojo
            'Dick Grayson': '#1E90FF',    # Azul
            'Tim Drake': '#228B22',       # Verde
            'Damian Wayne': '#FFD700'     # Amarillo
        }
        self.current_character_color = character_colors.get(character_name, '#DC143C')
        
        # Determinar nodo inicial segun personaje y dificultad
        nodo_map = {
            ("Jason Todd", "Facil"): "jason_facil_inicio",
            ("Jason Todd", "Normal"): "jason_normal_inicio",
            ("Jason Todd", "Dificil"): "jason_dificil_inicio",
            ("Dick Grayson", "Facil"): "grayson_facil_inicio",
            ("Dick Grayson", "Normal"): "grayson_normal_inicio",
            ("Dick Grayson", "Dificil"): "grayson_dificil_inicio",
            ("Tim Drake", "Facil"): "tim_facil_inicio",
            ("Tim Drake", "Normal"): "tim_normal_inicio",
            ("Tim Drake", "Dificil"): "tim_dificil_inicio",
            ("Damian Wayne", "Facil"): "damian_facil_inicio",
            ("Damian Wayne", "Normal"): "damian_normal_inicio",
            ("Damian Wayne", "Dificil"): "damian_dificil_inicio"
        }
        
        self.jugador.nodo_actual = nodo_map.get((character_name, difficulty), "jason_facil_inicio")
        
        # Reproducir sonido de confirmacion
        self.audio.play('audio/confirm.wav')
        
        # Actualizar UI y titulo de ventana
        self.ui.setWindowTitle(f"ROBINS - {character_name}")
        self.stacked.setCurrentWidget(self.game_page)
        self.load_scene()
        self.update_stats()

    def save_game(self):
        """Guardar partida al archivo JSON"""
        if not self.jugador:
            QtWidgets.QMessageBox.warning(
                self.ui,
                'No hay partida',
                'Debes iniciar un juego antes de guardar.'
            )
            return
        
        try:
            save_data = {
                "nombre": self.jugador.nombre,
                "salud": self.jugador.salud,
                "reputacion": self.jugador.reputacion,
                "recursos": self.jugador.recursos,
                "inventario": self.jugador.inventario,
                "decisiones": self.jugador.decisiones,
                "nodo_actual": self.jugador.nodo_actual,
                "dificultad": self.game_base.dificultad
            }
            
            save_path = os.path.join(os.path.dirname(__file__), '..', 'partida_guardada.json')
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self.audio.play('audio/save.wav')
            
            # Mostrar confirmacion
            QtWidgets.QMessageBox.information(
                self.ui,
                'Partida guardada',
                f'✅ Partida de {self.jugador.nombre} guardada exitosamente.\n\nArchivo: partida_guardada.json'
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.ui,
                'Error al guardar',
                f'No se pudo guardar la partida:\n\n{str(e)}'
            )

    def load_scene(self):
        """Carga la escena actual desde el nodo del juego de Robins.py"""
        if not self.jugador:
            return
            
        # Obtener nodo actual del sistema original
        nodo_id = self.jugador.nodo_actual
        node = self.game_base.historia.get(nodo_id)
        if not node:
            return
        
        # Extraer datos del nodo (objetos NodoHistoria de Robins.py)
        title = node.titulo
        text = node.descripcion
        img = node.imagen
        options = node.opciones
        
        # Cargar imagen desde Imagenes/ folder
        img_path = f'Imagenes/{img}'
        pix = self.image_cache.get(img_path)
        
        if pix:
            self.sceneLabel.setPixmap(pix.scaled(
                self.sceneLabel.size(), 
                QtCore.Qt.KeepAspectRatio, 
                QtCore.Qt.SmoothTransformation
            ))
        else:
            # Generar placeholder con titulo del nodo
            size = self.sceneLabel.size()
            if size.width() <= 0 or size.height() <= 0:
                size = QtCore.QSize(640, 360)
            
            pm = QtGui.QPixmap(size)
            pm.fill(QtGui.QColor('#0b0f14'))
            
            painter = QtGui.QPainter(pm)
            painter.setPen(QtGui.QColor('#8aa6c6'))
            font = painter.font()
            font.setPointSize(14)
            painter.setFont(font)
            
            # Mostrar titulo del nodo en placeholder
            placeholder_text = f'{title}\n\n(Imagen: {img})'
            painter.drawText(pm.rect(), QtCore.Qt.AlignCenter, placeholder_text)
            painter.end()
            
            self.sceneLabel.setPixmap(pm)
        
        # Actualizar titulo y texto con typewriter effect
        self.start_typewriter(text)
        
        # Poblar opciones
        self.populate_options(options)

    def resize_scene(self):
        # when main window resizes, scale pixmap
        if not self.jugador:
            return
        nodo = self.game_base.historia.get(self.jugador.nodo_actual)
        if nodo and nodo.imagen:
            img_path = f'Imagenes/{nodo.imagen}'
            pix = self.image_cache.get(img_path)
            if pix:
                self.sceneLabel.setPixmap(pix.scaled(self.sceneLabel.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def start_typewriter(self, text):
        self._type_buffer = text
        self._type_index = 0
        self.descText.clear()
        self._type_timer.start()

    def _type_step(self):
        if self._type_index >= len(self._type_buffer):
            self._type_timer.stop()
            return
        self._type_index += 1
        self.descText.setPlainText(self._type_buffer[:self._type_index])
        # autoscroll to bottom
        self.descText.moveCursor(QtGui.QTextCursor.End)

    def populate_options(self, options):
        """Pobla los botones de opciones desde el nodo actual"""
        layout = self.optionsWidget.layout()
        
        # Limpiar botones existentes
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        
        # Obtener color del personaje actual
        hover_color = self.current_character_color
        
        # Crear botones para cada opcion
        # opciones es una lista de dicts: {"texto": str, "siguiente": str, "stat": str, ...}
        for idx, opt_data in enumerate(options):
            if isinstance(opt_data, dict):
                label = opt_data.get('texto', 'Continuar')
                next_id = opt_data.get('siguiente')
            else:
                # Fallback for old tuple format
                label = str(opt_data)
                next_id = None
            
            # Agregar numero a la opcion para mejor UX
            numbered_label = f"► {label}"
            
            btn = QtWidgets.QPushButton(numbered_label)
            btn.setObjectName('optionButton')
            btn.setProperty('class', 'optionButton')
            btn.setMinimumHeight(55)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            
            # Estilo mejorado con color dinamico segun el personaje
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2a2a2a,
                        stop:1 #1a1a1a);
                    color: #ccc;
                    border: 2px solid #444;
                    border-radius: 6px;
                    padding: 14px 20px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba({self._hex_to_rgb(hover_color)}, 0.15),
                        stop:1 #1a1a1a);
                    border: 2px solid {hover_color};
                    color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {hover_color};
                    border: 2px solid white;
                    color: white;
                }}
            """)
            
            # Conectar boton con los datos completos de la opcion
            if next_id:
                btn.clicked.connect(
                    lambda checked=False, nid=next_id, data=opt_data: 
                    self.on_option_selected(nid, data)
                )
            
            layout.addWidget(btn)
    
    def _hex_to_rgb(self, hex_color):
        """Convierte color hexadecimal a valores RGB para gradientes"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"

    def on_option_selected(self, next_node_id, option_data):
        """Maneja la seleccion de una opcion y avanza al siguiente nodo usando Robins.py"""
        self.audio.play('audio/click.wav')
        
        if not self.jugador:
            return
            
        # Guardar decision
        self.jugador.guardar_decision(self.jugador.nodo_actual, option_data.get('texto', ''))
        
        # Aplicar modificaciones de stats del sistema original
        if option_data.get('stat') and option_data.get('cambio'):
            self.jugador.modificar_stat(option_data['stat'], option_data['cambio'])
        if option_data.get('stat2') and option_data.get('cambio2'):
            self.jugador.modificar_stat(option_data['stat2'], option_data['cambio2'])
        if option_data.get('item'):
            self.jugador.agregar_item(option_data['item'])
        
        # Avanzar al siguiente nodo
        self.jugador.nodo_actual = next_node_id
        
        # Actualizar UI
        self.load_scene()
        self.update_stats()

    def update_stats(self):
        """Actualiza las barras de estadisticas desde el jugador"""
        if not self.jugador:
            return
        self.healthBar.setValue(self.jugador.salud)
        self.repBar.setValue(self.jugador.reputacion)
        self.resBar.setValue(self.jugador.recursos)

    # small helpers
    def apply_character_palette(self, name):
        # set a QSS snippet for primary color per character
        palettes = {
            'Jason Todd': '#d32f2f',
            'Dick Grayson': '#1976d2',
            'Tim Drake': '#388e3c',
            'Damian Wayne': '#9c27b0'
        }
        color = palettes.get(name, '#607d8b')
        snippet = f"QProgressBar::chunk {{ background: {color}; }}"
        self.ui.setStyleSheet(self.ui.styleSheet() + '\n' + snippet)

    def show_credits(self):
        """Muestra un dialogo con los creditos del juego"""
        dialog = QtWidgets.QDialog(self.ui)
        dialog.setWindowTitle("Creditos")
        dialog.setModal(True)
        dialog.setMinimumSize(500, 400)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Texto de creditos con HTML
        credits_text = """
        <div style='text-align: center; color: white;'>
            <h1 style='color: #d32f2f; margin-bottom: 20px;'>🦇 ROBINS 🦇</h1>
            <h2 style='margin-bottom: 30px;'>Juego de Aventura en Texto</h2>
            
            <p style='font-size: 16px; margin: 20px 0;'>
                <b>Sistema de Juego:</b><br>
                998 nodos narrativos interactivos<br>
                12 caminos de historia unicos<br>
                4 Robins jugables × 3 dificultades
            </p>
            
            <p style='font-size: 16px; margin: 20px 0;'>
                <b>Personajes:</b><br>
                Jason Todd - El Segundo Robin<br>
                Dick Grayson - El Primer Robin<br>
                Tim Drake - El Detective<br>
                Damian Wayne - El Heredero
            </p>
            
            <p style='font-size: 14px; margin: 30px 0; color: #aaa;'>
                Inspirado en las historias de DC Comics<br>
                Batman, Robin y la familia de murcielagos
            </p>
            
            <p style='font-size: 16px; margin: 20px 0;'>
                <b>Tecnologia:</b><br>
                Python + PySide6<br>
                Sistema MVC con efectos visuales
            </p>
            
            <p style='font-size: 12px; margin-top: 40px; color: #666;'>
                © 2024 - Proyecto de aventura interactiva
            </p>
        </div>
        """
        
        credits_label = QtWidgets.QLabel(credits_text)
        credits_label.setWordWrap(True)
        credits_label.setTextFormat(QtCore.Qt.RichText)
        credits_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Scroll area para el texto
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(credits_label)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1a1a1a;
                border: none;
            }
        """)
        
        layout.addWidget(scroll)
        
        # Boton de cerrar
        close_btn = QtWidgets.QPushButton("← Cerrar")
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f44336;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        # Establecer estilo del dialogo
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
        """)
        
        self.audio.play('audio/click.wav')
        dialog.exec()

    def exit_game(self):
        """Cierra la aplicacion"""
        reply = QtWidgets.QMessageBox.question(
            self.ui,
            'Salir del juego',
            '¿Estas seguro de que quieres salir?\n\n¡No olvides guardar tu partida!',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.audio.play('audio/click.wav')
            QtWidgets.QApplication.quit()
