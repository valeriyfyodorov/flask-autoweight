# flask-autoweight

An unattended self-service weighing kiosk for a cargo terminal.

A truck driver drives onto one of two weighbridges (`north` or `south`), operates a touchscreen
terminal next to the scales, and drives off a minute later with a printed weighing receipt. No
weighbridge operator is involved at any point. The whole thing is a small Flask application running
on a Raspberry Pi, displayed full-screen in a kiosk browser.

## How a driver uses it

The terminal always starts on the language screen — Latvian, Russian, English, Estonian, Lithuanian
and Polish are offered. After picking a language the driver chooses a direction: incoming or
outgoing. If the driver walks away, the screen resets itself to the language selection after 60
seconds of inactivity, so the next arrival always finds a clean start.

Both journeys begin by weighing. The app reads both weighbridges at once; if a truck is standing on
only one of them, that scale is chosen automatically, and if both are occupied the driver is shown
the two recognised plate numbers and taps their own.

**Incoming (delivery).** The driver holds the invoice or CMR under the scanner box and the terminal
photographs it. Then they pick their client from today's delivery lists, pick the farm or shipper
the cargo came from — there are a couple of hundred of them, so the page offers a row of A-Z
buttons and shows only the farms starting with the letter tapped, with a "Cits..Другой..Other"
button for the ones not on the list — confirm the licence plates that the cameras read (correcting them if the
recognition was wrong), and enter the invoice number and declared weight. The terminal registers the
truck in the central system and prints driving instructions with a QR code and a map of where to
unload. The traffic lights in front of the scales turn green.

**Incoming empty (coming to load at the port).** A truck that weighs 10–30 t on arrival is taken as
empty: it has no invoice of its own yet, so the terminal skips the invoice photo and the invoice
number/weight page. After the plates it registers the truck by itself, with the number
`<list id>-MMDDHHmm` (e.g. `3797-09302031`) and a declared weight of 24 999 kg; the real weight comes
from the two weighings. If the system already knows the truck — for example the office registered
it first — the terminal shows "Registration refused … probably already registered" in English,
Latvian and Russian together, so the staff can read it whatever language the driver chose.

**Outgoing (departure).** The driver holds the QR code from those instructions under the camera. The
terminal recognises the transport unit, records the final weight, cross-checks the plates against
what the database has on file, and prints the receipt — either a goods-acceptance receipt or a
release waybill, depending on whether the truck got heavier or lighter between the two weighings.
A truck that came in empty (10–30 t) and leaves heavier — cargo loaded at the port — also gets the
waybill "Kravas pavadzīme" in 3 copies right after the receipt.
The lights turn green and the driver leaves.

## How it works under the hood

- **Weight** comes from the weighbridge indicators over **Modbus TCP** — two holding registers,
  combined into a kilogram value. Before trusting a reading the app checks a GPIO sensor to make sure
  the automatic sampler arm has returned home; if it hasn't, it waits and re-reads.
- **Licence plates** are grabbed as still frames from four **RTSP** cameras (front and rear at each
  scale), de-skewed and cropped with OpenCV, then sent to an **ALPR** service on the local network.
- **Invoice and QR scanning** use the **Raspberry Pi camera** inside the scanner box, with a lamp
  switched on and off over GPIO for the duration of the shot.
- **Traffic lights** are switched by publishing MQTT messages through a **Home Assistant** REST API.
- **All business data** — clients, cargoes, factories, transport units, weighings — lives in an
  external ASP.NET JSON API (`notscr.amgs.me`). This application stores almost nothing of its own;
  the only thing it writes to disk is archived photographs of plates, invoices and cargo, filed by
  date under `/var/www/html/`.
- **Printing** happens straight from the kiosk browser, which is launched with printing dialogs
  suppressed so the receipt comes out without anyone touching a mouse.

## Running it locally (macOS)

```bash
uv sync
./start.sh          # sets FLASK_APP=start and runs the Flask dev server
```

