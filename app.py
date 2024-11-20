import time
import vertexai
import pandas as pd
import io
from io import StringIO
from google.cloud import bigquery
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

registry_url = os.getenv("REGISTRY_URL")
deploy_region = os.getenv("DEPLOY_REGION")

vertexai.init(project="project_id", location="your_location")

BIGQUERY_DATASET_ID = "Billing_Workspace_Chatbot"

list_datasets_func = FunctionDeclaration(
    name="list_datasets",
    description="Get a list of datasets that will help answer the user's question",
    parameters={
        "type": "object",
        "properties": {},
    },
)

list_tables_func = FunctionDeclaration(
    name="list_tables",
    description="List tables in a dataset that will help answer the user's question",
    parameters={
        "type": "object",
        "properties": {
            "dataset_id": {
                "type": "string",
                "description": "Dataset ID to fetch tables from.",
            }
        },

        "required": [
            "dataset_id",
        ],
    },
)

get_table_func = FunctionDeclaration(
    name="get_table",
    description="Get information about a table, including the description, schema, and number of rows that will help answer the user's question. Always use the 'Billing_Workspace_Chatbot' dataset, 'subscription_logs' table or the provided procedures",
    parameters={
        "type": "object",
        "properties": {
            "table_id": {
                "type": "string",
                "description": "Fully qualified ID of the table to get information about",
            }
        },
        "required": [
            "table_id",
        ],
    },
)

sql_query_func = FunctionDeclaration(
    name="sql_query",
    description="Get information from data in BigQuery using SQL queries",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query on a single line that will help give quantitative answers to the user's question when run on a BigQuery dataset and table. In the SQL query, Always use the 'Billing_Workspace_Chatbot' dataset, 'subscription_logs' table or the provided procedures",
            }
        },
        "required": [
            "query",
        ],
    },
)

sql_query_tool = Tool(
    function_declarations=[
        list_datasets_func,
        list_tables_func,
        get_table_func,
        sql_query_func,
    ],
)

model = GenerativeModel(
    "gemini-1.5-pro-001",
    generation_config={"temperature": 0},
    tools=[sql_query_tool],
)

st.set_page_config(
    page_title="SQL Talk with BigQuery",
    page_icon="vertex-ai.png",
    layout="wide",
)

col1, col2 = st.columns([8, 1])
with col1:
    st.title("Billing App Demo")
# with col2:
#     st.image("vertex-ai.png")

st.subheader("Using BigQuery")

# st.markdown(
#     "[Source Code](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/function-calling/sql-talk-app/)   •   [Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/multimodal/function-calling)   •   [Codelab](https://codelabs.developers.google.com/codelabs/gemini-function-calling)   •   [Sample Notebook](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/function-calling/intro_function_calling.ipynb)"
# )
if st.button("Reset Chat History"):
    st.session_state.messages = []
    st.experimental_rerun()  # Rerun the app to reset the chat display

if "messages" not in st.session_state:
    st.session_state.messages = []
## modif
def get_conversation_history():
    """Combine all messages into a single string for context."""
    conversation_history = ""
    for message in st.session_state.messages:
        conversation_history += f"{message['role']}: {message['content']}\n"
    return conversation_history
##


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"].replace("$", "\$"))  
        try:
            with st.expander("Function calls, parameters, and responses"):
                st.markdown(message["backend_details"])
        except KeyError:
            pass

