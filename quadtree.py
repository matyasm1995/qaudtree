import json, turtle, sys, os.path
from operator import itemgetter


def open_geojson(file_name,mode):
    if os.path.isfile(file_name):
        try:
            with open(file_name,mode, encoding="utf-8") as in_f:
                data = json.load(in_f)
        except:
            print('soubor je poskozeny, ci se nejedna o korektni geojson')
            exit(1)
    else:
        print('soubor neexistuje')
        exit(1)
    return data

def build_quadtree(in_points, out_points, bbox, quadrant=0, depth=0, size=50):
    if len(in_points) <= size:
        graphic(bbox)
        for point in in_points:
            out_points.append(point)
        return
    else:
        node = [(bbox[0]+bbox[2])/2,(bbox[1]+bbox[3])/2]
        quad_1 = [node[0],node[1],bbox[2],bbox[3]]
        quad_2 = [node[0],bbox[1],bbox[2],node[1]]
        quad_3 = [bbox[0],bbox[1],node[0],node[1]]
        quad_4 = [bbox[0],node[1],node[0],bbox[3]]
        P1 = select_points(in_points, quad_1, 1)
        P2 = select_points(in_points, quad_2, 2)
        P3 = select_points(in_points, quad_3, 3)
        P4 = select_points(in_points, quad_4, 4)
        graphic(bbox)
        build_quadtree(P1,out_points, quad_1, 1, depth + 1, size)
        build_quadtree(P2,out_points, quad_2, 2, depth + 1, size)
        build_quadtree(P3,out_points, quad_3, 3, depth + 1, size)
        build_quadtree(P4,out_points, quad_4, 4, depth + 1, size)
    return out_points


def select_points(points, boundaries, quad):
    P = []
    for j in range(len(points)):
        ID = points[j][0]
        x = points[j][1]
        y = points[j][2]
        old_code = points[j][3]
        new_code = old_code + str(quad)
        if boundaries[0] <= x <= boundaries[2] and boundaries[1] <= y <= boundaries[3]:
            P.append([ID, x, y, new_code])
        else:
            continue
    return P


def graphic(bbox):
    turtle.speed(0)
    turtle.ht()
    turtle.up()
    turtle.setpos(bbox[0], bbox[1])
    turtle.down()
    turtle.forward(abs(bbox[2]-bbox[0]))
    turtle.left(90)
    turtle.forward(abs(bbox[3]-bbox[1]))
    turtle.left(90)
    turtle.forward(abs(bbox[2]-bbox[0]))
    turtle.left(90)
    turtle.forward(abs(bbox[3]-bbox[1]))
    turtle.left(90)
    turtle.up()


if len(sys.argv) != 3:
    print('malo nebo moc argumentu')
    exit(1)
else:
    data = open_geojson(sys.argv[1],'r')

if sys.argv[2][-8:] == ".geojson":
    out_file = sys.argv[2]
else:
    print('vystupni soubor neni geojson')
    exit(1)

group_size = 50

points = []
ID = 1
for feature in data['features']:
    xy = feature['geometry']['coordinates']
    points.append([ID, xy[0], xy[1],""])
    if ID == 1:
        min_x = xy[0]
        max_x = xy[0]
        min_y = xy[1]
        max_y = xy[1]
    else:
        if xy[0] < min_x:
            min_x = xy[0]
        if xy[0] > max_x:
            max_x = xy[0]
        if xy[1] < min_y:
            min_y = xy[1]
        if xy[1] > max_y:
            max_y = xy[1]
    ID += 1

bbox = [min_x, min_y, max_x, max_y]

turtle.setworldcoordinates(min_x, min_y, max_x, max_y)
turtle.speed(0)
turtle.ht()
turtle.tracer(50, 1)

for i in range(len(points)):
    turtle.up()
    turtle.setpos(points[i][1], points[i][2])
    turtle.down()
    turtle.dot(5, "blue")

if len(points) <= group_size:
    i = 0
    for feat in data['features']:
        feat['properties']['cluster_id'] = 0
        i += 1

    with open(out_file, 'w') as out:
        json.dump(data, out)
else:
    out_points = []
    out_points = build_quadtree(points, out_points, bbox,size=group_size)
    sorted_points = sorted(out_points, key=itemgetter(0))

    i = 0
    for feat in data['features']:
        feat['properties']['cluster_id'] = sorted_points[i][3]
        i += 1

    with open(out_file, 'w') as out:
        json.dump(data, out)


turtle.exitonclick()
