# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

## [Unreleased]

### Hinzugefügt
- Frontend Update-UI mit automatischer Update-Prüfung
- Update-Banner mit Download-Fortschritt
- Rollback-Funktion zu früheren Versionen
- Manuelle Update-Prüfung in den Einstellungen

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
