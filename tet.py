import random


def gen_a(M: int, m: int) -> list:
    n = int(M / m)
    if M % m != 0:
        n += 1

    semen = set()
    for index in range(n):
        out_chunk = list()

        for jndex in range((m - 1) + 1):
            elem = (index + 1) + (jndex * n)

            if elem > M:
                while elem in semen:
                    elem = random.randint(1, M)

            semen.add(elem)
            out_chunk.append(elem)
        yield out_chunk


def gen_norm(M: int, m: int) -> list:
    n = int(M / m)
    if M % m != 0:
        n += 1
    t = set()
    set_all_q = set(range(1, M + 1))
    for _ in range(n):
        diff = (set_all_q - t)
        if len(diff) < m:
            while len(diff) < m:
                diff.add(random.choice(list(set_all_q)))
        l = random.sample(list(diff), m)

        t.update(set(l))

        yield l


if __name__ == '__main__':
    print(list(gen_norm(20, 8)))
