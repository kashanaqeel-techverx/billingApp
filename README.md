# Billing App Demo

An intelligent ***NL2SQL*** chatbot for querying ***Google BigQuery*** data using Vertex AI. This app converts user natural language prompts into SQL queries to retrieve information from BigQuery datasets and then generates natural, conversational responses based on the retrieved information.
Designed for intuitive and interactive data exploration, it simplifies access to insights by enabling users to explore data through natural language queries.

****NB***:  In this project, I worked on a customer billing dataset provided by Premier Cloud as a use case, but this application can be adapted to work with any other BigQuery dataset.*


## Features

- **Natural Language Querying**: Gemini LLM converts user prompts into SQL queries.
- **BigQuery Integration**: The LLM execute SQL queries on BigQuery dataset using the best matching predefined procedures.
- **AI-Driven**: Uses Vertex AI's Gemini model for query interpretation.
- **User-Friendly**: Streamlit interface for easy navigation.

## How It Works

1. **Query Parsing**: Users ask  questions related to the dataset context.
2. **BigQuery Procedures**: Custom procedures and functions available for each use case.
3. **AI Model Response**: The Gemini LLM processes user prompts by either generating simple SQL queries or matching the prompt to a pre-defined procedure to retrieve relevant information, and then responds in natural language.
4. **Interactive Chat**: Saves conversation context for follow-ups.

## Repository Overview

- **`app.py`**: Main app logic; manages chat UI, BigQuery calls, and session state.
- **`Dockerfile`**: For containerization, making the app portable.
- **`cloudbuild.yaml`**: Automates build and deploy on Google Cloud Run.
- **`requirements.txt`**: Lists dependencies, including `streamlit` and `google-cloud-bigquery`.
- **`setup.sh`**: Initializes environment variables for Google Cloud access.
- **`Procfile`**: Command for deployment on platforms.
- **`tutorial.md`**: User guide for setup and usage.
- **`project.json`**: Contains project-specific configuration settings in JSON format, such as API keys, BigQuery project details, or other runtime parameters required by the app.

****This is an example use case with the Titanic dataset to illustrate how the project works. Since the dataset I worked with at Premier Cloud contains sensitive data, no real project data is shown here. The image below shows a conversation with the chatbot and how it responds to user queries by retrieving insights from the dataset:****

![Alt text](demo_pic.jpg)


