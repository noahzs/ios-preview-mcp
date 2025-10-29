import XCTest
import SnapshotTesting
import SwiftUI
@testable import MyApp  // ⚠️ Replace "MyApp" with your actual module name

/// Test class for capturing SwiftUI view snapshots.
/// Each test method captures a screenshot of a specific view for AI code review.
class ViewSnapshotTests: XCTestCase {

    /// Standard iPhone 15 Pro dimensions
    let standardFrame = CGRect(x: 0, y: 0, width: 393, height: 852)

    /// Test ContentView - the main entry view
    func testContentView() {
        let view = ContentView()
        let controller = UIHostingController(rootView: view)
        controller.view.frame = standardFrame

        assertSnapshot(of: controller, as: .image)
    }

    // MARK: - Add Your Views Here

    /// Template for adding new view tests
    /// 1. Copy this template
    /// 2. Replace "MyView" with your view name (must match exactly)
    /// 3. Initialize your view with any required parameters

    /*
    func testMyView() {
        let view = MyView()
        let controller = UIHostingController(rootView: view)
        controller.view.frame = standardFrame

        assertSnapshot(of: controller, as: .image)
    }
    */

    // MARK: - Examples with Different Sizes

    /*
    /// Example: Test a view at iPad size
    func testMyViewiPad() {
        let view = MyView()
        let controller = UIHostingController(rootView: view)
        controller.view.frame = CGRect(x: 0, y: 0, width: 1024, height: 1366) // iPad Pro 12.9"

        assertSnapshot(of: controller, as: .image)
    }

    /// Example: Test a view with specific parameters
    func testProfileViewWithData() {
        let mockUser = User(name: "John Doe", email: "john@example.com")
        let view = ProfileView(user: mockUser)
        let controller = UIHostingController(rootView: view)
        controller.view.frame = standardFrame

        assertSnapshot(of: controller, as: .image)
    }

    /// Example: Test a compact/small view
    func testButtonComponent() {
        let view = CustomButton(title: "Press Me", action: {})
        let controller = UIHostingController(rootView: view)
        controller.view.frame = CGRect(x: 0, y: 0, width: 200, height: 100)

        assertSnapshot(of: controller, as: .image)
    }
    */
}
