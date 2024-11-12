import os
import subprocess
from flask import Flask, request, jsonify
from google.cloud import storage

app = Flask(__name__)

# Initialize the Google Cloud Storage client
client = storage.Client()
bucket_name = 'ls_gunicorn_bucket'
bucket = client.bucket(bucket_name)

# Ensure the output directory exists within the working directory
output_dir = './output'
os.makedirs(output_dir, exist_ok=True)

@app.route('/process', methods=['POST'])
def process():
    try:
        # Get the instructions and layout files from the request
        instructions_file = request.files['instructions']
        layout_file = request.files['layout']
        
        # Extract base names without extensions
        instructions_name = os.path.splitext(instructions_file.filename)[0]
        layout_name = os.path.splitext(layout_file.filename)[0]
        
        # Create a combined output filename
        output_filename = f"{instructions_name}_{layout_name}.json"
        output_file_path = os.path.join(output_dir, output_filename)
        
        # Save the uploaded files to the working directory
        instructions_path = './instructions.txt'
        layout_path = './layout.txt'
        instructions_file.save(instructions_path)
        layout_file.save(layout_path)

        # Run lsqecc_slicer with the provided input files and dynamic output filename
        process = subprocess.run(
            ['./lsqecc_slicer', '-i', instructions_path, '-l', layout_path, '-o', output_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Capture stdout and stderr for debugging
        stdout = process.stdout.decode('utf-8')
        stderr = process.stderr.decode('utf-8')
        print("lsqecc_slicer stdout:", stdout)
        print("lsqecc_slicer stderr:", stderr)

        # Check for errors
        if process.returncode != 0:
            return jsonify({"message": "Error", "error": stderr}), 500

        # Check if the output file exists
        if not os.path.exists(output_file_path):
            return jsonify({"message": "Error", "error": "Output file not found"}), 500

        # Upload the output file to Google Cloud Storage
        blob = bucket.blob(f'output/{output_filename}')
        blob.upload_from_filename(output_file_path)

        # Return a success message with the file URL
        return jsonify({
            "message": "Success",
            "file_url": f"gs://{bucket_name}/output/{output_filename}"
        }), 200

    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({"message": "Error", "error": str(e)}), 400

if __name__ == '__main__':
    pass