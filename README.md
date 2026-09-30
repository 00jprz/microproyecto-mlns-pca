# microproyecto-mlns-pca
Genera paletas de colores dominantes desde una imagen usando los modelos KMeans incluidos en `resources/models`.

Instala las dependencias y ejecuta la aplicación con:

```sh
python -m pip install -r requirements.txt -c requirements.lock.txt
python -m streamlit run streamlit_app.py
```

En la aplicación, selecciona un estilo y una obra de referencia, carga una imagen y genera su paleta con la distribución de cada color.
