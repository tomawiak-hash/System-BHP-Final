import google.generativeai as genai
import streamlit as st
import re
import json
import time

# Konfiguracja modelu
MODEL_NAME = 'gemini-flash-latest' # Możesz tu użyć 1.5-flash, 2.0-flash lub pro

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    pass 


def generuj_kompletne_szkolenie(firma, nazwa_zawodu, opis_zawodu, dodatkowe_zagrozenia, obowiazki, srodowisko):
    model = genai.GenerativeModel(MODEL_NAME)
    
    prompt = f"""
    Jesteś ekspertem BHP i doświadczonym metodykiem. Twoim zadaniem jest stworzenie KOMPLETNEGO PROGRAMU SZKOLENIA WSTĘPNEGO (Instruktaż Ogólny i Stanowiskowy) dla stanowiska '{nazwa_zawodu}' w firmie '{firma}'.

    DANE DO PERSONALIZACJI:
    - Opis zawodu (Baza): {opis_zawodu}
    - Główne obowiązki: {obowiazki}
    - Środowisko pracy: {srodowisko}
    - Dodatkowe zagrożenia: {dodatkowe_zagrozenia}

    WYMAGANIA PRAWNE:
    Opieraj się na Rozporządzeniu Ministra Gospodarki i Pracy z dnia 27 lipca 2004 r. w sprawie szkolenia w dziedzinie bezpieczeństwa i higieny pracy.

    STRUKTURA DOKUMENTU (BEZWZGLĘDNA):
    
    TYTUŁ: SZCZEGÓŁOWY PROGRAM SZKOLENIA WSTĘPNEGO

    WSTĘP FORMALNY:
    - Wymień wyraźnie podstawy prawne szkolenia (Kodeks Pracy - Dział X, Rozporządzenie w sprawie szkoleń BHP, Polskie Normy). To jest kluczowe.

    CZĘŚĆ I: INSTRUKTAŻ OGÓLNY (Czas trwania: min. 3h lekcyjne)
    Rozwiń merytorycznie każdy z poniższych punktów ramowych nie zmieniając nazw żadnego z punktów:
    1. Istota bezpieczeństwa i higieny pracy.
    2. Zakres obowiązków i uprawnień pracodawcy oraz pracowników.
    3. Odpowiedzialność za naruszenie przepisów lub zasad BHP.
    4. Zasady poruszania się na terenie zakładu pracy (uwzględnij środowisko: {srodowisko}).
    5. Zagrożenia wypadkowe i zagrożenia dla zdrowia występujące w zakładzie i podstawowe środki zapobiegawcze.
    6. Podstawowe zasady BHP związane z obsługą urządzeń technicznych oraz transportem wewnątrzzakładowym.
    7. Zasady przydziału odzieży roboczej i środków ochrony indywidualnej.
    8. Porządek i czystość w miejscu pracy.
    9. Profilaktyczna opieka lekarska.
    10. Podstawowe zasady ochrony przeciwpożarowej.
    11. Postępowanie w razie wypadku i zasady udzielania pierwszej pomocy.

    CZĘŚĆ II: INSTRUKTAŻ STANOWISKOWY (Czas trwania: min. 2h lekcyjne)
    A. Przygotowanie pracownika do wykonywania pracy:
       - Omówienie warunków pracy (oświetlenie, ogrzewanie, wentylacja w: {srodowisko}).
       - Elementy stanowiska roboczego i ergonomia (normy PN-EN).
    
    B. Przebieg procesu pracy (SCALONE - Procesowy):
       Dla każdego obowiązku: {obowiazki} stwórz blok:
       1. Opis czynności.
       2. Zagrożenia przy tej czynności.
       3. Wymagane środki ochrony i zasady bezpiecznego zachowania.
    
    C. Zagrożenia i czynniki uciążliwe na stanowisku:
       - Czynniki fizyczne, chemiczne i psychofizyczne.
       - Ocena ryzyka zawodowego.
    
    D. Sposoby ochrony i postępowanie awaryjne:
       - Bezpieczna obsługa sprzętu.
       - Postępowanie w razie awarii.

    WYTYCZNE KRYTYCZNE ("SAFETY RULES"):
    1. **PODSTAWY PRAWNE:** ZAWSZE cytuj ustawy (używaj słów: "zgodnie z art.", "wg normy PN-EN", "Rozporządzenie").
    2. **LICZBY:** Nie wymyślaj parametrów bez powołania się na normę.
    3. **CZAS:** NIE WPISUJ czasu trwania w godzinach w treść (jest w harmonogramie).
    4. **STYL:** Instruktażowy, konkretny. Bez wstępów typu "Oto plan".
    5. Nie wypisuj na końcu rzeczy w stylu "Potwierdzam, że zapoznałem się z treścią..."

    Stwórz teraz kompletny materiał.
    """
    
    try:
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.3))
        tekst = response.text.strip()
        # (Tutaj Twój kod czyszczący śmieci na początku - zostaw go bez zmian)
        smieci_na_poczatku = ["Oczywiście", "Oto", "Poniżej", "Jasne", "W odpowiedzi", "Zgoda"]
        for smiec in smieci_na_poczatku:
            if tekst.startswith(smiec):
                match = re.search(r"(SZCZEGÓŁOWY|CZĘŚĆ|#)", tekst)
                if match: tekst = tekst[match.start():]
                break
        return tekst
    except Exception as e:
        st.error(f"Błąd API: {e}")
        return "Błąd generowania treści."
    
    

