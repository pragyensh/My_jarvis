import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QLabel, QPushButton, QSizePolicy, 
                             QTextEdit, QFrame, QStackedWidget, QDesktopWidget,
                             QMainWindow, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QRect, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QTextBlockFormat, QMovie, QPixmap, QIcon, QTextCursor, QPainter, QPalette

# Define global paths
GraphicsDirPath = "Frontend/Graphics"
TempDirPath = "temp"
Assistantname = "Jarvis"

# Create directories if they don't exist
os.makedirs(GraphicsDirPath, exist_ok=True)
os.makedirs(TempDirPath, exist_ok=True)

print("Looking for jarvis.gif at:", os.path.join(GraphicsDirPath, "jarvis.gif"))
print("Exists?", os.path.exists(os.path.join(GraphicsDirPath, "jarvis.gif")))

# Utility functions
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ['how', 'what', 'who', 'where', 'when', 'why', 'which', 'whose', 'whom', 'can you', 'what\'s', 'where\'s', 'how\'s'] 

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '?"'
        else:
            new_query += '?"'
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '."'
        else:
            new_query += '."'

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(os.path.join(TempDirPath, 'Mic.data'), "w", encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(os.path.join(TempDirPath, 'Mic.data'), "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, 'Status.data'), "w", encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    with open(os.path.join(TempDirPath, 'Status.data'), "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def MicButtonInitiated():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(filename):
    return os.path.join(GraphicsDirPath, filename)

def TempDirectoryPath(filename):
    return os.path.join(TempDirPath, filename)

def ShowTextToScreen(Text):
    with open(os.path.join(TempDirPath, 'Responses.data'), "w", encoding='utf-8') as file:
        file.write(Text)

# Animated label class for pulsing effects
class AnimatedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._opacity = 1.0
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(2000)
        self.animation.setStartValue(0.3)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InOutSine)
        self.animation.finished.connect(self.reverse_animation)
        
    @pyqtProperty(float)
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)
        self.update()
        
    def reverse_animation(self):
        start_val = self.animation.startValue()
        end_val = self.animation.endValue()
        self.animation.setStartValue(end_val)
        self.animation.setEndValue(start_val)
        self.animation.start()
        
    def start_pulsing(self):
        self.animation.start()

