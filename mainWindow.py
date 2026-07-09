from tkinter import Tk, Checkbutton, Entry, Button, Frame, Label, BooleanVar, filedialog, Listbox, END, SINGLE, messagebox, Toplevel
import tkinter.ttk as ttk
import json
import os
import threading
import time
from main import main


class LoadingScreen:
    """Tela de carregamento com barra de progresso"""
    def __init__(self, parent):
        self.root = Toplevel(parent)
        self.root.title("Carregando...")
        self.root.geometry("450x180")
        self.root.resizable(False, False)
        self.root.grab_set()
        self.closed = False
        
        
        # Centralizar na tela
        #self.root.transient(parent)
        self.root.update_idletasks()
        
        # Tentar centralizar, com fallback
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 225
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 90
            self.root.geometry(f"450x180+{x}+{y}")
        except:
            self.root.geometry("450x180")
        
        # Frame principal
        main_frame = Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Label de mensagem
        self.lbl_message = Label(main_frame, text="Conectando câmeras...", font=("Arial", 12, "bold"))
        self.lbl_message.pack(pady=(0, 15))
        
        # Barra de progresso
        self.progress = ttk.Progressbar(
            main_frame, 
            length=400, 
            mode='determinate',
            maximum=100
        )
        self.progress.pack(pady=10)
        
        # Label de porcentagem
        self.lbl_percent = Label(main_frame, text="0%", font=("Arial", 10))
        self.lbl_percent.pack(pady=(10, 0))
        
        
        
    def on_close(self):
        """Quando usuário tenta fechar a tela"""
        self.closed = False
        self.close()
        
    def update_progress(self, message, percent):
        """Atualizar progresso"""
        if self.closed:
            return
        try:
            self.lbl_message.config(text=message)
            self.progress['value'] = percent
            self.lbl_percent.config(text=f"{percent}%")
            self.root.update()
            self.root.update_idletasks()
        except:
            pass
    
    def close(self):
        """Fechar tela de carregamento"""
        try:
            self.root.destroy()
        except:
            pass


