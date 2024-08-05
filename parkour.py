from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

# Aplicación principal
app = Ursina(borderless=False)

# Semilla
random.seed(0)

# Ventana
window.size = (700, 700)

# Shader
Entity.default_shader = lit_with_shadows_shader

# Cargar sonido de salto en formato .mp3
jump_sound = Audio('coin_c_02-102844.mp3', autoplay=False)  # Asegúrate de que el archivo esté en la misma carpeta que main.py

# Definir jugador (inicialmente deshabilitado)
player = FirstPersonController()
player.disable()

# Crear menú de inicio
def show_gameplay_options():
    start_button.disable()
    gameplay_menu.enable()
    game_over_text.disable()  # Asegúrate de ocultar el texto de GAME OVER

menu = Entity(parent=camera.ui)
start_button = Button(text='Iniciar Juego', scale=(0.2, 0.1), position=(0, 0), parent=menu)
start_button.on_click = show_gameplay_options

def start_game():
    gameplay_menu.disable()
    difficulty_menu.enable()  # Muestra el menú de selección de dificultad

# Menú de opciones de jugabilidad
gameplay_menu = Entity(parent=camera.ui, enabled=False)

def set_gameplay_option(option):
    global gameplay_option
    gameplay_option = option
    configure_controls()  # Configura los controles pero no muestra la ayuda aún
    start_game()

# Título del menú de opciones
gameplay_label = Text(text='Seleccione el Modo de Jugabilidad', position=(0, 0.4), parent=gameplay_menu, scale=2, color=color.azure, origin=(0, 0))

# Botones de opciones de jugabilidad
clicks_button = Button(text='Especial (click derecho y click izquierdo)', scale=(0.6, 0.1), position=(0, 0.2), parent=gameplay_menu, color=color.black)
arrows_button = Button(text='Por Defecto (flechas arriba, abajo, izquierda, derecha)', scale=(0.8, 0.1), position=(0, 0.01), parent=gameplay_menu, color=color.black)
wsad_button = Button(text='Personalizado (teclas W, S, A, D)', scale=(0.6, 0.1), position=(0, -0.2), parent=gameplay_menu, color=color.black)

# Asignar funciones a los botones
clicks_button.on_click = Func(set_gameplay_option, 'clicks')
arrows_button.on_click = Func(set_gameplay_option, 'arrow keys')
wsad_button.on_click = Func(set_gameplay_option, 'wsad')

# Funciones de control
def update_with_clicks():
    if mouse.right:
        player.position += player.forward * 5 * time.dt
    if mouse.left:
        player.jump()
        jump_sound.play()  # Reproduce el sonido de salto

def update_with_arrow_keys():
    speed = 5 * time.dt
    direction = player.forward
    if held_keys['up arrow']:
        player.position += Vec3(direction.x, 0, direction.z) * speed
    if held_keys['down arrow']:
        player.position -= Vec3(direction.x, 0, direction.z) * speed
    if held_keys['left arrow']:
        player.position -= Vec3(direction.z, 0, -direction.x) * speed
    if held_keys['right arrow']:
        player.position += Vec3(direction.z, 0, -direction.x) * speed
    if held_keys['space']:
        player.jump()
        jump_sound.play()  # Reproduce el sonido de salto

def update_with_wsad():
    speed = 5 * time.dt
    direction = player.forward
    if held_keys['w']:
        player.position += Vec3(direction.x, 0, direction.z) * speed
    if held_keys['s']:
        player.position -= Vec3(direction.x, 0, direction.z) * speed
    if held_keys['a']:
        player.position -= Vec3(direction.z, 0, -direction.x) * speed
    if held_keys['d']:
        player.position += Vec3(direction.z, 0, -direction.x) * speed
    if held_keys['space']:
        player.jump()
        jump_sound.play()  # Reproduce el sonido de salto

# Crear menú de selección de dificultad
difficulty_menu = Entity(parent=camera.ui, enabled=False)

# Título del menú de dificultad
difficulty_label = Text(text='Seleccione la Dificultad', position=(0, 0.4), parent=difficulty_menu, scale=2, color=color.azure, origin=(0, 0))

# Botones de selección de dificultad
easy_button = Button(text='Fácil', scale=(0.5, 0.1), position=(0, 0.2), parent=difficulty_menu, color=color.green, text_color=color.black, text_scale=3, text_font='Arial')
medium_button = Button(text='Medio', scale=(0.5, 0.1), position=(0, 0), parent=difficulty_menu, color=color.yellow, text_color=color.black, text_scale=3, text_font='Arial')
hard_button = Button(text='Difícil', scale=(0.5, 0.1), position=(0, -0.2), parent=difficulty_menu, color=color.red, text_color=color.black, text_scale=3, text_font='Arial')

