import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4o")

print("Voceb size: ", encoder.n_vocab)

text = "the cat set on the mat"

tokens = encoder.encode(text)

print(tokens)

texts = encoder.decode(tokens)

print(texts)