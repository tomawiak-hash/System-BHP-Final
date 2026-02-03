import google.generativeai as genai
import os

# Twoja konfiguracja (jeśli używasz secrets, Streamlit je zaczyta, ale tu wpiszmy na sztywno do testu)
api_key = "AIzaSyBPK_8NdYMshhmHRaNdo3rxKn9tw_mWA4o" # Twój klucz

try:
    genai.configure(api_key=api_key)
    print("Szukam dostępnych modeli...")
    
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            
except Exception as e:
    print(f"Błąd: {e}")

input("\nNaciśnij Enter, aby zamknąć...")