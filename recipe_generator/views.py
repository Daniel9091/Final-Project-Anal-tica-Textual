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
    Recibe un JSON con la clave "ingredients".
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
        ingredients = data.get('ingredients')

        if not ingredients or not isinstance(ingredients, list):
            return HttpResponseBadRequest("La clave 'ingredients' es requerida y debe ser una lista.")

        # 3. Preparar el prompt y ejecutar el modelo.
        prompt = f"Crea una receta de cocina usando solo los siguientes ingredientes: {', '.join(ingredients)}\n\nReceta:"
        sequences = generator_pipeline(prompt, max_new_tokens=300, num_return_sequences=1)
        recipe = sequences[0]['generated_text'][len(prompt):].strip()

        return JsonResponse({'recipe': recipe})
    except Exception as e:
        logger.error(f"Error inesperado en la vista de generación: {e}")
        return JsonResponse({'error': 'Ocurrió un error interno en el servidor.'}, status=500)
