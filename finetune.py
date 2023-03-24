from functools import partial
from query import get_messages
from math import exp
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments)


# Returns proper tokenizer
def preprocess_function(tokenizer, training_data):
    return tokenizer([" ".join(x) for x in training_data["text"]], truncation=True)


# Tokenizes and preprocesses the data
def tokenize_preprocess(tokenizer, prep_function, data):
    partial_prep = partial(prep_function, tokenizer)
    tokenized_data = data.map(
        partial_prep,
        batched=True,
        num_proc=4,
        remove_columns=data["train"].column_names,
    )

    return tokenized_data


# Groups the text into blocks of 128 tokens
def group_texts(examples):
    block_size = 128
    concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
    total_length = len(concatenated_examples[list(examples.keys())[0]])
    total_length = (total_length // block_size) * block_size
    result = {
        k: [t[i: i + block_size] for i in range(0, total_length, block_size)]
        for k, t in concatenated_examples.items()
    }
    result["labels"] = result["input_ids"].copy()

    return result


# Generates the proper trainer object
def train(model, data_collator, train_dataset, val_dataset):
    training_args = TrainingArguments(
        evaluation_strategy="epoch",
        num_train_epochs=1,
        learning_rate=2e-5,
        weight_decay=0.01,
        output_dir="./.output",
        logging_dir="./.output",
        logging_steps=10,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
    )

    return trainer


# Finetunes the model
def fine_tune(tokenizer, model, data_collator, training):
    tokenized_replies = tokenize_preprocess(tokenizer, preprocess_function, training)
    lm_replies = tokenized_replies.map(group_texts, batched=True, num_proc=4)
    tokenizer.pad_token = tokenizer.eos_token

    trainer = train(model, data_collator, lm_replies["train"], lm_replies["test"])
    trainer.train()
    trainer.save_model("./model")
    tokenizer.save_pretrained("./model")

    print(f"Perplexity: {exp(trainer.evaluate()['eval_loss']):.2f}")


# Main function
def main(source):
    tokenizer = AutoTokenizer.from_pretrained(source)
    model = AutoModelForCausalLM.from_pretrained(source)
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    messages = get_messages().train_test_split(test_size=0.2)

    fine_tune(tokenizer, model, data_collator, messages)


if __name__ == "__main__":
    main(source="microsoft/DialoGPT-large")
