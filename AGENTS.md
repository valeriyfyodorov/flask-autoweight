# AGENTS.md

Operational rules for AI agents working in this repository. Read this before editing anything.
For domain background (what the kiosk does, how a driver uses it) see [README.md](README.md) — this
file does not repeat it.

## What this is

Self-service truck-weighing kiosk at a cargo terminal. Flask app on a Raspberry Pi, driven from a
full-screen kiosk browser. It reads weight over Modbus TCP, reads licence plates from RTSP cameras
via an ALPR service, scans invoices/QR codes with the Pi camera, calls an external ASP.NET JSON API
(`notscr.amgs.me/apijson.ashx`) for all business data, switches traffic lights through a Home
Assistant MQTT endpoint, and prints a weighing receipt.

## Entry point and layout

- **`start/__init__.py` is the entry point.** It creates a module-level `app = Flask(__name__)` —
  there is no application factory (the `create_app` version is commented out and dead). Importing
  `start` has side effects: it configures GPIO and imports every route module.
- **`main.py` is a `uv init` stub.** It prints a hello message and is not wired to anything. Never
  treat it as the entry point.
- **`start/routes/`**
  - `top.py` — `/`, `/direction`, `/scales`, `/directions`, `/unknownerror`, `/farewell`
  - `disch_in.py` — incoming: `/invoice`, `/lists`, `/factories`, `/plates`, `/cmr`
  - `disch_out.py` — outgoing: `/qrcode`
  - `printing.py` — `/qrinstructions`, `/qrimg`, `/printout`, `/waitprint`
  - `helpers.py` — shared utilities (query strings, API calls, traffic lights, image serving)
  - `settings.py` — loads the `vocabulary` translation dict
  - `routes/__init__.py` does `from .x import *`. **A new route module must be added there** or its
    routes are never registered.
- **`start/intranet/`** — hardware and external I/O
  - `config.py` — every constant in the project
  - `defs.py` — weight reading, plate recognition, photo archiving
  - `vision.py` — OpenCV, ALPR HTTP, QR decoding
  - `picam.py` — Pi camera + GPIO lamp
  - `utils.py` — `Timer`, `archiveFileName`, `dictFromArgs`
  - `GPIO.py` — no-op stub standing in for `RPi.GPIO` when `MAC_OS` is on
  - `startup.py` — GPIO buzzer/lamp init, imported for its side effects
- **`start/templates/`** — Jinja2, all extending `base.html` (Bootstrap 4, jQuery, Popper, Pace,
  idle-timer, all vendored under `start/static/` so the kiosk needs no internet).
- **`start/json/scales_lng.json`** — translations. Six languages (`en ru lv lt pl ee`), each with a
  key per page. Loaded with `utf-8-sig` in `routes/settings.py`, so a UTF-8 BOM would be tolerated;
  the file does not currently have one. Keep the `utf-8-sig` read, and don't add a BOM.

## Request flow and state

**Nearly all state between pages lives in the query string.** There is no Flask session and no
per-request server-side store. Keys in circulation: `lng` (language), `dir` (direction), `sc` (scale
id, `1`=south `2`=north), `ptf`/`ptr` (front/rear plate), `wkg` (weight in kg), `tranunit`
(transport unit id), `list`, `fr`, `ifn`, `inr`/`iwt` (invoice nr / weight), `local`.

Use `helpers.queryfromArgs(request.args, excludeKeysList=[...])` to rebuild the query string. Do not
hand-assemble one.

**The exception: the captured invoice image travels out of band**, through the single fixed path
`TEMP_INVOICE_IMG_FILE` (`config.py`, `/var/www/html/invoice.jpg`). `/lists` calls
`defs.readInvoice()` → `picam.captureInvoiceToFile()`, which writes that path; `/cmr` later calls
`defs.archiveInvoice()`, which copies from it. Nothing correlates the two beyond the filename.
Consequences an agent must respect:

- **Two drivers using the two scales at once will clobber each other's invoice image.** The kiosk is
  single-user in practice, which is why this has never bitten, but any change that widens concurrency
  (threaded server, second terminal, background task) must fix this first.
- The `ifn` query key looks like it carries the invoice filename, but it is written at
  `disch_in.py:31` and **read nowhere**. Do not build on it without wiring it up properly.
- `TEMP_PLATE_IMG_FILE_FRONT` / `_REAR` are shared the same way in `defs.archivePlates`.

- Incoming: `/` → `/direction` → `/scales` → `/invoice` → `/lists` → `/factories` → `/plates` →
  `/cmr` (POST registers the unit via API) → `/directions` → `/qrinstructions`
- Outgoing: `/` → `/direction` → `/scales` → `/qrcode` → `/farewell` (reads QR, posts final weight)
  → `/printout` → `/waitprint` → `/`
- `templates/idle_script.html` bounces the browser back to `/` after 60 s idle.

## Conventions — match them, do not "fix" them

- **camelCase** for functions, locals and helpers (`getWeightKg`, `queryfromArgs`, `readRtspImage`).
  This is not PEP 8 and that is intentional. New code follows the surrounding style.
- **Progress tracing is bare `print`**, always with a timestamp:
  `print(f"entering invoice def {time.strftime('%H:%M:%S')}")`. There is no `logging` setup; do not
  introduce one unasked.
