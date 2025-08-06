import eel
import os
import tkinter as tk
from dotenv import load_dotenv
from openai import OpenAI
import PyPDF2
import ctypes

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

    os.makedirs("config", exist_ok=True)
    with open("config/.env", "w") as f:
        f.write("OPENAI_API_KEY=" + envcontent)

    root.destroy()
    run_app()  # Continue app logic after window closes

def run_app():
    global start, client, chat_history

    load_dotenv(dotenv_path="config/.env")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment!")

    client = OpenAI(api_key=api_key)
    eel.init('gui')
    chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
    start = True

if not os.path.exists('config/.env'):
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



def load_pdf(file_path):
    """ Load and extract text from PDF """
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        return f"Error loading PDF: {e}"

@eel.expose
def analyze_pdf(file_path):
    """ Analyze the content of the loaded PDF """
    text = load_pdf(file_path)
    if text:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Analyze the following text from a PDF:\n{text}"}]
        )
        analysis = response.choices[0].message.content
        return analysis
    else:
        return "No text extracted from the PDF or an error occurred."

@eel.expose
def chat_with_assistant(prompt):
    """ Send a text prompt to the assistant for response """
    chat_history.append({"role": "user", "content": prompt})
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_history
        )
        reply = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"An error occurred: {e}"


if start:
    window = tk.Tk()

    height = window.winfo_screenheight()
    width = window.winfo_screenwidth()

    eel.start('index.html', size=(width, height))