import os
# Set TF log level (0 = all, 1 = filter out INFO, 2 = filter out WARNING, 3 = filter out ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Filter warnings and info

# Additional environment variables to suppress specific warnings
os.environ['AUTOGRAPH_VERBOSITY'] = '0'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import csv
import io
import soundfile as sf
import time
from datetime import datetime

# Find the name of the class with the top score when mean-aggregated across frames.
def class_names_from_csv(class_map_csv_text):
    """Returns list of class names corresponding to score vector."""
    class_map_csv = io.StringIO(class_map_csv_text)
    class_names = [display_name for (class_index, mid, display_name) in csv.reader(class_map_csv)]
    class_names = class_names[1:]  # Skip CSV header
    return class_names

def classify(waveform, model):
    # Make sure the waveform is the right shape
    waveform = waveform.reshape((16000,))
    
    # Run the model, check the output
    scores, embeddings, log_mel_spectrogram = model(waveform)
    scores.shape.assert_is_compatible_with([None, 521])
    embeddings.shape.assert_is_compatible_with([None, 1024])
    log_mel_spectrogram.shape.assert_is_compatible_with([None, 64])
    
    # Get class names
    class_map_path = model.class_map_path().numpy()
    class_names = class_names_from_csv(tf.io.read_file(class_map_path).numpy().decode('utf-8'))
    class_names = np.array(class_names)
    
    # Get top classes
    n_classes = -5  # number of classes to print
    class_ids = scores.numpy().mean(axis=0).argpartition(n_classes)[n_classes:]
    top_classes = class_names[class_ids]
    
    print(top_classes)
    return top_classes

def process_audio_file(file_path, model, output_file_path=None, window_size=16000, step_size=None):
    """
    Process an audio file in windows and classify each window
    
    Args:
        file_path: Path to the .wav file
        model: YAMNet model
        output_file_path: Path to save classification results (optional)
        window_size: Size of each window in samples (default: 16000 = 1 second at 16kHz)
        step_size: Step size between windows in samples (default: same as window_size)
    """
    # Set default step size if not provided
    if step_size is None:
        step_size = window_size

    # Create default output file path if not provided
    if output_file_path is None:
        # Extract filename without extension
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_path = f"{base_filename}_classification.txt"

    print(f"Processing audio file: {file_path}")
    print(f"Results will be saved to: {output_file_path}")
    
    # Load the audio file
    data, samplerate = sf.read(file_path)
    
    # Convert to mono if stereo
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
    
    # Resample to 16kHz if needed
    if samplerate != 16000:
        print(f"Resampling from {samplerate}Hz to 16000Hz")
        # You would need to add resampling code here
        # For example using librosa: data = librosa.resample(data, orig_sr=samplerate, target_sr=16000)
        # For simplicity, we'll assume the file is already at 16kHz
    
    # Normalize audio
    data = data / np.max(np.abs(data))
    
    # Process in windows
    total_windows = (len(data) - window_size) // step_size + 1
    print(f"Processing {total_windows} windows...")
    
    # Open the output file
    with open(output_file_path, 'w') as f:
        # Write header
        #f.write(f"# Audio Classification Results\n")
        #f.write(f"# File: {os.path.basename(file_path)}\n")
        #f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        #f.write(f"# Window Size: {window_size/16000:.2f}s, Step Size: {step_size/16000:.2f}s\n")
        #f.write(f"# Format: [Window Number] [Start Time - End Time] [Top 5 Classes]\n\n")
        
        for i in range(total_windows):
            # Extract window
            start = i * step_size
            end = start + window_size
            window = data[start:end]
            
            # Ensure the window is the right size
            if len(window) == window_size:
                # Format time range
                start_time = start/16000
                end_time = end/16000
                time_range = f"{start_time:.2f}s - {end_time:.2f}s"
                
                # Print window info
                #print(f"Window {i+1}/{total_windows} (Time: {time_range})")
                
                # Classify window
                top_classes = classify(window, model)
                
                # Write to file
                f.write(f"{', '.join(top_classes)}\n")
                f.flush()  # Ensure data is written immediately
                
                # Slight pause for readability in console
                time.sleep(0.1)
    
    print(f"\nClassification complete! Results saved to {output_file_path}")
    return output_file_path

if __name__ == "__main__":
    # Load the YAMNet model
    print("Loading YAMNet model...")
    model = hub.load('https://www.kaggle.com/models/google/yamnet/TensorFlow2/yamnet/1')
    
    # Path to your .wav file
    wav_file_path = "reference_audio.wav"#"txt2audio.mp3"  # Change this to your file path
    
    # Set window parameters
    window_size = 16000  # 1 second window at 16kHz
    step_size = 16000     # 0.5 second overlap (adjust as needed)
    
    # Process the file and save results
    output_file = process_audio_file(wav_file_path, model, window_size=window_size, step_size=step_size)
    
    #print('yamnet tags saved')