- **External calls partly swallow errors — do not over-trust this.** `helpers.jsonDictFromUrl`
  returns a sentinel `{"result": 100, "error": "unknown error"}` when it fails *quietly*, and callers
  check the shape of the result. But it only has `except timeout` (`socket.timeout`). These still
  propagate out of it and will 500 the request:
  - `urllib.error.HTTPError` on any non-200 — which also means the `getcode() != 200` branch inside
    it is effectively dead code, since `urlopen` raises before reaching it
  - `urllib.error.URLError` on DNS failure or a refused connection
  - `json.JSONDecodeError` on a malformed body

  So when adding a call, still handle failure at the call site; do not assume the helper is a
  complete safety net. `printing.py:printout` already wraps its calls in a retry loop for this
  reason. Note it catches `socket.error`, which does not cover the JSON or HTTP cases above.
- **Errors surface as redirects**, not exceptions: `redirect(url_for('unknownerror') + f"?error=…")`.
- Templates are the only place formatting lives; route functions build a `content` dict and hand it
  over.

## Two environments

| | Production (authoritative) | Local development |
| --- | --- | --- |
| Host | Raspberry Pi | macOS laptop |
| Python | Pi system Python | `uv`, Python ≥3.13 |
| Deps | `requirements.txt` (2020 pins, Flask 1.1.2) | `pyproject.toml` + `uv.lock` (Flask 3.1) |
| `MAC_OS` | `False` | `True` |
| GPIO/camera | real `RPi.GPIO`, `picamera` | stub `GPIO.py`, dummy JPEGs |
| Started by | `production_start.sh`, `startup.sh`, `multistart.sh`, `chromium.sh` | `./start.sh` |

The owner develops on the Mac and has **no access** to the Pi's GPIO pins, cameras, Modbus scales,
ALPR service, traffic lights or printer. Only part of the app can be exercised locally. Any change
touching hardware paths is verified by reading, not by running.

**Never commit `MAC_OS = True`.** Flipping it locally is expected; leaving it flipped in a commit
would stub out all hardware in production.

## Known gaps — state as facts, do not fix unasked

- `pyproject.toml` declares `zxing-cpp`, but `start/intranet/vision.py` imports `zbarlight`. A local
  `uv` run fails at import until one side is reconciled.
- `picamera` is not in `pyproject.toml` at all (it is Pi-only, so this is expected but means
  `picam.py` cannot be imported locally with `MAC_OS = False`).
- `config.py` ships with `MAC_OS = False`, so importing `start` on the Mac fails on
  `import RPi.GPIO`.
- **`MAC_OS = True` alone is not enough to run the outgoing flow locally.**
  `picam.captureInvoiceToFile()` branches on `MAC_OS` and falls back to dummy JPEGs, but
  `picam.camToPilImg()` does **not** — it branches only on `DEBUG_WITH_DUMMY_QR`. With that flag
  `False` on a Mac, `PiCamera` was never imported and the call dies with `NameError`. `/farewell`
  is unreachable locally unless `DEBUG_WITH_DUMMY_QR = True` is also set.
- Likewise `DEBUG_WITH_DUMMY_SCALES` (fakes 44000/9000 kg) and `DEBUG_WITH_DUMMY_PLATES` are
  separate switches from `MAC_OS`; all default to `False`. **`DEBUG_WITH_DUMMY_INVOICE` is defined
  but read nowhere** — it looks symmetric with the other three and is not. Invoice capture keys off
  `MAC_OS` instead.
- `MAC_TEST_LOCATION` (the dummy-image folder used when `MAC_OS` is on) points at
  `/Users/Valera/Documents/venprojs/pi/latest/html/`, a stale path from an older checkout. Anyone
  running locally has to repoint it.
- `requirements.txt` and `pyproject.toml` describe different stacks **by design**, not by mistake.
  Do not try to unify them.
- There is no automated test suite and no test framework configured.

## Files to ignore — never edit, never copy patterns from

Dated snapshots and backups left in place as history. Nothing imports them; they contain stale
config and broken code. Do not read them for guidance, do not update them alongside live files, and
do not delete them (the owner wants them kept).

- Any source file whose extension is a date or number: `*.py04`, `*.py26`, `*.py0408`, `*.py0708`,
  `*.py0804`, `*.py1008`, `*.py1213`, `*.py1711`, `*.py2710`
- `*.bak` — e.g. `start/routes/top.py.bak`, `start/intranet/defs.py.bak`, and note
  `start/templates/disch_in/factories.html.bak`, which sits *inside* the live template folder
- `start/intranet/defsbroken.py`
- `start/templates/old/`, `start/templates/disch_in_old/`, `start/templates/*_old`,
  `start/templates/*_old1`, `start/templates/scales.html0804`
- `start/json/scales_lng.json_old`, `start/json/smple.txt`

Also **not** a test suite: `start/intranet/tests.py` and `start/intranet/ltests.py` are standalone
hardware-poking scripts with their own copy-pasted, outdated `SCALES` dict. Never import from them
and never treat their config as current — `config.py` is the only source of truth.

## Configuration

`start/intranet/config.py` holds LAN IP addresses, RTSP camera URLs, Modbus hosts/ports, the ALPR
token, a Home Assistant bearer token and the API key in `SERVER_API_URL`. These are private-network
values that the owner has confirmed are **not sensitive** — do not flag them as a security finding
and do not propose moving them to environment variables unasked. Keep new constants in `config.py`
rather than scattering them across modules.

## Working agreements

- **Ask before changing hardware I/O behaviour**: Modbus register offsets and scaling, GPIO pin
  numbers, the sampler-homing wait in `defs.delayedForSamplerCheck`, camera crop/warp geometry. A
  wrong value here mis-weighs a truck or blocks the scales.
- No tests exist, so verify by careful reading plus, where possible, a local partial run. Say plainly
  what you could not verify.
- Do not modernise, reformat or lint files you were not asked to change. Legacy style is deliberate.
- Weights from the API are in tonnes and multiplied by 1000 for display; weights from Modbus are
  already kilograms. Check which one you are holding before doing arithmetic.
