import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from config_manager import ConfigManager

class SettingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicación de Gestión de Configuración")
        self.root.geometry("500x550")

        # Instancia del gestor de archivos
        self.config_manager = ConfigManager()
        self.current_config = self.config_manager.cargar_configuracion()

        self._crear_menu_principal()
        self._aplicar_estilos_iniciales()

    def _crear_menu_principal(self):
        """Crea la barra de menú con subopciones simuladas y Settings funcional."""
        barra_menu = tk.Menu(self.root)

        # Subopciones simuladas (exigidas por el proyecto)
        menu_archivo = tk.Menu(barra_menu, tearoff=0)
        menu_archivo.add_command(label="Nuevo (Simulado)", state="disabled")
        menu_archivo.add_command(label="Abrir (Simulado)", state="disabled")
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)

        menu_edicion = tk.Menu(barra_menu, tearoff=0)
        menu_edicion.add_command(label="Deshacer (Simulado)", state="disabled")
        barra_menu.add_cascade(label="Edición", menu=menu_edicion)

        menu_ver = tk.Menu(barra_menu, tearoff=0)
        menu_ver.add_command(label="Zoom (Simulado)", state="disabled")
        barra_menu.add_cascade(label="Ver", menu=menu_ver)

        # Menú Settings (Funcional)
        menu_settings = tk.Menu(barra_menu, tearoff=0)
        menu_settings.add_command(label="Configuración de Usuario", command=self.abrir_ventana_settings)
        barra_menu.add_cascade(label="Settings", menu=menu_settings)

        self.root.config(menu=barra_menu)

    def _aplicar_estilos_iniciales(self):
        """Aplica la configuración cargada a la interfaz."""
        try:
            self.root.configure(bg=self.current_config.get("color_menu", "#2C3E50"))
        except tk.TclError:
            self.root.configure(bg="#2C3E50")

    def abrir_ventana_settings(self):
        """Ventana emergente para editar los 7 parámetros de configuración."""
        ventana_win = tk.Toplevel(self.root)
        ventana_win.title("Settings - Configuración de Usuario")
        ventana_win.geometry("450x500")
        ventana_win.grab_set()

        # 1. Nombre de usuario
        tk.Label(ventana_win, text="Nombre de Usuario:").pack(anchor="w", padx=20, pady=2)
        entry_usuario = tk.Entry(ventana_win)
        entry_usuario.insert(0, self.current_config.get("nombre_usuario", ""))
        entry_usuario.pack(fill="x", padx=20, pady=2)

        # 2. Tema
        tk.Label(ventana_win, text="Tema de Interfaz:").pack(anchor="w", padx=20, pady=2)
        combo_tema = ttk.Combobox(ventana_win, values=["claro", "oscuro"], state="readonly")
        combo_tema.set(self.current_config.get("tema", "claro"))
        combo_tema.pack(fill="x", padx=20, pady=2)

        # 3. Idioma
        tk.Label(ventana_win, text="Idioma:").pack(anchor="w", padx=20, pady=2)
        combo_idioma = ttk.Combobox(ventana_win, values=["es", "es-ES", "en", "en-US"], state="readonly")
        combo_idioma.set(self.current_config.get("idioma", "es-ES"))
        combo_idioma.pack(fill="x", padx=20, pady=2)

        # 4. Tamaño de fuente
        tk.Label(ventana_win, text="Tamaño de Fuente:").pack(anchor="w", padx=20, pady=2)
        spin_fuente = tk.Spinbox(ventana_win, from_=8, to=48)
        spin_fuente.delete(0, "end")
        spin_fuente.insert(0, self.current_config.get("tamano_fuente", "12"))
        spin_fuente.pack(fill="x", padx=20, pady=2)

        # Variables de color y foto
        color_menu_var = tk.StringVar(value=self.current_config.get("color_menu", "#2C3E50"))
        color_letra_var = tk.StringVar(value=self.current_config.get("color_letra", "#333333"))
        foto_perfil_var = tk.StringVar(value=self.current_config.get("foto_perfil", "default.png"))

        # Selectores de Color y Archivos (5, 6 y 7)
        def seleccionar_color_menu():
            color = colorchooser.askcolor(title="Seleccionar Color de Menú")[1]
            if color:
                color_menu_var.set(color)

        def seleccionar_color_letra():
            color = colorchooser.askcolor(title="Seleccionar Color de Letra")[1]
            if color:
                color_letra_var.set(color)

        def seleccionar_foto():
            filepath = filedialog.askopenfilename(
                title="Seleccionar Foto de Perfil",
                filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp")]
            )
            if filepath:
                foto_perfil_var.set(filepath)

        frame_btns = tk.Frame(ventana_win)
        frame_btns.pack(fill="x", padx=20, pady=10)

        tk.Button(frame_btns, text="Color Menú", command=seleccionar_color_menu).grid(row=0, column=0, padx=5)
        tk.Button(frame_btns, text="Color Letra", command=seleccionar_color_letra).grid(row=0, column=1, padx=5)
        tk.Button(frame_btns, text="Seleccionar Foto", command=seleccionar_foto).grid(row=0, column=2, padx=5)

        # Guardar cambios
        def guardar():
            nueva_config = {
                "nombre_usuario": entry_usuario.get(),
                "tema": combo_tema.get(),
                "idioma": combo_idioma.get(),
                "tamano_fuente": spin_fuente.get(),
                "color_menu": color_menu_var.get(),
                "color_letra": color_letra_var.get(),
                "foto_perfil": foto_perfil_var.get()
            }
            
            éxito = self.config_manager.guardar_configuracion(nueva_config)
            if éxito:
                self.current_config = nueva_config
                self._aplicar_estilos_iniciales()
                messagebox.showinfo("Éxito", "Configuración guardada correctamente (.tmp -> .bak).")
                ventana_win.destroy()
            else:
                messagebox.showerror("Error", "No se pudo guardar la configuración en el archivo.")

        tk.Button(ventana_win, text="Guardar Configuración", bg="#27AE60", fg="white", command=guardar).pack(pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = SettingsApp(root)
    root.mainloop()