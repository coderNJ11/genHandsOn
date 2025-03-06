import os
import json
from flask import Flask, request, jsonify
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

app = Flask(__name__)


def flatten_and_extract_text(submission):
    """
    Flatten submission `data` and `metadata`. Returns:
    - A string that concatenates all keys and values for semantic embedding
    - The original submission object
    """

    def flatten_dict(d, parent_key='', sep=' '):
        """
        Recursively flattens a dictionary into key-value pair strings.
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, ' '.join(map(str, v))))
            else:
                items.append((new_key, str(v)))
        return dict(items)

    flattened_text = ""
    if "data" in submission:
        flattened_text += " ".join([f"{k}: {v}" for k, v in flatten_dict(submission["data"]).items()])
    if "metadata" in submission:
        flattened_text += " " + " ".join([f"{k}: {v}" for k, v in flatten_dict(submission["metadata"]).items()])
    return flattened_text.strip(), submission


def preprocess_submissions(submissions):
    """
    Preprocess all submissions: flatten and extract relevant fields for embedding.
    Returns:
    - A list of texts for generating embeddings
    - A list of the original submission objects
    """
    processed_docs = []
    submission_objects = []
    for submission in submissions:
        flattened_text, original_obj = flatten_and_extract_text(submission)
        processed_docs.append(flattened_text)
        submission_objects.append(original_obj)
    return processed_docs, submission_objects


def load_submissions(file_path):
    """
    Load submissions from a JSON file.
    """
    with open(file_path, "r") as file:
        return json.load(file)


def create_vector_db(submissions):
    """
    Create a FAISS vector database using OpenAI embeddings for the provided submissions.
    """
    # Flatten and extract text for embeddings, while keeping submission objects
    documents, submission_objects = preprocess_submissions(submissions)

    # Ensure OpenAI API key is set
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Environment variable `OPENAI_API_KEY` is not set.")

    # Initialize embeddings using OpenAI
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # Create FAISS vector DB
    vector_db = FAISS.from_texts(
        documents,
        embeddings,
        metadatas=submission_objects  # Reference the actual submission object as metadata
    )

    return vector_db


@app.route("/query", methods=["POST"])
def query_vector_db():
    try:
        # Read data from request
        data = request.get_json()
        query = data.get("query")  # Prompt like "Provide all submission with name: John"
        file_path = data.get("file_path")
        fetch_all = data.get("fetch_all", False)  # Optional parameter to fetch all results

        if not file_path:
            return jsonify({"status": "error", "message": "File path is missing"}), 400

        # Load submissions
        submissions = load_submissions(file_path)

        # Create the vector database
        vector_db = create_vector_db(submissions)

        # Handle query-based or fetch-all logic
        if query:
            retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": len(submissions)})
            search_results = retriever.get_relevant_documents(query)

            # Convert retrieved documents to a list of actual submissions
            results = [doc.metadata for doc in search_results]

            # Make results more concise if `fetch_all` is False
            if not fetch_all:
                results = results[:5]

        else:
            # Query not provided: Return all submission objects
            retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": len(submissions)})
            search_results = retriever.get_relevant_documents("")  # Empty query to extract all
            results = [doc.metadata for doc in search_results]

        # Return results as JSON
        return jsonify({
            "status": "success",
            "results": results
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
