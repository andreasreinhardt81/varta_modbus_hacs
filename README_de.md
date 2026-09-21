[🇩🇪 Deutsch](README_de.md) | [🇬🇧 English](README.md)

# VARTA Modbus

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.9%2B-green.svg)](https://www.home-assistant.io/)

Home-Assistant-Integration für VARTA-Energiespeichersysteme auf Basis von Modbus TCP und der modernen gemeinsamen Modbus-Verbindungsarchitektur von Home Assistant.

Die Integration stellt Batterie-, Netz- und Diagnosedaten bereit und ermöglicht zusätzlich das Schreiben ausgewählter Leistungsgrenzen direkt aus Home Assistant.

---

# Funktionen

## Batterieüberwachung

Die Integration stellt folgende Daten bereit:

- Betriebszustand
- Wirkleistung
- Scheinleistung
- Ladeleistung
- Entladeleistung
- Ladezustand (SOC)
- AC-zu-DC-Energie
- Installierte Kapazität

## Netzüberwachung

- Netzleistung

## Diagnoseinformationen

- Installierte Batteriemodule
- Tabellenversion
- EMS-Softwareversion
- ENS-Softwareversion
- Hauptsoftwareversion
- Watchdog-Timeout

## Beschreibbare Leistungsgrenzen

Direkter Zugriff auf folgende VARTA-Register:

| Register | Funktion |
|-----------|----------|
| 1074 | Maximale Entladeleistung |
| 1075 | Maximale Ladeleistung |

Typische Anwendungsfälle:

- Dynamische Stromtarife
- PV-Überschussladen
- Energiemanagementsysteme (EMS)
- Peak-Shaving
- Einspeisebegrenzung

---

# Voraussetzungen

- Home Assistant 2026.9 oder neuer
- VARTA-Energiespeicher mit Modbus-TCP-Unterstützung
- Netzwerkverbindung zwischen Home Assistant und Speicher

Standardwerte:

| Parameter | Standard |
|-----------|-----------|
| Port | 502 |
| Unit-ID | 1 |

---

# Installation

## HACS

1. HACS öffnen
2. Integrationen auswählen
3. Benutzerdefinierte Repositories öffnen
4. Dieses Repository als Integration hinzufügen
5. Nach „VARTA Modbus“ suchen
6. Installation durchführen
7. Home Assistant neu starten

## Manuelle Installation

Ordner:

```text
custom_components/varta_modbus
```

kopieren nach:

```text
config/custom_components/
```

Danach Home Assistant neu starten und die Integration unter:

```text
Einstellungen → Geräte & Dienste → Integration hinzufügen
```

hinzufügen.

---

# Konfiguration

Die Einrichtung erfolgt vollständig über den Home-Assistant-Konfigurationsdialog.

Benötigt werden:

- Hostname oder IP-Adresse
- Modbus-Port
- Unit-ID

Die Verbindung wird während der Einrichtung überprüft.

Über die Funktion **Neu konfigurieren** können die Einstellungen später geändert werden.

---

# Verfügbare Entitäten

## Sensoren

| Entität | Beschreibung |
|----------|-------------|
| Status | Aktueller Betriebszustand |
| Wirkleistung | Aktuelle Batterieleistung |
| Ladeleistung | Aktuelle Ladeleistung |
| Entladeleistung | Aktuelle Entladeleistung |
| Scheinleistung | Aktuelle Scheinleistung |
| Ladezustand | Batterieladezustand |
| AC-zu-DC-Energie | Energiezähler |
| Installierte Kapazität | Installierte Speicherkapazität |
| Netzleistung | Aktuelle Netzleistung |

## Diagnose-Sensoren

| Entität | Beschreibung |
|----------|-------------|
| Installierte Batteriemodule | Anzahl der Batteriemodule |
| Tabellenversion | Version der Registertabelle |
| EMS-Software | EMS-Firmwareversion |
| ENS-Software | ENS-Firmwareversion |
| Software | Hauptfirmwareversion |

## Einstellbare Leistungsgrenzen

| Entität | Beschreibung |
|----------|-------------|
| Maximale Ladeleistung | Beschreibbare Ladegrenze |
| Maximale Entladeleistung | Beschreibbare Entladegrenze |

---

# Betriebszustände

| Zustand | Bedeutung |
|----------|-----------|
| Aktiv | Verarbeitung läuft |
| Normalbetrieb | Regulärer Betrieb |
| Laden | Batterie lädt |
| Entladen | Batterie entlädt |
| Bereitschaft | Standby |
| Fehler | Fehlerzustand |
| Wartungsbetrieb | Servicebetrieb |
| Inselbetrieb | Netzunabhängiger Betrieb |

---

# Beschreibbare Leistungsgrenzen

Unterstützte Register:

| Register | Funktion |
|-----------|----------|
| 1074 | Maximale Entladeleistung |
| 1075 | Maximale Ladeleistung |

## Vorzeichenkonvention

VARTA verwendet intern vorzeichenbehaftete Werte:

| Vorgang | Beispiel |
|----------|----------|
| Laden | +4000 W |
| Entladen | -4000 W |

Beispiele:

```text
+4000 = Laden auf 4 kW begrenzen
-4000 = Entladen auf 4 kW begrenzen
```

---

# 500-W-Grenze

Viele VARTA-Firmwarestände akzeptieren keine Leistungsgrenzen unterhalb von etwa 500 W.

Typische gültige Werte:

```text
Maximale Entladeleistung:
0 W
oder <= -500 W

Maximale Ladeleistung:
0 W
oder >= 500 W
```

Werte innerhalb dieser Bereiche können vom Speicher abgelehnt werden.

Die Integration prüft diese Grenzwerte vor dem Schreiben.

---

# Watchdog-Verhalten

Das Schreiben auf Register 1074 oder 1075 aktiviert den externen VARTA-Leistungsregler.

Verwendete Register:

| Register | Funktion |
|----------|----------|
| 1073 | Watchdog-Timeout |
| 1074 | Maximale Entladeleistung |
| 1075 | Maximale Ladeleistung |

Aktuelle Implementierung:

- Watchdog-Timeout: 120 Sekunden
- Automatische Aktualisierung: alle 60 Sekunden

Solange ein externer Leistungswert aktiv ist, aktualisiert die Integration die Register automatisch, damit der Speicher nicht auf die internen Standardwerte zurückfällt.

---

# Migration von varta_storage

Alte Integration:

```text
varta_storage
```

Neue Integration:

```text
varta_modbus
```

Vorgehensweise:

1. Alte Integration entfernen
2. Alte Dateien löschen
3. VARTA Modbus installieren
4. Neue Integration anlegen

Der gleichzeitige Betrieb beider Integrationen mit demselben Speicher wird nicht empfohlen.

---

# Diagnostik

Die Integration unterstützt Home-Assistant-Diagnosedaten.

Beim Export werden automatisch anonymisiert:

- IP-Adressen
- Seriennummern

Damit können Diagnosedaten gefahrlos weitergegeben werden.

---

# Fehlerbehebung

## Verbindung kann nicht aufgebaut werden

Prüfen:

- Modbus TCP aktiviert
- IP-Adresse korrekt
- Port korrekt
- Unit-ID korrekt
- Firewall-Einstellungen

## Daten werden nicht aktualisiert

Prüfen:

- Netzwerkverbindung
- Geräteverfügbarkeit
- Home-Assistant-Protokolle

## Leistungsgrenzen wirken nicht

Prüfen:

- 500-W-Grenze eingehalten
- Watchdog aktiv
- Firmware unterstützt externe Leistungsregelung

---

# Mitwirken

Beiträge sind willkommen.

Bitte vor einem Pull Request die Datei:

```text
CONTRIBUTING.md
```

lesen.

---

# Haftungsausschluss

Dieses Projekt steht in keiner Verbindung zu VARTA AG und wird weder unterstützt noch freigegeben.

Die Verwendung erfolgt auf eigene Verantwortung.