def set_difficulty(option):
    global difficulty_level
    difficulty_level = option
    difficulty_menu.disable()
    player.enable()  # Inicia el juego con la dificultad seleccionada
    configure_difficulty()
    # Después de configurar la dificultad, muestra el texto de ayuda
    help_lines = configure_controls()
    display_help(help_lines)

# Asignar funciones a los botones de dificultad
easy_button.on_click = Func(set_difficulty, 'easy')
medium_button.on_click = Func(set_difficulty, 'medium')
hard_button.on_click = Func(set_difficulty, 'hard')

def configure_difficulty():
    global cubos
    for cubo in cubos:
        destroy(cubo)
    cubos = []
    
    if difficulty_level == 'easy':
        create_easy_level()
    elif difficulty_level == 'medium':
        create_medium_level()
    elif difficulty_level == 'hard':
        create_hard_level()

# Variables para almacenar opciones
gameplay_option = 'None'
difficulty_level = 'None'

class Cubo(Entity):
    def __init__(self, position=(0, 0, 0), color=color.black33, name=''):
        super().__init__(
            position=position,
            model='cube',
            scale=(1, 1),
            origin_y=-.5,
            color=color,
            collider='box',
            name=name
        )

def create_level(num_cubes, num_rows, max_height, spacing):
    used_positions = set()
    
    def generate_unique_position():
        while True:
            x = random.randint(0, num_rows - 1) * spacing
            y = random.randint(1, max_height)  # Asegúrate de que la altura esté sobre el suelo
            z = random.randint(0, num_cubes - 1) * spacing
            position = (x, y, z)
            if position not in used_positions:
                used_positions.add(position)
                return position
    
    # Generar cubos
    for _ in range(num_cubes):
        position = generate_unique_position()
        cubo = Cubo(position=position)
        if random.choice([True, False]):
            cubo.y += 1
        elif random.choice([True, False]):
            cubo.y -= 1
        cubos.append(cubo)
    
    # Colocar el cubo verde al final
    if used_positions:  # Verifica que haya posiciones usadas
        last_position = sorted(list(used_positions), key=lambda pos: (pos[2], pos[0], pos[1]))[-1]
        green_cube_position = (last_position[0], last_position[1], last_position[2] + spacing)
        
        # Imprimir la posición del cubo verde para depuración
        print("Green cube position:", green_cube_position)
        
        # Crear el cubo verde con la posición calculada
        green_cube = Cubo(position=green_cube_position, color=color.green, name='cubo verde')
        cubos.append(green_cube)
    
    return used_positions

# Variable para almacenar los cubos
cubos = []

# Valor inicial del jugador antes de crear niveles
player.position = Vec3(0, 3, 0)

# Suelo
ground = Entity(model='plane', scale=64, collider='box', color=color.red)
ground.position = Vec3(0, -20, 0)

# Definir el valor de spacing globalmente para cada nivel
SPACING_EASY = 0.9
SPACING_MEDIUM = 0.9
SPACING_HARD = 0.9

def create_level(num_cubes, num_rows, max_height, spacing):
    used_positions = set()
    
    def generate_unique_position():
        while True:
            x = random.randint(0, num_rows - 1) * spacing
            y = random.randint(1, max_height)  # Asegúrate de que la altura esté sobre el suelo
            z = random.randint(0, num_cubes - 1) * spacing
            position = (x, y, z)
            if position not in used_positions:
                used_positions.add(position)
                return position
    
    # Generar cubos
    for _ in range(num_cubes):
        position = generate_unique_position()
        cubo = Cubo(position=position)
        if random.choice([True, False]):
            cubo.y += 1
        elif random.choice([True, False]):
            cubo.y -= 1
        cubos.append(cubo)
    
    # Colocar el cubo verde al final
    last_position = sorted(list(used_positions), key=lambda pos: (pos[2], pos[0], pos[1]))[-1]
    green_cube_position = (last_position[0], last_position[1], last_position[2] + spacing)
    green_cube = Cubo(position=green_cube_position, color=color.green, name='cubo verde')
    cubos.append(green_cube)
    
    return used_positions

