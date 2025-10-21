from flask import Flask, render_template, request, redirect, \
    url_for, flash, abort
from .database import get_all_urls, get_url_by_name, \
    get_url_by_id, insert_url, insert_check, \
    get_checks_by_url_id
from urllib.parse import urlparse


def normalize_url(url):
    parsed = urlparse(url)
    scheme = parsed.scheme or "http"
    netloc = parsed.netloc or parsed.path
    normalized = f"{scheme}://{netloc}".lower().rstrip('/')
    return normalized


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/urls")
def urls_get():
    urls = get_all_urls()
    return render_template("urls/index.html", urls=urls)


@app.post("/urls")
def urls_post():
    url_name = request.form.get("url", "").strip()

    if not url_name:
        return redirect(url_for("index"))

    normalized_url = normalize_url(url_name)

    existing = get_url_by_name(normalized_url)
    if existing:
        flash("Страница уже существует", "info")
        return redirect(url_for("show_url", id=existing["id"]))

    new_id = insert_url(normalized_url)
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("show_url", id=new_id))


@app.route("/urls/<int:id>")
def show_url(id):
    url = get_url_by_id(id)
    if url is None:
        abort(404)

    checks = get_checks_by_url_id(id)
    return render_template("urls/show.html", url=url, checks=checks)


@app.post("/urls/<int:id>/checks")
def check_url(id):
    url = get_url_by_id(id)
    if url is None:
        abort(404)

    insert_check(id)
    flash("Страница успешно проверена", "success")
    return redirect(url_for("show_url", id=id))
