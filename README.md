# shittycorn
a very simple implementation of web server supporting WSGI compatible applications


# Usage
install the package
```shell
python3 -m pip install shittycorn
```

in `main.py`:
```python
import flask

app = flask.Flask(__name__)

@app.get('/')
def index():
    return 'Hello, World!'
```

run the wsgi application:
```shell
python3 -m shittycorn main.app
```