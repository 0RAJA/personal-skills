"""虚构的进程内去重示例，无外部副作用。"""


def enqueue(batch_id, seen, submitted):
    """仅在调用者复用同一个 seen 集合时跳过重复批次。"""
    if batch_id in seen:
        return False
    seen.add(batch_id)
    submitted.append(batch_id)
    return True
