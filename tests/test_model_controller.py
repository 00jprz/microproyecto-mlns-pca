from io import BytesIO
import unittest

from PIL import Image

from src.PaletteController import PaletteController


class PaletteControllerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = PaletteController()

    @staticmethod
    def encode_image(image):
        image_buffer = BytesIO()
        image.save(image_buffer, format="PNG")
        return image_buffer.getvalue()

    def test_uniform_image_produces_one_color_covering_the_image(self):
        image = Image.new("RGB", (32, 24), (220, 35, 45))
        style = self.controller.get_styles()[0]
        model_name = self.controller.get_model_names(style)[0]

        result = self.controller.generate_palette(
            self.encode_image(image), style, model_name
        )

        self.assertEqual(result["style"], style)
        self.assertEqual(result["reference"], model_name)
        self.assertEqual(len(result["colors"]), 1)
        self.assertEqual(result["colors"][0]["HEX"], "#dc232d")
        self.assertEqual(result["colors"][0]["proporcion"], 1.0)

    def test_rejects_invalid_image_and_model(self):
        style = self.controller.get_styles()[0]
        model_name = self.controller.get_model_names(style)[0]
        with self.assertRaises(ValueError):
            self.controller.generate_palette(b"not an image", style, model_name)
        with self.assertRaises(ValueError):
            self.controller.generate_palette(b"image", style, "missing.png")


if __name__ == "__main__":
    unittest.main()
