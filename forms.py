from flask_wtf import FlaskForm  # type: ignore
from wtforms import StringField, SubmitField  # type: ignore


class URLShortenForm(FlaskForm):
    url: StringField = StringField(
        render_kw={
            "placeholder": "Enter a URL to shorten",
            "class": "form-control m-1",
        },
        label="",
    )
    submit: SubmitField = SubmitField(
        "Shorten", render_kw={"class": "btn btn-md btn-primary m-1"}
    )
