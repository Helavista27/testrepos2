# testrepos2
1. Создать папку проекта
2. Создать в папке проекта venv
3. Создать в папке проекта папку для репозитория
3. Установить библиотеки 
	pip install playwright
	pip install pytest
	pip install pytest-playwright 
4. Установить браузеры
	playwright install
5. Установить Homebrew если не установлен
	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
6. Установить Allure Report
	brew install allure (проверить установку и версию allure --version)
7. В папку для репозитория склонировать репозиторий с гита
8. Запустить тест
	pytest test_1111.py --alluredir=allure-results (если ругнется что нет директории allure-results, то создать)
9. Запустить сервер отчетов
	allure serve allure-results
10. Просмотреть отчет