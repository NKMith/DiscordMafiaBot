class RoleGiver:
    def __init__(self, totalN :int): #innocentN >= mafiaN
        self.totalN = totalN
        self.innocentStackN :int = round(totalN * 0.75)
        self.mafiaStackN :int = totalN - self.innocentStackN
        self.stack = []
        for i in range(self.innocentStackN):
            self.stack.append(True)
        for i in range(self.mafiaStackN):
            self.stack.append(False)

    def giveRandomRole(self):
        print(len(self.stack))
        isInnocent = self.stack.pop()
        if isInnocent:
            return "Innocent"
        else:
            return "Mafia"

    def printInfo(self):
        print(f"Received total: {self.totalN}")
        print(f"Initial Innocents: {self.innocentStackN}")
        print(f"Initial Mafia {self.mafiaStackN}")
        print(f"Roles left: {len(self.stack)}")

