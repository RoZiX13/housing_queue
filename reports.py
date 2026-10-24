import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import OrderedDict

from db import fetch


class ReportWindow(ttk.Frame):
    def __init__(self, master, title, kind):
        super().__init__(master)
        self.report_title = title
        self.kind = kind
        self._build()
        self.generate()

    def _build(self):
        top = ttk.Frame(self); top.pack(fill="x", padx=5, pady=5)
        ttk.Label(top, text=self.report_title,
                  font=("", 13, "bold")).pack(side="left")
        ttk.Button(top, text="Сохранить в CSV",
                   command=self.export_csv).pack(side="right", padx=3)
        ttk.Button(top, text="Обновить",
                   command=self.generate).pack(side="right", padx=3)

        wrap = ttk.Frame(self); wrap.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree = ttk.Treeview(wrap, show="tree headings")
        ys = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=ys.set)
        ys.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

    def _clear(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

    def generate(self):
        self._clear()
        try:
            if self.kind == "main":
                self._main_report()
            elif self.kind.startswith("simple:"):
                self._simple_report(self.kind.split(":", 1)[1])
            elif self.kind.startswith("view:"):
                self._view_report(self.kind.split(":", 1)[1])
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ---------- Главный отчёт: 2 уровня группировки ----------
    def _main_report(self):
        self.tree["columns"] = ("count",)
        self.tree.heading("#0",    text="Организация / Основание")
        self.tree.heading("count", text="Количество очередников")
        self.tree.column("count", width=200, anchor="e")

        rows, _ = fetch("""
            SELECT o.name AS organization,
                   r.name AS reason,
                   COUNT(*) AS cnt
            FROM housing_queue q
            JOIN organizations     o ON o.id = q.organization_id
            JOIN inclusion_reasons r ON r.id = q.reason_id
            GROUP BY o.name, r.name
            ORDER BY o.name, r.name
        """)

        grouped = OrderedDict()
        for r in rows:
            grouped.setdefault(r["organization"], []).append(r)

        grand_total = 0
        for org_name, items in grouped.items():
            org_total = sum(i["cnt"] for i in items)
            grand_total += org_total
            org_node = self.tree.insert(
                "", "end",
                text=f"🏢 {org_name}",
                values=(org_total,),
                open=True,
                tags=("org",))
            for i in items:
                self.tree.insert(org_node, "end",
                                 text=f"     • {i['reason']}",
                                 values=(i["cnt"],))
        # Итоговая строка
        self.tree.insert("", "end", text="📊 ИТОГО ПО ВСЕМ ОРГАНИЗАЦИЯМ",
                         values=(grand_total,), tags=("grand",))

        self.tree.tag_configure("org",   background="#dde8ff",
                                font=("", 10, "bold"))
        self.tree.tag_configure("grand", background="#ffe9b3",
                                font=("", 11, "bold"))

    # ---------- Простые отчёты по таблицам ----------
    def _simple_report(self, table):
        rows, cols = fetch(f'SELECT * FROM "{table}" ORDER BY id')
        self.tree["columns"] = cols
        self.tree.heading("#0", text="№")
        self.tree.column("#0", width=60, anchor="center")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=150, anchor="w")
        for i, r in enumerate(rows, 1):
            vals = ["" if r[c] is None else r[c] for c in cols]
            self.tree.insert("", "end", text=str(i), values=vals)

    # ---------- Отчёт по представлению ----------
    def _view_report(self, view):
        rows, cols = fetch(f'SELECT * FROM "{view}"')
        self.tree["columns"] = cols
        self.tree.heading("#0", text="№")
        self.tree.column("#0", width=60, anchor="center")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=160, anchor="w")
        for i, r in enumerate(rows, 1):
            vals = ["" if r[c] is None else r[c] for c in cols]
            self.tree.insert("", "end", text=str(i), values=vals)

    # ---------- Экспорт в CSV ----------
    def export_csv(self):
        fn = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV-файл", "*.csv")])
        if not fn:
            return
        cols = self.tree["columns"]
        with open(fn, "w", encoding="utf-8-sig") as f:
            f.write(";".join(["Раздел"] + list(cols)) + "\n")

            def walk(parent):
                for iid in self.tree.get_children(parent):
                    text = self.tree.item(iid, "text").replace("•", "").strip()
                    vals = self.tree.item(iid, "values")
                    f.write(";".join([text] + [str(v) for v in vals]) + "\n")
                    walk(iid)

            walk("")
        messagebox.showinfo("Готово", f"Отчёт сохранён в {fn}")