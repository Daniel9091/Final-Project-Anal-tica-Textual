from django.apps import AppConfig
from django.conf import settings
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import logging
import os

# Configura un logger para ver el progreso en la consola de Django
logger = logging.getLogger(__name__)


class RecipeGeneratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipe_generator'

    # El pipeline se inicializa como None. Se cargará en el método ready().
    pipeline = None

    def ready(self):
        """
        Este método se ejecuta una vez cuando Django se inicia.
        Es el lugar perfecto para la carga pesada del modelo.
        """
        # Esta condición evita que el código se ejecute dos veces en modo DEBUG.
        if os.environ.get('RUN_MAIN', None) == 'true' and self.pipeline is None:
            try:
                logger.info("--- Iniciando la carga del modelo de IA ---")

                model_path = settings.BASE_DIR / 'ml_models'

                tokenizer = AutoTokenizer.from_pretrained(str(model_path))
                model = AutoModelForCausalLM.from_pretrained(
                    str(model_path),
                    device_map="auto",
                    dtype="auto", # Cambiamos torch_dtype por dtype
                    trust_remote_code=True
                )

                self.pipeline = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer
                )

                logger.info("--- ✅ Modelo de IA y pipeline cargados exitosamente ---")

            except Exception as e:
                logger.error(f"--- ❌ Error catastrófico al cargar el modelo de IA: {e} ---")
