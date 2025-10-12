from android_env import UIHierarchy, AndroidController
from pathlib import Path
import subprocess
import json
import cv2
import time
import xml.etree.ElementTree as ET
from typing import List, Tuple, Dict, Optional, Any

def get_connected_devices():
    # 执行adb devices命令
    output = subprocess.check_output(['adb', 'devices']).decode('utf-8')
    
    # 分割输出文本，过滤掉标题行和空行，获取设备列表
    devices = [line.split('\t')[0] for line in output.splitlines()[1:] if line.strip()]
    
    return devices

def get_only_device():
    # 获取当前连接的设备
    devices = get_connected_devices()
    
    # 如果没有设备连接，返回None
    if not devices:
        return None
    
    # 如果有多个设备连接，返回None
    if len(devices) > 1:
        return None
    
    return devices[0]

def get_hierarchy(ctl: AndroidController) -> UIHierarchy:
    '''
    Get the current UI hierarchy from the AndroidController
    '''
    hierarchy_str = ctl.dumpstr()
    hierarchy = UIHierarchy(ET.fromstring(hierarchy_str))
    return hierarchy

def prompt_type():
    '''
    Prompt the user to input the type of single step
    '''
    print("\nPlease select the type of single step:")
    while True:
        step_type = input("Enter step type (click, input, longclick, adb_command, restart, visible, invisible, stop, back):\n").lower()
        if step_type in ["click", "longclick", "input", "adb_command", "restart", "visible", "invisible", "stop", "back"]:
            return step_type
        else:
            print("Invalid step type, please try again.")


def get_element(hierarchy: UIHierarchy, target: Dict[str, Any]) -> Optional[Any]:
    for element in hierarchy.elements():
        match = True
        for attrib, value in target.items():
            if attrib == "index":
                # 处理index属性
                if element._index != int(value):
                    match = False
                    break
            elif attrib not in element._attrib or element._attrib[attrib] != value:
                match = False
                break
        if match:
            return element
    return None

def collect_single_widget(ctl: AndroidController) -> Dict:
    hierarchy = get_hierarchy(ctl)
    rules = input("\nEnter element match rules with format (key1:value1;key2:value2;...)\n(the key must be element attribute(e.g. resource-id, content-desc, text, index)):\n").split(";")
    rules = {rule.split(":")[0]: rule.split(":",1)[1].replace(r"\n", "\n") for rule in rules}
    element = get_element(hierarchy, rules)
    if element is None:
        print("\nNo matching element found, please try again.")
        return collect_single_widget(ctl)
    return rules

def collect_invisible_widget(ctl: AndroidController) -> Dict:
    hierarchy = get_hierarchy(ctl)
    rules = input("\nEnter invisible element match rules with format (key1:value1;key2:value2;...)\n(the key must be element attribute(e.g. resource-id, content-desc, text, index)):\n").split(";")
    rules = {rule.split(":")[0]: rule.split(":",1)[1] for rule in rules}
    element = get_element(hierarchy, rules)
    if element is None:
        return rules
    else:
        print("\nThe element is visible, please try again.")
        return collect_invisible_widget(ctl)

def collect_step(ctl: AndroidController) -> Dict:
    '''
    Collect a step of action or verification
    '''
    ret = dict()
    ret["type"] = prompt_type()
    ret["package"] = ctl.activity()[0]
    if ret["type"] in ["click", "longclick", "input", "adb_command", "restart"]:
        if ret["type"] == "adb_command":
            ret["cmdline"] = input("Enter adb command line:\n")
            if ret["cmdline"].startswith("push "):
                cmdlines = ret["cmdline"].split(" ")
                if len(cmdlines) != 3:
                    print("Invalid adb command, push command must have exactly 2 arguments like 'push xxx yyy', please try again.")
                    return collect_step(ctl)
                push_cmd, src, dst = cmdlines
                ctl.device.push(src, dst)
            elif ret["cmdline"].startswith("pull "):
                cmdlines = ret["cmdline"].split(" ")
                if len(cmdlines) != 3:
                    print("Invalid adb command, pull command must have exactly 2 arguments like 'pull xxx yyy', please try again.")
                    return collect_step(ctl)
                pull_cmd, src, dst = cmdlines
                ctl.device.pull(src, dst)
            else:
                ctl.shell(ret["cmdline"])
        elif ret["type"] == "restart":
            ctl.stop_app(ctl.app_pkg_name)
            ctl.start_app(ctl.app_pkg_name)
        else:
            ret["target"] = collect_single_widget(ctl)
            if ret["type"] == "input":
                ret["message"] = input("Enter input text:\n")
            hierarchy = get_hierarchy(ctl)
            if ret["type"] == "click":
                print(hierarchy, ret["target"])
                element = get_element(hierarchy, ret["target"])
                bounds = element._bounds
                x, y = (bounds[0] + bounds[2]) // 2, (bounds[1] + bounds[3]) // 2
                ctl.click(x, y)
            elif ret["type"] == "longclick":
                element = get_element(hierarchy, ret["target"])
                bounds = element._bounds
                x, y = (bounds[0] + bounds[2]) // 2, (bounds[1] + bounds[3]) // 2
                ctl.tap_hold(x, y, 2)
            elif ret["type"] == "input":
                element = get_element(hierarchy, ret["target"])
                bounds = element._bounds
                x, y = (bounds[0] + bounds[2]) // 2, (bounds[1] + bounds[3]) // 2
                ctl.click(x, y)
                ctl.input(ret["message"], clear=True)
    elif ret["type"] in ["visible", "invisible"]:
        if ret["type"] == "visible":
            ret["target"] = collect_single_widget(ctl)
        else:
            ret["target"] = collect_invisible_widget(ctl)
    elif ret["type"] == "back":
        ctl.back()
    elif ret["type"] == "stop":
        return None
    else:
        raise ValueError(f"Unsupported step type: {ret['type']}")

    return ret

