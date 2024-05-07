
from flask import Flask, render_template, request
import etcd3
import grpc

app = Flask(__name__)

# Connect to etcd
try:
    etcd = etcd3.client()
except grpc.RpcError as e:
    print("Error connecting to etcd:", e)
    etcd = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/put', methods=['POST'])
def put_key():
    if not check_etcd_connection():
        return render_template('error.html', message="Error: Failed to connect to etcd")

    key = request.form['key']
    value = request.form['value']
    try:
        create_or_update_key(key, value)
    except Exception as e:
        return render_template('error.html', message=str(e))
    return render_template('index.html')

# Apply similar changes to other route handlers


@app.route('/get', methods=['POST'])
def get_key():
    if etcd is None:
        return render_template('error.html', message="Error: Failed to connect to etcd")

    key = request.form['key']
    try:
        value = get_key_route(key)  # Make sure get_key_route is correctly fetching the value
        if value is None:
            return render_template('error.html', message=f"Key '{key}' not found")
        else:
            return render_template('new.html', key=key, value=value)
    except Exception as e:
        return render_template('error.html', message=str(e))



@app.route('/delete', methods=['POST'])
def delete_key():
    if etcd is None:
        return render_template('error.html', message="Error: Failed to connect to etcd")

    key = request.form['key']
    result = delete_key(key)
    if result == "Key does not exist":
        return render_template('error.html', message="Error: Key does not exist")
    return render_template('index.html', message=result)

@app.route('/list')
def list_keys():
    if etcd is None:
        return render_template('error.html', message="Error: Failed to connect to etcd")

    try:
        keys = list_keys()
    except Exception as e:
        return render_template('error.html', message=str(e))
    return render_template('list.html', keys=keys)

def create_or_update_key(key, value):
    try:
        etcd.put(key, value)
    except Exception as e:
        return render_template('error.html', message=str(e))

def get_key_route(key):
    try:
        value, _ = etcd.get(key)
        return value.decode() if value else None
    except Exception as e:
        return render_template('error.html', message=str(e))

def delete_key(key):
    value, _ = etcd.get(key)
    if value is None:
        return "Key does not exist"
    else:
        etcd.delete(key)
        return "Key deleted successfully"
    # try:
    #     etcd.delete(key)
    # except Exception as e:
    #     return render_template('error.html', message=str(e))

def list_keys():
    try:
        return [meta.key.decode() for _, meta in etcd.get_all()]
    except Exception as e:
        return render_template('error.html', message=str(e))
def check_etcd_connection():
    if etcd is None:
        return False
    try:
        # Attempt a simple get operation to check connectivity
        etcd.status()
        return True
    except Exception:
        return False


if __name__ == "__main__":
    app.run(debug=True)