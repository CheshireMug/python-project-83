from flask import Flask, render_template, request, \
    redirect, url_for, abort, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://project_manager:password@localhost:5432/page_analyzer'
db = SQLAlchemy(app)


class Url(db.Model):
    __tablename__ = 'urls'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/urls")
def urls_get():
    urls = Url.query.order_by(Url.id.desc()).all()
    return render_template("urls/index.html", urls=urls)


@app.post("/urls")
def urls_post():
    url_name = request.form.get("url").strip()

    if not url_name:
        return redirect(url_for("index"))

    # Проверяем, есть ли уже такой URL в базе
    existing = Url.query.filter_by(name=url_name).first()
    if existing:
        # Уже существует — перенаправляем на страницу этого URL
        flash("Страница уже существует", "info")
        return redirect(url_for("show_url", id=existing.id))

    # Создаём новую запись
    new_url = Url(name=url_name)
    db.session.add(new_url)
    db.session.commit()

    flash("Страница успешно добавлена", "success")
    # Перенаправляем на страницу с информацией о сайте
    return redirect(url_for("show_url", id=new_url.id))


@app.route("/urls/<int:id>")
def show_url(id):
    url = Url.query.get(id)
    if url is None:
        abort(404)
    return render_template("urls/show.html", url=url)
