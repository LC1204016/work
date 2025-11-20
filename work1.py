def work1(link:dict,names:list) -> None:
    # todo:不考虑拥堵，任意两点间的最快的路径是什么？
    # link[A] = [(B,capacity,speedmax,distance)] 终点 通行能力 限速 距离
    for z, x in enumerate(names):# 起点x 终点y
        for y in names[z + 1:]:
            print(x,y)