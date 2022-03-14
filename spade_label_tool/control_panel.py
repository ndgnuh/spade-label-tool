import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


def donothing():
    return


def menu_import(root, menubar):
    m = tk.Menu(menubar, tearoff=0)
    m.add_command(label="Data (CSV)", command=donothing)
    m.add_command(label="Data (JSONL)", command=donothing)
    m.add_command(label="Label", command=donothing)
    m.add_command(label="Image folder", command=donothing)
    return m


def menu_export(root, menubar):
    m = tk.Menu(menubar, tearoff=0)
    m.add_command(label="Data (JSONL)", command=donothing)
    return m


def menu_file(root, menubar):
    def quit():
        yesno = messagebox.askyesno(title="Comfirm",
                                    message="Are you sure you want to quit?")
        if yesno:
            root.destroy()

    m = tk.Menu(menubar, tearoff=0)
    m.add_command(label="Save session", command=donothing)
    m.add_command(label="Load session", command=donothing)
    m.add_command(label="Quit", command=quit)
    return m


def run():
    root = tk.Tk()
    root.attributes('-type', 'tooltip')

    # MENUBAR
    menubar = tk.Menu(root)
    menubar.add_cascade(label="File", menu=menu_file(root, menubar))
    menubar.add_cascade(label="Import", menu=menu_import(root, menubar))
    menubar.add_cascade(label="Export", menu=menu_export(root, menubar))
    root.config(menu=menubar)

    # Layout
    frm = ttk.Frame(root)
    frm.grid()
    label = tk.Label(frm, text="Next").grid(column=0, row=0)
    root.mainloop()


run()
