"""
針對 vision_catalog_agent 的匯入功能進行測試。

此檔案確保所有必要的模組和函式都能夠成功匯入，
包括 Agent 核心、ADK 相依性、圖片處理工具，以及 PIL/Pillow 的可用性。
"""

import pytest


def test_import_agent_module():
    """測試是否能成功匯入主要的 Agent 模組。"""
    from vision_catalog_agent import agent
    assert agent is not None


def test_import_root_agent():
    """測試是否能成功匯入 root_agent。"""
    from vision_catalog_agent import root_agent
    assert root_agent is not None


def test_import_adk_dependencies():
    """測試是否能成功匯入 ADK 的相依性套件。"""
    from google.adk.agents import Agent
    from google.adk.tools import FunctionTool
    from google.genai import types

    assert Agent is not None
    assert FunctionTool is not None
    assert types is not None


def test_import_image_utilities():
    """測試是否能成功匯入圖片處理工具。"""
    from vision_catalog_agent.agent import (
        load_image_from_file,
        optimize_image,
        create_sample_image,
        analyze_uploaded_image
    )

    assert load_image_from_file is not None
    assert optimize_image is not None
    assert create_sample_image is not None
    assert analyze_uploaded_image is not None


def test_import_agents():
    """測試是否能成功匯入 Agent 的各個元件。"""
    from vision_catalog_agent.agent import (
        vision_analyzer,
        catalog_generator,
        root_agent
    )

    assert vision_analyzer is not None
    assert catalog_generator is not None
    assert root_agent is not None


def test_import_tools():
    """測試是否能成功匯入所有的工具函式。"""
    from vision_catalog_agent.agent import (
        list_sample_images,
        generate_catalog_entry,
        generate_product_mockup,
        analyze_product_image,
        analyze_uploaded_image,
        compare_product_images
    )

    assert list_sample_images is not None
    assert generate_catalog_entry is not None
    assert generate_product_mockup is not None
    assert analyze_product_image is not None
    assert analyze_uploaded_image is not None
    assert compare_product_images is not None


def test_pil_available():
    """測試 PIL/Pillow 套件是否已安裝且可用。"""
    try:
        from PIL import Image
        assert Image is not None
    except ImportError:
        pytest.skip("PIL/Pillow 未安裝")
