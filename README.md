# Django Application with Celery for Managing and Translating Instruction Datasets

This Django application is designed to help manage and translate different instruction datasets in JSON format. It uses Celery for handling translation tasks asynchronously. The primary use of this application is through the admin panel. Here are the steps to set up and use the application:

## Setup

1. Clone the repository and navigate to the project directory.

2. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

3. Run the following Django management commands to set up the database:

   ```
   python manage.py makemigrations
   python manage.py makemigrations translator
   python manage.py migrate
   ```

4. Create a superuser to access the admin panel:

   ```
   python manage.py createsuperuser
   ```

## Configuration

- Open `settings.py` and configure the following settings:

  - `OPENAI_API_KEY`: Provide your OpenAI API key.
  - `OPENAI_API_URL`: Set the URL for the OpenAI API.
  - `SECRET_KEY`: Add a secret key for the application.

## Usage

1. Access the admin panel by visiting `http://localhost:8000/admin/` and log in with the superuser credentials created earlier.

2. In the admin panel, ensure that you have the following configured:

   - **Languages**: Add the languages you will be working with (e.g., English and Romanian).

   - **Translators**: Configure translators (e.g., OpenAI).

3. Create a new `DatasetLanguage` in the admin panel. For example, you can create a dataset named "alpaca_data" with the source language set to English and provide the corresponding JSON file.

4. After creating the `DatasetLanguage` object, use the custom admin action "Import JSON objects from file" to import the JSON data into the database. Depending on the file's size, this process may take some time.

5. Create a periodic task for handling translations. In the "Periodic Task" section, create a custom task named `translate_dataset` with the following arguments:

   ```json
   {
     "dataset_name": "alpaca_dataset",
     "source_language_code": "ro",
     "target_language_code": "en",
     "translator_name": "openai",
     "keys_to_skip": []
   }
   ```

   This task will initiate the translation of all data in the database.

6. Once the translations are completed, you can export the new dataset using the admin custom action "Export Dataset Language to JSON file" from the "Dataset Language" section in the admin panel.

Now you have a Django application with Celery set up to manage and translate instruction datasets. Feel free to customize the application and add additional custom translators in the `task.py` file to suit your needs.
