# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

## [Unreleased]

## [1.1.7] - 2025-12-26

### Verbessert
- Versionsnummer in Statusleiste jetzt fett dargestellt (bessere Sichtbarkeit)

### Hinweis
- Test-Release für Update-Mechanismus (v1.1.6 → v1.1.7)

## [1.1.6] - 2025-12-26

### Behoben
- Update-Mechanismus funktioniert jetzt korrekt in der .exe
- Dev-Mode-Erkennung basiert jetzt auf PyInstaller-Bundle-Status statt localhost
- Updates sind nun für .exe-Builds verfügbar

## [1.1.5] - 2025-12-26

### Hinzugefügt
- Versionsnummer in der Statusleiste angezeigt (unten rechts)

### Hinweis
- Dieser Release dient zum Testen des Update-Mechanismus

## [1.1.4] - 2025-12-26

### Verbessert
- Microsoft Edge Unterstützung hinzugefügt (standardmäßig auf Windows installiert)
- App funktioniert jetzt mit Chrome ODER Edge
- Automatische Browser-Erkennung mit Fallback zum Standard-Browser

## [1.1.3] - 2025-12-26

### Behoben
- Desktop-Modus komplett überarbeitet: Eel entfernt, Chrome direkt mit --app Flag geöffnet
- "Not Found" Fehler endgültig behoben
- Einfachere und zuverlässigere Desktop-Integration

### Geändert
- Eel-Abhängigkeit entfernt (nicht mehr benötigt)

## [1.1.2] - 2025-12-26

### Behoben
- Eel-Flask Integration: eel.start() verwendet jetzt URL-Route statt Dateiname

## [1.1.1] - 2025-12-26

### Behoben
- PyInstaller Bundle-Pfade: App findet jetzt Templates und Ressourcen korrekt

## [1.1.0] - 2025-12-26

### Hinzugefügt
- Frontend Update-UI mit automatischer Update-Prüfung
- Update-Banner mit Download-Fortschritt
- Rollback-Funktion zu früheren Versionen
- Manuelle Update-Prüfung in den Einstellungen
- GitHub Actions für automatische Release-Erstellung

## [1.0.0] - 2025-12-26

### Hinzugefügt
- Kern-Schreibfunktionen (Kapitel erstellen, bearbeiten, löschen)
- Markdown-Editor mit Formatierungs-Toolbar
- Deutsche Benutzeroberfläche
- Titelseite mit Bild und Farbauswahl
- PDF-Export für einzelne Kapitel und gesamte Memoiren
- Bild-Upload mit Qualitätsprüfung
- Schreibimpulse-Sidebar mit 40 deutschen Vorschlägen
- Konfigurierbarer Datenspeicherort (OneDrive-Integration)
- Automatisches Speichern
- Wortanzahl pro Kapitel
- Sicheres Löschen (Kapitel werden archiviert)
- Desktop-App Modus mit PyInstaller
- Automatische Backup-Erstellung vor Updates
- Test-Build-Isolation (separate Datenverzeichnisse)

### Technisch
- Flask Backend mit Python 3.10+
- WeasyPrint für PDF-Generierung
- Markdown-basierte Datenspeicherung
- YAML Frontmatter für Metadaten
- Vollständige Test-Abdeckung (62% gesamt, 96% kritische Module)

---

## Versionstypen

- **Hinzugefügt** - Neue Features
- **Geändert** - Änderungen an bestehenden Features
- **Veraltet** - Features, die bald entfernt werden
- **Entfernt** - Entfernte Features
- **Behoben** - Bugfixes
- **Sicherheit** - Sicherheits-Updates
