
source /home/alpr/.virtualenvs/flask/bin/activate
cd /home/alpr/projects/flask
export FLASK_APP=start
export FLASK_ENV=development
export WERKZEUG_DEBUG_PIN=off
flask run -h 0.0.0.0 -p 3000
