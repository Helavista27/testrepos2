import re
from playwright.sync_api import Playwright, sync_playwright, expect
import time

def test_add_pt1(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://demo.playwright.dev/todomvc/#/")
    page.get_by_placeholder("What needs to be done?").click()
    page.get_by_placeholder("What needs to be done?").fill("123")
    page.get_by_placeholder("What needs to be done?").press("Enter")
    page.get_by_test_id("todo-title").dblclick()
    page.get_by_label("Edit").fill("123456")
    page.get_by_label("Edit").press("Enter")
    #time.sleep(5)
    # ---------------------
    context.close()
    browser.close()