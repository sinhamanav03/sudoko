class Sudoko:
    def __init__(self,structure_file):
        # for i in range(9):
        #     row = [0 for j in range(9)]
        #     self.structure.append(row)
        self.blocks= []
        for i in range(9):
            for j in range(9):
                self.blocks.append((i,j))
        with open(structure_file) as f:
            contents = f.read().splitlines()
            self.dimension = 9

        self.structure = []
        self.values = []
        for i in range(self.dimension):
            row = []
            value_row = []
            for j in range(self.dimension):
                try:
                    if contents[i][j] == '_':
                        row.append(True)
                        value_row.append(None)
                    elif int(contents[i][j]) in range(1,10):
                        row.append(False)
                        value_row.append(int(contents[i][j]))                    
                except Exception:
                    print("Something Went Wrong")
    
            self.structure.append(row)
            self.values.append(value_row)


 
        
    def neighbors(self,block):
        """
        The function return all the blocks in sudoko which are either in 
        row,column or block 3x3 sector of the given block
        """
        (a,b) = block
        neigbors = []
        for i in range(9):
            if i != a:
                neigbors.append((i,b))
            if i!=b:
                neigbors.append((a,i))
        x = a - a % 3
        y = b - b % 3
        for i in range(3):
            for j in range(3):
                if x+i !=a and y+j!=b:
                    neigbors.append((x+i,y+j))

        return neigbors


    def generate_arcs(self):
        """
        The function generate all the ars that are present in sudoko
        """
        arcs=[]
        for i in range(9):
            for j in range(9):
                for k in range(9):
                    if k!=j:
                        arcs.append(((i,j),(i,k)))
                    if k!=i:
                        arcs.append(((i,j),(k,j)))
                x = i - i % 3
                y = j - j % 3
                for k in range(3):
                    for l in range(3):
                        if x+k !=i and y+l !=j:
                              arcs.append(((x+k,y+l),(i,j)))
        # print(arcs[:25])
        return arcs
