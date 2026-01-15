## 🧠💪 Sistema de Reconocimiento de Movimientos de la Muñeca con Señales EMG

Héctor A. Roca Pérez
Ingeniero Electrónico | Análisis de Señales | Machine Learning aplicado a Bioingeniería

## Resumen:

Este proyecto presenta el diseño e implementación de un sistema inteligente para el reconocimiento de los movimientos de flexión y extensión de la muñeca, a partir de señales electromiográficas (EMG) de superficie.

El sistema integra hardware biomédico, procesamiento de señales en el dominio tiempo-frecuencia y algoritmos de aprendizaje automático, con el objetivo de servir de base para aplicaciones futuras en rehabilitación, prótesis inteligentes e interfaces humano-máquina.

El desarrollo abarca todo el flujo del sistema:

<img width="320" height="451" alt="image" src="https://github.com/user-attachments/assets/3a570b65-8118-4423-8982-0b39021517ff" />

## 🎯 Objetivos

-objetivo General:

Implementar un sistema de análisis y procesamiento de señales electromiografías que permita el reconocimiento y clasificación de los  movimientos de flexión y extensión de la muñeca. 

-objetivos Específicos:

Construir un sistema de adquisición y filtrado de señales EMG que capturen información de los movimientos de flexión y extensión de la mano. 

Desarrollar un esquema de caracterización de las señales EMG adquiridas utilizando métodos de extracción de información de tiempo-frecuencia. 

Implementar un clasificador de las señales de EMG caracterizadas utilizando un método aprendizaje de máquinas. 

Validar todo el sistema desarrollado utilizando métricas de desempeño adecuadas 

## ⚙️ Arquitectura del Sistema

1. **Adquisición de Señales**
   - Sensor EMG de diseño propio
   - Electrodos de superficie
   - Amplificación con AD620
   - Filtrado pasa-banda

2. **Preprocesamiento**
   - Eliminación de ruido
   - Rectificación
   - Normalización

3. **Extracción de Características**
   - Dominio temporal
   - Dominio tiempo-frecuencia
   - Transformada Wavelet
   - Métricas estadísticas (entropía, curtosis, asimetría)

4. **Clasificación**
   - Árbol de Decisión
   - Redes Neuronales Artificiales (ANN)
   - Support Vector Machine (SVM)

5. **Evaluación**
   - Precisión
   - Recall
   - F1-Score
   - Matriz de confusión

6. **Interfaz Gráfica**
   - Visualización de señales EMG
   - Comparación de modelos
   - Resultados en tiempo real

---

## 🤖 Modelos de Machine Learning Implementados

| Modelo | Descripción |
|------|------------|
| Árbol de Decisión | Clasificación basada en reglas condicionales |
| Redes Neuronales | Reconocimiento de patrones no lineales |
| SVM | Separación óptima mediante hiperplanos |

---

## 🛠️ Tecnologías y Herramientas

### Hardware
- Arduino UNO  
- Sensor EMG (diseño propio)
- Amplificador de instrumentación AD620
- Electrodos de superficie

### Software
- **Python**
- **MATLAB**
- **KiCad**
- **Fusion 360**
- **Scikit-learn**
- **NumPy / SciPy**
- **Matplotlib**

---

## 📊 Resultados Destacados

- Reconocimiento confiable de flexión y extensión de la muñeca.
- Comparación objetiva de modelos de clasificación.
- Buen desempeño en precisión y estabilidad.
- Sistema de bajo costo y alta escalabilidad.

## 👥 Autores

Proyecto desarrollado de manera colaborativa por:

Yerson D. Díaz Carreño

Osmel D. Navarro Meza

Héctor A. Roca Pérez

📌 Repositorio mantenido por Héctor A. Roca Pérez como parte de su portafolio profesional.

## 🏫 Institución

Universidad Popular del Cesar
Facultad de Ingenierías y Tecnológicas
Programa de Ingeniería Electrónica

## 🎓 Dirección Académica

Ing. Lorena Paola Vargas Quintero, MSc, Ph. D

Ing. Leiner Barba Jiménez, MSc, Ph. D

## 📄 Estado del Proyecto

✔️ Proyecto académico finalizado
✔️ Escalable a más gestos y señales
✔️ Base sólida para sistemas en tiempo real y aplicaciones embebidas
