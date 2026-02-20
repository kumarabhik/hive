from __future__ import annotations

from fastmcp import FastMCP

from aden_tools.tools.chart_tool.chart_tool import ChartSpec
from aden_tools.tools.excel_write_tool.excel_write_tool import WorkbookSpec
from aden_tools.tools.powerpoint_tool.powerpoint_tool import DeckSpec
from aden_tools.tools.word_tool.word_tool import DocSpec


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    def office_skills_schema(tool_name: str) -> dict:
        """
        Return JSON schema for Office Skills Pack input specs.
        tool_name: one of ['chart', 'excel', 'powerpoint', 'word']
        """
        name = tool_name.strip().lower()
        if name == "chart":
            return ChartSpec.model_json_schema()
        if name == "excel":
            return WorkbookSpec.model_json_schema()
        if name == "powerpoint":
            return DeckSpec.model_json_schema()
        if name == "word":
            return DocSpec.model_json_schema()
        return {"error": "unknown tool_name"}
