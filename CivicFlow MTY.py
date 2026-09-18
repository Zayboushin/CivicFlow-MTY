#!/usr/bin/env python3
"""
CivicFlow MTY - Prototipo con interfaz gráfica (Tkinter)
=========================================================

Misma lógica que civicflow_bot.py (registro de problemáticas, folio único
MTY-XXXX, seguimiento de estatus Nuevo -> En Proceso -> Canalizado -> Atendido)
pero con una ventana de escritorio en lugar de un menú de terminal.

No requiere instalar nada adicional: usa Tkinter, incluido en la instalación
estándar de Python. (En algunas distribuciones de Linux hace falta instalar
el paquete del sistema "python3-tk"; en Windows y macOS ya viene incluido.)

Uso:
    python3 civicflow_bot_gui.py
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuración y persistencia (mismo formato que la versión de terminal)
# ---------------------------------------------------------------------------

DATA_FILE = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "reportes.json")

CATEGORIAS = [
    "Alumbrado público",
    "Baches y pavimentación",
    "Mantenimiento de parques",
    "Otro",
]

ESTATUS_FLUJO = ["Nuevo", "En Proceso", "Canalizado", "Atendido"]

ESTATUS_COLOR = {
    "Nuevo": "#f5c518",       # amarillo
    "En Proceso": "#2e86de",  # azul
    "Canalizado": "#e67e22",  # naranja
    "Atendido": "#27ae60",    # verde
}

# Paleta general de la app (inspirada en la identidad azul de CivicFlow MTY)
COLOR_FONDO = "#eef2f8"
COLOR_HEADER = "#3d5a80"
COLOR_HEADER_TEXTO = "#ffffff"
COLOR_ACENTO = "#2e86de"


def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"ultimo_folio": 1000, "reportes": []}


def guardar_datos(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ---------------------------------------------------------------------------
# Aplicación principal
# ---------------------------------------------------------------------------

class CivicFlowApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CivicFlow MTY - 7ma Regiduría")
        self.geometry("880x600")
        self.configure(bg=COLOR_FONDO)
        self.minsize(760, 520)

        self.data = cargar_datos()

        self._construir_header()
        self._construir_tabs()
        self._refrescar_panel()

    # -- Encabezado -----------------------------------------------------

    def _construir_header(self):
        header = tk.Frame(self, bg=COLOR_HEADER, height=70)
        header.pack(side="top", fill="x")

        tk.Label(
            header,
            text="CivicFlow MTY",
            bg=COLOR_HEADER,
            fg=COLOR_HEADER_TEXTO,
            font=("Segoe UI", 20, "bold"),
        ).pack(side="left", padx=20, pady=10)

        tk.Label(
            header,
            text="Registro y seguimiento de problemáticas — 7ma Regiduría del Cabildo de Monterrey",
            bg=COLOR_HEADER,
            fg="#d6e4f0",
            font=("Segoe UI", 10),
        ).pack(side="left", padx=5, pady=10)

    # -- Pestañas ---------------------------------------------------------

    def _construir_tabs(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TNotebook.Tab", font=(
            "Segoe UI", 10, "bold"), padding=[14, 8])
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_reportar = tk.Frame(self.tabs, bg=COLOR_FONDO)
        self.tab_consultar = tk.Frame(self.tabs, bg=COLOR_FONDO)
        self.tab_panel = tk.Frame(self.tabs, bg=COLOR_FONDO)

        self.tabs.add(self.tab_reportar, text="📝 Reportar problemática")
        self.tabs.add(self.tab_consultar, text="🔍 Consultar folio")
        self.tabs.add(self.tab_panel, text="📊 Panel de administración")

        self._construir_tab_reportar()
        self._construir_tab_consultar()
        self._construir_tab_panel()

    # -- Tab 1: Reportar --------------------------------------------------

    def _construir_tab_reportar(self):
        # Contenedor externo que centra la tarjeta tanto vertical como
        # horizontalmente dentro de la pestaña.
        contenedor = tk.Frame(self.tab_reportar, bg=COLOR_FONDO)
        contenedor.pack(expand=True)

        card = tk.Frame(
            contenedor, bg="white", bd=1, relief="solid", padx=40, pady=30
        )
        card.pack()

        tk.Label(
            card,
            text="¿Qué problema deseas reportar?",
            bg="white",
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="n", pady=(0, 20))

        etiqueta_kwargs = dict(bg="white", font=("Segoe UI", 10), anchor="e")

        tk.Label(card, text="Categoría:", **etiqueta_kwargs).grid(
            row=1, column=0, sticky="e", pady=6, padx=(0, 10)
        )
        self.var_categoria = tk.StringVar(value=CATEGORIAS[0])
        ttk.Combobox(
            card,
            textvariable=self.var_categoria,
            values=CATEGORIAS,
            state="readonly",
            width=35,
            justify="left",
        ).grid(row=1, column=1, sticky="w", pady=6)

        tk.Label(card, text="Descripción:", **etiqueta_kwargs).grid(
            row=2, column=0, sticky="ne", pady=6, padx=(0, 10)
        )
        self.txt_descripcion = tk.Text(
            card, width=40, height=4, font=("Segoe UI", 10))
        self.txt_descripcion.grid(row=2, column=1, sticky="w", pady=6)

        tk.Label(card, text="Ubicación:", **etiqueta_kwargs).grid(
            row=3, column=0, sticky="e", pady=6, padx=(0, 10)
        )
        self.entry_ubicacion = tk.Entry(card, width=43, font=("Segoe UI", 10))
        self.entry_ubicacion.grid(row=3, column=1, sticky="w", pady=6)

        tk.Label(card, text="Foto de evidencia:", **etiqueta_kwargs).grid(
            row=4, column=0, sticky="e", pady=6, padx=(0, 10)
        )
        self.entry_foto = tk.Entry(card, width=43, font=("Segoe UI", 10))
        self.entry_foto.grid(row=4, column=1, sticky="w", pady=6)
        tk.Label(
            card,
            text="(opcional, escribe el nombre del archivo simulando el adjunto)",
            bg="white",
            fg="#666666",
            font=("Segoe UI", 8),
        ).grid(row=5, column=1, sticky="w")

        self.var_anonimo = tk.BooleanVar(value=False)
        tk.Checkbutton(
            card,
            text="Enviar como reporte anónimo",
            variable=self.var_anonimo,
            bg="white",
            font=("Segoe UI", 10),
            command=self._toggle_contacto,
        ).grid(row=6, column=1, sticky="w", pady=(14, 6))

        tk.Label(card, text="Contacto:", **etiqueta_kwargs).grid(
            row=7, column=0, sticky="e", pady=6, padx=(0, 10)
        )
        self.entry_contacto = tk.Entry(card, width=43, font=("Segoe UI", 10))
        self.entry_contacto.grid(row=7, column=1, sticky="w", pady=6)

        btn = tk.Button(
            card,
            text="Enviar reporte",
            bg=COLOR_ACENTO,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            command=self._enviar_reporte,
        )
        btn.grid(row=8, column=0, columnspan=2, pady=(24, 6))

        self.lbl_confirmacion = tk.Label(
            card, text="", bg="white", fg="#1e7d32", font=("Segoe UI", 11, "bold")
        )
        self.lbl_confirmacion.grid(row=9, column=0, columnspan=2)

    def _toggle_contacto(self):
        if self.var_anonimo.get():
            self.entry_contacto.delete(0, tk.END)
            self.entry_contacto.config(state="disabled")
        else:
            self.entry_contacto.config(state="normal")

    def _enviar_reporte(self):
        categoria = self.var_categoria.get()
        descripcion = self.txt_descripcion.get("1.0", tk.END).strip()
        ubicacion = self.entry_ubicacion.get().strip()
        foto = self.entry_foto.get().strip() or None
        anonimo = self.var_anonimo.get()
        contacto = None if anonimo else (
            self.entry_contacto.get().strip() or None)

        if not descripcion or not ubicacion:
            messagebox.showwarning(
                "Faltan datos", "Por favor describe el problema e indica la ubicación."
            )
            return

        self.data["ultimo_folio"] += 1
        folio = f"MTY-{self.data['ultimo_folio']}"

        reporte = {
            "folio": folio,
            "categoria": categoria,
            "descripcion": descripcion,
            "ubicacion": ubicacion,
            "foto": foto,
            "anonimo": anonimo,
            "contacto": contacto,
            "estatus": ESTATUS_FLUJO[0],
            "historial": [{"estatus": ESTATUS_FLUJO[0], "fecha": ahora()}],
            "fecha_registro": ahora(),
        }
        self.data["reportes"].append(reporte)
        guardar_datos(self.data)

        self.lbl_confirmacion.config(
            text=f"✔ ¡Gracias! Tu reporte fue registrado con el folio #{folio}."
        )

        # Limpiar formulario
        self.txt_descripcion.delete("1.0", tk.END)
        self.entry_ubicacion.delete(0, tk.END)
        self.entry_foto.delete(0, tk.END)
        self.entry_contacto.delete(0, tk.END)
        self.var_anonimo.set(False)
        self.entry_contacto.config(state="normal")

        self._refrescar_panel()

    # -- Tab 2: Consultar folio --------------------------------------------

    def _construir_tab_consultar(self):
        frame = tk.Frame(self.tab_consultar, bg=COLOR_FONDO)
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(
            frame, text="Consulta el avance de tu reporte", bg=COLOR_FONDO,
            font=("Segoe UI", 13, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        tk.Label(frame, text="Folio (ej. MTY-1001):", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(
            row=1, column=0, sticky="w"
        )
        self.entry_folio_buscar = tk.Entry(
            frame, width=25, font=("Segoe UI", 10))
        self.entry_folio_buscar.grid(row=1, column=1, sticky="w", padx=8)
        self.entry_folio_buscar.bind(
            "<Return>", lambda e: self._buscar_folio())

        tk.Button(
            frame,
            text="Buscar",
            bg=COLOR_ACENTO,
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            command=self._buscar_folio,
        ).grid(row=1, column=2, sticky="w")

        self.resultado_frame = tk.Frame(
            frame, bg="white", bd=1, relief="solid")
        self.resultado_frame.grid(
            row=2, column=0, columnspan=3, sticky="nsew", pady=20)
        frame.grid_columnconfigure(2, weight=1)

        self.lbl_resultado_vacio = tk.Label(
            self.resultado_frame,
            text="Ingresa un folio para ver su estatus e historial.",
            bg="white",
            fg="#888888",
            font=("Segoe UI", 10),
            padx=16,
            pady=16,
        )
        self.lbl_resultado_vacio.pack()

    def _buscar_folio(self):
        folio = self.entry_folio_buscar.get().strip().upper().replace("#", "")
        if not folio:
            return
        if not folio.startswith("MTY-"):
            folio = f"MTY-{folio}"

        for widget in self.resultado_frame.winfo_children():
            widget.destroy()

        reporte = next(
            (r for r in self.data["reportes"] if r["folio"] == folio), None)

        if not reporte:
            tk.Label(
                self.resultado_frame,
                text=f"No se encontró ningún reporte con folio '{folio}'.",
                bg="white",
                fg="#c0392b",
                font=("Segoe UI", 10),
                padx=16,
                pady=16,
            ).pack(anchor="w")
            return

        info = tk.Frame(self.resultado_frame, bg="white")
        info.pack(fill="x", padx=16, pady=16, anchor="w")

        color = ESTATUS_COLOR.get(reporte["estatus"], "#999999")
        tk.Label(
            info, text=f"Folio #{reporte['folio']}", bg="white",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w")

        badge = tk.Label(
            info,
            text=reporte["estatus"],
            bg=color,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=3,
        )
        badge.pack(anchor="w", pady=(4, 10))

        campos = [
            ("Categoría", reporte["categoria"]),
            ("Descripción", reporte["descripcion"]),
            ("Ubicación", reporte["ubicacion"]),
            ("Anónimo", "Sí" if reporte["anonimo"] else "No"),
            ("Registrado", reporte["fecha_registro"]),
        ]
        for etiqueta, valor in campos:
            tk.Label(
                info, text=f"{etiqueta}: {valor}", bg="white", font=("Segoe UI", 10),
                anchor="w", justify="left", wraplength=600,
            ).pack(anchor="w", pady=2)

        tk.Label(
            info, text="Historial de avance:", bg="white",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(12, 4))

        for paso in reporte["historial"]:
            tk.Label(
                info,
                text=f"  •  {paso['fecha']}   →   {paso['estatus']}",
                bg="white",
                font=("Segoe UI", 9),
            ).pack(anchor="w")

    # -- Tab 3: Panel de administración -------------------------------------

    def _construir_tab_panel(self):
        frame = tk.Frame(self.tab_panel, bg=COLOR_FONDO)
        frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Resumen (tarjetas de conteo por estatus)
        self.resumen_frame = tk.Frame(frame, bg=COLOR_FONDO)
        self.resumen_frame.pack(fill="x", pady=(0, 12))

        # Tabla de reportes
        columnas = ("folio", "categoria", "ubicacion", "fecha", "estatus")
        self.tree = ttk.Treeview(
            frame, columns=columnas, show="headings", height=14)
        for col, ancho, titulo in [
            ("folio", 90, "Folio"),
            ("categoria", 180, "Categoría"),
            ("ubicacion", 200, "Ubicación"),
            ("fecha", 130, "Fecha"),
            ("estatus", 110, "Estatus"),
        ]:
            self.tree.heading(col, text=titulo)
            self.tree.column(col, width=ancho, anchor="w")
        self.tree.pack(fill="both", expand=True, side="top")

        for est, color in ESTATUS_COLOR.items():
            self.tree.tag_configure(est, background=self._color_claro(color))

        # Controles para actualizar estatus
        control = tk.Frame(frame, bg=COLOR_FONDO)
        control.pack(fill="x", pady=12)

        tk.Label(control, text="Cambiar estatus del folio seleccionado a:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(
            side="left"
        )
        self.var_nuevo_estatus = tk.StringVar(value=ESTATUS_FLUJO[0])
        ttk.Combobox(
            control,
            textvariable=self.var_nuevo_estatus,
            values=ESTATUS_FLUJO,
            state="readonly",
            width=18,
        ).pack(side="left", padx=8)

        tk.Button(
            control,
            text="Actualizar",
            bg=COLOR_ACENTO,
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            command=self._actualizar_estatus_seleccionado,
        ).pack(side="left", padx=6)

        tk.Button(
            control,
            text="Refrescar",
            bg="#95a5a6",
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            command=self._refrescar_panel,
        ).pack(side="left", padx=6)

    @staticmethod
    def _color_claro(hex_color):
        """Devuelve una versión muy clara del color para usar como fondo de fila."""
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i: i + 2], 16) for i in (0, 2, 4))
        r = int(r + (255 - r) * 0.85)
        g = int(g + (255 - g) * 0.85)
        b = int(b + (255 - b) * 0.85)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _refrescar_panel(self):
        # Actualiza tarjetas de resumen
        for widget in self.resumen_frame.winfo_children():
            widget.destroy()

        conteo = {est: 0 for est in ESTATUS_FLUJO}
        for r in self.data["reportes"]:
            conteo[r["estatus"]] = conteo.get(r["estatus"], 0) + 1

        for est in ESTATUS_FLUJO:
            tarjeta = tk.Frame(self.resumen_frame,
                               bg=ESTATUS_COLOR[est], padx=14, pady=8)
            tarjeta.pack(side="left", padx=6)
            tk.Label(
                tarjeta, text=str(conteo[est]), bg=ESTATUS_COLOR[est], fg="white",
                font=("Segoe UI", 16, "bold"),
            ).pack()
            tk.Label(
                tarjeta, text=est, bg=ESTATUS_COLOR[est], fg="white", font=("Segoe UI", 9),
            ).pack()

        # Actualiza tabla
        self.tree.delete(*self.tree.get_children())
        for r in self.data["reportes"]:
            self.tree.insert(
                "",
                "end",
                iid=r["folio"],
                values=(
                    f"#{r['folio']}",
                    r["categoria"],
                    r["ubicacion"],
                    r["fecha_registro"],
                    r["estatus"],
                ),
                tags=(r["estatus"],),
            )

    def _actualizar_estatus_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showinfo("Selecciona un folio",
                                "Elige un reporte de la tabla primero.")
            return

        folio = seleccion[0]
        nuevo_estatus = self.var_nuevo_estatus.get()

        reporte = next(
            (r for r in self.data["reportes"] if r["folio"] == folio), None)
        if not reporte:
            return

        if reporte["estatus"] == nuevo_estatus:
            messagebox.showinfo(
                "Sin cambios", "El folio ya tiene ese estatus.")
            return

        reporte["estatus"] = nuevo_estatus
        reporte["historial"].append(
            {"estatus": nuevo_estatus, "fecha": ahora()})
        guardar_datos(self.data)
        self._refrescar_panel()


if __name__ == "__main__":
    app = CivicFlowApp()
    app.mainloop()
