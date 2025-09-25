import requests

base_url = "http://localhost/v1"
key = "dataset-1D8BWciglQNEnBa4kJlSvuo3"
id = "fa870eaa-a664-428a-8eaf-82b1de8f9092"


def get_database_info():
    url = f"{base_url}/datasets/{id}"
    headers = {"Authorization": f"Bearer {key}"}
    response = requests.get(url, headers=headers)
    print(response.json())
    return response.json()


def database_post(title, content, database_info):
    '''将保存的文件通过路径的形式传输给database'''
    import requests

    url = f"{base_url}/datasets/{id}/document/create-by-text"

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
                    "separator": "#",
                    "max_tokens": 1000,
                    "chunk_overlap": 150
                },
                "parent_mode": "full-doc",
                "subchunk_segmentation": {
                    "separator": "#",
                    "max_tokens": 999,
                    "chunk_overlap": 150
                }
            }
        }
    else:
        process_rule = {"mode": "automatic"}

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
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.json())

def datebase_post_pipeline(title, content):
    database_info_response = get_database_info()  # 假设这个函数返回响应数据
    # 然后使用该信息创建文档
    database_post(title, content, database_info_response)
