import sys
import threading
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
        url = "http://127.0.0.1:8080/summarize"
        try:
            with httpx.stream("POST", url, json=self.prompt_payload, timeout=None) as response:
                for chunk in response.iter_text():
                    if chunk.strip():
                        if("thinking..." in chunk):
                            continue
                        
                        self.token_received.emit(chunk)
        except httpx.RemoteProtocolError:
            self.token_received.emit(".....**The response stream was cut off**")

class OverlayUI(QWidget):

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = False
            event.accept()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 400, 200)
        self.setStyleSheet("background-color: #161616; outline: none; border: none;")
        self.full_markdown = ""
        self.markdown_buffer = ""

        self._drag_active = False
        self._drag_position = None

        layout = QVBoxLayout(self)

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setStyleSheet("background-color: black; outline: none; border: none; color: white;")
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

        self.call_timer = QTimer()
        self.call_timer.setInterval(60000)
        self.call_timer.timeout.connect(self.start_worker)
        self.call_timer.start()

        self.start_worker()

    def start_worker(self):
        print("Working again...")
        
        self.prompt_payload = {
            "summary_type": "1-Minute",
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
