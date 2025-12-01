from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.apps import apps
import json
import logging

logger = logging.getLogger(__name__)

def chat_view(request: HttpRequest):
    return render(request, 'recipe_generator/chat.html')

@csrf_exempt # Desactiva la protección CSRF para esta API.
@require_http_methods(["POST"]) # Solo permite peticiones de tipo POST.
def generate_recipe_api(request: HttpRequest) -> JsonResponse:
    """
    Vista de API para generar una receta a partir de ingredientes.
    Recibe un JSON con las claves "dish_name" e "ingredients".
    """
    try:
        # 1. Obtener el pipeline cargado desde la configuración de la app.
        app_config = apps.get_app_config('recipe_generator')
        generator_pipeline = app_config.pipeline

        if generator_pipeline is None:
            logger.error("El pipeline no está disponible. ¿Hubo un error durante el inicio?")
            return JsonResponse({'error': 'El servicio de generación no está disponible en este momento.'}, status=503)

        # 2. Procesar la petición de entrada.
        data = json.loads(request.body)
        dish_name = data.get('dish_name')
        ingredients = data.get('ingredients')

        if not dish_name or not ingredients or not isinstance(ingredients, list):
            return HttpResponseBadRequest("Las claves 'dish_name' (texto) e 'ingredients' (lista) son requeridas.")

        # 3. Preparar el prompt para el modelo (usando el nuevo formato).
        prompt = f"### TÍTULO: {dish_name}\n### INGREDIENTES:\n{', '.join(ingredients)}\n\n### PREPARACIÓN:\n"

        # 4. Ejecutar el modelo con los parámetros optimizados de tu Colab.
        output = generator_pipeline(
            prompt,
            max_new_tokens=500,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.4,
            top_k=30,
            repetition_penalty=1.3,
            pad_token_id=generator_pipeline.tokenizer.eos_token_id,
            eos_token_id=generator_pipeline.tokenizer.eos_token_id
        )

        # 5. Post-procesar la respuesta para limpiarla.
        full_text = output[0]['generated_text']
        recipe = full_text.split("### PREPARACIÓN:\n")[-1].strip()
        if "###" in recipe: # Corta si el modelo empieza a alucinar otra sección.
            recipe = recipe.split("###")[0].strip()

        return JsonResponse({'recipe': recipe})
    except Exception as e:
        logger.error(f"Error inesperado en la vista de generación: {e}")
        return JsonResponse({'error': 'Ocurrió un error interno en el servidor.'}, status=500)
