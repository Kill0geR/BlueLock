"""
BlueLock - Notifier
Shows system notifications (works on Windows & Mac)
"""

import platform
import threading


class Notifier:
    def __init__(self):
        self.system = platform.system()

    def show(self, title: str, message: str, duration: int = 3):
        """Show a system notification in a non-blocking thread"""
        thread = threading.Thread(
            target=self._show, args=(title, message, duration), daemon=True
        )
        thread.start()

    def _show(self, title: str, message: str, duration: int):
        try:
            if self.system == "Windows":
                self._windows_notify(title, message, duration)
            elif self.system == "Darwin":
                self._mac_notify(title, message)
            else:
                self._linux_notify(title, message)
        except Exception as e:
            print(f"[Notifier] Fehler: {e}")

    def _windows_notify(self, title: str, message: str, duration: int):
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=duration, threaded=True)
        except ImportError:
            # Fallback: use plyer
            try:
                from plyer import notification
                notification.notify(title=title, message=message, timeout=duration)
            except Exception:
                print(f"[Notifier] {title}: {message}")

    def _mac_notify(self, title: str, message: str):
        import subprocess
        subprocess.run([
            "osascript", "-e",
            f'display notification "{message}" with title "{title}"'
        ], check=False)

    def _linux_notify(self, title: str, message: str):
        import subprocess
        subprocess.run(["notify-send", title, message], check=False)
