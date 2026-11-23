
from app.ai.text_processing.tokenizer import TextTokenizer

tokenizer = TextTokenizer()

training_texts = [
    "A cute white cat sitting on a chair",
    "A beautiful red car on the road",
    "A small house surrounded by green trees",
    "A cute cartoon dog playing in the garden",
]

vocab_size = tokenizer.build_vocab(training_texts)

prompt = "A cute white cat"

encoded = tokenizer.encode(prompt)
decoded = tokenizer.decode(encoded)

print("Vocabulary Size:", vocab_size)
print("Original Prompt:", prompt)
print("Encoded Tokens:", encoded)
print("Decoded Prompt:", decoded)

tokenizer.save_vocab("datasets/metadata/vocabulary.json")

print("Vocabulary saved successfully!")

