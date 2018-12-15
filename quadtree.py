import json, turtle, sys, os.path
from operator import itemgetter


def open_geojson(file_name):
    """
    funkce pro otevreni json/geojson
    :param file_name: nazev souboru
    :return: otevreny soubor
    """
    if os.path.isfile(file_name):  # pokud soubor existuje
        try:
            with open(file_name, encoding="utf-8") as in_f:  # zkus otevrit
                open_file = json.load(in_f)
        except Exception as e:
            print(e)
            print('soubor je poskozeny, ci se nejedna o korektni geojson')
            exit(1)
    else:
        print('soubor neexistuje')
        exit(1)
    return open_file


def build_quadtree(in_points, out_points, bbox, quadrant=0, size=10):
    """
    rekurzivni funkce pro deleni bodu do kvadrantu
    :param in_points: vstupni body
    :param out_points: vystupni body vcetne ID skupiny
    :param bbox: bounding box bodu
    :param quadrant: cislo kvadrantu
    :param size: maximalni velikost skupiny
    :return: out_points = seznam bodů včetně jejich unikátního kodu skupiny
    """
    if len(in_points) <= size:  # konecna podminka rekurze
        draw_bbox(bbox)
        for point in in_points:
            out_points.append(point)  # tvorba vystupniho seznamu bodu
        return
    else:
        middle = [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]  # stred bboxu
        quad_1 = [middle[0], middle[1], bbox[2], bbox[3]]  # bbox prvniho kvadrantu
        quad_2 = [middle[0], bbox[1], bbox[2], middle[1]]  # bbox druheho kvadrantu
        quad_3 = [bbox[0], bbox[1], middle[0], middle[1]]  # bbox tretiho kvadrantu
        quad_4 = [bbox[0], middle[1], middle[0], bbox[3]]  # bbox ctvtteho kvadrantu
        P1 = select_points(in_points, quad_1, 1)  # body v prvnim kvadrantu
        P2 = select_points(in_points, quad_2, 2)
        P3 = select_points(in_points, quad_3, 3)
        P4 = select_points(in_points, quad_4, 4)
        draw_bbox(bbox)
        build_quadtree(P1, out_points, quad_1, 1, size)  # rekuzivni volani funkce pro prvni kvadrant
        build_quadtree(P2, out_points, quad_2, 2, size)
        build_quadtree(P3, out_points, quad_3, 3, size)
        build_quadtree(P4, out_points, quad_4, 4, size)
    return out_points


def select_points(points, boundaries, quad):
    """
    funkce pro vyber bodu v kvadrantu
    :param points: seznam vstupnich bodu
    :param boundaries: hranice vyberu = bbox
    :param quad: cislo kvadrantu pro tvorbu kodu
    :return: seznam bodu vcetne ID skupiny
    """
    P = []
    for point in points:
        ID = point[0]
        x = point[1]
        y = point[2]
        old_code = point[3]
        new_code = old_code + str(quad)  # postupna uprava ID skupiny, podle kvadrantu a hloubky rekurze
        if boundaries[0] <= x <= boundaries[2] and boundaries[1] <= y <= boundaries[3]:
            P.append([ID, x, y, new_code])
        else:
            continue
    return P


def compute_bbox(data):
    """
    funkce která počítá rozeměry bounding boxu a zároveň vytváří seznam bodů ze vstupního geojsonu
    :param data: otevřený vstupní geojson
    :return: seznam bodů, rozměry bounding boxu
    """
    points = []
    for i, feature in enumerate(data['features'], 1):  # tvorba seznamu vstupnich bodu
        xy = feature['geometry']['coordinates']
        points.append([i, xy[0], xy[1], ""])
        if i == 1:  # hledani bounding boxu vsech bodu
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
    bbox = [min_x, min_y, max_x, max_y]
    return points, bbox


def draw_bbox(bbox):
    """"
    funkce pro vykresleni aktualniho kvadrantu
    :param bbox: souradnice pro vykresleni
    """
    turtle.speed(0)
    turtle.ht()
    turtle.up()
    turtle.setpos(bbox[0], bbox[1])
    turtle.down()
    turtle.forward(abs(bbox[2] - bbox[0]))
    turtle.left(90)
    turtle.forward(abs(bbox[3] - bbox[1]))
    turtle.left(90)
    turtle.forward(abs(bbox[2] - bbox[0]))
    turtle.left(90)
    turtle.forward(abs(bbox[3] - bbox[1]))
    turtle.left(90)
    turtle.up()


def draw_points(points):
    turtle.setworldcoordinates(bbox[0], bbox[1], bbox[2], bbox[3])  # uprava zobrazovaciho okna
    turtle.speed(0)
    turtle.ht()
    turtle.tracer(50, 1)
    for i in range(len(points)):  # vykresleni bodu
        turtle.up()
        turtle.setpos(points[i][1], points[i][2])
        turtle.down()
        turtle.dot(5, "blue")


if len(sys.argv) != 3:  # osetreni mnozstvi vstupnich argumentu
    print('malo nebo moc argumentu')
    exit(3)
else:
    data = open_geojson(sys.argv[1])

out_file = sys.argv[2]

points, bbox = compute_bbox(data)

draw_points(points)

group_size = 50  # maximalni velikost skupiny

if len(points) <= group_size:  # osetreni podminky, kdyz je velikost skupiny vetsi nebo rovna velikosti vsech bodu
    draw_bbox(bbox)
    for i, value in enumerate(data['features'], 0):
        value['properties']['cluster_id'] = 0
else:
    out_points = []
    out_points = build_quadtree(points, out_points, bbox, size=group_size)
    sorted_points = sorted(out_points, key=itemgetter(0))  # serazeni bodu podle jejich ID
    for i, value in enumerate(data['features'], 0):
        value['properties']['cluster_id'] = sorted_points[i][3]  # prirazeni kodu skupiny vystupnim bodum

dir = os.path.dirname(os.path.abspath(out_file))
if os.access(dir, os.W_OK):
    with open(out_file, 'w') as out:  # ulozeni vystupniho souboru
        json.dump(data, out)
    output = open_geojson(out_file)  # test vystupniho souboru
else:
    print('cesta k vystupnimu souboru neexistuje, nebo neni mozny zapis')

turtle.exitonclick()


