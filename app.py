from main import ShortURLManager
from flask import Flask, render_template, redirect, request, url_for
from flask_bootstrap import Bootstrap5
import secrets
from htmlmin.decorator import htmlmin

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


app = Flask(__name__)
Bootstrap5(app)
app.secret_key = secrets.token_hex(32)

manager = ShortURLManager("database/database.db")


class URLShortenForm(FlaskForm):
    url = StringField(
        render_kw={
            "placeholder": "Enter a URL to shorten",
            "class": "form-control m-1",
        },
        label="",
    )
    submit = SubmitField("Shorten", render_kw={"class": "btn btn-md btn-primary m-1"})


@app.route("/shorten", methods=["POST"])
def shorten():
    form = URLShortenForm()
    if form.validate_on_submit():
        try:
            shortened = f"{request.root_url}h/{manager.shorten(form.url.data)}"
            return render_template(
                "new_link.html", context={"to": shortened, "from": form.url.data}
            )
        except Exception as err:
            return render_template("index.html", context={"error": err}, form=form)
    return render_template("index.html", context={"error": form.errors}, form=form)


@app.route("/")
def main():
    return render_template("index.html", form=URLShortenForm())


@app.route("/h/<hash>")
def redirect_hash(hash):
    url = manager.unshorten(hash)
    if not url:
        return render_template(
            "index.html", context={"error": f"URL with hash '{hash}' doesn't exist"}
        )
    return redirect(url)


app.run(port=8080)
