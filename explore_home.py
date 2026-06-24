# -*- coding: utf-8 -*-
import json
from playwright.sync_api import sync_playwright

BASE = "https://qlrv.democloud.xyz"
OUT = r"C:\Users\Admin\site_explore.txt"

lines = []

def log(s):
    lines.append(s)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    for path in ["/", "/login", "/auth/login", "/account/login"]:
        page.goto(BASE + path, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        log(f"=== {path} => {page.url}")
        inputs = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('input, button')).map(el => ({
                tag: el.tagName, type: el.type, name: el.name, id: el.id,
                placeholder: el.placeholder || null, visible: el.offsetParent !== null
            }));
        }""")
        log(json.dumps(inputs, ensure_ascii=False))
        page.screenshot(path=f"C:\\Users\\Admin\\page_{path.replace('/','_')}.png", full_page=True)

    browser.close()

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("done", OUT)
