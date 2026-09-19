# Guía de contribución

Esta guía establece las reglas básicas para colaborar en el desarrollo de Kora.

## Commits

Los commits deben seguir esta estructura:

tipo: descripción breve

Tipos principales:

- `feat`: nueva funcionalidad.
- `fix`: corrección de errores.
- `docs`: documentación.
- `test`: pruebas.
- `refactor`: reorganización o mejora del código.
- `chore`: configuración y mantenimiento.

Ejemplos:

feat: agregar consulta de alimentos
fix: corregir validación de alimentos
docs: actualizar documentación de arquitectura

Los commits deben representar un cambio lógico y tener una descripción clara.

## Ramas

Las ramas deben indicar el propósito del trabajo:

feature/nombre-funcionalidad
fix/nombre-error
docs/nombre-documentacion

Ejemplos:

feature/consulta-alimentos
fix/validacion-alimentos
docs/arquitectura

## Flujo de trabajo

1. Crear una rama a partir de `main`.
2. Realizar los cambios correspondientes.
3. Crear commits siguiendo la convención establecida.
4. Subir la rama al repositorio remoto.
5. Crear un Pull Request hacia `main`.
6. Revisar los cambios antes de integrarlos.

## Pull Requests

Los Pull Requests deben:

- Indicar claramente qué cambios se realizaron.
- Explicar brevemente el propósito de los cambios.
- Relacionarse con la tarea o historia correspondiente cuando aplique.
- Ser revisados antes de integrarse a `main`.