import math
for _ in range(int(input())):
    n,k=map(int,input().split())

    x=int(math.ceil(n/10))
    x=x*10
    if n+k<x:
        print(n+k)
    else:
      x=x-n
      y=k-x
      y=str(y)
      y=y[len(y)-1]
      n=str(n)
      print(n[:len(n)-1]+y)