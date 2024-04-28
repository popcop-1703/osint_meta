import exifread
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from haversine import haversine, Unit
import os

ox.config(log_console=True, use_cache=True)


def get_exif_data(image_path_):
    # Открываем изображение для чтения бинарного режима
    with open(image_path_, 'rb') as image_file:
        # Читаем метаданные изображения
        tags = exifread.process_file(image_file)

        return tags


def get_geo_location(exif_data):
    # Проверяем, есть ли метаданные о геолокации
    if 'GPS GPSLongitude' in exif_data and 'GPS GPSLatitude' in exif_data:
        # Получаем значения долготы и широты
        longitude = exif_data['GPS GPSLongitude']
        latitude = exif_data['GPS GPSLatitude']

        # Преобразуем значения из градусов, минут и секунд в десятичную форму
        longitude_degrees = longitude.values[0].num / longitude.values[0].den
        longitude_minutes = longitude.values[1].num / longitude.values[1].den
        longitude_seconds = longitude.values[2].num / longitude.values[2].den
        latitude_degrees = latitude.values[0].num / latitude.values[0].den
        latitude_minutes = latitude.values[1].num / latitude.values[1].den
        latitude_seconds = latitude.values[2].num / latitude.values[2].den

        # Вычисляем долготу и широту в десятичной форме
        longitude_decimal = longitude_degrees + longitude_minutes / 60 + longitude_seconds / 3600
        latitude_decimal = latitude_degrees + latitude_minutes / 60 + latitude_seconds / 3600

        # Получаем направления (север, юг, восток, запад)
        longitude_direction = exif_data['GPS GPSLongitudeRef'].values
        latitude_direction = exif_data['GPS GPSLatitudeRef'].values

        # Возвращаем кортеж с координатами
        return latitude_decimal, longitude_decimal, latitude_direction, longitude_direction
    else:
        return None


# Папка с изображениями
folder_path = 'for_check/'

# Массив для хранения координат
coordinates = []

# Получаем список файлов в папке
image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

# Для каждого файла извлекаем метаданные и координаты
for image_file in image_files:
    image_path = os.path.join(folder_path, image_file)
    exif_data = get_exif_data(image_path)
    location = get_geo_location(exif_data)
    if location:
        coordinates.append((location[0], location[1]))

# Выводим координаты
for coord in coordinates:
    print("Latitude:", coord[0])
    print("Longitude:", coord[1])
    #print(coordinates[0])
    print()


##print("Геолокация изображения:", location)


def plot_route(origin, destination):
    # Загрузка графа дорог из OpenStreetMap для заданной области
    G = ox.graph_from_point(origin, network_type='drive', dist=dist_)

    # Нахождение ближайших узлов к заданным координатам
    orig_node = ox.distance.nearest_nodes(G, origin[1], origin[0])
    dest_node = ox.distance.nearest_nodes(G, destination[1], destination[0])

    # Построение маршрута между найденными узлами
    route = nx.shortest_path(G, orig_node, dest_node, weight='length')

    # Получение координат вершин маршрута
    route_nodes = ox.graph_to_gdfs(G, nodes=False)
    route_coords = route_nodes.loc[route].geometry.unary_union

    # Построение карты с маршрутом
    fig, ax = ox.plot_graph_route(G, route, route_color='b', route_linewidth=6, node_size=0, show=False, close=False)

    # Добавление начальной и конечной точек на карту
    ax.scatter(origin[1], origin[0], c='green', s=100, edgecolor='k', zorder=3)
    ax.scatter(destination[1], destination[0], c='red', s=100, edgecolor='k', zorder=3)

    # Отображение карты с маршрутом
    plt.show()


# Задание координат начальной и конечной точек (широта, долгота)
origin_point = (coordinates[0])
destination_point = (coordinates[1])
dist_ = haversine(origin_point, destination_point) * 1200

# Построение маршрута
plot_route(origin_point, destination_point)