def adjust_player_position(used_positions, spacing):
    # Convertir el conjunto a lista y filtrar posiciones sobre el suelo
    used_positions = sorted([pos for pos in used_positions if pos[1] > -20])
    # Asegurarse de que la posición inicial esté en el primer cubo válido
    if used_positions:  # Verificar que la lista no esté vacía
        first_cube = used_positions[0]
        # Ajustar la posición para que esté centrado dentro del cubo
        player.position = (first_cube[0], first_cube[1] + spacing / 2, first_cube[2])  # Ajustar posición para estar dentro del cubo

def create_easy_level():
    # Generar cubos y obtener sus posiciones
    used_positions = create_level(num_cubes=36, num_rows=4, max_height=1, spacing=SPACING_EASY)
    adjust_player_position(used_positions, SPACING_EASY)

def create_medium_level():
    # Generar cubos y obtener sus posiciones
    used_positions = create_level(num_cubes=56, num_rows=7, max_height=2, spacing=SPACING_MEDIUM)
    adjust_player_position(used_positions, SPACING_MEDIUM)

def create_hard_level():
    # Generar cubos y obtener sus posiciones
    used_positions = create_level(num_cubes=80, num_rows=10, max_height=3, spacing=SPACING_HARD)
    adjust_player_position(used_positions, SPACING_HARD)

# Funcion de texto de ayuda
def configure_controls():
    global gameplay_option
    if gameplay_option == 'clicks':
        update_controls = update_with_clicks
        help_lines = [
            'Usa click derecho para moverte hacia adelante.',
            'Usa click izquierdo para saltar.'
        ]
    elif gameplay_option == 'arrow keys':
        update_controls = update_with_arrow_keys
        help_lines = [
            'Usa las flechas: arriba para avanzar.',
            'Flecha abajo para retroceder.',
            'Flechas izquierda y derecha para moverse de lado a lado.',
            'Usa espacio para saltar.'
        ]
    elif gameplay_option == 'wsad':
        update_controls = update_with_wsad
        help_lines = [
            'Usa las teclas: W para avanzar.',
            'S para retroceder.',
            'A y D para moverse de lado a lado.',
            'Usa espacio para saltar.'
        ]

    return help_lines  # Devuelve las líneas de ayuda para ser usadas más tarde# Deshabilitar los textos de ayuda

# Variable para almacenar el texto de ayuda
help_texts = []

def disable_help_texts():
    for text in help_texts:
        text.disable()

def display_help(lines):
    global help_texts
    
    # Crear un texto de ayuda para cada línea y posicionarlo en una columna
    for i, line in enumerate(lines):
        help_text = Text(
            text=line,
            scale=1,  # Texto más pequeño
            color=color.white,
            origin=(0, 0),
            background=True,
            background_color=color.black,
            parent=camera.ui,
            position=(0, 0.2 - i * 0.1)  # Posicionar en columnas verticales
        )
        help_texts.append(help_text)
    
    invoke(disable_help_texts, delay=5)  # Ocultar el texto de ayuda después de 5 segundos

# Reiniciar posición
def update():
    if player.enabled:
        update1()

    if player.position.y <= -10:
        player.position = Vec3(0, 30, 0)

    # Actualizar controles según la opción seleccionada
    if gameplay_option == 'clicks':
        update_with_clicks()
    elif gameplay_option == 'arrow keys':
        update_with_arrow_keys()
    elif gameplay_option == 'wsad':
        update_with_wsad()

# Variable global para el texto de GAME OVER
game_over_text = Text(text='GAME OVER', scale=3, color=color.red, origin=(0,0), background=True, enabled=False)
game_over_text.background.color = color.black

# Función para mostrar GAME OVER
def show_game_over():
    game_over_text.enable()
    congratulations_text.disable()  # Asegúrate de ocultar el texto de "Logrado"
    player.disable()
    invoke(show_gameplay_options, delay=2)

# Manejar las entradas del teclado
def input(key):
    if key == 'escape':
        if game_over_text.enabled:
            show_gameplay_options()  # Regresa al menú de opciones de control
        elif congratulations_text.enabled:
            credits_text.disable()
            show_gameplay_options(delay=3)  # Regresa al menú de opciones de control después de 3 segundos
        else:
            show_game_over()  # Muestra el mensaje de GAME OVER

# Variable global para el texto de "Logrado"
congratulations_text = Text(text='Logrado', scale=3, color=color.green, origin=(0, 0), background=True, enabled=False)
congratulations_text.background.color = color.black

# Mostrar el texto de "Logrado"
def show_congratulations():
    player.disable()
    congratulations_text.enable()
    invoke(show_credits, delay=3)  # Muestra créditos 3 segundos después de "Logrado"

