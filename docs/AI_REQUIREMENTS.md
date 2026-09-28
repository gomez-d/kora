# Necesidades del Microservicio de IA — Kora

## 1. Descripción

El **Microservicio de IA** es el componente encargado de integrar las capacidades de Inteligencia Artificial de Kora.

Para la **V1**, el microservicio contará con dos capacidades principales:

1. **Visión / Machine Learning:** identificación de alimentos a partir de fotografías.
2. **LLM:** generación de respuestas y recomendaciones utilizando el contexto nutricional del usuario.

### Arquitectura general

```text
                         KORA
                           │
                           ▼
                  ┌─────────────────┐
                  │ Microservicio IA│
                  └────────┬────────┘
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
        ┌───────────────┐     ┌───────────────┐
        │ Modelo Vision │     │      LLM      │
        │ / Machine     │     │               │
        │ Learning      │     │  API externa  │
        └───────┬───────┘     └───────┬───────┘
                │                     │
                ▼                     ▼
        Identificación          Generación de
        de alimentos            respuestas
```

---

# 2. Capacidades del Microservicio IA

## Capacidad 1 — Visión

La primera capacidad permite identificar alimentos presentes en una fotografía.

### Entrada

Una imagen de comida.

### Procesamiento

El modelo de visión analiza la imagen e identifica los alimentos detectados.

### Salida

Para cada alimento identificado:

* Nombre del alimento.
* Nivel de confianza de la predicción.

### Ejemplo

```json
{
    "success": true,
    "detections": [
        {
            "food": "arroz",
            "confidence": 0.87
        },
        {
            "food": "huevo",
            "confidence": 0.79
        }
    ]
}
```

> **Importante:** en la V1, el modelo de visión identifica alimentos y proporciona una confianza de detección. No se debe interpretar automáticamente la confianza como cantidad, peso o porción del alimento.

---

# 3. Capacidad 2 — LLM

La segunda capacidad utiliza un modelo de lenguaje mediante una API externa.

Su función será procesar el **prompt del usuario junto con un contexto nutricional controlado** para generar respuestas personalizadas.

## Información utilizada como contexto

### Perfil del usuario

* Edad
* Sexo
* Peso
* Altura
* Actividad física

### Objetivos nutricionales

* Calorías
* Proteínas
* Carbohidratos
* Grasas

### Consumo actual

* Alimentos consumidos
* Cantidades disponibles
* Valores nutricionales disponibles

Esta información será procesada por Kora antes de enviarse al LLM.

```text
Usuario
   │
   ▼
Información del perfil
   +
Objetivos nutricionales
   +
Consumo actual
   +
Información recuperada
   │
   ▼
Contexto controlado
   │
   ▼
LLM
   │
   ▼
Respuesta estructurada
```

---

# 4. Funcionalidades de IA en Kora

| Funcionalidad                              | Tipo de IA                          | Entrada                                 | Salida                                | Uso en Kora                              |
| ------------------------------------------ | ----------------------------------- | --------------------------------------- | ------------------------------------- | ---------------------------------------- |
| Identificación de alimentos por fotografía | Modelo de visión / Machine Learning | Fotografía de una comida                | Alimentos identificados + confianza   | Ayudar al usuario a registrar su consumo |
| Recomendaciones nutricionales              | LLM mediante API                    | Perfil + objetivos + consumo + contexto | Recomendaciones en texto estructurado | Generar recomendaciones personalizadas   |

---

# 5. Selección del modelo LLM

Para la V1 se seleccionó **GPT-OSS 120B**, proporcionado mediante **Groq**.

La selección considera las necesidades del agente de Kora, especialmente:

* Razonamiento.
* Uso de herramientas.
* Respuestas estructuradas.
* Integración con RAG.
* Integración con Rules.
* Integración con Bayes.
* Integración con Vision.
* Manejo de contexto amplio.

## Comparación de modelos

| Característica       | GPT-OSS 120B | GPT-OSS 20B | Qwen 3.8 27B |
| -------------------- | ------------ | ----------- | ------------ |
| Razonamiento         | ✅ Alto       | ✅           | ✅ Alto       |
| Tool use             | ✅            | ✅           | ✅            |
| Tool use paralelo    | ❌            | ❌           | ✅            |
| Structured Outputs   | ✅            | ✅           | ✅            |
| JSON Schema estricto | ✅            | ✅           | ✅            |
| Contexto             | 131K         | 131K        | 131K         |
| Visión               | ❌            | ❌           | ✅            |
| Velocidad en Groq    | ~500 t/s     | Alta        | ~450+ t/s    |
| Adecuado para agente | ✅            | ✅           | ✅            |
| Complejidad de Kora  | Muy adecuada | Adecuada    | Muy adecuada |

