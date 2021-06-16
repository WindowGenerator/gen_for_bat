import random


def gen_a(M: int, m: int) -> list:
    n = int(M / m)
    if M % m != 0:
        n += 1
    for index in range(n):
        out_chunk = list()
        for jndex in range((m - 1) + 1):
            elem = (index + 1) + (jndex * n)
            if elem > M:
                elem = random.randint(1, M)
            out_chunk.append(elem)
        yield out_chunk


if __name__ == '__main__':
    print(list(gen_a(10, 5)))
