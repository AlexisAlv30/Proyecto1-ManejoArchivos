import csv
import os
import shutil

class ConfigManager:
    """
    Gestiona la persistencia de configuración de usuario utilizando el formato CSV.
    Implementa guardado atómico (.tmp), respaldos (.bak) y manejo robusto de errores.
    """
    
    DEFAULT_CONFIG = {
        "nombre_usuario": "Usuario_Default",
        "tema": "claro",
        "idioma": "es-ES",
        "tamano_fuente": "12",
        "color_menu": "#2C3E50",
        "color_letra": "#333333",
        "foto_perfil": "default.png"
    }

    FIELDS = [
        "nombre_usuario", "tema", "idioma", 
        "tamano_fuente", "color_menu", "color_letra", "foto_perfil"
    ]

    def __init__(self, filepath="config.csv"):
        self.filepath = filepath
        self.tmp_filepath = f"{filepath}.tmp"
        self.bak_filepath = f"{filepath}.bak"

    def cargar_configuracion(self):
        """
        Lee la configuración desde el archivo CSV con UTF-8.
        Si el archivo no existe, está corrupto o carece de permisos, 
        degrada a los valores por defecto sin lanzar excepciones no controladas.
        """
        # Caso 1: Archivo ausente
        if not os.path.exists(self.filepath):
            print("[INFO] Archivo de configuración ausente. Usando valores por defecto.")
            self.guardar_configuracion(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.filepath, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file, delimiter="|")
                filas = list(reader)

                # Caso 2: Archivo corrupto o vacío
                if not filas or len(filas) == 0:
                    raise ValueError("El archivo CSV está vacío o sin registros.")
                
                datos = filas[0]
                
                # Validar que contenga todos los campos requeridos
                for field in self.FIELDS:
                    if field not in datos or datos[field] is None:
                        raise ValueError(f"Falta el campo requerido: {field}")

                try:
                    int(datos["tamano_fuente"])
                except ValueError:
                    raise ValueError("El tamaño de fuente debe ser un número entero válido.")

                print("[ÉXITO] Configuración cargada correctamente desde el archivo CSV.")
                return datos

        except (PermissionError, OSError) as e:
            # Caso 3: Sin permisos de lectura o error de E/S
            print(f"[ERROR] Error de permisos o acceso al leer ({e}). Usando defaults.")
            return self.DEFAULT_CONFIG.copy()

        except (ValueError, csv.Error) as e:
            # Caso 2: Error de formato/corrupción
            print(f"[ERROR] Archivo corrupto o inválido ({e}). Restaurando defaults.")
            return self.DEFAULT_CONFIG.copy()

    def guardar_configuracion(self, config_dict):
        """
        Guarda la configuración con escritura segura:
        1. Crea respaldo (.bak) del archivo previo si existe.
        2. Escribe en archivo temporal (.tmp).
        3. Reemplaza el archivo final con el temporal.
        """
        try:
            # Step 1: Respaldo (Backup)
            if os.path.exists(self.filepath):
                shutil.copy2(self.filepath, self.bak_filepath)

            # Step 2: Escritura segura en archivo temporal
            with open(self.tmp_filepath, mode="w", newline="", encoding="utf-8") as tmp_file:
                writer = csv.DictWriter(tmp_file, fieldnames=self.FIELDS, delimiter="|")
                writer.writeheader()
                writer.writerow(config_dict)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())  # Fuerza el guardado físico a disco

            # Step 3: Reemplazo atómico
            os.replace(self.tmp_filepath, self.filepath)
            print("[ÉXITO] Configuración guardada de forma segura mediante .tmp y .bak.")
            return True

        except (PermissionError, OSError) as e:
            print(f"[ERROR] No se pudo guardar la configuración por permisos o E/S: {e}")
            if os.path.exists(self.tmp_filepath):
                try:
                    os.remove(self.tmp_filepath)
                except Exception:
                    pass
            return False