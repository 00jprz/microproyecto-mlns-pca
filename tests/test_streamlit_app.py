import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class StreamlitAppTest(unittest.TestCase):
    APP_PATH = Path(__file__).resolve().parents[1] / "streamlit_app.py"

    def test_displays_palette_model_and_image_controls(self):
        app = AppTest.from_file(self.APP_PATH, default_timeout=60).run()

        self.assertFalse(app.exception)
        self.assertEqual(app.title[0].value, "Generador de paletas de color")
        self.assertEqual(len(app.selectbox), 2)
        self.assertEqual(len(app.file_uploader), 1)
        self.assertEqual(app.button[0].label, "Generar paleta")


if __name__ == "__main__":
    unittest.main()
