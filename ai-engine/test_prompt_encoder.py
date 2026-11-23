
import torch

from app.ai.text_processing.tokenizer import TextTokenizer
from app.ai.text_processing.prompt_encoder import PromptEncoder

tokenizer = TextTokenizer()

texts = [
    "A cute white cat sitting on a chair",
    "A beautiful red car on the road",
    "A small house surrounded by green trees"
]

tokenizer.build_vocab(texts)

prompt = "A cute white cat"

token_ids = tokenizer.encode(prompt)

input_tensor = torch.tensor([token_ids], dtype=torch.long)

encoder = PromptEncoder(
    vocab_size=len(tokenizer.vocab),
    embedding_dim=64,
    max_length=32
)

output = encoder(input_tensor)

print("Input Shape:", input_tensor.shape)
print("Output Shape:", output.shape)
print("Device:", output.device)
print("Prompt Encoder Test Passed!")
