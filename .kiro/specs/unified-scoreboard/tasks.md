# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Marcador Aislado Por Dispositivo
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate that two independent localStorage instances return different data
  - **Scoped PBT Approach**: Scope the property to the concrete failing case — deviceA inserts an entry, deviceB reads getAll() and must see it
  - Create two mock localStorage instances (deviceA, deviceB) each with their own isolated storage
  - Instantiate LeaderboardManager twice, one per mock storage
  - Insert `{ mote: 'AAA', score: 100, date: '2025-01-01' }` via deviceA's manager
  - Assert that deviceB's manager.getAll() returns an array containing the entry with mote='AAA' and score=100
  - Run test on UNFIXED code (localStorage-based LeaderboardManager)
  - **EXPECTED OUTCOME**: Test FAILS — deviceB.getAll() returns [] instead of the inserted entry (proves localStorage isolation bug)
  - Document counterexample: "deviceB.getAll() returns [] when deviceA has [{ mote: 'AAA', score: 100 }]"
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Comportamiento Existente Del Leaderboard
  - **IMPORTANT**: Follow observation-first methodology
  - Observe on UNFIXED code (single-device, localStorage): qualifies(score) returns true when fewer than 10 entries exist; insert() keeps entries sorted DESC and capped at 10; clear('!Talentland') empties the board; clear('wrong') returns false and leaves data intact; getAll() with no entries returns []
  - Write property-based tests using fast-check or equivalent:
    - For any list of N entries (N > 10) inserted in random order, getAll() returns exactly 10 entries sorted DESC by score (from Preservation Requirements in design)
    - For any score S, qualifies(S) returns true iff getAll().length < 10 OR S > min(getAll().scores)
    - clear('!Talentland') always empties the board; clear(any_other_string) always returns false and leaves data unchanged
    - For any action that is not insert/clear, the leaderboard state does not change
  - Verify all tests PASS on UNFIXED code (single-device localStorage baseline)
  - **EXPECTED OUTCOME**: Tests PASS — confirms baseline behavior to preserve
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Fix: Unified Scoreboard via server.py + fetch API

  - [x] 3.1 Create server.py — Python HTTP server with REST scores API
    - Extend `http.server.SimpleHTTPRequestHandler` to intercept `/api/scores` routes
    - `GET /api/scores`: read `scores.json` from disk, return `[]` if file does not exist; respond `200 application/json`
    - `POST /api/scores`: parse JSON body (full entries array), write to `scores.json`; respond `200 application/json { ok: true }`
    - `DELETE /api/scores`: write `scores.json` with `[]`; respond `200 application/json { ok: true }`
    - `OPTIONS /api/scores`: respond `200` (CORS preflight)
    - All other paths: delegate to `SimpleHTTPRequestHandler.do_GET` (static file serving)
    - Add `Access-Control-Allow-Origin: *` header to all API responses
    - Server listens on port 8080 and prints local IP + URL on startup
    - _Bug_Condition: isBugCondition(deviceA, deviceB) where each device reads its own localStorage_
    - _Expected_Behavior: all devices read/write the same scores.json via HTTP_
    - _Preservation: static file serving for index.html and assets must remain unchanged_
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.5_

  - [x] 3.2 Modify LeaderboardManager in index.html — replace localStorage with fetch
    - Replace `_load()` with `_loadAsync()`: `fetch('/api/scores')` returning parsed JSON, fallback to `[]` on network error
    - Replace `_save(entries)` with `_saveAsync(entries)`: `fetch('/api/scores', { method: 'POST', body: JSON.stringify(entries), headers: { 'Content-Type': 'application/json' } })`, fail silently on error
    - Make `getAll()` async: returns `Promise<Entry[]>` via `_loadAsync()`
    - Make `qualifies(score)` async: returns `Promise<boolean>`
    - Make `insert(entry)` async: loads, inserts, sorts DESC, caps at 10, saves, returns `Promise<number>` (1-based rank)
    - Make `clear(password)` async: validates password client-side, calls `fetch('/api/scores', { method: 'DELETE' })`, returns `Promise<boolean>`
    - Make `getRank(score)` async: returns `Promise<number|null>`
    - Update `renderMenuScoreboard()` to call `LeaderboardManager.getAll().then(entries => ...)` instead of reading localStorage directly
    - Update all call sites to use `await` or `.then()`: renderLeaderboard, qualifies check in results screen, insert after mote entry, clear in admin panel, getRank in results
    - _Bug_Condition: isBugCondition where localStorage is device-local_
    - _Expected_Behavior: all reads/writes go through /api/scores, same data on all devices_
    - _Preservation: qualifies logic, top-10 cap, sort order, mote modal flow, results screen, clear with password — all unchanged_
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 3.3 Update start.bat, start.sh, restart-server.bat to use server.py
    - `start.bat`: replace `python -m http.server %PORT%` (and py/python3 fallbacks) with `python server.py` / `py server.py` / `python3 server.py`
    - `start.sh`: replace `xdg-open "$FILE"` / `open "$FILE"` static-open approach with launching `python3 server.py` (or `python server.py`) in background, then opening `http://localhost:8080/index.html` in browser
    - `restart-server.bat`: ensure it kills port 8080 process and relaunches via updated `start.bat` (no change needed if start.bat is updated correctly)
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.4 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Marcador Compartido Entre Dispositivos
    - **IMPORTANT**: Re-run the SAME test from task 1 — do NOT write a new test
    - The test from task 1 now targets the fetch-based LeaderboardManager backed by server.py
    - When this test passes, it confirms that deviceB.getAll() returns the entry inserted by deviceA
    - Run bug condition exploration test from step 1 against the fixed implementation
    - **EXPECTED OUTCOME**: Test PASSES — confirms shared scoreboard bug is fixed
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.5 Verify preservation tests still pass
    - **Property 2: Preservation** - Comportamiento Sin Cambios Para Flujos Existentes
    - **IMPORTANT**: Re-run the SAME tests from task 2 — do NOT write new tests
    - Run preservation property tests from step 2 against the fixed implementation (using a mock server or test instance of server.py)
    - **EXPECTED OUTCOME**: Tests PASS — confirms no regressions in qualifies, insert ordering, clear, fallback behavior
    - Confirm all tests still pass after fix (no regressions)

- [x] 4. Checkpoint — Ensure all tests pass
  - Run the full test suite (exploration test + preservation property tests + any unit/integration tests written during implementation)
  - Verify `GET /api/scores` returns `[]` when scores.json does not exist
  - Verify `POST /api/scores` writes correctly and subsequent `GET` returns the same data
  - Verify `DELETE /api/scores` empties the board
  - Verify end-to-end: start server.py, insert score from client A (fetch), read from client B (fetch) → same result
  - Verify fallback: stop server, call LeaderboardManager.getAll() → returns [] without visible error
  - Ensure all tests pass; ask the user if questions arise
