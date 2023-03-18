from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments)
from query import get_messages
import math


def preprocess_function(training_data):
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large", padding_side="left")

    return tokenizer([" ".join(x) for x in training_data["text"]], truncation=True)


def tokenize_preprocess(prep_function, data):
    tokenized_data = data.map(
        prep_function,
        batched=True,
        num_proc=4,
        remove_columns=data["train"].column_names,
    )

    return tokenized_data


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


def train(model, data_collator, train_dataset, val_dataset):
    training_args = TrainingArguments(
        evaluation_strategy="epoch",
        num_train_epochs=3,
        learning_rate=2e-5,
        weight_decay=0.01,
        output_dir="./model",
        logging_dir="./.logs",
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


def fine_tune(tokenizer, model, data_collator, training):
    tokenized_replies = tokenize_preprocess(preprocess_function, training)
    lm_replies = tokenized_replies.map(group_texts, batched=True, num_proc=4)
    tokenizer.pad_token = tokenizer.eos_token

    trainer = train(model, data_collator, lm_replies["train"], lm_replies["test"])
    trainer.train()
    trainer.save_model("./model")
    tokenizer.save_pretrained("./model")

    print(f"Perplexity: {math.exp(trainer.evaluate()['eval_loss']):.2f}")


def main():
    messages = get_messages()
    messages = messages.train_test_split(test_size=0.2)

    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large")
    model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-large")
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    fine_tune(tokenizer, model, data_collator, messages)


if __name__ == "__main__":
    main()
