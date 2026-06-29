# Anki UI Verification Notes

AnkiLens is symlinked into Anki for live testing:

```sh
ls -l "$HOME/Library/Application Support/Anki2/addons21/ankilens"
```

Expected target:

```text
/Users/arvgan/Documents/Projects/anki-missed-card-analytics/addon
```

## Current Visual QA Path

Use Computer Use app-state capture for visual checks:

```json
{"app": "Anki"}
```

This can read Anki's accessibility tree and return a screenshot of the active
Anki window. On June 27, 2026, this successfully captured the deck browser and
AnkiLens deck panel.

Terminal `screencapture` is not reliable in this Codex desktop environment. It
can return only the Codex desktop wallpaper/menu bar even while Computer Use can
see the Anki window. Do not use shell screenshots as the primary proof of Anki
visual state.

Still confirm the process with:

```sh
pgrep -fl Anki
```

## Lower-Level Capture Failure Notes

CoreGraphics can list an Anki window even when Computer Use cannot attach:

```sh
swift - <<'SWIFT'
import CoreGraphics
let opts = CGWindowListOption(arrayLiteral: .optionOnScreenOnly)
if let windows = CGWindowListCopyWindowInfo(opts, kCGNullWindowID) as? [[String: Any]] {
  for window in windows {
    let owner = window[kCGWindowOwnerName as String] as? String ?? ""
    if owner.contains("Anki") {
      print(window)
    }
  }
}
SWIFT
```

If the listed Anki window includes:

```text
"kCGWindowSharingState": 0
```

then macOS is reporting an on-screen window but refusing image capture for that
window. In that state, this command can fail:

```sh
screencapture -x -l <window-id> tmp/anki-window.png
```

Observed failure:

```text
could not create image from window
```

If `screencapture` shows only the desktop wallpaper, Anki is likely on another
Space/display or otherwise not visible to the active capture session. Do not
claim visual verification in that state.

AppleScript accessibility inspection may also be blocked by local automation
permissions:

```text
Not authorized to send Apple events to System Events. (-1743)
```

On June 27, 2026, both `python3` and `/usr/bin/python3` also failed to import
`Quartz` in this shell, and a full-screen `screencapture` showed only the
desktop wallpaper while Anki was running. Treat shell capture as
process/symlink verification only, not visual UI verification.

## Acceptable Evidence When Visual Capture Fails

For UI slices, record:

- `make test`
- `git diff --check`
- Anki process status
- Add-on symlink target
- Computer Use app-state screenshot/accessibility tree, when available
- CoreGraphics window metadata, including `kCGWindowSharingState` when present
- The exact capture failure if Computer Use is unavailable

This is weaker than actual visual verification. Use it only when the app window
cannot be captured, and state the gap clearly in the final note.
