from io import BytesIO
from pathlib import Path

import cv2
import joblib
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


class PaletteController:
    """Carga los modelos de color y extrae una paleta de una imagen."""

    CONFIG_FILENAME = "configuracion.joblib"
    MODELS_FILENAME = "modelos_paletas.joblib"

    def __init__(self, model_dir=None):
        default_model_dir = Path(__file__).resolve().parents[1] / "resources" / "models"
        self.model_dir = Path(model_dir or default_model_dir)
        config_path = self.model_dir / self.CONFIG_FILENAME
        models_path = self.model_dir / self.MODELS_FILENAME

        if not config_path.is_file():
            raise FileNotFoundError(f"No se encontró la configuración de paletas: {config_path}")
        if not models_path.is_file():
            raise FileNotFoundError(f"No se encontraron los modelos de paletas: {models_path}")

        self.config = joblib.load(config_path)
        self.models = joblib.load(models_path)
        self.preprocessing = self.config["preprocesamiento"]
        self._validate_artifacts()

    def _validate_artifacts(self):
        if self.config.get("version_formato") != 1:
            raise RuntimeError("La versión de configuración de paletas no es compatible.")
        if not isinstance(self.models, dict) or not self.models:
            raise RuntimeError("El archivo de modelos no contiene paletas utilizables.")
        for key, artifact in self.models.items():
            if (
                not isinstance(key, tuple)
                or len(key) != 2
                or not isinstance(artifact, dict)
                or not hasattr(artifact.get("modelo"), "predict")
            ):
                raise RuntimeError("El archivo de modelos tiene una estructura inesperada.")

    def get_styles(self):
        return sorted({style for style, _ in self.models})

    def get_model_names(self, style):
        return sorted(name for model_style, name in self.models if model_style == style)

    def generate_palette(self, image_data, style, model_name):
        model_key = (style, model_name)
        if model_key not in self.models:
            raise ValueError("El modelo de paleta seleccionado no está disponible.")
        if not isinstance(image_data, (bytes, bytearray)) or not image_data:
            raise ValueError("Selecciona una imagen válida para generar la paleta.")

        try:
            with Image.open(BytesIO(image_data)) as source_image:
                image = ImageOps.exif_transpose(source_image).convert("RGB")
                rgb_image = np.asarray(image, dtype=np.uint8)
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError("No fue posible leer la imagen. Prueba con un archivo PNG o JPEG.") from exc

        width, height = self.preprocessing["resize_to"]
        resized_rgb = cv2.resize(
            rgb_image,
            (width, height),
            interpolation=cv2.INTER_AREA,
        )
        lab_pixels = cv2.cvtColor(resized_rgb, cv2.COLOR_RGB2LAB).reshape(-1, 3)
        lab_pixels = lab_pixels.astype(self.preprocessing["dtype"])
        if self.preprocessing["normalizar"]:
            lab_pixels /= self.preprocessing["divisor"]

        sample_limit = min(
            self.preprocessing["muestra_pixeles"],
            self.preprocessing["max_pixeles"],
            len(lab_pixels),
        )
        random_state = self.config["entrenamiento"]["random_state"]
        generator = np.random.default_rng(random_state)
        sample_indices = generator.choice(len(lab_pixels), size=sample_limit, replace=False)
        sampled_lab = lab_pixels[sample_indices]
        sampled_rgb = resized_rgb.reshape(-1, 3)[sample_indices]

        model = self.models[model_key]["modelo"]
        labels = model.predict(sampled_lab)
        cluster_counts = np.bincount(labels, minlength=model.cluster_centers_.shape[0])
        total_pixels = len(labels)
        colors = []

        for cluster, count in enumerate(cluster_counts):
            if count == 0:
                continue
            rgb = np.rint(sampled_rgb[labels == cluster].mean(axis=0)).astype(int)
            red, green, blue = (int(channel) for channel in rgb)
            colors.append(
                {
                    "cluster": cluster,
                    "R": red,
                    "G": green,
                    "B": blue,
                    "HEX": f"#{red:02x}{green:02x}{blue:02x}",
                    "frecuencia": int(count),
                    "proporcion": float(count / total_pixels),
                }
            )

        colors.sort(key=lambda color: color["proporcion"], reverse=True)
        return {"style": style, "reference": model_name, "colors": colors}