### Modelo seleccionado

```text
Proveedor:
Groq

Modelo:
openai/gpt-oss-120b

API:
Groq API compatible con OpenAI API

Variable de entorno:
GROQ_API_KEY
```

---

# 6. Configuración del LLM

## Uso

El modelo será utilizado para:

* Generación de respuestas del agente.
* Razonamiento sobre el contexto proporcionado.
* Generación de recomendaciones nutricionales.
* Interpretación de información recuperada mediante RAG.
* Coordinación de herramientas disponibles.
* Integración con Rules, Bayes y Vision.

El LLM funcionará como parte del agente y no como sustituto de las herramientas especializadas.

## Entrada

La entrada estará compuesta por:

```text
Prompt del usuario
+
Contexto nutricional
+
Historial relevante
+
Resultados de herramientas disponibles
```

Por ejemplo:

```json
{
    "prompt": "¿Qué puedo comer para completar mis proteínas hoy?",
    "user_id": "123"
}
```

El microservicio será responsable de obtener y preparar el contexto correspondiente antes de realizar la consulta al modelo.

## Salida

El modelo generará una respuesta estructurada mediante JSON Schema.

Ejemplo simplificado:

```json
{
    "success": true,
    "response": "Puedes complementar tu consumo de proteínas con..."
}
```

---

# 7. Limitaciones del LLM

El LLM no debe considerarse como la única fuente de verdad nutricional de Kora.

Las recomendaciones deberán apoyarse, cuando corresponda, en:

* Información recuperada mediante RAG.
* Reglas nutricionales definidas por el sistema.
* Cálculos realizados mediante herramientas especializadas.
* Información proporcionada por el usuario.
* Resultados de los modelos de Machine Learning.

El modelo tampoco deberá inventar información que no esté disponible en el contexto.

Además, el uso del modelo mediante Groq está sujeto a los límites establecidos por el proveedor.

La API Key **no debe incluirse directamente en el código fuente**.

Debe almacenarse mediante una variable de entorno:

```env
GROQ_API_KEY=tu_api_key
```

El archivo `.env` deberá mantenerse fuera del control de versiones.

---

# 8. Modelo de Visión / Machine Learning

Kora utilizará un modelo de visión previamente desarrollado para la identificación de alimentos.

Como parte de la evaluación del componente de visión se consideraron diferentes modelos:

### Modelo 1 — Segmentación

```text
arunapb/yolo11l-food-segmentation
```

Su función es detectar regiones correspondientes a alimentos dentro de una imagen.

### Modelo 2 — Clasificación

```text
nateraw/food
```

Su función es realizar clasificación relacionada con alimentos.

### Modelo 3 — Comparación visual

```text
openai/clip-vit-base-patch32
```

Puede utilizarse para comparar representaciones visuales de una imagen contra diferentes conceptos o ingredientes.

---

# 9. Flujo del componente de visión

El flujo esperado es:

```text
Fotografía
    │
    ▼
Modelo de visión
    │
    ▼
Detección / clasificación
    │
    ▼
Alimentos identificados
    +
Confianza
    │
    ▼
Respuesta del Microservicio IA
```

### Ejemplo

Entrada:

```text
Fotografía de un plato con arroz y huevo
```

Salida:

```json
{
    "success": true,
    "detections": [
        {
            "food": "arroz",
            "confidence": 0.87
        },
        {
            "food": "huevo",
            "confidence": 0.79
        }
    ]
}
```

---

# 10. API del componente de Visión

## Entrada

La imagen será recibida mediante:

```text
multipart/form-data
```

Campo:

```text
image
```

Ejemplo conceptual:

```text
POST /vision/analyze

Content-Type: multipart/form-data

image: fotografia.jpg
```

## Salida

```json
{
    "success": true,
    "detections": [
        {
            "food": "arroz",
            "confidence": 0.87
        }
    ]
}
```

---

# 11. API del componente LLM

## Entrada

El endpoint recibirá información mínima para identificar la solicitud y generar el contexto correspondiente.

Ejemplo:

```json
{
    "prompt": "¿Qué puedo comer para completar mis proteínas hoy?",
    "user_id": "123"
}
```

El `user_id` permitirá al microservicio obtener la información necesaria del usuario mediante los componentes correspondientes.

## Salida

```json
{
    "success": true,
    "response": "Puedes complementar tu consumo de proteínas con..."
}
```

