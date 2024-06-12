import os
import replicate
import openai
import gspread
import typer
import json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_KEY')
openai_client = openai.Client(base_url="https://openrouter.ai/api/v1", api_key=os.getenv('OPENROUTER_API_KEY'))

def setup_environment():
    client = gspread.service_account(filename='./cred.json')

    return client

client = setup_environment()


def transcribe_with_replicate(audio_path, num_speakers):
    output = replicate.run(
        "thomasmol/whisper-diarization:b9fd8313c0d492bf1ce501b3d188f945389327730773ec1deb6ef233df6ea119",
        input={
            "file": open(audio_path, "rb"),
            "num_speakers": num_speakers,
            "group_segments": True,
            "transcript_output_format": "both"
        }
    )
    return output

def format_transcription(transcription):
    formatted_text = ""
    for segment in transcription['segments']:
        speaker = segment['speaker']
        text = segment['text']
        formatted_text += f"{speaker}: {text}\n"
    return formatted_text


def process_with_gpt(transcript):
    n = 1300
    split = transcript.split()
    snippets = [' '.join(split[i:i+n]) for i in range(0, len(split), n)]
    summary = ""
    previous = ""

    for i, snippet in enumerate(snippets):
        print(f"Processing snippet {i+1} of {len(snippets)}")
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": f"\"{snippet}\"\n This is the transcript. Do not summarize and keep every information. For additional context here is the previous rewritten message: \n {previous}"}
            ],
            temperature=0.6,
        )
        previous = gpt_response['choices'][0]['message']['content']
        summary += gpt_response['choices'][0]['message']['content']

    return summary

keys = ['id', 'agent_name', 'agent_feedback', 'agent_performance', 'concise_advice', 'summary', 'use_satisfaction_index', 'filename']

def grade_transcript_with_gpt(summary):
    print(f"TRANSCRIPT LENGTH: {len(summary)}")
    prompt = f"Here is a call transcription:\n{summary}\n\nPlease grade the customer agent's performance and provide a user satisfaction index using the result() function, along with any other relevant parameters."
    response = openai_client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        tools=[{"type": "function", "function": {
            "name": "result", "description": "Report the data about the call",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "The summary of the call"},
                    "agent_feedback": {"type": "string", "description": "Feedback for the customer agent - what could have been done better? (напиши фидбек на русском)"},
                    "concise_advice": {"type": "string", "description": "Concise advice for the customer agent - specific points of improvement (на русском, по пунктам)"},
                    "agent_performance": {"type": "number", "minimum": 0, "maximum": 10, "description": "Grade for the customer agent's performance"},
                    "user_satisfaction_index": {"type": "number", "minimum": 0, "maximum": 10, "description": "User satisfaction index"},
                    "additional_parameters": {"type": "object", "description": "Any other relevant parameters"}
                }
            }
        }}],
        tool_choice={"type": "function", "function": {"name": "result"}},
        temperature=0.25
    )
    
    message = response.choices[0].message
    try:
        data = json.loads(message.tool_calls[0].function.arguments if message.tool_calls else message.content, strict=False)
        if 'result' in data:
            data = data['result']
        if 'parameters' in data:
            data = data['parameters']
        return data
    except:
        import traceback
        traceback.print_exc()
        return {}

def get_sum_with_gpt(summary):
    prompt = f"Here is a call transcription:\n{summary}\n\nPlease, list the items/services sold, and get the total sum (in rubles)."
    response = openai_client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        tools=[{"type": "function", "function": {
            "name": "result", "description": "Report the data about the call",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "The summary of the call"},
                    "items_sold": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Name of the item"},
                                "price": {"type": "number", "description": "Price of the item in rubles"}
                            }
                        }
                    },
                    "total_sum": {"type": "number", "description": "Total sum of the items sold in rubles"},
                }
            }
        }}],
        tool_choice={"type": "function", "function": {"name": "result"}},
        temperature=0
    )
    
    message = response.choices[0].message
    try:
        data = json.loads(message.tool_calls[0].function.arguments if message.tool_calls else message.content, strict=False)
        if 'result' in data:
            data = data['result']
        if 'parameters' in data:
            data = data['parameters']
        return data
    except:
        import traceback
        traceback.print_exc()
        return {}



def save_to_google_sheets(client, sheet_name, data, row=None):
    # Open the Google Sheet
    sheet = client.open(sheet_name).sheet1
    
    # Find the next available row
    next_row = row or (len(sheet.get_all_values()) + 1)
    
    # Write new data
    rows = data.split('\n')
    for i, row in enumerate(rows):
        sheet.update_cell(next_row + i, 1, row)
    
    print("Data saved to Google Sheet")
    return next_row

def save_grading_to_google_sheets(client, sheet_name, grading_results, row=None):
    # Open the Google Sheet
    sheet = client.open(sheet_name).sheet1
    
    # Find the next available row
    next_row = row or (len(sheet.get_all_values()) + 1)
    
    # Write new data
    for i, key in enumerate(keys):
        # sheet.update_cell(next_row, 1, key)
        if key in grading_results:
            value = grading_results[key]
            sheet.update_cell(next_row, i + 1, str(value))
    
    print("Grading results saved to Google Sheet")
    return next_row


import typer

app = typer.Typer()

@app.command()
def analyze(audio_path: str, num_speakers: int = 2, sheet_name: str = "Calls", agent_name: str = '', call_id: str = ''):
    metadata = {
        'filename': audio_path,
        'id': call_id,
        'agent_name': agent_name
    }
    row = save_grading_to_google_sheets(client, sheet_name, metadata)
    # Transcribe
    transcription = transcribe_with_replicate(audio_path, num_speakers)
    formatted_transcription = format_transcription(transcription)
    print(formatted_transcription[:100])

    # Process with GPT
    #gpt_summary = process_with_gpt(formatted_transcription)

    # Grade with GPT
    grading_results = grade_transcript_with_gpt(formatted_transcription)
    print(grading_results)

    # Save to Google Sheets
    #save_to_google_sheets(client, sheet_name, gr)
    save_grading_to_google_sheets(client, sheet_name, grading_results, row)


@app.command()
def get_total_sum(audio_path: str):
    transcription = transcribe_with_replicate(audio_path, 2)
    formatted_transcription = format_transcription(transcription)
    res = get_sum_with_gpt(formatted_transcription)
    print(res)


if __name__ == "__main__":
    app()


