import csv # Módulo para leer y escribir archivos CSV de manera sencilla
import os # Módulo para interactuar con el sistema operativo (verificar existencia de archivos, permisos, etc.)
import shutil # Módulo para operaciones de alto nivel con archivos y directorios (copiar, mover, eliminar, etc.)

# Clase encargada de administrar la lectura y escritura del archivo de configuración
class ConfigManager:
    
    # Valores por defecto que usa la aplicación si el archivo no existe o se daña
    DEFAULT_CONFIG = {
        "nombre_usuario": "Usuario_Default",
        "tema": "claro",
        "idioma": "es-ES",
        "tamano_fuente": "12",
        "color_menu": "#2C3E50",
        "color_letra": "#333333",
        "foto_perfil": "default.png"
    }

    # Lista con los nombres exactos de los campos que deben existir en el archivo CSV
    FIELDS = [
        "nombre_usuario", "tema", "idioma", 
        "tamano_fuente", "color_menu", "color_letra", "foto_perfil"
    ]

    # Preparamos los nombres y extensiones de los tres archivos que va a manejar el sistema
    def __init__(self, filepath="config.csv"):
        self.filepath = filepath
        self.tmp_filepath = f"{filepath}.tmp"  # Archivo borrador o borrador temporal
        self.bak_filepath = f"{filepath}.bak"  # Archivo de copia de seguridad (respaldo)

    # Función para leer la configuración guardada en el disco
    def cargar_configuracion(self):
        
        # CASO 1: Si el archivo no existe todavía en la carpeta, creamos uno con los valores por defecto
        if not os.path.exists(self.filepath):
            print("[INFO] Archivo de configuración ausente. Usando valores por defecto.")
            self.guardar_configuracion(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

        try:
            # Abrimos el archivo en modo lectura usando utf-8 para que lea tildes y eñes sin problemas
            with open(self.filepath, mode="r", encoding="utf-8") as file:
                # Usamos el separador '|' para leer las columnas del CSV como un diccionario
                reader = csv.DictReader(file, delimiter="|")
                filas = list(reader)

                # CASO 2: Si el archivo está completamente vacío, forzamos un error para restaurarlo
                if not filas or len(filas) == 0:
                    raise ValueError("El archivo CSV está vacío o sin registros.")
                
                datos = filas[0]
                
                # Revisamos que la fila leída tenga todas las llaves requeridas
                for field in self.FIELDS:
                    if field not in datos or datos[field] is None:
                        raise ValueError(f"Falta el campo requerido: {field}")

                # Comprobamos que el tamaño de fuente realmente sea un número convertible
                try:
                    int(datos["tamano_fuente"])
                except ValueError:
                    raise ValueError("El tamaño de fuente debe ser un número entero válido.")

                print("[ÉXITO] Configuración cargada correctamente desde el archivo CSV.")
                return datos

        # CASO 3: Si Windows o el sistema operativo prohíben leer el archivo (sin permisos)
        except (PermissionError, OSError) as e:
            print(f"[ERROR] Error de permisos o acceso al leer ({e}). Usando defaults.")
            return self.DEFAULT_CONFIG.copy()

        # CASO 2 (Continuación): Si el archivo está roto, alterado o le faltan partes, cargamos defaults
        except (ValueError, csv.Error) as e:
            print(f"[ERROR] Archivo corrupto o inválido ({e}). Restaurando defaults.")
            return self.DEFAULT_CONFIG.copy()

    # Función para guardar la nueva configuración de forma segura en el disco
    def guardar_configuracion(self, config_dict):
        try:
            # PASO 1: Si ya existe un archivo config.csv, le sacamos una copia de respaldo (.bak) por seguridad
            if os.path.exists(self.filepath):
                shutil.copy2(self.filepath, self.bak_filepath)

            # PASO 2: Escribimos los nuevos datos primero en un archivo borrador (.tmp)
            with open(self.tmp_filepath, mode="w", newline="", encoding="utf-8") as tmp_file:
                writer = csv.DictWriter(tmp_file, fieldnames=self.FIELDS, delimiter="|")
                writer.writeheader()  # Escribe la primera fila con los títulos
                writer.writerow(config_dict)  # Escribe la fila de datos
                
                # Forzamos a Python y al sistema a volcar los datos pendientes directamente al disco físico
                tmp_file.flush()
                os.fsync(tmp_file.fileno())

            # PASO 3: Reemplazamos el archivo borrador (.tmp) por el oficial (config.csv) en un solo paso instantáneo
            os.replace(self.tmp_filepath, self.filepath)
            print("[ÉXITO] Configuración guardada de forma segura mediante .tmp y .bak.")
            return True

        # Si no se pudo guardar por falta de permisos o fallos del disco
        except (PermissionError, OSError) as e:
            print(f"[ERROR] No se pudo guardar la configuración por permisos o E/S: {e}")
            # Limpiamos y borramos el borrador incompleto para no dejar basura
            if os.path.exists(self.tmp_filepath):
                try:
                    os.remove(self.tmp_filepath)
                except Exception:
                    pass
            return False

    # Función para recuperar los datos desde la copia de respaldo .bak si fuera necesario
    def restaurar_desde_respaldo(self):
        if os.path.exists(self.bak_filepath):
            shutil.copy2(self.bak_filepath, self.filepath)
            print("[INFO] Configuración restaurada exitosamente desde .bak.")
            return True
        print("[ERROR] No existe archivo de respaldo .bak para restaurar.")
        return False