from flask import Flask, request, jsonify
from rag_pipeline import build_simple_index, query_index

app = Flask(__name__)
index = build_simple_index()

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json() or {}
    q = data.get("q", "")
    results = query_index(index, q)
    return jsonify(results)


if __name__ == "__main__":
    app.run(port=7860, debug=True)
