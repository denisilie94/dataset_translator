from tqdm import tqdm
from celery import shared_task

from .translators import get_translation_api
from .models import Dataset, Language, DatasetLanguage, Translator, JsonObject, JsonField


@shared_task
def translate_dataset(dataset_name, source_language_code, target_language_code, translator_name, keys_to_skip=[]):
    # Fetch the dataset, source language, and target language objects
    try:
        dataset = Dataset.objects.get(name=dataset_name)
        translator = Translator.objects.get(name=translator_name)
        source_language = Language.objects.get(code=source_language_code)
        target_language = Language.objects.get(code=target_language_code)
        source_dataset_language = DatasetLanguage.objects.get(dataset=dataset, language=source_language)
    except (Dataset.DoesNotExist, Language.DoesNotExist, Translator.DoesNotExist, DatasetLanguage.DoesNotExist) as e :
        return f"Error: {str(e)}"

    # Get the translator helper
    translate = get_translation_api(translator.name)

    # Get or create the DatasetLanguage object for the target language
    target_dataset_language, _ = DatasetLanguage.objects.get_or_create(
        dataset=dataset, 
        language=target_language
    )

    # Count the number of json objects that have been already translated
    n_json_objects_translated = JsonObject.objects.filter(dataset_language=target_dataset_language).count()

    # Fetch items to translate
    json_objects_to_translate = JsonObject.objects.filter(dataset_language=source_dataset_language).order_by('id')

    for idx, json_object in tqdm(enumerate(json_objects_to_translate)):
        # Assuming that the json objects are processed in the same order we are going to skip the first `n_json_objects_translated`
        if idx < n_json_objects_translated:
            continue

        json_object_translated = JsonObject.objects.create(dataset_language=target_dataset_language)

        for json_field in json_object.json_fields.all():
            json_field_translated = JsonField(
                key=json_field.key,
                value=json_field.value,
                json_object=json_object_translated,
                source_json_field=json_field,
                translator=translator
            )

            if json_field.key.name not in keys_to_skip and json_field.value:
                json_field_translated.value = translate(json_field_translated.value, source_language.name, target_language.name)

            json_field_translated.save()

    return f"Translation completed for dataset {dataset_name} from {source_language.code} to {target_language.code}"




