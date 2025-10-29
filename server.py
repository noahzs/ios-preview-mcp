#!/usr/bin/env python3
"""
iOS Preview MCP Server
Provides tools for building iOS views and capturing screenshots for AI code review.
"""

import subprocess
import os
import time
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("iOS Preview")


@mcp.tool()
def build_and_screenshot(
    view_name: str,
    workspace_path: str,
    scheme: str,
    test_target: str,
    device: str = "iPhone 15 Pro",
    snapshots_dir: str = "./__Snapshots__",
    record: bool = False,
) -> str:
    """
    Build a SwiftUI view and capture its screenshot using swift-snapshot-testing.

    Args:
        view_name: Name of the SwiftUI view (e.g., "ContentView", "ProfileView")
        workspace_path: Path to .xcworkspace or .xcodeproj file
        scheme: Xcode scheme name
        test_target: Name of the test target containing ViewSnapshotTests
        device: iOS Simulator device name (default: "iPhone 15 Pro")
        snapshots_dir: Directory where snapshots are stored (default: "./__Snapshots__")
        record: When true, runs in snapshot record mode to refresh baselines

    Returns:
        Absolute path to the captured screenshot PNG file

    Example:
        build_and_screenshot(
            view_name="ProfileView",
            workspace_path="/path/to/MyApp.xcworkspace",
            scheme="MyApp",
            test_target="MyAppTests"
        )
    """

    # Validate inputs
    if not os.path.exists(workspace_path):
        return f"❌ Error: Workspace/project not found at {workspace_path}"

    # Determine if it's a workspace or project
    is_workspace = workspace_path.endswith('.xcworkspace')
    build_flag = "-workspace" if is_workspace else "-project"

    try:
        print(f"🔨 Building and testing {view_name}...")

        # Boot simulator (ignore errors if already booted)
        boot_result = subprocess.run(
            ["xcrun", "simctl", "boot", device],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Wait a moment for simulator to be ready
        if boot_result.returncode == 0:
            time.sleep(2)

        # Construct test identifier
        test_identifier = f"{test_target}/ViewSnapshotTests/test{view_name}"

        # Determine if device is a UUID or name
        # UUIDs contain dashes, device names typically don't
        device_specifier = f"id={device}" if "-" in device else f"name={device}"

        # Run the specific snapshot test
        print(f"📱 Running test on {device}...")
        env = os.environ.copy()
        if record:
            env["SNAPSHOT_RECORD_MODE"] = "1"

        result = subprocess.run(
            [
                "xcodebuild", "test",
                build_flag, workspace_path,
                "-scheme", scheme,
                "-destination", f"platform=iOS Simulator,{device_specifier}",
                "-only-testing", test_identifier,
            ],
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )

        # Check for build/test failure
        if result.returncode != 0:
            # Extract useful error info
            stderr_lines = result.stderr.split('\n')
            error_lines = [line for line in stderr_lines if 'error:' in line.lower()]

            if error_lines:
                error_msg = '\n'.join(error_lines[:5])  # First 5 errors
                return f"❌ Build/test failed:\n{error_msg}\n\nRun with verbose logging to see full output."
            else:
                return f"❌ Build/test failed with exit code {result.returncode}\n{result.stderr[-1000:]}"

        # Find the screenshot file
        # swift-snapshot-testing uses format: __Snapshots__/TestClassName/testMethodName.1.png
        snapshot_filename = f"test{view_name}.1.png"

        # Try to find the snapshot in the expected location
        workspace_dir = os.path.dirname(os.path.abspath(workspace_path))
        possible_paths = [
            os.path.join(workspace_dir, snapshots_dir, "ViewSnapshotTests", snapshot_filename),
            os.path.join(workspace_dir, test_target, snapshots_dir, "ViewSnapshotTests", snapshot_filename),
        ]

        for snapshot_path in possible_paths:
            if os.path.exists(snapshot_path):
                abs_path = os.path.abspath(snapshot_path)
                print(f"✅ Screenshot captured successfully!")
                return abs_path

        # If not found, search for it
        search_result = subprocess.run(
            ["find", workspace_dir, "-name", snapshot_filename, "-type", "f"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if search_result.stdout.strip():
            found_path = search_result.stdout.strip().split('\n')[0]
            return os.path.abspath(found_path)

        return f"⚠️ Test passed but screenshot not found. Expected at one of:\n" + "\n".join(possible_paths)

    except subprocess.TimeoutExpired:
        return f"❌ Build timed out after 180 seconds. The build might be hanging or taking too long."
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


@mcp.tool()
def list_simulators() -> str:
    """
    List all available iOS Simulator devices.

    Returns:
        Formatted list of available simulator devices
    """
    try:
        # Remove "iOS" filter to show all runtimes including iOS 26.0+
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "available"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return f"❌ Failed to list simulators: {result.stderr}"

        # Parse and format the output - filter for iOS devices only
        lines = result.stdout.split('\n')
        devices = [line.strip() for line in lines if 'iPhone' in line or 'iPad' in line]

        if not devices:
            return "No iOS simulators found. Install simulators via Xcode preferences."

        return "Available iOS Simulators:\n" + "\n".join(f"  • {device}" for device in devices)

    except Exception as e:
        return f"❌ Error listing simulators: {str(e)}"


@mcp.tool()
def quick_screenshot(device: str = "iPhone 15 Pro") -> str:
    """
    Take a quick screenshot of the currently running simulator.
    Useful for capturing the current state without rebuilding.

    Args:
        device: iOS Simulator device name (default: "iPhone 15 Pro")

    Returns:
        Absolute path to the captured screenshot
    """
    try:
        # Create screenshots directory in /tmp
        screenshots_dir = "/tmp/ios_screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)

        # Generate filename with timestamp
        timestamp = int(time.time())
        screenshot_path = os.path.join(screenshots_dir, f"simulator_{timestamp}.png")

        # Take screenshot
        result = subprocess.run(
            ["xcrun", "simctl", "io", device, "screenshot", screenshot_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return f"❌ Failed to capture screenshot: {result.stderr}"

        if os.path.exists(screenshot_path):
            return os.path.abspath(screenshot_path)
        else:
            return f"❌ Screenshot command succeeded but file not found at {screenshot_path}"

    except Exception as e:
        return f"❌ Error taking screenshot: {str(e)}"


if __name__ == "__main__":
    mcp.run()
