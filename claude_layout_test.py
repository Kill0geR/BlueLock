import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QLabel,
                             QScrollArea, QFrame, QTreeWidget, QTreeWidgetItem,
                             QSplitter, QTextEdit, QGridLayout, QGraphicsBlurEffect)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPainter, QIcon
import random


class GlassWidget(QWidget):
    """Widget mit echtem Glassmorphism-Effekt"""

    def __init__(self, parent=None, blur_radius=0):
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if blur_radius > 0:
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(blur_radius)
            self.setGraphicsEffect(blur)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Glassmorphism-Effekt: dunkel, semi-transparent mit leichtem Rand
        painter.setBrush(QColor(30, 30, 40, 180))
        painter.setPen(QColor(255, 255, 255, 30))
        painter.drawRoundedRect(self.rect(), 15, 15)


class ModernButton(QPushButton):
    """Moderner Button mit Hover-Effekt und Glassmorphism"""

    def __init__(self, text="", icon_text="", parent=None):
        super().__init__(text, parent)
        self.icon_text = icon_text
        self.setMinimumHeight(38)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(50, 50, 60, 100);
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 8px;
                color: rgba(255, 255, 255, 200);
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(70, 70, 80, 140);
                border: 1px solid rgba(255, 255, 255, 60);
            }
            QPushButton:pressed {
                background-color: rgba(40, 40, 50, 160);
            }
        """)


class PasswordEntry(QFrame):
    """Einzelner Passwort-Eintrag"""

    def __init__(self, title, username, password, url="", parent=None):
        super().__init__(parent)
        self.title = title
        self.username = username
        self.password = password
        self.url = url
        self.password_visible = False

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(50, 50, 60, 100);
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 12px;
                padding: 15px;
            }
            QFrame:hover {
                background-color: rgba(60, 60, 70, 120);
                border: 1px solid rgba(255, 255, 255, 60);
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Titel
        title_label = QLabel(f"🔐 {title}")
        title_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 230);
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)

        # Username
        username_layout = QHBoxLayout()
        username_label = QLabel("👤 Username:")
        username_label.setStyleSheet("color: rgba(255, 255, 255, 180); background: transparent; border: none;")
        username_value = QLabel(username)
        username_value.setStyleSheet("color: rgba(255, 255, 255, 230); background: transparent; border: none;")
        username_layout.addWidget(username_label)
        username_layout.addWidget(username_value)
        username_layout.addStretch()

        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("🔑 Password:")
        password_label.setStyleSheet("color: rgba(255, 255, 255, 180); background: transparent; border: none;")
        self.password_value = QLabel("••••••••")
        self.password_value.setStyleSheet("color: rgba(255, 255, 255, 230); background: transparent; border: none;")

        show_btn = QPushButton("👁")
        show_btn.setFixedSize(30, 30)
        show_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        show_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 120, 200, 120);
                border: 1px solid rgba(100, 160, 240, 80);
                border-radius: 15px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(80, 140, 220, 150);
            }
        """)
        show_btn.clicked.connect(self.toggle_password)

        copy_btn = QPushButton("📋")
        copy_btn.setFixedSize(30, 30)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 200, 100, 120);
                border: 1px solid rgba(140, 240, 140, 80);
                border-radius: 15px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(120, 220, 120, 150);
            }
        """)
        copy_btn.clicked.connect(self.copy_password)

        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_value)
        password_layout.addWidget(show_btn)
        password_layout.addWidget(copy_btn)
        password_layout.addStretch()

        # URL (falls vorhanden)
        if url:
            url_layout = QHBoxLayout()
            url_label = QLabel("🌐 URL:")
            url_label.setStyleSheet("color: rgba(255, 255, 255, 180); background: transparent; border: none;")
            url_value = QLabel(url)
            url_value.setStyleSheet("color: rgba(100, 160, 240, 230); background: transparent; border: none;")
            url_layout.addWidget(url_label)
            url_layout.addWidget(url_value)
            url_layout.addStretch()
            layout.addLayout(url_layout)

        layout.addWidget(title_label)
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)

        self.setLayout(layout)

    def toggle_password(self):
        """Zeigt/Versteckt das Passwort"""
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_value.setText(self.password)
        else:
            self.password_value.setText("••••••••")

    def copy_password(self):
        """Kopiert das Passwort in die Zwischenablage"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.password)
        # Visuelles Feedback
        original_style = self.styleSheet()
        self.setStyleSheet(original_style + """
            QFrame {
                border: 1px solid rgba(100, 200, 100, 150);
            }
        """)
        QApplication.processEvents()
        import time
        time.sleep(0.2)
        self.setStyleSheet(original_style)


class KeePassUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GlassPass - Password Manager")
        self.setGeometry(100, 100, 1100, 700)

        # Transparentes Fenster aktivieren
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Fake Passwort-Daten
        self.passwords = {
            "Social Media": [
                {"title": "Facebook", "username": "max.mustermann@email.com", "password": "Fb$ecur3P@ss2024",
                 "url": "https://facebook.com"},
                {"title": "Instagram", "username": "max_insta", "password": "Inst@Gr4m!2024",
                 "url": "https://instagram.com"},
                {"title": "Twitter/X", "username": "@max_tweets", "password": "Tw1tt3r$P@ss",
                 "url": "https://twitter.com"},
            ],
            "Banking": [
                {"title": "Deutsche Bank", "username": "max.mustermann", "password": "D8!bank#Secure99",
                 "url": "https://deutsche-bank.de"},
                {"title": "PayPal", "username": "max.mustermann@email.com", "password": "P@yP4l$2024!",
                 "url": "https://paypal.com"},
                {"title": "N26", "username": "max.mustermann@email.com", "password": "N26#Secure!2024",
                 "url": "https://n26.com"},
            ],
            "Email": [
                {"title": "Gmail (Personal)", "username": "max.mustermann@gmail.com", "password": "Gm41l#Str0ng2024",
                 "url": "https://gmail.com"},
                {"title": "Outlook (Work)", "username": "max.mustermann@firma.com", "password": "W0rk$M@il2024!",
                 "url": "https://outlook.com"},
            ],
            "Shopping": [
                {"title": "Amazon", "username": "max.mustermann@email.com", "password": "Am4z0n!Sh0p24",
                 "url": "https://amazon.de"},
                {"title": "eBay", "username": "max_shopper", "password": "3B4y$ecure!2024", "url": "https://ebay.de"},
            ],
            "Streaming": [
                {"title": "Netflix", "username": "max.mustermann@email.com", "password": "N3tfl1x!Watch24",
                 "url": "https://netflix.com"},
                {"title": "Spotify", "username": "max.mustermann@email.com", "password": "Sp0t1fy#Music!",
                 "url": "https://spotify.com"},
                {"title": "Disney+", "username": "max_disney", "password": "D1sn3y+Pl@y24",
                 "url": "https://disneyplus.com"},
            ],
        }

        self.init_ui()

    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        # Haupt-Widget
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(central_widget)

        # Haupt-Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        central_widget.setLayout(main_layout)

        # Hintergrund-Container
        background = QWidget()
        background.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(26, 26, 46, 180), 
                    stop:0.5 rgba(22, 33, 62, 160), 
                    stop:1 rgba(15, 52, 96, 180));
                border-radius: 20px;
            }
        """)

        bg_layout = QVBoxLayout()
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(0)
        background.setLayout(bg_layout)

        # Header
        self.create_header(bg_layout)

        # Suchleiste
        self.create_search_bar(bg_layout)

        # Hauptbereich (Kategorien + Passwörter)
        self.create_main_area(bg_layout)

        # Statusleiste
        self.create_status_bar(bg_layout)

        main_layout.addWidget(background)

        # Schließen-Button
        self.add_close_button()

    def create_header(self, parent_layout):
        """Erstellt den Header-Bereich"""
        header = GlassWidget()
        header.setFixedHeight(80)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(25, 15, 25, 15)
        header.setLayout(header_layout)

        # Logo und Titel
        title_label = QLabel("🔐 GlassPass")
        title_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 230);
                font-size: 28px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)

        subtitle = QLabel("Secure Password Manager")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 150);
                font-size: 14px;
                background: transparent;
                border: none;
            }
        """)

        title_container = QVBoxLayout()
        title_container.addWidget(title_label)
        title_container.addWidget(subtitle)

        header_layout.addLayout(title_container)
        header_layout.addStretch()

        # Action Buttons
        new_btn = ModernButton("➕ New Entry")
        generate_btn = ModernButton("🎲 Generate")
        settings_btn = ModernButton("⚙️ Settings")

        header_layout.addWidget(new_btn)
        header_layout.addWidget(generate_btn)
        header_layout.addWidget(settings_btn)

        parent_layout.addWidget(header)

    def create_search_bar(self, parent_layout):
        """Erstellt die Suchleiste"""
        search_container = GlassWidget()
        search_container.setFixedHeight(70)

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(25, 15, 25, 15)
        search_container.setLayout(search_layout)

        # Suchfeld
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("🔍 Search passwords...")
        self.search_field.setMinimumHeight(40)
        self.search_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(50, 50, 60, 100);
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 20px;
                padding: 10px 20px;
                color: rgba(255, 255, 255, 230);
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(100, 160, 240, 150);
                background-color: rgba(60, 60, 70, 120);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 100);
            }
        """)
        self.search_field.textChanged.connect(self.filter_passwords)

        search_layout.addWidget(self.search_field)

        parent_layout.addWidget(search_container)

    def create_main_area(self, parent_layout):
        """Erstellt den Hauptbereich mit Kategorien und Passwörtern"""
        main_container = QWidget()
        main_container.setStyleSheet("background: transparent;")

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        main_container.setLayout(main_layout)

        # Linke Seite: Kategorien
        categories_container = GlassWidget()
        categories_container.setFixedWidth(250)

        cat_layout = QVBoxLayout()
        cat_layout.setContentsMargins(15, 15, 15, 15)
        categories_container.setLayout(cat_layout)

        cat_title = QLabel("Categories")
        cat_title.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 200);
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 5px;
            }
        """)
        cat_layout.addWidget(cat_title)

        # Kategorien als Buttons
        self.category_buttons = {}
        icons = {"Social Media": "📱", "Banking": "🏦", "Email": "📧",
                 "Shopping": "🛒", "Streaming": "🎬"}

        for category in self.passwords.keys():
            icon = icons.get(category, "📁")
            btn = ModernButton(f"{icon} {category}")
            btn.setMinimumHeight(45)
            btn.clicked.connect(lambda checked, c=category: self.show_category(c))
            cat_layout.addWidget(btn)
            self.category_buttons[category] = btn

        cat_layout.addStretch()

        # Rechte Seite: Passwort-Liste
        self.passwords_container = QWidget()
        self.passwords_container.setStyleSheet("background: transparent;")

        passwords_layout = QVBoxLayout()
        passwords_layout.setContentsMargins(0, 0, 0, 0)
        self.passwords_container.setLayout(passwords_layout)

        # Scroll-Bereich für Passwörter
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 20);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 80);
                border-radius: 5px;
            }
        """)

        self.passwords_list = QWidget()
        self.passwords_list.setStyleSheet("background: transparent;")
        self.passwords_list_layout = QVBoxLayout()
        self.passwords_list_layout.setSpacing(15)
        self.passwords_list_layout.setContentsMargins(10, 10, 10, 10)
        self.passwords_list.setLayout(self.passwords_list_layout)

        scroll_area.setWidget(self.passwords_list)
        passwords_layout.addWidget(scroll_area)

        main_layout.addWidget(categories_container)
        main_layout.addWidget(self.passwords_container)

        parent_layout.addWidget(main_container)

        # Zeige initial alle Passwörter
        self.show_all_passwords()

    def create_status_bar(self, parent_layout):
        """Erstellt die Statusleiste"""
        status_bar = GlassWidget()
        status_bar.setFixedHeight(50)

        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(25, 10, 25, 10)
        status_bar.setLayout(status_layout)

        # Statistiken
        total_entries = sum(len(entries) for entries in self.passwords.values())

        stats_label = QLabel(f"📊 Total Entries: {total_entries}  |  🔒 Database: Encrypted  |  ✅ Last Sync: Just now")
        stats_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 180);
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)

        status_layout.addWidget(stats_label)
        status_layout.addStretch()

        lock_btn = ModernButton("🔒 Lock")
        status_layout.addWidget(lock_btn)

        parent_layout.addWidget(status_bar)

    def show_category(self, category):
        """Zeigt Passwörter einer bestimmten Kategorie"""
        # Lösche aktuelle Liste
        while self.passwords_list_layout.count():
            child = self.passwords_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Füge Passwörter der Kategorie hinzu
        for entry in self.passwords[category]:
            password_widget = PasswordEntry(
                entry["title"],
                entry["username"],
                entry["password"],
                entry.get("url", "")
            )
            self.passwords_list_layout.addWidget(password_widget)

        self.passwords_list_layout.addStretch()

    def show_all_passwords(self):
        """Zeigt alle Passwörter"""
        # Lösche aktuelle Liste
        while self.passwords_list_layout.count():
            child = self.passwords_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Füge alle Passwörter hinzu, gruppiert nach Kategorie
        for category, entries in self.passwords.items():
            # Kategorie-Header
            cat_header = QLabel(f"📁 {category}")
            cat_header.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 220);
                    font-size: 18px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                    padding: 10px 5px;
                }
            """)
            self.passwords_list_layout.addWidget(cat_header)

            for entry in entries:
                password_widget = PasswordEntry(
                    entry["title"],
                    entry["username"],
                    entry["password"],
                    entry.get("url", "")
                )
                self.passwords_list_layout.addWidget(password_widget)

        self.passwords_list_layout.addStretch()

    def filter_passwords(self, text):
        """Filtert Passwörter basierend auf Suchtext"""
        search_text = text.lower()

        if not search_text:
            self.show_all_passwords()
            return

        # Lösche aktuelle Liste
        while self.passwords_list_layout.count():
            child = self.passwords_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Durchsuche alle Passwörter
        found_any = False
        for category, entries in self.passwords.items():
            for entry in entries:
                if (search_text in entry["title"].lower() or
                        search_text in entry["username"].lower() or
                        search_text in entry.get("url", "").lower()):
                    password_widget = PasswordEntry(
                        entry["title"],
                        entry["username"],
                        entry["password"],
                        entry.get("url", "")
                    )
                    self.passwords_list_layout.addWidget(password_widget)
                    found_any = True

        if not found_any:
            no_results = QLabel("🔍 No passwords found")
            no_results.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 150);
                    font-size: 16px;
                    background: transparent;
                    border: none;
                    padding: 20px;
                }
            """)
            self.passwords_list_layout.addWidget(no_results)

        self.passwords_list_layout.addStretch()

    def add_close_button(self):
        """Fügt einen Schließen-Button hinzu"""
        close_btn = QPushButton("✕")
        close_btn.setParent(self.centralWidget())
        close_btn.setGeometry(self.width() - 45, 10, 35, 35)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 80, 80, 150);
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 17px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 100, 100, 180);
            }
        """)
        close_btn.clicked.connect(self.close)
        close_btn.show()

    def mousePressEvent(self, event):
        """Ermöglicht das Verschieben des Fensters"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        """Verschiebt das Fenster"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_pos'):
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()


def main():
    app = QApplication(sys.argv)

    # Setze globale Schriftart
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = KeePassUI()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
