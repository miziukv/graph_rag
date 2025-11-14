from openai import OpenAI

client = OpenAI()

def embed(input: str):
    response = client.embeddings.create(
        input = input,
        model = 'text-embedding-3-small'
    )

    return response
