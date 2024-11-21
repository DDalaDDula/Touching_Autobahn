from settings import *
import math

def get_rotated_points(rect, angle):
    cx, cy = rect.center
    w, h = rect.size
    angle_rad = math.radians(angle)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    corners = [
        (-w / 2, -h / 2),
        (w / 2, -h / 2),
        (w / 2, h / 2),
        (-w / 2, h / 2),
    ]
    rotated_points = [
        (cx + x * cos_a - y * sin_a, cy + x * sin_a + y * cos_a) for x, y in corners
    ]
    return rotated_points

def project_polygon(points, axis):
    min_proj = max_proj = points[0][0] * axis[0] + points[0][1] * axis[1]
    for point in points[1:]:
        proj = point[0] * axis[0] + point[1] * axis[1]
        min_proj = min(min_proj, proj)
        max_proj = max(max_proj, proj)
    return min_proj, max_proj

def polygon_collision(poly1, poly2):
    polygons = [poly1, poly2]
    for polygon in polygons:
        for i in range(len(polygon)):
            j = (i + 1) % len(polygon)
            edge = (polygon[j][0] - polygon[i][0], polygon[j][1] - polygon[i][1])
            axis = (-edge[1], edge[0])
            min_proj1, max_proj1 = project_polygon(poly1, axis)
            min_proj2, max_proj2 = project_polygon(poly2, axis)
            if max_proj1 < min_proj2 or max_proj2 < min_proj1:
                return False
    return True