---

# 12. Relación con la arquitectura de Kora

El LLM no trabajará de forma aislada.

Dentro de `svc-agente`, el modelo podrá interactuar con las diferentes herramientas definidas para Kora.

```text
                         svc-agente
                             │
                             ▼
                      ┌─────────────┐
                      │     LLM     │
                      └──────┬──────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
             RAG           Rules          Bayes
              │              │              │
              └──────────────┼──────────────┘
                             │
                             ▼
                           Vision
                             │
                             ▼
                       Respuesta Kora
```

### RAG

Proporcionará información relevante desde la base de conocimiento de Kora.

### Rules

Permitirá aplicar reglas y restricciones definidas por el sistema.

### Bayes

Permitirá trabajar con probabilidades cuando el caso de uso lo requiera.

### Vision

Permitirá procesar imágenes de alimentos y devolver identificaciones con su nivel de confianza.

### LLM

Será responsable de interpretar el contexto, razonar sobre la información disponible y generar la respuesta estructurada para el usuario.

---

# 13. Flujo completo

El flujo general de una solicitud puede representarse de la siguiente manera:

```text
                    USUARIO
                       │
                       ▼
                 Solicitud Kora
                       │
                       ▼
                ┌──────────────┐
                │ svc-agente   │
                └──────┬───────┘
                       │
                       ▼
                  Planificación
                       │
                       ▼
                      LLM
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
         RAG         Rules         Bayes
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
                    Vision
                       │
                       ▼
                 Contexto final
                       │
                       ▼
                      LLM
                       │
                       ▼
              Respuesta estructurada
                       │
                       ▼
                    KORA
                       │
                       ▼
                    USUARIO
```

---

# 14. Responsabilidades del Microservicio IA

Para la V1, el microservicio será responsable de:

* Recibir solicitudes relacionadas con IA.
* Procesar imágenes de alimentos.
* Identificar alimentos mediante Machine Learning.
* Devolver niveles de confianza.
* Comunicarse con el proveedor del LLM.
* Preparar y enviar el contexto necesario al LLM.
* Procesar respuestas del modelo.
* Mantener respuestas estructuradas.
* Integrar las herramientas de IA definidas por Kora.
* Manejar errores relacionados con las llamadas a modelos externos.

---

# 15. Variables de entorno

Las credenciales y configuraciones sensibles deberán mantenerse mediante variables de entorno.

Ejemplo:

```env
GROQ_API_KEY=tu_api_key
```

No se deberá realizar:

```python
api_key = "gsk_xxxxxxxxxxxxxxxxx"
```

La clave tampoco deberá incluirse en:

* Código fuente.
* Commits.
* Pull Requests.
* Documentación pública.
* `README.md`.

---

# 16. Resumen de la V1

| Componente    | Tecnología / Modelo                             | Función                                 |
| ------------- | ----------------------------------------------- | --------------------------------------- |
| Visión        | Modelo de Machine Learning                      | Identificar alimentos                   |
| Visión        | Modelo previamente desarrollado en Google Colab | Procesamiento de fotografías            |
| LLM           | `openai/gpt-oss-120b`                           | Razonamiento y generación de respuestas |
| Proveedor LLM | Groq                                            | Acceso mediante API                     |
| RAG           | Base de conocimiento                            | Recuperar información relevante         |
| Rules         | Motor de reglas                                 | Aplicar restricciones y reglas          |
| Bayes         | Herramienta probabilística                      | Trabajar con probabilidades             |
| Agente        | LangChain + LangGraph                           | Orquestar el flujo de IA                |

---

# 17. Decisión para la V1

Para la primera versión de Kora se utilizará:

```text
VISIÓN
    │
    └── Modelo de Machine Learning
            │
            └── Identificación de alimentos
                    +
                    Confianza


LLM
    │
    └── Groq
            │
            └── openai/gpt-oss-120b
                    │
                    ├── RAG
                    ├── Rules
                    ├── Bayes
                    └── Vision
```

El objetivo es mantener una separación clara entre las responsabilidades de cada componente:

* **Vision/ML:** identifica alimentos.
* **RAG:** proporciona conocimiento.
* **Rules:** aplica reglas.
* **Bayes:** maneja probabilidades.
* **LLM:** interpreta, razona y genera la respuesta.
* **svc-agente:** coordina el flujo completo.
* **Kora:** presenta el resultado al usuario.

Esta separación permite que cada componente pueda evaluarse y modificarse de manera independiente sin convertir al LLM en el responsable directo de todas las funciones del sistema.
