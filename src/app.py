# from flask import Flask, request, jsonify, session
# from flask_cors import CORS
# from flask_session import Session
# import re
# from groq import Groq
# import secrets
# import os

# app = Flask(__name__)

# secret_key = secrets.token_hex(24)
# app.secret_key = secret_key  # Required for session management


# # Configure session to use filesystem (server-side session)
# # Configure session to use filesystem (server-side session)
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config['SESSION_FILE_DIR'] = './flask_session'
# app.config['SESSION_PERMANENT'] = True  # Sessions will not be permanent
# app.config['SESSION_USE_SIGNER'] = True   # Use a signer for the session cookie
# app.config['SESSION_KEY_PREFIX'] = 'myapp_' 

# # app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
# Session(app)
# CORS(app)
# list_to_be_asked = ["name", "phone#", "arrival city", "departure city", "date", "time"]



# client = Groq(
#     api_key="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",
# )


# # Function definitions
# def list_updater(output_array, list_to_be_asked):
#     if not output_array:
#         return list_to_be_asked
    
#     keys = []
#     for item in output_array:
#         cleaned_item = item.replace('"', '').replace(' ', '').split(',')
#         for pair in cleaned_item:
#             key = pair.split(':')[0]
#             keys.append(key)
    
#     normalized_keys = [key.lower().replace(' ', '') for key in keys]
#     normalized_list = [item.lower().replace(' ', '') for item in list_to_be_asked]
#     filtered_list = [item for item in list_to_be_asked if item.lower().replace(' ', '') not in normalized_keys]

#     return filtered_list

# def get_chatbot_response(client, list_to_be_asked):
#     chat_completion = client.chat.completions.create(
#         messages=[
#             {
#                 "role": "user",
#                 "content": f"You will act like a chatbot for bus seat reservation only no other things just ask him about one of the things at a time the user detail to ask: {list_to_be_asked}. \
#                     Ask 1 question at a time single line answer."
#             }
#         ],
#         model="llama3-8b-8192",
#     )
#     return chat_completion.choices[0].message.content

# def attribut(client, question, response):
#     chat_completion = client.chat.completions.create(
#         messages=[
#             {
#                 "role": "user",
#                 "content": f"[departure city, arrival city, name, date, time, gender, phone#] is the list of attributes that you have to find from the text \
#                     if they are present in the text. \
#                         I am going to provide you the question now: {question}. \
#                             Extract the desired result from the following answer of the above question: {response}. \
#                                 The answer can be of one word so keep in mind the question to look for which field to fill. \
#                                     Return a json file format of the fields only present do not write the null field. \
#                                     Only the file make sure to keep the attribute name same as the provided in the list."
#             },
#         ],
#         model="llama3-8b-8192",
#     )
#     return chat_completion.choices[0].message.content

# def extract_text_from_query(query):
#     combined_text = ''.join(query)
#     matches = re.findall(r'\{(.*?)\}', combined_text, re.DOTALL)
#     cleaned_matches = [match.replace('\n', '').strip() for match in matches]
#     return cleaned_matches

# @app.route('/chat', methods=['POST'])
# def chat():
#     # print(session)
#     if 'chat_state' not in session:
        
#         print('Initialize chat state')
#         session['chat_state'] = {
#             'output_array': [],
#             'list_to_be_asked': list_to_be_asked,
#             'last_question': ''
#         }
    
#     data = request.json
#     response = data.get('response')

#     if response is not None:
#         # Continue chat
#         question = session['chat_state'].get('last_question', '')
#         print(question)
#         if not question:  # Handle case where last_question is empty
#             output_array = session['chat_state']['output_array']
#             input_list = list_updater(output_array, session['chat_state']['list_to_be_asked'])
#             question = get_chatbot_response(client, input_list)
#             session['chat_state']['last_question'] = question
#             session.modified = True  # Mark session as modified
#             return jsonify({"next_question": question})

#         attributes = attribut(client, question, response)
#         attributes = str(attributes)
        
#         output_list = extract_text_from_query(attributes)
#         session['chat_state']['output_array'].extend(output_list)
#         input_list = list_updater(output_list, session['chat_state']['list_to_be_asked'])
        
