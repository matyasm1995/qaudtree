import json, sys, turtle

in_file = 'D:/Administrator/Documents/Geografie _Kartografie/magisterske_studium/1.rocnik/úvod do ' \
          'programování/qaudtree/DU2/points_around_zerou.geojson '
out_file = 'points_out.geojson'
group_size = 5

def build_quadtree(points,bbox,quad,depth):
    if len(points) <= group_size:
        print(bbox, quad, depth,'konec')
        graphic(bbox)
        return
    else:
        node = [(bbox[0]+bbox[2])/2,(bbox[1]+bbox[3])/2]
        quad_1 = [node[0],node[1],bbox[2],bbox[3]]
        quad_2 = [node[0],bbox[1],bbox[2],node[1]]
        quad_3 = [bbox[0],bbox[1],node[0],node[1]]
        quad_4 = [bbox[0],node[1],node[0],bbox[3]]
        P1 = select_points(points ,quad_1)
        P2 = select_points(points, quad_2)
        P3 = select_points(points, quad_3)
        P4 = select_points(points, quad_4)
        print(bbox,quad,depth)
        graphic(bbox)
        build_quadtree(P1, quad_1, 1, depth + 1)
        build_quadtree(P2, quad_2, 2, depth + 1)
        build_quadtree(P3, quad_3, 3, depth + 1)
        build_quadtree(P4, quad_4, 4, depth + 1)


def select_points(points,boundaries):
    P = []
    for j in range(len(points)):
        ID = points[j][0]
        x = points[j][1]
        y = points[j][2]
        if boundaries[0] <= x <= boundaries[2] and boundaries[1] <= y <= boundaries[3]:
            P.append([ID, x, y])
        else:
            continue
    return P

def graphic(bbox):
    turtle.speed(10)
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


with open(in_file, 'r') as in_f:
    data = json.load(in_f)

points = []
ID = 1
for feature in data['features']:
    xy = feature['geometry']['coordinates']
    points.append([ID, xy[0], xy[1]])
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
turtle.setworldcoordinates(min_x,min_y,max_x,max_y)

for i in range(len(points)):
    turtle.speed(10)
    turtle.ht()
    turtle.up()
    turtle.setpos(points[i][1], points[i][2])
    turtle.down()
    turtle.dot(5, "blue")

build_quadtree(points, bbox, 0, 0)

turtle.exitonclick()