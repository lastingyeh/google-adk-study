"""
適用於 ADK 代理的簡單數學工具。
"""


def add_numbers(a: float, b: float) -> float:
    """
    將兩個數字相加。

    參數:
        a: 第一個數字
        b: 第二個數字

    傳回:
        a 和 b 的和
    """
    return a + b


def subtract_numbers(a: float, b: float) -> float:
    """
    從 a 減去 b。

    參數:
        a: 第一個數字
        b: 第二個數字

    傳回:
        差 (a - b)
    """
    return a - b


def multiply_numbers(a: float, b: float) -> float:
    """
    將兩個數字相乘。

    參數:
        a: 第一個數字
        b: 第二個數字

    傳回:
        a 和 b 的積
    """
    return a * b


def divide_numbers(a: float, b: float) -> float:
    """
    將 a 除以 b。

    參數:
        a: 分子
        b: 分母

    傳回:
        商 (a / b)

    引發:
        ValueError: 如果 b 為零
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
