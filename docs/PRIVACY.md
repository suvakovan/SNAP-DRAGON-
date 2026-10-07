# Privacy Policy

## Data Collection

**LectureLens collects zero user data.** The application runs entirely offline on-device.

## What Stays Local

| Data Type | Storage Location | Cloud Transmission |
|---|---|---|
| Audio recordings | `data/` directory | âŒ Never |
| Transcripts | `data/sessions/` | âŒ Never |
| Study notes | `data/sessions/` | âŒ Never |
| Quiz answers | In-memory only | âŒ Never |
| Search index | `data/search_index/` | âŒ Never |
| Model weights | `models/` directory | âŒ Never |

## Network Verification

Run the offline verification script to confirm no network connections:

```powershell
python scripts/offline_check.py
```

## Third-Party Services

LectureLens does NOT use:
- Cloud AI APIs (OpenAI, Google, AWS, etc.)
- Analytics or tracking services
- Telemetry or crash reporting
- Remote model downloads at runtime

## Model Downloads

Model files are downloaded once during setup via `scripts/download_models.py`. After initial setup, the application operates fully offline.
