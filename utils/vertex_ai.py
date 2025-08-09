from google.cloud import aiplatform

def generate_answer(question, context_chunks, google_api_key):
    # Combine context chunks to prompt
    context = "\n\n".join(context_chunks)
    prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"

    # Set env var for Google API key
    import os
    os.environ["GOOGLE_API_KEY"] = google_api_key

    # Initialize Vertex AI client
    aiplatform.init(location="us-central1", credentials=None)

    # Adjust model name for PaLM or text-bison as needed
    model = aiplatform.models.TextGenerationModel.from_pretrained("text-bison@001")

    response = model.predict(
        prompt,
        max_output_tokens=256,
        temperature=0.2,
        top_p=0.8,
    )

    return response.text
