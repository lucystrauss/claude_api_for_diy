import requests
import subprocess
import anthropic
import sys
#import yam_wav_save
import time

# NB you must be connected to the internet for this to work...

print("\n")

num_loops = 3 # .. how much £££ do you want to spend on API credits...?

# set stable audio key
STABILITY_KEY = "YOUR STABLE AUDIO API KEY"

# set claude key
client = anthropic.Anthropic(api_key="YOUR ANTHROPIC API KEY")

def text_to_audio():

	file1 = open("text_prompt.txt", "r+")
	# Audio generation parameters
	#prompt = "Sharp percussive attack opens to a lyrical phrase that gradually distorts, culminating in rough-textured staccato utterances with jagged rhythmic contours."
	prompt = file1.read()


	audio = "reference_audio.wav" #@param {type:"string"}
	duration = 10  # seconds
	seed = 0
	steps = 30
	cfg_scale = 7.0
	output_format = "wav"
	strength = 0.5 #@param {type:"number"}

	# for use cases without reference audio:
	#files = {
	 #   "prompt": (None, prompt),
	  #  "duration": (None, str(duration)),
	   # "seed": (None, str(seed)),
		#"steps": (None, str(steps)),
	 #   "cfg_scale": (None, str(cfg_scale)),
	  #  "output_format": (None, output_format)
	#}

	# Make the API request
	response = requests.post(
		"https://api.stability.ai/v2beta/audio/stable-audio-2/audio-to-audio",
		headers={"Authorization": f"Bearer {STABILITY_KEY}", "Accept": "audio/*"},
		files={"audio": open(audio, "rb")},
		data={
		"prompt" : prompt,
		"duration": duration,
		"seed": seed,
		"steps": steps,
		"cfg_scale" : cfg_scale,
		"output_format": output_format,
		"strength": strength,
		}
	)

	if not response.ok:
		raise Exception(f"HTTP {response.status_code}: {response.text}")

	# Save and show the result
	filename = f"txt2audio.mp3"
	with open(filename, "wb") as f:
		f.write(response.content)
	#print(f"Saved {filename}")

	subprocess.Popen(['aplay', 'txt2audio.mp3'], 
                 stdout=subprocess.DEVNULL, 
                 stderr=subprocess.DEVNULL)
	
	

def keywords_to_text():
    
    # Function to send prompts and get responses with streaming
    def query_claude_streaming(prompt):
        try:
            # Create a streaming response
            with client.messages.stream(
                model="claude-3-7-sonnet-20250219",  # Choose appropriate model
                max_tokens=300,
                temperature=0.9,
                system="You are Claude, a helpful AI assistant.",
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                # Initialize an empty string to collect the full response
                full_response = ""
                #print("Claude is responding: ", end="")
                
                # Process each piece of text as it comes in
                for text in stream.text_stream:
                    # Print each piece of text as it arrives
                    sys.stdout.write(text)
                    sys.stdout.flush()  # Ensure output appears immediately
                    
                    # Also collect the full response
                    full_response += text
                
                # Return the complete response for saving to file
                return full_response
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    # Note the indentation fix here - these lines need to be at the same level as the def query_claude_streaming line
    with open("txt2audio_classification.txt", "r") as file:
        classifiers_content = file.read()
    
    claude_prompt = f"""Please provide a short narrative text score (for music) inspired by this string of words:
[classifiers]
{classifiers_content}
[/classifiers]

For each line in the classifiers .txt file provided, select only the most interesting or unexpected word to respond to. Disgard the other words. Then, group the words into groups of about five, in order in terms of the string. For each selected word, only select the most interesting or unusual word from each group. Disgard the rest.

Once you have a list of only these few most interesting words, build your narrative text score. Don't get too metaphorical. Limit your answer to only one sentence. Do not provide a title. All I want is the sentence.

The score should be instrument-agnostic; describe timbre, colour etc. but don't specify anything in instrumental terms."""
    
    # Example usage with streaming
    response = query_claude_streaming(claude_prompt)
    
    # Print newlines after the streaming is complete
    
    
    # Save the response to a file
    file = open('text_prompt.txt', 'w') 
    file.write(response) 
    file.close() 
    #print("Text saved to text_prompt.txt")
    #print("---------------------------------------")
	
	
	
def keywords_to_text_old():

	# Function to send prompts and get responses
	def query_claude(prompt):
		try:
		    message = client.messages.create(
		        model="claude-3-7-sonnet-20250219",  # Choose appropriate model
		        max_tokens=300,
		        temperature=0.9,
		        system="You are Claude, a helpful AI assistant.",
		        messages=[{"role": "user", "content": prompt}]
		    )
		    return message.content[0].text
		except Exception as e:
		    return f"Error: {str(e)}"

	print("\n")

	
	
	
	response = query_claude("Please provide a short narrative text score (for music) inspired by this string of words: pling, swirl, rhythm, patter. Keep your answer short, just a sentence. The score should be instrument-agnostic; describe timbre, colour etc. but don't specify anything in instrumental terms.")
	print(response)
	
	print("\n")

	file = open('text_prompt.txt', 'w') 
	file.write(response) 
	file.close() 


def yamnet_classification():

	subprocess.Popen([
    'xterm',
    '-fa', 'Noto Mono',  # Font face
    '-fs', '14',                # Font size
    '-geometry', '30x50+0+0',  # Width x Height + X + Y position
    '-bg', 'black',             # Background color
    '-fg', 'Magenta',        # Text color
    '-title', 'sound classifier',
    '-e', 'python', 'yam_wav_save.py'   # The command to run
])
	time.sleep(12.)
	
def yamnet_reference():

	subprocess.Popen([
    'xterm',
    '-fa', 'Noto Mono',  # Font face
    '-fs', '14',                # Font size
    '-geometry', '30x50+0+0',  # Width x Height + X + Y position
    '-bg', 'black',             # Background color
    '-fg', 'Magenta',        # Text color
    '-title', 'sound classifier',
    '-e', 'python', 'yam_wav_save_initial.py'   # The command to run
])
	#time.sleep(12.)
	
print("\n")
print('analysing sound...')
print("\n")
yamnet_reference() 

subprocess.Popen(['aplay', 'reference_audio.wav'], 
                 stdout=subprocess.DEVNULL, 
                 stderr=subprocess.DEVNULL)
                 
time.sleep(12.)                        



for i in range (num_loops):
	#subprocess.Popen(['xterm', '-e', 'python', 'yam_wav_save.py'])
	
	print('writing sound story...')
	print("\n")
	
	keywords_to_text()
	time.sleep(1.)
	
	print("\n")
	print('generating audio...')
	print("\n")
	
	text_to_audio()
	
	print('analysing sound...')
	print("\n")
	
	yamnet_classification()
	#print(i)
	
