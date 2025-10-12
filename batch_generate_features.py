#!/usr/bin/env python3
"""
批量为Jun Ren创建的54个应用生成feature描述的自动化工具
"""

import os
import subprocess
import json
from pathlib import Path
import time
import sys

# Jun Ren创建且仍存在的54个应用列表
JUN_APPS = [
    # "AnotherMonitor", "Arcticons", "audiorecorder", "Autostarts", "CityZen",
    # "createpdf", "Currency", "Daedalus", "DiskUsage", "DNS_Hero", "DNS66",
    # "Echo", "Enchanted_Fortress", "Equate", "FakeStandby", "Food_Tracker",
    # "Get_id", "Giggity", "GPS_Cockpit", "heartbeat", "Intra", 
    # "Karma_Firewall", "Little_Music_Player", "Location_Share", "LRCEditor",
    # "MedTimer", "Meme_Creator", "Morse", "Network_Tools_Library", "newpass",
    # "NextcloudServices", "openWorkout", "Oscilloscope", 
    # "periodical", "PianOli", "PrivacyBreacher", "RandomixDecisionMaker",
    # "Semitone", "Signal_Generator", "SimpleTextEditor", "Skewy",
    # "SlideshowWallpaper", "SMS_to_URL_Forwarder", "SocksTun", "SshDaemon",
    # "TimeLapseCam", "ToGoZip", "ulogger", "Vanilla_Music", "Vector_Pinball",
    # "Wave_Lines_Live_Wallpaper", "Wi_Fi_Privacy_Police"
    # "Notes",
    # "SecScanQR", 
    # "DiaguardDiabetesDiary",
    # "DailyDozen",
    "Skewy",
]

def setup_refine_directory():
    """创建refine目录结构"""
    refine_dir = Path("refine")
    refine_dir.mkdir(exist_ok=True)
    return refine_dir

def check_functional_tests(app_name):
    """检查应用是否有functional_tests目录和测试文件"""
    tests_dir = Path(f"tasks/{app_name}/functional_tests")
    if not tests_dir.exists():
        return False, "No functional_tests directory"
    
    json_files = list(tests_dir.glob("*.json"))
    if not json_files:
        return False, "No JSON test files found"
    
    return True, f"Found {len(json_files)} test files"

def run_generate_features(app_name, refine_dir):
    """为指定应用运行generate_features"""
    tests_dir = Path(f"tasks/{app_name}/functional_tests")
    output_file = refine_dir / f"{app_name}_features.txt"
    
    try:
        print(f"  🔄 Running feature generation...")
        
        # 确保环境变量被传递
        env = os.environ.copy()
        
        # 运行generate_feature.py
        result = subprocess.run([
            sys.executable, "generate_feature_open.py", 
            "--path", str(tests_dir)
        ], capture_output=True, text=True, timeout=300, env=env)  # 5分钟超时
        
        if result.returncode == 0:
            # 保存输出
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"=== Feature Description for {app_name} ===\n\n")
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\n\n=== Stderr ===\n{result.stderr}")
            
            print(f"  ✅ Success: {output_file}")
            return True, "Generated successfully"
        else:
            error_msg = f"Exit code {result.returncode}: {result.stderr}"
            print(f"  ❌ Failed: {error_msg}")
            
            # 保存错误信息
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"=== ERROR for {app_name} ===\n\n")
                f.write(f"Exit code: {result.returncode}\n")
                f.write(f"Stderr: {result.stderr}\n")
                f.write(f"Stdout: {result.stdout}\n")
            
            return False, error_msg
            
    except subprocess.TimeoutExpired:
        error_msg = "Timeout (>5 minutes)"
        print(f"  ⏰ Timeout: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Exception: {str(e)}"
        print(f"  💥 Exception: {error_msg}")
        return False, error_msg

def generate_summary_report(results, refine_dir):
    """生成汇总报告"""
    summary_file = refine_dir / "batch_summary.txt"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=== Batch Feature Generation Summary ===\n\n")
        f.write(f"Total apps processed: {len(results)}\n")
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        skipped = [r for r in results if r['status'] == 'skipped']
        
        f.write(f"Successful: {len(successful)}\n")
        f.write(f"Failed: {len(failed)}\n")
        f.write(f"Skipped: {len(skipped)}\n\n")
        
        if successful:
            f.write("=== SUCCESSFUL ===\n")
            for r in successful:
                f.write(f"✅ {r['app']}: {r['message']}\n")
            f.write("\n")
        
        if failed:
            f.write("=== FAILED ===\n")
            for r in failed:
                f.write(f"❌ {r['app']}: {r['message']}\n")
            f.write("\n")
        
        if skipped:
            f.write("=== SKIPPED ===\n")
            for r in skipped:
                f.write(f"⏭️ {r['app']}: {r['message']}\n")
            f.write("\n")
    
    print(f"\n📊 Summary report saved to: {summary_file}")

def main():
    print("🚀 Starting batch feature generation for Jun Ren's 54 apps...")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # 设置refine目录
    refine_dir = setup_refine_directory()
    print(f"📂 Refine directory: {refine_dir.absolute()}")
    
    # 检查generate_feature.py是否存在
    if not Path("generate_feature_open.py").exists():
        print("❌ Error: generate_feature_open.py not found in current directory")
        return
    
    results = []
    
    for i, app_name in enumerate(JUN_APPS, 1):
        print(f"\n[{i:2d}/{len(JUN_APPS)}] Processing {app_name}...")
        
        # 检查测试文件
        has_tests, test_info = check_functional_tests(app_name)
        
        if not has_tests:
            print(f"  ⏭️ Skipped: {test_info}")
            results.append({
                'app': app_name,
                'success': False,
                'status': 'skipped',
                'message': test_info
            })
            continue
        
        print(f"  📋 {test_info}")
        
        # 运行feature生成
        success, message = run_generate_features(app_name, refine_dir)
        results.append({
            'app': app_name,
            'success': success,
            'status': 'processed',
            'message': message
        })
        
        # 添加小延迟避免API限制
        if i < len(JUN_APPS):
            time.sleep(1)
    
    # 生成汇总报告
    generate_summary_report(results, refine_dir)
    
    # 打印最终统计
    successful = len([r for r in results if r['success']])
    total = len(results)
    print(f"\n🎉 Batch processing completed!")
    print(f"📈 Success rate: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"📁 All outputs saved in: {refine_dir.absolute()}")

if __name__ == "__main__":
    main()
