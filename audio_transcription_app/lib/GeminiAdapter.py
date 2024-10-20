import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# Configure API key
# os.environ["API_KEY"] = "your_api_key_here"  # Replace with your actual API key

# Configure the generative AI model
load_dotenv()
genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# Define your text and prompt
# conversation_text = """
# During our meeting, we discussed several key topics. Alice mentioned that the authentication module needs to be updated to fix login issues. Bob agreed and said he would refactor the database connection code to improve performance. Charlie volunteered to start drafting the introduction section for the documentation tomorrow. Additionally, we need to implement a new feature for user profile management.
# """
def generate_summary_and_json(conversation_text):
    prompt = f"""
    Summarize the following conversation and extract programming tasks and make sure each has a good description of what is expected and dicussed:

    Title: [Provide a concise title summarizing the main topic]
    Main Points:
    - [List each main point discussed in bullet form]
    Action Items:
    - [List any action items or tasks assigned and descirbe what is expected for the Item] [Priority, use default as low]
    Programming Tasks:
    - [Identify and list any programming-related tasks mentioned with what is described from the whole conversation]

    Conversation: {conversation_text}
    """

    # Generate content using the model
    response = model.generate_content(prompt)

    # Example response parsing (assuming response.text is structured as expected)
    response_text = response.text

    prompt2=f"""
    From the summary create a json structure with Action Items and programming tasks and priority and assignee if any so that I can consume. Give Issue with what to be done, description of issue, Priority and assignee for each programming task and action item.
    Make sure they have a description key which has a detailed description of the tasks. 

    I need the response in a format that I can convert into json with just json.loads from python. give it inside curly brackets. Use key for Action Items as action_items and Programming Task as programming_tasks and lowercase for all other keys.

    Summary: {response_text}
    """

    # Split the response text into sections based on headers
    response1 = model.generate_content(prompt2)
    response1 = response1.text
    first_brace_position = response1.find('{')
    last_brace_position = response1.rfind('}')
    extracted_string = response1[first_brace_position:last_brace_position + 1]

    return response_text, extracted_string


def jsonify_string(extracted_issues_data):
    query = json.loads(extracted_issues_data)
    return query

def get_output(query):
    output = []
    for item in query['action_items']:
        output.append({
            'type': 'action_item',
            'description': item['description'],
            'priority': item['priority'],
            'assignee': item['assignee'],
            'issue': item['issue']
        })

    for task in query['programming_tasks']:
        output.append({
            'type': 'programming_task',
            'description': task['description'],
            'priority': task['priority'],
            'assignee': task['assignee'],
            'issue': task['issue']
        })
    return output

def get_email_summary_and_jira_action_items(conversation_text):
    summary,extracted_issues_data = generate_summary_and_json(conversation_text)
    query = jsonify_string(extracted_issues_data)
    output = get_output(query)
    return summary, output
