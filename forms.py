import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from db import fetch, execute

# ============================================================
# Метаданные таблиц
# (col_name, russian_label, type, readonly)
# ============================================================
TABLE_META = {
    "regions": {
        "title": "Области",
        "fields": [
            ("id",   "Код",           "int",  True),
            ("name", "Наименование",  "str",  False),
        ],
    },
    "cities": {
        "title": "Города",
        "fields": [
            ("id",        "Код",           "int",  True),
            ("name",      "Наименование",  "str",  False),
            ("region_id", "Код области",   "int",  False),
        ],
    },
    "organizations": {
        "title": "Организации",
        "fields": [
            ("id",      "Код",          "int", True),
            ("name",    "Наименование", "str", False),
            ("city_id", "Код города",   "int", False),
        ],
    },
    "inclusion_reasons": {
        "title": "Основания включения в очередь",
        "fields": [
            ("id",   "Код",          "int", True),
            ("name", "Наименование", "str", False),
        ],
    },
    "housing_queue": {
        "title": "Очередники",
        "fields": [
            ("id",             "Идентификатор",       "int",  True),
            ("last_name",      "Фамилия",             "str",  False),
            ("queue_number",   "Номер очереди",       "int",  False),
            ("order_number",   "Номер приказа",       "str",  False),
            ("organization_id","Код организации",     "int",  False),
            ("reason_id",      "Код основания",       "int",  False),
            ("inclusion_date", "Дата (ГГГГ-ММ-ДД)",   "date", False),
            ("passport_data",  "Паспортные данные",   "str",  False),
            ("family_members", "Число членов семьи",  "int",  False),
            ("address",        "Адрес",               "str",  False),
        ],
    },
}


class GenericForm(ttk.Frame):
    """Универсальная форма CRUD для любой таблицы."""

    def __init__(self, master, table_name):
        super().__init__(master)
        self.table = table_name
        self.meta = TABLE_META[table_name]
        self.vars = {}
        self.current_pk = None
        self._build()
        self.refresh()

    def _build(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=5, pady=5)
        ttk.Label(top, text=self.meta["title"],
                  font=("", 13, "bold")).pack(side="left")

        # --- Таблица ---
        cols = [f[0] for f in self.meta["fields"]]
        self.tree = ttk.Treeview(self, show="headings", columns=cols, height=14)
        for col, label, _t, _ro in self.meta["fields"]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=130, anchor="w")
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        self.tree.pack(side="top", fill="both", expand=True, padx=5)
        sb.place(in_=self.tree, relx=1.0, rely=0.0, relheight=1.0, anchor="ne")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # --- Поля ввода ---
        frm = ttk.LabelFrame(self, text="Запись")
        frm.pack(fill="x", padx=5, pady=5)
        for i, (col, label, _t, ro) in enumerate(self.meta["fields"]):
            r, c = divmod(i, 2)
            ttk.Label(frm, text=label + ":").grid(
                row=r, column=c*2, sticky="e", padx=3, pady=2)
            v = tk.StringVar()
            ttk.Entry(frm, textvariable=v, width=32,
                      state="readonly" if ro else "normal").grid(
                row=r, column=c*2+1, sticky="we", padx=3, pady=2)
            self.vars[col] = v
        for c in (1, 3):
            frm.columnconfigure(c, weight=1)

        # --- Кнопки ---
        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=5, pady=5)
        ttk.Button(btns, text="Добавить",  command=self.on_add).pack(side="left", padx=3)
        ttk.Button(btns, text="Изменить",  command=self.on_update).pack(side="left", padx=3)
        ttk.Button(btns, text="Удалить",   command=self.on_delete).pack(side="left", padx=3)
        ttk.Button(btns, text="Обновить",  command=self.refresh).pack(side="left", padx=3)
        ttk.Button(btns, text="Очистить",  command=self.on_clear).pack(side="left", padx=3)

    # ---------------- логика ----------------
    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            rows, _ = fetch(f'SELECT * FROM "{self.table}" ORDER BY id')
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return
        for row in rows:
            vals = ["" if row[f[0]] is None else row[f[0]]
                    for f in self.meta["fields"]]
            self.tree.insert("", "end", iid=str(row["id"]), values=vals)

    def _on_select(self, _e=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        for (col, *_rest), v in zip(self.meta["fields"], vals):
            self.vars[col].set(v)
        self.current_pk = int(sel[0])

    def on_clear(self):
        for v in self.vars.values():
            v.set("")
        self.current_pk = None
        for s in self.tree.selection():
            self.tree.selection_remove(s)

    def _collect_nonpk(self):
        params = []
        for col, _label, ftype, ro in self.meta["fields"]:
            if ro:
                continue
            val = self.vars[col].get().strip()
            if val == "":
                params.append(None)
            elif ftype == "int":
                params.append(int(val))
            elif ftype == "date":
                params.append(datetime.date.fromisoformat(val))
            else:
                params.append(val)
        return params

    def on_add(self):
        try:
            cols = [f[0] for f in self.meta["fields"] if not f[3]]
            sql = (f'INSERT INTO "{self.table}" ({",".join(cols)}) '
                   f'VALUES ({",".join(["%s"]*len(cols))})')
            execute(sql, self._collect_nonpk())
            self.refresh(); self.on_clear()
            messagebox.showinfo("Готово", "Запись добавлена")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def on_update(self):
        if self.current_pk is None:
            messagebox.showwarning("Внимание", "Выберите запись")
            return
        try:
            cols = [f[0] for f in self.meta["fields"] if not f[3]]
            set_sql = ", ".join(f"{c}=%s" for c in cols)
            sql = f'UPDATE "{self.table}" SET {set_sql} WHERE id=%s'
            execute(sql, self._collect_nonpk() + [self.current_pk])
            self.refresh()
            messagebox.showinfo("Готово", "Запись обновлена")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def on_delete(self):
        if self.current_pk is None:
            messagebox.showwarning("Внимание", "Выберите запись")
            return
        if not messagebox.askyesno("Подтверждение", "Удалить запись?"):
            return
        try:
            execute(f'DELETE FROM "{self.table}" WHERE id=%s', [self.current_pk])
            self.refresh(); self.on_clear()
            messagebox.showinfo("Готово", "Запись удалена")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


class ReadOnlyTable(ttk.Frame):
    """Форма просмотра представлений и запросов."""

    def __init__(self, master, title, sql, params=None):
        super().__init__(master)
        self.title = title
        self.sql = sql
        self.params = params or ()
        self._build()
        self.refresh()

    def _build(self):
        top = ttk.Frame(self); top.pack(fill="x", padx=5, pady=5)
        ttk.Label(top, text=self.title, font=("", 13, "bold")).pack(side="left")
        ttk.Button(top, text="Обновить", command=self.refresh).pack(side="right", padx=3)

        wrap = ttk.Frame(self); wrap.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree = ttk.Treeview(wrap, show="headings")
        ys = ttk.Scrollbar(wrap, orient="vertical",   command=self.tree.yview)
        xs = ttk.Scrollbar(wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=ys.set, xscroll=xs.set)
        ys.pack(side="right", fill="y"); xs.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            rows, cols = fetch(self.sql, self.params)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e)); return
        self.tree["columns"] = cols
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=160, anchor="w")
        for row in rows:
            vals = ["" if row[c] is None else row[c] for c in cols]
            self.tree.insert("", "end", values=vals)


