from flask import Flask, request, jsonify, redirect, abort, render_template
from werkzeug.exceptions import HTTPException
import threading

app = Flask(__name__)

# In-memory URL store: short_code -> long_url
url_store = {}
# Simple incremental counter for generating IDs
_counter_lock = threading.Lock()
_counter = 0
_base62_alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _encode_base62(num: int) -> str:
    if num == 0:
        return _base62_alphabet[0]
    chars = []
    base = len(_base62_alphabet)
    while num > 0:
        num, rem = divmod(num, base)
        chars.append(_base62_alphabet[rem])
    return ''.join(reversed(chars))


def generate_short_code() -> str:
    global _counter
    with _counter_lock:
        _counter += 1
        return _encode_base62(_counter)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/shorten', methods=['POST'])
def shorten():
    """Create a short URL for the provided long URL.
    Accepts JSON {"url": "https://example.com"} or form field 'url'.
    Returns JSON with the short code and full short URL.
    """
    long_url = None
    if request.is_json:
        data = request.get_json(silent=True) or {}
        long_url = data.get('url')
    if not long_url:
        long_url = request.form.get('url')
    if not long_url:
        return jsonify({'error': 'Missing url'}), 400

    code = generate_short_code()
    url_store[code] = long_url

    short_url = request.host_url.rstrip('/') + '/' + code
    return jsonify({
        'code': code,
        'short_url': short_url,
        'long_url': long_url
    }), 201


@app.route('/<code>', methods=['GET'])
def redirect_code(code: str):
    long_url = url_store.get(code)
    if not long_url:
        abort(404)
    return redirect(long_url, code=302)


@app.errorhandler(Exception)
def handle_unexpected_error(err):
    """Return JSON for errors occurring on the /shorten endpoint so the
    frontend JS can show a clean message instead of failing to parse HTML.
    For other routes, keep default behavior (especially during debug) so
    Flask's debugger / HTML pages still help during development.
    """
    # Pass through HTTP errors (404, 400, etc.) unchanged unless we want
    # to enforce JSON for /shorten requests.
    if isinstance(err, HTTPException):
        if request.path.startswith('/shorten'):
            # Provide consistent JSON structure.
            return jsonify({'error': err.description or 'Request error'}), err.code
        return err

    # Log unexpected exceptions.
    app.logger.exception('Unhandled exception')
    if request.path.startswith('/shorten'):
        return jsonify({'error': 'Internal server error'}), 500
    # For non-/shorten paths, re-raise so Flask can show the debug page.
    raise err

if __name__ == '__main__':
    # Debug server for development
    app.run(host='0.0.0.0', port=5000, debug=True)
