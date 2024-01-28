import os
import secrets
import time
from typing import Optional
from urllib.parse import urljoin

from flask import Flask, redirect, render_template, request, jsonify
from flask_bootstrap import Bootstrap5  # type: ignore
from werkzeug.wrappers.response import Response

from main import ShortURLManager

from forms import URLShortenForm  # type: ignore

app = Flask(__name__)
Bootstrap5(app)
app.secret_key = secrets.token_hex(32)

manager = ShortURLManager("database/database.db")


@app.route("/shorten", methods=["POST"])
def shorten() -> str:
    form = URLShortenForm()
    if form.validate_on_submit():
        try:
            hash = manager.shorten(form.url.data)
            shortened = urljoin('/h/', hash)
            return render_template("new_link.html", context={
                "hash": hash,
                "to": shortened,
                "from": form.url.data
            })
        
        except Exception as err:
            return render_template("index.html", context={"error": err}, form=form)
    return render_template("index.html", context={"error": form.errors}, form=form)


@app.route("/")
def main() -> str:
    return render_template("index.html", form=URLShortenForm())

@app.route('/stats/<hash>')
def get_hash_stats(hash: str) -> str:
    hash_target = manager.unshorten(hash)
    if hash_target is None:
        return render_template(
            'link_stats.html',
            context={
                'exists': False,
                'hash': hash
            }
        )

    hash_stats = manager.get_hash_stats(hash)
    return render_template('link_stats.html', context={
        'exists': True,
        'hash': hash,
        'stats': hash_stats,
        'target': hash_target
    })

@app.route("/h/<hash>")
def redirect_hash(hash: str) -> Optional[Response | str]:
    url = manager.unshorten(hash)
    manager.add_stats(
        hash,
        request.headers.get('referer', ''),
        request.remote_addr,
        time.asctime()
    )

    if not url:
        return render_template(
            "index.html", context={"error": f"URL with hash '{hash}' doesn't exist"}
        )
    return redirect(url)


if __name__ == "__main__":
    app.run(port=8080, debug=os.environ.get("LOCAL", False))