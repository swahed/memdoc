/**
 * Internationalization (i18n) Module
 * Provides translation functionality for the app
 */

const i18n = {
    locale: 'de',  // Default to German

    strings: {
        de: {
            // App title and navigation
            appTitle: 'MemDoc',
            newChapter: '+ Neues Kapitel',
            noChaptersYet: 'Noch keine Kapitel. Erstelle dein erstes Kapitel!',

            // Editor placeholders
            chapterTitlePlaceholder: 'Kapiteltitel',
            subtitlePlaceholder: 'Untertitel (optional)',
            editorPlaceholder: `Beginne deine Memoiren zu schreiben...

Du kannst einfache Formatierung verwenden:
**fett** für fetten Text
*kursiv* für kursiven Text
# Überschrift für Abschnittsüberschriften`,

            // Formatting toolbar tooltips
            boldTitle: 'Fett (Strg+B)',
            italicTitle: 'Kursiv (Strg+I)',
            removeFormattingTitle: 'Formatierung entfernen',
            heading1Title: 'Überschrift 1',
            heading2Title: 'Überschrift 2',
            heading3Title: 'Überschrift 3',
            insertImageTitle: 'Bild einfügen',
            previewChapterTitle: 'Kapitel-Vorschau',
            exportPDFTitle: 'Als PDF exportieren',

            // Status bar
            statusReady: 'Bereit',
            statusSaving: 'Speichern...',
            statusSaved: 'Gespeichert',
            statusError: 'Fehler beim Speichern',
            statusLoading: 'Laden...',

            // Word count
            wordsSingular: 'Wort',
            wordsPlural: 'Wörter',

            // Writing prompts
            writingPrompts: 'Schreibanregungen',
            loadingPrompts: 'Lade Schreibanregungen...',
            failedToLoadPrompts: 'Fehler beim Laden der Schreibanregungen',
            toggleWritingPrompts: 'Schreibanregungen ein-/ausblenden',

            // Image upload modal
            insertImage: 'Bild einfügen',
            dragImageHere: 'Bild hierher ziehen oder klicken zum Durchsuchen',
            imageFormatsHint: 'JPG, PNG, GIF, WebP - Max. 20MB',
            file: 'Datei',
            size: 'Größe',
            dimensions: 'Abmessungen',
            position: 'Position',
            positionCenter: 'Zentriert',
            positionLeft: 'Links (Text umfließt)',
            positionRight: 'Rechts (Text umfließt)',
            positionFull: 'Volle Breite',
            displaySize: 'Anzeigegröße',
            sizeSmall: 'Klein (300px)',
            sizeMedium: 'Mittel (500px)',
            sizeLarge: 'Groß (700px)',
            sizeFull: 'Volle Breite',
            captionOptional: 'Bildunterschrift (optional)',
            captionPlaceholder: 'Beschreibe das Foto...',

            // Image tips
            imageTipsTitle: '💡 Tipps für beste Ergebnisse:',
            imageTip1: 'Verwende Originalfotos von Kamera/Scanner (keine Screenshots)',
            imageTip2: 'Ziele auf mindestens 1500 Pixel Breite für gute Druckqualität',
            imageTip3: 'Mittlere Größe (500px) funktioniert gut für die meisten Memoiren-Fotos',
            imageTip4: 'JPG-Format ist am besten für Fotos, PNG für Diagramme',

            // Image warnings
            lowResolutionWarning: 'Niedrige Auflösung! Bild druckt möglicherweise nicht gut. Mindestens 300 DPI empfohlen.',
            goodQualityForPrinting: 'Gute Qualität zum Drucken',

            // Image upload errors
            pleaseSelectImageFile: 'Bitte wähle eine Bilddatei (JPG, PNG, GIF, WebP)',
            imageTooLarge: 'Bilddatei ist zu groß. Maximale Größe ist 20MB.',
            failedToUploadImage: 'Fehler beim Hochladen des Bildes',

            // Preview modal
            chapterPreview: 'Kapitel-Vorschau',

            // Buttons
            close: 'Schließen',
            cancel: 'Abbrechen',
            insertImageButton: 'Bild einfügen',
            exportToPDF: 'Als PDF exportieren',

            // Chapter management prompts
            enterChapterTitle: 'Kapiteltitel eingeben:',
            enterChapterSubtitle: 'Kapitel-Untertitel eingeben (optional):',
            enterNewChapterTitle: 'Neuen Kapiteltitel eingeben:',
            enterNewSubtitle: 'Neuen Untertitel eingeben (optional):',

            // Chapter actions tooltips
            moveUp: 'Nach oben',
            moveDown: 'Nach unten',
            editChapter: 'Kapitel bearbeiten',
            deleteChapter: 'Kapitel löschen',

            // Delete confirmation
            deleteChapterConfirm: 'Löschen',
            deleteChapterMessage: 'löschen?\n\nDas Kapitel wird aus deinen Memoiren entfernt, aber die Datei wird im Ordner "deleted" auf deiner Festplatte gespeichert, sodass du sie bei Bedarf wiederherstellen kannst.',
            untitledChapter: 'Unbenanntes Kapitel',

            // Error messages
            failedToLoadChapters: 'Fehler beim Laden der Kapitel',
            failedToCreateChapter: 'Fehler beim Erstellen des Kapitels',
            failedToLoadChapter: 'Fehler beim Laden des Kapitels',
            failedToEditChapter: 'Fehler beim Bearbeiten des Kapitels',
            failedToDeleteChapter: 'Fehler beim Löschen des Kapitels',
            failedToReorderChapter: 'Fehler beim Neuordnen des Kapitels',
            failedToShowPreview: 'Fehler beim Anzeigen der Vorschau',
            failedToExportPDF: 'Fehler beim PDF-Export',

            // PDF export
            pdfExportNotAvailable: 'PDF-Export nicht verfügbar',
            pdfExportedSuccessfully: 'PDF erfolgreich exportiert! Überprüfe deinen Downloads-Ordner.',

            // Headings placeholders
            heading1Placeholder: 'Überschrift 1',
            heading2Placeholder: 'Überschrift 2',
            heading3Placeholder: 'Überschrift 3',

            // Formatting placeholders
            boldTextPlaceholder: 'fetter Text',
            italicTextPlaceholder: 'kursiver Text',

            // Cover page
            coverPage: 'Titelseite',
            editCoverPage: 'Titelseite bearbeiten',
            coverTitle: 'Titel',
            coverTitlePlaceholder: 'Titel deiner Memoiren',
            coverSubtitle: 'Untertitel',
            coverSubtitlePlaceholder: 'Untertitel (optional)',
            coverAuthor: 'Autor',
            coverAuthorPlaceholder: 'Dein Name',
            coverImage: 'Titelbild (optional)',
            chooseCoverImage: 'Titelbild wählen',
            removeCoverImage: 'Titelbild entfernen',
            previewCover: 'Vorschau',
            saveCover: 'Speichern',
            coverSaved: 'Titelseite gespeichert!',
            failedToSaveCover: 'Fehler beim Speichern der Titelseite',
            failedToLoadCover: 'Fehler beim Laden der Titelseite'
        }
    },

    /**
     * Get translated string
     * @param {string} key - Translation key
     * @param {object} params - Optional parameters for string interpolation
     * @returns {string} Translated string
     */
    t(key, params = {}) {
        let text = this.strings[this.locale]?.[key] || key;

        // Simple parameter substitution
        Object.keys(params).forEach(param => {
            text = text.replace(`{${param}}`, params[param]);
        });

        return text;
    },

    /**
     * Get word count text with correct plural form
     * @param {number} count - Word count
     * @returns {string} Formatted word count text
     */
    wordCount(count) {
        const word = count === 1 ? this.t('wordsSingular') : this.t('wordsPlural');
        return `${count} ${word}`;
    }
};

// Export for use in other modules
window.i18n = i18n;
