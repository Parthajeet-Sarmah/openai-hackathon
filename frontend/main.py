import sys
import threading
import time
import httpx
import markdown
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy, QScrollArea, QTextBrowser
from PySide6.QtCore import Qt, Signal, QObject, QTimer

class Worker(QObject):
    token_received = Signal(str)

    def __init__(self, prompt_payload):
        super().__init__()
        self.prompt_payload = prompt_payload

    def run(self):
        url = "http://localhost:8080/summarize"
        with httpx.stream("POST", url, json=self.prompt_payload, timeout=None) as response:
            for chunk in response.iter_text():
                if chunk.strip():
                    if("thinking..." in chunk):
                        continue
                    
                    self.token_received.emit(chunk)

class OverlayUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 400, 300)
        self.full_markdown = ""
        self.markdown_buffer = ""

        layout = QVBoxLayout(self)

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setStyleSheet("background: transparent; outline: none; border: none; color: white;")
        self.text_browser.setReadOnly(True)
        self.text_browser.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.text_browser)
        layout.addWidget(scroll)

        self.markdown_buffer = ""
        self.update_timer = QTimer()
        self.update_timer.setInterval(150)  # ms, adjust for smoothness
        self.update_timer.timeout.connect(self.flush_markdown_to_html)
        self.update_timer.start()

        self.start_worker()
        threading.Timer(60, self.start_worker)

    def start_worker(self):
        self.prompt_payload = {
            "summary_type": "daily",
            "max_events": 15,
            "event_type": "",
        }

        self.worker = Worker(self.prompt_payload)
        self.worker.token_received.connect(self.receive_token)

        thread = threading.Thread(target=self.worker.run, daemon=True)
        thread.start()
     
    def receive_token(self, token: str):
        if (token == "thinking..."):
            return
        
        self.markdown_buffer += token
    
    def flush_markdown_to_html(self):
        if self.markdown_buffer:
            scroll_bar = self.text_browser.verticalScrollBar()
            near_bottom = (scroll_bar.value() + scroll_bar.pageStep()) >= (scroll_bar.maximum() - 5)

            current_markdown = getattr(self, 'full_markdown', "")
            self.full_markdown = current_markdown + self.markdown_buffer

            html = markdown.markdown(self.full_markdown)
            self.text_browser.setHtml(html)

            if near_bottom:
                scroll_bar.setValue(scroll_bar.maximum())

            self.markdown_buffer = ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OverlayUI()
    window.show()
    sys.exit(app.exec())
