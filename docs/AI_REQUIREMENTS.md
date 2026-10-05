# AI Microservice Requirements — Kora

## 1. Description

The **AI Microservice** is the component responsible for integrating Kora's Artificial Intelligence capabilities.

For **V1**, the microservice will have two main capabilities:

1. **Vision / Machine Learning:** food identification from photographs.
2. **LLM:** generation of responses and recommendations using the user's nutritional context.

### General Architecture

```text
                         KORA
                           │
                           ▼
                  ┌─────────────────┐
                  │ AI Microservice│
                  └────────┬────────┘
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
        ┌───────────────┐     ┌───────────────┐
        │ Vision Model │     │      LLM      │
        │ / Machine     │     │               │
        │ Learning      │     │  External API  │
        └───────┬───────┘     └───────┬───────┘
                │                     │
                ▼                     ▼
        Food identification          Response
        generation             generation
```

---

# 2. AI Microservice Capabilities

## Capability 1 — Vision

The first capability allows the system to identify foods present in a photograph.

### Input

A food image.

### Processing

The vision model analyzes the image and identifies the detected foods.

### Output

For each identified food:

* Food name.
* Prediction confidence level.

### Example

```json
{
    "success": true,
    "detections": [
        {
            "food": "rice",
            "confidence": 0.87
        },
        {
            "food": "egg",
            "confidence": 0.79
        }
    ]
}
```

> **Important:** in V1, the vision model identifies foods and provides a detection confidence score. The confidence score must not be automatically interpreted as the food's quantity, weight, or serving size.

---

# 3. Capability 2 — LLM

The second capability uses a language model through an external API.

Its function will be to process the **user prompt together with controlled nutritional context** to generate personalized responses.

## Information Used as Context

### User Profile

* Age
* Sex
* Weight
* Height
* Physical activity

### Nutritional Goals

* Calories
* Protein
* Carbohydrates
* Fat

### Current Consumption

* Foods consumed
* Available quantities
* Available nutritional values

This information will be processed by Kora before being sent to the LLM.

```text
User
   │
   ▼
Profile information
   +
Nutritional goals
   +
Current consumption
   +
Retrieved information
   │
   ▼
Controlled context
   │
   ▼
LLM
   │
   ▼
Structured response
```

---

# 4. AI Features in Kora

| Feature                                    | AI Type                             | Input                                   | Output                                | Use in Kora                              |
| ------------------------------------------ | ----------------------------------- | --------------------------------------- | ------------------------------------- | ---------------------------------------- |
| Food identification from photograph       | Vision model / Machine Learning      | Photograph of a meal                   | Identified foods + confidence          | Help the user record their consumption  |
| Nutritional recommendations              | LLM through API                    | Profile + goals + consumption + context | Recommendations in structured text   | Generate personalized recommendations   |

---

# 5. LLM Model Selection

For V1, **GPT-OSS 120B**, provided through **Groq**, was selected.

The selection considers the needs of the Kora agent, especially:

* Reasoning.
* Tool use.
* Structured responses.
* RAG integration.
* Rules integration.
* Bayes integration.
* Vision integration.
* Large-context handling.

## Model Comparison

| Feature              | GPT-OSS 120B | GPT-OSS 20B | Qwen 3.8 27B |
| -------------------- | ------------ | ----------- | ------------ |
| Reasoning            | ✅ High      | ✅           | ✅ High       |
| Tool use             | ✅            | ✅           | ✅            |
| Parallel tool use    | ❌           | ❌           | ✅            |
| Structured Outputs   | ✅            | ✅           | ✅            |
| JSON Schema estricto | ✅            | ✅           | ✅            |
| Context           | 131K         | 131K        | 131K         |
| Vision               | ❌           | ❌           | ✅            |
| Speed on Groq        | ~500 t/s     | High        | ~450+ t/s    |
| Suitable for agent   | ✅           | ✅           | ✅            |
| Kora complexity      | Very suitable | Suitable | Very suitable |

### Selected Model

```text
Provider:
Groq

Model:
openai/gpt-oss-120b

API:
Groq API compatible con OpenAI API

Environment variable:
GROQ_API_KEY
```

---

# 6. LLM Configuration

## Usage

The model will be used for:

* Agent response generation.
* Reasoning over the provided context.
* Nutritional recommendation generation.
* Interpretation of information retrieved through RAG.
* Coordination of available tools.
* Integration with Rules, Bayes, and Vision.

The LLM will operate as part of the agent and not as a substitute for specialized tools.

## Input

The input will consist of:

```text
User prompt
+
Nutritional context
+
Relevant history
+
Results from available tools
```

For example:

```json
{
    "prompt": "¿Qué puedo comer para completar mis proteínas hoy?",
    "user_id": "123"
}
```

The microservice will be responsible for obtaining and preparing the corresponding context before querying the model.

## Output

The model will generate a structured response using JSON Schema.


```json
{
    "success": true,
    "response": "Puedes complementar tu consumo de proteínas con..."
}
```

---

# 7. LLM Limitations

The LLM should not be considered Kora's only source of nutritional truth.

Recommendations should be supported, when appropriate, by:

* Retrieved information mediante RAG.
* Nutritional rules defined by the system.
* Calculations performed by specialized tools.
* Information provided by the user.
* Results from Machine Learning models.

The model must not invent information that is not available in the context.

Additionally, use of the model through Groq is subject to the limits established by the provider.

