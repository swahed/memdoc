# TODO — Next Session

**Date written:** 2026-02-15
**Current version:** v1.3.4
**Context:** v1.3.4 fixed the preview regression. Two bugs remain.

---

## ~~Bug 1: Preview rendering broken~~ — FIXED in v1.3.4

Replaced catastrophic-backtracking regex with simpler `re.sub(r'\s+(\*{1,2})(?=\s|$|[.,;:!?\)])', r'\1', ...)`.
Fixed in both `markdown_to_html()` and `generate_memoir_preview_html()`. Added None guard and 7 unit tests.

---

## Bug 2: Single-instance check not working (MEDIUM)

Launching MemDoc.exe when already running opens the browser (good) but does NOT prevent a second server from starting (bad).

**Current implementation** (app.py `main()`):
```python
def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True
```

**Why it might not work:**
- The socket is immediately released after the check (race condition)
- `localhost` vs `127.0.0.1` binding mismatch
- Flask might not have bound the port yet when the second instance checks
- Windows firewall could interfere

**Better approaches to try:**
1. **File lock** — create `~/.memdoc/memdoc.lock`, check on startup, clean up on exit
2. **Windows named mutex** — `ctypes.windll.kernel32.CreateMutexW(None, False, "MemDocSingleInstance")`
3. **Connect instead of bind** — try `socket.connect(('localhost', port))` instead of bind. If connect succeeds, the server is running.

**Test:** Run `py app.py --browser`, then run `py app.py --browser` again in another terminal. Second should detect the first and exit.

---

## Bug 3: PowerShell window visible during folder pick (LOW)

Clicking "Durchsuchen" opens a visible empty PowerShell window alongside the folder dialog.

**Current code** (app.py, folder picker route):
```python
result = subprocess.run(
    ['powershell', '-NoProfile', '-Command', ps_script],
    capture_output=True, text=True, timeout=300
)
```

**Fix options (try in order):**
1. Add `creationflags=subprocess.CREATE_NO_WINDOW` to the `subprocess.run()` call
2. If that doesn't work, use `subprocess.STARTUPINFO`:
   ```python
   startupinfo = subprocess.STARTUPINFO()
   startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
   startupinfo.wShowWindow = 0  # SW_HIDE
   result = subprocess.run(..., startupinfo=startupinfo)
   ```

---

## Additional: Add taskkill to installer install step

The installer's `[UninstallRun]` kills MemDoc.exe before uninstall, but the `[Run]` (install) section does not.
When upgrading, running MemDoc instances can block the installer from replacing the exe.
Add a `[Code]` section or pre-install `[InstallRun]` with `taskkill /IM MemDoc.exe /F`.

---

## After fixing bugs

1. Run full test suite: `py -m pytest tests/ -q --ignore=tests/test_updater.py -k "not test_get_prompts"`
2. Bump version, commit, tag, push (CI builds installer automatically)
3. Test installed build again with the test plan below

---

## Test plan for v1.3.x

### Preview & rendering
- [ ] Open Kapitel-Vorschau — no error, content renders
- [ ] Bold text (`**word**`) renders as **bold**
- [ ] Italic text (`*word*`) renders as *italic*
- [ ] `**word **` (with trailing space) still renders as bold (server-side fix)
- [ ] Images with `{: .img-center .img-medium}` display correctly
- [ ] Drucken button triggers browser print dialog

### Editor toolbar
- [ ] Double-click word, press Bold → `**word** ` (space outside markers)
- [ ] Double-click word, press Italic → `*word* ` (space outside markers)
- [ ] Ctrl+B and Ctrl+I same behavior
- [ ] Manual selection (no trailing space) → markers tight: `**word**`

### Single instance
- [ ] Start MemDoc → app opens in browser
- [ ] Start MemDoc again → opens browser to existing instance, second process exits
- [ ] No two Flask servers running simultaneously

### Folder picker
- [ ] Settings → Durchsuchen → folder dialog opens
- [ ] No visible PowerShell/console window
- [ ] Selecting a folder works, canceling works

### Regression checks (from v1.3.0/v1.3.1)
- [ ] First-run onboarding appears when config is missing
- [ ] Corrupt memoir.json → recovery banner with backup path
- [ ] New chapter → no prompts, cursor in title field
- [ ] All UI text in German (no English strings)
- [ ] Markdown-Hilfe link works
