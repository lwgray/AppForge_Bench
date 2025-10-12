#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
evaluate_app.py  —— 端到端 APK 评测脚本（依赖 ~/android_env/controller.py）

步骤
────
1. adb 安装 APK
2. 使用 AndroidController 启动 / 操控应用
3. 按 tests_config.json 执行测试
4. 生成 evaluation_report.json
5. 所有测试通过时退出码为 0，否则为 1

示例:
    python evaluate_app.py \
        --apk-path ./output/app-debug.apk \
        --android-sdk-path $ANDROID_HOME \
        --device-id emulator-5554 \
        --tests-config ./tests_config.json
"""
import argparse
import json
import os
import re
# import cv2
import time
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from android_env import AndroidController, UIHierarchy
import xml.etree.ElementTree as ET

# ──────────────────────────────────────────────────────────────
# Evaluator
# ──────────────────────────────────────────────────────────────
class Evaluator:
    
    def __init__(self, device_id: str, apk_path: Path, pkg_name: str, task: str):
        self.device_id = device_id
        self.apk_path = apk_path
        self.pkg_name = pkg_name
        self.task = task
        self.ctrl = AndroidController(device_id, pkg_name)  # 使用 uiautomator2 控制
        task_info_path = Path(".") / "tasks" / task / "task_info.json"
        with open(task_info_path, "r", encoding="utf-8") as f:
            self.task_info = json.load(f)
        self.permissions = self.task_info.get("permissions", [])
        self.widget_test_num = self.task_info.get("widget_test_num", 0)
        self.functional_test_num = self.task_info.get("functional_test_num", 0)
        self.screenshot = False
        
    def init_env(self):
        """重置环境，确保 APK 重新安装，打开 APP"""
        if not self.apk_path.exists():
            raise FileNotFoundError(f"APK 文件不存在: {self.apk_path}")
        for _ in range(5):
            self.ctrl.uninstall_app(self.pkg_name)
            self.ctrl.install_app(self.pkg_name, self.apk_path)
            print(self.permissions)
            self.ctrl.grant_permission(self.permissions)
            self.ctrl.start_app(self.pkg_name)
            current_app = self.ctrl.device.app_current()
            time.sleep(0.5)
            if current_app['package'] == self.pkg_name:
                break
        
    def reset_env(self):
        """重置环境P"""
        self.ctrl.uninstall_app(self.pkg_name)
        
        
    def _debug(self):
        """调试方法，打印当前 UI 层级结构"""
        print("=" * 10, "debug", "=" * 10)
        hierarchy = self.get_hierarchy()
        for element in hierarchy.elements():
            print(f"Element: {element._attrib}")
        print("=" * 30)
        
    def get_hierarchy(self) -> UIHierarchy:
        hierarchy_str = self.ctrl.dumpstr()
        if not hierarchy_str:
            raise RuntimeError("无法获取 UI 层级结构")
        return UIHierarchy(ET.fromstring(hierarchy_str))
        
    def get_element(self, target: Dict[str, Any]) -> Optional[Any]:
        def better_compare(v1,v2):
            def are_strings_equal_ignoring_special_chars(s1, s2):
                # 移除非字母数字字符，并转换为小写（忽略大小写）
                pattern = re.compile(r'[^a-zA-Z0-9]')
                s1_clean = pattern.sub('', s1).lower()
                s2_clean = pattern.sub('', s2).lower()
                return s1_clean == s2_clean

            if are_strings_equal_ignoring_special_chars(v1,v2):
                return True
            
            try:
                num1 = float(v1)  # 使用float可以处理整数和小数
                num2 = float(v2)
                return math.fabs(num1-num2) < 0.00001
            except ValueError:
                0
            
            return False
            
        hierarchy = self.get_hierarchy()
        for element in hierarchy.elements():
            match = True
            for attrib, value in target.items():
                if attrib == "index":
                    # 处理index属性
                    if element._index != int(value):
                        match = False
                        break
                elif attrib == "resource-id":
                    if attrib not in element._attrib or value.split(':')[-1].lower() not in element._attrib[attrib].lower():
                        match = False
                        break
                elif attrib not in element._attrib or not better_compare(element._attrib[attrib],value):
                    match = False
                    break
            if match:
                return element
        return None
    
    def get_screenshot(self):
        self.screenshot_id += 1
        assert 0
        # cv2.imwrite(f'screenshots/{self.screenshot_id}.jpg', self.ctrl.capture_screen())
        
        
    def perform_action(self, action: Dict[str, Any]):
        # print(action)
        # input()
        action_type = action.get("type")
        if action_type == "click":
            target = action.get("target")
            element = self.get_element(target)
            if element == None:
                return {"success": False, "details": f"未找到元素: {target}"}
            x1, y1, x2, y2 = element._bounds
            mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
            self.ctrl.click(mid_x, mid_y)
        elif action_type == "longclick":
            target = action.get("target")
            element = self.get_element(target)
            if element == None:
                return {"success": False, "details": f"未找到元素: {target}"}
            x1, y1, x2, y2 = element._bounds
            mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
            self.ctrl.tap_hold(mid_x, mid_y, 2)
        elif action_type == "input":
            target = action.get("target")
            element = self.get_element(target)
            if element == None:
                return {"success": False, "details": f"未找到元素: {target}"}
            message = action.get("message", "")
            if not message:
                return {"success": False, "details": "输入内容不能为空"}
            x1, y1, x2, y2 = element._bounds
            mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
            self.ctrl.click(mid_x, mid_y)
            self.ctrl.input(message, clear=True)
        elif action_type == "restart":
            self.ctrl.stop_app(self.pkg_name)
            self.ctrl.start_app(self.pkg_name)
        elif action_type == "wait":
            time.sleep(1)
        elif action_type == "adb_command":
            cmdline = action.get("cmdline")
            if cmdline.startswith("push"):
                cmdlines = cmdline.split()
                if len(cmdlines) != 3:
                    return {"success": False, "details": "push 命令格式错误，应为 'push <src> <dst>'"}
                src, dst = cmdlines[1:3]
                self.ctrl.device.push(src, dst)
            elif cmdline.startswith("pull"):
                cmdlines = cmdline.split()
                if len(cmdlines) != 3:
                    return {"success": False, "details": "pull 命令格式错误，应为 'pull <src> <dst>'"}
                src, dst = cmdlines[1:3]
                self.ctrl.device.pull(src, dst)
            else:
                self.ctrl.shell(cmdline)
        elif action_type == "back":
            self.ctrl.back()
        else:
            raise NotImplementedError(f"未实现的操作类型: {action_type}")
        if self.screenshot:
            self.get_screenshot()
        return {"success": True}
    
    def perform_pre_condition(self, pre_conditions: List[Dict[str, Any]]):
        pass
    
    def check_post_condition(self, post_conditions: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        time.sleep(0.5)
        for cond in post_conditions:
            if cond["type"] == "visible":
                target = cond.get("target")
                element = self.get_element(target)
                if element is None:
                    self._debug()
                    return {"success": False, "details": f"未找到元素: {target}"}
            elif cond["type"] == "invisible":
                target = cond.get("target")
                element = self.get_element(target)
                if element is not None:
                    self._debug()
                    return {"success": False, "details": f"元素仍然可见: {target}"}
        return {"success": True}
    
    def run_single_widget_test(self, test_num: int):
        widget_test_path = Path(".") / "tasks" / self.task / "widget_tests" / f"test{test_num}.json"
        if not widget_test_path.exists():
            print(f"⚠️ 未找到小部件测试文件: {widget_test_path}")
            return {"success": False, "details": "未找到小部件测试文件"}
        with open(widget_test_path, "r", encoding="utf-8") as f:
            widget_test = json.load(f)
        pre_condition = widget_test.get("pre_condition", [])
        action = widget_test.get("action", {})
        post_condition = widget_test.get("post_condition", [])
        self.init_env()
        self.perform_pre_condition(pre_condition)   
        time.sleep(0.5)
        action_result = self.perform_action(action)
        if not action_result.get("success", True):
            self._debug()
            self.reset_env()
            return {"success": False, "details": action_result.get("details", "操作失败")}
        result = self.check_post_condition(post_condition)
        self.reset_env()
        return result

    def run_widget_tests(self):
        results = []
        for i in range(self.widget_test_num):
            results.append(self.run_single_widget_test(i + 1))
        return results
    
    def run_single_functional_test(self, test_num: int):
        functional_test_path = Path(".") / "tasks" / self.task / "functional_tests" / f"test{test_num}.json"
        if not functional_test_path.exists():
            print(f"⚠️ 未找到功能测试文件: {functional_test_path}")
            return {"success": False, "details": "未找到功能测试文件"}
        with open(functional_test_path, "r", encoding="utf-8") as f:
            functional_test = json.load(f)
        self.init_env()
        if self.screenshot:
            self.get_screenshot()
        for step in functional_test:
            time.sleep(0.5)
            waiting_times = [0.5,0.5,0.5]
            for id,ct in enumerate(waiting_times):
                type = step.get("type")
                if type in ["click", "longclick", "input", "adb_command", "restart", "wait","back"]:
                    result = self.perform_action(step)
                    if not result.get("success", True):
                        if id == len(waiting_times)-1:
                            self._debug()
                            self.reset_env()
                            return {"success": False, "details": result.get("details", "操作失败")}
                        else:
                            time.sleep(ct)
                            continue
                elif type in ["visible", "invisible"]:
                    result = self.check_post_condition([step])
                    if not result.get("success", True):
                        if id == len(waiting_times)-1:
                            self._debug()
                            self.reset_env()
                            return result
                        else:
                            time.sleep(ct)
                            continue
                else:   
                    self.reset_env()
                    raise ValueError(f"未知的操作类型: {type}")
                break
            
        self.reset_env()
        return {"success": True}
    
    def run_functional_tests(self):
        results = []
        for i in range(self.functional_test_num):
            results.append(self.run_single_functional_test(i + 1))
        return results
    
    def run_fuzzing(self, www_Name, device_id):
        self.init_env()
        
        cmd = f' ./fuzzing.sh {www_Name} {device_id}'
        os.system(cmd)
        self.reset_env()
      
    
# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser("evaluate_app with AndroidController")
    ap.add_argument("--apk-path", required=True)
    ap.add_argument("--package-name", required=True)
    ap.add_argument("--device-id", default="emulator-5554",
                    help="adb 设备序列号，如 emulator-5554")
    ap.add_argument("--task", default="calculator")
    ap.add_argument("--test", default="all")
 
    args = ap.parse_args()
    '''
    python evaluate_app.py --task Chess_Clock --test functional2screenshot --package-name 0\
    --apk-path compiler/output_v2.2.2/qwen3coder_round0/Chess_Clock/app/build/outputs/apk/debug/app-debug.apk\
    '''   
    id = (int(args.device_id.split('-')[-1])-5554)//2

        
    apk_path = Path(args.apk_path).expanduser().resolve()
    
    with open(args.apk_path.replace('app-debug.apk','output-metadata.json'),'r') as f:
        file = json.load(f)
        www_Name = file["applicationId"]
        args.package_name = www_Name
    evaluator = Evaluator(args.device_id, apk_path, args.package_name, args.task)
    
    if args.test == "widget":
        result = evaluator.run_widget_tests()
        print(result)
    elif args.test == "functional":
        result = evaluator.run_functional_tests()
        print(result)
    elif args.test == "all":
        result = evaluator.run_fuzzing(www_Name, args.device_id)
        print(result)
        result = evaluator.run_widget_tests()
        print(result)
        result = evaluator.run_functional_tests()
        print(result)
    elif args.test == "only_fuzz":
        result = evaluator.run_fuzzing(www_Name, args.device_id)
        print(result)
    elif args.test == "no_fuzz":
        # result = evaluator.run_fuzzing(www_Name, args.device_id)
        # print(result)
        result = evaluator.run_widget_tests()
        print(result)
        result = evaluator.run_functional_tests()
        print(result)
    elif "widget" in args.test:
        test_num = int(re.search(r'\d+', args.test).group())
        result = evaluator.run_single_widget_test(test_num)
        print(result)
    elif "functional" in args.test:
        test_num = int(re.search(r'\d+', args.test).group())
        if 'screenshot' in args.test:
            os.makedirs('screenshots/',exist_ok=True)
            shutil.rmtree('screenshots/')
            os.makedirs('screenshots/')
            evaluator.screenshot = True
            evaluator.screenshot_id = 0
        result = evaluator.run_single_functional_test(test_num)
        print(result)

if __name__ == "__main__":
    main()
