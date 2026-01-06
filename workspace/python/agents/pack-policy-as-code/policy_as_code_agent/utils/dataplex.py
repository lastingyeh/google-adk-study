import os


def get_project_id():
    """從環境變數或 gcloud 設定取得 GCP 專案 ID。"""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if project_id:
        return project_id, None

    try:
        import google.auth

        _, project_id = google.auth.default()
        if project_id:
            return project_id, None
    except (ImportError, google.auth.exceptions.DefaultCredentialsError):
        pass  # 無法匯入 google.auth 或找不到預設憑證時忽略

    return (
        None,
        "未設定 GOOGLE_CLOUD_PROJECT 環境變數，且無法取得預設專案 ID。",
    )


def convert_proto_to_dict(proto_obj):
    """
    遞迴將 protobuf 物件（包含 Struct 與 RepeatedComposite）
    轉換為標準 Python 字典與列表。
    """
    if hasattr(proto_obj, "keys"):  # 類似字典
        return {key: convert_proto_to_dict(value) for key, value in proto_obj.items()}
    elif hasattr(proto_obj, "__iter__") and not isinstance(proto_obj, str):  # 類似列表
        return [convert_proto_to_dict(item) for item in proto_obj]
    else:
        return proto_obj


def entry_to_dict(entry):
    """
    手動將 Dataplex Entry 物件轉換為與現有模擬邏輯相容的字典。
    """
    entry_dict = {
        "name": entry.name,
        "entryType": entry.entry_type,
        "fullyQualifiedName": entry.fully_qualified_name,
        "parentEntry": entry.parent_entry,
        "aspects": {},
    }
    if entry.entry_source:
        entry_dict["entrySource"] = {
            "resource": entry.entry_source.resource,
            "system": entry.entry_source.system,
            "platform": entry.entry_source.platform,
            "displayName": entry.entry_source.display_name,
            "location": entry.entry_source.location,
            "labels": dict(entry.entry_source.labels),
        }
    # 將每個 aspect 轉換為字典
    for key, aspect in entry.aspects.items():
        entry_dict["aspects"][key] = {
            "aspectType": aspect.aspect_type,
            "data": convert_proto_to_dict(aspect.data),
        }
    return entry_dict
