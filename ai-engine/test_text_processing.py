import torch

from app.ai.text_processing import (
    Vocabulary,
    Tokenizer,
    PromptEncoder,
    TextFeatureExtractor,
)


def main():
    print("Testing Cute3D Text Processing...")

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("Device:", device)

    # 1. Create vocabulary
    vocabulary = Vocabulary()

    # 2. Create tokenizer
    tokenizer = Tokenizer(
        vocabulary=vocabulary,
        max_length=32,
    )

    # 3. Build vocabulary from sample prompts
    prompts = [
        "A cute white cat",
        "A beautiful red flower",
        "A small brown dog",
        "A futuristic blue robot",
        "A beautiful green forest",
    ]

    tokenizer.build_vocabulary(prompts)

    print("Vocabulary Size:", vocabulary.size)

    # 4. Encode prompt
    prompt = "A cute white cat"

    tokens = tokenizer.tokenize(prompt)
    token_ids = tokenizer.encode(prompt)

    print("Original Prompt:", prompt)
    print("Tokens:", tokens)
    print("Token IDs:", token_ids)

    # 5. Decode prompt
    decoded_prompt = tokenizer.decode(token_ids)

    print("Decoded Prompt:", decoded_prompt)

    # 6. Save and reload vocabulary
    vocabulary_path = "datasets/metadata/vocabulary.json"

    tokenizer.save_vocabulary(vocabulary_path)

    loaded_vocabulary = Vocabulary.load(vocabulary_path)

    print("Saved and loaded vocabulary:", loaded_vocabulary.size)

    # 7. Convert token IDs to tensor
    input_tensor = torch.tensor(
        [token_ids],
        dtype=torch.long,
        device=device,
    )

    # 8. Prompt encoder
    prompt_encoder = PromptEncoder(
        vocab_size=vocabulary.size,
        embedding_dim=64,
        max_length=32,
    ).to(device)

    embeddings = prompt_encoder(input_tensor)

    print("Prompt Embedding Shape:", embeddings.shape)

    # 9. Extract text features
    feature_extractor = TextFeatureExtractor(
        embedding_dim=64,
        feature_dim=128,
    ).to(device)

    text_features = feature_extractor(
        embeddings,
        token_ids=input_tensor,
    )

    print("Text Feature Shape:", text_features.shape)

    # 10. Backpropagation test
    loss = text_features.mean()
    loss.backward()

    print("Backward Pass: Successful")
    print("Text Processing Test Passed!")


if __name__ == "__main__":
    main()
