def traverse(obj, sample_values, path=""):
    """
    遞迴遍歷 JSON 物件，將樣本值填入 sample_values 字典。
    """
    # 如果是字典型態，遞迴處理每個鍵值對
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else k  # 建立新的路徑
            traverse(v, sample_values, new_path)
    # 如果是列表型態，只遍歷第一個元素以保持樣本簡潔
    elif isinstance(obj, list):
        if obj:
            traverse(obj[0], sample_values, f"{path}[]")
    # 如果是基本型態，且該路徑尚未存值，則存入樣本值
    else:
        if path not in sample_values:
            sample_values[path] = obj