# Chat section widget
class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        
        # Enhanced chat styling with glow effects
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a1a);
                color: #00ffff;
                border: 2px solid #004080;
                border-radius: 15px;
                padding: 15px;
                font-size: 14px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            QScrollBar:vertical {
                border: none;
                background: #0a0a0a;
                width: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #004080, stop:1 #0080ff);
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0080ff, stop:1 #00ffff);
            }
        """)
        
        # Add glow effect
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(20)
        shadow_effect.setColor(QColor(0, 128, 255, 100))
        shadow_effect.setOffset(0, 0)
        self.chat_text_edit.setGraphicsEffect(shadow_effect)
        
        layout.addWidget(self.chat_text_edit)
        
        self.setStyleSheet("background-color: black;")
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        
        text_color = QColor(0, 255, 255)  # Cyan color
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        
        font = QFont("Consolas", 13)
        self.chat_text_edit.setFont(font)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)
        
        self.old_chat_message = ""

    def loadMessages(self):
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()

            if messages is None:
                pass
            elif len(messages) <= 1:
                pass
            elif str(self.old_chat_message) == str(messages):
                pass
            else:
                self.addMessage(message=messages, color='#00ffff')
                self.old_chat_message = messages
        except:
            pass

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
        except:
            messages = "Ready..."

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)
        self.chat_text_edit.ensureCursorVisible()

# Enhanced Initial screen widget
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Enhanced title with glow effect
        self.title_label = AnimatedLabel(f"{Assistantname} AI")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-size: 32px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                padding: 30px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 0, 0, 200), stop:1 rgba(0, 64, 128, 100));
                border: 1px solid #004080;
            }
        """)
        
        # Add glow effect to title
        title_shadow = QGraphicsDropShadowEffect()
        title_shadow.setBlurRadius(30)
        title_shadow.setColor(QColor(0, 255, 255, 150))
        title_shadow.setOffset(0, 0)
        self.title_label.setGraphicsEffect(title_shadow)
        self.title_label.start_pulsing()
        
        main_layout.addWidget(self.title_label)
        
        # Center content with GIF and controls
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setSpacing(30)
        
        # Enhanced GIF container
        gif_container = QWidget()
        gif_container.setFixedSize(400, 400)
        gif_layout = QVBoxLayout(gif_container)
        gif_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create GIF label with enhanced styling
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setStyleSheet("""
            QLabel {
                border: 3px solid #004080;
                border-radius: 200px;
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(0, 128, 255, 50), stop:1 rgba(0, 0, 0, 100));
            }
        """)
        
        # Add enhanced glow effect to GIF
        gif_shadow = QGraphicsDropShadowEffect()
        gif_shadow.setBlurRadius(50)
        gif_shadow.setColor(QColor(0, 128, 255, 200))
        gif_shadow.setOffset(0, 0)
        self.gif_label.setGraphicsEffect(gif_shadow)
        
        # Load GIF with better sizing
        gif_path = GraphicsDirectoryPath('Jarvis.gif')
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.movie.setScaledSize(QSize(350, 350))
            self.gif_label.setMovie(self.movie)
            self.movie.start()
            self.gif_label.setFixedSize(370, 370)
        else:
            print(f"GIF not found at: {gif_path}")
            # Create a placeholder with animated text
            self.gif_label.setText("◉ JARVIS ◉")
            self.gif_label.setStyleSheet("""
                QLabel {
                    color: #00ffff;
                    font-size: 28px;
                    font-weight: bold;
                    border: 3px solid #004080;
                    border-radius: 185px;
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        stop:0 rgba(0, 128, 255, 50), stop:1 rgba(0, 0, 0, 100));
                }
            """)
            self.gif_label.setFixedSize(370, 370)
        
        gif_layout.addWidget(self.gif_label)
        center_layout.addWidget(gif_container, alignment=Qt.AlignCenter)
        
        # Enhanced status label with animation
        self.status_label = AnimatedLabel("Ready...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-size: 18px;
                font-weight: bold;
                margin: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 64, 128, 150), stop:0.5 rgba(0, 128, 255, 100), stop:1 rgba(0, 64, 128, 150));
                padding: 15px 30px;
                border-radius: 25px;
                border: 2px solid #004080;
                font-family: 'Arial', sans-serif;
            }
        """)
        
        # Add glow to status
        status_shadow = QGraphicsDropShadowEffect()
        status_shadow.setBlurRadius(25)
        status_shadow.setColor(QColor(0, 255, 255, 120))
        status_shadow.setOffset(0, 0)
        self.status_label.setGraphicsEffect(status_shadow)
        self.status_label.start_pulsing()
        
        center_layout.addWidget(self.status_label)
        
        # Enhanced mic button with better styling
        self.mic_button = QPushButton()
        mic_icon_path = GraphicsDirectoryPath('Mic_on.png')
        if os.path.exists(mic_icon_path):
            self.mic_button.setIcon(QIcon(mic_icon_path))
        self.mic_button.setIconSize(QSize(50, 50))
        self.mic_button.setFixedSize(100, 100)
        self.mic_button.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(255, 255, 255, 250), stop:1 rgba(0, 128, 255, 200));
                border: 3px solid #004080;
                border-radius: 50px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(255, 255, 255, 255), stop:1 rgba(0, 255, 255, 200));
                border: 3px solid #00ffff;
            }
            QPushButton:pressed {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(0, 255, 255, 200), stop:1 rgba(0, 128, 255, 150));
            }
        """)
        
        # Add glow to mic button
        mic_shadow = QGraphicsDropShadowEffect()
        mic_shadow.setBlurRadius(30)
        mic_shadow.setColor(QColor(0, 128, 255, 150))
        mic_shadow.setOffset(0, 0)
        self.mic_button.setGraphicsEffect(mic_shadow)
        
        self.mic_button.clicked.connect(self.toggle_mic)
        self.mic_on = True
        center_layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)
        
        main_layout.addLayout(center_layout)
        main_layout.addStretch(1)
        
        self.setLayout(main_layout)
        
        # Enhanced background with gradient
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #000000, stop:0.3 #001122, stop:0.7 #001122, stop:1 #000000);
            }
        """)
        
        # Timer for status updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(100)
        
        # Animation timer for dynamic effects
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start(50)
        self.animation_counter = 0

    def update_animations(self):
        self.animation_counter += 1
        # Add subtle pulsing effects or other animations here if needed

    def update_status(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                status = file.read().strip()
            if status:
                self.status_label.setText(status)
        except:
            self.status_label.setText("Ready...")

    def toggle_mic(self):
        if self.mic_on:
            mic_off_path = GraphicsDirectoryPath('Mic_off.png')
            if os.path.exists(mic_off_path):
                self.mic_button.setIcon(QIcon(mic_off_path))
            MicButtonClosed()
            self.status_label.setText("Microphone Off")
            # Change button color when off
            self.mic_button.setStyleSheet("""
                QPushButton {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        stop:0 rgba(128, 128, 128, 200), stop:1 rgba(64, 64, 64, 200));
                    border: 3px solid #666666;
                    border-radius: 50px;
                }
                QPushButton:hover {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        stop:0 rgba(160, 160, 160, 200), stop:1 rgba(96, 96, 96, 200));
                    border: 3px solid #888888;
                }
            """)
        else:
            mic_on_path = GraphicsDirectoryPath('Mic_on.png')
            if os.path.exists(mic_on_path):
                self.mic_button.setIcon(QIcon(mic_on_path))
            MicButtonInitiated()
            self.status_label.setText("Listening...")
            # Restore active button color
            self.mic_button.setStyleSheet("""
                QPushButton {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        stop:0 rgba(255, 255, 255, 250), stop:1 rgba(0, 128, 255, 200));
                    border: 3px solid #004080;
                    border-radius: 50px;
                }
                QPushButton:hover {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        stop:0 rgba(255, 255, 255, 255), stop:1 rgba(0, 255, 255, 200));
                    border: 3px solid #00ffff;
                }
            """)
        self.mic_on = not self.mic_on

# Message screen widget with enhanced styling
class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #000000, stop:0.3 #001122, stop:0.7 #001122, stop:1 #000000);
            }
        """)

