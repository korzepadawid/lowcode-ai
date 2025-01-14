import requests

from typing import List


def retrieve_wiki(query: str) -> List[str]:
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {"query": query, "collection_name": "KartonBERT_USE_base_v1"}
    response = requests.post(
        "https://ferryt-rag.csi.wmi.amu.edu.pl/api/retrieve",
        headers=headers,
        json=data,
    )
    results = []
    if response.status_code == 200:
        print("Response from Ferryt Wiki:", response.json())
        data = response.json()
        for item in data:
            if "page" not in item:
                continue
            page = item["page"]
            if "text_raw" in page:
                results.append(page["text_raw"])
    else:
        print(
            f"Request from Ferryt Wiki failed with status code {response.status_code}"
        )
        print("Response from Ferryt Wiki Text:", response.text)
        return []
    return results