Then open <http://localhost:5000>.

Before that will get anywhere you need to set `MAC_OS = True` at the top of
`start/intranet/config.py`, which swaps the Raspberry Pi GPIO library for a no-op stub. That one flag
is not sufficient on its own, though — the dummy-data switches next to it are independent, and you
will want them too:

```python
MAC_OS = True
DEBUG_WITH_DUMMY_SCALES = True   # fake weights instead of Modbus
DEBUG_WITH_DUMMY_PLATES = True   # fake plate images instead of RTSP
DEBUG_WITH_DUMMY_QR = True       # required, or the outgoing flow crashes on PiCamera
```

`DEBUG_WITH_DUMMY_QR` in particular is not optional: invoice capture honours `MAC_OS` and falls back
to a dummy JPEG, but QR capture does not, and without that flag the departure page fails outright.
The dummy images themselves are read from the path in `MAC_TEST_LOCATION`, which you will need to
point at a folder of your own.

Be realistic about what a laptop can do here: the weighbridges, the RTSP cameras, the scanner-box
camera, the ALPR service, the traffic lights and the printer are all on the terminal's private
network and none of them are reachable. You can exercise the page flow and the templates; you cannot
exercise a real weighing. There are also dependency mismatches that currently stop a clean local
import — they are listed under "Known gaps" in [AGENTS.md](AGENTS.md).

## Running in production (Raspberry Pi)

Production runs on the Pi's system Python, with `MAC_OS = False`. What is really installed there
(checked 2026-09-30) is Python 3.7.3, Flask 1.0.2 and Werkzeug 0.14.1 — older than the pins in
`requirements.txt`. `pyproject.toml` and `uv.lock` describe the newer local development setup and are
not what the Pi uses.

The shell scripts in the repository root:

| Script | What it does |
| --- | --- |
| `start.sh` | Sets `FLASK_APP=start`, disables the Werkzeug debug PIN, runs `flask run` and copies its output into `logs/` |
| `production_start.sh` | Activates the virtualenv and serves on `0.0.0.0:3000` |
| `startup.sh` | Boot script: opens a terminal running `start.sh`, a ping window, then Firefox in kiosk mode |
| `multistart.sh` | Same idea, backgrounds Flask and launches Chromium |
| `chromium.sh` | Full-screen Chromium with error dialogs, infobars and translation prompts off, and `--kiosk-printing` |

### Updating files on the kiosk over SSH

| | |
| --- | --- |
| Production Pi | `pi@192.168.100.2` (SSH) |
| App folder | `/home/pi/Desktop/flask` (same layout as this repository) |

The Pi is not updated with git (its `.git` folder is a stale 2023 leftover): changed files are
copied over one by one. Before overwriting, keep the old version next to it as
`<file>.<MMDDHHmm>.bak`, so a bad update is undone with one `cp`. (The first update of 2026-09-30
used `<file>.bak.2609301540` — those files are still there.)
Run the commands from the repository root on the Mac; replace the stamp and the file list.

```sh
# 1. back up the files about to change (on the Pi, -p keeps the original date)
ssh pi@192.168.100.2 'cd /home/pi/Desktop/flask && for f in \
    start/routes/disch_in.py start/routes/printing.py; do
    cp -p "$f" "$f.09302035.bak"; done'

# 2. copy the new versions - one scp per target folder
scp start/routes/disch_in.py start/routes/printing.py \
    pi@192.168.100.2:/home/pi/Desktop/flask/start/routes/

# 3. check what landed
ssh pi@192.168.100.2 'ls -l /home/pi/Desktop/flask/start/routes/ | grep disch_in'

# undo: put a backup back
ssh pi@192.168.100.2 'cd /home/pi/Desktop/flask && cp -p \
    start/routes/disch_in.py.09302035.bak start/routes/disch_in.py'
```

