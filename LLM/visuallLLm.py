import json
import os
from flask import Flask, request, jsonify, send_file
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)


# Load submissions from a JSON file
def load_submissions(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


# Generate a bar chart for submissions based on formName and state
def generate_chart(submissions, filters=None):
    """
    Generates a chart based on the provided submissions.
    If filters are provided (e.g., state, formName), data is filtered accordingly.
    Returns a file-like object containing the generated HTML chart.
    """
    # Apply filters if provided
    filtered_submissions = submissions
    if filters:
        for key, value in filters.items():
            filtered_submissions = [sub for sub in filtered_submissions if sub.get(key) == value]

    # Group data by formName and state
    chart_data = {}
    for sub in filtered_submissions:
        form_name = sub.get("formName", "Unknown")
        state = sub.get("state", "Unknown")
        chart_data.setdefault(form_name, {}).setdefault(state, 0)
        chart_data[form_name][state] += 1

    # Generate data for the bar chart
    form_names = list(chart_data.keys())
    states = set()
    for state_counts in chart_data.values():
        states.update(state_counts.keys())
    states = list(states)

    # Data transformation for plotting
    state_counts_by_form = {state: [chart_data[form].get(state, 0) for form in form_names] for state in states}

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.8 / len(states)  # Split bar width for multiple states
    x = range(len(form_names))

    for i, state in enumerate(states):
        ax.bar(
            [pos + i * bar_width for pos in x],
            state_counts_by_form[state],
            bar_width,
            label=f"State: {state}"
        )

    ax.set_xlabel("Form Name")
    ax.set_ylabel("Submission Count")
    ax.set_title("Submissions by Form Name and State")
    ax.set_xticks([pos + bar_width * (len(states) / 2 - 0.5) for pos in x])
    ax.set_xticklabels(form_names)
    ax.legend()

    # Save the image to a file-like object
    img = BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()

    return img


@app.route("/generate-chart", methods=["POST"])
def generate_chart_api():
    try:
        # Parse request data
        data = request.get_json()
        file_path = data.get("file_path")  # Path to the JSON file
        filters = data.get("filters", None)  # Filters for submissions (e.g., by state or formName)

        if not file_path:
            return jsonify({"status": "error", "message": "File path is missing!"}), 400

        # Load submissions from file
        submissions = load_submissions(file_path)

        # Generate chart with or without filters
        img = generate_chart(submissions, filters)

        # Save the response as an image file and return for viewing
        output_file = "output_chart.png"
        with open(output_file, "wb") as f:
            f.write(img.read())
        return send_file(output_file, mimetype="image/png")

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    # Start the Flask app
    app.run(host="0.0.0.0", port=5000)
