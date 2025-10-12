import os
import json
import shutil
from typing import Dict
import re

class AndroidTemplateManager:
    """Android模板管理器"""
    
    def __init__(self, templates_dir: str):
        self.templates_dir = templates_dir
        self.available_templates = {
            'empty_activity': 'Empty Activity模板',
            # 'basic_activity': 'Basic Activity模板',
            # 'bottom_navigation': 'Bottom Navigation模板'
        }
    
    def create_from_template(self, template_name: str, output_dir: str, project_name: str) -> str:
        """从模板创建项目"""
        template_path = os.path.join(self.templates_dir, template_name)
        project_path = os.path.join(output_dir, project_name)
        
        if not os.path.exists(template_path):
            raise ValueError(f"模板不存在: {template_name}")
        
        # 复制模板到目标目录
        shutil.copytree(template_path, project_path)
        print(f"从模板 '{template_name}' 创建项目: {project_path}")
        
        return project_path
    
    def get_template_info(self, template_name: str) -> Dict:
        """获取模板信息"""
        template_path = os.path.join(self.templates_dir, template_name)
        info_file = os.path.join(template_path, 'template_info.json')
        
        if os.path.exists(info_file):
            with open(info_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认信息
        return {
            'package_name': 'com.example.myapp',
            'main_activity': 'MainActivity',
            'replaceable_files': ['MainActivity.java', 'activity_main.xml'],
            'configurable_items': ['package_name', 'app_name', 'activity_name']
        }

class TemplateFileReplacer:
    """模板文件替换器"""
    
    def __init__(self):
        self.file_mapping = {
            # 大模型生成的文件名 -> 模板中的文件路径
            'MainActivity.java': 'app/src/main/java/{package_path}/MainActivity.java',
            'activity_main.xml': 'app/src/main/res/layout/activity_main.xml',
            'AndroidManifest.xml': 'app/src/main/AndroidManifest.xml',
            'strings.xml': 'app/src/main/res/values/strings.xml'
        }
    
    def replace_files(self, project_path: str, generated_files: Dict[str, str], 
                     template_info: Dict) -> Dict:
        """替换模板中的文件"""
        
        replacement_log = {
            'replaced_files': [],
            'skipped_files': [],
            'errors': []
        }
        
        # 分析生成的文件，提取配置信息
        config = self._analyze_generated_files(generated_files)
        
        # 更新项目配置
        self._update_project_config(project_path, config, template_info)
        
        # 替换文件
        for gen_filename, gen_content in generated_files.items():
            try:
                success = self._replace_single_file(
                    project_path, gen_filename, gen_content, config
                )
                
                if success:
                    replacement_log['replaced_files'].append(gen_filename)
                else:
                    replacement_log['skipped_files'].append(gen_filename)
                    
            except Exception as e:
                replacement_log['errors'].append(f"{gen_filename}: {str(e)}")
        
        return replacement_log
    
    def _analyze_generated_files(self, generated_files: Dict[str, str]) -> Dict:
        """分析生成的文件，提取配置信息"""
        config = {
            'package_name': 'com.example.myapp',
            'main_activity': 'MainActivity',
            'app_name': 'My App'
        }
        
        # 从Java文件中提取包名和类名
        for filename, content in generated_files.items():
            if filename.endswith('.java'):
                package_match = re.search(r'package\s+([\w.]+)', content)
                if package_match:
                    config['package_name'] = package_match.group(1)
                
                class_match = re.search(r'class\s+(\w+)', content)
                if class_match:
                    config['main_activity'] = class_match.group(1)
                break
        
        # 从AndroidManifest中提取应用名
        manifest_content = generated_files.get('AndroidManifest.xml', '')
        if manifest_content:
            label_match = re.search(r'android:label="([^"]+)"', manifest_content)
            if label_match and not label_match.group(1).startswith('@'):
                config['app_name'] = label_match.group(1)
        
        return config
    
    def _replace_single_file(self, project_path: str, filename: str, 
                           content: str, config: Dict) -> bool:
        """替换单个文件"""
        
        if filename in self.file_mapping:
            # 计算目标路径
            target_pattern = self.file_mapping[filename]
            if '{package_path}' in target_pattern:
                package_path = config['package_name'].replace('.', '/')
                target_pattern = target_pattern.format(package_path=package_path)
            
            target_path = os.path.join(project_path, target_pattern)
        else:
            target_path = os.path.join(project_path, filename)
            if os.path.exists(target_path):
                print(f"⚠️ 未知文件类型，但是找到对应文件了: {filename}")
            else:
                print(f"⚠️ 未知文件类型，直接创造新的空文件: {filename}")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # 写入内容
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 替换文件: {filename} -> {os.path.relpath(target_path, project_path)}")
        print(f"✅ 替换文件: {filename} -> {content[:10]}")
        return True
    
    def _update_project_config(self, project_path: str, config: Dict, template_info: Dict):
        """更新项目配置"""
        
        # 更新build.gradle中的包名
        self._update_build_gradle(project_path, config)
        
        # 更新strings.xml中的app_name（如果没有被替换）
        self._update_strings_xml(project_path, config)
        
        # 更新AndroidManifest.xml中的包名（如果没有被替换）
        self._update_manifest_package(project_path, config)
    
    def _update_build_gradle(self, project_path: str, config: Dict):
        """更新app/build.gradle"""
        build_gradle_path = os.path.join(project_path, 'app/build.gradle')
        
        if not os.path.exists(build_gradle_path):
            return
        
        with open(build_gradle_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新namespace和applicationId
        content = re.sub(
            r'namespace\s+[\'"][^\'"]+[\'"]',
            f"namespace '{config['package_name']}'",
            content
        )
        content = re.sub(
            r'applicationId\s+[\'"][^\'"]+[\'"]',
            f"applicationId \"{config['package_name']}\"",
            content
        )
        
        with open(build_gradle_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"🔧 更新build.gradle: 包名 -> {config['package_name']}")
    
    def _update_strings_xml(self, project_path: str, config: Dict):
        """更新strings.xml（仅当未被替换时）"""
        strings_path = os.path.join(project_path, 'app/src/main/res/values/strings.xml')
        
        if not os.path.exists(strings_path):
            return
        
        with open(strings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新app_name
        content = re.sub(
            r'<string name="app_name">[^<]*</string>',
            f'<string name="app_name">{config["app_name"]}</string>',
            content
        )
        
        with open(strings_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"🔧 更新strings.xml: 应用名 -> {config['app_name']}")
    
    def _update_manifest_package(self, project_path: str, config: Dict):
        """更新AndroidManifest.xml包名（仅当未被替换时）"""
        manifest_path = os.path.join(project_path, 'app/src/main/AndroidManifest.xml')
        
        if not os.path.exists(manifest_path):
            return
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新package属性
        content = re.sub(
            r'package="[^"]+"',
            f'package="{config["package_name"]}"',
            content
        )
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"🔧 更新AndroidManifest.xml: 包名 -> {config['package_name']}")
   

def setup_templates(templates_dir: str):
    """设置模板目录"""
    os.makedirs(templates_dir, exist_ok=True)
    
    # 可以通过以下方式准备模板：
    # 1. 手动在Android Studio中创建项目，然后复制到templates_dir
    # 2. 使用Android SDK的模板
    # 3. 准备预配置的最小项目
    
    empty_activity_template = os.path.join(templates_dir, 'empty_activity')
    
    if not os.path.exists(empty_activity_template):
        print("请手动准备Empty Activity模板:")
        print(f"1. 在Android Studio中创建Empty Activity项目")
        print(f"2. 将项目复制到: {empty_activity_template}")
        print(f"3. 创建template_info.json文件")
        
        # 创建template_info.json示例
        template_info = {
            "package_name": "com.example.template",
            "main_activity": "MainActivity",
            "replaceable_files": [
                "MainActivity.java",
                "activity_main.xml",
                "AndroidManifest.xml"
            ],
            "configurable_items": [
                "package_name",
                "app_name",
                "MainActivity"
            ]
        }
    
    info_file = os.path.join(empty_activity_template, 'template_info.json')
    os.makedirs(empty_activity_template, exist_ok=True)
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(template_info, f, indent=2)
   
if __name__ == "__main__":
    setup_templates("./templates")