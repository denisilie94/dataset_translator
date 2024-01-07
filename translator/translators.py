from openai import OpenAI

from django.conf import settings


def openai_translate(api_key=settings.OPENAI_API_KEY):
    def translate(content, source_language, target_language):
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"You will be provided with a sentence in {source_language}, and your task is to translate it into {target_language}. If the translation is not possible, return the original text."
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            temperature=0.7,
            max_tokens=4096,
            top_p=1
        )

        return response.choices[0].message.content

    return translate


def another_translate(api_key=settings.SYSTRAN_API_KEY):
    def translate(content, source_language, target_language):
        pass
    return translate


def get_translation_api(api_name):
    if api_name.lower() == 'openai':
        return openai_translate()
    elif api_name.lower() == 'another':
        return anotherapi_translate()
    else:
        raise ValueError("Unsupported API")
