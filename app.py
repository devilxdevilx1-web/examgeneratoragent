from pathlib import Path
import runpy

# Keep `streamlit run app.py` working while the actual UI lives in ui/app.py.
runpy.run_path(Path(__file__).resolve().parent / "ui" / "app.py", run_name="__main__")
