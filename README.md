# Radar de Fraude en Tiempo Real — README (Simulación)

> ⚠️ **IMPORTANTE:**  
> Este proyecto es un **simulacro educativo** de un sistema de detección de fraude en tiempo real.  
> **No** procesa datos reales, **no** se conecta a sistemas externos y **no** lee información de tu computadora.  
> Su propósito es demostrar cómo funcionaría un pipeline completo de análisis de fraude en un entorno controlado.

---

## 🧩 1. Resumen del proyecto
**Radar de Fraude en Tiempo Real** es una aplicación desarrollada con **FastAPI**, **Python** y **WebSocket**, que simula el flujo continuo de transacciones de un sistema de e-commerce.

Cada transacción generada se evalúa mediante un modelo de **machine learning (Isolation Forest)** o reglas heurísticas simples, asignando un nivel de riesgo (`LOW`, `MEDIUM`, `HIGH`).  
Los resultados se almacenan localmente y se muestran en un **dashboard interactivo en tiempo real** con métricas, alertas y explicaciones automáticas.

---

## 🎭 2. ¿Qué es un simulacro?
Este proyecto **no usa datos reales**.  
Todo lo que ves en el dashboard proviene de un **motor de simulación** que genera datos falsos con valores aleatorios, imitando el comportamiento de usuarios reales.

- ✅ Genera usuarios, países, montos, métodos de pago y dispositivos aleatorios.  
- ✅ Evalúa cada transacción con un modelo entrenado sintéticamente.  
- ✅ Guarda resultados en una base local (`SQLite`) dentro de la carpeta `data/`.  
- 🚫 No accede a información personal ni de tu sistema operativo.  
- 🚫 No envía información fuera de tu computadora.

Es una herramienta 100% local y segura.

---

## ⚙️ 3. Componentes principales y responsabilidades
| Componente | Descripción |
|-------------|-------------|
| **`app/utils/generator.py`** | Motor que genera transacciones simuladas aleatorias. |
| **`app/utils/scoring.py`** | Calcula el riesgo y explica por qué una transacción se considera sospechosa. |
| **`app/ml/train_model.py`** | Entrena el modelo de Machine Learning con datos sintéticos. |
| **`app/db/database.py`** | Maneja la conexión con la base de datos SQLite. |
| **`app/db/models.py`** | Define las tablas `Transaction` y `Alert`. |
| **`app/main.py`** | Núcleo de la aplicación: FastAPI, WebSocket, simulación y endpoints. |
| **`app/templates/index.html`** | Interfaz web del dashboard. |
| **`app/static/css/style.css`** | Estilo visual del dashboard (tema oscuro, moderno). |
| **`app/static/js/app.js`** | Lógica del frontend (streaming en vivo, botones, explicaciones). |
| **`data/fraud.db`** | Base local con las transacciones simuladas. |

---

## 🔁 4. Flujo de datos
1. El **generador** crea una transacción falsa cada segundo.  
2. El **modelo o heurística** evalúa su riesgo (0.0 a 1.0).  
3. Se guarda en la base de datos local (`fraud.db`).  
4. Si el riesgo es medio o alto, se crea una alerta.  
5. El **WebSocket** transmite la nueva transacción al navegador.  
6. El **dashboard** la muestra en tiempo real y actualiza las métricas.

---

## 🧠 5. Criterios usados para marcar fraude
El sistema analiza cada transacción con las siguientes condiciones simuladas:

| Criterio | Descripción | Efecto |
|-----------|-------------|--------|
| `ip_risk > 0.7` | Dirección IP con puntaje de riesgo alto | Aumenta el riesgo |
| `is_new_device = True` | Usuario usando un dispositivo nuevo | Aumenta el riesgo |
| `account_age_days < 30` | Cuenta muy reciente | Aumenta el riesgo |
| `amount > 500` | Monto fuera del patrón habitual | Aumenta el riesgo |
| `country + payment_method` | Combinaciones históricamente más riesgosas (ej. BR + pix) | Riesgo alto |

Cada transacción recibe un puntaje total (`risk`) entre **0.0** y **1.0**, y se clasifica:
- **LOW (verde):** transacción normal  
- **MEDIUM (amarillo):** sospechosa  
- **HIGH (rojo):** posible fraude

---

## 🖥️ 6. Ejecución local
### Paso 1 — Crear entorno virtual
```bash
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt


## 🔐 7. Seguridad y privacidad
- Este sistema **no transmite ni recibe información externa**.  
- Todos los datos están **dentro de tu máquina**.  
- La base de datos (`fraud.db`) solo almacena simulaciones locales.  
- Si se integra con datos reales en el futuro, se recomienda:
  - Implementar **HTTPS / WSS** para cifrar la comunicación.  
  - Anonimizar o tokenizar datos personales antes de procesarlos.  
  - Añadir autenticación (JWT / OAuth2) para proteger el acceso al dashboard.  
  - Cumplir las normativas de privacidad y protección de datos (GDPR, LGPD, etc.).  
  - Implementar registro de accesos y logs de seguridad para trazabilidad.  

---

## 🔗 8. Puntos de integración (para versiones reales)
Para transformar este simulador en un sistema conectado a datos reales, pueden realizarse las siguientes mejoras:

| Nivel | Qué hacer | Archivo a modificar |
|-------|------------|--------------------|
| **Ingesta de eventos** | Reemplazar `TransactionGenerator` por un conector a Kafka, RabbitMQ o API REST que reciba transacciones reales. | `app/utils/generator.py` |
| **Scoring real** | Integrar un modelo de machine learning entrenado con datos históricos reales o usar un servicio externo de inferencia. | `app/utils/scoring.py` |
| **Persistencia** | Cambiar SQLite por una base de datos robusta (Postgres, MySQL, MongoDB o BigQuery). | `app/db/database.py` |
| **Dashboard avanzado** | Agregar gráficas interactivas (Chart.js, Plotly) y filtros adicionales en el frontend. | `app/templates/index.html`, `app/static/js/app.js` |
| **Seguridad** | Implementar login, permisos y roles con OAuth2 o JWT. | `app/main.py` |
| **Escalabilidad** | Ejecutar la app en contenedores (Docker) y orquestar con Kubernetes o Docker Compose. | Configuración del proyecto |

---

## 🚫 9. Qué no hace hoy
- No procesa pagos ni información real de usuarios.  
- No se conecta a pasarelas de pago, bancos ni plataformas externas.  
- No analiza datos ni archivos locales de tu computadora.  
- No envía información fuera de tu entorno local.  
- Es un **simulador educativo** diseñado únicamente para demostrar arquitectura y flujo de análisis de fraude.  

---

## 🚀 10. Siguientes pasos sugeridos
1. Ajustar la sensibilidad del modelo (`RiskScorer`) para generar una distribución más equilibrada de riesgos (LOW / MEDIUM / HIGH).  
2. Incorporar **gráficas históricas** (riesgo medio por país, método de pago, hora del día, etc.).  
3. Implementar **autenticación y control de accesos** en el dashboard.  
4. Añadir **explicabilidad visual (SHAP / LIME)** para mostrar el peso de cada variable en la predicción.  
5. Desarrollar un **conector de ejemplo** que consuma datos reales (simulados desde un archivo CSV o API).  
6. **Dockerizar** el proyecto para facilitar despliegues en la nube (Railway, Fly.io, Render, etc.).  
7. Configurar **pipelines CI/CD** y pruebas automáticas para robustecer el código.  

-