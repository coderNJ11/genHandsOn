import os
import json
from flask import Flask, request, jsonify
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

app = Flask(__name__)


# Load submissions from JSON file
def load_submissions(file_path):
    with open(file_path, "r") as file:
        submissions = json.load(file)
    return submissions


# Create FAISS vector database from submissions
def create_vector_db(submissions):
    # Extract document texts and metadata from the submissions
    documents = [
        {"text": sub["data"]["comments"], "metadata": {"id": sub["_id"]}}
        for sub in submissions if "comments" in sub.get("data", {})
    ]

    # Ensure OpenAI API key is set
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Environment variable `OPENAI_API_KEY` is not set.")

    # Initialize embeddings using OpenAI
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # Create the vector database using FAISS
    vector_db = FAISS.from_texts(
        [doc["text"] for doc in documents],
        embeddings,
        metadatas=[doc["metadata"] for doc in documents],
    )

    return vector_db


# Flask route for querying the vector database
@app.route("/query", methods=["POST"])
def query_vector_db():
    try:
        # Get the request data containing query and file path
        data = request.get_json()
        query = data.get("query")
        file_path = data.get("file_path")

        if not query or not file_path:
            return jsonify({"status": "error", "message": "Query or file path is missing"}), 400

        # Load submissions from the specified file
        submissions = load_submissions(file_path)

        # Create the vector database
        vector_db = create_vector_db(submissions)

        # Perform the search in the vector database
        retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        search_results = retriever.get_relevant_documents(query)

        # Convert `Document` objects to JSON-serializable format
        results = [
            {
                "text": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in search_results
        ]

        # Return the search results as JSON
        return jsonify({
            "status": "success",
            "results": results
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    # Start the Flask app
    app.run(host="0.0.0.0", port=5000)
