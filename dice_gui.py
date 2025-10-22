# dice_gui.py  —— 右下角⚙设置按钮版本
import os, sys, json, random
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

CONFIG_FILE = "config.json"

def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel)

# 可选：防止任务栏与旧图标合并（Windows）
try:
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.happytown.dicegui")
except Exception:
    pass

# ---------------- 动效 ----------------
def flash(widget, cycles=8, interval=80, hi_bg="#FFF3BF", hi_fg="#B46900"):
    orig_bg = widget.cget("bg")
    orig_fg = widget.cget("fg")
    def toggle(i=0):
        if i >= cycles:
            widget.config(bg=orig_bg, fg=orig_fg); return
        widget.config(bg=hi_bg if i%2==0 else orig_bg, fg=hi_fg if i%2==0 else orig_fg)
        widget.after(interval, lambda: toggle(i+1))
    toggle(0)

def pulse(font_obj, base=50, peak=62, interval=30):
    frames = [54, 58, peak, 58, 54, base]
    def step(i=0):
        if i >= len(frames): return
        font_obj.configure(size=frames[i])
        root.after(interval, lambda: step(i+1))
    step(0)

# ---------------- 配置 ----------------
def load_config():
    try:
        with open(resource_path(CONFIG_FILE), "r", encoding="utf-8") as f:
            data = json.load(f)
            a = int(data.get("min", 1))
            b = int(data.get("max", 6))
            if a > b: a, b = b, a
            return a, b
    except Exception:
        return 1, 6

def save_config(a, b):
    try:
        with open(resource_path(CONFIG_FILE), "w", encoding="utf-8") as f:
            json.dump({"min": int(a), "max": int(b)}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ---------------- 逻辑 ----------------
def set_range(a, b):
    global min_v, max_v
    a, b = int(a), int(b)
    if a > b: a, b = b, a
    min_v, max_v = a, b
    update_title()
    save_config(a, b)

def current_range():
    return min_v, max_v

def update_title():
    a, b = current_range()
    root.title(f"小白露专用每日盲盒 {a}-{b}")

def roll(event=None):
    try:
        a, b = current_range()
        n = random.randint(a, b)
        result_var.set(str(n))
        flash(value_lbl)
        pulse(value_font)
    except Exception:
        result_var.set("×")
        flash(value_lbl, hi_bg="#FFEBEB", hi_fg="#B00000")

# ---------------- 设置对话框 ----------------
def open_settings(event=None):
    a0, b0 = current_range()
    win = tk.Toplevel(root)
    win.transient(root)
    win.title("设置")
    win.resizable(False, False)
    try:
        win.iconbitmap(resource_path("tuzi.ico"))
    except Exception:
        pass

    frm = ttk.Frame(win, padding=14)
    frm.grid(row=0, column=0)

    ttk.Label(frm, text="倍率最小值", font=("Microsoft YaHei UI", 11)).grid(row=0, column=0, sticky="e", padx=(0,8), pady=6)
    ttk.Label(frm, text="倍率最大值", font=("Microsoft YaHei UI", 11)).grid(row=1, column=0, sticky="e", padx=(0,8), pady=6)

    sv_min = tk.StringVar(value=str(a0))
    sv_max = tk.StringVar(value=str(b0))

    sp_min = tk.Spinbox(frm, from_=-999999, to=999999, textvariable=sv_min, width=10,
                        font=("Microsoft YaHei UI", 13), justify="center", wrap=True)
    sp_max = tk.Spinbox(frm, from_=-999999, to=999999, textvariable=sv_max, width=10,
                        font=("Microsoft YaHei UI", 13), justify="center", wrap=True)
    sp_min.grid(row=0, column=1, pady=6)
    sp_max.grid(row=1, column=1, pady=6)

    hint = ttk.Label(frm, text="提示：若最小值大于最大值，将自动交换。", foreground="#666")
    hint.grid(row=2, column=0, columnspan=2, pady=(2,8))

    btns = ttk.Frame(frm)
    btns.grid(row=3, column=0, columnspan=2, pady=(4,0))
    def on_ok(*_):
        try:
            a = int(sv_min.get().strip())
            b = int(sv_max.get().strip())
            set_range(a, b)
            win.destroy()
        except Exception:
            hint.config(text="请输入整数，例如 1 和 6", foreground="#B00000")
            win.bell()

    ttk.Button(btns, text="确定", command=on_ok).grid(row=0, column=0, padx=6)
    ttk.Button(btns, text="取消", command=win.destroy).grid(row=0, column=1, padx=6)

    win.bind("<Return>", on_ok)
    win.bind("<Escape>", lambda e: win.destroy())

    # 居中到主窗
    win.update_idletasks()
    x = root.winfo_rootx() + (root.winfo_width() - win.winfo_width()) // 2
    y = root.winfo_rooty() + (root.winfo_height() - win.winfo_height()) // 2
    win.geometry(f"+{x}+{y}")
    win.grab_set()

# ---------------- UI ----------------
root = tk.Tk()

# 图标
ico_file = resource_path("tuzi.ico")
try:
    root.iconbitmap(ico_file)
except Exception:
    pass

# 配置范围与标题
min_v, max_v = load_config()
update_title()

# 样式
style = ttk.Style(root)
style.configure("Heiti.TButton", font=("SimHei", 15))         # 主按钮
style.configure("Floating.TButton", padding=(6, 2))           # 右下角小齿轮

# 主体区域
result_var = tk.StringVar(value="-")
title_lbl = ttk.Label(root, text="  今日盲盒暴击倍率：", font=("Microsoft YaHei UI", 30))

value_font = tkfont.Font(family="SimHei", size=50)
value_lbl = tk.Label(root, textvariable=result_var, font=value_font)

roll_btn = ttk.Button(root, text="启动！", command=roll, style="Heiti.TButton")

# 布局（留出底部空间）
title_lbl.pack(padx=20, pady=(10, 4))
value_lbl.pack(padx=20, pady=4)
roll_btn.pack(padx=20, pady=(6, 40))  # 多留一点底部内边距，防止被齿轮挡住

# 右下角齿轮按钮（使用 place 固定在窗口右下，随窗口变化）
gear_img = None
for p in ("gear.png", "settings.png", "gear.gif"):
    full = resource_path(p)
    if os.path.exists(full):
        try:
            gear_img = tk.PhotoImage(file=full)
            break
        except Exception:
            gear_img = None

gear_btn = ttk.Button(
    root,
    text="⚙" if gear_img is None else "",
    image=gear_img,
    compound="left",
    command=open_settings,
    width=2,
    style="Floating.TButton",
)
# 靠右下角，留 10px 外边距
gear_btn.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

# 快捷键1
root.bind("<Return>", roll)
root.bind("<Control-comma>", open_settings)

root.mainloop()
