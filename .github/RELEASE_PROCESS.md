# Release Process

Schritt-für-Schritt Anleitung zum Erstellen eines neuen MemDoc Release.

## Voraussetzungen

- Alle Tests müssen grün sein
- Alle Änderungen sind committed
- CHANGELOG.md ist aktualisiert

## Release erstellen

### 1. Version aktualisieren

Bearbeite `core/version.py`:

```python
VERSION = "1.1.0"  # Neue Version
RELEASE_DATE = "2025-12-26"  # Heutiges Datum
```

### 2. CHANGELOG.md aktualisieren

Verschiebe Änderungen von `[Unreleased]` zu einem neuen Versions-Abschnitt:

```markdown
## [1.1.0] - 2025-12-26

### Hinzugefügt
- Frontend Update-UI
- Automatische Update-Prüfung
...
```

### 3. Commit und Push

```bash
git add core/version.py CHANGELOG.md
git commit -m "Bump version to 1.1.0"
git push origin main
```

### 4. Tag erstellen und pushen

```bash
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

**Wichtig:** Der Tag muss mit `v` beginnen (z.B. `v1.1.0`)

### 5. GitHub Actions läuft automatisch

Nach dem Push des Tags:
1. GitHub Actions startet automatisch
2. Baut `MemDoc.exe` mit PyInstaller
3. Erstellt ein GitHub Release
4. Lädt die .exe hoch

Überwache den Fortschritt: https://github.com/swahed/memdoc/actions

### 6. Release Notes vervollständigen

Nach der automatischen Erstellung:
1. Gehe zu: https://github.com/swahed/memdoc/releases
2. Klicke auf "Edit" beim neuen Release
3. Ersetze den Platzhalter `<!-- Füge hier die Änderungen ein -->` mit:
   - Neuen Features (✨)
   - Verbesserungen (🔧)
   - Bugfixes (🐛)
4. Verwende `.github/RELEASE_TEMPLATE.md` als Vorlage
5. Speichere die Änderungen

### 7. Testen

1. Lade die `MemDoc.exe` aus dem Release herunter
2. Führe sie aus und teste grundlegende Funktionen
3. Teste die Update-Funktion (erstelle ein weiteres Test-Release v1.1.1)

## Versionsschema (Semantic Versioning)

- **Major (X.0.0)**: Breaking Changes, große neue Features
- **Minor (1.X.0)**: Neue Features, abwärtskompatibel
- **Patch (1.1.X)**: Bugfixes, kleine Verbesserungen

Beispiele:
- `1.0.0` → `1.1.0`: Neue Features (Update-UI)
- `1.1.0` → `1.1.1`: Bugfix
- `1.1.0` → `2.0.0`: Breaking Change

## Hotfix-Prozess

Für dringende Bugfixes:

```bash
# Erstelle Hotfix-Branch von Tag
git checkout -b hotfix/1.1.1 v1.1.0

# Fixe den Bug
git commit -m "Fix critical bug"

# Update Version zu 1.1.1
# Update CHANGELOG

# Merge zurück
git checkout main
git merge hotfix/1.1.1

# Tag und Release
git tag -a v1.1.1 -m "Hotfix v1.1.1"
git push origin main v1.1.1
```

## Rollback eines Release

Falls ein Release Probleme hat:

1. Erstelle einen neuen Patch-Release mit dem Fix
2. **NIEMALS** ein GitHub Release löschen (bricht Update-Mechanismus)
3. Markiere problematisches Release als "Pre-release" wenn nötig

## Troubleshooting

### Build schlägt fehl

- Prüfe GitHub Actions Logs
- Teste `python build.py` lokal
- Stelle sicher, dass alle Dependencies in `requirements.txt` sind

### Release wird nicht erstellt

- Prüfe, dass Tag mit `v` beginnt
- Prüfe GitHub Actions Permissions
- Stelle sicher, dass `GITHUB_TOKEN` verfügbar ist

### .exe fehlt im Release

- Prüfe PyInstaller Logs in GitHub Actions
- Stelle sicher, dass `dist/MemDoc.exe` existiert
- Prüfe Pfad in workflow (`./dist/MemDoc.exe`)

## Checkliste

Vor jedem Release:

- [ ] Alle Tests grün (`pytest`)
- [ ] Version in `core/version.py` erhöht
- [ ] CHANGELOG.md aktualisiert
- [ ] Änderungen committed und gepusht
- [ ] Tag erstellt mit `v` Prefix
- [ ] Tag gepusht
- [ ] GitHub Actions erfolgreich gelaufen
- [ ] Release Notes vervollständigt
- [ ] .exe heruntergeladen und getestet
- [ ] Update-Funktion getestet (optional)
