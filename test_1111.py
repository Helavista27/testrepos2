import time

import allure
import pytest
from playwright.sync_api import Playwright, sync_playwright, expect
from xml.etree import ElementTree as ET

@pytest.fixture(scope="module")
def browser_context(playwright: Playwright):
    """Фикстура для запуска браузера и открытия страницы."""
    browser = playwright.chromium.launch(headless=False, slow_mo=300)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True
    )
    context.grant_permissions(['clipboard-read', 'clipboard-write'])
    page = context.new_page()
    page.goto("https://test-mes.hightech-plant.ru/")
    yield page
    context.close()
    browser.close()

def login(page):
    with allure.step("Заполнение поля Login"):
        page.get_by_label("Login").click()
        page.get_by_label("Login").fill("admin")
    with allure.step("Заполнение поля Password"):
        page.get_by_label("Password").click()
        page.get_by_label("Password").fill("1")
    with allure.step("Нажатие Log in"):
        page.get_by_role("button", name="Log in").click()

@allure.suite("UI Tests")
@allure.sub_suite("Логин и Выход")
def test_ui_login_logout(browser_context):
    page = browser_context
    login(page)
    with allure.step("Нажатие admin"):
        page.get_by_text("admin").click()
    with allure.step("Открытие Logoff"):
        page.get_by_role("menuitem", name="Logoff").click()

@allure.suite("UI Tests")
@allure.sub_suite("Логин и Производство")
def test_ui_login_production(browser_context):
    page = browser_context
    login(page)
    with allure.step("Открытие раздела Production"):
        page.get_by_role("heading", name="Production").click()
    with allure.step("Открытие консоли оператора"):
        page.get_by_text("Operator Console").nth(1).click()
    with allure.step("Выбор линии 3IN1 Mixing Line"):
        page.get_by_text("3IN1 Mixing Line", exact=True).click()
    with allure.step("Выбор 3in1 Mixer"):
        page.get_by_text("3in1 Mixer", exact=True).click()
    with allure.step("Переход на вкладку Produce"):
        page.get_by_role("tab", name="Produce").click()
    with allure.step("Клик по строке HALB 000000000043567699"):
        page.get_by_role("row", name="HALB 000000000043567699").get_by_role("button").click()
    with allure.step("Нажатие кнопки Produce"):
        page.get_by_role("button", name="Produce").click()
    with allure.step("Извлечение значений Produce"):
        page.wait_for_selector("mat-dialog-content")
        local_copy_mix_value = page.locator("#mat-mdc-dialog-0").locator("text=local_copy_mix").inner_text()
        production_date_value = page.get_by_label("Production Date").inner_text()
        common_expiration_date_value = page.locator("app-date-time-picker").filter(
            has_text="Common_ExpirationDate").inner_text()
        batch_value = page.get_by_label("Batch").inner_text()
        quantity_kg_text = page.locator("text=Quantity KG").inner_text()
        quantity_value = quantity_kg_text.split(' ')[1]
        print('Process Order:', local_copy_mix_value)
        print('Production Date:', production_date_value)
        print('Expiration Date:', common_expiration_date_value)
        print('Batch Code:', batch_value)
        print('UOM:', quantity_value)
    with allure.step("Нажатие на поле Quantity KG"):
        page.wait_for_selector("label:has-text('Quantity KG')")
        page.get_by_label("Quantity KG").click()
    with allure.step("Заполнение поля Quantity KG"):
        page.get_by_label("Quantity KG").fill("0.01")
    with allure.step("Повторное нажатие кнопки Produce"):
        page.get_by_role("button", name="Produce").click()
    with allure.step("Получение SSCC"):
        page.wait_for_selector("//td[contains(@class, 'mat-column-material_sublot__id')]")
        material_sublot_id_value = page.locator("//td[contains(@class, 'mat-column-material_sublot__id')]").nth(
            0).inner_text()
        print('SSCC:', material_sublot_id_value)
    with allure.step("Переход к EVENT_LOGS"):
        page.get_by_role("heading", name="EVENT_LOGS").click()
    with allure.step("Открытие Activity Log"):
        page.get_by_text("Activity Log").nth(1).click()
    with allure.step("Клик по строке FW_MaterialProducedActual"):
        page.locator('mat-icon[role="img"][class*="material-icons"]:has-text("description")').nth(0).click()
    with allure.step("Клик по строке верхней"):
        page.locator('(//mat-icon[text()="description"])[1]').click()
    with allure.step("Копирование информации"):
        page.get_by_role("button", name="btn-copy").click()
    with allure.step("Подтверждение копирования текста"):
        success_message = page.get_by_text("alert-text-copied")
        assert success_message.is_visible(), "Сообщение об успешном копировании текста не отображается"
    clipboard_text = page.evaluate("navigator.clipboard.readText()") # Получение текста из буфера обмена
    if clipboard_text:
        print("XML текст скопирован в буфер обмена.")
        try:
            root = ET.fromstring(clipboard_text) # Парсинг XML
            globe_expiration_date = root.findtext('.//globe_ExpirationDate') # Извлечение значения globe_ExpirationDate (Expiration Date)
            print('Expiration Date XML:', globe_expiration_date)
            quantity_string = root.findtext('.//QuantityString') # Извлечение значения QuantityString (Quantity)
            print('Quantity XML:', quantity_string)
            material_lot_id = root.findtext('.//MaterialLotID') # Извлечение значения MaterialLotID (Batch Code)
            print('Batch Code XML:', material_lot_id)
            production_request_id_text = root.findtext('.//ProductionRequestID') # Извлечение значения ProductionRequestID (Process Order)
            #actual_production_request_id = production_request_id_text[4:]
            print('Process Order XML:', production_request_id_text)
            unit_of_measure = root.findtext('.//UnitOfMeasure') # Извлечение значения UnitOfMeasure (UOM)
            print('UOM XML:', unit_of_measure)
            material_sub_lot_id = root.findtext('.//MaterialSubLotID') # Извлечение значения MaterialSubLotID (SSCC)
            print('SSCC XML:', material_sub_lot_id)
            # Сравнение значений при запуске производства с отправленными в САП
            comparisons = [
                ("Process Order", local_copy_mix_value, production_request_id_text),
                ("Expiration Date", common_expiration_date_value, globe_expiration_date),
                ("Batch Code", batch_value, material_lot_id),
                ("UOM", quantity_value, unit_of_measure),
                ("SSCC", material_sublot_id_value, material_sub_lot_id),
            ]
            for label, local_value, xml_value in comparisons:
                if local_value == xml_value:
                    print(f"{label} значения равны: '{local_value}'")
                else:
                    print(f"{label} значения не равны: '{local_value}' и '{xml_value}'.")
        except ET.ParseError as e:
            print("Ошибка парсинга XML:", e)
    else:
        print("XML текст не скопирован в буфер обмена.")


