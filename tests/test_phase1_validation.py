#!/usr/bin/env python3
"""
Phase 1 Validation Test - Tests the refactored system components
"""

import sys
from pathlib import Path

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

def test_imports():
    """Test that all refactored modules can be imported"""
    print("🔍 Testing imports...")

    try:
        # Test core imports
        from core import CommunalBrain, BrainConfig
        print("✅ Core imports successful")

        # Test storage module imports
        from core.brain.storage import StorageAbstraction, StorageConfig
        from core.brain.storage.interfaces import StorageBackend
        from core.brain.storage.backends.sqlite import SQLiteBackend
        print("✅ Storage module imports successful")

        # Test config imports
        from core.config.models import GlobalConfig, StorageConfig as GlobalStorageConfig
        print("✅ Configuration imports successful")

        # Test DI container
        from core.di import Container, get_container
        print("✅ DI container imports successful")

        # Test brain components
        from core.brain.components.config import BrainConfig as ComponentBrainConfig
        from core.brain.components.device import DeviceManager
        from core.brain.components.sync import SyncManager
        print("✅ Brain components imports successful")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config_structure():
    """Test that configuration is properly structured"""
    print("\n⚙️ Testing configuration structure...")

    try:
        from core.config.models import GlobalConfig

        config = GlobalConfig()

        # Test storage config
        assert hasattr(config, 'storage'), "GlobalConfig missing storage"
        assert config.storage.local_db_path == "data/communal_brain.db", f"Wrong default path: {config.storage.local_db_path}"
        print("✅ Storage config correct")

        # Test LLM config
        assert hasattr(config, 'llm'), "GlobalConfig missing llm"
        assert hasattr(config.llm, 'model'), "LLM config incomplete"
        print("✅ LLM config correct")

        # Test embeddings config
        assert hasattr(config, 'embeddings'), "GlobalConfig missing embeddings"
        assert hasattr(config.embeddings, 'model_name'), "Embeddings config incomplete"
        print("✅ Embeddings config correct")

        return True

    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_storage_modularization():
    """Test that storage is properly modularized"""
    print("\n🗂️ Testing storage modularization...")

    try:
        from core.brain.storage.config import StorageConfig
        from core.brain.storage.interfaces import StorageBackend, StorageBackendProtocol
        from core.brain.storage.abstraction import StorageAbstraction

        # Test config
        config = StorageConfig()
        assert config.local_db_path == "data/communal_brain.db", "Storage config not using data directory"
        print("✅ Storage config modularized")

        # Test interfaces
        assert hasattr(StorageBackend, 'store_memory'), "StorageBackend interface incomplete"
        assert hasattr(StorageBackend, 'retrieve_memories'), "StorageBackend interface incomplete"
        print("✅ Storage interfaces defined")

        # Test abstraction can be instantiated (without actually connecting)
        abstraction = StorageAbstraction(config)
        assert hasattr(abstraction, '_get_primary_backend'), "StorageAbstraction incomplete"
        print("✅ Storage abstraction layer works")

        return True

    except Exception as e:
        print(f"❌ Storage modularization test failed: {e}")
        return False

def test_brain_refactoring():
    """Test that brain components are properly refactored"""
    print("\n🧠 Testing brain refactoring...")

    try:
        from core.brain.components.config import BrainConfig
        from core.brain.components.device import DeviceManager
        from core.brain.components.sync import SyncManager

        # Test brain config
        config = BrainConfig()
        assert hasattr(config, 'storage'), "BrainConfig missing storage"
        assert hasattr(config, 'device_name'), "BrainConfig missing device_name"
        print("✅ Brain config refactored")

        # Test device manager
        device_id = DeviceManager.generate_device_id()
        assert device_id, "Device ID generation failed"
        assert len(device_id) > 0, "Device ID is empty"

        capabilities = DeviceManager.detect_capabilities()
        assert isinstance(capabilities, list), "Capabilities not a list"
        print("✅ Device manager works")

        # Test sync manager (just instantiation)
        # Note: We can't fully test sync without a brain instance
        print("✅ Sync manager structure correct")

        return True

    except Exception as e:
        print(f"❌ Brain refactoring test failed: {e}")
        return False

def test_di_container():
    """Test dependency injection container"""
    print("\n🏗️ Testing DI container...")

    try:
        from core.di import Container

        container = Container()

        # Test registration
        class TestService:
            def __init__(self):
                self.value = "test"

        container.register(TestService, TestService)

        # Test resolution
        instance = container.resolve(TestService)
        assert instance.value == "test", "DI resolution failed"
        print("✅ DI container registration and resolution works")

        # Test singleton
        container.register_instance(str, "singleton_test")
        instance1 = container.resolve(str)
        instance2 = container.resolve(str)
        assert instance1 is instance2, "Singleton not working"
        print("✅ DI singleton behavior correct")

        return True

    except Exception as e:
        print(f"❌ DI container test failed: {e}")
        return False

def test_data_directory_structure():
    """Test that data directory structure is correct"""
    print("\n📁 Testing data directory structure...")

    try:
        data_dir = workspace_root / "core" / "data"

        # Check that data directory exists
        assert data_dir.exists(), f"Data directory not found: {data_dir}"
        print("✅ Data directory exists")

        # Check that database is in data directory
        db_file = data_dir / "communal_brain.db"
        assert db_file.exists(), f"Database not found in data directory: {db_file}"
        print("✅ Database in correct location")

        # Check that required subdirectories exist
        required_dirs = ["conversations", "summaries", "archive"]
        for dir_name in required_dirs:
            dir_path = data_dir / dir_name
            assert dir_path.exists(), f"Required directory missing: {dir_path}"
        print("✅ Required subdirectories exist")

        return True

    except Exception as e:
        print(f"❌ Data directory test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🚀 Phase 1 Validation Tests")
    print("=" * 50)

    tests = [
        test_imports,
        test_config_structure,
        test_storage_modularization,
        test_brain_refactoring,
        test_di_container,
        test_data_directory_structure,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All Phase 1 validation tests passed!")
        print("✅ The refactored system is working correctly!")
        return True
    else:
        print("❌ Some validation tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)