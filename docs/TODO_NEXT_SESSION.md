# TODO — Next Session

**Date written:** 2026-02-09 (late night)
**Current version:** v1.3.2
**Context:** User tested v1.3.2 installed build and found 3 bugs.

---

## Bug 1: Preview rendering broken (HIGH PRIORITY)

The Kapitel-Vorschau now shows an error. This is a **regression introduced in v1.3.2** by the regex added to fix lenient bold/italic markers.

**What was added (v1.3.2):**
```python
# In pdf_generator.py, markdown_to_html() and generate_memoir_preview_html()
import re
markdown_content = re.sub(r'(\*{1,2})(\S(?:.*?\S)?)\s+(\1)', r'\1\2\3', markdown_content)
```

**What to do:**
1. Reproduce the error: start app with `py app.py --browser --debug`, open Kapitel-Vorschau
2. Check Flask console for the Python traceback
3. Test the regex with the problematic content:
   ```
   this is a text. I might **make ** this bold or even *underline *it though i *don't *know how to do that in markdown-
   ```
4. The regex likely chokes on unmatched/overlapping markers. Consider a simpler approach:
   - Just strip spaces before `**` and `*` closers: `re.sub(r'\s+(\*{1,2})(\s|$)', r'\1\2', text)`
   - Or: only fix cases where there's a matching opener
5. Fix is needed in TWO places in pdf_generator.py (line ~121 and ~525)
6. Run tests: `py -m pytest tests/test_pdf_generator.py -v`

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

## After fixing bugs

1. Run full test suite: `py -m pytest tests/ -q --ignore=tests/test_updater.py -k "not test_get_prompts"`
2. Bump version to v1.3.3
3. Commit, tag, push
4. Test installed build again with the test plan below

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
