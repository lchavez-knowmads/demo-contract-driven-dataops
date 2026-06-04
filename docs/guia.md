# Guía para el Docente: Spec-Driven DataOps con Git e IA

## Datos de la Clase

* Tiempo total: 120 minutos
* Módulo: Fundamentos
* Stack: Git, GitHub Actions, Python, YAML, Data Contracts, Trunk-Based Development, CI/CD, JSON

## Objetivos

* Diseñar e implementar contratos de datos automatizados con YAML
* Liderar la transición de Git Flow a Trunk-Based Development
* Orquestar agentes de IA como desarrolladores de datos junior
* Implementar arquitecturas de datos descentralizadas y escalables
* Desplegar infraestructura y modelos de ML con enfoque declarativo

## Preparación

* Clonar el repositorio: `git clone https://github.com/TU_USUARIO/spec-driven-dataops.git`
* Archivos a revisar:
	+ `repo/.github/workflows/dataops-governance.yml`
	+ `repo/README.md`
	+ `repo/contracts/customer_v1.yaml`
	+ `repo/data/landing_raw.json`
	+ `repo/data/landing_processed.json`
	+ `repo/src/validator.py`
	+ `repo/src/pipeline_ai_broken.py`
	+ `repo/src/pipeline_ai_governed.py`
* Dependencias: `pip install pyyaml`

## Escenario de Negocio

El caso de uso se centra en la migración segura del pipeline de clientes de una fintech. El objetivo es implementar un sistema Spec-Driven DataOps que defina contratos de datos como única fuente de verdad, automatice validaciones en CI/CD, use Trunk-Based Development para eliminar merge hell, integre IA generativa controlada por especificaciones y despliegue infraestructura declarativa gobernada por Git.

## Guión de Clase

### Sección 1: Introducción a Spec-Driven DataOps (15 minutos)

* **Archivo:** `repo/.github/workflows/dataops-governance.yml`
* **Código:**
```yaml
name: Spec-Driven DataOps Governance
on:
  pull_request:
    branches:
      - main
```
* **Qué hace:** Configura un flujo de trabajo en GitHub Actions que utiliza Trunk-Based Development para validar cambios de código.
* **Ejecutar:** `git clone https://github.com/TU_USUARIO/spec-driven-dataops.git`
* **Resultado:** Se crea un repositorio con un flujo de trabajo configurado.
* **Error:** Si no se configura correctamente el flujo de trabajo, no se ejecutará en los PRs.

### Sección 2: Escribir el Contrato de Datos (20 minutos)

* **Archivo:** `repo/contracts/customer_v1.yaml`
* **Código:**
```yaml
dataset_name: customer_gold
version: 1.0.0
description: "Contrato de datos para validar ingresos de clientes antes del Lakehouse"
fields:
  customer_id:
    type: string
    required: true
    pattern: "^usr-[0-9]+$"
  signup_timestamp:
    type: string
    required: true
  subscription_plan:
    type: string
    required: true
    allowed_values: ['free', 'premium', 'enterprise']
  mrr_value:
    type: float
    required: true
    min_value: 0.0
```
* **Qué hace:** Define la especificación y reglas inquebrantables de negocio del dataset de clientes.
* **Ejecutar:** Ejecutar el pipeline gobernado para producir el archivo procesado y validarlo:
  ```bash
  python src/pipeline_ai_governed.py
  python src/validator.py data/landing_processed.json
  ```
* **Resultado:** La consola muestra que `data/landing_processed.json cumple 100% con la especificación`.
* **Error:** Si se ejecuta el pipeline roto (`pipeline_ai_broken.py`) y se valida su salida, se detectarán violaciones de contrato en campos como `subscription_plan` (valor no permitido 'basic') y `mrr_value` (valor menor al mínimo permitido).

### Sección 3: Uso de IA para Generar Código Gobernable (20 minutos)

* **Archivo:** `repo/src/pipeline_ai_governed.py` y `repo/src/pipeline_ai_broken.py`
* **Qué hace:** Muestra la diferencia entre programar con y sin contexto del contrato. El pipeline no gobernado comete errores silenciosos de datos que violan el contrato. El pipeline gobernado valida y ajusta defensivamente las entradas (ej. mapeando planes inválidos a 'free' y MRR negativo a 0.0) para asegurar la conformidad.
* **Ejecutar:** Simular el comportamiento de la IA copiando y ejecutando la versión sin control frente a la versión controlada:
  ```bash
  # Escenario 1: IA sin control
  cp src/pipeline_ai_broken.py src/pipeline.py
  python src/pipeline.py
  python src/validator.py data/landing_processed.json   # Retornará código de error 1

  # Escenario 2: IA gobernada
  cp src/pipeline_ai_governed.py src/pipeline.py
  python src/pipeline.py
  python src/validator.py data/landing_processed.json   # Retornará código de éxito 0
  ```
* **Resultado:** Se demuestra que la validación falla en el Escenario 1 (impidiendo la entrada de basura al Lakehouse) y pasa en el Escenario 2.

### Sección 4: Implementación de Trunk-Based Development y CI/CD (20 minutos)

* **Archivo:** `repo/.github/workflows/dataops-governance.yml`
* **Código:**
```yaml
name: Spec-Driven DataOps Governance
on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]
jobs:
  dataops-audit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout de código
        uses: actions/checkout@v4
      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Instalar dependencias
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml
      - name: Ejecutar pipeline (si existe)
        run: |
          if [ -f src/pipeline.py ]; then
            python src/pipeline.py
          else
            python src/pipeline_ai_governed.py
          fi
      - name: Validar salida contra el contrato
        run: python src/validator.py data/landing_processed.json
```
* **Qué hace:** Ejecuta de manera automática y obligatoria la validación en cada Pull Request a `main`.
* **Ejecutar:** Subir cambios en una short-lived branch con el pipeline roto (`src/pipeline.py` copiado de `pipeline_ai_broken.py`) y abrir un Pull Request hacia `main`.
* **Resultado:** GitHub Actions ejecuta el workflow, detecta el error en el validador y bloquea el botón de Merge para salvaguardar la producción.