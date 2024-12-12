import asyncio
import logging
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

# ログの準備
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-datetime")

# サーバの準備
server = Server("mcp-datetime")


# 日時フォーマット関数
def format_datetime(format_type: str) -> str:
    # 毎回新しい時刻オブジェクトを生成し、タイムゾーンを考慮
    current_time = datetime.now(timezone.utc).astimezone()
    formats = {
        # 基本的な日付フォーマット
        "date": "%Y-%m-%d",  # 2024-12-10
        "date_slash": "%Y/%m/%d",  # 2024/12/10
        "date_jp": "%Y年%m月%d日",  # 2024年12月10日
        # 基本的な日時フォーマット
        "datetime": "%Y-%m-%d %H:%M:%S",  # 2024-12-10 00:54:01
        "datetime_jp": "%Y年%m月%d日 %H時%M分%S秒",  # 2024年12月10日 00時54分01秒
        "datetime_t": "%Y-%m-%dT%H:%M:%S",  # 2024-12-10T00:54:01
        # ファイル名やID用のコンパクトフォーマット
        "compact": "%Y%m%d%H%M%S",  # 20241210005401
        "compact_date": "%Y%m%d",  # 20241210
        "compact_time": "%H%M%S",  # 005401
        # ファイル名用フォーマット
        "filename_md": "%Y%m%d%H%M%S.md",  # 20241210005401.md
        "filename_txt": "%Y%m%d%H%M%S.txt",  # 20241210005401.txt
        "filename_log": "%Y%m%d%H%M%S.log",  # 20241210005401.log
        # ISO 8601フォーマット
        "iso": "%Y-%m-%dT%H:%M:%S%z",  # 2024-12-10T00:54:01+0900
        "iso_basic": "%Y%m%dT%H%M%S%z",  # 20241210T005401+0900
        # ログ用フォーマット
        "log": "%Y-%m-%d %H:%M:%S.%f",  # 2024-12-10 00:54:01.123456
        "log_compact": "%Y%m%d_%H%M%S",  # 20241210_005401
        # 時刻のみのフォーマット
        "time": "%H:%M:%S",  # 00:54:01
        "time_jp": "%H時%M分%S秒",  # 00時54分01秒
    }

    if format_type not in formats:
        raise ValueError(f"Unknown format type: {format_type}")

    try:
        return current_time.strftime(formats[format_type])
    except Exception as e:
        logger.error("Format error: %s", str(e))
        raise RuntimeError(f"Error formatting date: {str(e)}") from e


# 利用可能なツール一覧の取得
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_datetime",
            description="Get current date and time in various formats",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": """
Available formats:
- date: 2024-12-10
- date_slash: 2024/12/10
- date_jp: 2024年12月10日
- datetime: 2024-12-10 00:54:01
- datetime_jp: 2024年12月10日 00時54分01秒
- datetime_t: 2024-12-10T00:54:01
- compact: 20241210005401
- compact_date: 20241210
- compact_time: 005401
- filename_md: 20241210005401.md
- filename_txt: 20241210005401.txt
- filename_log: 20241210005401.log
- iso: 2024-12-10T00:54:01+0900
- iso_basic: 20241210T005401+0900
- log: 2024-12-10 00:54:01.123456
- log_compact: 20241210_005401
- time: 00:54:01
- time_jp: 00時54分01秒
""",
                    }
                },
                "required": ["format"],
            },
        )
    ]


# ツールの呼び出し
@server.call_tool()
async def call_tool(
    name: str, arguments: Any
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    if name == "get_datetime":
        try:
            format_type = arguments.get("format")
            if not format_type:
                raise ValueError("Format type is required")
            formatted_time = format_datetime(format_type)
            return [TextContent(type="text", text=formatted_time)]
        except ValueError as e:
            logger.error("Format error: %s", str(e))
            raise RuntimeError(str(e)) from e
    else:
        raise ValueError(f"Unknown tool: {name}")


# メイン
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
