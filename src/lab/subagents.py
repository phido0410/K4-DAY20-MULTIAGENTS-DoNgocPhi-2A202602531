"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use this agent to inspect the workspace, read specifications, README, docstrings, "
                "or inspect data and log files. Call this before modifying code to gather accurate facts. "
                "This agent only analyzes and never modifies files."
            ),
            "system_prompt": (
                "You are an investigative exploration agent. Your task is to explore the codebase, "
                "read documentation, inspect file contents, and report factual findings accurately. "
                "Do NOT edit or delete files. Return a concise, structured factual summary."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use this agent to execute code changes, fix functions, create new files, clean data, "
                "or run tests using shell commands after specifications are understood. Provide detailed requirements and target files."
            ),
            "system_prompt": (
                "You are a software implementer agent. Your task is to apply edits to code, create files, "
                "and run tests using the shell to verify fixes. Verify your changes pass before completing. "
                "Report exactly what changes you made and the verification results."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use this agent to independently verify completed work against instructions, "
                "docstrings, edge cases, and output formatting rules without making any changes."
            ),
            "system_prompt": (
                "You are an independent quality review agent. Your task is to verify outputs, check "
                "against task instructions and edge cases, and run regression tests. Do not edit files. "
                "Report any discrepancies or confirm full compliance."
            ),
        },
    ]
