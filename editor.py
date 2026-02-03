import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token
import os

# ==========================================
# 🖤 MINIMAL BLACK + DARK WHITE THEME
# ==========================================
BG = "#0d0d0d"
SIDEBAR = "#141414"
TEXT = "#e6e6e6"
MUTED = "#aaaaaa"
LINE_BG = "#111111"
BTN = "#1c1c1c"
HOVER = "#2a2a2a"

KEYWORD = "#ffffff"
STRING = "#dddddd"
COMMENT = "#777777"
FUNCNAME = "#f2f2f2"

FONT = ("Cascadia Code", 12)

# ==========================================
# MAIN WINDOW
# ==========================================
root = tk.Tk()
root.title("lw's Editor - Lightweight Text Editor")
root.geometry("1350x780")
root.config(bg=BG)

open_files = {}

# ==========================================
# SYNTAX HIGHLIGHTING
# ==========================================
def highlight(editor):
    code = editor.get("1.0", tk.END)

    for tag in editor.tag_names():
        editor.tag_remove(tag, "1.0", tk.END)

    lexer = PythonLexer()
    index = "1.0"

    for token, content in lex(code, lexer):
        length = len(content)
        end_index = editor.index(f"{index}+{length}c")

        if token in Token.Keyword:
            editor.tag_add("keyword", index, end_index)
        elif token in Token.String:
            editor.tag_add("string", index, end_index)
        elif token in Token.Comment:
            editor.tag_add("comment", index, end_index)
        elif token in Token.Name.Function:
            editor.tag_add("function", index, end_index)

        index = end_index

    editor.tag_config("keyword", foreground=KEYWORD)
    editor.tag_config("string", foreground=STRING)
    editor.tag_config("comment", foreground=COMMENT)
    editor.tag_config("function", foreground=FUNCNAME)

# ==========================================
# LINE NUMBERS
# ==========================================
def update_line_numbers(editor, line_box):
    line_box.config(state="normal")
    line_box.delete("1.0", tk.END)

    lines = editor.get("1.0", tk.END).split("\n")
    for i in range(1, len(lines)):
        line_box.insert(tk.END, f"{i}\n")

    line_box.config(state="disabled")

# ==========================================
# CREATE TAB WITH ✖ RIGHT END + SHORTCUTS
# ==========================================
def create_tab(filepath=None, content=""):
    tab = ttk.Frame(notebook)

    filename = os.path.basename(filepath) if filepath else "Untitled"

    # Push ✖ to right end
    tab_width = 15
    padded_name = filename.ljust(tab_width)
    notebook.add(tab, text=f"{padded_name}✖")

    tab.rowconfigure(0, weight=1)
    tab.columnconfigure(1, weight=1)

    # Line Numbers
    line_box = tk.Text(
        tab,
        width=5,
        bg=LINE_BG,
        fg=MUTED,
        font=FONT,
        state="disabled",
        border=0
    )
    line_box.grid(row=0, column=0, sticky="ns")

    # Editor Widget
    editor = tk.Text(
        tab,
        bg=BG,
        fg=TEXT,
        insertbackground=TEXT,
        font=FONT,
        undo=True,
        autoseparators=True,
        maxundo=-1,
        border=0,
        padx=18,
        pady=18
    )
    editor.grid(row=0, column=1, sticky="nsew")

    editor.insert("1.0", content)

    # Scrollbar
    scroll = ttk.Scrollbar(tab, command=editor.yview)
    scroll.grid(row=0, column=2, sticky="ns")
    editor.config(yscrollcommand=scroll.set)

    # Update Highlight + Lines
    def on_key(event=None):
        update_line_numbers(editor, line_box)
        highlight(editor)

    editor.bind("<KeyRelease>", on_key)

    # ==========================================
    # ✅ VS CODE KEYBOARD SHORTCUTS
    # ==========================================
    def select_all(event=None):
        editor.tag_add("sel", "1.0", "end")
        return "break"

    def copy(event=None):
        editor.event_generate("<<Copy>>")
        return "break"

    def paste(event=None):
        editor.event_generate("<<Paste>>")
        return "break"

    def cut(event=None):
        editor.event_generate("<<Cut>>")
        return "break"

    def undo(event=None):
        editor.edit_undo()
        return "break"

    def redo(event=None):
        editor.edit_redo()
        return "break"

    def indent(event=None):
        editor.insert("insert", "    ")
        return "break"

    def unindent(event=None):
        line_start = editor.index("insert linestart")
        line_text = editor.get(line_start, line_start + "+4c")
        if line_text == "    ":
            editor.delete(line_start, line_start + "+4c")
        return "break"

    # Bind Shortcuts
    editor.bind("<Control-a>", select_all)
    editor.bind("<Control-A>", select_all)

    editor.bind("<Control-c>", copy)
    editor.bind("<Control-C>", copy)

    editor.bind("<Control-v>", paste)
    editor.bind("<Control-V>", paste)

    editor.bind("<Control-x>", cut)
    editor.bind("<Control-X>", cut)

    editor.bind("<Control-z>", undo)
    editor.bind("<Control-y>", redo)

    editor.bind("<Tab>", indent)
    editor.bind("<Shift-Tab>", unindent)

    update_line_numbers(editor, line_box)
    highlight(editor)

    open_files[tab] = {"editor": editor, "path": filepath}
    notebook.select(tab)

