from flask import Flask, render_template, request, redirect, url_for
import subprocess

app = Flask(__name__)

# Model file paths
MODEL_PATHS = {
    "model1": r"C:\Users\shail\Desktop\Project\3 models\final1.py",
    "model2": r"C:\Users\shail\Desktop\Project\3 models\final2.py",
    "model3": r"C:\Users\shail\Desktop\Project\3 models\final3.py"
}


@app.route('/')
def index():
    """Render the home page with model buttons."""
    return render_template('index.html')


@app.route('/run_model', methods=['POST'])
def run_model():
    """Launch the selected model in a new terminal window."""
    model_name = request.form.get('model')
    
    if model_name in MODEL_PATHS:
        model_path = MODEL_PATHS[model_name]
        try:
            # Launch model in a new terminal window
            subprocess.Popen(f'start cmd /k python "{model_path}"', shell=True)
        except Exception as e:
            print(f"Failed to start model: {e}")
    
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
