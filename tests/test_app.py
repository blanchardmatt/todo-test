"""
Playwright test script for the Todo application
"""
from playwright.sync_api import sync_playwright
import time
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import os
    os.system("chcp 65001 > nul")

def test_todo_app():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("[PASS] Browser launched")

        # Navigate to the app
        page.goto("http://localhost:8080")
        print("[PASS] Navigated to http://localhost:8080")

        # Check page title
        title = page.title()
        print(f"[PASS] Page title: {title}")

        # Test 1: Add a new todo
        print("\n--- Test 1: Adding a new todo ---")
        page.fill("#todoInput", "Test todo item from Playwright")
        page.click("#addBtn")
        time.sleep(0.5)

        # Verify the todo was added
        todo_text = page.locator(".todo-item .todo-text").first.text_content()
        print(f"[PASS] Todo added: {todo_text}")

        # Test 2: Mark todo as completed
        print("\n--- Test 2: Marking todo as completed ---")
        page.locator(".todo-item input[type='checkbox']").first.check()
        time.sleep(0.5)
        is_checked = page.locator(".todo-item input[type='checkbox']").first.is_checked()
        print(f"[PASS] Todo marked as completed: {is_checked}")

        # Test 3: Add another todo
        print("\n--- Test 3: Adding another todo ---")
        page.fill("#todoInput", "Second test todo")
        page.click("#addBtn")
        time.sleep(0.5)

        todo_count = page.locator(".todo-item").count()
        print(f"[PASS] Total todos: {todo_count}")

        # Test 4: Delete a todo
        print("\n--- Test 4: Deleting a todo ---")
        page.locator(".todo-item .delete-btn").first.click()
        time.sleep(0.5)

        remaining_todos = page.locator(".todo-item").count()
        print(f"[PASS] Remaining todos after deletion: {remaining_todos}")

        # Test 5: Verify stats
        print("\n--- Test 5: Verifying task statistics ---")
        stats_text = page.locator("#todoStats").text_content()
        print(f"[PASS] Stats display: {stats_text}")

        # Take a screenshot
        page.screenshot(path="../output/test_screenshot.png")
        print("\n[PASS] Screenshot saved as ../output/test_screenshot.png")

        # Close browser
        browser.close()
        print("\n[SUCCESS] All tests completed successfully!")

if __name__ == "__main__":
    test_todo_app()
