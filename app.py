from flask import Flask, request, jsonify, redirect, abort
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
    # Placeholder: later this will return an HTML form to submit a long URL.
    return 'Hello, world!'


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


if __name__ == '__main__':
    # Debug server for development
    app.run(host='0.0.0.0', port=5000, debug=True)
