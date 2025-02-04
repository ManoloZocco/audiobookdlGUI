from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QGroupBox, QGridLayout,
                               QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
                               QPushButton, QFileDialog, QCheckBox, QComboBox, QPlainTextEdit)
from PySide6.QtCore import Qt, Signal  # Modifica: aggiunto Signal
from PySide6.QtGui import QIcon
import subprocess, threading, os, sys, json
from functools import partial  # aggiunto insieme agli altri import

class AudiobookDownloaderGUI(QMainWindow):
    output_signal = Signal(str)  # Nuovo segnale per aggiornare l'output in modo thread-safe

    def __init__(self):
        super().__init__()
        # Definizione lingua predefinita e dizionario traduzioni
        self.lang = 'it'
        self.translations = {
            'it': {
                'window_title': "Audiobook Downloader GUI",
                'url_label': "URL(s):",
                'url_tooltip': "URL della pagina dove ascolti l'audiolibro",
                'input_file_label': "File di Input:",
                'input_file_tooltip': "Seleziona un file di input (ad es. un file di testo contenente una lista di URL da elaborare).",
                'username_label': "Username:",
                'username_tooltip': "Username per il servizio (Richiesto per il login)",
                'password_label': "Password:",
                'password_tooltip': "Password per il servizio (Richiesto per il login)",
                'library_label': "Library:",
                'library_tooltip': "Libreria specifica del servizio (A volte richiesto per il login)",
                'cookie_file_label': "Cookie File:",
                'cookie_file_tooltip': "Percorso del file cookie in formato Netscape",
                'save_dir_label': "Directory di Salvataggio:",
                'save_dir_tooltip': "Seleziona la directory in cui salvare i file.",
                'output_template_label': "Output Template:",
                'output_template_tooltip': ("Template per il nome del file di output. Puoi usare i seguenti tag:\n"
                                            "{title} - Titolo del libro\n"
                                            "{author} - Autore\n"
                                            "{series} - Serie\n"
                                            "{narrator} - Narratore"),
                'remove_chars_label': "Rimuovi caratteri:",
                'remove_chars_tooltip': "Lista di caratteri da rimuovere dal percorso di output",
                'output_format_label': "Output Format:",
                'output_format_tooltip': "Formato del file di output",
                'config_file_label': "Config File:",
                'config_file_tooltip': "Seleziona il file di configurazione.",
                'advanced_show': "Mostra Opzioni Avanzate",
                'advanced_hide': "Nascondi Opzioni Avanzate",
                'download_button': "Avvia Download",
                'basic_group': "Opzioni di Base",
                'advanced_group': "Opzioni Avanzate",
                'browse_button': "Sfoglia",
                'remember_credentials': "Ricorda credenziali",
                'combine_files': "Combina file",
                'combine_files_tooltip': "Combina tutti i file di output in un unico file (richiede ffmpeg)",
                'debug_mode': "Debug mode",
                'debug_mode_tooltip': "Mostra informazioni di debug",
                'quiet_mode': "Quiet mode",
                'print_output': "Print output",
                'cover_only': "Solo cover",
                'cover_only_tooltip': "Scarica solo la copertina",
                'no_chapters': "No chapters",
                'no_chapters_tooltip': "Non includere i capitoli nel file di output",
                'verbose_ffmpeg': "Verbose ffmpeg",
                'verbose_ffmpeg_tooltip': "Mostra l'output di ffmpeg nel terminale",
                'write_metadata': "Scrivi JSON metadata"
            },
            'en': {
                'window_title': "Audiobook Downloader GUI",
                'url_label': "URL(s):",
                'url_tooltip': "The url of the page where you listen to the audiobook",
                'input_file_label': "Input File:",
                'input_file_tooltip': "Select an input file (e.g. a text file containing a list of URLs to process).",
                'username_label': "Username:",
                'username_tooltip': "Username to source (Required when using login)",
                'password_label': "Password:",
                'password_tooltip': "Password to source (Required when using login)",
                'library_label': "Library:",
                'library_tooltip': "Specific library on service (Sometimes required when using login)",
                'cookie_file_label': "Cookie File:",
                'cookie_file_tooltip': "Path to a Netscape cookie file",
                'save_dir_label': "Save Directory:",
                'save_dir_tooltip': "Select the directory to save files.",
                'output_template_label': "Output Template:",
                'output_template_tooltip': ("Template for output filename. You can use these tags:\n"
                                            "{title} - Book title\n"
                                            "{author} - Author\n"
                                            "{series} - Series\n"
                                            "{narrator} - Narrator"),
                'remove_chars_label': "Remove Characters:",
                'remove_chars_tooltip': "List of characters that will be removed from output path",
                'output_format_label': "Output Format:",
                'output_format_tooltip': "Output file format",
                'config_file_label': "Config File:",
                'config_file_tooltip': "Select the configuration file.",
                'advanced_show': "Show Advanced Options",
                'advanced_hide': "Hide Advanced Options",
                'download_button': "Start Download",
                'basic_group': "Basic Options",
                'advanced_group': "Advanced Options",
                'browse_button': "Browse",
                'remember_credentials': "Remember credentials",
                'combine_files': "Combine files",
                'combine_files_tooltip': "Combine all output files into a single file (requires ffmpeg)",
                'debug_mode': "Debug mode",
                'debug_mode_tooltip': "Print debug information",
                'quiet_mode': "Quiet mode",
                'print_output': "Print output",
                'cover_only': "Cover only",
                'cover_only_tooltip': "Only download cover",
                'no_chapters': "No chapters",
                'no_chapters_tooltip': "Don't include chapters in output file",
                'verbose_ffmpeg': "Verbose ffmpeg",
                'verbose_ffmpeg_tooltip': "Show ffmpeg output in terminal",
                'write_metadata': "Write JSON metadata"
            }
        }
        self.setWindowTitle(self.translations[self.lang]['window_title'])
        self.setMinimumSize(900, 450)
        
        # Central widget e layout principale
        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QVBoxLayout(central)
        
        # Selettore di lingua
        language_container = QWidget()
        lang_layout = QHBoxLayout(language_container)
        lang_label = QLabel("Language / Lingua:")
        lang_layout.addWidget(lang_label)
        self.lang_selector = QComboBox()
        self.lang_selector.addItem(QIcon("assets/flags/it_flag.png"), "Italiano")
        self.lang_selector.addItem(QIcon("assets/flags/en_flag.png"), "English")
        self.lang_selector.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_selector)
        lang_layout.addStretch()
        self.layout.addWidget(language_container)
        
        # Contenitore per il contenuto principale (traducibile)
        self.content_container = QWidget()
        self.layout.addWidget(self.content_container)
        self.create_widgets()
        self.load_credentials()
        self.center_window()
        # Collega il segnale per aggiornare l'output
        self.output_signal.connect(self.output_text.appendPlainText)
    
    @staticmethod
    def label_with_help(text, tooltip):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(text)
        layout.addWidget(label)
        help_btn = QPushButton("?")
        help_btn.setFixedSize(20, 20)
        help_btn.setToolTip(tooltip)
        help_btn.setFlat(True)
        layout.addWidget(help_btn)
        # RIMOSSO layout.addStretch() PER AVVICINARE IL PULSANTE '?' ALLA LABEL
        return container

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

    def create_widgets(self):
        translations = self.translations[self.lang]
        
        # Layout V principale del content_container
        content_layout = QVBoxLayout(self.content_container)
        
        # Layout H per raggruppare Basic e Advanced
        options_layout = QHBoxLayout()
        
        # Opzioni di Base
        basic_group = QGroupBox(translations['basic_group'])
        basic_layout = QGridLayout(basic_group)
        basic_layout.addWidget(self.label_with_help(translations['url_label'], translations['url_tooltip']), 0, 0)
        self.url_text = QTextEdit()
        self.url_text.setFixedHeight(60)
        basic_layout.addWidget(self.url_text, 0, 1, 1, 2)
        
        basic_layout.addWidget(self.label_with_help(translations['input_file_label'], translations['input_file_tooltip']), 1, 0)
        self.input_file_entry = QLineEdit()
        basic_layout.addWidget(self.input_file_entry, 1, 1)
        input_file_btn = QPushButton(translations['browse_button'])
        input_file_btn.clicked.connect(self.browse_input_file)
        basic_layout.addWidget(input_file_btn, 1, 2)
        
        basic_layout.addWidget(self.label_with_help(translations['username_label'], translations['username_tooltip']), 2, 0)
        self.username_entry = QLineEdit()
        basic_layout.addWidget(self.username_entry, 2, 1)
        
        basic_layout.addWidget(self.label_with_help(translations['password_label'], translations['password_tooltip']), 3, 0)
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        basic_layout.addWidget(self.password_entry, 3, 1)
        
        self.remember_cb = QCheckBox(translations['remember_credentials'])
        basic_layout.addWidget(self.remember_cb, 4, 1)
        
        basic_layout.addWidget(self.label_with_help(translations['library_label'], translations['library_tooltip']), 5, 0)
        self.library_entry = QLineEdit()
        basic_layout.addWidget(self.library_entry, 5, 1)
        
        basic_layout.addWidget(self.label_with_help(translations['cookie_file_label'], translations['cookie_file_tooltip']), 6, 0)
        self.cookie_entry = QLineEdit()
        basic_layout.addWidget(self.cookie_entry, 6, 1)
        cookie_btn = QPushButton(translations['browse_button'])
        cookie_btn.clicked.connect(self.browse_cookie_file)
        basic_layout.addWidget(cookie_btn, 6, 2)
        
        basic_layout.addWidget(self.label_with_help(translations['save_dir_label'], translations['save_dir_tooltip']), 7, 0)
        self.save_dir_entry = QLineEdit()
        basic_layout.addWidget(self.save_dir_entry, 7, 1)
        save_dir_btn = QPushButton(translations['browse_button'])
        save_dir_btn.clicked.connect(self.browse_save_directory)
        basic_layout.addWidget(save_dir_btn, 7, 2)
        
        options_layout.addWidget(basic_group, 2)
        
        # Opzioni Avanzate
        self.advanced_group = QGroupBox(translations['advanced_group'])
        advanced_layout = QGridLayout(self.advanced_group)
        
        # Label + help per Output Template
        advanced_layout.addWidget(
            self.label_with_help(
                translations['output_template_label'],
                translations['output_template_tooltip']
            ),
            0, 0,
            Qt.AlignmentFlag.AlignTop  # facoltativo, se vuoi tenerla in alto
        )

        # Layout verticale: la QLineEdit e sotto i pulsanti
        template_vlayout = QVBoxLayout()
        self.output_template_entry = QLineEdit("{title}")
        template_vlayout.addWidget(self.output_template_entry)

        # Layout orizzontale per i pulsanti tag
        tag_btn_layout = QHBoxLayout()
        for tag in ['{title}', '{author}', '{series}', '{narrator}']:
            tag_btn = QPushButton(tag)
            tag_btn.setFixedWidth(80)
            tag_btn.clicked.connect(partial(self.insert_tag, tag))
            tag_btn_layout.addWidget(tag_btn)
        template_vlayout.addLayout(tag_btn_layout)

        # Aggiungiamo il layout verticale alla griglia
        advanced_layout.addLayout(template_vlayout, 0, 1, 1, 2)

        # Rimuovi caratteri
        advanced_layout.addWidget(self.label_with_help(translations['remove_chars_label'], translations['remove_chars_tooltip']), 1, 0)
        self.remove_chars_entry = QLineEdit()
        advanced_layout.addWidget(self.remove_chars_entry, 1, 1)
        
        # Output Format
        advanced_layout.addWidget(self.label_with_help(translations['output_format_label'], translations['output_format_tooltip']), 2, 0)
        self.output_format_entry = QLineEdit()
        advanced_layout.addWidget(self.output_format_entry, 2, 1)
        
        # Config File
        advanced_layout.addWidget(self.label_with_help(translations['config_file_label'], translations['config_file_tooltip']), 3, 0)
        self.config_entry = QLineEdit()
        advanced_layout.addWidget(self.config_entry, 3, 1)
        config_btn = QPushButton(translations['browse_button'])
        config_btn.clicked.connect(self.browse_config_file)
        advanced_layout.addWidget(config_btn, 3, 2)
        
        # CheckBox vari
        self.combine_cb = QCheckBox(translations['combine_files'])
        self.combine_cb.setToolTip(translations['combine_files_tooltip'])
        advanced_layout.addWidget(self.combine_cb, 4, 0)
        
        self.debug_cb = QCheckBox(translations['debug_mode'])
        self.debug_cb.setToolTip(translations['debug_mode_tooltip'])
        advanced_layout.addWidget(self.debug_cb, 4, 1)
        
        self.quiet_cb = QCheckBox(translations['quiet_mode'])
        advanced_layout.addWidget(self.quiet_cb, 4, 2)
        
        self.print_output_cb = QCheckBox(translations['print_output'])
        advanced_layout.addWidget(self.print_output_cb, 5, 0)
        
        self.cover_cb = QCheckBox(translations['cover_only'])
        self.cover_cb.setToolTip(translations['cover_only_tooltip'])
        advanced_layout.addWidget(self.cover_cb, 5, 1)
        
        self.no_chapters_cb = QCheckBox(translations['no_chapters'])
        self.no_chapters_cb.setToolTip(translations['no_chapters_tooltip'])
        advanced_layout.addWidget(self.no_chapters_cb, 5, 2)
        
        self.verbose_ffmpeg_cb = QCheckBox(translations['verbose_ffmpeg'])
        self.verbose_ffmpeg_cb.setToolTip(translations['verbose_ffmpeg_tooltip'])
        advanced_layout.addWidget(self.verbose_ffmpeg_cb, 6, 0)
        
        self.write_json_metadata_cb = QCheckBox(translations['write_metadata'])
        advanced_layout.addWidget(self.write_json_metadata_cb, 6, 1)
        
        options_layout.addWidget(self.advanced_group, 1)
        self.advanced_group.hide()
        
        content_layout.addLayout(options_layout)
        
        # Pulsante per mostra/nascondere opzioni avanzate
        self.toggle_button = QPushButton(translations['advanced_show'])
        self.toggle_button.clicked.connect(self.toggle_advanced)
        content_layout.addWidget(self.toggle_button)
        
        # Pulsante Download
        self.download_button = QPushButton(translations['download_button'])
        self.download_button.clicked.connect(self.start_download)
        content_layout.addWidget(self.download_button)
        
        # Output
        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)
        content_layout.addWidget(self.output_text)

    def change_language(self):
        # Aggiorna la lingua in base all'indice selezionato
        self.lang = 'it' if self.lang_selector.currentIndex() == 0 else 'en'
        self.setWindowTitle(self.translations[self.lang]['window_title'])
        
        # Rimuovi il vecchio contenitore
        if self.content_container:
            self.content_container.deleteLater()
        
        # Crea un nuovo contenitore
        self.content_container = QWidget()
        self.layout.addWidget(self.content_container)
        
        # Ricrea i widget
        self.create_widgets()
        
        # Ridimensiona e centra
        self.adjustSize()
        self.center_window()
    
    def toggle_advanced(self):
        translations = self.translations[self.lang]
        if self.advanced_group.isVisible():
            self.advanced_group.hide()
            self.toggle_button.setText(translations['advanced_show'])
        else:
            self.advanced_group.show()
            self.toggle_button.setText(translations['advanced_hide'])
        self.adjustSize()
        self.center_window()
    
    def browse_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona File di Input", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            self.input_file_entry.setText(file_path)
    
    def browse_cookie_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona Cookie File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            self.cookie_entry.setText(file_path)
    
    def browse_config_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona Config File", "", "TOML Files (*.toml);;All Files (*)")
        if file_path:
            self.config_entry.setText(file_path)
    
    def browse_save_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Seleziona Directory di Salvataggio")
        if dir_path:
            self.save_dir_entry.setText(dir_path)
    
    def load_credentials(self):
        credentials_file = os.path.expanduser("~/.audiobookdl_credentials.json")
        if os.path.exists(credentials_file):
            try:
                with open(credentials_file, "r") as f:
                    data = json.load(f)
                self.username_entry.setText(data.get("username", ""))
                self.password_entry.setText(data.get("password", ""))
                self.remember_cb.setChecked(data.get("remember", False))
                self.save_dir_entry.setText(data.get("download_dir", ""))
            except Exception:
                pass
    
    def save_credentials(self):
        if self.remember_cb.isChecked():
            data = {
                "username": self.username_entry.text().strip(),
                "password": self.password_entry.text().strip(),
                "remember": True,
                "download_dir": self.save_dir_entry.text().strip()
            }
            credentials_file = os.path.expanduser("~/.audiobookdl_credentials.json")
            try:
                with open(credentials_file, "w") as f:
                    json.dump(data, f)
            except Exception:
                pass
    
    def start_download(self):
        self.save_credentials()
        cmd = ["audiobook-dl"]
        
        # Debug: stampa il contenuto grezzo della textbox
        raw_content = self.url_text.toPlainText()
        self.output_signal.emit(f"Contenuto grezzo della textbox:\n{raw_content}\n")
        
        # Gestione degli URL
        urls_raw = raw_content.strip().splitlines()
        self.output_signal.emit(f"URLs trovati: {len(urls_raw)}\n")
        
        urls = []
        for u in urls_raw:
            if u and u.strip():
                stripped_url = u.strip()
                self.output_signal.emit(f"Processando URL: {stripped_url}\n")
                # Utilizza l'URL così com'è, senza trasformazione
                urls.append(stripped_url)
                self.output_signal.emit(f"URL aggiunto: {stripped_url}\n")

        if not urls:  # Se non ci sono URL validi, mostra un errore
            self.output_signal.emit("Errore: Nessun URL valido fornito. Assicurati di aver inserito almeno un URL valido.\n")
            return
        
        # Aggiungi gli URL al comando
        cmd.extend(urls)
        
        input_file = self.input_file_entry.text().strip()
        if input_file:
            cmd.extend(["--input-file", input_file])
        cookie_file = self.cookie_entry.text().strip()
        if cookie_file:
            cmd.extend(["--cookies", cookie_file])
        if self.combine_cb.isChecked():
            cmd.append("--combine")
        output_template = self.output_template_entry.text().strip()
        if output_template:
            cmd.extend(["--output", output_template])
        remove_chars = self.remove_chars_entry.text().strip()
        if remove_chars:
            cmd.extend(["--remove-chars", remove_chars])
        if self.debug_cb.isChecked():
            cmd.append("--debug")
        if self.quiet_cb.isChecked():
            cmd.append("--quiet")
        if self.print_output_cb.isChecked():
            cmd.append("--print-output")
        if self.cover_cb.isChecked():
            cmd.append("--cover")
        if self.no_chapters_cb.isChecked():
            cmd.append("--no-chapters")
        output_format = self.output_format_entry.text().strip()
        if output_format:
            cmd.extend(["-f", output_format])
        if self.verbose_ffmpeg_cb.isChecked():
            cmd.append("--verbose-ffmpeg")
        username = self.username_entry.text().strip()
        if username:
            cmd.extend(["--username", username])
        password = self.password_entry.text().strip()
        if password:
            cmd.extend(["--password", password])
        library = self.library_entry.text().strip()
        if library:
            cmd.extend(["--library", library])
        if self.write_json_metadata_cb.isChecked():
            cmd.append("--write-json-metadata")
        config_file = self.config_entry.text().strip()
        if config_file:
            cmd.extend(["--config", config_file])
        
        download_dir = self.save_dir_entry.text().strip() or None

        # Filtra la lista per eliminare eventuali None
        cmd = [x for x in cmd if x is not None]
        
        self.output_text.clear()
        # Modifica qui: converti tutti gli elementi in stringa, anche se sono None.
        self.output_text.appendPlainText("Esecuzione del comando:\n" + " ".join(str(x) for x in cmd) + "\n")
        
        threading.Thread(target=self.run_command, args=(cmd, download_dir), daemon=True).start()
    
    def run_command(self, cmd, cwd=None):
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=cwd
            )
            for line in iter(process.stdout.readline, ''):
                self.output_signal.emit(line)  # Modifica: usa il segnale invece di aggiornare direttamente
            process.stdout.close()
            process.wait()
            self.output_signal.emit("\nDownload terminato.\n")
        except Exception as e:
            self.output_signal.emit("\nErrore: " + str(e) + "\n")
    
    def center_window(self):
        frameGm = self.frameGeometry()
        centerPoint = QApplication.primaryScreen().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def insert_tag(self, tag):
        """Inserisce il tag alla fine del testo corrente nel campo output_template"""
        current_text = self.output_template_entry.text()
        if current_text and not current_text.endswith("}"):
            current_text += "_"
        self.output_template_entry.setText(current_text + tag)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudiobookDownloaderGUI()
    window.show()
    sys.exit(app.exec())
