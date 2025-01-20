
# TODO

- echo https://sweetalert2.github.io/

## Stack

- python
- flask: web framework
- jinja2: templating

## Refs

- Python Crash Course from No Starch Press
- Learn Python the Hard Way by Zed Shaw
- Python for Everybody by Dr. Charles R. Severance

## Nix environment / shell

- shell.nix

```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python310
    pkgs.python310Packages.flask
    pkgs.python310Packages.jinja2
  ];
}
```

- to run:

```zsh
nix-shell
```

and

```
python --version
flask --version
```

- create app.py (in root?)

```
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

- create templates/index.html

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Flask HTMX Tutorial</title>
  </head>
  <body>
    <h1>Welcome to Flask + HTMX</h1>
  </body>
</html>
```

- run app / server:

```bash
python app.py

```

http://127.0.0.1:5000/

# Bugs

- [ ] email is being saved without clicking save button but when clicking back button.
