# MTGA Log parser

Simple client for passing relevant events from MTG Arena logs to the 17Lands REST endpoint.

## For developers

### Installing dependencies

```bash
uv sync
```

### Running the log parser

Running using `uv`:

```
uv run 17lands.py
```

### Environment Variables

The application supports the following environment variables:

- `SEVENTEENLANDS_COLOR_LOGS`: Controls whether console logs use color formatting. Set to `false` to disable colors (default: `true`).

## Notes

Licensed under GNU GPL v3.0 (see included LICENSE).

This MTGA log follower is unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC. See https://company.wizards.com/fancontentpolicy for more details.
