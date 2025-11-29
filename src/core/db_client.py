import time
import os
import sys
import requests
from ..config import settings

class CosdataManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CosdataManager, cls).__new__(cls)
            try:
                Client = None
                # 1) Prefer bundled SDK if present
                sdk_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "cosdata-sdk-python",
                    "src",
                )
                if os.path.isdir(sdk_path):
                    if sdk_path not in sys.path:
                        sys.path.insert(0, sdk_path)
                    try:
                        from cosdata import Client as _Client
                        Client = _Client
                    except Exception:
                        Client = None

                # 2) Try installed cosdata_client
                if Client is None:
                    try:
                        from cosdata_client import Client as _Client
                        Client = _Client
                    except Exception:
                        Client = None

                # 3) Try installed cosdata
                if Client is None:
                    try:
                        from cosdata import Client as _Client
                        Client = _Client
                    except Exception:
                        Client = None

                if Client is None:
                    raise ImportError("Unable to locate Cosdata Client class from any known package")
                cls._instance.client = Client(
                    host=settings.COSDATA_HOST,
                    username=settings.COSDATA_USER,
                    password=settings.COSDATA_PASS,
                    verify=False
                )
            except Exception as e:
                print(f"Warning: DB Connection failed on init: {e}")
                cls._instance.client = None
        return cls._instance

    def get_collection(self, reset: bool = False):
        if not self.client:
             raise Exception("Database Client not initialized. Check server status.")

        if reset:
            try:
                self.client.get_collection(settings.COLLECTION_NAME).delete()
                print(f"🧹 Collection '{settings.COLLECTION_NAME}' deleted.")
                time.sleep(1)
            except Exception:
                pass

        try:
            if not reset:
                return self.client.get_collection(settings.COLLECTION_NAME)
            raise Exception("Force create")
        except:
            print(f"🚀 Creating collection '{settings.COLLECTION_NAME}'...")
            col = self.client.create_collection(
                name=settings.COLLECTION_NAME,
                dimension=384,
                tf_idf_options={"enabled": True}
            )
            col.create_index(distance_metric="cosine")
            col.create_tf_idf_index(name="sparse_idx", k1=1.5, b=0.75)
            return col

    def manual_hybrid_search(self, dense_vec: list, text_query: str, top_k: int = 10, fusion_k: float = 60.0):
        if not self.client: return []
        
        url = f"{self.client.base_url}/collections/{settings.COLLECTION_NAME}/search/hybrid"
        headers = self.client._get_headers()
        
        payload = {
            "queries": [
                {"dense": {"vector": dense_vec}},
                {"tf-idf": {"query": text_query}}
            ],
            "fusion_constant_k": float(fusion_k),
            "top_k": top_k,
            "return_raw_text": True
        }
        
        try:
            resp = requests.post(url, headers=headers, json=payload, verify=False)
            if resp.status_code == 200:
                return resp.json().get("results", [])
            print(f"❌ Search Error ({resp.status_code}): {resp.text}")
            return []
        except Exception as e:
            print(f"🚨 Connection Error: {e}")
            return []

db = CosdataManager()