class MainWindow:
    def __init__(self):
        self.root = Tk()
        self.root.title("RTSP Multi View Player")

    # Usar somente se necessário um tamanho inicial fixo da janela
        #self.root.geometry(f"{screen_width}x{screen_width}")

    # Impedir que a janela seja redimensionada
        self.root.resizable(False, False) 

    # Protocolo de fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_close) 

    # Capta taqmanho horizontal da janela
        self.screen_width = self.root.winfo_screenwidth()

    # Capta tamanho vertical da janela
        self.screen_height = self.root.winfo_screenheight() 

    # Agrupa tamanho horizontal e vertical da janela
        self.screen = (self.screen_width, self.screen_height) 

    # Funcionalidade em testes. Nenhum desempenho adicional percebido
        self.use_hardware_acceleration = BooleanVar(value=False) 
        
    # Linha de funcionalidades adicionais
        self.frm_options = Frame(self.root, bd=2, relief='groove') 

    # Container dos widgets no lado esquerdo da tela
        self.frm_fields_left = Frame(self.root) 

    # Container dos widgets no lado direito da tela
        self.frm_fields_right = Frame(self.root) 
        
    # checkbox para funcionalidade de aceleração por hardware (ainda em testes)
        self.chck_hardware_acceleration = Checkbutton(
            self.frm_options,
            text="Use Hardware Acceleration (GPU/OpenCL)",
            variable=self.use_hardware_acceleration,)
        self.chck_hardware_acceleration.pack(padx=10, pady=10, side='right', anchor='nw')
    
    # Campo de inserção de urls
        self.frm_entry_name = Frame(self.frm_fields_right, bd=1, relief="sunken")
        self.label_url_name = Label(self.frm_entry_name, text="Nomear Url:")
        self.label_url_name.pack(anchor="nw")
        self.entry_url_name = Entry(self.frm_entry_name, width=50, state='normal', name="url_name")
        self.entry_url_name.pack(padx=10, pady=10, ipadx=4, ipady=4)
        self.frm_entry_name.pack(expand=True, fill="both")

        self.frm_entry_url = Frame(self.frm_fields_right, bd=1, relief="sunken")
        self.label_url = Label(self.frm_entry_url, text="Url:")
        self.label_url.pack(anchor="nw")
        self.entry_url = Entry(self.frm_entry_url, width=50, state='normal', name="url_name")
        self.entry_url.pack(padx=10, pady=10, ipadx=4, ipady=4)
        self.frm_entry_url.pack(expand=True, fill="both")

        
    # Area do Listbox para exibir e manipular URLs
        self.lbl_urls = Label(self.frm_fields_left, text="URLs Salvas:")
        self.lbl_urls.pack(padx=10, pady=(5, 0))
        
        self.listbox_urls = Listbox(self.frm_fields_left, selectmode=SINGLE, width=80, height=6) # selectmode setado para tipo de seleção simples (evitar editar mais de uma url ao mesmo tempo)
        self.listbox_urls.bind("<<ListboxSelect>>", self.on_select_from_listbox) # adicionado evento de seleção para ativar os botoes: EDITAR e APAGAR url selecionada
        self.listbox_urls.pack(padx=10, pady=5)

        self.frm_btt_left = Frame(self.frm_fields_left) # container dos botoes a esquerda

    # Botões de funcionalidades de URLs (á esquerda abaixo do listbox)
        self.frm_edit_btt = Frame(self.frm_btt_left, bd=2, relief='groove')

        self.bttn_edit_url = Button(self.frm_edit_btt, text="Edit Selected", fg="blue", command=lambda: self.edit_selected(), width=15)
        self.bttn_edit_url.config(state="disabled") # desabilitar botão ate que uma url seja selecionada
        self.bttn_edit_url.pack(padx=5, pady=2, side='left')

        self.bttn_remove_url = Button(self.frm_edit_btt, text="Remove Selected", fg="red", command=lambda: self.remove_selected(), width=15)
        self.bttn_remove_url.config(state="disabled") # desabilitar botão ate que uma url seja selecionada
        self.bttn_remove_url.pack(padx=5, pady=2, side='left')
        self.frm_edit_btt.pack(side="left", padx=10, pady=5)

        self.bttn_save_default = Button(self.frm_btt_left, text="Save to urls.json", fg="green", command=lambda: self.save_default_urls(), width=15)
        self.bttn_save_default.pack(padx=5, pady=2, side='bottom')

        self.frm_btt_left.pack(padx=10, pady=5, expand=True, fill='x')

    # Botoes de inserção de dados (lado direiro abaixo da caixa de entrada de dados)
        self.frm_btt_right = Frame(self.frm_fields_right)
        self.bttn_load_urls = Button(self.frm_btt_right, text="Load urls.json", command=lambda: self.load_urls(), width=15)
        self.bttn_load_urls.pack(padx=5, pady=2, side='left')

        self.bttn_select = Button(self.frm_btt_right, text="Select Videos", command=lambda: self.on_select_videos(), width=15)
        self.bttn_select.pack(padx=10, pady=10, side='left')

        self.bttn_add_url = Button(self.frm_btt_right, text="Add URL", command=lambda: self.add_url(), width=15)
        self.bttn_add_url.pack(padx=5, pady=2, side='left')
        
        self.frm_bttn_start = Frame(self.frm_fields_right, bd=2, relief='groove')
        self.bttn_start = Button(self.frm_bttn_start, text="Start", bg='green', fg='white', command=lambda: self.open_urls())
        self.bttn_start.pack(padx=10, pady=10, expand=True, fill='both')
        
    # Empacotamento e configuração dos containers de widgets
        self.frm_options.pack(expand=True, fill='x')
        self.frm_fields_left.pack(side='left', expand=True, fill='y')
        self.frm_fields_right.pack(side='left', expand=True, fill='y')

        self.frm_btt_left.pack()
        self.frm_btt_right.pack()
        self.frm_bttn_start.pack(side='bottom', expand=True, fill='both')
        
    # Pre carregamento de urls salvas em arquivo
        # default urls file in working directory
        self.default_urls_file = os.path.join(os.getcwd(), 'urls.json')
        # try auto-load default URLs
        self.load_default_urls()
    
    # Loop da janela principal
        self.root.mainloop()

    # Função para evento de seleção no listbox de urls
    def on_select_from_listbox(self, event):
        event.__dict__["widget"].config(fg="green")
        self.bttn_edit_url.config(state="normal")
        self.bttn_remove_url.config(state="normal")
        self.root.update_idletasks()

    # Função de carregamento em arquivos de video selecionados
    def on_select_videos(self):
        video_paths = filedialog.askopenfilenames(
        title="Select Video Files",
        filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov"), ("All files", "*.*")]
        )
        if not video_paths:
            return
        
        self.root.withdraw()  # Hide the main window
        videos = list(video_paths)
        
        # Criar tela de loading
        loading = LoadingScreen(self.root)
        
        # Rodar main() em thread separada
        def run_main():
            try:
                main(
                    videos, 
                    self.screen, 
                    use_gpu=self.use_hardware_acceleration.get(),
                    on_progress=loading.update_progress
                )
            except Exception as e:
                print(f"Erro ao reproduzir: {e}")
            finally:
                try:
                    loading.close()
                except:
                    pass
                self.root.deiconify()
                self.root.update_idletasks()
        
        thread = threading.Thread(target=run_main, daemon=False)
        thread.start()
        
    def add_url(self):
        name: str = self.entry_url_name.get().strip()
        url: str = self.entry_url.get().strip()
        saved = self.listbox_urls.get(0, END)

        if not name:
            messagebox.showwarning("Nomear Url", "Por favor insira um NOME para url a ser adicionada.")
            return
        if not url:
            messagebox.showwarning("Add URL", "Por favor insira uma url válida.")
            return
        
        if self.check_urls({name: url}):
            self.listbox_urls.insert(END, name.capitalize())
            with open("tmpUrl.json", 'w', encoding='utf-8') as f:
                json.dump({name: url}, f, ensure_ascii=False, indent=2)

            self.entry_url_name.delete(0, END)
            self.entry_url.delete(0, END)
        
        return

    def check_urls(self, entry):
        
        try: 
            with open("urls.json", "r", encoding="utf-8") as f:
                str_urls = json.load(f)  
        except (FileNotFoundError, json.JSONDecodeError):
            str_urls = []

        # 2. Extrai a chave e o valor de 'entry' uma única vez (evita repetir list())
        entry_name, entry_url = next(iter(entry.items()))

        # 3. Varre a lista de URLs salvas
        for tmp_url in str_urls:
            # Verifica se o nome (chave) já existe
            if entry_name in tmp_url:
                messagebox.showwarning(
                    "Nome Existente",
                    "Existe uma URL salva com este Nome, por favor escolha outro nome.",
                )
                return 0

            # Verifica se a URL (valor) já existe
            if entry_url in tmp_url.values():
                messagebox.showwarning(
                    "URL Existente",
                    "Esta URL ja está na Lista. Nenhum dado será salvo.",
                )
                return 0

        return True

    def remove_selected(self):
        sel = self.listbox_urls.curselection()
        if not sel:
            messagebox.showwarning("Remove URL", "Select a URL to remove.")
            return
        self.listbox_urls.delete(sel[0])

    def edit_selected(self):
        sel = self.listbox_urls.curselection()
        if not sel:
            messagebox.showwarning("Edit URL", "Select a URL to edit.")
            return
        idx = sel[0]
        val = self.listbox_urls.get(idx)

        self.listbox_urls.delete(idx)
        self.entry_url.delete(0, END)
        self.entry_url.insert(0, val)

    def save_urls(self):
        urls = list(self.listbox_urls.get(0, END))
        if not urls:
            messagebox.showwarning("Save URLs", "No URLs to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files','*.json')])
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(urls, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Save URLs", f"Saved {len(urls)} URLs to {file_path}")
        except Exception as e:
            messagebox.showerror("Save URLs", f"Error saving URLs: {e}")

    def load_urls(self):
        file_path = filedialog.askopenfilename(filetypes=[('JSON files','*.json'), ('All files','*.json')])
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list):
                messagebox.showerror("Load URLs", "JSON file must contain a list of URLs.")
                return
            self.listbox_urls.delete(0, END)
            for u in data:
                self.listbox_urls.insert(END, str(u))
            messagebox.showinfo("Load URLs", f"Loaded {len(data)} URLs from {file_path}")
        except Exception as e:
            messagebox.showerror("Load URLs", f"Error loading URLs: {e}")

    def load_default_urls(self):
        if not os.path.exists(self.default_urls_file):
            return
        try:
            with open(self.default_urls_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list):
                return
            self.listbox_urls.delete(0, END)
            for u in data:
                self.listbox_urls.insert(END, str(u))
        except Exception:
            return

    def save_default_urls(self):
        urls = list(self.listbox_urls.get(0, END))
        if not urls:
            messagebox.showwarning("Save URLs", "No URLs to save.")
            return
        try:
            with open(self.default_urls_file, 'w', encoding='utf-8') as f:
                json.dump(urls, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Save URLs", f"Saved {len(urls)} URLs to {self.default_urls_file}")
        except Exception as e:
            messagebox.showerror("Save URLs", f"Error saving URLs: {e}")

    def open_urls(self):

        urls = list(self.listbox_urls.get(0, END))
        print(urls)
        if not urls:
            messagebox.showwarning("Open URLs", "No URLs to open. Add or load URLs first.")
            return
        self.root.withdraw()
        
        # Criar tela de loading
        loading = LoadingScreen(self.root)
        
        # Rodar main() em thread separada
        def run_main():
            try:
                main(
                    urls, 
                    self.screen, 
                    use_gpu=self.use_hardware_acceleration.get(),
                    on_progress=loading.update_progress
                )
            except Exception as e:
                print(f"Erro ao reproduzir: {e}")
            finally:
                try:
                    loading.close()
                except:
                    pass
                self.root.deiconify()
                self.root.update_idletasks()
        
        thread = threading.Thread(target=run_main, daemon=False)
        thread.start()
        
    def on_close(self):
        self.root.destroy()


if __name__ == "__main__":
    main_window = MainWindow()
    
