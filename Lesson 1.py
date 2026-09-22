x1, y1, r1, x2, y2, r2 = map(float, input().split())

a = x1 - x2
b = y1 - y2

c2 = a**2 + b**2

if c2 == 0:
    if r1 == r2:
        print(-1)
    else:
        print(0)

elif c2 > (r1 + r2)**2:
    print(0)

elif c2 < (r1 - r2)**2:
    print(0)

elif c2 == (r1 + r2)**2 or c2 == (r1 - r2)**2:
    print(1)

else:
    print(2)