import os
from flask import Flask, request, jsonify
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["your_database_name"]


def flatten_json(json_obj, parent_key="", sep=" "):
    items = []
    for key, value in json_obj.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_json(value, new_key, sep=sep).items())
        elif isinstance(value, list):
            if all(isinstance(i, dict) for i in value):
                for idx, item in enumerate(value):
                    items.extend(flatten_json(item, f"{new_key}[{idx}]", sep=sep).items())
            else:
                items.append((new_key, " ".join(map(str, value))))
        else:
            items.append((new_key, str(value)))
    return dict(items)


def flatten_and_extract_text(json_record):
    flattened_json = flatten_json(json_record)
    flattened_text = " ".join([f"{k}: {v}" for k, v in flattened_json.items()])
    return flattened_text.strip(), json_record


def preprocess_json_records(records):
    processed_docs = []
    original_objects = []
    for record in records:
        flattened_text, original_obj = flatten_and_extract_text(record)
        processed_docs.append(flattened_text)
        original_objects.append(original_obj)
    return processed_docs, original_objects


def fetch_json_records(collection_name, start_date=None, end_date=None):
    collection = db[collection_name]
    query = {}
    if start_date and end_date:
        query["created"] = {
            "$gte": datetime.fromisoformat(start_date),
            "$lte": datetime.fromisoformat(end_date),
        }
    records = list(collection.find(query))
    for record in records:
        record.pop("_id", None)
    return records


def create_vector_db(json_records):
    documents, original_objects = preprocess_json_records(json_records)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Environment variable `OPENAI_API_KEY` is not set.")
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vector_db = FAISS.from_texts(documents, embeddings, metadatas=original_objects)
    return vector_db


@app.route("/query", methods=["POST"])
def query_vector_db():
    try:
        data = request.get_json()
        query = data.get("query")
        collection_name = data.get("collection_name")
        fetch_all = data.get("fetch_all", False)
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        if not collection_name:
            return jsonify({"status": "error", "message": "Collection name is missing"}), 400
        json_records = fetch_json_records(collection_name, start_date, end_date)
        if not json_records:
            return jsonify({"status": "error", "message": "No records found in the specified collection"}), 400
        vector_db = create_vector_db(json_records)
        if query:
            retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": len(json_records)})
            search_results = retriever.get_relevant_documents(query)
            results = [doc.metadata for doc in search_results]
            if not fetch_all:
                results = results[:5]
        else:
            retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": len(json_records)})
            search_results = retriever.get_relevant_documents("")
            results = [doc.metadata for doc in search_results]
        return jsonify({"status": "success", "results": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
