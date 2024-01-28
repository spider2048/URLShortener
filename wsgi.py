from app import app

if __name__ == '__main__':
    from waitress import serve
    from flask_minify import Minify  # minify html

    Minify(app=app, html=True, js=True, cssless=True)
    serve(app, host='0.0.0.0', port=8000)