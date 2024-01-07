from django.db import models
from django.core.validators import FileExtensionValidator


class Language(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Key(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Dataset(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Translator(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class DatasetLanguage(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='dataset_languages')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='dataset_languages')
    file = models.FileField(upload_to='datasets/', validators=[FileExtensionValidator(allowed_extensions=['json'])])
    imported = models.BooleanField(default=False)

    class Meta:
        unique_together = ('dataset', 'language')
        indexes = [
            models.Index(fields=['dataset', 'language']),
        ]

    def __str__(self):
        return f"{self.dataset.name} - {self.language.name}"


class JsonObject(models.Model):
    dataset_language = models.ForeignKey(DatasetLanguage, on_delete=models.CASCADE, related_name='json_objects')

    def __str__(self):
        return f"JSON object for {self.dataset_language}"


class JsonField(models.Model):
    key = models.ForeignKey(Key, on_delete=models.CASCADE, related_name='json_fields')
    value = models.TextField()
    json_object = models.ForeignKey(JsonObject, on_delete=models.CASCADE, related_name='json_fields')
    source_json_field = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='json_fields')
    translator = models.ForeignKey(Translator, on_delete=models.CASCADE, null=True, blank=True, related_name='json_fields')
    valid = models.BooleanField(default=False)

    def __str__(self):
        return f"JSON field: {self.key.name} - Valid: {self.valid}"
