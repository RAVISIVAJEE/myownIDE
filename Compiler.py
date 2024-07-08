from tkinter import *
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.messagebox import showerror
import subprocess
import os
import tkinter.scrolledtext as scrolledtext
from pygments import lex
from pygments.lexers import PythonLexer, JavascriptLexer, CLexer, JavaLexer
from pygments.styles import get_style_by_name
from pygments.token import Token

file_path = ''  # Initialize file_path as an empty string

# Syntax highlighting configuration
LEXERS = {
    "Python": PythonLexer,
    "JavaScript": JavascriptLexer,
    "C": CLexer,
    "Java": JavaLexer
}

current_lexer = PythonLexer()
style = get_style_by_name('monokai')

def set_file_path(path):
    global file_path
    file_path = path

def run():
    if file_path == '':
        showerror("Execution Error", "Save your code before running.")
        return

    lang = language.get()
    if lang == "Python":
        command = f'python "{file_path}"'
    elif lang == "JavaScript":
        command = f'node "{file_path}"'
    elif lang == "C":
        command = f'gcc "{file_path}" -o output && ./output'
    elif lang == "Java":
        class_name = os.path.basename(file_path).replace('.java', '')
        directory = os.path.dirname(file_path)
        command = f'javac "{file_path}" && java -cp "{directory}" {class_name}'
    else:
        showerror("Execution Error", "Unsupported language selected.")
        return

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, error = process.communicate()
        output.delete("1.0", END)  # Clear previous output
        output.insert("1.0", out.decode())
        output.insert("1.0", error.decode())
    except Exception as e:
        showerror("Execution Error", str(e))

def open_file():
    path = askopenfilename(
        filetypes=[("Python Files", "*.py"), ("JavaScript Files", "*.js"), ("C Files", "*.c"), ("Java Files", "*.java"),
                   ("All Files", "*.*")])
    if path:
        try:
            with open(path, 'r') as file:
                code = file.read()
                editor.delete("1.0", END)
                editor.insert("1.0", code)
                set_file_path(path)
                highlight_code(None)
        except Exception as e:
            showerror("Open File Error", str(e))

def save_file():
    global file_path
    if file_path == '':
        save_as()
    else:
        try:
            with open(file_path, 'w') as file:
                code = editor.get("1.0", END)
                file.write(code)
        except Exception as e:
            showerror("Save File Error", str(e))

def save_as():
    global file_path
    path = asksaveasfilename(defaultextension=".py",
                             filetypes=[("Python Files", "*.py"), ("JavaScript Files", "*.js"), ("C Files", "*.c"),
                                        ("Java Files", "*.java"), ("All Files", "*.*")])
    if path:
        try:
            with open(path, 'w') as file:
                code = editor.get("1.0", END)
                file.write(code)
                set_file_path(path)
        except Exception as e:
            showerror("Save File Error", str(e))

def exit_app():
    compiler.quit()

def change_language(*args):
    global current_lexer
    lang = language.get()
    current_lexer = LEXERS.get(lang, PythonLexer)()
    highlight_code(None)

def highlight_code(event):
    code = editor.get("1.0", END)
    tokens = lex(code, current_lexer)
    editor.mark_set("range_start", "1.0")
    for token, content in tokens:
        editor.mark_set("range_end", f"range_start+{len(content)}c")
        editor.tag_add(str(token), "range_start", "range_end")
        editor.mark_set("range_start", "range_end")
    for token, token_style in style:
        foreground = token_style['color']
        if foreground:
            editor.tag_configure(str(token), foreground=f"#{foreground}")

# Create the main window
compiler = Tk()
compiler.title("IDE")
compiler.geometry("800x600")

# Set the background colors
bg_color = "#2E3440"
text_bg_color = "#3B4252"
text_color = "#D8DEE9"
menu_bg_color = "#4C566A"
output_bg_color = "#4C566A"
button_bg_color = "#5E81AC"
button_fg_color = "#ECEFF4"

compiler.config(bg=bg_color)

# Create the menu bar
menu_bar = Menu(compiler, bg=menu_bg_color, fg=text_color)

# Create the File menu
file_menu = Menu(menu_bar, tearoff=0, bg=menu_bg_color, fg=text_color)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As", command=save_as)
file_menu.add_command(label="Exit", command=exit_app)
menu_bar.add_cascade(label="File", menu=file_menu)

# Create the Run menu
run_bar = Menu(menu_bar, tearoff=0, bg=menu_bg_color, fg=text_color)
run_bar.add_command(label="Run", command=run)
menu_bar.add_cascade(label="Run", menu=run_bar)

# Configure the menu bar
compiler.config(menu=menu_bar)

# Create a dropdown menu for language selection
language = StringVar(compiler)
language.set("Python")  # Set default language
language.trace('w', change_language)
language_menu = OptionMenu(compiler, language, "Python", "JavaScript", "C", "Java")
language_menu.config(bg=button_bg_color, fg=button_fg_color, activebackground=button_bg_color, activeforeground=button_fg_color)
language_menu.pack(pady=5)

# Create the text editor widget with syntax highlighting
editor = Text(compiler, wrap=NONE, bg=text_bg_color, fg=text_color, insertbackground=text_color)
editor.pack(expand=True, fill=BOTH)

# Add a scroll bar to the editor
scrollbar = Scrollbar(editor)
scrollbar.pack(side=RIGHT, fill=Y)
scrollbar.config(command=editor.yview)
editor.config(yscrollcommand=scrollbar.set)

# Create the output text widget
output = scrolledtext.ScrolledText(compiler, height=7, wrap=NONE, bg=output_bg_color, fg=text_color, insertbackground=text_color)
output.pack(expand=True, fill=BOTH, pady=5)

# Highlight initial code
editor.bind("<KeyRelease>", highlight_code)

# Run the main loop
compiler.mainloop()