# Enhanced top bar widget
class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()
        self.draggable = True
        self.offset = None

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        
        # Enhanced navigation buttons
        home_button = QPushButton("🏠 Home")
        home_button.setStyleSheet("""
            QPushButton {
                color: #00ffff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #003366, stop:1 #001133);
                border: 1px solid #004080;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #004080, stop:1 #002244);
                border: 1px solid #00ffff;
            }
        """)
        home_button.clicked.connect(self.showInitialScreen)
        
        chat_button = QPushButton("💬 Chat")
        chat_button.setStyleSheet("""
            QPushButton {
                color: #00ffff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #003366, stop:1 #001133);
                border: 1px solid #004080;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #004080, stop:1 #002244);
                border: 1px solid #00ffff;
            }
        """)
        chat_button.clicked.connect(self.showMessageScreen)
        
        # Enhanced title
        title_label = QLabel(f"⚡ {Assistantname} AI ⚡")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        
        # Enhanced window controls
        minimize_button = QPushButton("➖")
        minimize_button.setFixedSize(30, 30)
        minimize_button.setStyleSheet(self.get_control_button_style("#ffaa00"))
        minimize_button.clicked.connect(self.minimizeWindow)
        
        self.maximize_button = QPushButton("⬜")
        self.maximize_button.setFixedSize(30, 30)
        self.maximize_button.setStyleSheet(self.get_control_button_style("#00aa00"))
        self.maximize_button.clicked.connect(self.maximizeWindow)
        
        close_button = QPushButton("❌")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet(self.get_control_button_style("#ff0000"))
        close_button.clicked.connect(self.closeWindow)
        
        # Add widgets to layout
        layout.addWidget(home_button)
        layout.addWidget(chat_button)
        layout.addStretch(1)
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        
        # Enhanced top bar background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #002244, stop:1 #001122);
                border-bottom: 2px solid #004080;
            }
        """)

    def get_control_button_style(self, hover_color):
        return f"""
            QPushButton {{
                color: white;
                background-color: #333333;
                border: 1px solid #555555;
                border-radius: 15px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border: 1px solid white;
            }}
        """

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setText("⬜")
        else:
            self.parent().showMaximized()
            self.maximize_button.setText("🗗")

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable and event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset and event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

    def showMessageScreen(self):
        self.stacked_widget.setCurrentIndex(1)

    def showInitialScreen(self):
        self.stacked_widget.setCurrentIndex(0)

# Enhanced main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.initUI()
        
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Set window size to be larger and centered
        window_width = 900
        window_height = 700
        self.setGeometry(
            (screen_width - window_width) // 2,
            (screen_height - window_height) // 2,
            window_width,
            window_height
        )
        
        # Create stacked widget for screens
        self.stacked_widget = QStackedWidget(self)
        
        # Create screens
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        
        # Add screens to stacked widget
        self.stacked_widget.addWidget(initial_screen)
        self.stacked_widget.addWidget(message_screen)
        
        # Set initial screen
        self.stacked_widget.setCurrentIndex(0)
        
        # Create top bar
        top_bar = CustomTopBar(self, self.stacked_widget)
        
        # Enhanced window styling with gradient border
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #000000, stop:1 #001122);
                border: 2px solid #004080;
            }
        """)
        
        # Add glow effect to main window
        main_shadow = QGraphicsDropShadowEffect()
        main_shadow.setBlurRadius(40)
        main_shadow.setColor(QColor(0, 128, 255, 100))
        main_shadow.setOffset(0, 0)
        self.setGraphicsEffect(main_shadow)
        
        # Set menu widget and central widget
        self.setMenuWidget(top_bar)
        self.setCentralWidget(self.stacked_widget)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    
    # Set application style for better look
    app.setStyle('Fusion')
    
    # Create and configure the window
    window = MainWindow()
    window.show()
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()
    