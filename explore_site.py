# -*- coding: utf-8 -*-
import json
from playwright.sync_api import sync_playwright

BASE = "https://qlrv.democloud.xyz"
ACCOUNTS = {
    "ADMIN": ("administrator@gmail.com", "123456@Ab"),
    "OFFICER": ("tktruongphong@gmail.com", "I1zxKHhAia@K"),
    "EMPLOYEE": ("tdydoan.0102@gmail.com", "g1wUeT3@aGJ@"),
}

def login(page, email, password):
    page.goto(BASE, wait_until="networkidle", timeout=60000)
    # try common login patterns
    if "/login" not in page.url.lower() and "checklist" not in page.url:
        page.goto(f"{BASE}/login", wait_until="networkidle", timeout=60000)
    
    inputs = page.locator("input").all()
    info = []
    for inp in inputs:
        try:
            info.append({
                "type": inp.get_attribute("type"),
                "name": inp.get_attribute("name"),
                "placeholder": inp.get_attribute("placeholder"),
                "id": inp.get_attribute("id"),
            })
        except Exception:
            pass
    
  # fill email/password
    email_sel = "input[type='email'], input[name*='email' i], input[placeholder*='email' i], input[placeholder*='Email' i], input[type='text']"
    pass_sel = "input[type='password']"
    
    page.locator(email_sel).first.fill(email, timeout=10000)
    page.locator(pass_sel).first.fill(password)
    
    btn = page.locator("button:has-text('Đăng nhập'), button:has-text('Login'), button[type='submit']").first
    btn.click()
    page.wait_for_timeout(5000)
    
    return page.url, info

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    url, inputs = login(page, *ACCOUNTS["ADMIN"])
    print("URL after login:", url)
    print("Inputs on login:", json.dumps(inputs, ensure_ascii=False))
    
    # try template page
    page.goto(f"{BASE}/hrm/checklist/template", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    print("Template URL:", page.url)
    print("Title:", page.title())
    body_text = page.locator("body").inner_text()[:2000]
    print("Body snippet:", body_text[:1500])
    
    # screenshot
    page.screenshot(path=r"C:\Users\Admin\template_admin.png", full_page=True)
    
    # checklist list
    page.goto(f"{BASE}/hrm/checklist", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    print("Checklist URL:", page.url)
    page.screenshot(path=r"C:\Users\Admin\checklist_admin.png", full_page=True)
    
    browser.close()
