import sys

from sudoko import *

class SudokoCreator:

    def __init__(self,sudoko):
        self.sudoko = sudoko
        self.domains = {}
        self.update_domain(dict())
        
    def update_domain(self,assignment):
        for i in range(self.sudoko.dimension):
            for j in range(self.sudoko.dimension):
                self.domains[i,j] = self.available_domain((i,j),assignment)

    def print(self,assignment=None):
        for i in range(9):
            for j in range(9):
                if not self.sudoko.structure[i][j]:
                    print(self.sudoko.values[i][j],end ="|")
                elif assignment!= None and assignment[i,j]!=None:
                    print(assignment[i,j],end="|")
                else:
                    print("_",end="|")
            print()

    def init_assignment(self):
        assignment = dict()
        for i in range(self.sudoko.dimension):
            for j in range(self.sudoko.dimension):
                if not self.sudoko.structure[i][j]:
                    assignment[i,j] = self.sudoko.values[i][j]
        return assignment 

    def save(self,assignment,file_name):
        from PIL import Image,ImageDraw,ImageFont
        cell_size = 50
        cell_border = 2
        interior_size = cell_size - 2 *cell_border

        img = Image.new(
            "RGBA",
            (self.sudoko.dimension * cell_size,
            self.sudoko.dimension * cell_size),
            "black"
        )

        font = ImageFont.truetype("assets/OpenSans-Regular.ttf",40)
        draw = ImageDraw.Draw(img)

        for i in range(self.sudoko.dimension):
            for j in range(self.sudoko.dimension):
                rect=[
                    (j*cell_size+cell_border,
                    i*cell_size +cell_border),
                    ((j+1)*cell_size+cell_border,
                    (i+1)*cell_size+cell_border)
                ]
                draw.rectangle(rect,fill="white")
                w,h =draw.textsize(str(assignment[i,j]),font=font)
                draw.text(
                    (rect[0][0]+((interior_size-w)/2),
                    rect[0][1]+((interior_size-w)/2)-10),
                    str(assignment[i,j]),fill= "black",font = font
                )

                #draw vertical lines
                draw.line(
                (((j+1)*cell_size+cell_border,
                    (i)*cell_size+cell_border),
                    ((j+1)*cell_size+cell_border,
                    (i+1)*cell_size +cell_border)) 
                ,fill="black",width=5)
                
                #draw horizontal lines
                draw.line(
                (((j)*cell_size+cell_border,
                    (i)*cell_size+cell_border),
                    ((j+1)*cell_size+cell_border,
                    (i)*cell_size +cell_border)) 
                ,fill="black",width=5)


                
        
        img.save(file_name)

    def solve(self):
        return self.backtrack(self.init_assignment())

    def revise(self,block1,block2):
        """
        make block1 arc consistent with block2
        """
        revision = False
        inconsistent_val = []
        for x in self.domains[block1]:
            if not any(x!=y for y in self.domains[block2]):
                inconsistent_val.append(x)
                revision = True
        if revision:
            for x in inconsistent_val:
                self.domains[block1].remove(x)
        
        return revision

    def ac3(self,arcs = None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = self.sudoko.generate_arcs()
        else:
            queue = arcs
        while len(queue)!=0:
            (block1,block2) = queue.pop()
            # print(block1,block2)
            # print(self.revise(block1,block2))
            if self.revise(block1,block2):
                if len(self.domains[block1]) == 0:
                    print(block1)
                    return False
                else:
                    for block in self.sudoko.neighbors(block1):
                        queue.append((block,block1))
        return True

    def assignment_complete(self,assignment):
        for block in self.sudoko.blocks:
            if block not in assignment:
                return False
        return True

    def consistent(self,block,assignment):
        for neighbor in self.sudoko.neighbors(block):
            # print(neighbor,end=" - ")
            if neighbor not in assignment:
                # print("no issue")
                continue
            elif assignment[neighbor] == assignment[block]:
                # print("false")
                return False

        return True        

    def select_unassigned_block(self,assignment):
        unassigned_blocks = []
        for block in self.sudoko.blocks:
            if block not in assignment.keys():
                unassigned_blocks.append(block)
        
        smallest_domain_block = []
        smallest_domain_block.append(unassigned_blocks[0])
        for block in unassigned_blocks:
            if len(self.domains[block]) < len(self.domains[smallest_domain_block[0]]):
                smallest_domain_block.clear()
                smallest_domain_block.append(block) 
            elif len(self.domains[block]) == len(self.domains[smallest_domain_block[0]]):
                smallest_domain_block.append(block)

        if len(smallest_domain_block) == 1:
            return smallest_domain_block[0]

        largest_degree_block = smallest_domain_block[0]

        for block in smallest_domain_block:
            if len(self.sudoko.neighbors(block)) > len(self.sudoko.neighbors(largest_degree_block)):
                largest_degree_block = block

        return largest_degree_block 


    def order_domain_values(self,block,assignment):
        domain = list(self.domains[block])
        val_order = [0 for _ in range(len(self.domains[block]))]
        i = 0
        for val in domain:
            for neigbour in self.sudoko.neighbors(block):
                if neigbour not in assignment and val in self.domains[neigbour]:
                    val_order[i]+=1
            i+=1

        domainx = [i for val,i in sorted(zip(val_order,domain))]

        return domainx

    def available_domain(self,block,assignment):
        domain={i for i in range(1,10)}
        
        if block in assignment:
            return {assignment[block]}

        for neighbor in self.sudoko.neighbors(block):
            if neighbor in assignment:
                if assignment[neighbor] in domain:
                    domain.remove(assignment[neighbor])
        return domain

    def backtrack(self,assignment):
        if self.assignment_complete(assignment):
            return assignment
        self.update_domain(assignment)
        block = self.select_unassigned_block(assignment)
        for val in self.order_domain_values(block,assignment):
            assignment[block] = val
            if self.consistent(block,assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return assignment
            assignment.pop(block)
        return None
        # raise NotImplementedError

def main():
    
    # check usage
    # if len(sys.agrv) != 2:
    #     sys.exit("usage py generate.py structure")
    
    sudoko = Sudoko(sys.argv[1])
    creator = SudokoCreator(sudoko)
    assignemnt = creator.solve()

    if assignemnt is None:
        print('No Solution')
    else:
        creator.print(assignemnt)
        creator.save(assignemnt,sys.argv[2])

if __name__ == "__main__":
    main()



