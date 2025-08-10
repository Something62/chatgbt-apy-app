import eel
import os
import tkinter as tk
from dotenv import load_dotenv
from openai import OpenAI
import PyPDF2
import ctypes
import base64
import io
from PIL import Image

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

start = False

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

def save_key():
    envcontent = userinput.get()
    if not envcontent:
        print("No input value detected!")
        return

    config_path = os.path.join(base_dir, "config")
    os.makedirs(config_path, exist_ok=True)
    env_file_path = os.path.join(config_path, ".env")
    with open(env_file_path, "w") as f:
        f.write("OPENAI_API_KEY=" + envcontent)

    root.destroy()
    run_app()  

def run_app():
    global start, client, chat_history

    env_path = os.path.join(base_dir, "config", ".env")
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment!")

    client = OpenAI(api_key=api_key)
    gui_path = os.path.join(base_dir, "gui")
    eel.init(gui_path)
    chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
    start = True

if not os.path.exists(os.path.join(base_dir, 'config', '.env')):

    print("Error! File not found.")

    root = tk.Tk()
    root.title("API Key")
    root.resizable(False, False)
    root.overrideredirect(True)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width_of_window = int(screen_width * 0.2)
    height_of_window = int(screen_height * 0.3)

    x_coordinate = (screen_width // 2) - (width_of_window // 2)
    y_coordinate = (screen_height // 2) - (height_of_window // 2)

    root.geometry(f"{width_of_window}x{height_of_window}+{x_coordinate}+{y_coordinate}")

    label = tk.Label(root, text="Please enter your OpenAI API key here:",
                     anchor=tk.CENTER, font=("Arial", 10))
    label.pack(pady=10)

    userinput = tk.Entry(root, font=("Arial", 10))
    userinput.pack(padx=10)

    button = tk.Button(root, text="Save Key", command=save_key)
    button.pack(pady=10)

    root.mainloop()

else:
    run_app()




def load_pdf(base64_pdf_data):
    try:
        if "," in base64_pdf_data:
            header, encoded = base64_pdf_data.split(",", 1)
        else:
            encoded = base64_pdf_data
        pdf_bytes = base64.b64decode(encoded)
        pdf_stream = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_stream)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text if text else "No text found in PDF."
    except Exception as e:
        return f"Error loading PDF: {e}"


@eel.expose
def chat_with_assistant(prompt, model):
    chat_history.append({"role": "user", "content": prompt})
    try:
        response = client.chat.completions.create(
            model=model,
            messages=chat_history
        )

        reply = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"An error occurred: {e}"

@eel.expose
def analyze_image_with_prompt(base64_image, prompt_text, model):
    try:
        if "," in base64_image:
            header, encoded = base64_image.split(",", 1)
        else:
            return "Invalid image format."

        if not prompt_text.strip():
            prompt_text = "What do you see in this image?"

        image_url_object = {
            "type": "image_url",
            "image_url": {"url": base64_image}
        }

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt_text},
                image_url_object
            ]}]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Error analyzing image: {e}"

@eel.expose
def analyze_pdf(file_path, model):
    text = load_pdf(file_path)
    if text:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": f"Analyze the following text from a PDF:\n{text}"}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing PDF: {e}"
    else:
        return "No text extracted from the PDF or an error occurred."



if start:
    window = tk.Tk()

    height = window.winfo_screenheight()
    width = window.winfo_screenwidth()

    eel.start('index.html', size=(width, height), block=True)
