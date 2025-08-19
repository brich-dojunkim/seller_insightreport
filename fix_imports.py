#!/usr/bin/env python3
"""테스트 파일들의 경로 문제 자동 수정 스크립트"""

import os
import re
from pathlib import Path

def add_path_fix_to_file(file_path):
    """파일에 경로 수정 코드 추가"""
    
    if not os.path.exists(file_path):
        print(f"⚠️ 파일이 없습니다: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 이미 경로 수정 코드가 있는지 확인
    if 'sys.path.insert(0' in content:
        print(f"📄 이미 수정됨: {file_path}")
        return False
    
    # 경로 수정 코드
    path_fix_code = '''# 경로 문제 해결
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

'''
    
    # 첫 번째 import 문을 찾아서 그 앞에 경로 수정 코드 삽입
    import_pattern = r'(from\s+\w+\s+import|import\s+\w+)'
    match = re.search(import_pattern, content)
    
    if match:
        # import 문 앞에 경로 수정 코드 삽입
        insert_pos = match.start()
        
        # 파일 시작 부분의 주석들 건너뛰기
        lines = content.split('\n')
        insert_line = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            # 빈 줄이거나 주석이면 건너뛰기
            if not stripped or stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            else:
                insert_line = i
                break
        
        # 라인 단위로 삽입
        lines.insert(insert_line, path_fix_code.strip())
        new_content = '\n'.join(lines)
        
    else:
        # import 문을 찾지 못했으면 파일 시작 부분에 추가
        new_content = path_fix_code + content
    
    # 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 수정됨: {file_path}")
    return True

def fix_all_test_files():
    """모든 테스트 파일에 경로 수정 코드 추가"""
    
    print("🔧 테스트 파일 경로 자동 수정 시작...")
    
    # tests 폴더의 모든 Python 파일 찾기
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("❌ tests 폴더가 없습니다.")
        return
    
    python_files = list(tests_dir.glob("*.py"))
    
    if not python_files:
        print("❌ tests 폴더에 Python 파일이 없습니다.")
        return
    
    print(f"📁 발견된 테스트 파일: {len(python_files)}개")
    
    fixed_count = 0
    for file_path in python_files:
        if add_path_fix_to_file(file_path):
            fixed_count += 1
    
    print(f"✅ 총 {fixed_count}개 파일 수정 완료!")
    
    # 추가로 루트 디렉토리의 테스트 파일들도 확인
    root_test_files = [
        "integration_test.py",
        "test_utils.py", 
        "comprehensive_integration_test.py",
        "complete_45_metrics_test.py"
    ]
    
    print("\n🔧 루트 디렉토리 테스트 파일 확인...")
    root_fixed = 0
    for filename in root_test_files:
        if os.path.exists(filename):
            if add_path_fix_to_file(filename):
                root_fixed += 1
    
    if root_fixed > 0:
        print(f"✅ 루트 디렉토리에서 {root_fixed}개 파일 추가 수정!")

def also_fix_main_imports():
    """메인 파일들의 import도 수정"""
    
    print("\n🔧 메인 파일 import 수정...")
    
    files_to_fix = [
        "main.py",
        "report_generator.py"
    ]
    
    replacements = {
        r'from data_processor import': 'from data_processing import',
        r'import data_processor': 'import data_processing as data_processor',
    }
    
    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old_pattern, new_pattern in replacements.items():
            content = re.sub(old_pattern, new_pattern, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Import 수정: {file_path}")
        else:
            print(f"📄 변경없음: {file_path}")

def fix_config_path():
    """config.py의 파일 경로도 수정"""
    
    print("\n🔧 config.py 파일 경로 수정...")
    
    if not os.path.exists("config.py"):
        print("⚠️ config.py 파일이 없습니다.")
        return
    
    with open("config.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 절대경로를 상대경로로 변경
    old_path = r'/Users/brich/Desktop/seller_insightreport/order_list_20250818120157_497\.xlsx'
    new_path = './files/order_list_20250818120157_497.xlsx'
    
    if old_path.replace('\\', '') in content:
        content = re.sub(old_path, new_path, content)
        
        with open("config.py", 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ config.py 파일 경로 수정됨")
    else:
        print("📄 config.py 이미 올바른 경로")

def main():
    """메인 실행"""
    
    print("🚀 전체 프로젝트 경로 문제 자동 수정 시작!")
    print("=" * 50)
    
    # 1. 테스트 파일들에 경로 수정 코드 추가
    fix_all_test_files()
    
    # 2. 메인 파일들의 import 수정
    also_fix_main_imports()
    
    # 3. config.py 경로 수정
    fix_config_path()
    
    print("\n" + "=" * 50)
    print("🎉 모든 수정 완료!")
    print("\n📋 테스트 방법:")
    print("1. cd /Users/brich/Desktop/seller_insightreport")  
    print("2. python3 tests/test_utils.py")
    print("3. python3 tests/integration_test.py")

if __name__ == "__main__":
    main()