from flask import Flask, render_template, request, redirect, \
    url_for, flash, abort
from .database import get_all_urls, get_last_check, get_url_by_name, \
    get_url_by_id, insert_url, insert_check, get_checks_by_url_id
from urllib.parse import urlparse
import requests


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

    urls_with_checks = []
    for url in urls:
        last_check = get_last_check(url["id"])
        url_info = {
            "id": url["id"],
            "name": url["name"],
            "created_at": url["created_at"],
            "last_check": url["last_check"],
            "status_code": last_check["status_code"] if last_check else None
        }
        urls_with_checks.append(url_info)

    return render_template("urls/index.html", urls=urls_with_checks)


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

    try:
        response = requests.get(
            url["name"]
        )
        status_code = response.status_code
    except requests.exceptions.RequestException as e:
        flash("Произошла ошибка при проверке", "error")
        return redirect(url_for("show_url", id=id))

    insert_check(id, status_code)
    flash("Страница успешно проверена", "success")
    return redirect(url_for("show_url", id=id))
