from llama_cpp import Llama
import os.path as osp


def gen(model, prompt, max_tokens=64):
    llm = Llama(model_path=osp.expanduser(model))
    output = llm(prompt, max_tokens=max_tokens, echo=False)

    return output["choices"][0]["text"]