class MasterDetailForm(ttk.Frame):
    """Составная форма: организации -> очередники выбранной организации."""

    def __init__(self, master):
        super().__init__(master)
        left = ttk.LabelFrame(self, text="Организации")
        left.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.org_tree = ttk.Treeview(left, show="headings",
                                     columns=("id", "name"), height=18)
        self.org_tree.heading("id",   text="Код")
        self.org_tree.heading("name", text="Наименование")
        self.org_tree.column("id",   width=60)
        self.org_tree.column("name", width=250)
        self.org_tree.pack(fill="both", expand=True)
        self.org_tree.bind("<<TreeviewSelect>>", self._on_org)

        right = ttk.LabelFrame(self, text="Очередники выбранной организации")
        right.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.q_tree = ttk.Treeview(right, show="headings",
            columns=("queue_number", "last_name", "family_members", "reason"))
        for c, lbl, w in [
            ("queue_number",   "Номер очереди",     110),
            ("last_name",      "Фамилия",           140),
            ("family_members", "Членов семьи",       110),
            ("reason",         "Основание",         220),
        ]:
            self.q_tree.heading(c, text=lbl)
            self.q_tree.column(c, width=w)
        self.q_tree.pack(fill="both", expand=True)

        self.refresh_orgs()

    def refresh_orgs(self):
        for i in self.org_tree.get_children():
            self.org_tree.delete(i)
        rows, _ = fetch("SELECT id, name FROM organizations ORDER BY name")
        for r in rows:
            self.org_tree.insert("", "end", iid=str(r["id"]),
                                 values=(r["id"], r["name"]))

    def _on_org(self, _e=None):
        for i in self.q_tree.get_children():
            self.q_tree.delete(i)
        sel = self.org_tree.selection()
        if not sel:
            return
        rows, _ = fetch(
            "SELECT q.queue_number, q.last_name, q.family_members, r.name AS reason "
            "FROM housing_queue q "
            "JOIN inclusion_reasons r ON r.id = q.reason_id "
            "WHERE q.organization_id = %s "
            "ORDER BY q.queue_number",
            [int(sel[0])])
        for r in rows:
            self.q_tree.insert("", "end",
                values=(r["queue_number"], r["last_name"],
                        r["family_members"], r["reason"]))