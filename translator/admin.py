import json

from tqdm import tqdm

from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponse

from .models import Language, Key, Dataset, Translator, DatasetLanguage, JsonObject, JsonField


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Translator)
class TranslatorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.action(description='Import JSON objects from file')
def import_json_objects(modeladmin, request, queryset):
    for dataset_language in queryset:
        try:
            # Read the JSON file
            with dataset_language.file.open('r') as file:
                data = json.load(file)

            if isinstance(data, list):
                for obj in tqdm(data):
                    # Create a JsonObject instance
                    json_object = JsonObject.objects.create(dataset_language=dataset_language)

                    for key, value in obj.items():
                        # Ensure the key exists in the Key model
                        key_instance, created = Key.objects.get_or_create(name=key)

                        # Create a JsonField instance
                        JsonField.objects.create(
                            key=key_instance,
                            value=value,
                            json_object=json_object,
                            valid=True
                        )

                dataset_language.imported = True
                dataset_language.save()
            else:
                raise ValidationError("The file does not contain a JSON array.")

        except json.JSONDecodeError:
            modeladmin.message_user(request, f"Invalid JSON in file: {dataset_language.file.name}", level='error')
        except Exception as e:
            modeladmin.message_user(request, f"Error processing file: {dataset_language.file.name} - {e}", level='error')


@admin.action(description='Export Dataset Language to JSON file')
def export_json_objects(modeladmin, request, queryset):
    # Ensure only one dataset is selected
    if queryset.count() != 1:
        messages.error(request, "Please select only one dataset for export.")
        return

    dataset_language = queryset.first()
    exported_data = []

    # For the selected DatasetLanguage, find all related JsonObjects
    json_objects = dataset_language.json_objects.all()

    for json_object in json_objects:
        # Serialize each JsonObject into a dictionary
        json_fields = json_object.json_fields.all()
        json_data = {field.key.name: field.value for field in json_fields}
        exported_data.append(json_data)

    # Convert the dictionary to a JSON string
    json_string = json.dumps(exported_data, indent=4, ensure_ascii=False)

    # Create an HttpResponse with a JSON file
    response = HttpResponse(json_string, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{dataset_language.dataset.name}_{dataset_language.language.code}.json"'

    return response


@admin.register(DatasetLanguage)
class DatasetLanguageAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'language', 'file', 'imported')
    search_fields = ('dataset__name', 'language__name')
    list_filter = ('dataset', 'language')
    actions = [import_json_objects, export_json_objects]


class JsonFieldInline(admin.TabularInline):
    model = JsonField
    extra = 0
    fields = ('key', 'value', 'translator', 'valid')

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in JsonField._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(JsonObject)
class JsonObjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'dataset_language',)
    search_fields = ('id',)
    list_filter = ('dataset_language__dataset', 'dataset_language__language')
    inlines = [JsonFieldInline]

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in JsonObject._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(JsonField)
class JsonFieldAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'json_object', 'translator', 'valid')
    search_fields = ('key__name', 'json_object__dataset_language__dataset__name', 'json_object__dataset_language__language__name')
    list_filter = ('valid', 'key', 'json_object__dataset_language__dataset', 'json_object__dataset_language__language')

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in JsonField._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True
