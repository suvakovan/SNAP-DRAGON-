# Export Formats Reference

LectureLens supports multiple export formats for study materials.

## Markdown Study Sheet (`export_study_sheet`)
Complete formatted study document with summary, key terms, quiz, and flashcards.
```
Title â€” Study Sheet
Summary bullets
Key terms with definitions
Quiz with answer key
Flashcards
```

## Anki CSV (`export_anki_csv`)
Compatible with [Anki](https://apps.ankiweb.net/) spaced repetition software.
- Format: `question, answer, tags`
- Import directly into Anki deck

## SRT Subtitles (`export_srt`)
Standard SubRip subtitle format for video overlay.
```
1
00:00:00,000 --> 00:00:10,000
First segment text
```

## Plain Transcript (`export_plain_transcript`)
Timestamped plain text transcript.
```
[0.0s] First segment
[10.0s] Second segment
```

## Markdown Notes (`export_markdown`)
Executive summary with backend performance metrics.

## Usage

```python
from lecturelens.storage.exports import export_anki_csv, export_srt
from lecturelens.storage.store import export_markdown

# Export single session
path = export_anki_csv(session)
path = export_srt(session)
path = export_markdown(session)
```

```powershell
# Batch export all sessions
python scripts/export_all.py --format all
```
