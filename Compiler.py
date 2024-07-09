from tkinter import *
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.messagebox import showerror
import subprocess
import os
import tkinter.scrolledtext as scrolledtext
from pygments import lex
from pygments.lexers import PythonLexer, JavascriptLexer, CLexer, JavaLexer
from pygments.styles import get_style_by_name
import jedi

file_path = ''

LEXERS = {
    "Python": PythonLexer,
    "JavaScript": JavascriptLexer,
    "C": CLexer,
    "Java": JavaLexer
}

current_lexer = PythonLexer()
style = get_style_by_name('monokai')
auto_complete_listbox = None

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

def auto_complete(event):

    global auto_complete_listbox
    if language.get() == "Python":
        cursor_position = editor.index(INSERT)
        line, column = map(int, cursor_position.split('.'))
        code = editor.get("1.0", END)
        script = jedi.Script(code, path=file_path)
        completions = script.complete(line=line, column=column)
        if completions:
            if auto_complete_listbox:
                auto_complete_listbox.destroy()
            auto_complete_listbox = Listbox(editor, bg=menu_bg_color, fg=text_color)
            for completion in completions:
                auto_complete_listbox.insert(END, completion.name)
            auto_complete_listbox.place(x=event.x, y=event.y)
            auto_complete_listbox.bind("<<ListboxSelect>>", lambda e: insert_completion(completions[auto_complete_listbox.curselection()[0]].name))
        else:
            if auto_complete_listbox:
                auto_complete_listbox.destroy()
    else:
        if auto_complete_listbox:
            auto_complete_listbox.destroy()

def insert_completion(completion):

    cursor_position = editor.index(INSERT)
    editor.insert(cursor_position, completion)
    editor.see(cursor_position)  # Ensure the cursor position is visible
    if auto_complete_listbox:
        auto_complete_listbox.destroy()

def handle_auto_closing(event):

    opening_chars = {"(": ")", "{": "}", "[": "]", "\"": "\"", "'": "'"}
    cursor_position = editor.index(INSERT)
    char = event.char
    if char in opening_chars:
        closing_char = opening_chars[char]
        editor.insert(cursor_position, closing_char)
        editor.mark_set(INSERT, cursor_position)

def handle_indentation(event):

    cursor_position = editor.index(INSERT)
    line, column = map(int, cursor_position.split('.'))
    if editor.get(f"{line}.0", f"{line}.end").strip().endswith(':'):
        editor.insert(cursor_position, "\n" + " " * 4)
        return "break"

compiler = Tk()
compiler.title("IDE")
compiler.geometry("800x600")

bg_color = "#2E3440"
text_bg_color = "#3B4252"
text_color = "#D8DEE9"
menu_bg_color = "#4C566A"
output_bg_color = "#4C566A"
button_bg_color = "#5E81AC"
button_fg_color = "#ECEFF4"

compiler.config(bg=bg_color)

menu_bar = Menu(compiler, bg=menu_bg_color, fg=text_color)

file_menu = Menu(menu_bar, tearoff=0, bg=menu_bg_color, fg=text_color)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As", command=save_as)
file_menu.add_command(label="Exit", command=exit_app)
menu_bar.add_cascade(label="File", menu=file_menu)

run_bar = Menu(menu_bar, tearoff=0, bg=menu_bg_color, fg=text_color)
run_bar.add_command(label="Run", command=run)
menu_bar.add_cascade(label="Run", menu=run_bar)

compiler.config(menu=menu_bar)

language = StringVar(compiler)
language.set("Python")
language.trace('w', change_language)
language_menu = OptionMenu(compiler, language, "Python", "JavaScript", "C", "Java")
language_menu.config(bg=button_bg_color, fg=button_fg_color, activebackground=button_bg_color, activeforeground=button_fg_color)
language_menu.pack(pady=5)

editor = Text(compiler, wrap=NONE, bg=text_bg_color, fg=text_color, insertbackground=text_color)
editor.pack(expand=True, fill=BOTH)

scrollbar = Scrollbar(editor)
scrollbar.pack(side=RIGHT, fill=Y)
scrollbar.config(command=editor.yview)
editor.config(yscrollcommand=scrollbar.set)

output = scrolledtext.ScrolledText(compiler, height=7, wrap=NONE, bg=output_bg_color, fg=text_color, insertbackground=text_color)
output.pack(expand=True, fill=BOTH, pady=5)

editor.bind("<KeyRelease>", highlight_code)
editor.bind("<KeyRelease>", auto_complete)
editor.bind("<Key>", handle_auto_closing)
editor.bind("<Return>", handle_indentation)

compiler.mainloop()
