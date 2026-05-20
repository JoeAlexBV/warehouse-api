def solution(arr1: [int]) -> [int]:
    for i, n in enumerate(arr1):
        if arr1[i] == 0:
            pass
        try:
            if arr1[i] == arr1[i+1]:
                arr1 = arr1.pop(i+1)
                i=i-1
                print(arr1)
            else:
                arr1[i], arr1[i+1] = lcm(arr1[i], arr1[i+1])
        except IndexError:
            pass
    res = arr1.remove(0)
    print(res)
    return res

def lcm(x,y):
    i = 1
    z = 1
    if y > x:
        while z % y != 0:
            i+=1
            z= x*i
    else:
        while z % x != 0:
            i+=1
            z= y*i

    print(z)

    if z == x*y:
        return x,y
    else:
        return z,0


print(solution([6, 4, 3, 2, 7, 6, 2]))