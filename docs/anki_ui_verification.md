# Anki UI Verification Notes

Bonsai is symlinked into Anki for live testing:

```sh
ls -l "$HOME/Library/Application Support/Anki2/addons21/bonsai"
```

Expected target:

```text
/Users/arvgan/Documents/Projects/anki-missed-card-analytics/addon
```

## Current Automation Limitation

Computer Use currently sees Anki in the app registry, but cannot attach to its
key window:

```text
Computer Use server error -10005: cgWindowNotFound
```

This does not mean Anki is stopped. Confirm the process with:

```sh
pgrep -fl Anki
```

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

## Acceptable Evidence When Visual Capture Fails

For UI slices, record:

- `make test`
- `git diff --check`
- Anki process status
- Add-on symlink target
- CoreGraphics window metadata, including `kCGWindowSharingState` when present
- The exact Computer Use or capture failure

This is weaker than actual visual verification. Use it only when the app window
cannot be captured, and state the gap clearly in the final note.
