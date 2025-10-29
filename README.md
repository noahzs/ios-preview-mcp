# iOS Preview MCP Server

AI-powered iOS UI development tool that lets Claude Code build SwiftUI views and capture screenshots for iterative review.

## What This Does

Provides Claude Code with tools to:
- 📸 Build and screenshot isolated SwiftUI views
- 🔍 Review UI layouts visually
- 🔄 Iterate on design changes quickly
- 📱 Test views at different device sizes

## Quick Start

### 1. Install Prerequisites (5 minutes)

```bash
# Install uv (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install FastMCP
uv pip install fastmcp

# Verify Xcode is installed
xcode-select --install  # Run only if needed
```

### 2. Set Up Your iOS Project (10 minutes)

#### Add swift-snapshot-testing Package

In Xcode:
1. File → Add Package Dependencies
2. Enter: `https://github.com/pointfreeco/swift-snapshot-testing`
3. Add to your test target

#### Add Snapshot Test File

1. Copy `ViewSnapshotTests.swift` from this repo to your test target
2. Update `@testable import MyApp` to match your app's module name
3. Build your project to verify it compiles

#### Find Your Project Details

You'll need these values for the MCP tool:

```bash
# From your Xcode project directory:

# 1. Workspace/Project path (use ONE of these):
ls *.xcworkspace  # If you have a workspace
ls *.xcodeproj    # If you only have a project

# 2. Scheme name:
xcodebuild -list  # Look under "Schemes:"

# 3. Test target name:
xcodebuild -list  # Look under "Targets:" for your test target
```

Example output:
```
Workspace: MyApp.xcworkspace
Scheme: MyApp
Test Target: MyAppTests
```

### 3. Configure Claude Code

In your iOS project root, create `.mcp.json`:

```json
{
  "mcpServers": {
    "ios-preview": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "fastmcp",
        "/Users/Noah/Documents/GitHub/ios-preview-mcp/server.py"
      ]
    }
  }
}
```

**Note:** The `.mcp.json` file should be placed at the root of your project directory (where your `.xcodeproj` file is located).

### 4. Restart Claude Code

After adding the configuration, restart Claude Code for changes to take effect.

## Usage

### Example Workflow

**Building a new view:**

```
User: Build me a profile screen with a circular avatar, name, and bio
Claude: [Creates ProfileView.swift]
Claude: [Adds testProfileView() to ViewSnapshotTests.swift]
Claude: Let me see how this looks...
Claude: [Calls build_and_screenshot tool]
Claude: [Views the screenshot]
Claude: The avatar is looking good, but the spacing between name and bio is too tight.
        Let me adjust that...
Claude: [Fixes padding]
Claude: [Screenshots again to verify]
Claude: Perfect! Here's your ProfileView.
```

### Available Tools

#### `build_and_screenshot`

Build a specific view and capture its screenshot.

**Parameters:**
- `view_name` (required): View name, e.g., "ProfileView"
- `workspace_path` (required): Path to .xcworkspace or .xcodeproj
- `scheme` (required): Xcode scheme name
- `test_target` (required): Test target name
- `device` (optional): Simulator device, default "iPhone 15 Pro"
- `snapshots_dir` (optional): Snapshot directory, default "./__Snapshots__"

**Example:**
```python
build_and_screenshot(
    view_name="ProfileView",
    workspace_path="/Users/Noah/MyApp/MyApp.xcworkspace",
    scheme="MyApp",
    test_target="MyAppTests"
)
```

#### `list_simulators`

List all available iOS simulator devices.

**Example:**
```python
list_simulators()
```

#### `quick_screenshot`

Take a quick screenshot of the currently running simulator (no rebuild).

**Parameters:**
- `device` (optional): Simulator device name, default "iPhone 15 Pro"

**Example:**
```python
quick_screenshot(device="iPhone 15 Pro")
```

## Adding New Views

When Claude builds a new SwiftUI view, it needs to add a corresponding test method:

```swift
// In ViewSnapshotTests.swift
func testMyNewView() {
    let view = MyNewView()
    let controller = UIHostingController(rootView: view)
    controller.view.frame = standardFrame

    assertSnapshot(of: controller, as: .image)
}
```

**Important:** The test method name must be `test{ViewName}` (e.g., `testProfileView` for `ProfileView`).

## Troubleshooting

### "Build failed" errors

**Check build logs:**
```bash
cd /path/to/your/ios/project
xcodebuild test \
  -workspace MyApp.xcworkspace \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
  -only-testing 'MyAppTests/ViewSnapshotTests/testContentView'
```

Common issues:
- Missing import statement in ViewSnapshotTests.swift
- View initializer requires parameters
- Module name incorrect in `@testable import`

### "Screenshot not found" errors

The test passed but the screenshot wasn't where expected. This usually means:
- First time running - swift-snapshot-testing creates the snapshot
- Snapshot directory moved
- Working directory is different than expected

**Find the snapshot manually:**
```bash
find /path/to/project -name "testMyView.1.png"
```

### Simulator won't boot

**Reset the simulator:**
```bash
xcrun simctl shutdown all
xcrun simctl erase "iPhone 15 Pro"
xcrun simctl boot "iPhone 15 Pro"
```

### MCP server not loading

**Check Claude Code logs:**
1. Open Claude Code
2. Check for MCP connection errors in console
3. Verify the path to `server.py` is correct in your config

**Test the server directly:**
```bash
cd /Users/Noah/Documents/GitHub/ios-preview-mcp
uv run --with fastmcp python server.py
# Should start without errors
```

## How It Works

1. **Claude creates a SwiftUI view** in your project
2. **Claude adds a snapshot test** for that view
3. **Claude calls `build_and_screenshot`** with your project details
4. **MCP server runs `xcodebuild test`** on that specific test
5. **swift-snapshot-testing** captures a PNG screenshot
6. **MCP server returns the path** to the screenshot
7. **Claude uses Read tool** to view the PNG
8. **Claude reviews the layout** and iterates if needed

## Performance Notes

- **First build:** 30-90 seconds (full compile)
- **Subsequent builds:** 15-30 seconds (incremental)
- **No code changes:** 5-10 seconds (test only)

This is acceptable for iterative review but not tight feedback loops. For rapid iteration, use `quick_screenshot` on a running app.

## File Structure

```
ios-preview-mcp/
├── server.py                              # MCP server implementation
├── ViewSnapshotTests.swift                # iOS test template
├── README.md                              # This file
└── .mcp.json.example                      # Config example
```

## Credits

Built for Claude Code to enable autonomous iOS UI development with visual feedback.

Uses:
- [FastMCP](https://github.com/jlowin/fastmcp) - Python MCP framework
- [swift-snapshot-testing](https://github.com/pointfreeco/swift-snapshot-testing) - Snapshot testing library
