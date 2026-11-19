import random

class Orderable:
    def __lt__(self, other: "Orderable") -> bool:
        raise NotImplementedError

    def __gt__(self, other: "Orderable") -> bool:
        raise NotImplementedError

    def __eq__(self, other: "Orderable") -> bool:
        raise NotImplementedError

# Heap
class Heap[T]:
    def __init__(self):
        self.data = []

    def push(self, value: T) -> None:
        self.data.append(value)
        i = len(self.data)-1
        while i>0:
            p=(i-1)//2
            if self.data[i] < self.data[p]:
                self.data[i], self.data[p] = self.data[p], self.data[i]
                i = p
            else:
                break

    @property
    def min(self) -> T:
        return self.data[0]

    def pop(self) -> T:
        assert self.data, "Empty heap"
        if len(self)==1:
            return self.data.pop()
        min = self.data[0]
        self.data[0]=self.data.pop()
        i=0
        while True:
            c1 = (2*i)+1 # left child
            c2 = (2*i)+2 # right child

            if c1 >= len(self.data):
                break
            if c2 >= len(self.data):
                cm = c1 # minimum child
            else:
                if self.data[c1] < self.data[c2]:
                    cm = c1
                else:
                    cm = c2

            if self.data[i] > self.data[cm]:
                self.data[i], self.data[cm] = self.data[cm], self.data[i]
                i = cm
            else:
                break
        return min

    def __str__(self) -> str:
        return str(self.data)

    def __len__(self) -> int:
        return len(self.data)



if __name__ == "__main__":
    heap=Heap()
    # heap.push(8)
    # heap.push(7)
    # heap.push(1)
    # heap.push(5)
    # heap.push(2)
    # print(heap)
    # print(len(heap))
    # while True:
    #     print(heap.pop())

    for i in range(1,100):
        random_value = random.randint(1,1000)
        heap.push(random_value)

    while(heap):
        print(heap.pop())
