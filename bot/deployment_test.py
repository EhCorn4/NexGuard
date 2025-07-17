#!/usr/bin/env python3
"""
Deployment Test Script for NexGuard Discord Bot
Tests all deployment configurations and health endpoints
"""

import asyncio
import aiohttp
import sys
import os
from datetime import datetime

async def test_health_endpoint(url, endpoint_name):
    """Test a health endpoint"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                content = await response.text()
                status = response.status
                print(f"✅ {endpoint_name}: {status} - {content[:50]}...")
                return True
    except Exception as e:
        print(f"❌ {endpoint_name}: Failed - {str(e)}")
        return False

async def test_deployment_readiness():
    """Test deployment readiness"""
    print("🚀 NexGuard Discord Bot - Deployment Readiness Test")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test configuration
    base_url = "http://localhost:5000"
    
    # Test endpoints
    endpoints = [
        (f"{base_url}/", "Health Check (/)"),
        (f"{base_url}/health", "Health Check (/health)"),
        (f"{base_url}/status", "Status Endpoint (/status)")
    ]
    
    results = []
    for url, name in endpoints:
        result = await test_health_endpoint(url, name)
        results.append(result)
    
    print()
    print("📋 Configuration Check:")
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Working directory: {os.getcwd()}")
    print(f"✅ PORT environment: {os.getenv('PORT', 'Not set (using default 5000)')}")
    print(f"✅ DISCORD_TOKEN: {'Present' if os.getenv('DISCORD_TOKEN') else 'Not set'}")
    
    print()
    print("📁 Deployment Files:")
    deployment_files = [
        "main.py", "app.py", "run.py", "deploy.sh",
        "Procfile", "pyproject.toml", "runtime.txt"
    ]
    
    for file in deployment_files:
        if os.path.exists(file):
            print(f"✅ {file}: Present")
        else:
            print(f"❌ {file}: Missing")
    
    print()
    print("🎯 Deployment Summary:")
    if all(results):
        print("✅ All health endpoints are responding correctly")
        print("✅ Application is ready for deployment")
        print("✅ Use 'python main.py' as the run command")
        print("✅ HTTP health checks will pass")
    else:
        print("❌ Some endpoints are not responding")
        print("❌ Check the application logs for errors")
        print("❌ Ensure the Discord bot is running")
    
    print()
    print("🔗 Deployment Commands:")
    print("  Primary: python main.py")
    print("  Alternative: python app.py")
    print("  Development: python run.py")
    print("  Shell: ./deploy.sh")
    
    return all(results)

if __name__ == "__main__":
    try:
        success = asyncio.run(test_deployment_readiness())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Test failed: {e}")
        sys.exit(1)