L = [78,97,116, 105, 111, 110, 97, 108, 32, 73, 110]
L.reverse()

V = 0
for i in range(len(L)):
    V+= L[i]*(65536**i)

print(V)
