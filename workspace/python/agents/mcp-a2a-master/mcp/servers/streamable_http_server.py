"""
重點摘要:
- **核心概念**: MCP HTTP Server 範例。
- **關鍵技術**: `FastMCP`, `Pydantic` (資料驗證), `async/await`。
- **重要結論**: 實作了一個簡單的算術加法工具，並透過 HTTP SSE (Server-Sent Events) 暴露服務。
"""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field


class ArithmeticInput(BaseModel):
    a: float = Field(..., description="第一個數字 (First number)")
    b: float = Field(..., description="第二個數字 (Second number)")


class ArithmeticOutput(BaseModel):
    result: float = Field(
        ..., description="算術運算的結果 (Result of the arithmetic operation)"
    )
    expression: str = Field(..., description="評估的表達式 (Expression evaluated)")


mcp = FastMCP(
    "arithmetic_server",
    host="localhost",
    port=3000,
    stateless_http=True,
)


@mcp.tool("add_numbers")
async def add_numbers(input: ArithmeticInput) -> ArithmeticOutput:
    """
    將兩個數字相加並回傳結果。
    Add two numbers and return the result.

    Args:
        input (ArithmeticInput): 包含兩個要相加的數字的輸入。 (Input containing two numbers to add.)

    Returns:
        ArithmeticOutput: 包含結果和評估表達式的輸出。 (Output containing the result and the expression evaluated.)
    """
    result = input.a + input.b
    expression = f"{input.a} + {input.b} = {result}"
    return ArithmeticOutput(result=result, expression=expression)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
