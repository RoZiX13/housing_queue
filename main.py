import tkinter as tk
from tkinter import ttk

from forms import (GenericForm, ReadOnlyTable,
                   MasterDetailForm, TABLE_META)
from reports import ReportWindow

# ---------- Представления ----------
VIEWS = [
    ("v_housing_queue_full", "Полный список очередников"),
    ("v_cross_org_reason",   "Сводная: организации × основания"),
    ("v_queue_totals",       "Итоги по организациям и основаниям"),
    ("v_chart_queue_by_org", "Данные для диаграммы"),
]

# ---------- Запросы ----------
QUERIES = [
    ("Семьи с 4+ членами",
     "SELECT last_name, queue_number, family_members "
     "FROM housing_queue WHERE family_members > 4 "
     "ORDER BY family_members DESC"),
    ("Очередники по городам",
     "SELECT c.name AS city, COUNT(*) AS queue_count "
     "FROM housing_queue q "
     "JOIN organizations o ON o.id = q.organization_id "
     "JOIN cities c        ON c.id = o.city_id "
     "GROUP BY c.name ORDER BY queue_count DESC"),
    ("Основания по количеству",
     "SELECT r.name AS reason, COUNT(*) AS cnt "
     "FROM housing_queue q "
     "JOIN inclusion_reasons r ON r.id = q.reason_id "
     "GROUP BY r.name ORDER BY cnt DESC"),
]

# ---------- Отчёты ----------
REPORTS = [
    ("Главный отчёт: предприятия × основания", "main"),
    ("Отчёт: Области",                         "simple:regions"),
    ("Отчёт: Города",                          "simple:cities"),
    ("Отчёт: Организации",                     "simple:organizations"),
    ("Отчёт: Основания",                       "simple:inclusion_reasons"),
    ("Отчёт: Очередники",                      "simple:housing_queue"),
    ("Отчёт: Полный список очередников",       "view:v_housing_queue_full"),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Учёт очередников на получение жилья")
        self.geometry("1350x780")
        self._build_sidebar()
        self._build_notebook()

    # ============================================================
    # ЛЕНТА ПОЛЬЗОВАТЕЛЯ (пункт 7)
    # ============================================================
    def _build_sidebar(self):
        side = ttk.Frame(self, width=310)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        header = ttk.Frame(side)
        header.pack(fill="x", pady=(8, 4))
        ttk.Label(header, text="📁 Лента пользователя",
                  font=("", 13, "bold")).pack()

        canvas = tk.Canvas(side, highlightthickness=0)
        vsb = ttk.Scrollbar(side, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # --- Таблицы ---
        self._section(inner, "📋 Таблицы")
        for tname, meta in TABLE_META.items():
            self._btn(inner, meta["title"],
                      lambda tn=tname, ti=meta["title"]: self.open_table(tn, ti))

        # --- Формы ---
        self._section(inner, "🖼 Формы (составные)")
        self._btn(inner, "Организации + очередники",
                  lambda: self.open_tab_unique(
                      "Составная: организации + очередники",
                      lambda master: MasterDetailForm(master)))

        # --- Представления ---
        self._section(inner, "🔎 Представления")
        for view, title in VIEWS:
            self._btn(inner, title,
                      lambda v=view, t=title: self.open_view(v, t))

        # --- Запросы ---
        self._section(inner, "🔍 Запросы")
        for title, sql in QUERIES:
            self._btn(inner, title,
                      lambda t=title, s=sql: self.open_query(t, s))

        # --- Отчёты ---
        self._section(inner, "📄 Отчёты")
        for title, kind in REPORTS:
            self._btn(inner, title,
                      lambda t=title, k=kind: self.open_report(t, k))

    def _section(self, parent, text):
        frm = ttk.Frame(parent)
        frm.pack(fill="x", padx=6, pady=(10, 2))
        ttk.Label(frm, text=text, font=("", 10, "bold"),
                  foreground="#003a80").pack(anchor="w")
        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=6)

    def _btn(self, parent, text, command):
        ttk.Button(parent, text=text, command=command,
                   width=34).pack(fill="x", padx=8, pady=1)

    # ============================================================
    # РАБОЧАЯ ОБЛАСТЬ
    # ============================================================
    def _build_notebook(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(side="left", fill="both", expand=True)

    def _open(self, title, widget_factory):
        # если вкладка с таким заголовком уже открыта — переключаемся
        for tab_id in self.nb.tabs():
            if self.nb.tab(tab_id, "text") == title:
                self.nb.select(tab_id)
                return
        widget = widget_factory(self.nb)
        self.nb.add(widget, text=title)
        self.nb.select(widget)

    def open_tab_unique(self, title, factory):
        self._open(title, factory)

    def open_table(self, table_name, title):
        self._open(title, lambda m: GenericForm(m, table_name))

    def open_view(self, view, title):
        self._open(title,
                   lambda m: ReadOnlyTable(m, title, f'SELECT * FROM "{view}"'))

    def open_query(self, title, sql):
        self._open("Запрос: " + title,
                   lambda m: ReadOnlyTable(m, title, sql))

    def open_report(self, title, kind):
        self._open(title, lambda m: ReportWindow(m, title, kind))


if __name__ == "__main__":
    App().mainloop()