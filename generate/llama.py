from llama_cpp import Llama
import os


def gen(prompt, model="models/llama", max_tokens=64):
    llm = Llama(model_path=os.path.expanduser(model))
    output = llm(prompt, max_tokens=max_tokens, echo=False)
    reply = output["choices"][0]["text"]
    reply_firstline = reply.split("\n")[0]

    return reply_firstline
