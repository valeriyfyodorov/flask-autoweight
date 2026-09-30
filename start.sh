export FLASK_APP=start
export FLASK_ENV=development
export WERKZEUG_DEBUG_PIN=off
# Python holds back print() output in blocks when it goes into a pipe (see tee below),
# which would delay both the terminal and the log - this makes every line go out at once
export PYTHONUNBUFFERED=1

# Everything Flask prints - progress lines, every request (the error page url carries its
# error text), Python tracebacks - still shows in this terminal AND goes into a log file,
# one file per start: logs/flask_YYMMDD_HHMM.log. Logs older than 30 days are deleted.
mkdir -p logs
find logs -name "flask_*.log" -mtime +30 -delete
flask run 2>&1 | tee -a "logs/flask_$(date +%y%m%d_%H%M).log"
