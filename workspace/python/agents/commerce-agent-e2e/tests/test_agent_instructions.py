def test_root_agent_instruction_constraints():
    path = "tutorial_implementation/commerce_agent_e2e/commerce_agent/agent.py"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # 指令必須明確禁止在輸出中使用字面片語
    assert (
        "Do NOT print the literal phrase: Engaging Narrative:" in text
        or 'do NOT include the exact literal header or phrase "Engaging Narrative:"'
        in text
    ), "代理指令中未明確禁止在輸出中使用字面片語"

    # 指令必須要求儲存偏好設定並確認
    assert (
        "ALWAYS call the Preference Manager" in text or "Preferences saved." in text
    ), "在代理指令中找不到偏好設定管理員的儲存指令或確認訊息"

    # 指令必須要求使用搜尋結果中的確切 URL
    assert (
        "use REAL URLs copied from search results" in text
        or "use only URLs present in search results" in text
    ), "在代理指令中找不到 URL 出處要求"

    print("指令約束存在且正確")
