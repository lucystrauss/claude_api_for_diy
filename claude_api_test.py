import anthropic

# Initialize the client
client = anthropic.Anthropic(api_key="YOUR_API_KEY_GOES_HERE")

# Function to send prompts and get responses
def query_claude(prompt):
    try:
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",  # Choose appropriate model
            max_tokens=300,
            temperature=0.9,
            system="You are Claude, a helpful AI assistant.", # YOU CAN CHANGE THIS SYSTEM PROMPT
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


response = query_claude("YOUR PROMPT GOES HERE")
print(response)
