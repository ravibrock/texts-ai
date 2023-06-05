from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


"""
Possible model choices:
    Promising:
        microsoft/DialoGPT-large
        microsoft/DialoGPT-medium
    Poor results:
        DistilGPT-2
        GPT-2
        microsoft/DialoGPT-small
        microsoft/GODEL-v1_1-base-seq2seq
        microsoft/GODEL-v1_1-large-seq2seq
    Too resource-intensive:
        EleutherAI/gpt-j-6B
        PygmalionAI/pygmalion-6b
"""


def main(source):
    tokenizer = AutoTokenizer.from_pretrained(source)
    model = AutoModelForCausalLM.from_pretrained(source)

    for step in range(5):
        new_user_input_ids = tokenizer.encode(tokenizer.eos_token + input(">> User: "), return_tensors='pt')
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

        chat_history_ids = model.generate(
            bot_input_ids,
            max_length=1000,
            pad_token_id=tokenizer.eos_token_id,
            top_p=0.9,
            do_sample=True
        )

        print(
            "DialoGPT: {}".format(
                tokenizer.decode(
                    chat_history_ids[:, bot_input_ids.shape[-1]:][0],
                    skip_special_tokens=True
                )
            )
        )


if __name__ == "__main__":
    main(source="./model")