#         if not input_list:
#             session.modified = True  # Mark session as modified
#             return jsonify({"status": "completed", "message": "Thank you for providing all the information!"})
        
#         next_question = get_chatbot_response(client, input_list)
#         session['chat_state']['list_to_be_asked'] = input_list
#         session['chat_state']['last_question'] = next_question
#         session.modified = True  # Mark session as modified
#         return jsonify({"next_question": next_question})
    
#     else:
#         # Start chat
#         output_array = session['chat_state']['output_array']
#         input_list = list_updater(output_array, session['chat_state']['list_to_be_asked'])
#         question = get_chatbot_response(client, input_list)
#         session['chat_state']['last_question'] = question
#         session.modified = True  # Mark session as modified
#         return jsonify({"next_question": question})
    
    
    
# if __name__ == '__main__':
#     app.run(debug=True)



from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from groq import Groq
import secrets
import json
app = Flask(__name__)
CORS(app)

list_to_be_asked = ["name", "phone#", "arrival city", "departure city", "date", "time"]

client = Groq(
    api_key="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",
)

# Function definitions
def list_updater(output_array, list_to_be_asked):
    if not output_array:
        return list_to_be_asked

    keys = []
    for item in output_array:
        cleaned_item = item.replace('"', '').replace(' ', '').split(',')
        for pair in cleaned_item:
            key = pair.split(':')[0]
            keys.append(key)

    normalized_keys = [key.lower().replace(' ', '') for key in keys]
    normalized_list = [item.lower().replace(' ', '') for item in list_to_be_asked]
    filtered_list = [item for item in list_to_be_asked if item.lower().replace(' ', '') not in normalized_keys]

    return filtered_list

def get_chatbot_response(client, list_to_be_asked):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"You will act like a chatbot for bus seat reservation only no other things just ask him about one of the things at a time the user detail to ask: {list_to_be_asked}. \
                    Ask 1 question at a time single line answer."
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def attribut(client, question, response):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"[departure city, arrival city, name, date, time, gender, phone#] is the list of attributes that you have to find from the text \
                    if they are present in the text. \
                        I am going to provide you the question now: {question}. \
                            Extract the desired result from the following answer of the above question: {response}. \
                                The answer can be of one word so keep in mind the question to look for which field to fill. \
                                    Return a json file format of the fields only present do not write the null field. \
                                    Only the file make sure to keep the attribute name same as the provided in the list."
            },
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def extract_text_from_query(query):
    combined_text = ''.join(query)
    matches = re.findall(r'\{(.*?)\}', combined_text, re.DOTALL)
    cleaned_matches = [match.replace('\n', '').strip() for match in matches]
    return cleaned_matches

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    response = data.get('response')
    chat_state = data.get('chat_state')
    print(chat_state)

    if response is not None:
        question = chat_state.get('last_question', '')
        print(question)
        if not question:
            output_array = chat_state['output_array']
            input_list = list_updater(output_array, chat_state['list_to_be_asked'])
            question = get_chatbot_response(client, input_list)
            chat_state['last_question'] = question
            print(chat_state)
            return jsonify({"next_question": question, "chat_state": chat_state})

        attributes = attribut(client, question, response)
        attributes = str(attributes)

        output_list = extract_text_from_query(attributes)
        chat_state['output_array'].extend(output_list)
        input_list = list_updater(output_list, chat_state['list_to_be_asked'])

        if not input_list:
            file_path = './data.json'

            # Writing data to JSON file
            with open(file_path, 'w') as file:
                json.dump(chat_state['output_array'], file, indent=4)
            return jsonify({"status": "completed", "message": "Thank you for providing all the information your seat has been booked!"})

        next_question = get_chatbot_response(client, input_list)
        chat_state['list_to_be_asked'] = input_list
        chat_state['last_question'] = next_question
        return jsonify({"next_question": next_question, "chat_state": chat_state})
    
    else:
        output_array = chat_state['output_array']
        input_list = list_updater(output_array, chat_state['list_to_be_asked'])
        question = get_chatbot_response(client, input_list)
        chat_state['last_question'] = question
        return jsonify({"next_question": question, "chat_state": chat_state})

if __name__ == '__main__':
    app.run(debug=True)