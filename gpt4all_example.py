from gpt4all import GPT4All
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
#model = GPT4All("nous-hermes-llama2-13b.Q4_0.gguf")
with model.chat_session():
    print(model.generate("quadratic formula"))