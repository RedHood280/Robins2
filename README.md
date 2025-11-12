# Robins Visual Novel - Qt UI

Este repositorio contiene una conversion de la aplicacion de historia interactiva a una interfaz moderna usando Qt for Python (PySide6). El diseno contiene:

- `ui/main_window.ui`: UI principal diseniada para cargarse con Qt (QMainWindow con paginas de menu y juego).
- `controllers/main_controller.py`: Logica de interfaz / controlador (separada de la logica del juego).
- `model/game_state.py`: Estado del juego (MVC) y funciones de guardado/carga.
- `resources.py`: Cache de imagenes para carga anticipada.
- `audio_manager.py`: Reproduccion de sonidos opcional con pygame.
- `styles.qss`: Estilos QSS para dar la apariencia visual tematica.

Requisitos:

- Python 3.8+
- Instalar dependencias: `pip install -r requirements.txt`

Como ejecutar (Windows PowerShell):

```powershell
pip install -r requirements.txt
python app.py
```

Notas:
- Las imagenes de escena deben colocarse en la carpeta `Imagenes/` y referenciadas por rutas dentro del `GameState`.
- No incluimos imagenes de stock; `Imagenes/placeholder_scene.png` es un marcador de posicion si lo desea.
- El .ui es intencionalmente simple y esta pensado para personalizarlo con Qt Designer si desea.
