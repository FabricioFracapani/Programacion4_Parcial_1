# Guion de la Exposición del Parcial: Desarrollo del Backend

**Tema del Proyecto:** Catálogo de Productos (FastAPI)
**Integrantes:** 4 Locutores
**Tiempo estimado:** 5 a 10 minutos en total

---

## Locutor 1: Introducción y Configuración General

"Hola a todos, somos el grupo de desarrollo y hoy vamos a presentar la parte de backend correspondiente al parcial de Programación 4. Nuestro proyecto consiste en un sistema de Catálogo de Productos.

Para desarrollar este proyecto decidimos utilizar **FastAPI**, un framework moderno y asíncrono de Python que nos permite construir APIs RESTful de manera muy rápida y con alto rendimiento estructural. 

La aplicación está diseñada para gestionar tres entidades principales de negocio: Categorías, Ingredientes y Productos.

Si nos enfocamos en el punto de entrada de nuestro proyecto, el archivo `main.py`, es allí donde inicializamos la aplicación de FastAPI y configuramos aspectos globales de seguridad e integración, como las políticas de CORS. Esto último es vital para permitirle al frontend hacer peticiones sin ser bloqueado.
Además, en este mismo archivo vinculamos nuestros *routers* o rutas, y preparamos nuestra base de datos para que cada módulo se cargue correctamente cuando inicializa el servidor. 

Todo este setup inicial está planificado de manera modular para que el sistema sea fácil de mantener y escalar. Ahora le paso la palabra a nuestro segundo locutor para que ahonde en la arquitectura base."

---

## Locutor 2: Arquitectura Limpia y Capa Core (Base de Datos)

"Hola a todos. Así como mencionó mi compañero, implementamos una arquitectura fuertemente separada en capas. En nuestro código tenemos una carpeta especial llamada `core`, donde se concentra el corazón del acceso a los datos de la aplicación.

A nivel de base de datos implementamos dos patrones de diseño sumamente importantes: el **Patrón Repositorio (Repository Pattern)** y el **Unit of Work (Unidad de Trabajo)**.

El patrón **Repositorio** actúa como un mediador entre nuestra lógica de negocio y la base de datos. En vez de esparcir consultas SQL complejas por todo el código, usamos clases que encapsulan los métodos comunes como crear, buscar, listar o borrar registros.

Por otra parte, la **Unidad de Trabajo** es la herramienta que nos permite garantizar el éxito sistémico de nuestras transacciones. Si un proceso de negocio requiere realizar varios cambios agrupados en la base de datos (por ejemplo, guardar el producto y luego mapear sus ingredientes), el Unit of Work asegura de que todo sea exitoso mediante un 'commit', o si cualquier pequeño paso falla, se revierte todo con un 'rollback'. Esto es fundamental en sistemas profesionales para nunca dejar bases de datos corruptas u operaciones a medias."

---

## Locutor 3: Módulos, Dominio y Validación (Modelos vs Schemas)

"Pasando ya a la parte lógica central del dominio, en la carpeta `modules` separamos nuestra entidades base en: `categoria`, `ingrediente` y `producto`. Utilizar estos directorios nos permite organizar funcionalidades por su relevancia y significado en el negocio (Dominio Dirigido).

Dentro de cada uno de esos módulos tenemos una división muy clara entre la validación de peticiones y el guardado local, que es representado por la separación de `models.py` y `schemas.py`.

Por un lado usamos los **Modelos**. Estas son clases implementadas con SQLAlchemy, y su principal trabajo es delinear cómo se van a crear y relacionar las tablas en nuestra base de datos.

Por el otro lado, introdujimos la tecnología Pydantic a través de los **Schemas** (Esquemas). Mientras que el Modelo habla con la base de datos, el Schema se encarga de proteger la entrada y salida de nuestra API. Validamos estrictamente los datos: qué se requiere, el tipo de dato y, si se espera un precio, no dejar que se ingrese un texto. Esta capa de contención captura todas las equivocaciones generadas por el cliente, entregando un mensaje de error exacto sin sobrecargar la Base de Datos con solicitudes fallidas."

---

## Locutor 4: Lógica de Negocio y Ciclo de Petición (Routers, Services y Responses)

"Por último, me gustaría detallar cómo interactúan todas estas piezas que estuvimos nombrando a la hora de procesar una solicitud del usuario.

El flujo inicia cuando una solicitud llega a nuestra API a través de los **Routers** (los archivos `router.py` en cada módulo). Los routers hacen una única labor: ser la puerta de entrada. No contienen lógica ni cálculos pesados. 

La solicitud es automáticamente redirigida hacia nuestros archivos `service.py`, donde verdaderamente reside toda la **Lógica de Negocio**. Aquí, el *Servicio* implementa todas las reglas, validaciones avanzadas, y comanda al Patrón Unit of Work explicado por Locutor 2, para ejecutar un guardado en la base si la operación procede exitosamente.

Además, nos aseguramos de que toda la comunicación con el frontend o usuario de la API sea estandarizada utilizando el archivo global `responses.py`. De este modo, si la operación es un éxito, o si ocurre un fallo (ejemplo producto no encontrado), el servidor devolverá siempre la información bajo un cuerpo predecible (status, mensaje y data).

Finalmente, esta arquitectura en capaz combinada con la documentación auto-generada por Swagger proporciona un ecosistema robusto, donde el desarrollo a futuro resulta intuitivo y altamente fiable. Con esto damos por finalizada nuestra presentación del back-end. ¿Alguien tiene alguna pregunta? ¡Muchas gracias!"
