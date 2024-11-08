import os
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# Ensure the output directory exists
os.makedirs("/output", exist_ok=True)

@app.route('/process', methods=['POST'])
def process():
    try:
        # Get the instructions and layout files from the request
        instructions_file = request.files['instructions']
        layout_file = request.files['layout']
        
        # Save the uploaded files to the container
        instructions_path = './instructions.txt'
        layout_path = './layout.txt'
        
        instructions_file.save(instructions_path)
        layout_file.save(layout_path)

        # Run lsqecc_slicer with the provided input files
        process = subprocess.run(
            ['./lsqecc_slicer', '-i', instructions_path, '-l', layout_path, '-o', '/output/output.json'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Return the process output or error
        if process.returncode == 0:
            return jsonify({"message": "Success", "output": process.stdout.decode('utf-8')}), 200
        else:
            print(f"Error: {process.stderr.decode('utf-8')}")
            return jsonify({"message": "Error", "error": process.stderr.decode('utf-8')}), 500

    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({"message": "Error", "error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
