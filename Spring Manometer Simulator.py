import tkinter as tk
from tkinter import ttk
import random
import math

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Manómetro con Resorte — Cálculo y DCL")
        self.geometry("980x620")
        self.minsize(920, 580)

        self.bg = "#0B1220"
        self.card = "#0F1A33"
        self.card2 = "#0C1730"
        self.text = "#EAF2FF"
        self.muted = "#9CB0D1"
        self.accent = "#6AE4FF"
        self.accent2 = "#8C7CFF"
        self.good = "#58F29A"
        self.warn = "#FFCB6B"
        self.bad = "#FF6B7A"

        self.configure(bg=self.bg)
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except:
            pass

        self._style_ttk()

        self.P_kPa = tk.DoubleVar(value=120.0)
        self.D_mm = tk.DoubleVar(value=40.0)
        self.x_mm = tk.DoubleVar(value=10.0)

        self.A_m2 = 0.0
        self.A_mm2 = 0.0
        self.F = 0.0
        self.k_Nm = 0.0
        self.k_Nmm = 0.0

        self.status = tk.StringVar(value="Listo. Ingresa datos o usa Random.")
        self.result_k = tk.StringVar(value="k = —")
        self.result_F = tk.StringVar(value="F = —")
        self.result_A = tk.StringVar(value="A = —")

        self.target_compression_px = 0
        self.current_compression_px = 0
        self.animating = False

        self._build_ui()
        self._recalc()
        self._draw_scene()

        self.style.configure("Mono.TLabel", font=("Menlo", 12), background=self.card2, foreground=self.muted)
        self.style.configure("MonoK.TLabel", font=("Menlo", 13, "bold"), background=self.card2, foreground=self.good)

    def _style_ttk(self):
        self.style.configure("TFrame", background=self.bg)
        self.style.configure("Card.TFrame", background=self.card, relief="flat")
        self.style.configure("Card2.TFrame", background=self.card2, relief="flat")

        self.style.configure("TLabel", background=self.card, foreground=self.text, font=("SF Pro Display", 13))
        self.style.configure("Title.TLabel", background=self.bg, foreground=self.text, font=("SF Pro Display", 20, "bold"))
        self.style.configure("Sub.TLabel", background=self.bg, foreground=self.muted, font=("SF Pro Display", 12))
        self.style.configure("Muted.TLabel", background=self.card, foreground=self.muted, font=("SF Pro Display", 12))
        self.style.configure("Badge.TLabel", background=self.bg, foreground=self.accent, font=("SF Pro Display", 11, "bold"))

        self.style.configure("TEntry", fieldbackground="#0B1633", foreground=self.text, bordercolor="#13244A", insertcolor=self.text)
        self.style.map("TEntry", fieldbackground=[("focus", "#0C1A3B")])
        self.style.configure("Fixed.TEntry", font=("Menlo", 12))

        self.style.configure("Accent.TButton", background=self.accent2, foreground="#0B1220", font=("SF Pro Display", 12, "bold"), padding=10, borderwidth=0)
        self.style.map("Accent.TButton", background=[("active", "#A096FF")])

        self.style.configure("Soft.TButton", background="#142653", foreground=self.text, font=("SF Pro Display", 12), padding=10, borderwidth=0)
        self.style.map("Soft.TButton", background=[("active", "#1B3470")])

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=22, pady=(18, 10))

        title_row = ttk.Frame(top)
        title_row.pack(fill="x")

        ttk.Label(title_row, text="Manómetro con Resorte", style="Title.TLabel").pack(side="left")
        ttk.Label(title_row, text="Equilibrio estático · F = P·A · k = F/x", style="Badge.TLabel").pack(side="right", pady=6)

        ttk.Label(top, text="Unidades amigables: P en kPa, D y x en mm. Cálculo interno en SI.", style="Sub.TLabel").pack(anchor="w", pady=(6, 0))

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=22, pady=(6, 18))

        left = ttk.Frame(body, style="Card.TFrame", width=330)
        left.pack(side="left", fill="y", padx=(0, 14), pady=0, ipadx=14, ipady=14)
        left.pack_propagate(False)

        right = ttk.Frame(body, style="Card.TFrame")
        right.pack(side="right", fill="both", expand=True, padx=0, pady=0, ipadx=14, ipady=14)

        ttk.Label(left, text="Datos de entrada", font=("SF Pro Display", 14, "bold")).pack(anchor="w", pady=(2, 10), padx=10)

        grid = ttk.Frame(left, style="Card.TFrame")
        grid.pack(fill="x", padx=10)

        self._field(grid, "Presión P (kPa)", self.P_kPa, 0)
        self._field(grid, "Diámetro D (mm)", self.D_mm, 1)
        self._field(grid, "Desplazamiento x (mm)", self.x_mm, 2)

        btns = ttk.Frame(left, style="Card.TFrame")
        btns.pack(fill="x", padx=10, pady=(12, 10))

        ttk.Button(btns, text="Calcular", style="Accent.TButton", command=self._recalc).pack(fill="x", pady=(0, 8))
        ttk.Button(btns, text="Datos Random", style="Soft.TButton", command=self._randomize).pack(fill="x", pady=(0, 8))
        ttk.Button(btns, text="Reset", style="Soft.TButton", command=self._reset).pack(fill="x")

        res = ttk.Frame(left, style="Card2.TFrame")
        res.pack(fill="x", padx=10, pady=(14, 10), ipady=10)

        ttk.Label(res, text="Resultados", background=self.card2, foreground=self.text, font=("SF Pro Display", 14, "bold")).pack(anchor="w", padx=12, pady=(8, 8))
        ttk.Label(res, textvariable=self.result_A, style="Mono.TLabel").pack(anchor="w", padx=12, pady=2)
        ttk.Label(res, textvariable=self.result_F, style="Mono.TLabel").pack(anchor="w", padx=12, pady=2)
        ttk.Label(res, textvariable=self.result_k, style="MonoK.TLabel").pack(anchor="w", padx=12, pady=(6, 10))

        hint = ttk.Frame(left, style="Card.TFrame")
        hint.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Label(hint, text="Notas rápidas", style="Muted.TLabel", font=("SF Pro Display", 13, "bold")).pack(anchor="w", pady=(2, 6))
        ttk.Label(hint, text="• Entrada: kPa y mm\n• El sistema convierte a SI internamente\n• x debe ser > 0", style="Muted.TLabel").pack(anchor="w")

        ttk.Label(right, text="Visualización (Resorte + Émbolo) y DCL", font=("SF Pro Display", 14, "bold")).pack(anchor="w", padx=10, pady=(2, 10))

        self.canvas = tk.Canvas(right, bg="#071025", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        bottom_status = ttk.Frame(self)
        bottom_status.pack(fill="x", padx=22, pady=(0, 16))
        self.status_lbl = tk.Label(bottom_status, textvariable=self.status, bg=self.bg, fg=self.muted, font=("SF Pro Display", 12))
        self.status_lbl.pack(anchor="w")

        self.bind("<Return>", lambda e: self._recalc())
        self.canvas.bind("<Configure>", lambda e: self._draw_scene())

    def _field(self, parent, label, var, row):
        ttk.Label(parent, text=label, style="Muted.TLabel").grid(row=row*2, column=0, sticky="w", pady=(0, 4))
        ent = ttk.Entry(parent, textvariable=var, style="Fixed.TEntry", width=18)
        ent.grid(row=row * 2 + 1, column=0, sticky="w", pady=(0, 10))
        parent.grid_columnconfigure(0, weight=0)

    def _reset(self):
        self.P_kPa.set(120.0)
        self.D_mm.set(40.0)
        self.x_mm.set(10.0)
        self.status.set("Reset aplicado.")
        self._recalc()

    def _randomize(self):
        P = round(random.uniform(10.0, 350.0), 2)
        D = round(random.uniform(10.0, 95.0), 2)
        x = round(random.uniform(0.5, 30.0), 2)
        self.P_kPa.set(P)
        self.D_mm.set(D)
        self.x_mm.set(x)
        self.status.set("Datos aleatorios (realistas) cargados.")
        self._recalc()

    def _recalc(self):
        try:
            P_kPa = float(self.P_kPa.get())
            D_mm = float(self.D_mm.get())
            x_mm = float(self.x_mm.get())

            if P_kPa <= 0 or D_mm <= 0 or x_mm <= 0:
                raise ValueError()

            P_Pa = P_kPa * 1000.0
            D_m = D_mm / 1000.0
            x_m = x_mm / 1000.0

            self.A_m2 = math.pi * (D_m * D_m) / 4.0
            self.A_mm2 = self.A_m2 * 1_000_000.0
            self.F = P_Pa * self.A_m2
            self.k_Nm = self.F / x_m
            self.k_Nmm = self.k_Nm / 1000.0

            self.result_A.set("A = {:.3f} mm²   ({:.6e} m²)".format(self.A_mm2, self.A_m2))
            self.result_F.set("F = {:.3f} N".format(self.F))
            self.result_k.set("k = {:.3f} N/mm   ({:.3f} N/m)".format(self.k_Nmm, self.k_Nm))

            self.status.set("Cálculo OK. Mostrando resorte y DCL.")
            self._update_compression_target(x_mm)
        except:
            self.result_A.set("A = —")
            self.result_F.set("F = —")
            self.result_k.set("k = —")
            self.status.set("Datos inválidos. Asegura P(kPa), D(mm), x(mm) > 0.")
            self._update_compression_target(None)

        self._draw_scene()

    def _update_compression_target(self, x_mm):
        if x_mm is None:
            self.target_compression_px = 0
        else:
            x_clamped = max(0.0, min(60.0, float(x_mm)))
            self.target_compression_px = int(16 + (x_clamped / 60.0) * 120)

        if not self.animating:
            self.animating = True
            self.after(10, self._animate)

    def _animate(self):
        step = 6
        if self.current_compression_px < self.target_compression_px:
            self.current_compression_px = min(self.target_compression_px, self.current_compression_px + step)
            self._draw_scene()
            self.after(12, self._animate)
        elif self.current_compression_px > self.target_compression_px:
            self.current_compression_px = max(self.target_compression_px, self.current_compression_px - step)
            self._draw_scene()
            self.after(12, self._animate)
        else:
            self.animating = False

    def _draw_scene(self):
        c = self.canvas
        c.delete("all")
        w = max(10, c.winfo_width())
        h = max(10, c.winfo_height())

        self._draw_bg(c, w, h)
        self._draw_header_overlay(c, w, h)
        self._draw_system(c, w, h)
        self._draw_fbd(c, w, h)

    def _draw_bg(self, c, w, h):
        c.create_rectangle(0, 0, w, h, fill="#071025", outline="")
        for i in range(0, 14):
            y = int((h / 14) * i)
            c.create_line(0, y, w, y, fill="#0B1A3A")
        for i in range(0, 18):
            x = int((w / 18) * i)
            c.create_line(x, 0, x, h, fill="#091733")

        c.create_oval(-200, -180, 420, 420, fill="#0B1D3D", outline="")
        c.create_oval(w-520, -260, w+220, 480, fill="#0A1936", outline="")
        c.create_oval(w-420, h-380, w+240, h+300, fill="#08162F", outline="")

    def _draw_header_overlay(self, c, w, h):
        pad = 18
        c.create_rectangle(pad, pad, w-pad, pad+58, fill="#0B1633", outline="#142A55", width=2)
        c.create_text(pad+16, pad+20, anchor="w", text="Vista del sistema", fill="#EAF2FF", font=("SF Pro Display", 16, "bold"))
        subtitle = "Entrada en kPa y mm · Internamente: Pa y m · DCL: F_presión y F_resorte"
        c.create_text(pad+16, pad+44, anchor="w", text=subtitle, fill="#9CB0D1", font=("SF Pro Display", 12))

    def _draw_system(self, c, w, h):
        left = 60
        top = 95
        sys_w = int(w * 0.60) - 70
        sys_h = h - 135
        x0, y0 = left, top
        x1, y1 = left + sys_w, top + sys_h

        c.create_rectangle(x0, y0, x1, y1, fill="#071A3A", outline="#183A78", width=2)

        inner_pad = 34
        cx0, cy0 = x0 + inner_pad, y0 + inner_pad
        cx1, cy1 = x1 - inner_pad, y1 - inner_pad

        c.create_rectangle(cx0, cy0, cx1, cy1, fill="#061431", outline="#0E2A5A", width=2)

        piston_w = int((cx1 - cx0) * 0.42)
        piston_h = 44
        piston_x = cx0 + int((cx1 - cx0) * 0.45)
        base_y = cy1 - 70

        compression = self.current_compression_px
        piston_y = base_y - piston_h - compression

        rod_w = 20
        rod_x = piston_x + piston_w/2 - rod_w/2

        spring_top = cy0 + 78
        spring_bottom = piston_y - 10
        spring_len = max(70, spring_bottom - spring_top)

        c.create_rectangle(cx0+40, cy0+45, cx1-40, cy0+65, fill="#0B224C", outline="#1C4B99", width=2)
        c.create_text(cx0+52, cy0+55, anchor="w", text="Tapa / Cuerpo", fill="#9CB0D1", font=("SF Pro Display", 11, "bold"))

        chamber_x0 = cx0 + 44
        chamber_x1 = cx1 - 44
        chamber_y0 = cy0 + 65
        chamber_y1 = cy1 - 60
        c.create_rectangle(chamber_x0, chamber_y0, chamber_x1, chamber_y1, fill="#05102A", outline="#0E2A5A", width=2)

        spring_center_x = rod_x + rod_w/2
        self._draw_spring_centered(c, spring_center_x, spring_top, spring_len, width=110)

        support_y = spring_top - 12
        c.create_line(spring_center_x - 70, support_y, spring_center_x + 70, support_y, fill="#2E6BFF", width=3)
        c.create_text(spring_center_x, support_y - 12, text="Apoyo", fill="#9CB0D1", font=("SF Pro Display", 11, "bold"))

        c.create_rectangle(piston_x, piston_y, piston_x+piston_w, piston_y+piston_h, fill="#0F2A5A", outline="#6AE4FF", width=2)
        c.create_text(piston_x + piston_w/2, piston_y + piston_h/2, text="Émbolo", fill="#EAF2FF", font=("SF Pro Display", 12, "bold"))

        c.create_rectangle(rod_x, cy0+70, rod_x+rod_w, piston_y, fill="#0C2148", outline="#2B5DB6", width=2)

        port_w, port_h = 54, 26
        port_x = chamber_x1 - port_w - 10
        port_y = chamber_y0 + 18

        c.create_rectangle(port_x, port_y, port_x+port_w, port_y+port_h, fill="#0B224C", outline="#1C4B99", width=2)

        midy = port_y + port_h/2
        chamber_wall_x = chamber_x1
        c.create_line(port_x+port_w, midy, chamber_wall_x, midy, fill="#1C4B99", width=4)

        arrow_to = chamber_wall_x - 28
        c.create_line(chamber_wall_x, midy, arrow_to, midy, fill="#6AE4FF", width=3)
        c.create_polygon(arrow_to, midy, arrow_to+12, midy-6, arrow_to+12, midy+6, fill="#6AE4FF", outline="")

        c.create_text(port_x + port_w/2, port_y - 12, text="Entrada P", fill="#9CB0D1", font=("SF Pro Display", 11, "bold"))

        p_txt = "P = {:.2f} kPa".format(self._safe_num(self.P_kPa.get()))
        d_txt = "D = {:.2f} mm".format(self._safe_num(self.D_mm.get()))
        x_txt = "x = {:.2f} mm".format(self._safe_num(self.x_mm.get()))
        c.create_text(chamber_x0+18, chamber_y0+20, anchor="w", text=p_txt, fill="#EAF2FF", font=("SF Pro Display", 12, "bold"))
        c.create_text(chamber_x0+18, chamber_y0+42, anchor="w", text=d_txt, fill="#9CB0D1", font=("SF Pro Display", 11))
        c.create_text(chamber_x0+18, chamber_y0+62, anchor="w", text=x_txt, fill="#9CB0D1", font=("SF Pro Display", 11))

        comp_label = "Compresión visual: {} px".format(self.current_compression_px)
        c.create_text(cx0+18, cy1-18, anchor="w", text=comp_label, fill="#6AE4FF", font=("SF Pro Display", 11, "bold"))

    def _draw_spring_centered(self, c, x_center, y, length, width=110):
        turns = max(6, int(length / 18))
        amp = width / 2
        y0 = y
        y1 = y + length
        pts = []
        for i in range(turns * 2 + 1):
            t = i / (turns * 2)
            yy = y0 + t * length
            if i == 0 or i == turns * 2:
                xx = x_center
            else:
                xx = x_center + (amp * 0.95 if i % 2 == 0 else -amp * 0.95)
            pts.extend([xx, yy])

        c.create_line(x_center, y0-10, x_center, y0, fill="#2E6BFF", width=3)
        c.create_line(x_center, y1, x_center, y1+10, fill="#2E6BFF", width=3)
        c.create_line(*pts, fill="#8C7CFF", width=4, smooth=True)
        c.create_line(*pts, fill="#6AE4FF", width=2, smooth=True)
        c.create_text(x_center, y0 + length/2, text="RESORTE", fill="#9CB0D1", font=("SF Pro Display", 11, "bold"))

    def _draw_fbd(self, c, w, h):
        right_panel_x0 = int(w * 0.60) + 20
        top = 95
        x0 = right_panel_x0
        y0 = top
        x1 = w - 60
        y1 = h - 40

        c.create_rectangle(x0, y0, x1, y1, fill="#071A3A", outline="#183A78", width=2)
        c.create_text(x0+16, y0+18, anchor="w", text="Diagrama de Cuerpo Libre (Émbolo)", fill="#EAF2FF", font=("SF Pro Display", 14, "bold"))

        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2 + 30

        body_w, body_h = 160, 70
        c.create_rectangle(cx-body_w/2, cy-body_h/2, cx+body_w/2, cy+body_h/2, fill="#0F2A5A", outline="#6AE4FF", width=2)
        c.create_text(cx, cy, text="ÉMBOLO", fill="#EAF2FF", font=("SF Pro Display", 12, "bold"))

        F = self.F if self.k_Nm > 0 else 0.0
        Ftxt = "{:.2f} N".format(F) if F > 0 else "—"

        arrow_len = 130
        c.create_line(cx, cy-body_h/2-10, cx, cy-body_h/2-arrow_len, fill="#FFCB6B", width=5)
        c.create_polygon(cx-9, cy-body_h/2-arrow_len+18, cx+9, cy-body_h/2-arrow_len+18, cx, cy-body_h/2-arrow_len, fill="#FFCB6B", outline="")
        c.create_text(cx+12, cy-body_h/2-arrow_len+10, anchor="w", text="F_resorte = " + Ftxt, fill="#FFCB6B", font=("SF Pro Display", 12, "bold"))

        c.create_line(cx, cy+body_h/2+10, cx, cy+body_h/2+arrow_len, fill="#FF6B7A", width=5)
        c.create_polygon(cx-9, cy+body_h/2+arrow_len-18, cx+9, cy+body_h/2+arrow_len-18, cx, cy+body_h/2+arrow_len, fill="#FF6B7A", outline="")
        c.create_text(cx+12, cy+body_h/2+arrow_len-10, anchor="w", text="F_presión = " + Ftxt, fill="#FF6B7A", font=("SF Pro Display", 12, "bold"))

        eq = "Equilibrio: F_presión = F_resorte"
        c.create_text(x0+16, y1-28, anchor="w", text=eq, fill="#9CB0D1", font=("SF Pro Display", 12))
        c.create_text(x1-16, y1-28, anchor="e", text="k = F/x", fill="#6AE4FF", font=("SF Pro Display", 12, "bold"))

    def _safe_num(self, v):
        try:
            return float(v)
        except:
            return 0.0


if __name__ == "__main__":
    App().mainloop()