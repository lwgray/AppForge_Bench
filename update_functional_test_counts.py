#!/usr/bin/env python3
import os
import json
import glob

def count_functional_tests(task_dir):
    """Count the number of functional test directories in a task directory"""
    functional_tests_dir = os.path.join(task_dir, "functional_tests")
    if not os.path.exists(functional_tests_dir):
        return 0
    
    test_dirs = [d for d in os.listdir(functional_tests_dir) 
                 if os.path.isdir(os.path.join(functional_tests_dir, d)) 
                 and d.startswith("test")]
    
    test_files = [f for f in os.listdir(functional_tests_dir) 
                  if f.endswith(".json") 
                  and f.startswith("test") 
                  and os.path.isfile(os.path.join(functional_tests_dir, f))]
    
    test_numbers = set()
    
    for item in test_dirs + test_files:
        # Extract number from "test1", "test2", etc.
        if item.startswith("test"):
            try:
                # Remove "test" prefix and ".json" extension if present
                item_name = item.replace(".json", "")
                num = int(item_name[4:])  # Remove "test" prefix
                test_numbers.add(num)
            except ValueError:
                continue
    
    return len(test_numbers)

def update_task_info(task_dir):
    """Update the functional_test_num in task_info.json"""
    task_info_path = os.path.join(task_dir, "task_info.json")
    
    if not os.path.exists(task_info_path):
        print(f"Warning: {task_info_path} not found")
        return
    
    # Count functional tests
    actual_count = count_functional_tests(task_dir)
    
    try:
        with open(task_info_path, 'r', encoding='utf-8') as f:
            task_info = json.load(f)
    except Exception as e:
        print(f"Error reading {task_info_path}: {e}")
        return
    
    current_count = task_info.get("functional_test_num", 0)
    
    if current_count != actual_count:
        print(f"Updating {task_dir}: {current_count} -> {actual_count}")
        task_info["functional_test_num"] = actual_count
        
        try:
            with open(task_info_path, 'w', encoding='utf-8') as f:
                json.dump(task_info, f, indent=4, ensure_ascii=False)
            print(f"  ✓ Updated {task_info_path}")
        except Exception as e:
            print(f"  ✗ Error writing {task_info_path}: {e}")
    else:
        print(f"✓ {task_dir}: {actual_count} (already correct)")

def main():
    """Main function to process all task directories"""
    tasks_dir = "tasks"
    
    if not os.path.exists(tasks_dir):
        print(f"Error: {tasks_dir} directory not found")
        return
    
    task_dirs = [d for d in os.listdir(tasks_dir) 
                 if os.path.isdir(os.path.join(tasks_dir, d)) 
                 and not d.startswith('.')]
    
    print(f"Found {len(task_dirs)} task directories")
    print("=" * 50)
    
    updated_count = 0
    total_count = 0
    
    for task_dir in sorted(task_dirs):
        full_path = os.path.join(tasks_dir, task_dir)
        total_count += 1
        
        try:
            update_task_info(full_path)
        except Exception as e:
            print(f"Error processing {task_dir}: {e}")
    
    print("=" * 50)
    print(f"Processed {total_count} task directories")

if __name__ == "__main__":
    main()
