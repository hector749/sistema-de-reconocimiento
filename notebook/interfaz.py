# ====================
# BIBLIOTECAS ESTÁNDAR
# ====================
import os
import time
import gc
import multiprocessing
from datetime import datetime

# ====================
# INTERFAZ GRÁFICA
# ====================
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Frame, Tk
from PIL import Image, ImageTk, ImageOps

# ====================
# MANEJO DE DATOS
# ====================
import pandas as pd
import numpy as np

# ====================
# VISUALIZACIÓN
# ====================
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

# ====================
# PROCESAMIENTO DE SEÑALES
# ====================
import scipy.signal as signal
from scipy.fft import fft
from scipy.signal import iirnotch, lfilter, butter, filtfilt, hilbert
from scipy.ndimage import gaussian_filter1d
from scipy.stats import entropy
import pywt

# ====================
# MACHINE LEARNING
# ====================
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    make_scorer,
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score
)
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier, plot_tree

# ====================
# COMUNICACIÓN SERIAL
# ====================
import serial


class SerialReader:
    def __init__(self, port, speed):
        self.port = port
        self.speed = speed
        self.columns = ["Fecha y hora", "Tiempo (s)", "Muestra", "Valor lectura", "Sujeto", "Movimiento_ID"]
        self.records_to_read = 100
        self.data = pd.DataFrame(columns=self.columns)
        self.ax = None
        self.canvas = None
        self.text_widget = None  # Widget para mostrar los datos
        
    def set_text_widget(self, text_widget):
        self.text_widget = text_widget

    def set_records_number(self, count):
        self.records_to_read = count
        
    def set_plot_widgets(self, ax, canvas):
        self.ax = ax
        self.canvas = canvas

    def read_from_port(self, subject_id, movement_type):
        """Lectura de datos seriales con visualización en tiempo real"""
        try:
            movement_id = 13 if movement_type == "Flexion" else 14
            ser = serial.Serial(self.port, self.speed, timeout=0.1)
            
            # Configurar widget de texto si existe
            if self.text_widget:
                self.text_widget.delete('1.0', tk.END)
                self.text_widget.insert(tk.END, f"Iniciando captura...\nSujeto: {subject_id}\nMovimiento: {movement_type}\n")
                self.text_widget.insert(tk.END, "-"*40 + "\n")
            
            buffer_data = []
            start_time = time.time()
            
            for sample_num in range(1, self.records_to_read + 1):
                line = ser.readline().decode(errors='ignore').strip()
                if line:
                    now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    elapsed = round(time.time() - start_time, 2)
                    buffer_data.append([now, elapsed, sample_num, float(line), subject_id, movement_id])
                    
                    # Mostrar en widget de texto
                    if self.text_widget:
                        self.text_widget.insert(tk.END, f"Muestra {sample_num:3d}: {float(line):>8.2f} | T: {elapsed:5.2f}s\n")
                        self.text_widget.see(tk.END)  # Auto-scroll
                        self.text_widget.update()  # Actualizar en tiempo real
            
            # Guardar datos y mostrar resultados
            self.data = pd.DataFrame(buffer_data, columns=self.columns)
            
            if self.text_widget and len(buffer_data) > 0:
                self.text_widget.insert(tk.END, "-"*40 + "\n")
                self.text_widget.insert(tk.END, f"Captura completada: {len(buffer_data)} muestras\n")
            
            self._show_plot(subject_id, movement_type)
            messagebox.showinfo("Éxito", f"Datos capturados: {len(self.data)} muestras")
            
        except Exception as e:
            error_msg = f"Error en lectura: {str(e)}"
            if self.text_widget:
                self.text_widget.insert(tk.END, "\nERROR: " + error_msg + "\n")
            messagebox.showerror("Error", error_msg)
        finally:
            if 'ser' in locals():
                ser.close()

    def _show_plot(self, subject_id, movement_type):
        """Visualización de los datos capturados"""
        if self.ax and self.canvas and not self.data.empty:
            self.ax.clear()
            
            # Excluir los primeros 50 datos si hay suficientes muestras
            data_to_plot = self.data.iloc[1000:] if len(self.data) > 1000 else self.data
            
            self.ax.plot(data_to_plot['Muestra'], data_to_plot['Valor lectura'], 'b-')
            self.ax.set_title(f'Sujeto: {subject_id} | Movimiento: {movement_type}')
            self.ax.set_xlabel('Muestra')
            self.ax.set_ylabel('Valor Lectura')
            self.ax.grid(True)
            self.canvas.draw()

# Constantes
ROOT_PATH = r"C:\Users\Work\Desktop\aplicacion"
ASSETS_PATH = os.path.join(ROOT_PATH, "assets")
COLOR_PRINCIPAL = '#2c3e50'

class InterfazApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BioMotion Analyzer")
        self.root.geometry("1000x700")
        icon_path = os.path.join(ROOT_PATH, "icono.ico")
        self.root.iconbitmap(icon_path)
        
        # Verificación de recursos (debug)
        print("=== Verificación inicial ===")
        print("Ruta actual:", os.path.abspath(os.getcwd()))
        if os.path.exists(ASSETS_PATH):
            print("Archivos en assets/:", os.listdir(ASSETS_PATH))
        
        # Configuración inicial
        self._setup_background()
        self._setup_main_frame()
        self._setup_button_icons()
        self._setup_ui_components()
        
    def _setup_background(self):
        """Configura el fondo con manejo robusto de errores"""
        try:
            bg_path = os.path.join(ROOT_PATH, f"fondo.png")
            if not os.path.exists(bg_path):
                bg_path = os.path.join(ASSETS_PATH, "fondo.jpg")
            bg_img = Image.open(bg_path)
            bg_img = bg_img.resize((self.root.winfo_screenwidth(), 
                                  self.root.winfo_screenheight()),
                                  Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_img)
            bg_label = tk.Label(self.root, image=self.bg_photo)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            bg_label.lower()
        except Exception as e:
            self.root.configure(bg=COLOR_PRINCIPAL)
            print(f"Error al cargar fondo: {str(e)}")
            
    def _setup_main_frame(self):
        """Crea el marco principal semitransparente"""
        self.main_frame = tk.Frame(self.root, bg='#cce6ff', bd=2, relief='groove')
        self.main_frame.place(relwidth=0.8, relheight=0.9, relx=0.10, rely=0.05)

        # Título
        title = tk.Label(self.main_frame, text="Análisis Inteligente de Movimiento", 
                        font=("Arial", 24, "bold"), bg='#6699cc', fg="white")
        title.pack(pady=(20, 10))

        # Frame para imágenes debajo del título
        img_frame = tk.Frame(self.main_frame, bg='#cce6ff')
        img_frame.pack(pady=(10, 20))  # espacio entre título e imágenes

        # Cargar imágenes desde ROOT_PATH
        Mov_path = os.path.join(ROOT_PATH, "imagen.png")

        Mov_img = Image.open(Mov_path).resize((400, 250))  # nuevo tamaño

        self.flexion_photo = ImageTk.PhotoImage(Mov_img)

        # Marcos para cada imagen
        Mov_frame = tk.Frame(img_frame, bg='#cce6ff')

        # Solo imágenes (sin texto)
        Mov_label = tk.Label( Mov_frame, image=self.flexion_photo, bg='#cce6ff')
        Mov_label.pack()

        Mov_frame.pack(side='left', padx=40)



    def _setup_button_icons(self):
        """Carga los iconos para los botones - redimensionados de forma uniforme sin deformar"""
        self.icons = {}
        icon_mapping = {
            'load': 'load_icon',
            'capture': 'capture_icon',
            'signal': 'signal_icon',
            'test': 'test_icon',
            'results': 'results_icon'
        }

        icon_size = (32, 32)  # Tamaño uniforme para todos los íconos

        for code_name, file_name in icon_mapping.items():
            icon_loaded = False
            for ext in ['.png']:
                img_path = os.path.join(ROOT_PATH, f"{file_name}{ext}")
                if os.path.exists(img_path):
                    try:
                        img = Image.open(img_path).convert("RGBA")

                        # Crear un lienzo transparente del tamaño final
                        canvas = Image.new("RGBA", icon_size, (0, 0, 0, 0))

                        # Redimensionar sin deformar (manteniendo aspecto)
                        img.thumbnail(icon_size, Image.Resampling.LANCZOS)

                        # Calcular posición para centrar la imagen
                        offset = ((icon_size[0] - img.width) // 2, (icon_size[1] - img.height) // 2)
                        canvas.paste(img, offset)

                        icon = ImageTk.PhotoImage(canvas)
                        self.icons[code_name] = icon

                        print(f"Icono cargado y ajustado: {file_name}{ext}, original: {img.size}, final: {canvas.size}")
                        icon_loaded = True
                        break
                    except Exception as e:
                        print(f"Error al procesar {img_path}: {e}")
            if not icon_loaded:
                print(f"¡Icono {file_name} no encontrado!")
                self.icons[code_name] = None


    def _setup_ui_components(self):
        """Configura todos los componentes de la interfaz"""
        self.frame_imagenes = tk.Frame(self.main_frame, bg='white')
        self.frame_imagenes.pack(pady=10)

        self._setup_buttons()
        self._setup_message_area()

    def _setup_buttons(self):
        """Configuración de botones corregida y optimizada"""
        button_configs = [
            {"text": "Cargar Archivo", "icon": "load", "bg": "#3498db", "command": self.cargar_archivo},
            {"text": "Capturar Datos", "icon": "capture", "bg": "#2ecc71", "command": self.capturar_datos},
            {"text": "Ver Señales", "icon": "signal", "bg": "#9b59b6", "command": self.ver_senales},
            {"text": "Prueba", "icon": "test", "bg": "#e67e22", "command": self.prueba},
            {"text": "Resultados", "icon": "results", "bg": "#34495e", "command": self.resultados},
        ]

        self.frame_botones = tk.Frame(self.main_frame, bg='#6699cc')
        self.frame_botones.pack(pady=20)

        # Creación automática en grid 1x5
        for i, config in enumerate(button_configs):
            btn = self._create_button(config)
            btn.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            self.frame_botones.grid_columnconfigure(i, weight=1)

    def _create_button(self, config):
        """Versión robusta para creación de botones"""
        icon_img = self.icons.get(config['icon'])
        if icon_img:
            btn = tk.Button(
                self.frame_botones,
                text=config['text'],
                image=icon_img,
                compound="top",
                command=config['command'],
                width=180,
                height=80,
                font=("Arial", 11, "bold"),
                bg=config['bg'],
                fg='white',
                activebackground=self._darken_color(config['bg']),
                relief='flat',
                bd=0
            )
            btn.image = icon_img  # Referencia a la imagen
        else:
            btn = tk.Button(
                self.frame_botones,
                text=config['text'],
                command=config['command'],
                width=180,
                height=50,
                font=("Arial", 11, "bold"),
                bg=config['bg'],
                fg='white',
                activebackground=self._darken_color(config['bg']),
                relief='flat',
                bd=0
            )

        return btn


    def _darken_color(self, hex_color, factor=0.8):
        """Oscurece un color hexadecimal para el efecto hover"""
        rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * factor)) for c in rgb)
        return f'#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}'

    def _setup_message_area(self):
        """Configura el área de mensajes con scrollbar"""
        self.text_frame = tk.Frame(self.main_frame, bg='white')
        self.text_frame.pack(pady=20, fill='both', expand=True)
        
        self.scrollbar = tk.Scrollbar(self.text_frame)
        self.scrollbar.pack(side='right', fill='y')
        
        self.area_mensajes = tk.Text(
            self.text_frame,
            height=50,
            width=70,
            font=("Consolas", 11),
            bg='#f9f9f9',
            fg='#333',
            yscrollcommand=self.scrollbar.set,
            wrap='word'
        )
        self.area_mensajes.pack(fill='both', expand=True)
        self.scrollbar.config(command=self.area_mensajes.yview)

    def cargar_archivo(self):
        self.area_mensajes.delete(1.0, tk.END)
        # Nombre del archivo a cargar
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        try:
            # Cargar el archivo Excel
            self.df = pd.read_excel(archivo)
            self.file_name = archivo

            # Verificar que las columnas necesarias existen
            if 'Valor lectura' not in self.df.columns or 'Sujeto' not in self.df.columns or 'Movimiento_ID' not in self.df.columns:
                raise ValueError("El archivo no contiene las columnas necesarias: 'Valor lectura', 'Sujeto' o 'Movimiento_ID'.")

            # Parámetros del filtro
            fs = 500  # Frecuencia de muestreo (200 Hz)
            Ts = 1 / fs  # Periodo de muestreo
            low_cutoff = 20  # Frecuencia de corte inferior (Hz)
            high_cutoff = 200  # Frecuencia de corte superior (Hz)
            Q = 20.0  # Factor de calidad del notch
            
            
            # Función para identificar frecuencias de ruido
            def identificar_ruidos(senal, num_ruidos=4):
                N = len(senal)
                yf = fft(senal)
                xf = np.linspace(0.0, fs / 2, N // 2)
                magnitudes = 2.0 / N * np.abs(yf[0:N // 2])
                indices_ruido = np.argsort(magnitudes)[-num_ruidos:]
                return xf[indices_ruido]

            # Función para aplicar el filtro notch
            def aplicar_filtro_notch(senal, f0, Q):
                b, a = iirnotch(f0, Q, fs)
                return lfilter(b, a, senal)

            # Función para diseñar el filtro pasabanda
            def butter_bandpass(lowcut, highcut, fs, order=5):
                nyquist = 0.5 * fs
                low = lowcut / nyquist
                high = highcut / nyquist
                b, a = butter(order, [low, high], btype='band')
                return b, a

            # Función para aplicar el filtro pasabanda
            def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
                b, a = butter_bandpass(lowcut, highcut, fs, order=order)
                return filtfilt(b, a, data)


            self.df['Señal Filtrada'] = np.nan

            # Filtrar por sujeto y tipo de movimiento
            sujetos = self.df['Sujeto'].unique()
            movimientos = self.df['Movimiento_ID'].unique()

            for sujeto in sujetos:
                for movimiento in movimientos:
                    # Seleccionar los datos del sujeto y movimiento actual
                    df_sujeto_movimiento = self.df[(self.df['Sujeto'] == sujeto) & (self.df['Movimiento_ID'] == movimiento)]
                    # Verificar si la señal tiene suficientes muestras
                    if len(df_sujeto_movimiento) < 34:
                        self.area_mensajes.insert(
                            tk.END, 
                            f"Sujeto {sujeto}, Movimiento {movimiento}: señal demasiado corta ({len(df_sujeto_movimiento)} muestras), se omite el filtrado.\n"
                        )
                        continue  # Saltar esta señal

                    # Aplicar el filtro pasabanda
                    senal_filtrada = butter_bandpass_filter(df_sujeto_movimiento['Valor lectura'].values, low_cutoff, high_cutoff, fs)

                    # Identificar y aplicar filtros notch
                    frecs_ruido = identificar_ruidos(senal_filtrada, num_ruidos=4)
                    for f0 in frecs_ruido:
                        senal_filtrada = aplicar_filtro_notch(senal_filtrada, f0, Q)

                    # Asignar la señal filtrada a la columna correspondiente
                    self.df.loc[(self.df['Sujeto'] == sujeto) & (self.df['Movimiento_ID'] == movimiento), 'Señal Filtrada'] = senal_filtrada
            

            # Guardar el DataFrame con la señal filtrada en el mismo archivo Excel
            with pd.ExcelWriter(archivo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                self.df.to_excel(writer, index=False)

            # Mostrar mensaje de éxito
            self.area_mensajes.insert(tk.END, f"Archivo cargado: {archivo}\n")
            messagebox.showinfo("Éxito", "Archivo cargado y señal filtrada correctamente.")

            # Mostrar las primeras filas del DataFrame con la nueva columna
            self.area_mensajes.insert(tk.END, "Primeras filas del archivo con señal filtrada:\n")
            self.area_mensajes.insert(tk.END, str(self.df.head()) + "\n")

        except Exception as e:
            # Mostrar mensaje de error
            self.area_mensajes.insert(tk.END, f"Error: {str(e)}\n")
            messagebox.showerror("Error", f"Error al cargar el archivo: {str(e)}")

            
    def capturar_datos(self):
        self.abrir_ventana_captura()
    
    def abrir_ventana_captura(self):
        # Crear una nueva ventana
        ventana_captura = tk.Toplevel(self.root)
        ventana_captura.title("Captura de Datos")
        ventana_captura.geometry("900x700")  # Aumenté el tamaño para mejor visualización
        ventana_captura.grid_columnconfigure(0, weight=1)
        ventana_captura.grid_rowconfigure(4, weight=1)
        ventana_captura.iconbitmap(os.path.join(ROOT_PATH, "icono.ico"))
        ventana_captura.configure(bg="#e6e6e6") 

        # Frame para controles de entrada
        frame_controles = tk.Frame(ventana_captura)
        frame_controles.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Campos de entrada
        tk.Label(frame_controles, text="Puerto:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_puerto = tk.Entry(frame_controles, font=("Arial", 12))
        self.entry_puerto.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frame_controles, text="Subject ID:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_subject_id = tk.Entry(frame_controles, font=("Arial", 12))
        self.entry_subject_id.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frame_controles, text="Tipo de Movimiento:", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_movement_type = ttk.Combobox(frame_controles, values=["Flexion", "Extension"], font=("Arial", 12))
        self.entry_movement_type.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.entry_movement_type.current(0)  # Selección por defecto

        # Botón para iniciar la captura
        boton_iniciar = tk.Button(frame_controles, text="Iniciar Captura", command=self.iniciar_captura, 
                                width=20, font=("Arial", 12), bg="#6699cc", fg="white")
        boton_iniciar.grid(row=3, column=0, columnspan=2, pady=10)

        # Frame para gráfica
        frame_grafica = tk.Frame(ventana_captura)
        frame_grafica.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_grafica)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Frame para consola de texto
        frame_texto = tk.Frame(ventana_captura)
        frame_texto.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        # Widget de texto con scroll
        self.text_widget = tk.Text(frame_texto, height=12, wrap=tk.NONE, font=("Consolas", 10))
        scroll_y = tk.Scrollbar(frame_texto, command=self.text_widget.yview)
        scroll_x = tk.Scrollbar(frame_texto, orient=tk.HORIZONTAL, command=self.text_widget.xview)
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.text_widget.config(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        # Configurar tags para colores
        self.text_widget.tag_config('header', foreground='blue')
        self.text_widget.tag_config('error', foreground='red')
        self.text_widget.tag_config('success', foreground='green')

    def iniciar_captura(self):
        port = self.entry_puerto.get()
        subject_id = self.entry_subject_id.get()
        movement_type = self.entry_movement_type.get()

        if not port or not subject_id or not movement_type:
            messagebox.showwarning("Advertencia", "Complete todos los campos")
            return

        # Limpiar widgets antes de nueva captura
        self.ax.clear()
        self.canvas.draw()
        self.text_widget.delete('1.0', tk.END)
        
        # Configurar y ejecutar captura
        try:
            reader = SerialReader(port, 9600)
            reader.set_records_number(6015)  # Ajusta según necesidad
            reader.set_plot_widgets(self.ax, self.canvas)
            reader.set_text_widget(self.text_widget)  # ¡Importante! Asignar el widget de texto
            reader.read_from_port(subject_id, movement_type)
        except Exception as e:
            self.text_widget.insert(tk.END, f"Error al iniciar captura: {str(e)}\n", 'error')
            messagebox.showerror("Error", f"No se pudo iniciar la captura: {str(e)}")
            
    def ver_senales(self):
        # Crear una nueva ventana
        ventana_senales = tk.Toplevel(self.root)
        ventana_senales.title("Visualización de Señales")
        ventana_senales.geometry("1400x900")
        ventana_senales.iconbitmap(os.path.join(ROOT_PATH, "icono.ico"))
        ventana_senales.configure(bg="#e6e6e6")

        # Frame para las gráficas
        frame_graficas = ttk.Frame(ventana_senales)
        frame_graficas.pack(fill='both', expand=True)

        # Crear figura de matplotlib con subgráficos
        fig, axs = plt.subplots(2, 2, figsize=(8, 6))
        fig.suptitle("Análisis de Señales", fontsize=12)

        # Selección de Sujeto
        tk.Label(frame_graficas, text="Seleccionar Sujeto:", font=("Arial", 12)).pack(pady=10)
        sujetos = self.df['Sujeto'].astype(str).unique()  # Convertir a cadenas de texto
        sujetos = [s.replace("['", "").replace("']", "") for s in sujetos]  # Eliminar corchetes y comillas
        self.combo_sujeto = ttk.Combobox(frame_graficas, values=sujetos, font=("Arial", 12))
        self.combo_sujeto.pack(pady=10)

        # Vincular el evento de selección a la función mostrar_senales_sujeto
        self.combo_sujeto.bind("<<ComboboxSelected>>", lambda event: self.mostrar_senales_sujeto(axs, fig))

        # Ajustar espaciado entre gráficas
        plt.tight_layout()

        # Integrar la figura en Tkinter
        self.canvas_senales = FigureCanvasTkAgg(fig, master=frame_graficas)
        self.canvas_senales.draw()
        self.canvas_senales.get_tk_widget().pack(fill='both', expand=True)

    def mostrar_senales_sujeto(self, axs, fig):
        # Obtener el sujeto seleccionado
        sujeto_seleccionado = self.combo_sujeto.get()

        # Limpiar las gráficas anteriores
        for ax in axs.flat:
            ax.clear()

        # Gráficas de amplitud
        self.def_amplitud(axs, sujeto_seleccionado)

        # Gráficas de Fourier
        self.def_fourier(axs, sujeto_seleccionado)

        # Actualizar la figura
        fig.suptitle(f"Análisis de Señales ({sujeto_seleccionado})", fontsize=14)
        self.canvas_senales.draw()

    def def_amplitud(self, axs, sujeto_seleccionado):
        # Gráfica 1: Flexión para el sujeto seleccionado
        flexion_df = self.df[(self.df['Movimiento_ID'] == 13) & (self.df['Sujeto'] == sujeto_seleccionado)]
        envolvente_flexion = np.abs(signal.hilbert(flexion_df['Señal Filtrada'].to_numpy()))
        envolvente_flexion_suave = gaussian_filter1d(envolvente_flexion, sigma=20)
        axs[0, 0].plot(flexion_df['Tiempo (s)'], envolvente_flexion_suave, color='red', label='Flexión')
        axs[0, 0].set_title('Amplitud de la señal', fontsize=10)
        axs[0, 0].set_ylabel('Valor Lectura', fontsize=10)
        axs[0, 0].legend()
        axs[0, 0].grid(True)

        # Gráfica 2: Extensión para el sujeto seleccionado
        extension_df = self.df[(self.df['Movimiento_ID'] == 14) & (self.df['Sujeto'] == sujeto_seleccionado)]
        envolvente_extension = np.abs(signal.hilbert(extension_df['Señal Filtrada'].to_numpy()))
        envolvente_extension_suave = gaussian_filter1d(envolvente_extension, sigma=20)

        # Recortar a las primeras 4950 muestras
        envolvente_recortada = envolvente_extension_suave[:4950]
        tiempo_recortado = extension_df['Tiempo (s)'].to_numpy()[:4950]

        axs[1, 0].plot(tiempo_recortado, envolvente_recortada, color='blue', label='Extensión')
        axs[1, 0].set_title('Amplitud de la señal', fontsize=10)
        axs[1, 0].set_xlabel('Tiempo (s)', fontsize=10)
        axs[1, 0].set_ylabel('Valor Lectura', fontsize=10)
        axs[1, 0].legend()
        axs[1, 0].grid(True)

    def def_fourier(self, axs, sujeto_seleccionado):
        Fs = 500
        Ts = 1 / Fs  # Periodo de muestreo

        # Gráfica 3: Espectro de Fourier para flexión
        flexion_df = self.df[(self.df['Movimiento_ID'] == 13) & (self.df['Sujeto'] == sujeto_seleccionado)]
        freqs_flex, espectro_flex_db = self.calcular_fft(flexion_df['Señal Filtrada'], Ts)
        axs[0, 1].plot(freqs_flex, espectro_flex_db, label="Flexión", color='r')
        axs[0, 1].set_title('Flexión: Espectro de Fourier ', fontsize=10)
        axs[0, 1].set_ylabel("Magnitud (dB/Hz)", fontsize=10)
        axs[0, 1].legend()
        axs[0, 1].grid(True)

        # Gráfica 4: Espectro de Fourier para extensión
        extension_df = self.df[(self.df['Movimiento_ID'] == 14) & (self.df['Sujeto'] == sujeto_seleccionado)]
        freqs_ext, espectro_ext_db = self.calcular_fft(extension_df['Señal Filtrada'], Ts)
        axs[1, 1].plot(freqs_ext, espectro_ext_db, label="Extensión", color='b')
        axs[1, 1].set_title('Extensión: Espectro de Fourier ', fontsize=10)
        axs[1, 1].set_xlabel('Frecuencia (Hz)', fontsize=10)
        axs[1, 1].set_ylabel("Magnitud (dB/Hz)", fontsize=10)
        axs[1, 1].legend()
        axs[1, 1].grid(True)

    def calcular_fft(self, senal, Ts):
        senal_np = senal.to_numpy()
        N = len(senal_np)  # Longitud de la señal
        yf = fft(senal_np) 
        frecuencias = np.linspace(0.0, 1.0 / (2.0 * Ts), N // 2)  # Eje de frecuencias
        espectro_db = 2.0 / N * np.abs(yf[0:N // 2])  # Magnitud del espectro
        return frecuencias, espectro_db
    
    def prueba(self):
        if hasattr(self, 'df'):
            # Funciones auxiliares internas
            def limpiar_id_sujeto(sujeto_id):
                """Limpia y normaliza el ID del sujeto"""
                if isinstance(sujeto_id, str):
                    import re
                    match = re.search(r'\d+', str(sujeto_id))
                    if match:
                        return int(match.group())
                    else:
                        return sujeto_id
                return sujeto_id

            def suavizar_wavelet(signal, wavelet='db4', level=4):
                """Aplica suavizado wavelet a la señal"""
                coeffs = pywt.wavedec(signal, wavelet, level=level)
                coeffs_suavizados = [coeffs[0]] + [np.zeros_like(c) for c in coeffs[1:]]
                return pywt.waverec(coeffs_suavizados, wavelet)[:len(signal)]

            def extraer_caracteristicas_avanzadas(senal, fs=1000, wavelet='db4'):
                """Extrae características avanzadas para ML"""
                
                # 1. Características temporales
                rms = np.sqrt(np.mean(np.square(senal)))
                var = np.var(senal)
                mean_abs = np.mean(np.abs(senal))
                skewness = np.mean(((senal - np.mean(senal)) / np.std(senal)) ** 3)
                kurtosis = np.mean(((senal - np.mean(senal)) / np.std(senal)) ** 4)
                
                # 2. Características de frecuencia (FFT)
                fft_vals = np.fft.fft(senal)
                freqs = np.fft.fftfreq(len(senal), 1/fs)
                magnitudes = np.abs(fft_vals)
                
                # Potencia en bandas de frecuencia
                banda_baja = np.sum(magnitudes[(freqs >= 20) & (freqs <= 80)])
                banda_media = np.sum(magnitudes[(freqs >= 80) & (freqs <= 150)])
                banda_alta = np.sum(magnitudes[(freqs >= 150) & (freqs <= 250)])
                
                freq_mediana = np.median(freqs[magnitudes > np.max(magnitudes)*0.1])
                
                # 3. Características wavelet
                coeffs = pywt.wavedec(senal, wavelet, level=4)
                energia_total = sum([np.sum(c**2) for c in coeffs])
                
                caracteristicas_wavelet = []
                for i, c in enumerate(coeffs):
                    energia_nivel = np.sum(c**2) / energia_total if energia_total > 0 else 0
                    caracteristicas_wavelet.extend([
                        energia_nivel,
                        np.std(c),
                        np.mean(np.abs(c))
                    ])
                
                # 4. Características de la envolvente
                envolvente = np.abs(hilbert(senal))
                rms_envolvente = np.sqrt(np.mean(envolvente**2))
                var_envolvente = np.var(envolvente)
                
                # Compilar todas las características
                features = {
                    # Temporales básicas
                    #'rms': rms,
                    #'varianza': var,
                    #'mean_abs': mean_abs,
                    'skewness': skewness,
                    'kurtosis': kurtosis,
                    #'banda_baja': banda_baja,
                    #'banda_media': banda_media,
                    #'banda_alta': banda_alta,
                    #'freq_mediana': freq_mediana,
                    #'rms_envolvente': rms_envolvente,
                    #'var_envolvente': var_envolvente,
                    # Entropía
                    'entropia': entropy(np.histogram(senal, bins=50)[0])
                }
                
                # Agregar características wavelet
                for i, val in enumerate(caracteristicas_wavelet):
                    features[f'wavelet_{i}'] = val
                
                return features

            def crear_dataset_ml(df):
                """Crea dataset para machine learning usando todos los sujetos disponibles"""
                caracteristicas_lista = []
                
                # Crear copia con IDs limpios
                df_limpio = df.copy()
                df_limpio['Sujeto_Limpio'] = df_limpio['Sujeto'].apply(limpiar_id_sujeto)
                
                # Procesar todos los sujetos disponibles para movimientos 13 y 14
                for movimiento_id in [13, 14]:  # Flexión y Extensión
                    df_mov = df_limpio[df_limpio['Movimiento_ID'] == movimiento_id]
                    
                    for sujeto in df_mov['Sujeto_Limpio'].unique():
                        df_sujeto = df_mov[df_mov['Sujeto_Limpio'] == sujeto]
                        if not df_sujeto.empty:
                            senal = df_sujeto['Señal Filtrada'].values
                            senal_suave = suavizar_wavelet(senal)
                            
                            features = extraer_caracteristicas_avanzadas(senal_suave)
                            features.update({
                                'Sujeto': sujeto,
                                'Movimiento_ID': movimiento_id,
                                'Clase': 'Flexion' if movimiento_id == 13 else 'Extension'
                            })
                            caracteristicas_lista.append(features)
                
                return pd.DataFrame(caracteristicas_lista)

            def dividir_datos_manual(df_ml, sujetos_test=None, usar_automatico=True, test_size=0.2, random_state=42):
                """
                Divide los datos de forma manual o automática
                
                Parámetros:
                - df_ml: DataFrame con las características
                - sujetos_test: Lista de sujetos para test (si None, se usa división automática)
                - usar_automatico: Si True, usa división automática; si False, usa sujetos_test
                - test_size: Proporción para test en división automática
                - random_state: Semilla para reproducibilidad
                
                Retorna:
                - Tupla con (X_train, X_test, y_train, y_test, suj_train, suj_test)
                """
                
                # Preparar características y etiquetas
                feature_columns = [col for col in df_ml.columns 
                                if col not in ['Sujeto', 'Movimiento_ID', 'Clase']]
                
                X = df_ml[feature_columns].values
                y = df_ml['Clase'].values
                sujetos = df_ml['Sujeto'].values
                
                if usar_automatico or sujetos_test is None:
                    # División automática
                    print("🔄 Usando división automática de datos...")
                    X_train, X_test, y_train, y_test, suj_train, suj_test = train_test_split(
                        X, y, sujetos, test_size=test_size, random_state=random_state, stratify=y
                    )
                else:
                    # División manual
                    print(f"✋ Usando división manual de datos...")
                    print(f"Sujetos seleccionados para test: {sujetos_test}")
                    
                    # Validar que los sujetos existen
                    sujetos_disponibles = set(df_ml['Sujeto'].unique())
                    sujetos_test_set = set(sujetos_test)
                    
                    if not sujetos_test_set.issubset(sujetos_disponibles):
                        sujetos_invalidos = sujetos_test_set - sujetos_disponibles
                        raise ValueError(f"Los siguientes sujetos no están disponibles: {sujetos_invalidos}")
                    
                    # Crear máscaras para separar datos
                    mask_test = df_ml['Sujeto'].isin(sujetos_test)
                    mask_train = ~mask_test
                    
                    # Separar datos
                    X_train = df_ml.loc[mask_train, feature_columns].values
                    X_test = df_ml.loc[mask_test, feature_columns].values
                    y_train = df_ml.loc[mask_train, 'Clase'].values
                    y_test = df_ml.loc[mask_test, 'Clase'].values
                    suj_train = df_ml.loc[mask_train, 'Sujeto'].values
                    suj_test = df_ml.loc[mask_test, 'Sujeto'].values
                    
                    # Verificar distribución
                    test_classes = pd.Series(y_test).value_counts()
                    train_classes = pd.Series(y_train).value_counts()
                    
                    print(f"📊 Distribución en entrenamiento: {dict(train_classes)}")
                    print(f"📊 Distribución en test: {dict(test_classes)}")
                    
                    if len(test_classes) < 2:
                        print("⚠️  ADVERTENCIA: El conjunto de test no tiene ambas clases!")
                
                print(f"📈 Datos de entrenamiento: {len(X_train)} muestras")
                print(f"🧪 Datos de prueba: {len(X_test)} muestras")
                
                return X_train, X_test, y_train, y_test, suj_train, suj_test, feature_columns

            try:
                # Crear una nueva ventana
                ventana_prueba = tk.Toplevel(self.root)
                ventana_prueba.title("Entrenando modelo con características avanzadas")
                ventana_prueba.geometry("1400x900")
                ventana_prueba.iconbitmap(os.path.join(ROOT_PATH, "icono.ico"))
                ventana_prueba.configure(bg="#e6e6e6")

                # Frame principal para organizar los elementos
                frame_principal = tk.Frame(ventana_prueba)
                frame_principal.pack(fill=tk.BOTH, expand=True)

                # Frame para el gráfico del árbol de decisión (parte superior)
                frame_grafico = tk.Frame(frame_principal)
                frame_grafico.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

                # Frame para los datos de test y entrenamiento (parte inferior)
                frame_datos = tk.Frame(frame_principal)
                frame_datos.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

                # Frame para los datos de test (mitad izquierda)
                frame_test = tk.Frame(frame_datos)
                frame_test.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                # Frame para los datos de entrenamiento (mitad derecha)
                frame_train = tk.Frame(frame_datos)
                frame_train.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

                print("🔬 Creando dataset con características avanzadas...")
                # Crear dataset con características avanzadas
                df_ml = crear_dataset_ml(self.df)
                
                print(f"📊 Dataset creado con {len(df_ml)} muestras y {len(df_ml.columns)-3} características")
                print(f"🎯 Clases disponibles: {df_ml['Clase'].value_counts().to_dict()}")
                print(f"👥 Sujetos disponibles: {sorted(df_ml['Sujeto'].unique())}")

                # Dividir datos (puedes cambiar usar_automatico=False y especificar sujetos_test para división manual)
                X_train, X_test, y_train, y_test, suj_train, suj_test, feature_columns = dividir_datos_manual(
                    df_ml, 
                    usar_automatico=True,  # Cambiar a False para división manual
                    # sujetos_test=[1, 2],  # Especificar sujetos para test si usar_automatico=False
                    test_size=0.3,
                    random_state=42
                )

                # Normalizar características
                print("🔧 Normalizando características...")
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Guardar el escalador para uso posterior
                self.scaler = scaler

                # Configurar y entrenar modelo con GridSearch
                print("🚀 Entrenando modelo con GridSearch...")
                param_grid = {
                    'criterion': ['gini', 'entropy'],
                    'max_depth': [3, 5, 7, 10, 15],
                    'min_samples_split': [2, 3, 5, 7, 10],
                    'min_samples_leaf': [1, 2, 3, 5, 7],
                    'max_features': ['sqrt', 'log2', None]
                }

                grid_search = GridSearchCV(
                    DecisionTreeClassifier(random_state=42), 
                    param_grid, 
                    cv=5,  # Reducido para mayor velocidad
                    scoring=make_scorer(accuracy_score),
                    n_jobs=1
                )
                
                grid_search.fit(X_train_scaled, y_train)
                self.model = grid_search.best_estimator_
                
                # Guardar datos para uso posterior
                self.X_train = X_train_scaled
                self.X_test = X_test_scaled
                self.y_train = y_train
                self.y_test = y_test
                self.feature_columns = feature_columns

                # Evaluar modelo
                y_pred = self.model.predict(X_test_scaled)
                accuracy = accuracy_score(y_test, y_pred)
                
                print(f"✅ Entrenamiento completado!")
                print(f"🎯 Mejor precisión en validación cruzada: {grid_search.best_score_:.3f}")
                print(f"🎯 Precisión en test: {accuracy:.3f}")
                print(f"⚙️  Mejores parámetros: {grid_search.best_params_}")

                # Graficar el árbol de decisión con tamaño dinámico
                fig, ax = plt.subplots(figsize=(14, 8))
                plot_tree(
                    self.model, 
                    feature_names=[f"F{i}" for i in range(len(feature_columns))],  # Nombres cortos
                    filled=True, 
                    class_names=['Extensión', 'Flexión'],
                    max_depth=3,  # Limitar profundidad para mejor visualización
                    fontsize=8
                )
                plt.title(f"Árbol de Decisión - Precisión: {accuracy:.3f}", fontsize=12, fontweight='bold')
                
                canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

                # Mostrar datos de test en un cuadro de texto
                tk.Label(frame_test, text="Datos de Test Normalizados:", font=("Arial", 12, "bold")).pack(pady=10)
                text_test = tk.Text(frame_test, wrap=tk.NONE, font=("Courier", 8))
                text_test.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar_test_vertical = ttk.Scrollbar(frame_test, orient="vertical", command=text_test.yview)
                scrollbar_test_vertical.pack(side=tk.RIGHT, fill="y")
                scrollbar_test_horizontal = ttk.Scrollbar(frame_test, orient="horizontal", command=text_test.xview)
                scrollbar_test_horizontal.pack(side=tk.BOTTOM, fill="x")
                text_test.configure(yscrollcommand=scrollbar_test_vertical.set, xscrollcommand=scrollbar_test_horizontal.set)
                
                # Crear DataFrame para mostrar
                df_test_display = pd.DataFrame(X_test_scaled, columns=[f"F{i}" for i in range(len(feature_columns))])
                df_test_display["Clase_Real"] = y_test
                df_test_display["Clase_Pred"] = y_pred
                df_test_display["Sujeto"] = suj_test
                
                text_test.insert(tk.END, df_test_display.to_string(index=False, float_format='%.3f'))

                # Mostrar datos de entrenamiento en un cuadro de texto
                tk.Label(frame_train, text="Datos de Entrenamiento Normalizados:", font=("Arial", 12, "bold")).pack(pady=10)
                text_train = tk.Text(frame_train, wrap=tk.NONE, font=("Courier", 8))
                text_train.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar_train_vertical = ttk.Scrollbar(frame_train, orient="vertical", command=text_train.yview)
                scrollbar_train_vertical.pack(side=tk.RIGHT, fill="y")
                scrollbar_train_horizontal = ttk.Scrollbar(frame_train, orient="horizontal", command=text_train.xview)
                scrollbar_train_horizontal.pack(side=tk.BOTTOM, fill="x")
                text_train.configure(yscrollcommand=scrollbar_train_vertical.set, xscrollcommand=scrollbar_train_horizontal.set)
                
                # Crear DataFrame para mostrar
                df_train_display = pd.DataFrame(X_train_scaled, columns=[f"F{i}" for i in range(len(feature_columns))])
                df_train_display["Clase"] = y_train
                df_train_display["Sujeto"] = suj_train
                
                text_train.insert(tk.END, df_train_display.to_string(index=False, float_format='%.3f'))

                # Mostrar métricas detalladas
                from sklearn.metrics import classification_report, confusion_matrix
                report = classification_report(y_test, y_pred)
                conf_matrix = confusion_matrix(y_test, y_pred)
                
                messagebox.showinfo(
                    "Resultados del Entrenamiento", 
                    f"Precisión en validación cruzada: {grid_search.best_score_:.3f}\n"
                    f"Precisión en test: {accuracy:.3f}\n"
                    f"Características utilizadas: {len(feature_columns)}\n"
                    f"Muestras de entrenamiento: {len(X_train)}\n"
                    f"Muestras de test: {len(X_test)}\n\n"
                    f"Mejores parámetros:\n{grid_search.best_params_}"
                )
                
            except Exception as e:
                messagebox.showerror("Error", f"Error durante el entrenamiento: {str(e)}")
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            messagebox.showwarning("Advertencia", "Primero carga un archivo.")

    
    def resultados(self):
        if hasattr(self, 'df') and hasattr(self, 'model') and hasattr(self, 'X_test') and hasattr(self, 'y_test'):
            
            # ==================== FUNCIÓN INTERNA: EVALUAR MÚLTIPLES MODELOS ====================
            def evaluar_modelos_internos():
                """Evalúa múltiples modelos de ML con búsqueda de hiperparámetros"""
                from sklearn.tree import DecisionTreeClassifier
                from sklearn.svm import SVC
                from sklearn.neural_network import MLPClassifier
                from sklearn.model_selection import GridSearchCV
                from sklearn.metrics import accuracy_score

                modelos = {
                    'Decision Tree': {
                        'modelo': DecisionTreeClassifier(random_state=42),
                        'param_grid': {
                            'criterion': ['gini'],
                            'max_depth': [3, 5, 7, 10, 12, 15, 20],
                            'min_samples_split': [2, 5, 10],
                            'min_samples_leaf': [1, 2, 4],
                            'max_features': ['sqrt', 'log2'],
                            'class_weight': [None, 'balanced'],
                            'splitter': ['best']  
                        }
                    },
                    'SVM': {
                        'modelo': SVC(random_state=42),
                        'param_grid': {
                            'C': [0.1, 1, 10],
                            'kernel': ['linear', 'rbf', 'poly'],
                            'gamma': ['scale', 'auto']
                        }
                    },
                    'Neural Network': {
                        'modelo': MLPClassifier(max_iter=1000, random_state=42),
                        'param_grid': {
                            'hidden_layer_sizes': [(50,), (100,), (100, 50)],
                            'activation': ['relu', 'tanh'],
                            'solver': ['adam', 'sgd'],
                            'alpha': [0.0001, 0.001, 0.01]
                        }
                    }
                }

                resultados = {}
                
                # Crear ventana de progreso
                ventana_progreso = tk.Toplevel(self.root)
                ventana_progreso.title("Evaluando Modelos...")
                ventana_progreso.geometry("400x200")
                ventana_progreso.configure(bg="#e6e6e6")
                
                label_progreso = tk.Label(ventana_progreso, text="Iniciando evaluación...", 
                                        font=("Arial", 10), bg="#e6e6e6")
                label_progreso.pack(pady=20)
                
                progress_bar = ttk.Progressbar(ventana_progreso, length=300, mode='determinate')
                progress_bar.pack(pady=10)
                progress_bar['maximum'] = len(modelos)

                for i, (nombre, config) in enumerate(modelos.items()):
                    label_progreso.config(text=f"Evaluando {nombre}...")
                    ventana_progreso.update()
                    
                    grid = GridSearchCV(
                        estimator=config['modelo'],
                        param_grid=config['param_grid'],
                        cv=5,
                        scoring=make_scorer(accuracy_score),
                        n_jobs=1
                    )
                    grid.fit(self.X_train, self.y_train)

                    mejor_modelo = grid.best_estimator_
                    y_pred = mejor_modelo.predict(self.X_test)
                    accuracy = accuracy_score(self.y_test, y_pred)
                    cv_scores = grid.cv_results_['mean_test_score']
                    cv_std = grid.cv_results_['std_test_score']

                    resultados[nombre] = {
                        'modelo': mejor_modelo,
                        'accuracy': accuracy,
                        'cv_mean': grid.best_score_,
                        'cv_std': cv_std[grid.best_index_],
                        'y_pred': y_pred,
                        'mejores_params': grid.best_params_
                    }
                    
                    progress_bar['value'] = i + 1
                    ventana_progreso.update()

                ventana_progreso.destroy()

                # Seleccionar el mejor modelo
                mejor_modelo = max(
                    resultados,
                    key=lambda x: 0.5 * resultados[x]['cv_mean'] + 0.5 * resultados[x]['accuracy']
                )

                return resultados, mejor_modelo

            # ==================== FUNCIÓN INTERNA: EXPORTAR RESULTADOS ====================
            def exportar_resultados_internos():
                try:
                    from tkinter import filedialog
                    archivo = filedialog.asksaveasfilename(
                        defaultextension=".txt",
                        filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")]
                    )
                    if archivo:
                        with open(archivo, 'w', encoding='utf-8') as f:
                            f.write("REPORTE DE RESULTADOS DEL MODELO\n")
                            f.write("="*50 + "\n\n")
                            
                            if evaluar_multiples:
                                f.write(f"MEJOR MODELO ENCONTRADO: {mejor_modelo_nombre}\n")
                                f.write(f"Precisión del mejor modelo: {resultados_modelos[mejor_modelo_nombre]['accuracy']:.4f}\n")
                                f.write(f"Validación cruzada: {resultados_modelos[mejor_modelo_nombre]['cv_mean']:.4f}\n\n")
                                
                                # Métricas del mejor modelo
                                y_pred_mejor = resultados_modelos[mejor_modelo_nombre]['y_pred']
                                precision = precision_score(self.y_test, y_pred_mejor, average='weighted')
                                recall = recall_score(self.y_test, y_pred_mejor, average='weighted')
                                f1 = f1_score(self.y_test, y_pred_mejor, average='weighted')
                                
                                f.write(f"Precision: {precision:.4f}\n")
                                f.write(f"Recall: {recall:.4f}\n")
                                f.write(f"F1-Score: {f1:.4f}\n\n")
                        
                        messagebox.showinfo("Éxito", f"Resultados exportados exitosamente a {archivo}")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al exportar: {str(e)}")

            # ==================== INICIO DEL MÉTODO PRINCIPAL ====================
            
            # Verificar si hay datos de entrenamiento para evaluación completa
            evaluar_multiples = hasattr(self, 'X_train') and hasattr(self, 'y_train')
            
            # Variables para almacenar resultados de evaluación múltiple
            resultados_modelos = None
            mejor_modelo_nombre = None
            
            if evaluar_multiples:
                # Evaluar múltiples modelos
                messagebox.showinfo("Información", "Se evaluarán múltiples modelos. Esto puede tomar unos minutos...")
                resultados_modelos, mejor_modelo_nombre = evaluar_modelos_internos()
            else:
                messagebox.showwarning("Advertencia", "No se encontraron datos de entrenamiento. Solo se mostrará el modelo actual.")
                return
            
            # Crear ventana principal de resultados
            ventana_resultados = tk.Toplevel(self.root)
            ventana_resultados.title("Resultados del Modelo de Machine Learning")
            ventana_resultados.geometry("1400x900")
            ventana_resultados.iconbitmap(os.path.join(ROOT_PATH, "icono.ico"))
            ventana_resultados.configure(bg="#f0f0f0")

            # Notebook para organizar las pestañas
            notebook = ttk.Notebook(ventana_resultados)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # ==================== PESTAÑA 1: COMPARACIÓN DE MODELOS ====================
            frame_comparacion = ttk.Frame(notebook)
            notebook.add(frame_comparacion, text="Comparación de Modelos")
            
            # Frame para resultados de comparación
            frame_comp_superior = tk.Frame(frame_comparacion, bg="#f0f0f0")
            frame_comp_superior.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Texto con resultados de todos los modelos
            tk.Label(frame_comp_superior, text="Resultados de Evaluación de Modelos:", 
                    font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=(0,10))
            
            text_comparacion = tk.Text(frame_comp_superior, wrap=tk.NONE, height=15, width=80)
            text_comparacion.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar_v2 = ttk.Scrollbar(frame_comp_superior, orient="vertical", command=text_comparacion.yview)
            scrollbar_v2.pack(side=tk.RIGHT, fill="y")
            text_comparacion.configure(yscrollcommand=scrollbar_v2.set)
            
            # Insertar resultados de todos los modelos
            text_comparacion.insert(tk.END, f"MEJOR MODELO: {mejor_modelo_nombre}\n")
            text_comparacion.insert(tk.END, "="*60 + "\n\n")
            
            for nombre, resultado in resultados_modelos.items():
                text_comparacion.insert(tk.END, f"MODELO: {nombre}\n")
                text_comparacion.insert(tk.END, "-" * 30 + "\n")
                text_comparacion.insert(tk.END, f"Precisión en Test: {resultado['accuracy']:.4f}\n")
                text_comparacion.insert(tk.END, f"Validación Cruzada: {resultado['cv_mean']:.4f} ± {resultado['cv_std']:.4f}\n")
                text_comparacion.insert(tk.END, f"Mejores Parámetros: {resultado['mejores_params']}\n")
                
                # Agregar reporte de clasificación para cada modelo
                text_comparacion.insert(tk.END, "\nReporte de Clasificación:\n")
                text_comparacion.insert(tk.END, classification_report(self.y_test, resultado['y_pred']))
                text_comparacion.insert(tk.END, "\n" + "="*60 + "\n\n")
            
            # Frame para gráficos de comparación
            frame_graf_comp = tk.Frame(frame_comparacion, bg="#f0f0f0")
            frame_graf_comp.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Gráfico de comparación de modelos
            fig_comp = plt.figure(figsize=(12, 4))
            
            # Subplot 1: Comparación de precisión
            plt.subplot(1, 2, 1)
            modelos_nombres = list(resultados_modelos.keys())
            accuracies = [resultados_modelos[m]['accuracy'] for m in modelos_nombres]
            cv_scores = [resultados_modelos[m]['cv_mean'] for m in modelos_nombres]
            
            x = range(len(modelos_nombres))
            width = 0.35
            
            plt.bar([i - width/2 for i in x], accuracies, width, label='Test Precisión', alpha=0.8, color='skyblue')
            plt.bar([i + width/2 for i in x], cv_scores, width, label='CV Score', alpha=0.8, color='lightcoral')
            
            plt.xlabel('Modelos')
            plt.ylabel('Precisión')
            plt.title('Comparación de Modelos')
            plt.xticks(x, modelos_nombres, rotation=45)
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Agregar valores en las barras
            for i, (acc, cv) in enumerate(zip(accuracies, cv_scores)):
                plt.text(i - width/2, acc + 0.01, f'{acc:.3f}', ha='center', va='bottom', fontsize=8)
                plt.text(i + width/2, cv + 0.01, f'{cv:.3f}', ha='center', va='bottom', fontsize=8)
            
            # Subplot 2: Matriz de confusión del mejor modelo
            plt.subplot(1, 2, 2)
            mejor_y_pred = resultados_modelos[mejor_modelo_nombre]['y_pred']
            cm_mejor = confusion_matrix(self.y_test, mejor_y_pred)
            sns.heatmap(cm_mejor, annot=True, fmt='d', cmap='Greens',
                    xticklabels=['Extensión', 'Flexión'],
                    yticklabels=['Extensión', 'Flexión'])
            plt.title(f'Matriz de Confusión - {mejor_modelo_nombre}')
            plt.xlabel('Predicho')
            plt.ylabel('Real')
            
            plt.tight_layout()
            canvas_comp = FigureCanvasTkAgg(fig_comp, master=frame_graf_comp)
            canvas_comp.draw()
            canvas_comp.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # ==================== PESTAÑA 2: PREDICCIONES ====================
            frame_predicciones = ttk.Frame(notebook)
            notebook.add(frame_predicciones, text="Predicciones")

            # Frame principal con scrollbar
            frame_pred_main = tk.Frame(frame_predicciones, bg="#f0f0f0")
            frame_pred_main.pack(fill=tk.BOTH, expand=True)

            canvas_pred = tk.Canvas(frame_pred_main, bg="#f0f0f0")
            scrollbar_pred = ttk.Scrollbar(frame_pred_main, orient="vertical", command=canvas_pred.yview)
            scrollable_frame_pred = tk.Frame(canvas_pred, bg="#f0f0f0")

            scrollable_frame_pred.bind(
                "<Configure>",
                lambda e: canvas_pred.configure(
                    scrollregion=canvas_pred.bbox("all")
                )
            )

            canvas_pred.create_window((0, 0), window=scrollable_frame_pred, anchor="nw")
            canvas_pred.configure(yscrollcommand=scrollbar_pred.set)

            canvas_pred.pack(side="left", fill="both", expand=True)
            scrollbar_pred.pack(side="right", fill="y")

            # Contenido de la pestaña
            frame_pred_content = tk.Frame(scrollable_frame_pred, bg="#f0f0f0")
            frame_pred_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Título
            tk.Label(frame_pred_content, 
                    text=f"Predicciones del Modelo: {mejor_modelo_nombre}", 
                    font=("Arial", 14, "bold"), 
                    bg="#f0f0f0").pack(pady=(0, 20))

            # ==================== GRÁFICO DE BARRAS PRINCIPAL (VERSIÓN ROBUSTA) ====================
            frame_grafico_principal = tk.Frame(frame_pred_content, bg="#f0f0f0")
            frame_grafico_principal.pack(fill=tk.BOTH, expand=True, pady=10)

            try:
                fig_pred = plt.figure(figsize=(12, 6), dpi=100)
                ax = fig_pred.add_subplot(111)

                # 1. DETECCIÓN Y NORMALIZACIÓN DE ETIQUETAS (VERSIÓN ROBUSTA)
                if isinstance(self.y_test[0], str):
                    # Mapeo que admite múltiples variantes
                    label_map = {
                        'flexión': 13, 'flexion': 13, 'flx': 13,
                        'extensión': 14, 'extension': 14, 'ext': 14
                    }
                    
                    # Función para normalizar etiquetas
                    def normalizar_etiqueta(label):
                        label = label.strip().lower()
                        if 'flex' in label or 'flx' in label: return 'flexión'
                        if 'exten' in label or 'ext' in label: return 'extensión'
                        return label
                    
                    # Conversión segura con manejo de errores
                    try:
                        y_test_num = np.array([label_map[normalizar_etiqueta(label)] for label in self.y_test])
                        y_pred_num = np.array([label_map[normalizar_etiqueta(label)] for label in mejor_y_pred])
                        categorias = ['Flexión', 'Extensión']  # Formato consistente para visualización
                        
                        # Verificación de etiquetas no reconocidas
                        etiquetas_unicas = set(normalizar_etiqueta(label) for label in self.y_test)
                        if not all(etq in label_map for etq in etiquetas_unicas):
                            raise ValueError(f"Etiquetas no reconocidas: {etiquetas_unicas - set(label_map.keys())}")
                            
                    except KeyError as e:
                        raise ValueError(f"Error en formato de etiquetas. Asegúrese que sean 'Flexión' o 'Extensión' (variantes aceptadas)")
                else:
                    # Versión original para números
                    categorias = ['Flexión', 'Extensión']
                    y_test_num = self.y_test
                    y_pred_num = mejor_y_pred

                # Cálculo de aciertos y errores
                aciertos = [
                    np.sum((y_test_num == 13) & (y_pred_num == 13)),
                    np.sum((y_test_num == 14) & (y_pred_num == 14))
                ]
                errores = [
                    np.sum((y_test_num == 13) & (y_pred_num == 14)),
                    np.sum((y_test_num == 14) & (y_pred_num == 13))
                ]

                # Configuración del gráfico
                bar_width = 0.6
                index = np.arange(len(categorias))

                bar_aciertos = ax.bar(index, aciertos, bar_width, 
                                    label='Aciertos', color='#4CAF50', edgecolor='white')
                bar_errores = ax.bar(index, errores, bar_width, 
                                    bottom=aciertos, label='Errores', color='#F44336', edgecolor='white')

                # Personalización del gráfico
                ax.set_xlabel('Movimiento', fontsize=12)
                ax.set_ylabel('Cantidad de Muestras', fontsize=12)
                ax.set_title('Distribución de Aciertos y Errores por Clase', fontsize=14, pad=20)
                ax.set_xticks(index)
                ax.set_xticklabels(categorias, fontsize=12)
                ax.legend(fontsize=12)
                ax.grid(axis='y', alpha=0.3)

                # Mostrar valores en las barras
                for rect in bar_aciertos + bar_errores:
                    height = rect.get_height()
                    bottom = rect.get_y()
                    ax.annotate(f'{int(height)}',
                            xy=(rect.get_x() + rect.get_width() / 2, bottom + height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', fontsize=11)

                # Mostrar porcentajes de precisión
                total_muestras = len(self.y_test)
                for i, (cat, acc, err) in enumerate(zip(categorias, aciertos, errores)):
                    porcentaje_acierto = (acc / (acc + err)) * 100 if (acc + err) > 0 else 0
                    ax.text(i, acc + err + 0.05*total_muestras, 
                        f'{porcentaje_acierto:.1f}% de precisión', 
                        ha='center', va='bottom', fontsize=12, color='black')

                canvas_pred_fig = FigureCanvasTkAgg(fig_pred, master=frame_grafico_principal)
                canvas_pred_fig.draw()
                canvas_pred_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)


                # ==================== ESTADÍSTICAS DETALLADAS ====================
                frame_estadisticas = tk.Frame(frame_pred_content, bg="#f0f0f0")
                frame_estadisticas.pack(fill=tk.X, pady=(20, 10))

                # Cálculo de métricas
                accuracy = accuracy_score(y_test_num, y_pred_num)
                precision = precision_score(y_test_num, y_pred_num, average='weighted')
                recall = recall_score(y_test_num, y_pred_num, average='weighted')
                f1 = f1_score(y_test_num, y_pred_num, average='weighted')

                stats_text = (f"• Precisión General (accuracy_score): {accuracy:.2%}\n"
                            f"• Precisión (Precision): {precision:.2%}\n"
                            f"• Sensibilidad (Recall): {recall:.2%}\n"
                            f"• F1-Score: {f1:.2%}\n"
                            f"• Total Muestras: {total_muestras}\n"
                            f"• Aciertos Totales: {sum(aciertos)}\n"
                            f"• Errores Totales: {sum(errores)}")

                tk.Label(frame_estadisticas, 
                        text="Estadísticas Detalladas:", 
                        font=("Arial", 12, "bold"), 
                        bg="#f0f0f0").pack(anchor='w')

                tk.Label(frame_estadisticas, 
                        text=stats_text, 
                        font=("Arial", 11), 
                        bg="#f0f0f0", 
                        justify='left').pack(anchor='w', padx=20)

                # ==================== MATRIZ DE CONFUSIÓN ====================
                frame_matriz = tk.Frame(frame_pred_content, bg="#f0f0f0")
                frame_matriz.pack(fill=tk.BOTH, expand=True, pady=(10, 20))

                fig_matriz = plt.figure(figsize=(8, 6), dpi=100)
                ax_matriz = fig_matriz.add_subplot(111)

                cm = confusion_matrix(y_test_num, y_pred_num)
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                        xticklabels=categorias, 
                        yticklabels=categorias,
                        ax=ax_matriz)

                ax_matriz.set_title('Matriz de Confusión', fontsize=14, pad=15)
                ax_matriz.set_xlabel('Predicciones', fontsize=12)
                ax_matriz.set_ylabel('Valores Reales', fontsize=12)

                canvas_matriz = FigureCanvasTkAgg(fig_matriz, master=frame_matriz)
                canvas_matriz.draw()
                canvas_matriz.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            except Exception as e:
                # Manejo de errores con interfaz amigable
                error_frame = tk.Frame(frame_pred_content, bg="#f0f0f0")
                error_frame.pack(fill=tk.X, pady=20)
                
                tk.Label(error_frame, 
                        text="Error al procesar las predicciones", 
                        fg="red", font=("Arial", 12, "bold"), 
                        bg="#f0f0f0").pack()
                
                tk.Label(error_frame, 
                        text=str(e), 
                        font=("Arial", 11), 
                        bg="#f0f0f0").pack()
                
                tk.Label(error_frame, 
                        text="Revise el formato de sus etiquetas (deben ser 'Flexión' o 'Extensión' o variantes)", 
                        font=("Arial", 11), 
                        bg="#f0f0f0").pack()


        else:
            messagebox.showwarning("Advertencia", "Primero carga un archivo y ejecuta la prueba.")



if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazApp(root)
    root.mainloop()
