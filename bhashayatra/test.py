import os
from google import genai


API_KEY_FALLBACK = "AIzaSyBPiK3XOEmXg0xfSMEVUf5jltcYJlr3yfQ"


def _get_client() -> genai.Client:
    api_key = (os.getenv("GEMINI_API_KEY") or API_KEY_FALLBACK).strip()
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY or update API_KEY_FALLBACK")
    return genai.Client(api_key=api_key)


def _list_models(client: genai.Client) -> None:
    print("Checking accessible models...")
    try:
        for model in client.models.list():
            print(f" - Found: {model.name}")
    except Exception as exc:
        print(f"Error connecting: {exc}")


def _sample_completion(client: genai.Client) -> None:
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents="Explain how AI works in a few words",
        )
        print(response.text)
    except Exception as exc:
        print(f"Generation failed: {exc}")


def main() -> None:
    client = _get_client()
    _list_models(client)
    _sample_completion(client)


if __name__ == "__main__":
    main()