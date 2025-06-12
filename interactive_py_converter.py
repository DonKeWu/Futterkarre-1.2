#!/usr/bin/env python3
# Datei: interactive_py_converter.py

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import argparse

class PyToTxtConverter:
    def __init__(self):
        self.ignore_dirs = {'.git', '.idea', '__pycache__', '.vscode', '.pytest_cache'}
        self.ignore_files = {'*.pyc', '*.pyo', '*.pyd'}
    
    def convert_directory(self, source_dir, target_dir):
        """Konvertiert Verzeichnis von Python zu Text"""
        converted = 0
        copied = 0
        
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            rel_path = os.path.relpath(root, source_dir)
            target_root = os.path.join(target_dir, rel_path)
            os.makedirs(target_root, exist_ok=True)
            
            for file in files:
                if file.endswith(('.pyc', '.pyo', '.pyd')):
                    continue
                    
                src_file = os.path.join(root, file)
                
                if file.endswith('.py'):
                    base_name = os.path.splitext(file)[0]
                    dst_file = os.path.join(target_root, base_name + '.txt')
                    shutil.copy2(src_file, dst_file)
                    converted += 1
                else:
                    dst_file = os.path.join(target_root, file)
                    shutil.copy2(src_file, dst_file)
                    copied += 1
        
        return converted, copied
    
    def run_gui(self):
        """Startet GUI-Version"""
        root = tk.Tk()
        root.title("Python zu Text Konverter")
        root.geometry("500x300")
        
        def select_source():
            folder = filedialog.askdirectory(title="Quellordner auswählen")
            if folder:
                source_var.set(folder)
        
        def select_target():
            folder = filedialog.askdirectory(title="Zielordner auswählen")
            if folder:
                target_var.set(folder)
        
        def convert():
            source = source_var.get()
            target = target_var.get()
            
            if not source or not target:
                messagebox.showerror("Fehler", "Bitte beide Ordner auswählen!")
                return
            
            try:
                converted, copied = self.convert_directory(source, target)
                messagebox.showinfo("Erfolg", 
                    f"Konvertierung abgeschlossen!\n"
                    f"{converted} Python-Dateien konvertiert\n"
                    f"{copied} andere Dateien kopiert")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler bei Konvertierung: {str(e)}")
        
        # GUI-Elemente
        source_var = tk.StringVar()
        target_var = tk.StringVar()
        
        tk.Label(root, text="Python zu Text Konverter", font=("Arial", 16)).pack(pady=10)
        
        tk.Label(root, text="Quellordner:").pack(anchor="w", padx=20)
        frame1 = tk.Frame(root)
        frame1.pack(fill="x", padx=20, pady=5)
        tk.Entry(frame1, textvariable=source_var, width=50).pack(side="left", fill="x", expand=True)
        tk.Button(frame1, text="Durchsuchen", command=select_source).pack(side="right")
        
        tk.Label(root, text="Zielordner:").pack(anchor="w", padx=20, pady=(10,0))
        frame2 = tk.Frame(root)
        frame2.pack(fill="x", padx=20, pady=5)
        tk.Entry(frame2, textvariable=target_var, width=50).pack(side="left", fill="x", expand=True)
        tk.Button(frame2, text="Durchsuchen", command=select_target).pack(side="right")
        
        tk.Button(root, text="Konvertieren", command=convert, bg="green", fg="white", 
                 font=("Arial", 12)).pack(pady=20)
        
        root.mainloop()
    
    def run_cli(self, source, target):
        """Startet Kommandozeilen-Version"""
        if not os.path.exists(source):
            print(f"Fehler: Quellordner '{source}' existiert nicht!")
            return
        
        print(f"Konvertiere von: {source}")
        print(f"Konvertiere nach: {target}")
        print("-" * 50)
        
        converted, copied = self.convert_directory(source, target)
        
        print(f"\nKonvertierung abgeschlossen!")
        print(f"Python-Dateien konvertiert: {converted}")
        print(f"Andere Dateien kopiert: {copied}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python zu Text Konverter")
    parser.add_argument("--gui", action="store_true", help="GUI-Modus starten")
    parser.add_argument("source", nargs="?", help="Quellordner")
    parser.add_argument("target", nargs="?", help="Zielordner")
    
    args = parser.parse_args()
    converter = PyToTxtConverter()
    
    if args.gui:
        converter.run_gui()
    elif args.source and args.target:
        converter.run_cli(args.source, args.target)
    else:
        print("Verwendung:")
        print("  GUI-Modus: python3 interactive_py_converter.py --gui")
        print("  CLI-Modus: python3 interactive_py_converter.py <quell_ordner> <ziel_ordner>")

