import exifread
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from haversine import haversine
import os
from geopy.geocoders import Nominatim

ox.config(log_console=True, use_cache=True)


def get_exif_data(image_path_):
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


def get_address_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="geo_locator")
    location = geolocator.reverse((latitude, longitude))
    return location.address


def write_coordinates_and_addresses_to_file(coordinates_array, addresses_array, filename):
    with open(filename, 'w') as file:
        for i in range(len(coordinates_array)):
            latitude, longitude = coordinates_array[i]
            address = addresses_array[i]
            file.write(f"Coordinates: {latitude}, {longitude}, Address: {address}\n")


# Папка с изображениями
folder_path = 'for_check/'

# Массив для хранения координат
coordinates = []
addresses_array = []

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

for coords in coordinates:
    latitude, longitude = coords
    address = get_address_from_coordinates(latitude, longitude)
    addresses_array.append(address)

write_coordinates_and_addresses_to_file(coordinates, addresses_array, "coordinates_and_addresses.txt")
print("Координаты и адреса успешно записаны в файл.")
# Вывод результатов
for i, address in enumerate(addresses_array):
    print(f"Coordinates: {coordinates[i]}, Address: {address}")


def plot_route(waypoints):
    # Load road network graph from OpenStreetMap for the specified area
    G = ox.graph_from_point(waypoints[0], network_type='drive', dist=haversine(waypoints[0], waypoints[2]) * 1200)

    # Find nearest nodes to the first waypoint
    orig_node = ox.nearest_nodes(G, waypoints[0][1], waypoints[0][0])

    # Plotting the route between consecutive waypoints
    for i in range(1, len(waypoints)):
        dest_node = ox.nearest_nodes(G, waypoints[i][1], waypoints[i][0])
        route = nx.shortest_path(G, orig_node, dest_node, weight='length')

        # Get coordinates of route nodes
        route_nodes = ox.graph_to_gdfs(G, nodes=False)
        route_coords = route_nodes.loc[route].geometry.unary_union

        # Plotting the route on the map
        fig, ax = ox.plot_graph_route(G, route, route_color='b', route_linewidth=6, node_size=0, show=False,
                                      close=False)

        # Adding start and end points to the map
        ax.scatter(waypoints[0][1], waypoints[0][0], c='green', s=100, edgecolor='k', zorder=3)
        ax.scatter(waypoints[i][1], waypoints[i][0], c='red', s=100, edgecolor='k', zorder=3)

        orig_node = dest_node

    plt.show()


waypoints = [(coordinates[0]), (coordinates[1]), (coordinates[2])]

plot_route(waypoints)
