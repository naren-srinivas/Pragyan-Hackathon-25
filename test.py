from gpt4all import GPT4All
MODEL_PATH = "E:/Pragyan Hackathon 25/ggml-gpt4all-j-v1.3-groovy.bin"
model = GPT4All("ggml-gpt4all-j-v1.3-groovy.bin", allow_download=False)
response = model.generate("What is the capital of France?")
print(response)