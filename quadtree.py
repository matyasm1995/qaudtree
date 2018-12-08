import json, turtle, sys, os.path
from operator import itemgetter


def open_geojson(file_name,mode):
    '''
    funkce pro otevreni json/geojson
    :param file_name: nazev souboru
    :param mode: write/read
    :return: otevreny soubor
    '''
    if os.path.isfile(file_name): #pokud soubor existuje
        try:
            with open(file_name,mode, encoding="utf-8") as in_f: #zkus otevrit
                data = json.load(in_f)
        except:
            print('soubor je poskozeny, ci se nejedna o korektni geojson')
            exit(1)
    else:
        print('soubor neexistuje')
        exit(1)
    return data

def build_quadtree(in_points, out_points, bbox, quadrant=0, depth=0, size=50):
    '''
    rekurzivni funkce pro deleni bodu do kvadrantu
    :param in_points: vstupni body
    :param out_points: vystupni body vcetne ID skupiny
    :param bbox: bounding box bodu
    :param quadrant: cislo kvadrantu
    :param depth: hloubka rekurze
    :param size: maximalni velikost skupiny
    :return: out_points
    '''
    if len(in_points) <= size: #konecna podminka rekurze
        graphic(bbox)
        for point in in_points:
            out_points.append(point) #tvorba vystupniho seznamu bodu
        return
    else:
        node = [(bbox[0]+bbox[2])/2,(bbox[1]+bbox[3])/2] #stred bboxu
        quad_1 = [node[0],node[1],bbox[2],bbox[3]] #bbox prvniho kvadrantu
        quad_2 = [node[0],bbox[1],bbox[2],node[1]] #bbox druheho kvadrantu
        quad_3 = [bbox[0],bbox[1],node[0],node[1]] #bbox tretiho kvadrantu
        quad_4 = [bbox[0],node[1],node[0],bbox[3]] #bbox ctvtteho kvadrantu
        P1 = select_points(in_points, quad_1, 1) #body v prvnim kvadrantu
        P2 = select_points(in_points, quad_2, 2)
        P3 = select_points(in_points, quad_3, 3)
        P4 = select_points(in_points, quad_4, 4)
        graphic(bbox)
        build_quadtree(P1,out_points, quad_1, 1, depth + 1, size) #rekuzivni volani funkce pro prvni kvadrant
        build_quadtree(P2,out_points, quad_2, 2, depth + 1, size)
        build_quadtree(P3,out_points, quad_3, 3, depth + 1, size)
        build_quadtree(P4,out_points, quad_4, 4, depth + 1, size)
    return out_points


def select_points(points, boundaries, quad):
    '''
    funkce pro vyber bodu v kvadrantu
    :param points: seznam vstupnich bodu
    :param boundaries: hranice vyberu = bbox
    :param quad: cislo kvadrantu pro tvorbu kodu
    :return: seznam bodu vcetne ID skupiny
    '''
    P = []
    for j in range(len(points)):
        ID = points[j][0]
        x = points[j][1]
        y = points[j][2]
        old_code = points[j][3]
        new_code = old_code + str(quad) #postupna uprava ID skupiny, podle kvadrantu a hloubky rekurze
        if boundaries[0] <= x <= boundaries[2] and boundaries[1] <= y <= boundaries[3]:
            P.append([ID, x, y, new_code])
        else:
            continue
    return P


def graphic(bbox):
    '''
    funkce pro vykresleni aktualniho kvadrantu
    :param bbox: souradnice pro vykresleni
    '''
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


if len(sys.argv) != 3: #osetreni mnozstvi vstupnich argumentu
    print('malo nebo moc argumentu')
    exit(1)
else:
    data = open_geojson(sys.argv[1],'r')

if sys.argv[2][-8:] == ".geojson": #kontrola koncovky vystupniho souboru
    out_file = sys.argv[2]
else:
    print('vystupni soubor neni .geojson')
    exit(1)

group_size = 50 # maximalni velikost skupiny

points = []
ID = 1
for feature in data['features']: #tvorba seznamu vstupnich bodu
    xy = feature['geometry']['coordinates']
    points.append([ID, xy[0], xy[1],""])
    if ID == 1: #hledani bounding boxu vsech bodu
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

turtle.setworldcoordinates(min_x, min_y, max_x, max_y) #uprava zobrazovaciho okna
turtle.speed(0)
turtle.ht()
turtle.tracer(50, 1)

for i in range(len(points)): #vykresleni bodu
    turtle.up()
    turtle.setpos(points[i][1], points[i][2])
    turtle.down()
    turtle.dot(5, "blue")

if len(points) <= group_size: #osetreni podminky, kdyz je velikost skupiny vetsi nebo rovna velikosti vsech bodu
    i = 0
    for feat in data['features']: #prirazeni kodu skupiny vystupnim bodum
        feat['properties']['cluster_id'] = 0
        i += 1

    with open(out_file, 'w') as out: #ulozeni vystupniho souboru
        json.dump(data, out)
else:
    out_points = []
    out_points = build_quadtree(points, out_points, bbox,size=group_size)
    sorted_points = sorted(out_points, key=itemgetter(0)) #serazeni bodu podle jejich ID

    i = 0
    for feat in data['features']:
        feat['properties']['cluster_id'] = sorted_points[i][3] #prirazeni kodu skupiny vystupnim bodum
        i += 1

    with open(out_file, 'w') as out: #ulozeni vystupniho souboru
        json.dump(data, out)


turtle.exitonclick()