if prompt := st.chat_input("Ask here..."):
    # Append the user prompt to the session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display the user message in the chat
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        chat = model.start_chat(response_validation=False)
        client = bigquery.Client()

        # Build the prompt with conversation history
        conversation_history = get_conversation_history()
        prompt_with_history = (
        conversation_history +
        f"User: {prompt}\n"
        """
                Welcome to the AI Assistant!
                
                This is a template for building a project-specific AI assistant. 
                You can customize the logic and prompts to suit your project's requirements. 
                Make sure to provide clear instructions for how the assistant should behave.
                
                For example:
                - Define your project's use case (e.g., query a database, provide recommendations).
                - Specify any datasets, APIs, or procedures the assistant should interact with.
                - Include user-friendly responses tailored to your application.
                
                Happy coding!
        """
    )


        response = chat.send_message(prompt_with_history) # Send the prompt with history to the model
        if len(response.candidates) > 0 and len(response.candidates[0].content.parts) > 0:
            response = response.candidates[0].content.parts[0]
        else:
            st.error("No valid response received from the model. Please try again.")
            # Optionally print the raw response for debugging
            # st.write(response)


        print(response)

        api_requests_and_responses = []
        backend_details = ""

        function_calling_in_process = True
        while function_calling_in_process:
            try:
                params = {}
                for key, value in response.function_call.args.items():
                    params[key] = value

                print(response.function_call.name)
                print(params)

                if response.function_call.name == "list_datasets":
                    api_response = client.list_datasets()
                    api_response = BIGQUERY_DATASET_ID
                    api_requests_and_responses.append(
                        [response.function_call.name, params, api_response]
                    )

                if response.function_call.name == "list_tables":
                    dataset_id = params["dataset_id"]
                    api_response = client.list_tables(dataset_id)
                    api_response = str([table.table_id for table in api_response])
                    api_requests_and_responses.append(
                        [response.function_call.name, params, api_response]
                    )

                if response.function_call.name == "get_table":
                    api_response = client.get_table(params["table_id"])
                    api_response = api_response.to_api_repr()
                    api_requests_and_responses.append(
                        [
                            response.function_call.name,
                            params,
                            [
                                str(api_response.get("description", "")),
                                str(
                                    [
                                        column["name"]
                                        for column in api_response["schema"]["fields"]
                                    ]
                                ),
                            ],
                        ]
                    )
                    api_response = str(api_response)

                if response.function_call.name == "sql_query":
                    job_config = bigquery.QueryJobConfig(maximum_bytes_billed=200000000)
                    try:
                        cleaned_query = (
                            params["query"]
                            .replace("\\n", " ")
                            .replace("\n", "")
                            .replace("\\", "")
                        )
                        query_job = client.query(cleaned_query, job_config=job_config)
                        api_response = query_job.result()
                        rows = [dict(row) for row in api_response]

                        # Convert API response data to CSV format
                        df = pd.DataFrame(rows)
                        csv_buffer = StringIO()
                        df.to_csv(csv_buffer, index=False)
                        csv_data = csv_buffer.getvalue()
                        csv_buffer.close()

                        api_response = csv_data
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                        )
                    except Exception as e:
                        api_response = f"Error: {str(e)}"
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                        )

                print(api_response)

                response = chat.send_message(
                    Part.from_function_response(
                        name=response.function_call.name,
                        response={
                            "content": api_response,
                        },
                    ),
                )
                response = response.candidates[0].content.parts[0]

                backend_details += "- Function call:\n"
                backend_details += (
                    "   - Function name: ```"
                    + str(api_requests_and_responses[-1][0])
                    + "```"
                )
                backend_details += "\n\n"
                backend_details += (
                    "   - Function parameters: ```"
                    + str(api_requests_and_responses[-1][1])
                    + "```"
                )
                backend_details += "\n\n"
                backend_details += (
                    "   - API response: ```"
                    + str(api_requests_and_responses[-1][2])
                    + "```"
                )
                backend_details += "\n\n"
                with message_placeholder.container():
                    st.markdown(backend_details)

            except AttributeError:
                function_calling_in_process = False

        time.sleep(3)

        full_response = response.text
        with message_placeholder.container():
            st.markdown(full_response.replace("$", "\$"))  # noqa: W605
            with st.expander("Function calls, parameters, and responses:"):
                st.markdown(backend_details)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": full_response,
                "backend_details": backend_details,
            }
        )
        #CSV download option
        if 'csv_data' in locals():
            st.download_button(
                    label="Download full data as CSV",
                    data=csv_data,
                    file_name='query_results.csv',
                    mime='text/csv'
            )




# import os
# import streamlit as st
# from requests_oauthlib import OAuth2Session
# import json

# # Define OAuth parameters
# client_id = "YOUR_GOOGLE_CLIENT_ID"
# client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
# redirect_uri = "https://my-streamlit-app-1067806797832.us-central1.run.app"
# authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
# token_url = 'https://accounts.google.com/o/oauth2/token'
# scope = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']

# # Initialize session for OAuth
# oauth = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)

# # Function to check if user is logged in
# def is_logged_in():
#     if 'oauth_token' not in st.session_state:
#         return False
#     return True

# # Function to fetch user's profile info
# def fetch_user_info(token):
#     userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
#     oauth = OAuth2Session(client_id, token=token)
#     user_info = oauth.get(userinfo_url).json()
#     return user_info

# # Authentication handling
# def authenticate_user():
#     if not is_logged_in():
#         # Step 1: User is redirected to Google's login page
#         authorization_url, state = oauth.authorization_url(authorization_base_url, access_type="offline", prompt="consent")
#         st.write(f"Please go to this URL for login: [Google Login]({authorization_url})")
        
#         # Step 2: After redirect, extract the code from the URL
#         code = st.experimental_get_query_params().get('code', None)
        
#         if code:
#             # Step 3: Exchange authorization code for a token
#             token = oauth.fetch_token(token_url, client_secret=client_secret, code=code)
            
#             # Save the token in the session state
#             st.session_state['oauth_token'] = token
            
#             # Fetch user info
#             user_info = fetch_user_info(token)
            
#             # Step 4: Restrict access to users from premiercloud.com
#             email_domain = user_info['email'].split('@')[-1]
#             if email_domain != 'premiercloud.com':
#                 st.error("Unauthorized: You must use a premiercloud.com email.")
#                 st.stop()
#             else:
#                 st.success(f"Welcome, {user_info['email']}!")
#                 # Store user info for later use
#                 st.session_state['user_info'] = user_info



# # OAuth handling before rendering the main app
# if is_logged_in():
#     user_info = st.session_state['user_info']
#     st.sidebar.success(f"Logged in as: {user_info['email']}")
#     main_app()
# else:
#     authenticate_user()

