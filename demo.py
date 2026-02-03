import os
from ultralytics import YOLO
import cv2

# --- KONFIGURACJA ---
# Tutaj wstawisz ścieżkę do pobranego z Colaba modelu
MODEL_PATH = 'best.pt'

# Źródło obrazu:
# 0 -> Kamera internetowa (webcam)
# "nazwa_pliku.mp4" -> plik wideo
# "test.jpg" -> zdjęcie
SOURCE = "trash.jpg"

# Próg pewności (0.5 = pokaż tylko to, czego jesteś pewien na 50%)
CONFIDENCE_THRESHOLD = 0.5


def run_demo():
    # 1. Sprawdzenie czy model istnieje
    if not os.path.exists(MODEL_PATH):
        print(f"BŁĄD: Nie znaleziono pliku modelu '{MODEL_PATH}'!")
        print("Pobierz 'best.pt' z Google Colab i wklej go do folderu z tym skryptem.")
        return

    # 2. Ładowanie modelu
    print(f"Ładowanie modelu: {MODEL_PATH}...")
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"Błąd ładowania modelu: {e}")
        return

    # 3. Uruchomienie predykcji
    # show=True automatycznie otwiera okienko z podglądem
    # save=True zapisuje wynik do folderu runs/detect (dowód dla prowadzącego)
    print("Uruchamiam detekcję. Naciśnij 'q' w oknie podglądu, aby zakończyć.")

    results = model.predict(
        source=SOURCE,
        show=True,  # Pokaż okno
        conf=CONFIDENCE_THRESHOLD,
        save=True,  # Zapisz wideo/zdjęcie z ramkami
        stream=True  # Tryb strumieniowy (wymagany dla kamery/wideo, żeby nie zapchać RAMu)
    )

    # Pętla potrzebna, żeby okno nie zamknęło się natychmiast (dla streamu)
    for r in results:
        pass  # Tu można dodać własną logikę, np. zliczanie butelek


if __name__ == '__main__':
    run_demo()