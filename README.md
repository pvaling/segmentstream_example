# SegmentStream Workflow Sketch

## Общие сведения о задаче.

Нужно было решить задачу проектирования гибкого workflow движка реализующего ETL процесс.
Процесс, в двух словах, заключается в получении статистики из различных внешних систем, трансформации этой статистики,
слияния данных, обучения модели на новых исторических данных и формирование прогноза на день вперед.

## Структура проекта

/dags - сценарий задачи на фреймворке Apache Airflow

/jupyter - ноутбук с наработками по ML

/services - сервисы-эмуляторы внешних систем

## Общая схема решения

Draw.io Chart
https://drive.google.com/file/d/1WmB1P8F2aTch973tmXorJalT7HWSykBC/view?usp=sharing

![alt text](docs/images/SegmentStreamOverview.png)

## Установка
Airflow из докера
остальное локально запускается
todo...

## Скрины
### Граф процесса
![alt text](docs/images/airflow_graph.png "Airflow DAG Graph Example")
### Мониторинг периодических запусков
![alt text](docs/images/airflow_tree.png "Airflow DAG Graph Example")
### Диаграмма Ганта
![alt text](docs/images/airflow_timeline.png "Airflow DAG Graph Example")
### Динамика времени выполнения операций
![alt text](docs/images/airflow_chart.png "Airflow DAG Graph Example")
### Логи исполнения задачи
![alt text](docs/images/airflow_logs.png "Airflow DAG Graph Example")
### Исторические данные в MongoDB
![alt text](docs/images/mongo_history.png "Airflow DAG Graph Example")
### Данные прогноза в MongoDB
![alt text](docs/images/mongo_predictions.png "Airflow DAG Graph Example")
### Визуализация обученной модели
![alt text](docs/images/polynomial_predictor.png "Airflow DAG Graph Example")




