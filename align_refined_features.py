#!/usr/bin/env python3
"""
根据应用名称对齐refined features到checked.xlsx的正确行
"""

import pandas as pd
from pathlib import Path

def extract_refined_content(file_path):
    """从features文件中提取====分割线下面的内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找====================================分割线
        split_marker = "====================================" 
        if split_marker in content:
            # 取分割线后的内容
            refined_part = content.split(split_marker, 1)[1].strip()
            return refined_part
        else:
            print(f"警告: {file_path} 中没有找到分割线")
            return ""
    except Exception as e:
        print(f"错误处理文件 {file_path}: {e}")
        return ""

def main():
    # 读取checked.xlsx文件
    try:
        checked_df = pd.read_excel('checked.xlsx')
        print(f"读取checked.xlsx成功，共 {len(checked_df)} 行")
    except Exception as e:
        print(f"错误读取checked.xlsx: {e}")
        return
    
    # 创建结果DataFrame，复制checked.xlsx的结构
    result_df = checked_df.copy()
    
    # 收集refine文件夹中的数据
    refine_dir = Path("refine")
    if not refine_dir.exists():
        print("错误: refine目录不存在")
        return
    
    feature_files = list(refine_dir.glob("*_features.txt"))
    print(f"找到 {len(feature_files)} 个features文件")
    
    # 建立应用名称到refined content的映射
    refined_data = {}
    for file_path in feature_files:
        app_name = file_path.stem.replace("_features", "")
        refined_content = extract_refined_content(file_path)
        if refined_content:
            refined_data[app_name] = refined_content
    
    # 对齐到checked.xlsx中的对应行
    updated_count = 0
    not_found = []
    
    for index, row in result_df.iterrows():
        app_name = row['name']
        
        # 查找匹配的refined feature
        if app_name in refined_data:
            result_df.at[index, 'Refined_Features'] = refined_data[app_name]
            updated_count += 1
            print(f"✅ 更新: {app_name}")
        else:
            # 尝试一些变体匹配
            found = False
            for refined_name in refined_data.keys():
                # 尝试去掉空格、下划线等进行匹配
                if (app_name.replace(' ', '').replace('_', '').replace('-', '').lower() == 
                    refined_name.replace(' ', '').replace('_', '').replace('-', '').lower()):
                    result_df.at[index, 'Refined_Features'] = refined_data[refined_name]
                    updated_count += 1
                    print(f"✅ 更新 (模糊匹配): {app_name} -> {refined_name}")
                    found = True
                    break
            
            if not found:
                not_found.append(app_name)
    
    # 保存结果
    output_file = "checked_with_refined_features.xlsx"
    result_df.to_excel(output_file, index=False)
    
    print(f"\n🎉 处理完成！")
    print(f"📊 成功更新了 {updated_count} 个应用的Refined_Features")
    print(f"💾 结果保存到: {output_file}")
    
    if not_found:
        print(f"\n⚠️  以下 {len(not_found)} 个应用在refine文件夹中未找到匹配：")
        for app in not_found[:10]:  # 只显示前10个
            print(f"   - {app}")
        if len(not_found) > 10:
            print(f"   ... 还有 {len(not_found)-10} 个")
    
    # 显示一些统计信息
    print(f"\n📈 统计信息:")
    print(f"checked.xlsx总行数: {len(checked_df)}")
    print(f"refine文件数量: {len(refined_data)}")
    print(f"成功匹配更新: {updated_count}")
    print(f"未匹配: {len(not_found)}")

if __name__ == "__main__":
    main()
