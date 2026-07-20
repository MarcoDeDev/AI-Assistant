# Architekturentscheidungen

## API-Versionierung

Die REST-API verwendet von Beginn an das Präfix `/api/v1`.

### Gründe

- Klare Versionierung der API.
- Spätere Einführung von `/api/v2` ohne Breaking Changes.
- Gängige Praxis in professionellen REST-APIs.

## Trennung zwischen API und Business-Logik

Die API-Router enthalten ausschließlich HTTP-spezifische Logik.

Die eigentliche Geschäftslogik wird in Services implementiert.

### Gründe

- Bessere Testbarkeit
- Wiederverwendbarkeit
- Klare Verantwortlichkeiten
- Einfache Erweiterung für weitere Clients (Flutter, CLI, Agenten)

## Zentrale Konfiguration

Die gesamte Anwendung verwendet eine zentrale Konfigurationsklasse (`Settings`).

### Gründe

- Keine Konfiguration im Code
- Einfache Anpassung zwischen Entwicklung und Produktion
- API-Keys werden nicht im Quellcode gespeichert
- Einheitlicher Zugriff auf Konfigurationswerte

## LLM-Abstraktion

Der ChatService kommuniziert nicht direkt mit einem konkreten KI-Modell.

Stattdessen erfolgt die Kommunikation über eine gemeinsame LLM-Schnittstelle.

### Gründe

- Austausch des KI-Modells ohne Änderungen am ChatService
- Einfache Tests mit Mock-Implementierungen
- Unterstützung mehrerer Provider (OpenAI, Ollama, Claude ...)
- Geringe Kopplung zwischen Business-Logik und externen Diensten

## LLM-Zugriff über externe API

Das Sprachmodell wird über eine externe API angesprochen.

### Gründe

- Keine lokale GPU erforderlich
- Aktuelle Modelle stehen sofort zur Verfügung
- Anbieter kann später ausgetauscht werden
- Abrechnung erfolgt nutzungsbasiert pro Token

## Provider-Kapselung

Jeder LLM-Anbieter erhält eine eigene Implementierung der `BaseLLM`-Schnittstelle.

### Gründe

- Geringe Kopplung
- Austauschbarkeit der Anbieter
- Klare Verantwortlichkeiten
- Einfache Erweiterbarkeit

## Dependency Injection

Objekte werden nicht innerhalb der Klassen erzeugt.

Alle Abhängigkeiten werden zentral über Dependency Provider bereitgestellt.

### Gründe

- Geringe Kopplung
- Hohe Testbarkeit
- Wiederverwendbarkeit
- Austauschbarkeit von Implementierungen
- Einheitliche Erstellung gemeinsam genutzter Ressourcen

## Adapter für externe KI-Anbieter

Die Kommunikation mit externen LLM-Anbietern erfolgt ausschließlich über Adapter-Klassen.

### Gründe

- Entkopplung der Anwendung von Anbieter-APIs
- Einfacher Austausch von SDKs oder Endpunkten
- Zentrale Anpassung bei API-Änderungen
- Bessere Testbarkeit

## Composition Root

Alle Objekte werden zentral in `core/dependencies.py` erstellt.

Klassen greifen nicht direkt auf globale Konfigurationen oder Singleton-Objekte zu.

### Gründe

- Explizite Abhängigkeiten
- Höhere Testbarkeit
- Geringere Kopplung
- Zentrale Objektverwaltung

## Domänenmodell für LLM-Antworten

Alle LLM-Provider liefern ein gemeinsames Domänenmodell (`LLMResponse`) zurück.

### Gründe

- Einheitliche Schnittstelle für alle Anbieter
- Entkopplung vom OpenAI-SDK
- Zentrale Erweiterbarkeit
- Keine externen SDK-Klassen außerhalb der Adapter

## Logging

Die Anwendung verwendet das Python-Logging-Modul.

Die Konfiguration erfolgt zentral in `app/core/logging.py`.

Jede Datei erstellt ihren eigenen Logger über:

```python
logger = logging.getLogger(__name__)

## Performance-Messung

Die Dauer einer Chat-Anfrage wird im `ChatService` mit `time.perf_counter()` gemessen.

### Gründe

- Monotone Uhr
- Hohe Präzision
- Messung der gesamten Business-Operation
- Grundlage für Monitoring und Performance-Optimierung