## Gemini Function Calling Demo Script Documentation

**Version:** 1.0

![image](https://github.com/user-attachments/assets/ff35d50a-fc74-47b8-9b2a-61df8894e9aa)


### 1. Overview

This Python script demonstrates how to use Google's Gemini AI models with function calling capabilities. It sets up a chat interface where a user can interact with a Gemini model. The model can understand when the user's request requires executing a predefined function (a "tool"). If so, the model will request to call that function with specific arguments. The script then simulates the execution of this function and uses another Gemini model call to generate a user-friendly confirmation message.

The script includes examples for:
1.  Scheduling a meeting (`schedule_meeting`)
2.  Sending an email to users (`email_user`)
3.  Getting current temperature (declaration only: `get_current_temperature`)
4.  Creating a bar chart (declaration only: `create_bar_chart`)

It showcases how to:
*   Define functions in Python.
*   Declare these functions for the Gemini model using `types.FunctionDeclaration` or dictionary format.
*   Configure a Gemini chat client with these tools and system instructions.
*   Handle responses from the model, distinguishing between text answers and function call requests.
*   Execute the requested function locally.
*   Generate a natural language confirmation of the function call.

### 2. Prerequisites

*   **Python 3.9+**
*   **Google Generative AI SDK:** `google-generativeai`
*   **Google Cloud Project & API Key:** You need a Google Cloud Project with the Generative Language API enabled. You'll also need an API key associated with this project.

### 3. Setup

1.  **Install the SDK:**
    ```bash
    pip install google-genai
    ```

2.  **Set your API Key:**
    Open the `function.py` file and replace the placeholder API key:
    ```python
    API_KEY = 'YOUR_GEMINI_API_KEY'
    ```
    **Security Note:** For production applications, it's highly recommended to manage API keys securely, for example, using environment variables or a secrets manager, rather than hardcoding them.

### 4. How the Script Works (Workflow)

1.  **Initialization:**
    *   The script defines Python functions (`schedule_meeting`, `email_user`) that simulate real-world actions.
    *   It creates "Function Declarations" (`schedule_meeting_function_decl`, etc.) which describe these Python functions to the Gemini model (name, description, parameters, required parameters, enums for parameters).
    *   A Gemini client (`genai.Client`) is initialized with your API key.
    *   A chat session (`client.chats.create`) is started with the `gemini-2.0-flash` model. This chat is configured with:
        *   `tools`: The list of declared functions the model can use.
        *   `system_instruction`: A prompt guiding the model's behavior, especially regarding when and how to use tools.

2.  **User Interaction Loop:**
    *   The script enters an infinite loop, prompting the user for input.
    *   The user's message is sent to the Gemini chat session (`chat.send_message(message1)`).

3.  **Model Response Processing:**
    *   The model processes the user's message. Based on its understanding and the `system_instruction`, it decides:
        *   **If a tool should be used:** The model's response will contain a `function_call` object. This object includes the `name` of the function to call and the `args` (arguments) for that function, extracted from the user's query.
        *   **If no tool is needed:** The model's response will contain `text` – a direct textual answer to the user's query.

4.  **Function Call Execution (if requested):**
    *   If a `function_call` is present:
        *   The script prints the function name and arguments.
        *   It calls the `call_a_function` utility.
        *   `call_a_function` looks up the actual Python function in the `ALL_FUNCTIONS` dictionary and executes it with the provided arguments.
        *   The Python functions (`schedule_meeting`, `email_user`) in this demo simply print their arguments to simulate execution.
        *   After simulated execution, `call_a_function` constructs a prompt for *another* Gemini model (`gemini-2.0-flash-lite` via `formate_message`). This prompt asks the model to generate a short, friendly confirmation message based on the function called and its arguments.
        *   The generated confirmation is printed as "Simulated Tool Response."

5.  **Text Response (if no function call):**
    *   If the model returns `text`, it's printed directly as "Model Response."

6.  **Loop or Quit:**
    *   The loop continues until the user types "quit".

### 5. Detailed Code Breakdown

#### 5.1. Imports
```python
from google import genai
from google.genai import types
```
*   `google.genai`: The main library for interacting with Google's Generative AI services.
*   `google.genai.types`: Contains specific data types used by the library, like `FunctionDeclaration`, `Tool`, `GenerateContentConfig`.

#### 5.2. Global Variables
```python
API_KEY = 'YOUR_GEMINI_API_KEY'
```
*   Your Google Generative AI API key. **Remember to replace the placeholder!**

```python
EMAIL_TYPE = ["congratulatory", "reminder", "promotion", "otp", "welcome", "transactional"]
USER_TYPE = ["new_users", "old_users", "most_commenting_users", "most_liking_users", "most_profile_viewing_users"]
```
*   These lists define allowed enumerated values for the `email_type` and `user_type` parameters of the `email_user` function. They are used in the `email_user_function_decl`.

#### 5.3. Simulated Python Functions
These are the actual Python functions that get executed when the Gemini model requests a tool use. In a real application, these would perform actual tasks (e.g., interacting with a calendar API or an email service).

```python
def schedule_meeting(attendees, date, time, topic):
    # ... prints arguments ...

def email_user(email_type, user_type):
    # ... prints arguments ...
```
*   They currently only print the arguments they receive for demonstration purposes.

```python
ALL_FUNCTIONS = {
    'schedule_meeting': schedule_meeting,
    'email_user': email_user,
}
```
*   A dictionary mapping function names (as known by the Gemini model) to their actual Python function implementations. This is used by `call_a_function` to dispatch the call.
*   **Note:** `get_current_temperature` and `create_bar_chart` are declared to the model but don't have corresponding Python functions in `ALL_FUNCTIONS`. If the model tried to call them, `call_a_function` would fail (as currently written without specific error handling for missing keys).

#### 5.4. `call_a_function(function_name, args)`
```python
def call_a_function(function_name, args):
    try:
        function_to_call = ALL_FUNCTIONS[function_name]
        function_to_call(**args) # Executes the local Python function

        # Prompt engineering for the confirmation message
        text_to_format = (
            f"Generate a short, friendly confirmation for a successful call to “{function_name}” "
            f"using only the values in {args}. "
            f"Include “successfully” (or similar) but skip all parameter names. "
            f"Example  for Function call: schedule_meeting  \n"
            f"Arguments: {{'time':'10:00','attendees':['Bob','Alice'],'topic':'Q3 planning','date':'2025-03-14'}}:  \n"
            f"'Successfully scheduled your Q3 planning meeting on 2025-03-14 at 10:00 with Bob and Alice! 😊'\n"
            f"Now format: {args}"
        )

        response_text = formate_message(text_to_format) # Gets the formatted confirmation
        print(f"Simulated Tool Response: {response_text}")

    except Exception as e: # Basic error handling
        print(f'Function call failed: {e}') # Modified to show the error
```
*   This function is the bridge between the Gemini model's request and the local Python code.
*   It looks up the `function_name` in `ALL_FUNCTIONS` and calls it using `**args` to unpack the arguments.
*   Crucially, it then crafts a detailed prompt to `formate_message`. This prompt instructs another LLM to generate a user-friendly confirmation message based *only* on the provided arguments, mimicking how a real API might return a success message. The example within the prompt is key for few-shot learning.

#### 5.5. Function Declarations for Gemini
These declarations describe your Python functions to the Gemini model so it knows what tools are available, what they do, and what parameters they expect.

```python
schedule_meeting_function_decl = types.FunctionDeclaration(...)
email_user_function_decl = types.FunctionDeclaration(...)
```
*   Uses `types.FunctionDeclaration` for a structured way to define tools.
    *   `name`: The name the model will use to refer to the function.
    *   `description`: A natural language description of what the function does. This helps the model decide when to use it.
    *   `parameters`: A schema (JSON schema like) defining the expected arguments.
        *   `type: "OBJECT"`: Indicates parameters are a collection of key-value pairs.
        *   `properties`: Defines each parameter (e.g., `attendees`, `date`).
            *   `type`: Data type (STRING, ARRAY, NUMBER, etc.).
            *   `items`: For ARRAY type, defines the type of items in the array.
            *   `description`: Explains the parameter to the model.
            *   `enum`: (For `email_user_function_decl`) A list of allowed string values for the parameter.
        *   `required`: A list of parameter names that are mandatory.

```python
weather_function_decl = { ... }
create_chart_function_decl = { ... }
```
*   These demonstrate that function declarations can also be provided as Python dictionaries following the same schema. This can be more concise for simpler declarations.

#### 5.6. System Instruction
```python
system_instruction = """You are a helpful and friendly assistant.
# ... (rest of the instruction) ...
Do not refuse to answer general questions by stating your purpose is limited to tools."""
```
*   This is a critical prompt given to the Gemini model at the start of the chat session. It guides the model's overall behavior, persona, and specifically how it should approach using the provided tools.
*   Key points:
    *   Use tools only when explicitly asked.
    *   Handle only one tool at a time if multiple are requested.
    *   Answer general questions normally.

#### 5.7. Tool Configuration and Client Setup
```python
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
    model="gemini-2.0-flash", # You can experiment with other models like "gemini-pro"
    config=config,
)
```
*   `TOOLS`: A list containing all the function declarations.
*   `client`: Initializes the connection to the Gemini API.
*   `available_tools`: Wraps the `TOOLS` list into a `types.Tool` object. This is how the SDK expects the tools to be packaged.
*   `config`: A `types.GenerateContentConfig` object that bundles the `available_tools` and the `system_instruction`. This configuration is applied to the chat session.
*   `chat`: Creates a persistent chat session with the specified model (`gemini-2.0-flash`) and configuration. Messages sent to this `chat` object will maintain context (up to the model's context window limit).

#### 5.8. `formate_message(input_text: str) -> str`
```python
def formate_message(input_text: str) -> str:
    try:
        # ... (client initialization, model call) ...
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite", # Uses a lightweight model for formatting
            contents=[input_text],
            config=types.GenerateContentConfig(
                max_output_tokens=500,
                temperature=1 # Higher temperature for more creative/varied confirmations
            )
        )
        return response.text
    # ... (error handling) ...
```
*   This function is responsible for generating the user-friendly confirmation message *after* a tool (local Python function) has been called.
*   It makes a separate, non-chat API call to `gemini-2.0-flash-lite` (a fast, lightweight model suitable for tasks like summarization or formatting).
*   The `input_text` it receives is the carefully crafted prompt from `call_a_function`.
*   `temperature=1`: A higher temperature encourages more varied and creative responses for the confirmation message. For strictly deterministic formatting, a lower temperature (e.g., 0.2) might be preferred.

#### 5.9. Main Interaction Loop
```python
while True:
    message1 = input('User: ')
    if message1.lower() == 'quit':
        break

    response1 = chat.send_message(message1)

    # ... (response parsing and handling logic) ...
```
*   Prompts the user for input.
*   Sends the message to the `chat` object.
*   `response1.candidates[0].content.parts[0]`: This navigates the structure of the Gemini API response to get the relevant part.
    *   A response can have multiple `candidates`. We usually take the first one (`[0]`).
    *   A candidate's `content` can have multiple `parts`. For simple text or a single function call, we typically look at the first part (`[0]`).
*   **Conditional Logic:**
    *   `if part1.function_call:`: Checks if the model is requesting a function call. If yes, extracts `name` and `args` and passes them to `call_a_function`.
    *   `elif part1.text:`: Checks if the model returned a simple text response. If yes, prints it.
    *   `else`: Handles unexpected response structures.

### 6. How to Run and Interact

1.  **Save the code:** Ensure the code is saved as `function.py` (or adjust the run command accordingly).
2.  **Set your API Key:** (As described in Setup).
3.  **Run from the terminal:**
    ```bash
    python function.py
    ```
4.  **Interact with the prompt:**

    *   **Example 1 (Function Call - Schedule Meeting):**
        ```
        User: Schedule a meeting with Alice and Bob for next Friday at 2 PM to discuss the Q4 budget.
        ```
        Expected output flow:
        1.  `Function call: schedule_meeting`
        2.  `Arguments: {'attendees': ['Alice', 'Bob'], 'date': 'YYYY-MM-DD', 'time': '14:00', 'topic': 'Q4 budget'}` (Date will be inferred by the model)
        3.  The `schedule_meeting` function's print statements.
        4.  `Simulated Tool Response: Successfully scheduled your Q4 budget meeting on YYYY-MM-DD at 14:00 with Alice and Bob! 🎉` (or similar, generated by `formate_message`)

    *   **Example 2 (Function Call - Email User):**
        ```
        User: Send a welcome email to new users.
        ```
        Expected output flow:
        1.  `Function call: email_user`
        2.  `Arguments: {'email_type': 'welcome', 'user_type': 'new_users'}`
        3.  The `email_user` function's print statements.
        4.  `Simulated Tool Response: Successfully sent the welcome email to new users. 👍` (or similar)

    *   **Example 3 (General Question):**
        ```
        User: What is the capital of France?
        ```
        Expected output:
        ```
        Model Response: The capital of France is Paris.
        ```

    *   **Example 4 (Requesting a tool not fully implemented in Python):**
        ```
        User: What's the weather like in London?
        ```
        Expected output flow:
        1.  `Function call: get_current_temperature`
        2.  `Arguments: {'location': 'London'}`
        3.  `Function call failed: 'get_current_temperature'` (Because `get_current_temperature` is not in `ALL_FUNCTIONS`)
            *To make this work, you'd add `get_current_temperature` to `ALL_FUNCTIONS` and implement the actual Python logic.*

    *   **Example 5 (Requesting multiple tools - as per system instruction):**
        ```
        User: Schedule a meeting for tomorrow and send a promo email to old users.
        ```
        Expected output:
        ```
        Model Response: I can help with that, but I can only perform one action at a time. Would you like to schedule the meeting first, or send the promo email?
        ``` (Or similar, based on the `system_instruction`)

5.  **To Exit:** Type `quit` and press Enter.

### 7. Extending the Script (Adding New Tools)

To add a new tool (e.g., a to-do list manager):

1.  **Write the Python Function:**
    ```python
    def add_todo_item(task_description, due_date=None):
        print('-'*70)
        print("Function: add_todo_item")
        print("Arguments:")
        print(f"  - task_description: {task_description}")
        if due_date:
            print(f"  - due_date: {due_date}")
        print("This would add the task to a to-do list.")
        print('-'*70)
        # In a real app, you'd interact with a database or API here
    ```

2.  **Add to `ALL_FUNCTIONS`:**
    ```python
    ALL_FUNCTIONS = {
        'schedule_meeting': schedule_meeting,
        'email_user': email_user,
        'add_todo_item': add_todo_item, # Add the new function
    }
    ```

3.  **Create the Function Declaration:**
    ```python
    add_todo_item_function_decl = types.FunctionDeclaration(
        name="add_todo_item",
        description="Adds a new task to the user's to-do list. Can optionally include a due date.",
        parameters={
            "type": "OBJECT",
            "properties": {
                "task_description": {
                    "type": "STRING",
                    "description": "The description of the task to add.",
                },
                "due_date": {
                    "type": "STRING",
                    "description": "Optional. The due date for the task (e.g., 'YYYY-MM-DD').",
                },
            },
            "required": ["task_description"],
        },
    )
    ```

4.  **Add the Declaration to `TOOLS`:**
    ```python
    TOOLS = [
        schedule_meeting_function_decl,
        email_user_function_decl,
        weather_function_decl,
        create_chart_function_decl,
        add_todo_item_function_decl, # Add the new declaration
    ]
    ```

5.  **(Optional) Update `system_instruction`:** If the new tool has specific nuances or you want to guide the model on its usage, you might update the `system_instruction` string.

Now, if you run the script, the model will be aware of the `add_todo_item` tool and can request its execution.

### 8. Important Notes & Considerations

*   **Error Handling:** The current error handling is basic. Robust applications would require more comprehensive error checking and logging, especially for API calls and function executions.
*   **API Costs:** Be mindful that each call to `chat.send_message()` and `client.models.generate_content()` (in `formate_message`) incurs API usage costs.
*   **Security:** As mentioned, hardcoding API keys is not recommended for production. The simulated functions here are safe, but if they interacted with real systems, proper input validation and sanitization would be crucial.
*   **Model Choice:** `gemini-2.0-flash` is used for the main chat, and `gemini-2.0-flash-lite` for formatting. You can experiment with other models (e.g., `gemini-pro` for potentially more capable reasoning in the main chat) but be aware of different capabilities and pricing.
*   **Confirmation Message Generation:** Using an LLM (`formate_message`) to generate the confirmation is a neat trick for natural language output. However, for critical applications where the exact format of a confirmation is important, a template-based string formatting approach might be more reliable.
*   **Context Window:** Chat models have a limited context window. For very long conversations, the model might start to "forget" earlier parts of the discussion.
