import requests

from utils import base_url,id,key


class DifyKnowledgeBase:
    def __init__(self,separator="#", max_tokens=1000, chunk_overlap=150,sub_separator="#", sub_max_tokens=1000, sub_chunk_overlap=150):
        self.base_url = base_url
        self.id = id
        self.key = key
        self.database_info = None

        # RAG切分配置
        self.separator = separator
        self.max_tokens = max_tokens
        self.chunk_overlap = chunk_overlap
        self.sub_separator = sub_separator
        self.sub_max_tokens = sub_max_tokens
        self.sub_chunk_overlap = sub_chunk_overlap

    def get_database_info(self):
        url = f"{self.base_url}/datasets/{self.id}"
        headers = {"Authorization": f"Bearer {self.key}"}
        response = requests.get(url, headers=headers)
        print(response.json())
        return response.json()


    def database_post(self,title, content, database_info):
        '''将保存的文件通过路径的形式传输给database'''
        import requests

        url = f"{self.base_url}/datasets/{self.id}/document/create-by-text"

        # 从数据库信息中提取相关字段
        retrieval_model_info = database_info.get("retrieval_model_dict", {})
        reranking_model_info = retrieval_model_info.get("reranking_model", {})

        # 根据 doc_form 设置不同的 process_rule
        # 父子分段模式现在没处理好
        if database_info.get("doc_form") == "hierarchical_model":
            process_rule = {
                "mode": "hierarchical",
                "rules": {
                    "pre_processing_rules": [],
                    "segmentation": {
                        "separator": self.separator,
                        "max_tokens": self.max_tokens,
                        "chunk_overlap": self.chunk_overlap
                    },
                    "parent_mode": "full-doc",
                    "subchunk_segmentation": {
                        "separator": self.sub_separator,
                        "max_tokens": self.sub_max_tokens,
                        "chunk_overlap": self.sub_chunk_overlap
                    }
                }
            }
        else:
            process_rule = {
                "pre_processing_rules": [
                    {
                        "id": "remove_extra_spaces",
                        "enabled": True
                    },
                    {
                        "id": "remove_urls_emails",
                        "enabled": True
                    }
                ],
                "segmentation": {
                    "separator": self.separator,
                    "max_tokens": self.max_tokens,
                    "chunk_overlap": self.chunk_overlap
                },
                "mode": "automatic"
            }


        payload = {
            "name": title,
            "text": content,
            "indexing_technique": database_info.get("indexing_technique", "high_quality"),
            "doc_form": database_info.get("doc_form", "hierarchical_model"),
            "doc_language": "Chinese",
            "process_rule": process_rule,
            "retrieval_model": {
                "search_method": retrieval_model_info.get("search_method", "hybrid_search"),
                "reranking_enable": retrieval_model_info.get("reranking_enable", True),
                "reranking_mode": reranking_model_info.get("reranking_model_name", "BAAI/bge-reranker-v2-m3"),
                "top_k": retrieval_model_info.get("top_k", 3),
                "score_threshold_enabled": retrieval_model_info.get("score_threshold_enabled", False),
                "score_threshold": retrieval_model_info.get("score_threshold", 0),
                "weights": retrieval_model_info.get("weights", None)
            },
            "embedding_model_provider": database_info.get("embedding_model_provider", "langgenius/siliconflow/siliconflow"),
            "embedding_model": database_info.get("embedding_model", "BAAI/bge-m3")
        }

        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        print(response.json())

    def datebase_post_pipeline(self,title, content):
        if self.database_info is None:
            self.database_info = self.get_database_info()
        # 然后使用该信息创建文档
        self.database_post(title, content, self.database_info)
