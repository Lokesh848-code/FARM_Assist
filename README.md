# Farmer Assist 🌱

Farmer Assist is a RAG-powered smart farming advisory chatbot for small-scale Indian farmers. It uses local, offline TF-IDF/keyword retrieval from a structured `master_farming_dataset.txt` file and calls the IBM watsonx.ai REST API directly for language generation.

## Features
- **Offline Agronomic Dashboard**: Visual crop selector for major crops (Rice, Maize, Cotton, Mango, Apple, Coconut) with automatic offline retrieval of Soil/Climate, Pest Control, Mandi Price, and Irrigation summaries.
- **Context-Aware AI Chatbot**: A chatbot that maintains the active crop context, allowing farmers to ask specific follow-up questions easily.
- **Secure Configuration**: Fully customized to hide developer credentials while supporting environment-based settings.

---

## Setup Instructions

Follow these steps to run the application locally:

### 1. Copy Environment Configuration
Sensitive API keys and configurations should never be committed to Git. We use environment variables via `python-dotenv`.

Copy the sample environment file to create your active `.env`:
```bash
cp .env.example .env
```
*(On Windows Command Prompt, use `copy .env.example .env`)*

### 2. Fill in credentials
Open the newly created `.env` file in a text editor and fill in the values:
- `WATSONX_API_KEY`: Generate an IBM Cloud API Key by visiting [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys).
- `WATSONX_PROJECT_ID`: Find this in your IBM watsonx.ai project settings.
- `WATSONX_REGION_URL`: The API URL endpoint matching your project's region (default: `https://us-south.ml.cloud.ibm.com`).
- `WATSONX_MODEL_ID`: The LLM ID to use for generation (default: `ibm/granite-4-h-small`).

**⚠️ Warning**: Never commit your `.env` file containing actual keys to public version control! The `.gitignore` has been preconfigured to exclude it.

### 3. Install Dependencies
Run the following command to install all packages:
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
Start the Streamlit server locally:
```bash
streamlit run app.py
```
Then open the displayed local URL (typically [http://localhost:8501](http://localhost:8501)) in your web browser.