# Ajusta la llamada a show_congratulations cuando el jugador colisiona con el cubo verde
def update1():
    if player.enabled:
        # Chequear colisiones con los cubos verdes
        for cubo in cubos:
            if cubo.color == color.green and player.intersects(cubo).hit:
                show_congratulations()

# Configurar y mostrar el texto de "Logrado" al colisionar
def on_collision(collision):
    if collision.entity.name == 'cubo verde':  # Asegúrate de que el cubo verde tenga el nombre adecuado
        show_congratulations()

# Deshabilitar el texto de "Logrado"
def disable_congratulations_text():
    congratulations_text.enabled = False

# Configurar colisiones para el jugador
player.on_collision = on_collision

# Variable global para el texto de créditos
credits_text = Text(
    text='Créditos\n\n' 
          '--------------------------------\n\n'
          'Echo por:\n\n'
          'Rolando Siguenza\n'
          'Carlos Segovia\n\n'
          '--------------------------------',
    scale=2,
    color=color.white,
    origin=(0, 0),
    background=True,
    enabled=False
)
credits_text.background.color = color.black

# Centrar el texto en la pantalla
credits_text.x = 0
credits_text.y = 0

# Mostrar los créditos
def show_credits():
    congratulations_text.disable()  # Ocultar texto de "Logrado"
    credits_text.enable()
    # Regresar al menú de jugabilidad después de mostrar los créditos
    invoke(return_to_gameplay_options, delay=3)  # Ocultar créditos y mostrar menú de jugabilidad después de 3 segundos

# Regresar al menú de jugabilidad
def return_to_gameplay_options():
    credits_text.disable()  # Ocultar créditos
    show_gameplay_options()  # Regresar al menú de jugabilidad

# Función para mostrar los créditos y salir del juego
def show_credits_and_exit():
    # Crear una ventana de créditos
    credits_window = Entity(parent=camera.ui, enabled=True)
    
    # Mensaje de créditos
    credits_text = Text(
        text='Créditos\n\n' 
              '--------------------------------\n\n'
              'Echo por:\n\n'
              'Rolando Siguenza\n\n'
              'Carlos Segovia\n\n'
              '--------------------------------',
        parent=credits_window,
        position=(0, 0),
        origin=(0, 0),
        scale=2,
        color=color.white,
        background=True
    )
    credits_text.background.color = color.black
    credits_text.text = credits_text.text.replace('\n', ' \n')  # Opcional: Reemplaza los saltos de línea para centrar mejor

    # Centrar el texto en la pantalla
    credits_text.x = 0
    credits_text.y = 0

    # Ajustar el tamaño de la ventana de créditos si es necesario
    credits_window.scale = (1.2, 1.2)  # Ajusta el tamaño según lo necesario
    credits_window.x = 0
    credits_window.y = 0

    # Salir del juego después de 3 segundos
    invoke(application.quit, delay=3)  # Salir de la aplicación después de 3 segundos

# Función para confirmar la salida
def confirm_exit():
    # Deshabilita los elementos de la interfaz mientras se muestra la alerta
    gameplay_menu.disable()
    
    # Crea una ventana de confirmación
    confirm_window = Entity(parent=camera.ui, enabled=True)
    
    # Mensaje de confirmación
    confirm_text = Text(
        text='¿Estás seguro de que deseas salir?',
        parent=confirm_window,
        position=(0, 0.2),
        origin=(0, 0),
        scale=2,
        color=color.white,
        background=True
    )
    
    # Botón "Sí"
    yes_button = Button(
        text='Sí',
        scale=(0.3, 0.1),
        position=(-0.2, -0.1),
        parent=confirm_window,
        color=color.red
    )
    
    # Botón "No"
    no_button = Button(
        text='No',
        scale=(0.3, 0.1),
        position=(0.2, -0.1),
        parent=confirm_window,
        color=color.green
    )

    # Acción para el botón "Sí"
    def exit_game():
        confirm_window.disable()  # Ocultar la ventana de confirmación
        show_credits_and_exit()  # Mostrar créditos y salir después de 3 segundos

    yes_button.on_click = exit_game

    # Acción para el botón "No"
    def cancel_exit():
        confirm_window.disable()
        gameplay_menu.enable()
        
    no_button.on_click = cancel_exit

# Botón para salir del juego
exit_button = Button(text='Salir del Juego', scale=(0.5, 0.1), position=(0, -0.4), parent=gameplay_menu, color=color.red)
exit_button.on_click = confirm_exit  # Usar confirm_exit

# Fondo de pantalla
Sky()

app.run()
