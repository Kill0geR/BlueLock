import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QLabel,
                             QScrollArea, QFrame, QTabWidget, QGraphicsBlurEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QLinearGradient, QPixmap


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
        painter.setBrush(QColor(30, 30, 40, 120))  # Sehr transparent
        painter.setPen(QColor(255, 255, 255, 30))  # Leichter weißer Rand
        painter.drawRoundedRect(self.rect(), 15, 15)


class ModernButton(QPushButton):
    """Moderner Button mit Hover-Effekt und Glassmorphism"""

    def __init__(self, text="", icon_text="", parent=None):
        super().__init__(text, parent)
        self.icon_text = icon_text
        self.setMinimumHeight(36)
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


class ChatMessage(QFrame):
    """Chat-Nachricht Widget mit Glassmorphism"""

    def __init__(self, text, is_user=False, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"""
            QLabel {{
                background-color: {'rgba(60, 120, 200, 130)' if is_user else 'rgba(50, 50, 60, 100)'};
                border: 1px solid {'rgba(100, 160, 240, 100)' if is_user else 'rgba(255, 255, 255, 40)'};
                border-radius: 12px;
                padding: 12px 16px;
                color: rgba(255, 255, 255, 230);
                font-size: 14px;
            }}
        """)

        if is_user:
            layout.addStretch()
            layout.addWidget(message_label)
        else:
            layout.addWidget(message_label)
            layout.addStretch()

        self.setLayout(layout)
        self.setStyleSheet("background: transparent;")


class ModernChatUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Chat Interface")
        self.setGeometry(100, 100, 900, 650)

        # Transparentes Fenster aktivieren
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Haupt-Widget
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(central_widget)

        # Haupt-Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        central_widget.setLayout(main_layout)

        # Hintergrund-Container mit Blur
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

        # Layout für Hintergrund
        bg_layout = QVBoxLayout()
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(0)
        background.setLayout(bg_layout)

        # Tab-Bereich (Chat, Transcript)
        self.create_tab_area(bg_layout)

        # Chat-Bereich
        self.create_chat_area(bg_layout)

        # Eingabebereich
        self.create_input_area(bg_layout)

        main_layout.addWidget(background)

        # Schließen-Button hinzufügen
        self.add_close_button()

    def create_tab_area(self, parent_layout):
        """Erstellt den Tab-Bereich oben mit Glassmorphism"""
        tab_container = GlassWidget()
        tab_container.setFixedHeight(90)

        tab_layout = QVBoxLayout()
        tab_layout.setContentsMargins(20, 12, 20, 12)
        tab_container.setLayout(tab_layout)

        # Erste Reihe: Home, Chat, Transcript
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        home_btn = ModernButton("🏠")
        home_btn.setFixedWidth(50)

        chat_btn = ModernButton("Chat")
        chat_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 30);
                border: 1px solid rgba(255, 255, 255, 60);
                font-weight: bold;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 40);
            }
        """)

        transcript_btn = ModernButton("Transcript")

        top_row.addWidget(home_btn)
        top_row.addWidget(chat_btn)
        top_row.addWidget(transcript_btn)
        top_row.addStretch()

        # Zweite Reihe: Assist, What should I say?, Follow-up, Recap
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(10)

        assist_btn = ModernButton("✨ Assist")
        suggest_btn = ModernButton("💬 What should I say?")
        followup_btn = ModernButton("📋 Follow-up questions")
        recap_btn = ModernButton("🔄 Recap")

        bottom_row.addWidget(assist_btn)
        bottom_row.addWidget(suggest_btn)
        bottom_row.addWidget(followup_btn)
        bottom_row.addWidget(recap_btn)
        bottom_row.addStretch()

        tab_layout.addLayout(top_row)
        tab_layout.addLayout(bottom_row)

        parent_layout.addWidget(tab_container)

    def create_chat_area(self, parent_layout):
        """Erstellt den Chat-Bereich"""
        # Scroll-Bereich für Nachrichten
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 30);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 100);
                border-radius: 5px;
            }
        """)

        # Container für Nachrichten
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(15)
        self.messages_container.setLayout(self.messages_layout)
        self.messages_container.setStyleSheet("background: transparent;")

        # Beispiel-Nachrichten
        self.add_message("Hallo! Wie kann ich dir heute helfen?", False)
        self.add_message("Kannst du mir eine moderne UI in PyQt6 erstellen?", True)
        self.add_message("Natürlich! Ich erstelle gerne eine moderne Benutzeroberfläche für dich.", False)

        self.messages_layout.addStretch()

        scroll_area.setWidget(self.messages_container)
        parent_layout.addWidget(scroll_area)

    def create_input_area(self, parent_layout):
        """Erstellt den Eingabebereich unten mit Glassmorphism"""
        input_container = GlassWidget()
        input_container.setFixedHeight(85)

        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(20, 18, 20, 18)
        input_container.setLayout(input_layout)

        # Eingabefeld
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask about your screen or conversation, or ⌘ for Assist")
        self.input_field.setMinimumHeight(48)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(50, 50, 60, 100);
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 24px;
                padding: 12px 20px;
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
        self.input_field.returnPressed.connect(self.send_message)

        # Senden-Button
        send_btn = QPushButton("▶")
        send_btn.setFixedSize(48, 48)
        send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 120, 200, 150);
                border: 1px solid rgba(100, 160, 240, 100);
                border-radius: 24px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(80, 140, 220, 180);
                border: 1px solid rgba(120, 180, 255, 120);
            }
            QPushButton:pressed {
                background-color: rgba(50, 110, 190, 200);
            }
        """)
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_btn)

        parent_layout.addWidget(input_container)

    def add_close_button(self):
        """Fügt einen Schließen-Button hinzu (da Fenster frameless ist)"""
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

    def add_message(self, text, is_user=False):
        """Fügt eine neue Nachricht hinzu"""
        message = ChatMessage(text, is_user)
        # Füge vor dem Stretch ein
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, message)

    def send_message(self):
        """Sendet eine Nachricht"""
        text = self.input_field.text().strip()
        if text:
            self.add_message(text, True)
            self.input_field.clear()

            # Simuliere eine Antwort
            QApplication.processEvents()
            import random
            responses = [
                "Verstanden! Ich arbeite daran.",
                "Gute Frage! Lass mich das für dich herausfinden.",
                "Das ist interessant. Hier ist meine Antwort...",
                "Ich kann dir dabei helfen!",
            ]
            self.add_message(random.choice(responses), False)


def main():
    app = QApplication(sys.argv)

    # Setze globale Schriftart
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = ModernChatUI()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()