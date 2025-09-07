import subprocess

if __name__ == "__main__":
    print("🚀 Running forecasting pipeline...")
    subprocess.run(["python", "src/forecasting.py"])

    print("🌐 Starting FastAPI backend...")
    subprocess.Popen(["uvicorn", "app.fastapi_app:app", "--reload", "--port", "8000"])

    print("📊 Starting Streamlit dashboard...")
    subprocess.Popen(["streamlit", "run", "app/streamlit_app.py"])
