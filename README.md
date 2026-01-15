## 🧠💪 Sistema de Reconocimiento de Movimientos de la Muñeca con Señales EMG

## 👥 Autores

Proyecto desarrollado de manera colaborativa por:

Yerson D. Díaz Carreño, Ingeniero Electrónico

Osmel D. Navarro Meza, Ingeniero Electrónico

Héctor A. Roca Pérez, Ingeniero Electrónico

📌 Repositorio mantenido por Héctor A. Roca Pérez como parte de su portafolio profesional.

## 🏫 Institución

Universidad Popular del Cesar
Facultad de Ingenierías y Tecnológicas
Programa de Ingeniería Electrónica

## 🎓 Dirección Académica

Ing. Lorena Paola Vargas Quintero, MSc, Ph. D

Ing. Leiner Barba Jiménez, MSc, Ph. D


## Resumen:

Este proyecto presenta el diseño e implementación de un sistema inteligente para el reconocimiento de los movimientos de flexión y extensión de la muñeca, a partir de señales electromiográficas (EMG) de superficie.

El sistema integra hardware biomédico, procesamiento de señales en el dominio tiempo-frecuencia y algoritmos de aprendizaje automático, con el objetivo de servir de base para aplicaciones futuras en rehabilitación, prótesis inteligentes e interfaces humano-máquina.

El desarrollo abarca todo el flujo del sistema:

![proceso](https://github.com/user-attachments/assets/5948a4fc-5ed6-4720-85ba-181ce4bb8ae4)


## 🎯 Objetivos

- Objetivo General:

Implementar un sistema de análisis y procesamiento de señales electromiográficas que permita reconocer y clasificar los movimientos de flexión y extensión de la muñeca. 

- Objetivos Específicos:

Construir un sistema de adquisición y filtrado de señales EMG que capture información de los movimientos de flexión y extensión de la mano. 

Desarrollar un esquema de caracterización de las señales EMG adquiridas utilizando métodos de extracción de información de tiempo-frecuencia. 

Implementar un clasificador de las señales de EMG caracterizadas utilizando un método de aprendizaje de máquinas. 

Validar todo el sistema desarrollado utilizando métricas de desempeño adecuadas 

## 👥 Participantes

El estudio contó con la participación voluntaria de miembros de la Universidad Popular del Cesar, incluyendo estudiantes y docentes.

- Total de participantes: 80

- Hombres: 57

- Mujeres: 23

- Rango de edad: 20 a 27 años

Adicionalmente, se registraron datos antropométricos como peso y altura para el cálculo del Índice de Masa Corporal (IMC), con el fin de analizar su posible influencia en la captación de las señales EMG

## 📈 Datos Recolectados

Para cada participante se adquirieron:

- Señales EMG crudas de superficie

- Registros asociados a:

  - Flexión de la muñeca

  - Extensión de la muñeca

- Dos repeticiones por cada tipo de movimiento

- Etiquetado del movimiento correspondiente

- Información básica del sujeto (anonimizada)

Las señales fueron almacenadas en formato .xlsx, facilitando su lectura y procesamiento posterior

## Protocolo de Medición

El protocolo experimental se desarrolló bajo condiciones controladas:

- El participante se sentó frente a un computador portátil que proporcionaba seguimiento visual de los estímulos.

- Cada sujeto realizó movimientos repetidos de:

 - Flexión y extensión de la muñeca.

- Cada gesto fue:

  - Sostenido durante 3 segundos

  - Seguido por una pausa de 2 segundos

- Se realizaron 2 repeticiones por movimiento.

- El rango de movimiento fue aproximadamente:

 - 90° para flexión

 - 60° para extensión 

## Consideraciones Éticas

- Todos los participantes firmaron un consentimiento informado.

- Los datos fueron anonimizados mediante identificadores.

- La información fue utilizada exclusivamente con fines académicos y de investigación

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


