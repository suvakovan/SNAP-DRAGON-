# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Privacy-First Architecture

LectureLens is designed as a fully offline application:

- **No cloud API calls**: All inference runs locally on-device
- **No telemetry**: Zero data collection or phone-home behavior
- **Local storage only**: All sessions, transcripts, and notes stay on disk
- **Offline verification**: `scripts/offline_check.py` validates no network sockets are opened

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Email the maintainers directly with details
3. Include steps to reproduce the vulnerability
4. Allow 72 hours for initial response

## Security Considerations

- Audio recordings contain sensitive lecture content â€” stored only in `data/sessions/`
- Model files in `models/` should be verified against known checksums
- The `.env` file may contain endpoint configurations â€” never commit it (it's in `.gitignore`)
