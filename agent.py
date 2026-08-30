import os
import json

from dotenv import load_dotenv
from groq import Groq

from tools import (
    train_search,
    availability_check,
    fare_check,
    booking_status,
)


# =========================
# ENVIRONMENT
# =========================

load_dotenv()


# =========================
# GROQ CLIENT
# =========================

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# =========================
# TOOLS
# =========================

tools = [

    # =========================
    # TRAIN SEARCH
    # =========================

    {
        "type": "function",
        "function": {
            "name": "train_search",
            "description": (
                "Search for trains between two "
                "stations on a specific journey date."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source station or city."
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination station or city."
                    },
                    "journey_date": {
                        "type": "string",
                        "description": (
                            "Journey date in YYYY-MM-DD format."
                        )
                    }
                },
                "required": [
                    "source",
                    "destination",
                    "journey_date"
                ]
            }
        }
    },


    # =========================
    # AVAILABILITY
    # =========================

    {
        "type": "function",
        "function": {
            "name": "availability_check",
            "description": (
                "Check train seat availability "
                "for a specific date and class."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "train_number": {
                        "type": "string",
                        "description": "Train number."
                    },
                    "journey_date": {
                        "type": "string",
                        "description": (
                            "Journey date in YYYY-MM-DD format."
                        )
                    },
                    "travel_class": {
                        "type": "string",
                        "description": (
                            "Travel class such as "
                            "SL, 3A, 2A or 1A."
                        )
                    }
                },
                "required": [
                    "train_number",
                    "journey_date",
                    "travel_class"
                ]
            }
        }
    },


    # =========================
    # FARE
    # =========================

    {
        "type": "function",
        "function": {
            "name": "fare_check",
            "description": (
                "Check the current fare for a "
                "specific train and travel class."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "train_number": {
                        "type": "string",
                        "description": "Train number."
                    },
                    "journey_date": {
                        "type": "string",
                        "description": (
                            "Journey date in YYYY-MM-DD format."
                        )
                    },
                    "travel_class": {
                        "type": "string",
                        "description": "Travel class."
                    }
                },
                "required": [
                    "train_number",
                    "journey_date",
                    "travel_class"
                ]
            }
        }
    },


    # =========================
    # BOOKING STATUS
    # =========================

    {
        "type": "function",
        "function": {
            "name": "booking_status",
            "description": (
                "Check the status of an existing "
                "railway reservation using its "
                "booking reference."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_reference": {
                        "type": "string",
                        "description": (
                            "Booking reference or PNR."
                        )
                    }
                },
                "required": [
                    "booking_reference"
                ]
            }
        }
    }
]


# =========================
# AI AGENT
# =========================

class RailwayReservationAgent:

    def __init__(self):

        self.name = (
            "Railway Reservation Agent"
        )

        self.conversation_history = []


    # =========================
    # RUN AGENT
    # =========================

    def run(self, goal):

        messages = [

            {
                "role": "system",
                "content": (

                    "You are an AI Railway Reservation Agent. "

                    "Understand the user's railway "
                    "reservation-related goal and "
                    "use available tools when necessary. "

                    "Use train_search when the user "
                    "needs train options. "

                    "Use availability_check when the "
                    "user asks about seat availability. "

                    "Use fare_check when the user "
                    "asks about ticket fare. "

                    "Use booking_status when the user "
                    "provides a booking reference or PNR "
                    "and wants its status. "

                    "Never invent train availability, "
                    "fare, booking status, PNR or "
                    "reservation confirmation. "

                    "Only report information returned "
                    "by the tools. "

                    "If a railway API is unavailable, "
                    "clearly tell the user that live "
                    "railway data is not currently "
                    "configured. "

                    "Before any irreversible booking "
                    "or payment action, require explicit "
                    "user confirmation. "

                    "Do not ask for passwords, OTPs, "
                    "UPI PINs, card CVVs or other "
                    "private authentication secrets. "

                    "Use previous conversation context "
                    "when it is relevant. "

                    "Answer clearly and concisely."
                )
            }
        ]


        # =========================
        # MEMORY
        # =========================

        messages.extend(
            self.conversation_history
        )


        # =========================
        # USER REQUEST
        # =========================

        messages.append(
            {
                "role": "user",
                "content": goal
            }
        )


        # =========================
        # AGENT LOOP
        # =========================

        max_iterations = 5

        for _ in range(max_iterations):

            response = (
                groq_client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=messages,

                    tools=tools,

                    tool_choice="auto",

                    parallel_tool_calls=False,

                    temperature=0.2
                )
            )


            message = (
                response.choices[0].message
            )


            # =========================
            # FINAL ANSWER
            # =========================

            if not message.tool_calls:

                final_answer = (
                    message.content
                    or "No response generated."
                )


                # Save conversation

                self.conversation_history.append(
                    {
                        "role": "user",
                        "content": goal
                    }
                )

                self.conversation_history.append(
                    {
                        "role": "assistant",
                        "content": final_answer
                    }
                )


                # Keep memory limited

                self.conversation_history = (
                    self.conversation_history[-10:]
                )


                return final_answer


            # =========================
            # ADD ASSISTANT TOOL CALL
            # =========================

            messages.append(message)


            # =========================
            # EXECUTE TOOLS
            # =========================

            for tool_call in message.tool_calls:

                function_name = (
                    tool_call.function.name
                )


                # =========================
                # PARSE ARGUMENTS
                # =========================

                try:

                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                except json.JSONDecodeError:

                    result = (
                        "Invalid tool arguments."
                    )

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id":
                                tool_call.id,
                            "content":
                                result
                        }
                    )

                    continue


                # =========================
                # TRAIN SEARCH
                # =========================

                if function_name == "train_search":

                    result = train_search(
                        arguments["source"],
                        arguments["destination"],
                        arguments["journey_date"]
                    )


                # =========================
                # AVAILABILITY
                # =========================

                elif function_name == "availability_check":

                    result = availability_check(
                        arguments["train_number"],
                        arguments["journey_date"],
                        arguments["travel_class"]
                    )


                # =========================
                # FARE
                # =========================

                elif function_name == "fare_check":

                    result = fare_check(
                        arguments["train_number"],
                        arguments["journey_date"],
                        arguments["travel_class"]
                    )


                # =========================
                # BOOKING STATUS
                # =========================

                elif function_name == "booking_status":

                    result = booking_status(
                        arguments["booking_reference"]
                    )


                # =========================
                # UNKNOWN TOOL
                # =========================

                else:

                    result = (
                        "Unknown tool requested."
                    )


                # =========================
                # TOOL RESULT
                # =========================

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id":
                            tool_call.id,
                        "content":
                            result
                    }
                )


        # =========================
        # MAX ITERATIONS
        # =========================

        return (
            "The agent reached the maximum "
            "number of tool steps without "
            "completing the task."
        )


# =========================
# AGENT INSTANCE
# =========================

agent = RailwayReservationAgent()
