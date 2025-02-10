import os
import subprocess
import logging
from flask import Flask, request, jsonify
from utils import *

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Determine whether to use Google Cloud Storage
USE_GCS = os.environ.get('USE_GCS', 'False').lower() == 'true'

# Determine whether to suppress output
NO_SLICES = os.environ.get('NO_SLICES', 'False').lower() == 'true'

if USE_GCS:
    from google.cloud import storage
    # Initialize the Google Cloud Storage client
    client = storage.Client()
    bucket_name = os.environ.get('BUCKET_NAME', 'ls_gunicorn_bucket')  # Parameterize the bucket name with default value
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
        instructions_path = os.path.join(output_dir, 'instructions.txt')
        layout_path = os.path.join(output_dir, 'layout.txt')

        instructions_file.save(instructions_path)
        layout_file.save(layout_path)

        if instructions_file.filename.lower().endswith('qasm'):
            cmd = ['./lsqecc_slicer', '-q', '-i', instructions_path, '-l', layout_path]
        else:
            cmd = ['./lsqecc_slicer', '-i', instructions_path, '-l', layout_path]


        if NO_SLICES:
            cmd.append('--noslices')  # Suppress output generation
        else:
            cmd.extend(['-o', output_file_path])  # Specify output file

        # Run lsqecc_slicer with the provided input files
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2  # Timeout in seconds
        )

        # Capture stdout and stderr for debugging
        stdout = proc.stdout.decode('utf-8')
        stderr = proc.stderr.decode('utf-8')
        logging.info("lsqecc_slicer stdout:\n%s", stdout)
        logging.error("lsqecc_slicer stderr:\n%s", stderr)

        # Check for errors
        if proc.returncode != 0:
            return jsonify({"message": "Error", "error": stderr}), 500

        # If no errors while computing
        if NO_SLICES:
            # If NO_SLICES is true, return a simple success message
            result = parse_stdout(stdout)
            return jsonify({"message": "Success", "result": result}), 200
        else:
            # Check if the output file exists
            if not os.path.exists(output_file_path):
                return jsonify({"message": "Error", "error": "Output file not found"}), 500

            if USE_GCS:
                # Upload the output file to Google Cloud Storage
                blob = bucket.blob(f'output/{output_filename}')
                blob.upload_from_filename(output_file_path)

                # Return a success message with the file URL
                return jsonify({
                    "message": "Success",
                    "file_url": f"gs://{bucket_name}/output/{output_filename}"
                }), 200
            else:
                # Read the output file content
                with open(output_file_path, 'r') as f:
                    output_data = f.read()
                # Return the output data as a JSON response
                return app.response_class(
                    response=output_data,
                    status=200,
                    mimetype='application/json'
                )
    except Exception as e:
        logging.exception("Exception occurred during processing")
        return jsonify({"message": "Error", "error": str(e)}), 400

if __name__ == '__main__':
    pass