- **Never scp `start/intranet/config.py`.** The Pi's copy has its own values (`MAC_OS = False`,
  hardware settings). Back it up the same way, then add new lines by hand:
  `ssh -t pi@192.168.100.2 nano /home/pi/Desktop/flask/start/intranet/config.py`.
- `start.sh` runs Flask with `FLASK_ENV=development`, so the reloader picks up changed `.py` files
  and templates without a restart. A file that fails to import stops the app instead — if the
  kiosk shows a connection error after an update, restore the backup and reboot the Pi.
  (Confirmed on 2026-09-30: `disch_in.py` was recompiled 3 seconds after it was copied.)
  Shell scripts such as `start.sh` itself are not watched — they take effect at the next reboot.

### Reading the Flask log on the kiosk

`start.sh` writes everything Flask prints into `/home/pi/Desktop/flask/logs/flask_YYMMDD_HHMM.log`,
one file per start of the app, and deletes files older than 30 days. The same lines still show in
the "Starting Flask" terminal window.

```sh
# the newest log, last 200 lines
ssh pi@192.168.100.2 'cd /home/pi/Desktop/flask/logs && tail -n 200 "$(ls -t flask_*.log | head -1)"'

# only the problems: error pages, Python tracebacks, server errors (500)
ssh pi@192.168.100.2 'cd /home/pi/Desktop/flask/logs && grep -n -A 20 -E "unknownerror|Traceback| 500 " "$(ls -t flask_*.log | head -1)"'

# download all logs to the Mac
scp -r pi@192.168.100.2:/home/pi/Desktop/flask/logs ~/Downloads/kiosk-logs
```

What the usual lines mean:

- `GET /unknownerror?...&error=...` — the driver got the error page; the reason is in `error=`
  (percent-encoded, e.g. `%20` is a space).
- `jsonDictFromUrl. ... zero length response received` followed by `registerNewUnit. API answer
  without id` — the API refused the registration, almost always because the truck is already
  registered (by the office, or by an earlier try at the kiosk). Look the plate up in the central
  system before suspecting the kiosk.
- `readRtspImage. Failed to capture image at rtsp://...` — one camera did not answer; the photo for
  the archive is missing, the registration itself carries on.

## Repository layout

```
main.py                     uv scaffolding stub — not the entry point
start/
  __init__.py               creates the Flask app; importing it wires up everything
  db.py                     sqlite helpers (largely unused)
  routes/
    top.py                  language, direction, weighing, farewell
    disch_in.py             incoming: invoice, lists, factories, plates, CMR
    disch_out.py            outgoing: QR scan
    printing.py             driving instructions, receipts, QR images
    helpers.py              query-string, API and traffic-light helpers
    settings.py             loads the translation vocabulary
  intranet/                 everything that talks to hardware or the outside world
    config.py               all configuration lives here
    defs.py                 weight reading, plate recognition, photo archiving
    vision.py               OpenCV, ALPR, QR decoding
    picam.py                Raspberry Pi camera and lamp
    GPIO.py                 no-op GPIO stub used when MAC_OS is on
  templates/                Jinja2 templates
  static/                   Bootstrap, jQuery and images, vendored so the kiosk needs no internet
  json/scales_lng.json      translations for all six languages
```

The repository also contains a fair number of dated backup snapshots alongside the live files —
things like `top.py1213`, `disch_in.py04`, `defs.py.bak` and the `templates/*_old` folders. They are
history, kept for reference, and nothing imports them.

## Configuration

Everything configurable sits in `start/intranet/config.py`: the definition of both scales with their
camera URLs, crop and de-skew geometry, Modbus hosts and ports, MQTT light topics and sampler GPIO
pins; the ALPR and Home Assistant endpoints; the central API URL; the GPIO pin numbers for the buzzer
and lamp; and a set of `DEBUG_WITH_DUMMY_*` switches that feed canned values in place of real
hardware.

---

Contributors and AI agents working on this code should read [AGENTS.md](AGENTS.md) first.
