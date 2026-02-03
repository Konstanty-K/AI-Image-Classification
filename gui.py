import customtkinter as ctk
import tkinter as tk  # Importujemy klasyczny tkinter dla Labela wideo
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import os

# --- KONFIGURACJA WYGLĄDU ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ModernTrashApp(ctk.CTk):
    def __init__(self, model_path='best.pt'):
        super().__init__()

        # Konfiguracja głównego okna
        self.title("AI Trash Detector Pro")
        self.geometry("1000x700")

        # Ładowanie modelu
        self.model_path = model_path
        if not os.path.exists(self.model_path):
            print(f"OSTRZEŻENIE: Brak {self.model_path}. Używam yolov8n.pt.")
            self.model = YOLO('yolov8n.pt')
        else:
            self.model = YOLO(self.model_path)

        # Zmienne stanu
        self.cap = None
        self.is_running = False
        self.current_conf = 0.40
        self.current_image = None  # Zmienna do trzymania referencji obrazu

        # --- UKŁAD GUI ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._create_sidebar()
        self._create_main_area()

    def _create_sidebar(self):
        """Tworzy lewy panel z przyciskami"""
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="♻️ DETEKTOR", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_img = ctk.CTkButton(self.sidebar_frame, text="Wczytaj Zdjęcie", command=self.load_image)
        self.btn_img.grid(row=1, column=0, padx=20, pady=10)

        self.btn_cam = ctk.CTkButton(self.sidebar_frame, text="Kamera Start", command=self.toggle_camera,
                                     fg_color="green")
        self.btn_cam.grid(row=2, column=0, padx=20, pady=10)

        self.conf_label = ctk.CTkLabel(self.sidebar_frame, text="Czułość (50%):", anchor="w")
        self.conf_label.grid(row=3, column=0, padx=20, pady=(20, 0))

        self.slider = ctk.CTkSlider(self.sidebar_frame, from_=0.1, to=0.9, command=self.update_conf)
        self.slider.set(0.5)
        self.slider.grid(row=4, column=0, padx=20, pady=10)

    def _create_main_area(self):
        """Tworzy prawy panel z obrazem"""
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # FIX: Używamy standardowego tk.Label zamiast ctk.CTkLabel dla WIDEO/OBRAZU.
        # Jest dużo stabilniejszy przy szybkim odświeżaniu i nie gubi referencji.
        # Ustawiamy bg na kolor tła ramki (szary w trybie Dark)
        self.video_label = tk.Label(self.main_frame, text="Wybierz źródło obrazu", bg="#2b2b2b", fg="white",
                                    font=("Arial", 14))
        self.video_label.pack(expand=True, fill="both", padx=10, pady=10)

    def update_conf(self, value):
        self.current_conf = value
        self.conf_label.configure(text=f"Czułość ({int(value * 100)}%):")

    def load_image(self):
        self.stop_camera()
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not path: return

        try:
            results = self.model.predict(source=path, conf=self.current_conf)
            res_plotted = results[0].plot()
            self.display_frame(res_plotted)
        except Exception as e:
            print(f"Błąd detekcji: {e}")

    def toggle_camera(self):
        if self.is_running:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Błąd kamery")
            return
        self.is_running = True
        self.btn_cam.configure(text="Zatrzymaj Kamerę", fg_color="#c0392b", hover_color="#e74c3c")
        self.update_frame()

    def stop_camera(self):
        self.is_running = False
        if self.cap: self.cap.release()
        self.btn_cam.configure(text="Kamera Start", fg_color="green", hover_color="#2ecc71")

        # Resetujemy label bezpiecznie
        self.video_label.config(image='', text="Kamera zatrzymana")
        self.current_image = None

    def update_frame(self):
        if self.is_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                results = self.model.predict(frame, conf=self.current_conf, verbose=False)
                annotated_frame = results[0].plot()
                self.display_frame(annotated_frame)
            # Wywołanie zwrotne po 10ms
            self.after(10, self.update_frame)

    def display_frame(self, frame_bgr):
        # 1. Konwersja OpenCV -> PIL
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)

        # 2. Obliczanie wymiarów (zabezpieczenie przed startem aplikacji)
        w = self.main_frame.winfo_width() - 20
        h = self.main_frame.winfo_height() - 20
        if w < 10 or h < 10: w, h = 800, 600

        # 3. Skalowanie
        img_pil.thumbnail((w, h))

        # 4. Konwersja do standardowego ImageTk (nie CTkImage)
        # To jest klucz do naprawienia błędu "pyimage1 doesn't exist"
        imgtk = ImageTk.PhotoImage(image=img_pil)

        # 5. Zapamiętanie referencji (Garbage Collector protection)
        self.current_image = imgtk

        # 6. Wyświetlenie w standardowym tk.Label
        self.video_label.configure(image=imgtk, text="")


if __name__ == "__main__":
    app = ModernTrashApp()
    app.mainloop()