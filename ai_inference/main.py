from llama_cpp import Llama

# Initialize the model
model = Llama(
    model_path="models/openai_gpt-oss-20b-MXFP4.gguf",
    n_threads=8,         # Adjust based on your CPU
    n_gpu_layers=35,      # Adjust based on your GPU VRAM
)

def run_inference_stream(prompt: str, max_tokens=3000, temperature=1):
    output_text = ""
    
    # Use the __call__ method with stream=True
    for output in model(prompt=prompt, max_tokens=max_tokens, temperature=temperature, stream=True):
        token = output['choices'][0]['text'] # type: ignore
        output_text += token
        print(token, end='', flush=True)

    print()
    return output_text

# Example usage
prompt = "What is the color of the sky?"
run_inference_stream(prompt)