The API Key **must not be included directly in the source code**.

It must be stored using an environment variable:

```env
GROQ_API_KEY=tu_api_key
```

The `.env` file must be kept out of version control.

---

# 8. Vision / Machine Learning Model

Kora will use a previously developed vision model for food identification.

As part of the evaluation of the vision component, different models were considered:

### Model 1 — Segmentation

```text
arunapb/yolo11l-food-segmentation
```

Its function is to detect regions corresponding to foods within an image.

### Model 2 — Classification

```text
nateraw/food
```

Its function is to perform food-related classification.

### Model 3 — Visual Comparison

```text
openai/clip-vit-base-patch32
```

It can be used to compare visual representations of an image against different concepts or ingredients.

---

# 9. Vision Component Flow

The expected flow is:

```text
Photograph
    │
    ▼
Modelo de visión
    │
    ▼
Detection / classification
    │
    ▼
Identified foods
    +
Confidence
    │
    ▼
AI Microservice response
```

### Example

Input:

```text
Photograph de un plato con rice y egg
```

Output:

```json
{
    "success": true,
    "detections": [
        {
            "food": "rice",
            "confidence": 0.87
        },
        {
            "food": "egg",
            "confidence": 0.79
        }
    ]
}
```

---

# 10. Vision Component API

## Input

The image will be received through:

```text
multipart/form-data
```

Field:

```text
image
```

Conceptual example:

```text
POST /vision/analyze

Content-Type: multipart/form-data

image: fotografia.jpg
```

## Output

```json
{
    "success": true,
    "detections": [
        {
            "food": "rice",
            "confidence": 0.87
        }
    ]
}
```

---

# 11. LLM Component API

## Input

The endpoint will receive the minimum information needed to identify the request and generate the corresponding context.

Ejemplo:

```json
{
    "prompt": "¿Qué puedo comer para completar mis proteínas hoy?",
    "user_id": "123"
}
```

The `user_id` will allow the microservice to obtain the user's required information through the corresponding components.

## Output

```json
{
    "success": true,
    "response": "Puedes complementar tu consumo de proteínas con..."
}
```

---

# 12. Relationship with Kora's Architecture

The LLM will not operate in isolation.

Within `svc-agente`, the model will be able to interact with the different tools defined for Kora.

```text
                         svc-ai
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
                        Kora's Response
```

### RAG

It will provide relevant information from Kora's knowledge base.

### Rules

It will allow the system to apply defined rules and restrictions.

### Bayes

It will allow the system to work with probabilities when required by the use case.

### Vision

It will allow food images to be processed and identifications to be returned with their confidence levels.

### LLM

It will be responsible for interpreting the context, reasoning over the available information, and generating the structured response for the user.

---

# 13. Complete Flow

The general flow of a request can be represented as follows:

```text
                    USER
                       │
                       ▼
                 Kora request
                       │
                       ▼
                ┌──────────────┐
                │ svc-ai       │
                └──────┬───────┘
                       │
                       ▼
                  Planning
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
                 Final context
                       │
                       ▼
                      LLM
                       │
                       ▼
              Structured response
                       │
                       ▼
                    KORA
                       │
                       ▼
                    USER
```

---

# 14. AI Microservice Responsibilities

For V1, the microservice will be responsible for:

* Receiving AI-related requests.
* Processing food images.
* Identifying foods using Machine Learning.
* Returning confidence levels.
* Communicating with the LLM provider.
* Preparing and sending the necessary context to the LLM.
* Processing model responses.
* Maintaining structured responses.
* Integrating the AI tools defined by Kora.
* Handling errors related to calls to external models.

---

# 15. Environment Variables

Sensitive credentials and configurations must be maintained using environment variables.

Ejemplo:

```env
GROQ_API_KEY=tu_api_key
```

The following must not be done:

```python
api_key = "gsk_xxxxxxxxxxxxxxxxx"
```

The key must also not be included in:

* Source code.
* Commits.
* Pull Requests.
* Public documentation.
* `README.md`.

---

# 16. V1 Summary

| Component     | Technology / Model                              | Function                                |
| ------------- | ----------------------------------------------- | --------------------------------------- |
| Vision        | Machine Learning model                         | Identify foods                          |
| Vision        | Model previously developed in Google Colab    | Photograph processing                   |
| LLM           | `openai/gpt-oss-120b`                          | Reasoning and response generation       |
| LLM Provider  | Groq                                            | API access                              |
| RAG           | Knowledge base                                  | Retrieve relevant information           |
| Rules         | Rule engine                                     | Apply restrictions and rules            |
| Bayes         | Probabilistic tool                              | Work with probabilities                 |
| Agent         | LangChain + LangGraph                           | Orchestrate the AI flow                 |

---

# 17. V1 Decision

The following will be used for the first version of Kora:

```text
VISION
    │
    └── Machine Learning Model
            │
            └── Food Identification
                    +
                    Confidence


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

The goal is to maintain a clear separation between the responsibilities of each component:

* **Vision/ML:** identifies foods.
* **RAG:** provides knowledge.
* **Rules:** applies rules.
* **Bayes:** handles probabilities.
* **LLM:** interprets, reasons, and generates the response.
* **svc-agente:** coordinates the complete flow.
* **Kora:** presents the result to the user.

This separation allows each component to be evaluated and modified independently without making the LLM directly responsible for all system functions.
