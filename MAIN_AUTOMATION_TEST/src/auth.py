# -*- coding: utf-8 -*-
from playwright.sync_api import Page, TimeoutError as PWTimeout

from config.settings import Account, Settings


def login(page: Page, settings: Settings, account: Account, log) -> bool:
    log.log(f"[{account.role}] Login: {account.email}")
    page.goto(settings.base_url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(1500)
    email_inp = page.locator("#email")
    try:
        if email_inp.count() == 0 or not email_inp.is_visible():
            log.log(f"[{account.role}] Session dang hoat dong — bo qua form login → {page.url}")
            return True
    except Exception:
        log.log(f"[{account.role}] Session dang hoat dong — bo qua form login → {page.url}")
        return True
    email_inp.fill(account.email)
    page.locator("#password").fill(account.password)
    page.locator("button[type='submit']").click()
    page.wait_for_timeout(3500)
    try:
        page.wait_for_function("() => !document.querySelector('#email')", timeout=15000)
        log.log(f"[{account.role}] Login OK → {page.url}")
        return True
    except PWTimeout:
        log.log(f"[{account.role}] Login FAILED", "ERROR")
        return False
