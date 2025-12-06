from app.utils.groq_client import client

def groq_llm(prompt: str, temperature=0.2):
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return resp.choices[0].message.content