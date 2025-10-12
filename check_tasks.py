#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据 functional_tests 中缺失 target 字段的情况，生成两份测试用例清单：
1. incomplete_targets_with_owner.xlsx  —— 含缺失字段的用例及负责人
2. complete_targets_with_owner.xlsx    —— 所有 target 字段均完整的 App 及负责人

兼容需求：
- tasks/ 目录采用下划线命名（如 3d_model_viewer）
- output.xlsx 中采用空格命名（如 3D Model Viewer）

改动：合并负责人信息时 **保留 output.xlsx 的全部列**。

运行：
    python generate_test_reports.py
"""

import json
from pathlib import Path
import pandas as pd
import re
from typing import Set, Tuple


def slugify(s: str) -> str:
    """统一名称：全部转小写、空格→下划线、连续下划线折叠"""
    s = s.lower().replace(" ", "_")
    return re.sub(r"_+", "_", s.strip("_"))


def collect_tests(tasks_root: Path) -> Tuple[pd.DataFrame, Set[str]]:
    """扫描 functional_tests，返回：
    1. 缺少 resource-id / text / content-desc 的用例清单 DataFrame
    2. target 字段完整的 app_name 集合 ok_apps
    """
    records = []
    ok_apps: Set[str] = set()

    for json_path in tasks_root.rglob("functional_tests/**/*.json"):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                steps = json.load(f)
        except Exception:
            continue  # 跳过无法解析的 JSON

        if not isinstance(steps, list):
            continue

        has_incomplete_target = any(
            isinstance(step, dict)
            and isinstance(step.get("target"), dict)
            and ("resource-id" not in step["target"])
            and ("text" not in step["target"])
            and ("content-desc" not in step["target"])
            for step in steps
        )

        app_name = json_path.relative_to(tasks_root).parts[0]

        if has_incomplete_target:
            records.append(
                {
                    "app_name": app_name,
                    "app_key": slugify(app_name),
                    "test_file": str(json_path.relative_to(tasks_root)),
                }
            )
        else:
            ok_apps.add(app_name)

    df_incomplete = pd.DataFrame(records)
    return df_incomplete, ok_apps


def main():
    tasks_dir = Path("tasks")
    owner_file = Path("output.xlsx")

    out_incomplete = Path("incomplete_targets_with_owner.xlsx")
    out_complete = Path("complete_targets_with_owner.xlsx")

    if not tasks_dir.exists():
        raise FileNotFoundError("❌ 未找到 tasks 目录")
    if not owner_file.exists():
        raise FileNotFoundError("❌ 未找到 output.xlsx（需包含列 name 与 负责人）")

    # 1. 扫描
    df_incomplete, ok_apps = collect_tests(tasks_dir)

    # 2. 读取负责人表并归一化
    df_owner = pd.read_excel(owner_file, dtype=str)
    if not {"name", "负责人"}.issubset(df_owner.columns):
        raise ValueError("output.xlsx 必须包含列 'name' 和 '负责人'")
    df_owner["app_key"] = df_owner["name"].apply(slugify)

    # 3. 缺失 target 清单（保留 owner 全列）
    if not df_incomplete.empty:
        df_result_incomplete = (
            df_incomplete
            .merge(df_owner, on="app_key", how="left")
            .sort_values(["app_name", "test_file"])
            .reset_index(drop=True)
        )
        df_result_incomplete.to_excel(out_incomplete, index=False)
        print(
            f"✅ 已生成缺失 target 清单：{out_incomplete.resolve()}（{len(df_result_incomplete)} 条记录）"
        )
    else:
        print("🎉 未发现缺失 target 的用例！")

    # 4. target 完整的 App 清单（保留 owner 全列）
    ok_complete = ok_apps - set(df_incomplete["app_name"].unique())

    if ok_complete:
        df_ok = (
            pd.DataFrame(sorted(ok_complete), columns=["app_name"])
            .assign(app_key=lambda df: df["app_name"].apply(slugify))
            .merge(df_owner, on="app_key", how="left")
            .sort_values("app_name")
            .reset_index(drop=True)
        )
        df_ok.to_excel(out_complete, index=False)
        print(
            f"✅ 已生成全部 target 完整的 App 清单：{out_complete.resolve()}（{len(df_ok)} 条记录）"
        )
    else:
        print("⚠️ 未找到 target 完整的 App，或扫描结果为空。")


if __name__ == "__main__":
    main()
