import time
import requests
from cosdata import Client
from ..config import settings

class CosdataManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CosdataManager, cls).__new__(cls)
            cls._instance.client = Client(
                host=settings.COSDATA_HOST,
                username=settings.COSDATA_USER,
                password=settings.COSDATA_PASS,
                verify=False
            )
        return cls._instance

    def get_collection(self, reset: bool = False):
        """
        Retrieves the collection. 
        If reset=True, it deletes the existing one to prevent conflicts.
        If it doesn't exist, it creates it with TF-IDF enabled.
        """
        if reset:
            try:
                self.client.get_collection(settings.COLLECTION_NAME).delete()
                print(f"🧹 Collection '{settings.COLLECTION_NAME}' deleted.")
                time.sleep(1) # Allow server to cleanup
            except Exception:
                pass

        try:
            # Try fetching existing
            if not reset:
                return self.client.get_collection(settings.COLLECTION_NAME)
            raise Exception("Force create")
        except:
            # Create new if missing or reset requested
            print(f"🚀 Creating collection '{settings.COLLECTION_NAME}'...")
            col = self.client.create_collection(
                name=settings.COLLECTION_NAME,
                dimension=384,
                tf_idf_options={"enabled": True}
            )
            # Create Indexes immediately
            col.create_index(distance_metric="cosine")
            col.create_tf_idf_index(name="sparse_idx", k1=1.5, b=0.75)
            return col

    def manual_hybrid_search(self, dense_vec: list, text_query: str, top_k: int = 10):
        """
        Executes a manual POST request for Hybrid Search 
        since the SDK wrapper is experimental.
        """
        url = f"{self.client.base_url}/collections/{settings.COLLECTION_NAME}/search/hybrid"
        headers = self.client._get_headers()
        
        payload = {
            "queries": [
                {"dense": {"vector": dense_vec}},
                {"tf-idf": {"query": text_query}}
            ],
            "fusion_constant_k": 60.0,
            "top_k": top_k,
            "return_raw_text": True
        }
        
        try:
            resp = requests.post(url, headers=headers, json=payload, verify=False)
            if resp.status_code == 200:
                return resp.json().get("results", [])
            print(f"❌ Search Error: {resp.text}")
            return []
        except Exception as e:
            print(f"🚨 Connection Error: {e}")
            return []

db = CosdataManager()
