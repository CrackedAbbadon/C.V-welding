from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image

model = YOLO("vision/best.pt")  # загрузите предварительно обученную модель YOLOv8n
CLASS_NAMES = ['Bad_Welding', 'Crack', 'Excess_Reinforcement', 'Good_Welding', 'Porosity', 'Spatters']

colors = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255),
    (255, 0, 255), (192, 192, 192), (128, 128, 128), (128, 0, 0), (128, 128, 0),
    (0, 128, 0), (128, 0, 128), (0, 128, 128), (0, 0, 128), (72, 61, 139),
    (47, 79, 79), (47, 79, 47), (0, 206, 209), (148, 0, 211), (255, 20, 147)
]

# Функция для обработки изображения
def process_image(image):
    # Преобразование PIL Image в формат OpenCV
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    results = model(image)[0]
    print
    # Получение оригинального изображения и результатов
    image = results.orig_img
    classes_names = results.names
    classes = results.boxes.cls.cpu().numpy()
    boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)

    # Подготовка словаря для группировки результатов по классам
    grouped_objects = {}
    class_counts = {class_name: 0 for class_name in CLASS_NAMES}

    # Рисование рамок и группировка результатов
    for class_id, box in zip(classes, boxes):
        class_name = classes_names[int(class_id)]
        color = colors[int(class_id) % len(colors)]  # Выбор цвета для класса
        if class_name not in grouped_objects:
            grouped_objects[class_name] = []
        grouped_objects[class_name].append(box)
        class_counts[class_name] += 1  # Увеличиваем счётчик для данного класса

        # Рисование рамок на изображении
        x1, y1, x2, y2 = box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Сохранение измененного изображения
    new_image_path ='processed_image.jpg'
    cv2.imwrite(new_image_path, image)
    return Image.open(new_image_path), class_counts
