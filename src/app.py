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



from flask import Flask, request, jsonify, send_file,url_for
from flask_cors import CORS
import re
from groq import Groq
import json
import pymysql
import time
from fpdf import FPDF
import os
from io import BytesIO
import uuid

app = Flask(__name__)
CORS(app)


# In-memory store for PDF files
pdf_store = {}

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Bus Booking Ticket', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def passenger_details(self, booking_details):
        self.set_font('Arial', '', 12)
        for key, value in booking_details.items():
            self.cell(0, 10, f'{key}: {value}', 0, 1)


def create_ticket_pdf(booking_details):
    pdf = PDF()
    pdf.add_page()
    pdf.passenger_details(booking_details)

    pdf_stream = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_stream.write(pdf_output)
    pdf_stream.seek(0)
    return pdf_stream


list_to_be_asked = ["name", "phone#", "arrival city", "departure city", "date", "time","gender"]

client = Groq(
    api_key="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",
)

MYSQL_HOST = "mysql-3f45e23a-wasamkhann-65e7.c.aivencloud.com"
MYSQL_PORT = 21270
MYSQL_USERNAME = "avnadmin"
MYSQL_PASSWORD = "AVNS_dvBv9kmy0rprIpyKSUY"

# Function definitions
def list_updater(output_dict, list_to_be_asked):
    if not output_dict:
        return list_to_be_asked

    keys = list(output_dict.keys())
    
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
    
    # Replace 'null' with 'None' to make it a valid Python dictionary
    joined_string = ''.join(cleaned_matches)
    data = json.loads('{' + joined_string + '}')

# Remove keys with null values
    filtered_data = {k: v for k, v in data.items() if v is not None}

    
    return filtered_data

def list_to_dict(input_array):

    # Convert the array into a single string
    input_str = ', '.join(input_array)
    print(input_str)

    # Convert the string to a dictionary
    data_dict = {}
    items = input_str.split(',')
    for item in items:
        key, value = item.split(': ')
        key = key.strip(' "')
        value = value.strip(' "')
        if value == 'null':
            value = None
        data_dict[key] = value
    
    return data_dict

def update_database(MYSQL_HOST,MYSQL_PASSWORD,MYSQL_PORT,MYSQL_USERNAME,data_dict,retries=3):

    timeout = 30
    while retries > 0:
        try:
            connection = pymysql.connect(
                charset="utf8mb4",
                connect_timeout=timeout,
                cursorclass=pymysql.cursors.DictCursor,
                db="defaultdb",
                host=MYSQL_HOST,
                password=MYSQL_PASSWORD,
                read_timeout=timeout,
                port=MYSQL_PORT,
                user=MYSQL_USERNAME,
                write_timeout=timeout,
            )

            
            cursor = connection.cursor()
            
            # Create table if it doesn't exist
            create_table_query = """
            CREATE TABLE IF NOT EXISTS busbooking (
                SEAT_NO INT AUTO_INCREMENT PRIMARY KEY,
                DepartureCity VARCHAR(255),
                ArrivalCity VARCHAR(255),
                Name VARCHAR(255),
                Mobile VARCHAR(255),
                BookingDate VARCHAR(255),
                BookingTime VARCHAR(255),
                Gender VARCHAR(255)
            )
            """
            cursor.execute(create_table_query)
            
            # Insert data into the table
            insert_query = """
            INSERT INTO busbooking (DepartureCity,ArrivalCity,Name,Mobile,BookingDate,BookingTime,Gender)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (data_dict['departure city'], data_dict['arrival city'], data_dict['name'], data_dict['phone#'], data_dict['date'], data_dict['time'], data_dict['gender']))
            
            # Commit the transaction
            connection.commit()

            # Get the generated SEAT_NO
            seat_no = cursor.lastrowid

            print("Updated Successfully...")

            return seat_no  
            
        
        except pymysql.err.OperationalError as e:
            print(f"OperationalError: {e}")
            retries -= 1
            print(f"Retrying... ({retries} attempts left)")
            time.sleep(5)  # Wait for 5 seconds before retrying

        finally:
            connection.close()
    


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
        print(attributes)
        attributes = str(attributes)


        output_list = extract_text_from_query(attributes)
        print("\n",output_list)
        
        chat_state['output_array'].update(output_list)
        input_list = list_updater(output_list, chat_state['list_to_be_asked'])

        if not input_list:
            file_path = './data.json'

            # Writing data to JSON file
            with open(file_path, 'w') as file:
                json.dump(chat_state['output_array'], file, indent=4)
                print("FINAL DICTIONARY : ",chat_state['output_array'])
                # print(chat_state['output_array'])
                booking_obj = chat_state['output_array']
                
                #print("FINAL DICT : ",booking_obj)
                seat_no = update_database(MYSQL_HOST,MYSQL_PASSWORD,MYSQL_PORT,MYSQL_USERNAME,booking_obj)
                if(seat_no):

                    booking_obj['seat_no'] = seat_no

                    # Create PDF ticket
                    pdf_file = create_ticket_pdf(booking_obj)

                    # Generate unique identifier
                    ticket_id = str(uuid.uuid4())
                    pdf_store[ticket_id] = pdf_file  # Store the PDF in memory
                    print(pdf_store[ticket_id])

                    # send_file(pdf_filepath, as_attachment=True, download_name='ticket.pdf')
                    # Return JSON response with the PDF URL and status message
                    return (jsonify({"status": "completed", "message": "Thank you for providing all the information your seat has been booked!", "ticket_id": ticket_id}))

                else:   
                    return jsonify({"status": "failed", "message": "Booking Failed!!. Kindly Try Again Later"})
            
            # return jsonify({"status": "completed", "message": "Thank you for providing all the information your seat has been booked!"})

            
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
    

@app.route('/download_ticket/<ticket_id>')
def download_ticket(ticket_id):
    pdf_stream = pdf_store.get(ticket_id)
    if pdf_stream:
        return send_file(
            pdf_stream,
            as_attachment=True,
            download_name='ticket.pdf',
            mimetype='application/pdf'
        )
    else:
        return jsonify({"status": "failed", "message": "File not found!"}), 404

if __name__ == '__main__':
    app.run(debug=True)
