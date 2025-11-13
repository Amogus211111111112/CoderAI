import customtkinter as ctk
import g4f
import json
import os
import uuid
import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

CHAT_DIR = "chats"

class SmartCatAI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CoderAI")
        self.geometry("920x720")
        self.resizable(False, False)

        os.makedirs(CHAT_DIR, exist_ok=True)

        # Benutzer-Code laden oder neu erstellen
        self.user_code = self._load_or_create_user_code()

        # GUI-Elemente bauen
        self._build_interface()

        self.chat_log = self._load_user_history()
        self._display_saved_history()

    def _build_interface(self):
        self.code_label = ctk.CTkLabel(self, text=f"🔐 dein Code: {self.user_code}", font=("Arial", 14))
        self.code_label.pack(pady=5)

        self.switch_frame = ctk.CTkFrame(self)
        self.switch_frame.pack(pady=5)
        self.code_entry = ctk.CTkEntry(self.switch_frame, width=200, placeholder_text="Code eingeben...")
        self.code_entry.pack(side="left", padx=(0, 10))
        self.code_button = ctk.CTkButton(self.switch_frame, text="🔄 Account wechseln", command=self.switch_user)
        self.code_button.pack(side="left")

        self.chat_display = ctk.CTkTextbox(self, width=880, height=300, font=("Consolas", 14), wrap="word")
        self.chat_display.configure(state="disabled")
        self.chat_display.pack(pady=10)

        self.prompt_entry = ctk.CTkTextbox(self, width=880, height=100, font=("Consolas", 14), wrap="word")
        self.prompt_entry.pack(pady=(0, 10))

        self.send_button = ctk.CTkButton(self, text="Senden ➣", command=self.send_message)
        self.send_button.pack(pady=(0, 10))

        self.history_label = ctk.CTkLabel(self, text="📜 Verlauf (dein gesamter Gesprächsverlauf):")
        self.history_label.pack()

        self.history_display = ctk.CTkTextbox(self, width=880, height=200, font=("Courier", 12), wrap="word")
        self.history_display.configure(state="disabled")
        self.history_display.pack(pady=(0, 20))

    def send_message(self):
        prompt = self.prompt_entry.get("1.0", "end").strip()
        if not prompt:
            return

        self._append_chat(f"🧑 Du: {prompt}\n")
        self.prompt_entry.delete("1.0", "end")

        # Baue Nachrichtenverlauf für GPT auf
        messages = [
            {
                "role": "system",
                "content": (
                    "Du bist ein geduldiger Programmier-Tutor und Informatik-Tutor für deutschsprachige Schüler. "
                    "Du hilfst Schülern in dem Fach Informatik "
                    "Du sollst auch es gut denn Schülern erklären die keine Ahnung von Programmieren haben"
                    "Du sollst Scratch, Python,JS, Java, C++ und mehr wissen "
                    "Stelle Fragen, bewerte Antworten, gib eine Note am Ende, helfe denn Schülern"
                    "Rede nur auf Deutsch, du kannst auch auf anderen Sprachen reden aber nur wenn der Nutzer es von dir verlangt"
                )
            }
        ]

        # Chatverlauf an messages anhängen
        # Die Einträge alternieren zwischen User und Assistant
        for i, item in enumerate(self.chat_log):
            role = "user" if i % 2 == 0 else "assistant"
            content = item["user"] if role == "user" else item["ai"]
            messages.append({"role": role, "content": content})

        # Neue User-Nachricht anhängen
        messages.append({"role": "user", "content": prompt})

        # GPT-Anfrage
        try:
            antwort = g4f.ChatCompletion.create(
                model="gpt-4",
                messages=messages
            )
            # Falls Antwort ein dict mit 'message' ist (je nach g4f Version)
            if isinstance(antwort, dict) and "message" in antwort:
                antwort = antwort["message"]["content"]
        except Exception as e:
            antwort = f"❌ Fehler: {e}"

        self._append_chat(f"🤖 CoderAI: {antwort}\n\n")

        self._save_user_history(prompt, antwort)
        self._display_saved_history()

    def _append_chat(self, text):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", text)
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def _load_or_create_user_code(self):
        user_file = "user_code.txt"
        if os.path.exists(user_file):
            with open(user_file, "r") as f:
                return f.read().strip()
        else:
            new_code = str(uuid.uuid4())[:8]
            with open(user_file, "w") as f:
                f.write(new_code)
            return new_code

    def _get_history_file(self):
        return os.path.join(CHAT_DIR, f"user_{self.user_code}.json")

    def _load_user_history(self):
        path = self._get_history_file()
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_user_history(self, prompt, antwort):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user": prompt,
            "ai": antwort
        }
        self.chat_log.append(entry)
        with open(self._get_history_file(), "w", encoding="utf-8") as f:
            json.dump(self.chat_log, f, ensure_ascii=False, indent=2)

    def _display_saved_history(self):
        self.history_display.configure(state="normal")
        self.history_display.delete("1.0", "end")
        for item in self.chat_log[-10:]:
            ts = item.get("timestamp", "")[:19].replace("T", " ")
            self.history_display.insert("end", f"[{ts}]\nDu: {item['user']}\nAI: {item['ai']}\n\n")
        self.history_display.configure(state="disabled")

    def switch_user(self):
        code = self.code_entry.get().strip()
        if len(code) < 4:
            return
        self.user_code = code
        with open("user_code.txt", "w") as f:
            f.write(code)
        self.code_label.configure(text=f"🔐 dein Code: {self.user_code}")
        self.chat_log = self._load_user_history()
        self._display_saved_history()
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")

if __name__ == "__main__":
    app = SmartCatAI()
    app.mainloop()