@st.cache_data
def generuj_cel_szkolenia(nazwa_szkolenia):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = f"""
        Jesteś metodykiem nauczania dorosłych.
        Sformułuj CEL SZKOLENIA wstępnego BHP dla stanowiska: '{nazwa_szkolenia}'.
        ZASADY:
        1. Metoda SMART.
        2. Skup się na nabyciu wiedzy i umiejętności.
        3. Jedno, rozbudowane zdanie.
        4. Bez wstępów.
        5. Start: "Celem szkolenia jest..."
        """
        response = model.generate_content(prompt)
        tekst = response.text.replace('*', '').replace('#', '').replace('_', '')
        zbedne = ["Oczywiście", "oto propozycja", ":", "\n"]
        for z in zbedne: tekst = tekst.replace(z, ' ')
        return " ".join(tekst.split()).strip()
    except Exception:
        return "Przygotowanie pracownika do bezpiecznego i ergonomicznego wykonywania pracy na powierzonym stanowisku biurowym."

@st.cache_data
def generuj_test_bhp(_finalna_tresc):
    """Generuje listę pytań kontrolnych (otwartych)."""
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = f"""
    Jesteś instruktorem BHP. Przygotuj zestaw 10 PYTAŃ KONTROLNYCH (otwartych) oraz ZADAŃ PRAKTYCZNYCH do instruktażu stanowiskowego.

    FORMAT:
    1. [Pytanie/Zadanie] - [Oczekiwana odpowiedź/Działanie]
    
    Oprzyj pytania o poniższy materiał:
    {_finalna_tresc[:35000]} 
    
    Nie dodawaj wstępów. Tylko lista numerowana.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip(), None 
    except Exception as e:
        st.error(f"Błąd generowania pytań: {e}")
        return "Błąd.", None

@st.cache_data
def przeprowadz_audyt_tresci(tekst, dane_wejsciowe=""):
    """
    Sprawdza występowanie kluczowych elementów.
    Obsługuje status 'SKIP' dla Personalizacji.
    """
    tekst_lower = tekst.lower()
    
    # 1. Definicja stałych kryteriów
    wyniki = {
        "Podstawa prawna": any(s in tekst_lower for s in ["rozporządzenie", "kodeks pracy", "dz.u.", "art.", "pn-en", "norma", "ustawa", "k.p."]),
        "Instruktaż Ogólny": any(s in tekst_lower for s in ["instruktaż ogólny", "część i", "część 1"]),
        "Instruktaż Stanowiskowy": any(s in tekst_lower for s in ["instruktaż stanowiskowy", "część ii", "część 2"]),
    }

    # 2. Logika Personalizacji (Przywrócona)
    if not dane_wejsciowe or len(dane_wejsciowe.strip()) < 5:
        # Jeśli użytkownik nic nie wpisał (lub wpisał bzdury < 5 znaków), zwracamy "SKIP"
        wyniki["Personalizacja"] = "SKIP"
    else:
        # Jeśli wpisał dane, sprawdzamy czy słowa kluczowe z wejścia są w wyjściu
        slowa_kluczowe = [s.strip() for s in dane_wejsciowe.lower().split() if len(s) > 4]
        # Szukamy przynajmniej jednego pasującego słowa kluczowego (z tolerancją)
        znaleziono = any(slowo in tekst_lower for slowo in slowa_kluczowe)
        wyniki["Personalizacja"] = znaleziono
        
    return wyniki

@st.cache_data
def przypisz_godziny_do_tematow(_spis_tresci_lista):
    """
    Funkcja przypisuje godziny zgodnie z Ramowym Programem Szkolenia (Dz.U.).
    Obsługuje ułamkowe godziny lekcyjne.
    """
    
    # --- NOWA LISTA AWARYJNA (Zgodna z Rozporządzeniem) ---
    lista_awaryjna = [
        {
            "nazwa": "Istota BHP, zakres obowiązków i uprawnień, odpowiedzialność pracownicza",
            "godziny": 0.6
        },
        {
            "nazwa": "Zasady poruszania się po zakładzie, zagrożenia wypadkowe i środki zapobiegawcze",
            "godziny": 0.5
        },
        {
            "nazwa": "Zasady BHP przy obsłudze urządzeń technicznych i transporcie wewnątrzzakładowym",
            "godziny": 0.4
        },
        {
            "nazwa": "Odzież robocza, porządek w miejscu pracy, profilaktyka lekarska",
            "godziny": 0.5
        },
        {
            "nazwa": "Ochrona przeciwpożarowa i pierwsza pomoc",
            "godziny": 1.0
        },
        {
            "nazwa": "INSTRUKTAŻ STANOWISKOWY: Przygotowanie, proces pracy, zagrożenia, wyposażenie",
            "godziny": 2.0
        }
    ]

    # Szybki fallback
    if not _spis_tresci_lista:
        return lista_awaryjna

    model = genai.GenerativeModel(MODEL_NAME)
    tekst_spisu = "\n".join(_spis_tresci_lista)
    
    prompt = f"""
    Jesteś metodykiem BHP. Twoim zadaniem jest pogrupowanie tematów szkolenia w BLOKI PRAWNE zgodne z Ramowym Programem Szkolenia Wstępnego.

    WYMAGANA STRUKTURA I CZAS (Nie zmieniaj godzin, są one narzucone prawnie):
    1. Blok Prawny (Istota BHP, Prawo Pracy, Odpowiedzialność) -> 0.6 h
    2. Blok Organizacyjny (Poruszanie się, Zagrożenia ogólne) -> 0.5 h
    3. Blok Techniczny (Urządzenia, Transport) -> 0.4 h
    4. Blok Higieniczny (Odzież, Porządek, Lekarz) -> 0.5 h
    5. Blok Ratunkowy (PPOŻ, Pierwsza Pomoc) -> 1.0 h
    6. INSTRUKTAŻ STANOWISKOWY (Wszystkie tematy specyficzne dla stanowiska) -> 2.0 h

    Zadanie:
    Dopasuj wykryte w tekście tematy do tych 6 bloków.
    Zwróć wynik WYŁĄCZNIE jako listę JSON w formacie:
    [
        {{"nazwa": "1. [Tytuł bloku]", "godziny": 0.6}},
        {{"nazwa": "2. [Tytuł bloku]", "godziny": 0.5}},
        ...
    ]
    
    SPIS TREŚCI DO PRZETWORZENIA:
    {tekst_spisu}
    """
    
    max_proby = 3
    for proba in range(max_proby):
        try:
            response = model.generate_content(prompt)
            text_resp = response.text.strip()
            
            if text_resp.startswith("```json"): text_resp = text_resp[7:-3]
            elif text_resp.startswith("```"): text_resp = text_resp[3:-3]
            
            dane = json.loads(text_resp)
            
            if not dane or not isinstance(dane, list):
                raise ValueError("Pusty lub niepoprawny JSON")
                
            return dane

        except Exception as e:
            wait_time = (proba + 1) * 2
            time.sleep(wait_time)
            continue

    return lista_awaryjna