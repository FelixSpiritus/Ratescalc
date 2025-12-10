# Аналитическая система мониторинга COVID-19 по метаданным рентгеновских снимков

Проект выполняет загрузку, очистку, нормализацию и анализ метаданных COVID-19 Chest X-Ray Dataset с использованием Apache Spark и PySpark.  
Реализованы статистические методы обработки пропусков, унификация диагнозов, категоризация возраста, SQL-аналитика и визуализации.  

# Структура проекта

project/  
- analysis.ipynb — основной ноутбук  
- metadata.csv — автоматически скачиваемые исходные данные  
- covid_processed_parquet/ — финальный очищенный датасет  
- presentation.pdf — итоговая презентация  
- README.md — документация  
- requirements.txt — список зависимостей  

# Требования к среде

Проект запускается на системах:

Операционные системы:
- Windows  
- Linux  
- macOS  

Необходимые компоненты:
- Python 3.9+ (в проекте 3.11)  
- Java OpenJDK 11 (обязательно для Apache Spark)  
- Apache Spark 3.5.1 (режим работы local[*])  
- Библиотеки Python (через pip или conda):
  - pyspark  
  - pandas  
  - requests  
  - matplotlib  
  - seaborn  

# Установка окружения

## 1. Перейти в каталог проекта
git clone <url>  
cd project  

## 2. Установить зависимости Python
Через pip:
pip install -r requirements.txt

Или вручную:
pip install pyspark==3.5.1 pandas requests matplotlib seaborn

## 3. Установить Apache Spark (cross-platform)
Скачать Spark 3.5.1 (prebuilt for Hadoop 3) с сайта Apache:  
https://spark.apache.org/downloads.html

Распаковать в удобную директорию, например:

Windows:
C:\spark

Linux/macOS:
/opt/spark

Указать переменные окружения (пример для Windows PowerShell):
$env:SPARK_HOME="C:\spark"
$env:PATH="$env:PATH;$env:SPARK_HOME\bin"

Для Linux/macOS:
export SPARK_HOME=/opt/spark
export PATH=$PATH:$SPARK_HOME/bin

Обязательно указать Java:
export JAVA_HOME=<путь к OpenJDK 11>

# Запуск проекта

## 1. Запустить Jupyter Notebook
jupyter notebook

## 2. Открыть файл analysis.ipynb

В ноутбуке автоматически создается Spark-сессия:
spark = (
    SparkSession.builder
    .appName("covid_xray_analysis")
    .master("local[*]")
    .getOrCreate()
)

Для стабильной работы файловой системы:
spark.sparkContext._jsc.hadoopConfiguration().set("fs.defaultFS", "file:///")

# Основные этапы обработки данных

## 1. Загрузка исходных данных
- metadata.csv скачивается с GitHub через requests  
- читается Spark-ом с inferSchema=True  

## 2. Анализ качества данных
- подсчёт пропусков  
- анализ аномальных значений возраста  
- анализ категориальных полей (diagnosis, sex, view)  
- выявление многочисленных форматов даты  

## 3. Очистка и нормализация
- age:
  - сначала медиана по диагнозу
  - затем глобальная медиана  
- sex:
  - сначала мода по диагнозу
  - затем глобальная мода  
- date:
  - нормализация множества форматов в date_normalized
  - добавление флага is_date_missing  
- удаление дубликатов по комбинации:
  patientid + date + view + finding  

## 4. Использование UDF
- UDF для унификации диагнозов (finding_unified)  
- UDF для группировки возраста (age_group)  

## 5. Фильтрация данных
Оставлены только:
- валидные нормализованные даты  
- возраст 18+  
- диагнозы: COVID-19, Pneumonia, Normal, Tuberculosis  
- проекции: PA, AP, AP Supine  

## 6. SQL-аналитика
Реализованы обязательные запросы:
1. Базовая статистика по диагнозам  
2. Распределение пола по диагнозам  
3. Топ-3 по возрасту в каждой группе диагнозов (оконная функция)  
4. Временные тренды по месяцам  
5. Heatmap: диагноза × проекция снимка  

## 7. Визуализации
- круговая диаграмма диагнозов  
- распределение возрастных групп  
- временные тренды  
- heatmap: finding vs view  

## 8. Сохранение результата в Parquet
df_filtered.write.mode("overwrite").option("compression", "snappy").parquet("./covid_processed_parquet")

## 9. Повторное использование очищенных данных
df = spark.read.parquet("./covid_processed_parquet")

# Примечания
- проект работает в local-режиме без кластера  
- формат Parquet ускоряет повторные вычисления  
- ноутбук полностью воспроизводим  
- структура легко масштабируется для больших данных  
