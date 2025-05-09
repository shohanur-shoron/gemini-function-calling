from google import genai
from google.genai import types


API_KEY = 'YOUR_API_KEY'

EMAIL_TYPE = ["congratulatory", "reminder", "promotion", "otp", "welcome", "transactional"]
USER_TYPE = ["new_users", "old_users", "most_commenting_users", "most_liking_users", "most_profile_viewing_users"]


def schedule_meeting(attendees, date, time, topic):
    print('-'*70)
    print("Function: schedule_meeting")
    print("Arguments:")
    if attendees is not None:
        print(f"  - attendees: {attendees}")
    if date is not None:
        print(f"  - date: {date}")
    if time is not None:
        print(f"  - time: {time}")
    if topic is not None:
        print(f"  - topic: {topic}")
    print('-'*70)


def email_user(email_type, user_type):
    print('-'*70)
    print("Function: email_user")
    print("Arguments:")
    if email_type is not None:
        print(f"  - email_type: {email_type}")
    if user_type is not None:
        print(f"  - user_type: {user_type}")
    print('-'*70)


ALL_FUNCTIONS = {
    'schedule_meeting': schedule_meeting,
    'email_user': email_user,
}


def call_a_function(function_name, args):
    try:
        function_to_call = ALL_FUNCTIONS[function_name]
        function_to_call(**args)

        text_to_format = (
            f"Generate a short, friendly confirmation for a successful call to “{function_name}” "
            f"using only the values in {args}. "
            f"Include “successfully” (or similar) but skip all parameter names. "
            f"Example  for Function call: schedule_meeting  \n"
            f"Arguments: {{'time':'10:00','attendees':['Bob','Alice'],'topic':'Q3 planning','date':'2025-03-14'}}:  \n"
            f"'Successfully scheduled your Q3 planning meeting on 2025-03-14 at 10:00 with Bob and Alice! 😊'\n"
            f"Now format: {args}"
        )

        response_text = formate_message(text_to_format)
        
        print(f"Simulated Tool Response: {response_text}")

    except:
        print('Function call failed')


schedule_meeting_function_decl = types.FunctionDeclaration(
    name="schedule_meeting",
    description="Schedules a meeting with specified attendees at a given time and date.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "attendees": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "List of people attending the meeting.",
            },
            "date": {
                "type": "STRING",
                "description": "Date of the meeting (e.g., 'YYYY-MM-DD')",
            },
            "time": {
                "type": "STRING",
                "description": "Time of the meeting (e.g., 'HH:MM')",
            },
            "topic": {
                "type": "STRING",
                "description": "The subject or topic of the meeting.",
            },
        },
        "required": ["attendees", "date", "time", "topic"],
    },
)

email_user_function_decl = types.FunctionDeclaration(
    name="email_user",
    description="Sends an email of a specific type to a defined group of users.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "email_type": {
                "type": "STRING",
                "description": "The type of email content to send.",
                "enum": EMAIL_TYPE
            },
            "user_type": {
                "type": "STRING",
                "description": "The category or segment of users to send the email to.",
                "enum": USER_TYPE
            }
        },
        "required": [
            "email_type",
            "user_type"
        ]
    }
)

weather_function_decl = {
    "name": "get_current_temperature",
    "description": "Gets the current temperature for a given location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city name, e.g. San Francisco",
            },
        },
        "required": ["location"],
    },
}

create_chart_function_decl = {
    "name": "create_bar_chart",
    "description": "Creates a bar chart given a title, labels, and corresponding values.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title for the chart.",
            },
            "labels": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of labels for the data points (e.g., ['Q1', 'Q2', 'Q3']).",
            },
            "values": {
                "type": "array",
                "items": {"type": "number"},
                "description": "List of numerical values corresponding to the labels (e.g., [50000, 75000, 60000]).",
            },
        },
        "required": ["title", "labels", "values"],
    },
}

system_instruction = """You are a helpful and friendly assistant.
You have the ability to schedule meetings and send emails and others using the provided tools.
Use the tools only when the user explicitly asks you to perform one of those actions.
If user ask you to use multiple tool at once send responce that you can use only one tool at a time.
For all other questions, provide helpful and informative responses based on your general knowledge.
Do not refuse to answer general questions by stating your purpose is limited to tools."""

TOOLS = [
    schedule_meeting_function_decl, 
    email_user_function_decl,
    weather_function_decl,
    create_chart_function_decl,
]

client = genai.Client(api_key=API_KEY)
available_tools = types.Tool(function_declarations=TOOLS)
config = types.GenerateContentConfig(tools=[available_tools], system_instruction=system_instruction)

chat = client.chats.create(
    model="gemini-2.0-flash",
    config=config,
)


def formate_message(input_text: str) -> str:
    try:
        client = genai.Client(api_key=API_KEY)

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=[input_text],
            config=types.GenerateContentConfig(
                max_output_tokens=500,
                temperature=1
            )
        )

        return response.text

    except Exception as e:
        print(f"ERROR during formatting model communication: {e}")
        return f"[Formatting error: Communication failed - {e}]"
    

while True:
    message1 = input('User: ')

    if message1.lower() == 'quit':
        break

    response1 = chat.send_message(message1)

    # Check if the response is valid and contains content parts
    if response1.candidates and response1.candidates[0].content and response1.candidates[0].content.parts:
        part1 = response1.candidates[0].content.parts[0]

        # Check if the model requested a function call
        if part1.function_call:
            print(f"Function call: {part1.function_call.name}")
            print(f"Arguments: {part1.function_call.args}")

            call_a_function(function_name=part1.function_call.name, args=part1.function_call.args)

        elif part1.text:
            print(f"Model Response: {part1.text}")

        # Handle other potential part types if needed
        else:
            print("Model returned an unexpected part type.")
    else:
        print("Model response did not contain expected content parts.")