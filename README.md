# Dokumentace k úkolu č. 2
Tento program slouží k přiřazení unikátního kódu skupiny bodům, dle jejich polohy, pomocí algoritmu Quadtree

Součástí programu je i vykreslení všech vstupních bodů a následné dělení do skupin

## Vstupy
- absolutní/relativní cesta k geojson souboru obsahující body
- absolutní/relativní cesta k geojson souboru, kam mají být uloženy body včetně jejich unikátního kódu skupiny

## Výstupy
- geojson obsahující vstupní body, včetně jejich unikátního kódu skupiny
- vykreslení všech vstupních bodů, včetně vykreslení výsledných skupin

## Popis funkcí
#### open_geojson(file_name)
- funkce, který má za úkol zkontrolovat zda daný soubor existuje a pokusit se ho otevřít
#### build_quadtree(in_points, out_points, bbox, quadrant=0, size=10)
- funkce, která obstarává vlastní průběh algoritmu quadtree    
- v rámcí této funkce jsou vypočítány rozměry všech 4 kvadrantů
- následně je zavolána funkce, která rozdělí body do jednotlivých kvadrantů
- jako poslední je rekuzivně volána samotná funkce pro body v jednotlivých kvadrantech
- pokud dojde k překročení rekuzivní podmínky (počet bodů v daném kvadrantu je menší než 50):    
    jsou do výstupního seznamu  bodu přiřazeny body v akutálním kvadrantu, včetně jejich unikátního kodu skupiny
- unikátní kód je souslednost čísel kvadrantů, ve kterých se body nacházely v dané hloubce rekuze
- výstupem funkce je výstupní seznam bodů
- součástí této funkce je i volání funkce pro vykreslení aktuálního kvadrantu
#### select_points(points, boundaries, quad)
- funkce, která vybírá body ze vstupního seznamu, které se nachází v prostoru ohraničeném argumentem "boundaries"
- argument "quad" je zde pro tvobu jedinečného kódu skupiny
- výstupem je seznam bodů
#### compute_bbox(data)
- funkce která počítá bounding box ze vstupního otevřeného geojsonu a tvoří seznam bodů, který obsahuje souřadnice a prázdné pole pro ID skupiny
- výstupem je seznam bodů a jejich bounding box
#### def draw_bbox(bbox)
- funkce která vykresluje aktuální kvadrant
#### def draw_points(points)
- funkce pro vykreslení bodů

## Popis vlastního běhu programu
1) otevření vstupního souboru
2) spočítání boundng boxu vstupních bodů a vytvoření seznamu jejich souřadnic
3) vykreslení všech bodů
4) volání funkce pro aplikaci algoritmu quadtree pro pro seznam vstupních bodů
5) setřídění výstupního seznamu této funkce podle ID jednotlivých bodů
6) vytvoření atribtu cluster_id a zapsání ID skupin jednotlivým bodům
7) zkontrolování zda existuje cesta k výstupnímu souboru a zda je možné zapisovat do této složky
8) vytvoření "kopie" vstupního geojsonu, včetně atributu cluster_id
9) test zda je možné výstupní soubor otevřít