def collect_widget_test(ctl) -> Tuple[List[Dict], Dict, List[Dict]]:
    '''
    Collect widget test case, return pre-condition, action and post-condition
    '''
    print("\nCollecting widget test case, please follow the instructions.")
    pre_condition = []
    action = {}
    post_condition = []

    # collect pre-condition
    print("\nCollecting pre-condition, please follow the instructions.")
    print("Not Implemented.")
    # while True:
    #     condition = input("Enter pre-condition (or press Enter to finish):\n")
    #     if condition == "":
    #         break
    #     pre_condition.append(condition)

    # collect action
    print("\nCollecting action, please follow the instructions.")
    action = collect_step(ctl)

    # collect post-condition
    print("\nCollecting post-condition, please follow the instructions.")
    while True:
        step = collect_step(ctl)
        if step == None:
            break
        else:
            post_condition.append(step)
    return pre_condition, action, post_condition

def collect_functional_test(ctl: AndroidController) -> List[Dict]:
    '''
    Collect functional test case, return a sequence of steps
    '''
    print("\nCollecting functional test case, please follow the instructions.")
    hierarchies = [ctl.dumpstr()]
    screenshots = [ctl.capture_screen(format="pillow").convert("RGB")]
    seqs = []
    while True:
        step = collect_step(ctl)
        if step == None:
            break
        else:
            seqs.append(step)
        hierarchies.append(ctl.dumpstr())
        screenshots.append(ctl.capture_screen(format="pillow").convert("RGB"))
    return seqs, hierarchies, screenshots

if __name__ == "__main__":
    
    collect_config_path = Path("collect_config.json")
    if collect_config_path.exists():
        with open(collect_config_path, 'r', encoding='utf-8') as f:
            collect_config = json.load(f)
        port = collect_config.get("port")
        task_name = collect_config.get("task_name")
        apk_path = collect_config.get("apk_path")
    else:

        port = get_only_device()

        if port is None:
            print("\nUse 'adb devices' to check connected devices.\n")
            port = input("Enter emulator port (example: emulator-5554):\n")

        task_name = input("\nEnter task name:\n")
        apk_path = input("\nEnter APK path:\n")
        
    task_info_path = Path("tasks") / task_name / "task_info.json"

    with open(task_info_path) as f:
        task_info = json.load(f)
    
    package_name = task_info["package_name"]
    
    ctl = AndroidController(port, package_name)
    ctl.uninstall_app(package_name)
    ctl.install_app(package_name, apk_path)
    permissions = task_info.get("permissions", [])
    print(f"\nGranting permissions: {permissions}")
    ctl.grant_permission(permissions)
    ctl.start_app(package_name)
    
    task_type = input("\nEnter task type, 0 for widget test and 1 for functional test:\n")
    if task_type not in ["0", "1"]:
        print("\nInvalid task type, please try again.")
        exit(1)
    
    if task_type == "0":
        trace_dir = Path("tasks") / task_name / "widget_tests"
        num = len(list(trace_dir.glob('test*.json')))
        case_path = trace_dir / f"test{num + 1}.json"
        pre_condition, action, post_condition = collect_widget_test(ctl)
        print(pre_condition, action, post_condition)
        with open(case_path, 'w', encoding='utf-8') as f:
            json.dump({
                "pre_condition": pre_condition,
                "action": action,
                "post_condition": post_condition
            }, f, indent=4)
        task_info["widget_test_num"] += 1
        with open(task_info_path, 'w', encoding='utf-8') as f:
            json.dump(task_info, f, indent=4)
        
    else:
        trace_dir = Path("tasks") / task_name / "functional_tests"
        num = len(list(trace_dir.glob('test*.json')))
        case_path = trace_dir / f"test{num + 1}.json"
        seqs, hierarchies, screenshots = collect_functional_test(ctl)
        trace_dir.mkdir(exist_ok=True)
        with open(case_path, 'w', encoding='utf-8') as f:
            json.dump(seqs, f, indent=4)
        task_info["functional_test_num"] += 1
        with open(task_info_path, 'w', encoding='utf-8') as f:
            json.dump(task_info, f, indent=4)
        case_dir = Path("tasks") / task_name / "functional_tests" / f"test{num + 1}"
        case_dir.mkdir(parents=True, exist_ok=True)
        for i, hierarchy in enumerate(hierarchies):
            with open(case_dir / f"hierarchy_{i}.xml", 'w', encoding='utf-8') as f:
                f.write(hierarchy)
        for i, screenshot in enumerate(screenshots):
            # screenshot: PIL.Image
            screenshot.save(case_dir / f"screenshot_{i}.png")
