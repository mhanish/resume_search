import httpx
import json
import os


def get_embeddings(input_list):
    with httpx.Client() as client:
        payload = json.dumps({"inputs": input_list})
        tf_response = client.post(
            os.environ["EMBEDDINGS_URL"],
            data=payload,
        )
    return tf_response
