# test_supabase.py - Run this in your terminal
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.supabase_manager import get_supabase_manager
from datetime import datetime

def test_supabase():
    db = get_supabase_manager()
    
    if not db.is_connected():
        print("❌ Supabase not connected!")
        print("Check your .env file has SUPABASE_URL and SUPABASE_ANON_KEY")
        return
    
    print("✅ Supabase connected!")
    
    # Test 1: Save dataset
    print("\n📊 Testing dataset save...")
    dataset_id = db.save_dataset(
        user_id="test_user",
        dataset_name="Test Dataset",
        file_name="test.csv",
        file_size=1024,
        rows=100,
        columns=5,
        column_info={"col1": "int64", "col2": "object"},
        metadata={"test": True}
    )
    
    if dataset_id:
        print(f"✅ Dataset saved! ID: {dataset_id}")
    else:
        print("❌ Failed to save dataset")
        return
    
    # Test 2: Save audit log
    print("\n📝 Testing audit log...")
    log_id = db.log_user_activity(
        user_id="test_user",
        activity_type="test",
        description="Testing audit log",
        metadata={"timestamp": datetime.now().isoformat()}
    )
    
    if log_id:
        print(f"✅ Audit log saved! ID: {log_id}")
    else:
        print("❌ Failed to save audit log")
    
    # Test 3: Retrieve data
    print("\n📥 Testing data retrieval...")
    datasets = db.get_user_datasets("test_user")
    print(f"✅ Found {len(datasets)} datasets for test_user")
    
    logs = db.get_user_activity_logs("test_user")
    print(f"✅ Found {len(logs)} audit logs for test_user")
    
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    test_supabase()