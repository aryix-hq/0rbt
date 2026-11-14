# Apple Media Ecosystem & Library Safety Standards

This standard governs all interactions with macOS Apple Photos, iMovie, and macOS media subsystems executed by agents in this repository.

---

## 1. Photos Library Immutability Invariant

- **Zero Direct SQLite Mutation**: The internal database of the macOS Photos Library (`~/Pictures/Photos Library.photoslibrary/database/Photos.sqlite`) is an Apple proprietary storage structure. Under no circumstance may an agent or script execute `INSERT`, `UPDATE`, or `DELETE` SQL operations directly on `Photos.sqlite`. Direct modification risks permanent corruption of the user's media database.
- **Read-Only Inspection**: Any SQLite query used for metadata auditing or index inspection must be executed strictly with the read-only URI parameter:
  ```bash
  sqlite3 "file:$HOME/Pictures/Photos%20Library.photoslibrary/database/Photos.sqlite?mode=ro"
  ```
- **Authoritative Ingest via AppleScript**: Asset retrieval, album listing, and media extraction must execute via AppleScript / JXA (`osascript`), which interfaces safely with the running Photos daemon.

---

## 2. Non-Destructive Media Staging

- **Isolated Staging Directories**: Media exported from Apple Photos must be written to designated project staging directories (e.g., `assets/raw/`, `/tmp/photos_staging/`).
- **Preserve Master Files**: Never delete, move, or rename master files inside `Photos Library.photoslibrary/originals/`.
- **Master Quality Export**: Media exports intended for professional NLE editing must use the AppleScript option `with using originals` to avoid lossy re-compression:
  ```applescript
  tell application "Photos"
    export {targetMedia} to POSIX file stagingPath with using originals
  end tell
  ```

---

## 3. macOS TCC Security & Permission Graceful Handling

- **Apple Events Authorization**: Interfacing with Apple Photos, Final Cut Pro, or iMovie via `osascript` requires macOS Accessibility & Automation (TCC) privileges.
- **Fault-Tolerant Execution**: Scripts must catch permission errors (e.g., `-1743: Not authorized to send Apple events`) and emit clear user instructions:
  - *"Please grant Antigravity / Terminal permission in macOS System Settings > Privacy & Security > Automation."*
- **Offline Mock Fallback**: All CLI tools and MCP servers must provide simulated offline / mock operational paths for continuous integration and non-macOS environments.

---

## 4. Metadata & EXIF Preservation

- **Camera & Sensor Provenance**: When ingesting or organizing media assets, retain:
  - Camera make and model (e.g., iPhone 16 Pro, Sony FX3)
  - Color profile / Transfer function (e.g., Apple Log, Rec.709)
  - Exposure timestamp (UTC)
  - Focal length, aperture, ISO, and shutter speed
- **Search Metadata**: Leverage photo metadata tags (`favorite`, `keyword`, `album_name`) to automate asset selection for video rough cuts.

---

## 5. iMovie to Final Cut Pro Interoperability

- **Rough-Cut Sequencing**: iMovie projects must be structured as linear storyboards with clearly defined A-roll clips, B-roll cutaways, and title cards.
- **Conform Ready**: Avoid obscure consumer transitions or stylized filters that fail to transfer cleanly when executing "Send to Final Cut Pro" or FCPXML export.
