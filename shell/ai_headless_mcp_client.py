#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Minimal MCP-over-HTTP (Streamable HTTP) client for garlic headless (v3).

v3: 保存/打印时自动把 garlic 返回的 JSON 载荷解码为可读文本
    （含 "code" 字段的 -> 直接输出源码；其他 dict/list -> 缩进美化）。

用法:
  python garlic_mcp.py --status
  python garlic_mcp.py --tool-list
  python garlic_mcp.py --tool get_class_source --args '{"class_name":"com.facecoll.shell.MainActivity"}' --save probes/MainActivity.java
  python garlic_mcp.py --tool search_method_by_name --args '{"method_name":"upload"}' --save probes/search_upload.txt
"""
import json, sys, argparse, urllib.request, urllib.error

BASE = "http://127.0.0.1:8650/mcp"
_sid = None
_id = [0]


def _post(body, timeout=300):
    global _sid
    req = urllib.request.Request(
        BASE, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream"})
    if _sid:
        req.add_header("Mcp-Session-Id", _sid)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code, "_body": e.read().decode("utf-8", "replace")[:800]}
    except Exception as e:
        return {"_error": repr(e)}
    sid = resp.headers.get("Mcp-Session-Id")
    if sid:
        _sid = sid
    raw = resp.read().decode("utf-8", "replace")
    if raw.lstrip().startswith("event:") or "\ndata:" in raw or raw.startswith("data:"):
        for line in raw.splitlines():
            if line.startswith("data:"):
                try:
                    return json.loads(line[5:].strip())
                except Exception:
                    pass
        return {"_raw": raw[:800]}
    try:
        return json.loads(raw)
    except Exception:
        return {"_raw": raw[:800]}


def rpc(method, params=None, notify=False, timeout=300):
    body = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        body["params"] = params
    if not notify:
        _id[0] += 1
        body["id"] = _id[0]
    return _post(body, timeout)


def initialize():
    r = rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                           "clientInfo": {"name": "hermes", "version": "1.0"}})
    rpc("notifications/initialized", {}, notify=True)
    return r


def call(tool, args=None, timeout=300):
    return rpc("tools/call", {"name": tool, "arguments": args or {}}, timeout=timeout)


def extract_text(r):
    try:
        content = r["result"]["content"]
        parts = []
        for c in content:
            if isinstance(c, dict) and c.get("text"):
                parts.append(c["text"])
        return "\n".join(parts)
    except Exception:
        return None


def pretty(txt):
    """把 garlic 的 JSON 载荷解码成可读文本。"""
    if txt is None:
        return None
    try:
        obj = json.loads(txt)
    except Exception:
        return txt
    if isinstance(obj, dict):
        if "code" in obj and isinstance(obj["code"], str):
            return obj["code"]
        return json.dumps(obj, ensure_ascii=False, indent=1)
    return json.dumps(obj, ensure_ascii=False, indent=1)


def main():
    global BASE
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--tool")
    ap.add_argument("--args", default="{}")
    ap.add_argument("--tool-list", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--limit", type=int, default=20000)
    ap.add_argument("--save", default=None, help="把解码后的完整输出写入文件")
    a = ap.parse_args()
    BASE = a.base

    init = initialize()
    if isinstance(init, dict) and "result" in init:
        si = init["result"].get("serverInfo", {})
        print(f"[init] {si.get('name')} v{si.get('version')} protocol={init['result'].get('protocolVersion')}")
    else:
        print("[init]", json.dumps(init, ensure_ascii=False)[:400])

    if a.tool_list:
        print("\n== tools/list ==")
        print(json.dumps(rpc("tools/list"), ensure_ascii=False)[:12000])
        return

    st = call("get_status")
    txt = pretty(extract_text(st)) or json.dumps(st, ensure_ascii=False)
    if a.status or a.tool:
        print("\n== get_status ==")
        print(txt[:1500])

    if a.tool:
        out = call(a.tool, json.loads(a.args))
        full = pretty(extract_text(out)) or json.dumps(out, ensure_ascii=False, indent=1)
        if a.save:
            with open(a.save, "w", encoding="utf-8") as f:
                f.write(full)
            print(f"\n[saved {len(full)} chars -> {a.save}]")
        print(f"\n== {a.tool} ==")
        print(full[: a.limit])


if __name__ == "__main__":
    main()
