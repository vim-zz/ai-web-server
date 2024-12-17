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
        Currently collecting: {current_field}
        Already collected: {collected}

        Respond naturally and conversationally. Ask for one piece of information at a time.
        For passwords, ensure they are at least 8 characters with numbers and special characters.

        IMPORTANT: When the user provides valid information, start your response with "VALID:"
        When the user asks questions or provides invalid input, respond normally without the "VALID:" prefix.
        """

        messages = [
            {
                "role": "system",
                "content": system_prompt.format(
                    current_field=self.current_field,
                    collected=json.dumps(self.collected_info, indent=2),
                ),
            },
            {"role": "user", "content": user_message},
        ]

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"model": "gpt-3.5-turbo", "messages": messages, "temperature": 0.7},
            )

            if response.status_code == 200:
                ai_message = response.json()["choices"][0]["message"]["content"]
                is_valid_response = ai_message.startswith("VALID:")

                # Remove the "VALID:" prefix from the message if it exists
                display_message = ai_message[6:] if is_valid_response else ai_message

                # Only update collected info if the AI confirms it's a valid response
                if is_valid_response:
                    if self.current_field == "name" and self.collected_info["name"] is None:
                        cleaned_value = self.clean_user_input("name", user_message)
                        if cleaned_value:
                            self.collected_info["name"] = cleaned_value
                            self.current_field = "username"

                    elif (
                        self.current_field == "username"
                        and self.collected_info["username"] is None
                    ):
                        cleaned_value = self.clean_user_input("username", user_message)
                        if cleaned_value:
                            self.collected_info["username"] = cleaned_value
                            self.current_field = "password"

                    elif (
                        self.current_field == "password"
                        and self.collected_info["password"] is None
                    ):
                        if len(user_message) >= 8:
                            self.collected_info["password"] = user_message
                            self.current_field = "workplace"

                    elif self.current_field == "workplace":
                        cleaned_value = self.clean_user_input("workplace", user_message)
                        if cleaned_value:
                            self.collected_info["workplace"] = cleaned_value
                            self.current_field = "completed"

                # Check if registration is complete
                registration_complete = self.current_field == "completed" and all(
                    value is not None for value in self.collected_info.values()
                )

                return {
                    "message": display_message,
                    "collected_info": self.collected_info,
                    "registration_complete": registration_complete,
                }

            else:
                return {
                    "message": "Sorry, I'm having trouble connecting to the AI service."
                }

        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}