@allure.suite("UI Tests")
@allure.sub_suite("Логин и Потребление")
def test_ui_login_consume(browser_context):
    page = browser_context
    login(page)
    with allure.step("Открытие раздела Production"):
        page.get_by_role("heading", name="Production").click()
    with allure.step("Открытие консоли оператора"):
        page.get_by_text("Operator Console").nth(1).click()
    with allure.step("Выбор линии 3IN1 Mixing Line"):
        page.get_by_text("3IN1 Mixing Line", exact=True).click()
    with allure.step("Открытие 3in1 Mixer"):
        page.get_by_text("3in1 Mixer", exact=True).click()
    with allure.step("Открытие вкладки Consume"):
        page.get_by_role("tab", name="Consume").click()
    with allure.step("Переключение на следующую вкладку"):
        page.get_by_role("tab", name="Consume").press("ArrowRight")
    with allure.step("Открытие строки с именем 0100 0120 HALB 43567745"):
        page.get_by_role("row", name="0100 0120 HALB 43567745").get_by_role("button").click()
    with allure.step("Открытие вкладки Consume снова"):
        page.get_by_role("tab", name="Consume").click()
    with allure.step("Открытие строки с именем 0100 0120 ROH 43567751 Flavor"):
        page.get_by_role("row", name="0100 0120 ROH 43567751 Flavor").get_by_role("button").click()
    with allure.step("Нажатие кнопки Consume"):
        page.get_by_role("button", name="Consume").click()
    with allure.step("Ввод количества в Quantity g"):
        page.get_by_label("Quantity g").click()
    with allure.step("Заполнение Quantity g значением 0.1"):
        page.get_by_label("Quantity g").fill("0.1")
    with allure.step("Нажатие кнопки Consume для завершения потребления"):
        page.get_by_role("button", name="Consume").click()
    with allure.step("Клик на Inventory Consumed"):
        page.get_by_text("Inventory Consumed").click()
"""  
    with allure.step("Переход к EVENT_LOGS"):
        page.get_by_role("heading", name="EVENT_LOGS").click()
    with allure.step("Открытие Activity Log"):
        page.get_by_text("Activity Log").nth(1).click()
    with allure.step("Клик по строке FW_MaterialProducedActual 1"):
        page.get_by_role("row", name="FW_MaterialProducedActual 1").locator("mat-icon").click()
    with allure.step("Клик по строке 6422 Nov 12, 2024, 14:21 Nov"):
        page.get_by_role("row", name="6422 Nov 12, 2024, 14:21 Nov").locator("mat-icon").click()
    with allure.step("Копирование информации"):
        page.get_by_role("button", name="btn-copy").click()
    with allure.step("Подтверждение копирования текста"):
        success_message = page.get_by_text("alert-text-copied")
        assert success_message.is_visible(), "Сообщение об успешном копировании текста не отображается"
    with allure.step("Нажатие admin"):
        page.get_by_text("admin").click()
    with allure.step("Открытие Common_logoff"):
        page.get_by_role("menuitem", name="Common_logoff").click()
"""

@pytest.fixture(scope="module")
def playwright():
    with sync_playwright() as p:
        yield p