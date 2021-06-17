from flask import Flask  # 1.0.2
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
import os
import datetime
import main
from resume import summarize
from hashlib import sha256
from colorama import init  # 0.4.1
from colorama import Fore
from threading import Timer
from du_texte_aux_questions import Document
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf import Form, RecaptchaField
from wtforms import TextAreaField, StringField, HiddenField, ValidationError, RadioField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from repondre_aux_questions import reponse_finale
import re
import gevent.monkey
from gevent.pywsgi import WSGIServer

gevent.monkey.patch_all()


# create flask app
def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)
    Bootstrap(app)

    app.config['SECRET_KEY'] = 'ffedg0890489574'

    @app.after_request
    def after_request(response):
        """
        Enables CORS to allow AJAX requests from the webpage
        """

        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response

    @app.route("/default", methods=["GET"])
    def default():
        """
        Default landing page
        Allows users to input their text to be processed
        """

        log("Received request for default page")
        return render_template("default.html")

    @app.route('/', methods=('GET', 'POST'))
    def index():
        if request.method == 'POST':
            try:
                question = request.form['question']
            except Exception as e:
                print("key error")
                print("I got a KeyError - reason %s") % str(e)
            except Exception as e:
                print("I got another exception, but I should re-raise")
                raise

            print(question)
            answer = reponse_finale(question)
            print("answer: "), answer
            answer = re.sub('([(].*?[)])', "", answer)

            return render_template('answer.html', answer=answer, question=question)

        form = ExampleForm()
        return render_template('index.html', form=form)

    @app.route('/resume', methods=('GET', 'POST'))
    def resume():
        if request.method == 'POST':
            try:
                text_initial = request.form['text']
            except Exception as e:
                print("key error")
                print("I got a KeyError - reason %s") % str(e)
            except Exception as e:
                print("I got another exception, but I should re-raise")
                raise

            # print(text)
            text_resume = summarize(text_initial)
            # print("resume: "), text_resume
            answer = re.sub('([(].*?[)])', "", text_resume)

            return render_template('resume.html', entrez_text=None, voir_resume="true", resume=answer, texte=text_initial, longueur_finale=len(text_resume), longueur_initiale=len(text_initial))

        form = ResumeForm()
        return render_template('resume.html', form=form,voit_resume=None, entrez_texte="true")

    @app.route('/questions_intelligentes', methods=('GET', 'POST'))
    def questions_intelligentes():
        if request.method == 'POST':
            try:
                texte = request.form['text']
            except Exception as e:
                print("key error")
                print("I got a KeyError - reason %s") % str(e)
            except Exception as e:
                print("I got another exception, but I should re-raise")
                raise


            questions_avec_interrogation = main.generer(texte)
            # answer = re.sub('([(].*?[)])', "", text_resume)

            return render_template('questions_intelligentes.html', entrez_text=None, voir_questions="true", questions=questions_avec_interrogation,
                                   texte=texte)

        form = ResumeForm()
        return render_template('questions_intelligentes.html', form=form, voit_questions=None, entrez_texte="true")

    @app.route("/generate", methods=["POST"])
    def generate():
        """
        Accepts raw text data and creates questions
        Saves data with session id
        """

        global data

        log("Received request to generate questions")

        session_id = get_hash()
        log("Created session id", session_id=session_id)

        # make questions
        raw_data = str(request.form.get("data"))
        questions_avec_blancs = Document(raw_data).format_questions()

        log("Created session id", session_id=session_id)

        # store data
        data[session_id] = {
            "questions": questions_avec_blancs
        }
        # timer to delete data
        # reset_timer(session_id)

        log("Redirecting to questions page to begin questions", session_id=session_id)
        return (redirect(url_for("questions", session_id=session_id)))

    @app.route("/questions", methods=["GET"])
    def questions():
        """
        Each request is requesting a new question
        Generates all past questions and current question to send back
        """

        global data

        session_id = request.args.get("session_id")

        log("Received request for new questions", session_id=session_id)

        if session_id in data:


            qu = data[session_id]["questions"]

            return render_template(
                "questions.html",
                session_id=session_id,
                Question=qu
            )
        else:
            # we dont have them at all (never made questions or it timed out and got deleted)
            log("No available questions (session id not found, timed out?), returning to home page")
            return redirect(url_for("default"))

    @app.route("/generate", methods=["GET"])
    def redirect_to_default():
        """
        Redirects users to main page if they make a GET request to /generate
        Generate should only be POSTed to
        """

        log("Received GET request for /generate, returning to default page")
        return redirect(url_for("default"))

    return app


# init colorama, reset coloring on each print
init(autoreset=True)


class ExampleForm(Form):
    question = StringField('', description='', validators=[DataRequired()], )
    submit_button = SubmitField('answer')


class ResumeForm(Form):
    text = TextAreaField('', description='', validators=[DataRequired()], render_kw={'style': 'height: 50ch;width:100ch;', "rows": 70, "cols": 11}, )
    submit_button = SubmitField('resume')


"""
{
    "session_id": {
        "questions": [
            ("question", "answer")
        ],
        "current_question": index of last question that was sent as a form,
        "timer": <datetime object representing when data should be deleted>
    }
}
"""
data = dict()


def get_hash():
    """
    Returns hash for current user based on IP address and current time
    Used as user identifier
    """

    # put ip and date together
    ip = str(request.remote_addr)
    time = str(datetime.datetime.now())
    to_hash = (ip + time).encode()

    # sha256 hash
    h = sha256()
    h.update(to_hash)
    return h.hexdigest()


def reset_timer(session_id):
    """
    Resets (or adds, if it does not exist) a timer to delete a user's data
        after 10 minutes (prevents unused memory buildup)
    """

    global data
    # length of deletion timer (minutes)
    TIMER_LENGTH = 10

    # cancel last timer if there is one
    if session_id in data and "timer" in data[session_id]:
        data[session_id]["timer"].cancel()

    # make new timer
    data[session_id]["timer"] = Timer(60 * TIMER_LENGTH, delete_questions, args=[session_id])
    data[session_id]["timer"].start()
    log("Setting timer to", str(datetime.datetime.now() + datetime.timedelta(minutes=TIMER_LENGTH)),
        session_id=session_id)


def delete_questions(session_id):
    """
    Deletes questions for an IP address
    Intended to be used by timer
    """

    global data

    if session_id in data:
        log("Deleting data", session_id=session_id)
        del data[session_id]


def log(args, session_id=None):
    """
    Session_id - session id
    Prints a message in yellow in format [current time, session_id] message
    """

    # construct message from args
    message = ""
    for arg in args:
        message += str(arg) + " "

    # print in yellow color
    # [current time, session_id] message
    print(Fore.YELLOW + "[%s, %s] %s" % (str(datetime.datetime.now()), str(session_id), message))


# create main callable
app = create_app()

if __name__ == '__main__':
    http_server = WSGIServer(('127.0.0.1', 9191), app)
    print("starting server on port 9191")
    http_server.serve_forever()
