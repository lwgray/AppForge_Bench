import argparse
from typing import Dict,List,Optional
import subprocess
import os
import time
import shutil
import json
from create_template import AndroidTemplateManager, TemplateFileReplacer
class TemplateBasedCompiler:
    """基于模板的Android编译器"""
    
    def __init__(self, android_sdk_path: str, templates_dir: str):
        self.android_sdk_path = android_sdk_path
        self.template_manager = AndroidTemplateManager(templates_dir)
        self.file_replacer = TemplateFileReplacer()
        self.builder = AndroidBuilder(android_sdk_path)
    
    def compile_with_template(self, generated_files: Dict[str, str], 
                            output_dir: str, template_name: str = 'empty_activity', project_name: str = '') -> Dict:
        """使用模板编译生成的文件"""
        
        print(f"🚀 开始基于模板 '{template_name}' 的编译流程")
        
        result = {
            'success': False,
            'project_path': None,
            'apk_path': None,
            'template_used': template_name,
            'replacement_log': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # 1. 从模板创建项目
            if len(project_name) == 0:
                project_name = f"generated_app_{int(time.time())}"
            project_path = self.template_manager.create_from_template(
                template_name, output_dir, project_name
            )
            result['project_path'] = project_path
            
            # 2. 获取模板信息
            template_info = self.template_manager.get_template_info(template_name)
            
            # 3. 替换文件
            replacement_log = self.file_replacer.replace_files(
                project_path, generated_files, template_info
            )
            print("replace log:", replacement_log)
            result['replacement_log'] = replacement_log
            
            if replacement_log['errors']:
                result['warnings'].extend(replacement_log['errors'])
            
            # 4. 编译项目
            print("🔨 编译APK...")
            build_result = self.builder.build_apk(project_path)
            
            result['success'] = build_result['success']
            result['apk_path'] = build_result['apk_path']
            result['errors'] = build_result['errors']
            
            if result['success']:
                print(f"✅ 编译成功! APK: {result['apk_path']}")
                print(f"📊 替换了 {len(replacement_log['replaced_files'])} 个文件")
            else:
                print(f"❌ 编译失败")
                for error in result['errors']:
                    print(f"   {error}")
            
        except Exception as e:
            result['errors'].append(f"编译流程异常: {str(e)}")
            print(f"❌ 编译流程异常: {str(e)}")
        
        return result


class AndroidBuilder:
    def __init__(self, android_sdk_path: str):
        self.android_sdk_path = android_sdk_path
        self.gradle_wrapper = './gradlew'
        
    def build_apk(self, project_path: str) -> Dict:
        """编译Android项目生成APK"""
        result = {
            'success': False,
            'apk_path': None,
            'errors': [],
            'warnings': [],
            'build_output': ''
        }
        try:
            # 设置环境变量
            env = os.environ.copy()
            env['ANDROID_HOME'] = self.android_sdk_path

            # 确保gradlew有执行权限
            gradlew_path = os.path.join(project_path, 'gradlew')
            if os.path.exists(gradlew_path):
                import stat
                current_permissions = os.stat(gradlew_path).st_mode
                os.chmod(
                    gradlew_path,
                    current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                )

            # 执行Gradle编译
            cmd = [self.gradle_wrapper, 'assembleDebug']
            process = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                env=env,
                timeout=300  # 5分钟超时
            )
            
            result['build_output'] = process.stdout + process.stderr
            
            if process.returncode == 0:
                result['success'] = True
                # 查找生成的APK文件
                apk_path = self.find_generated_apk(project_path)
                result['apk_path'] = apk_path
            else:
                result['errors'] = self.parse_build_errors(process.stderr)
                
        except subprocess.TimeoutExpired:
            result['errors'].append("编译超时")
        except Exception as e:
            result['errors'].append(f"编译异常: {str(e)}")
        return result
    
    def find_generated_apk(self, project_path: str) -> Optional[str]:
        """查找生成的APK文件"""
        apk_dir = os.path.join(project_path, 'app/build/outputs/apk/debug')
        if os.path.exists(apk_dir):
            for file in os.listdir(apk_dir):
                if file.endswith('.apk'):
                    return os.path.join(apk_dir, file)
        return None
    
    def parse_build_errors(self, stderr: str) -> List[str]:
        """解析编译错误"""
        errors = []
        lines = stderr.split('\n')
        
        for line in lines:
            if 'error:' in line.lower() or 1:
                errors.append(line.strip())
                
        return errors
   
   

def read_file_to_string(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"文件 {filename} 不存在")
        return None
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None
# # by 12travellers
# def direct_build(android_sdk_path, output_dir, templates_dir, template_name):
#     compiler = TemplateBasedCompiler(
#         android_sdk_path=android_sdk_path,
#         templates_dir=templates_dir
#     )
#     result = compiler.compile_with_template(
#         generated_files={},
#         output_dir=output_dir,
#         template_name=template_name
#     )
    
#     assert result['success'], 'compilation failure'
#     return result['apk_path']
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Android App Compiler")
    parser.add_argument("--android-sdk-path", type=str, required=True, help="Android SDK path")
    parser.add_argument("--templates-dir", type=str, default="./templates", help="模板目录路径")
    parser.add_argument("--output-dir", type=str, default="./output", help="输出目录路径")
    parser.add_argument("--project-name", type=str, default="", help="项目名称；默认为时间戳")
    parser.add_argument("--generated-files", type=str, required=True, help="生成的文件路径（JSON格式）")
    parser.add_argument("--json_content_directly", action='store_true', default=False )
    args = parser.parse_args()
    
    # 2. 准备生成的文件
    file_dicts = json.load(open(args.generated_files,'r', encoding='utf-8'))
    if args.json_content_directly:
       generated_files = {k:v for k, v in file_dicts.items()} 
    else:
        generated_files = {k:read_file_to_string(v) for k, v in file_dicts.items() if read_file_to_string(v) is not None}
    # 3. 编译
    compiler = TemplateBasedCompiler(
        android_sdk_path=args.android_sdk_path,
        templates_dir=args.templates_dir
    )
    result = compiler.compile_with_template(
        generated_files=generated_files,
        output_dir=args.output_dir,
        template_name='empty_activity',
        project_name=args.project_name,
    )
    
    print(f"\n📋 编译报告:")
    print(f"成功: {result['success']}")
    print(f"使用模板: {result['template_used']}")
    print(f"替换文件: {result['replacement_log']['replaced_files']}")
    if result['success']:
        print(f"APK路径: {result['apk_path']}")