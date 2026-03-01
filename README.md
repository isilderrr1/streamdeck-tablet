# StreamDeck Tablet

Questo progetto crea un **stream deck personalizzato** utilizzando un tablet Android come interfaccia per controllare azioni specifiche su un PC. Utilizza **AutoHotkey** per eseguire macro personalizzate (come aprire applicazioni su schermi specifici) e un **server Flask** per gestire la comunicazione tra il tablet e il PC.

![Configurazione](/setup.jpeg)

## Funzionalità

- **Controllo delle applicazioni**: Premi i tasti per eseguire azioni come aprire **Terminale**, **VS Code**, **YouTube**, **Discord**, ecc., su schermi specifici del tuo PC.
- **Calendario Google**: Visualizza eventi del calendario Google direttamente sullo schermo del tablet.
- **Meteo**: Mostra la temperatura attuale (Napoli) con l'icona corrispondente.
- **Modalità Offline**: Se il PC non è raggiungibile (offline), lo schermo del tablet mostra l'ora e un messaggio che indica che il PC è offline.

## Architettura

- **PC (Windows)**: Eseguito con **AutoHotkey** per gestire le macro e **Flask** per il server web che comunica con il tablet.
- **Tablet Android**: Utilizza **Fully Kiosk Browser** per aprire il pannello e inviare richieste al server Flask.
  
Il progetto utilizza un **server Flask** per esporre un'API RESTful che consente al tablet di interagire con il PC, eseguendo comandi come l'apertura di applicazioni su schermi specifici.

## Tecnologie

- **Flask**: Framework Python per la gestione delle API.
- **AutoHotkey**: Linguaggio di scripting per la gestione delle macro su Windows.
- **Fully Kiosk Browser**: Browser Android per visualizzare l'interfaccia del pannello.
- **Open-Meteo API**: API gratuita per ottenere il meteo.
- **Google Calendar iCal API**: Per visualizzare gli eventi dal calendario Google.

## Come funziona

### Lato Server (PC)
1. **Flask** gestisce un server che espone le seguenti funzionalità:
   - **API per le macro**: Quando viene premuto un tasto sul tablet, viene inviata una richiesta POST al server Flask, che esegue la macro corrispondente (ad esempio, aprire il terminale o Discord su un monitor specifico).
   - **API per il calendario**: Recupera gli eventi dal calendario Google e li visualizza sul tablet.
   - **API per il meteo**: Recupera i dati del meteo attuale tramite Open-Meteo e li visualizza sul tablet.

2. **AutoHotkey** esegue i comandi per spostare le finestre delle applicazioni sui monitor specificati.

### Lato Client (Tablet)
1. Il tablet visualizza un'interfaccia tramite **Fully Kiosk Browser**, che include:
   - Un calendario.
   - I tasti per eseguire le azioni sul PC.
   - Un'area per il meteo.
   - Un'area per l'orologio e la data.

2. Ogni tasto invia una richiesta POST al server Flask per eseguire l'azione corrispondente.

3. Se il PC è offline, viene visualizzato un messaggio che indica che il PC non è raggiungibile.

## Come configurarlo

### 1. Preparazione del server
- Installa **Python 3.x** sul PC.
- Installa le librerie necessarie con:
  ```bash
  pip install Flask requests icalendar
   ```

2. Impostazione del tablet

Installa Fully Kiosk Browser sul tablet Android.

Configura l'URL del server (ad esempio: http://IP_DEL_PC:5000) come pagina di avvio.

Imposta il tablet in modalità kiosk per fare in modo che l'interfaccia non venga chiusa accidentalmente.

3. Esecuzione del server

Avvia il server Flask:

 ```bash
python server.py
 ```

### 4. Uso

Una volta che il server è in esecuzione, apri l'interfaccia sul tablet.

Premi i tasti per eseguire le macro sul PC, visualizzare il calendario e il meteo.
