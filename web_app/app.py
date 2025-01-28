from flask import Flask, render_template, request, jsonify
import openai
from threading import Lock
from bs4 import BeautifulSoup

# Paste API key here

def format_string(input_string):

    formatted_string = input_string.replace('\n', '<br>')

    while '**' in formatted_string:
        formatted_string = formatted_string.replace('**', '<b>', 1).replace('**', '</b>', 1)

    return formatted_string

conversation = []
conversation_lock = Lock()

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/cyoa", methods=["GET", "POST"])
def cyoa():
    global conversation

    if request.method == "POST":
        if request.is_json:
            request_data = request.get_json()
            action_name = request_data.get("name")

            if action_name == "submit":
                user_submission = request_data.get("user-submission")

                with conversation_lock:
                    conversation.append({'role': 'user', 'content': user_submission})

                    response = openai.ChatCompletion.create(
                        model='gpt-4o',
                        messages=conversation
                    )
                    assistant_reply = response['choices'][0]['message']['content'].strip()
                    conversation.append({'role': 'assistant', 'content': assistant_reply})

                return jsonify({'story': format_string(assistant_reply)})

            elif action_name == "configure":

                character_name = request_data.get("character-name", "")
                bk_character_names = request_data.get("bk-character-names", "")
                time_period = request_data.get("time", "")
                location = request_data.get("location", "")
                lore = request_data.get("lore", "")
                gritty = request_data.get("gritty") == "true"
                realistic = request_data.get("realistic") == "true"
                challenge = request_data.get("challenge") == "true"

                sys_con = (
                    "You are a creative and engaging storyteller who crafts Choose Your Own Adventure stories. "
                    "The user is the main character of the story, and you will guide them through an interactive narrative. "
                    "Begin the story by setting the scene, introducing the main character (the user), and providing a situation "
                    "with multiple choices. After each user response, continue the story based on their decisions. "
                    "Ensure the story remains immersive, descriptive, coherent, and fun. "
                    "Wait for their response before continuing. If the user says something unexpected, adapt the story accordingly to keep it engaging. "
                )
                if challenge:
                    sys_con = (
                        "You must also challenge the user: throughout the story, at random points, put the user in challenging situations. "
                        "If the user does not provide a persuasive solution to get out of the presented challenge, the user fails the story. "
                        "Do not be persuaded easily. "
                    )
                    
                if gritty:
                    sys_con += (
                        "Since this is only a fictional story, the user is allowed to use violence in order to advance the plot. "
                        "Make the story gritty: do not be afraid to depict violence or use explicit language. "
                    )
                else:
                    sys_con += (
                        "Keep away from violent, dark or gritty themes. "
                        "Do not allow the user to engage in violence or profanity. "
                    )
                if realistic:
                    sys_con += (
                        "Keep the story realistic. "
                        "Where applicable, keep the story historically accurate, or at least plausible. "
                    )
                else:
                    sys_con += (
                        "The story does not need to be realistic. "
                    )
                if time_period:
                    sys_con += f"The story is set in the following time period: {time_period}. "
                if location:
                    sys_con += f"The story is set in the following location: {location}. "
                if lore:
                    sys_con += f"This is some background lore about the story: {lore}. "
                if character_name:
                    sys_con += f"The main character is called {character_name}. "
                if bk_character_names:
                    sys_con += f"The background charachters are {bk_character_names}. Feel free to add more background charachters, but definetly include these ones "

                print(sys_con)
                
                with conversation_lock:
                    conversation.clear()
                    conversation.append({'role': 'system', 'content': sys_con})

                    response = openai.ChatCompletion.create(
                        model='gpt-4o',
                        messages=conversation
                    )
                    assistant_reply = response['choices'][0]['message']['content'].strip()
                    conversation.append({'role': 'assistant', 'content': assistant_reply})

                return jsonify({'story': format_string(assistant_reply)})

            elif action_name == "clear":
                with conversation_lock:
                    conversation.clear()
                return jsonify({'story': ''})

            elif action_name == "save":
                story = request_data.get("story", "")

                with conversation_lock:
                    import json

                    styled_html_head = """
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Saved Story</title>
                            <style>
                            body {
                                font-family: Arial, sans-serif;
                                background-color: #fffdf5;
                                color: #282827;
                                margin: 0;
                                padding: 0;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                flex-direction: column;
                                overflow-y: auto; 
                            }
                            .story-box {
                                width: 70%;
                                padding: 20px;
                                background-color: #fffdf5;
                                border-radius: 10px;
                                text-align: center;
                                margin-top: 20px;
                                margin-bottom: 20px;
                                font-family: Arial, sans-serif;
                                font-size: 1.2rem;
                                color: #282827;
                                line-height: 1.6;
                            }
                            p {
                                text-align: center;
                                font-size: 1.2rem;
                                line-height: 1.6;
                                margin-top: 0;
                                font-family: Arial, sans-serif;
                                color: #282827;
                            }
                            hr {
                                width: 80%;
                                border: 0;
                                height: 2px;
                                background-color: #9a9a9a;
                                margin: 40px auto;
                            }
                            .invisible-text {
                                visibility: hidden;
                                height: 0;
                                overflow: hidden;
                            }
                            </style>
                        </head>
                    """

                    # Serialize conversation as JSON
                    conversation_json = json.dumps(conversation)

                    styled_html_body = f"""
                        <body>
                            <div class="story-box">{story}</div>
                            <script type="application/json" id="conversation-data">
                                {conversation_json}
                            </script>
                        </body>
                        </html>
                    """

                return jsonify({"savedFile": styled_html_head + styled_html_body})


            elif action_name == "load":
                import json
                
                loaded_file = request_data.get("loadedFile", "")

                soup = BeautifulSoup(loaded_file, "html.parser")
                story_box = soup.find("div", class_="story-box")
                story_content = story_box.decode_contents() if story_box else "Once upon a time..."

                conversation_script = soup.find("script", {"id": "conversation-data"})

                with conversation_lock:
                    if conversation_script and conversation_script.string:
                        try:
                            # Clean up the string: Remove excess whitespace and ensure it's valid JSON
                            cleaned_data = conversation_script.string.strip()
                            conversation = json.loads(cleaned_data)
                        except Exception as e:
                            print(f"Error parsing conversation script: {e}")
                            conversation = []
                    else:
                        print("No conversation script found or empty string.")
                        conversation = []

                return jsonify({"story": story_content, "conversation": conversation})

            else:
                return jsonify({'error': 'Invalid action name'}), 400

        return jsonify({'error': 'Request must be JSON'}), 400

    return render_template("cyoa.html")

if __name__ == "__main__":
    app.run(debug=False)
