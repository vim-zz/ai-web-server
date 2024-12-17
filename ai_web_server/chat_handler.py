import os
import json
import requests
import re


class ChatHandler:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.collected_info = {
            "name": None,
            "username": None,
            "password": None,
            "workplace": None,
        }
        self.current_field = "name"
        self.conversation_history = []

    def clean_user_input(self, field, value):
        """Clean user input based on field type."""
        value = value.strip()

        if field == "name":
            # Remove common prefixes and keep only the actual name
            value = re.sub(
                r"^(my name is|i am|it's|its|i'm|\s)+", "", value, flags=re.IGNORECASE
            )
            # Remove punctuation at the end
            value = re.sub(r"[.,!]$", "", value)
            # Capitalize first letter of each word
            value = value.title()

        elif field == "username":
            # Remove common prefixes and spaces
            value = re.sub(
                r"^(my username is|username|\s)+", "", value, flags=re.IGNORECASE
            )
            value = value.strip()
            # Remove any spaces and special characters except underscores and hyphens
            value = re.sub(r"[^\w\-]", "", value)
            value = value.lower()

        elif field == "workplace":
            # Remove common prefixes
            value = re.sub(
                r"^(i work at|i study at|i'm at|i am at|workplace is|school is|\s)+",
                "",
                value,
                flags=re.IGNORECASE,
            )
            # Remove punctuation at the end
            value = re.sub(r"[.,!]$", "", value)
            value = value.strip()

        return value

    def handle_message(self, user_message):
        system_prompt = """
        You are a registration assistant. You need to collect: name, username, password, and workplace/school.
        Current field to collect: {current_field}
        Current collected information: {collected}

        YOU MUST ALWAYS RESPOND WITH EXACTLY TWO PARTS:
        1. A friendly conversational message
        2. The JSON data in the next line

        EXACT FORMAT REQUIRED:
        <your conversation message>
        {{"name": "value", "username": "value", "password": "value", "workplace": "value"}}

        Example valid responses:
        "Great! I'll set your username as banana12. Now, please create a strong password (at least 8 characters with numbers and special characters)."
        {{"name": "Ofer", "username": "banana12", "password": null, "workplace": null}}

        OR

        "That username isn't valid. Please try another username."
        {{"name": "Ofer", "username": null, "password": null, "workplace": null}}

        Current field progression:
        name -> username -> password -> workplace

        Rules for conversation:
        - Be friendly and natural
        - Focus on collecting the CURRENT field only ({current_field})
        - After collecting valid input, ask for the next field
        - For passwords, ensure they are at least 8 characters with numbers and special characters
        """

        # Create conversation context
        conversation_context = []
        for i in range(min(3, len(self.conversation_history))):
            conversation_context.append(self.conversation_history[-(i+1)])
        conversation_context.reverse()

        messages = [
            {
                "role": "system",
                "content": system_prompt.format(
                    current_field=self.current_field,
                    collected=json.dumps(self.collected_info, indent=2),
                ),
            },
            # Add recent conversation history
            *conversation_context,
            # Add current user message
            {"role": "user", "content": user_message},
            # Final reminder for AI
            {
                "role": "assistant",
                "content": """Remember to respond with BOTH:
1. Conversation message
2. JSON data
Example:
"Your message here"
{"json": "data"}"""
            }
        ]

        try:
            print(f"DEBUG to AI: {messages}")
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"model": "gpt-3.5-turbo", "messages": messages, "temperature": 0.7},
            )

            if response.status_code == 200:
                ai_message = response.json()["choices"][0]["message"]["content"]
                print(f"DEBUG from AI: {ai_message}")

                try:
                    # If we only got JSON, add a default conversational message
                    if ai_message.strip().startswith('{'):
                        default_messages = {
                            "username": "Great! Now please create a strong password (at least 8 characters with numbers and special characters).",
                            "password": "Perfect! Finally, where do you work or study?",
                            "workplace": "Thank you! Your registration is complete.",
                            "name": "Great! Could you choose a username for your account?"
                        }
                        ai_message = f"{default_messages.get(self.current_field, 'Please continue with the registration.')}\n{ai_message}"

                    last_brace_start = ai_message.rindex('{')
                    last_brace_end = ai_message.rindex('}') + 1
                    collected_json = json.loads(ai_message[last_brace_start:last_brace_end])
                    display_message = ai_message[:last_brace_start].strip()

                    # Add to conversation history
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": display_message
                    })

                    if collected_json[self.current_field] is not None and collected_json[self.current_field] != self.collected_info[self.current_field]:
                        self.collected_info = collected_json
                        # Progress to next field
                        if self.current_field == "name":
                            self.current_field = "username"
                        elif self.current_field == "username":
                            self.current_field = "password"
                        elif self.current_field == "password":
                            self.current_field = "workplace"
                        elif self.current_field == "workplace":
                            self.current_field = "completed"

                    # Add user message to conversation history after processing
                    self.conversation_history.append({
                        "role": "user",
                        "content": user_message
                    })

                    # Check if registration is complete
                    registration_complete = all(value is not None for value in self.collected_info.values())

                    return {
                        "message": display_message,
                        "collected_info": self.collected_info,
                        "registration_complete": registration_complete,
                    }

                except (ValueError, json.JSONDecodeError) as e:
                    print(f"Error processing AI response: {e}")
                    return {
                        "message": "Could you please provide the information requested?",
                        "collected_info": self.collected_info,
                        "registration_complete": False,
                    }

            else:
                return {
                    "message": "Sorry, I'm having trouble connecting to the AI service."
                }

        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}
