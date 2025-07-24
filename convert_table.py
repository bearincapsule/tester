import pandas as pd
import os

def convert_csv_to_xlsx():
    # Путь к файлам
    csv_file = 'test_results.csv'
    xlsx_file = 'test_results.xlsx'
    
    try:
        # Читаем CSV с правильной кодировкой
        df = pd.read_csv(csv_file, encoding='utf-8')
        
        # Создаем writer для Excel
        writer = pd.ExcelWriter(xlsx_file, engine='xlsxwriter')
        
        # Записываем данные
        df.to_excel(writer, index=False, sheet_name='Results')
        
        # Получаем объект workbook и worksheet
        workbook = writer.book
        worksheet = writer.sheets['Results']
        
        # Автоподбор ширины столбцов
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            ) + 2
            worksheet.set_column(idx, idx, max_length)
        
        # Сохраняем результат
        writer.close()
        print(f"Файл успешно сконвертирован в {xlsx_file}")
        
    except Exception as e:
        print(f"Ошибка при конвертации: {e}")

if __name__ == "__main__":
    convert_csv_to_xlsx()