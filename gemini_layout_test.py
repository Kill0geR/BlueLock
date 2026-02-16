import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QCursor


class FloatingUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Variablen für das Bewegen des rahmenlosen Fensters
        self.oldPos = self.pos()

    def initUI(self):
        # Fenster-Einstellungen: Rahmenlos, immer im Vordergrund, transparenter Hintergrund
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(700, 250)

        # Hauptlayout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)  # Abstand zwischen Top-Bar und Chat-Panel

        # 1. Obere Steuerungsleiste (Pill-Form) bauen
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar, alignment=Qt.AlignmentFlag.AlignHCenter)

        # 2. Haupt-Chat-Panel bauen
        chat_panel = self.create_chat_panel()
        main_layout.addWidget(chat_panel)

        main_layout.addStretch()

    def create_top_bar(self):
        frame = QFrame()
        frame.setObjectName("TopBar")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(10)

        # Stylesheet für die Pillenform
        frame.setStyleSheet("""
            #TopBar {
                background-color: rgba(30, 33, 40, 230);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 20);
            }
            QPushButton {
                background: transparent;
                color: white;
                font-size: 16px;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 20);
                border-radius: 10px;
            }
        """)

        # Icons (Unicode als Platzhalter)
        icons = ["👁️", "⏸", "⏹", "⌃", "⠿", "✕"]
        for icon in icons:
            btn = QPushButton(icon)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            if icon == "✕":  # Close Button Logik
                btn.clicked.connect(self.close)
            layout.addWidget(btn)

        return frame

    def create_chat_panel(self):
        frame = QFrame()
        frame.setObjectName("ChatPanel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(15)

        # Stylesheet für das Hauptpanel
        frame.setStyleSheet("""
            #ChatPanel {
                background-color: rgba(30, 33, 40, 230);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 20);
            }
            QLabel {
                color: #b0b3b8;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        # -- Header Row (Home, Chat, Transcript) --
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        home_lbl = QLabel("🏠")
        home_lbl.setStyleSheet("font-size: 18px; color: white;")

        chat_btn = QPushButton("Chat")
        chat_btn.setStyleSheet("""
            background-color: rgba(255, 255, 255, 20);
            color: white;
            border-radius: 12px;
            padding: 5px 15px;
            font-weight: bold;
        """)

        transcript_lbl = QLabel("Transcript")
        transcript_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")

        header_layout.addWidget(home_lbl)
        header_layout.addWidget(chat_btn)
        header_layout.addWidget(transcript_lbl)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # -- Action Row (Assist, Follow-up etc.) --
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        actions = [
            ("✨", "Assist"),
            ("🪄", "What should I say?"),
            ("💬", "Follow-up questions"),
            ("↻", "Recap")
        ]

        for i, (icon, text) in enumerate(actions):
            btn = QPushButton(f"{icon} {text}")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: white;
                    font-size: 13px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    color: #8ab4f8;
                }
            """)
            action_layout.addWidget(btn)

            # Punkt als Separator hinzufügen (außer nach dem letzten Element)
            if i < len(actions) - 1:
                dot = QLabel("·")
                dot.setStyleSheet("color: #5f6368; font-weight: bold;")
                action_layout.addWidget(dot)

        action_layout.addStretch()
        layout.addLayout(action_layout)

        # -- Input Area --
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 10);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 20px;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 5, 5, 5)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Ask about your screen or conversation, or ⌃ ↵ for Assist")
        line_edit.setStyleSheet("""
            QLineEdit {
                background: transparent;
                color: white;
                border: none;
                font-size: 14px;
            }
        """)

        send_btn = QPushButton("➤")
        send_btn.setFixedSize(32, 32)
        send_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #0a58d0;
                color: white;
                border-radius: 16px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #0842a0;
            }
        """)

        input_layout.addWidget(line_edit)
        input_layout.addWidget(send_btn)

        layout.addWidget(input_frame)

        return frame

    # ---- Erlaubt das Verschieben des rahmenlosen Fensters mit der Maus ----
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Optional: Eine Standard-Schriftart setzen, die gut aussieht
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = FloatingUI()
    window.show()
    sys.exit(app.exec())