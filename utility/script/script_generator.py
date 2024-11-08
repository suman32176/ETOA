import os
import json

# Determine which API client to use
if len(os.environ.get("GROQ_API_KEY", "")) > 30:
    from groq import Groq
    model = "mixtral-8x7b-32768"
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
else:
    from openai import OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_KEY')
    model = "gpt-4"
    client = OpenAI(api_key=OPENAI_API_KEY)

def process_script(script, video_type='short'):
    if video_type == 'short':
        # For short videos, ensure the script is concise (around 140 words)
        prompt = (
            f"""You are a script editor for short-form videos. Your task is to edit the following script to make it concise and engaging, 
            suitable for a video lasting less than 50 seconds (approximately 140 words). Maintain the core message and key points while 
            trimming unnecessary details. Here's the script to edit:

            {script}

            Please provide the edited script, ensuring it's brief, highly interesting, and unique.
            """
        )
    else:  # Long video script processing
        prompt = (
            f"""You are an expert script editor for long-form educational videos. Your task is to refine and structure the following script 
            to make it more engaging and suitable for a 10-minute video (approximately 1,200 to 1,400 words). Maintain the core content and key points 
            while ensuring a smooth flow of information. Here's the script to edit:

            {script}

            Please provide the edited script, ensuring it flows well, is informative, and maintains viewer engagement throughout. 
            Structure the content in a logical manner without using explicit section headers.
            """
        )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Please edit the script as instructed."}
            ]
        )
        
        processed_script = response.choices[0].message.content.strip()
        return processed_script
    except Exception as e:
        print("An error occurred while processing the script:", str(e))
        return script  # Return the original script if processing fails

# Keep the existing generate_script function for backwards compatibility
def generate_script(topic, video_type='short'):
    # ... (keep the existing implementation)
    pass

if __name__ == "__main__":
    # ... (keep the existing main block for testing purposes)
    pass