# ==========================================
# CLOSE TAB ON ✖ CLICK
# ==========================================
def close_tab(event):
    x, y = event.x, event.y

    try:
        tab_index = notebook.index(f"@{x},{y}")
    except:
        return

    tab_text = notebook.tab(tab_index, "text")

    if "✖" in tab_text and x > 110:
        notebook.forget(tab_index)

        if len(notebook.tabs()) == 0:
            create_tab()

# ==========================================
# CURRENT EDITOR
# ==========================================
def get_current_editor():
    tab = notebook.select()
    tab_widget = root.nametowidget(tab)
    return tab_widget, open_files[tab_widget]["editor"]

# ==========================================
# FILE FUNCTIONS
# ==========================================
def new_file():
    create_tab()
    status_bar.config(text="🆕 New File Created")

def open_file():
    filepath = askopenfilename()
    if not filepath:
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    create_tab(filepath, content)
    status_bar.config(text=f"📂 Opened: {filepath}")

def save_file():
    tab_widget, editor = get_current_editor()
    filepath = open_files[tab_widget]["path"]

    if not filepath:
        save_as_file()
        return

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(editor.get("1.0", tk.END))

    status_bar.config(text=f"💾 Saved: {filepath}")

def save_as_file():
    tab_widget, editor = get_current_editor()

    filepath = asksaveasfilename(defaultextension=".txt")
    if not filepath:
        return

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(editor.get("1.0", tk.END))

    open_files[tab_widget]["path"] = filepath
    filename = os.path.basename(filepath)

    tab_width = 18
    padded_name = filename.ljust(tab_width)

    notebook.tab(tab_widget, text=f"{padded_name}✖")
    status_bar.config(text=f"💾 Saved As: {filepath}")

# ==========================================
# SEARCH & REPLACE
# ==========================================
def search_replace():
    popup = tk.Toplevel(root)
    popup.title("Search & Replace")
    popup.geometry("420x220")
    popup.config(bg=BG)

    tk.Label(popup, text="Search:", bg=BG, fg=TEXT).pack(pady=5)
    search_entry = tk.Entry(popup, bg=BTN, fg=TEXT)
    search_entry.pack(fill="x", padx=15)

    tk.Label(popup, text="Replace:", bg=BG, fg=TEXT).pack(pady=5)
    replace_entry = tk.Entry(popup, bg=BTN, fg=TEXT)
    replace_entry.pack(fill="x", padx=15)

    def do_replace():
        _, editor = get_current_editor()
        content = editor.get("1.0", tk.END)

        editor.delete("1.0", tk.END)
        editor.insert("1.0", content.replace(search_entry.get(), replace_entry.get()))

        showinfo("Done", "Replaced Successfully!")

    tk.Button(
        popup,
        text="Replace All",
        bg=TEXT,
        fg=BG,
        relief="flat",
        command=do_replace
    ).pack(pady=20)

# ==========================================
# UI LAYOUT
# ==========================================
root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

# Sidebar
sidebar = tk.Frame(root, bg=SIDEBAR, width=230)
sidebar.grid(row=0, column=0, sticky="ns")

tk.Label(
    sidebar,
    text="VS CODE MENU",
    bg=SIDEBAR,
    fg=TEXT,
    font=("Segoe UI", 11, "bold")
).pack(pady=20)

def sidebar_button(text, cmd):
    btn = tk.Button(
        sidebar,
        text=text,
        bg=BTN,
        fg=TEXT,
        font=("Segoe UI", 10),
        relief="flat",
        anchor="w",
        padx=15,
        command=cmd
    )
    btn.pack(fill="x", padx=15, pady=7)

    btn.bind("<Enter>", lambda e: btn.config(bg=HOVER))
    btn.bind("<Leave>", lambda e: btn.config(bg=BTN))

sidebar_button("🆕 New File", new_file)
sidebar_button("📂 Open File", open_file)
sidebar_button("💾 Save File", save_file)
sidebar_button("💾 Save As...", save_as_file)
sidebar_button("🔍 Search & Replace", search_replace)
sidebar_button("❌ Exit", root.quit)

# ==========================================
# NOTEBOOK STYLE
# ==========================================
style = ttk.Style()
style.theme_use("default")

style.configure("TNotebook", background=BG, borderwidth=0)

style.configure(
    "TNotebook.Tab",
    background=SIDEBAR,
    foreground=TEXT,
    padding=[5, 5],
    font=("Segoe UI", 10),
    width=13
)

style.map(
    "TNotebook.Tab",
    background=[("selected", BTN)],
    foreground=[("selected", TEXT)]
)

# Notebook
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=1, sticky="nsew")
notebook.bind("<Button-1>", close_tab)

# Status Bar
status_bar = tk.Label(
    root,
    text="Ready",
    bg=SIDEBAR,
    fg=TEXT,
    anchor="w",
    font=("Segoe UI", 9)
)
status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

# Default Tab
create_tab()

root.mainloop()
