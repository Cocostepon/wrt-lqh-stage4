# tests/test_agent.py
import os
import sys
import tempfile
import pytest

# Ensure project root (the folder containing tools.py) is on sys.path
# This makes imports robust whether you run pytest from stage2/ or from parent folder.
HERE = os.path.dirname(__file__)          # tests/
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, ".."))  # stage2/
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools import lookup_word, solve_math, save_note
from orchestrator import execute_plan
def test_lookup_word_valid():
    res = lookup_word("agent")
    assert "代理人" in res

def test_lookup_word_empty():
    res = lookup_word("")
    assert "请输入要查询的单词" in res

def test_solve_math_valid():
    res = solve_math("2+3*4")
    assert "计算结果为：14" in res

def test_solve_math_invalid():
    res = solve_math("abc")
    assert "格式不正确" in res

def test_save_note_valid(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    res = save_note("测试笔记")
    assert "记录成功" in res
    assert (tmp_path/"notes.txt").exists()

def test_save_note_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    res = save_note(" ")
    assert "笔记内容不能为空" in res

def test_execute_plan_simple(tmp_path, monkeypatch):
    # 测试多步：先算 2+2 再保存结果
    steps = [
        {"tool":"solve_math","args":{"expr":"2+2"},"desc":"calc"},
        {"tool":"save_note","args":{"content":"结果 $ctx.last_result"},"desc":"save"}
    ]
    monkeypatch.chdir(tmp_path)
    e = execute_plan(steps)
    assert e["ok"]
    assert "记录成功" in e["summary"] or "结果 4" in e["summary"]

def test_execute_plan_ask():
    # 测试 ask 步骤
    steps = [{"tool":"ask","args":{"question":"缺少参数"},"desc":"ask"}]
    e = execute_plan(steps)
    assert not e["ok"] and "ask" in e
