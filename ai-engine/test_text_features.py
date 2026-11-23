
import torch

from app.ai.text_processing.tokenizer import TextTokenizer
from app.ai.text_processing.prompt_encoder import PromptEncoder
from app.ai.text_processing.text_features import TextFeatureExtractor

tokenizer = TextTokenizer()

tokenizer.build_vocab([
    "A cute white cat sitting on a chair",
    "A beautiful red car on the road"
])

token_ids = tokenizer.encode("A cute white cat")
input_tensor = torch.tensor([token_ids], dtype=torch.long)

encoder = PromptEncoder(
    vocab_size=len(tokenizer.vocab),
    embedding_dim=64
)

extractor = TextFeatureExtractor(
    embedding_dim=64,
    feature_dim=128
)

embeddings = encoder(input_tensor)
features = extractor(embeddings)

print("Embedding Shape:", embeddings.shape)
print("Feature Shape:", features.shape)
print("Text Feature Extraction Passed!")
