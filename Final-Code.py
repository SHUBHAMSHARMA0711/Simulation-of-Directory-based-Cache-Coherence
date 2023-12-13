import random
import matplotlib.pyplot as plt
updateDirectoryCount = 0
updateDirectoryList = []


def Plot():
    global core0
    global core1
    global core2
    global core3
    global updateDirectoryList
    memLatency = []
    missRate = []
    # plot1

    def calc(miss, hit, memLatency):
        try:
            a = (((miss*100)/(miss+hit))*2)+1
            b = (miss*100)/(miss+hit)
        except:
            a = 0
            b = 100
            pass
        memLatency.append(a)
        missRate.append(b)

    core0Miss = core0.cache.miss
    core0Hit = core0.cache.hit
    calc(core0Miss, core0Hit, memLatency)

    core1Miss = core1.cache.miss
    core1Hit = core1.cache.hit
    calc(core1Miss, core1Hit, memLatency)

    core2Miss = core2.cache.miss
    core2Hit = core2.cache.hit
    calc(core2Miss, core2Hit, memLatency)

    core3Miss = core3.cache.miss
    core3Hit = core3.cache.hit
    calc(core3Miss, core3Hit, memLatency)

    plt.bar(["Core 0", " Core 1", "Core 2", "Core 3"],
            memLatency, color='red', width=0.3)
    plt.xlabel("Cores")
    plt.ylabel("Latency (clock cycles)")
    plt.title("Average memory access latency")
    plt.show()

    plt.bar(["Core 0", " Core 1", "Core 2", "Core 3"], missRate, width=0.3)
    plt.xlabel("Cores")
    plt.ylabel("Miss Rate (%)")
    plt.title("Miss rate of each Core")
    plt.show()

    # plot2
    global updateDirectoryList
    x = []
    for i in range(len(updateDirectoryList)):
        x.append(i)
    plt.plot(x, updateDirectoryList, color='orange')
    plt.ylabel("No. of updates")
    plt.xlabel("Time")
    plt.title("No. of directory updates vs Time")
    plt.show()
    updateDirectoryList.clear()


class Cache:
    Data = []
    Directory = []
    History = []
    myCore = 0
    memory = 0
    miss = 0
    hit = 0

    def __init__(self, core, memory):
        self.Data = ["@" for i in range(4)]
        self.Directory = [["@", "@"] for i in range(4)]
        self.History = [-1 for i in range(4)]
        self.myCore = core
        self.memory = memory
        self.miss = 0
        self.hit = 0

    def clearCore(self):
        self.Data = ["@" for i in range(4)]
        self.Directory = [["@", "@"] for i in range(4)]
        self.History = [-1 for i in range(4)]
        self.miss = 0
        self.hit = 0

    def isBlockPresentInCache(self, address):
        address = int(address)
        if (address % 2 == 0):  # 1st set
            if (self.Directory[0][1] == address):
                return 0

            elif (self.Directory[1][1] == address):
                return 1

            else:
                return -1

        else:  # 2nd set
            if (self.Directory[2][1] == address):
                return 2

            elif (self.Directory[3][1] == address):
                return 3

            else:
                return -1

    def placeBlockInCache(self, state, address, flag):
        address = int(address)
        block = self.isBlockPresentInCache(address)
        if (flag and block == -1):
            self.miss += 1

        if (block != -1):
            self.hit += 1

        if (block != -1):
            self.Directory[block][0] = state
            self.Directory[block][1] = address

            if (state != "10"):
                self.Data[block] = self.memory.Data[int(address)]
                self.History[block] = max(self.History)+1
                self.memory.BitRaise(self.myCore, address)

            if (state == "10"):
                self.memory.BitDown(self.myCore, self.Directory[block][1])
                self.History[block] = -1

        elif (flag):
            # LRU
            blockToBeEvicted = -1
            maxPointer = 1000000

            if (address % 2 == 0):
                if (self.History[0] < maxPointer):
                    blockToBeEvicted = 0
                    maxPointer = self.History[0]

                if (self.History[1] < maxPointer):
                    blockToBeEvicted = 1
                    maxPointer = self.History[1]

            if (address % 2 == 1):
                if (self.History[2] < maxPointer):
                    blockToBeEvicted = 2
                    maxPointer = self.History[2]

                if (self.History[3] < maxPointer):
                    blockToBeEvicted = 3
                    maxPointer = self.History[3]

            oldAddress = self.Directory[blockToBeEvicted][1]
            self.Directory[blockToBeEvicted][0] = state
            self.Directory[blockToBeEvicted][1] = address

            if (state != "10"):
                self.Data[blockToBeEvicted] = self.memory.Data[int(address)]
                self.History[blockToBeEvicted] = max(self.History)+1
                self.memory.BitRaise(self.myCore, address)
                self.memory.BitDown(self.myCore, oldAddress)

            if (state == "10"):
                self.memory.BitDown(self.myCore, oldAddress)
                self.History[blockToBeEvicted] = -1


class Core:
    cache = 0
    executeTransaction = 0
    memory = 0
    coreNum = 0

    def __init__(self, coreNum, memory):
        self.cache = Cache(coreNum, memory)
        self.memory = memory
        self.coreNum = coreNum
        self.executeTransaction = ExecuteTransaction(
            self.cache, coreNum, memory)

    def execute(self, lines):
        self.executeTransaction.handleRequest(lines)

    def intToBinary(num):
        return '0' * (10 - len(str(bin(num)))) + str(bin(num))[2:]


class Memory:
    Data = []
    memory_Directory = 0

    def __init__(self):
        self.Data = ["00000000" for i in range(64)]
        self.memory_Directory = [["10", "@@", "0000"] for i in range(64)]

    def clearMem(self):
        self.Data = ["00000000" for i in range(64)]
        self.memory_Directory = [["10", "@@", "0000"] for i in range(64)]

    def UpdateDirectory(self, core, address, state, makeOwner):
        global updateDirectoryCount
        updateDirectoryCount += 1
        address = int(address)

        if (core == 0):
            self.memory_Directory[address][0] = state
            if (makeOwner == True):
                self.memory_Directory[address][1] = "00"

        if (core == 1):
            self.memory_Directory[address][0] = state
            if (makeOwner == True):
                self.memory_Directory[address][1] = "01"

        if (core == 2):
            self.memory_Directory[address][0] = state
            if (makeOwner == True):
                self.memory_Directory[address][1] = "10"

        if (core == 3):
            self.memory_Directory[address][0] = state
            if (makeOwner == True):
                self.memory_Directory[address][1] = "11"

    def BitRaise(self, core, address):
        try:
            address = int(address)
        except:
            return

        global updateDirectoryCount
        updateDirectoryCount += 1

        if (core == 0):
            char_list = [x for x in self.memory_Directory[address][2]]
            char_list[-1] = "1"
            my_string = ''.join(char_list)
            self.memory_Directory[address][2] = my_string

        if (core == 1):
            char_list = [x for x in self.memory_Directory[address][2]]
            char_list[-2] = "1"
            my_string = ''.join(char_list)
            self.memory_Directory[address][2] = my_string

        if (core == 2):
            char_list = [x for x in self.memory_Directory[address][2]]
            char_list[-3] = "1"
            my_string = ''.join(char_list)
            self.memory_Directory[address][2] = my_string

        if (core == 3):
            char_list = [x for x in self.memory_Directory[address][2]]
            char_list[0] = "1"
            my_string = ''.join(char_list)
            self.memory_Directory[address][2] = my_string

    def BitDown(self, core, address):
        try:
            address = int(address)
        except:
            return

        global updateDirectoryCount
        updateDirectoryCount += 1

        if (core == 0):
            char_list = [x for x in self.memory_Directory[address][2]]
            char_list[-1] = "0"
            my_string = ''.join(char_list)
            self.memory_Directory[address][2] = my_string

        if (core == 1):

            char_list = [x for x in self.memory_Directory[address][2]]
            char_list[-2] = "0"
            my_string = ''.join(char_list)
            self.memory_Directory[address][2] = my_string

        if (core == 2):
            char_list = [x for x in self.memory_Directory[address][2]]
            char_list[-3] = "0"
            my_string = ''.join(char_list)
            self.memory_Directory[address][2] = my_string

        if (core == 3):
            char_list = [x for x in self.memory_Directory[address][2]]
            char_list[0] = "0"
            my_string = ''.join(char_list)
            self.memory_Directory[address][2] = my_string


class ExecuteInstruction:
    cache = 0
    core = 0
    memory = 0
    global core0
    global core1
    global core2
    global core3

    def __init__(self, cache, coreNum, memory):
        self.cache = cache
        self.core = str(coreNum)
        self.memory = memory
        self.core0 = core0
        self.core1 = core1
        self.core2 = core2
        self.core3 = core3

    def LS(self, address):
        address = int(address)

        if (self.core == '0'):
            char_list = [x for x in self.memory.memory_Directory[address][2]]
            anyOwner = False

            for i in range(0, len(char_list)):
                if (char_list[i] == "1"):
                    anyOwner = True

            if (anyOwner == True):
                self.cache.placeBlockInCache("01", str(address), 1)
                self.memory.UpdateDirectory(0, address, "01", False)

            else:
                self.cache.placeBlockInCache("11", str(address), 1)
                self.memory.UpdateDirectory(0, address, "11", True)

        elif (self.core == '1'):
            char_list = [x for x in self.memory.memory_Directory[address][2]]
            anyOwner = False

            for i in range(0, len(char_list)):
                if (char_list[i] == "1"):
                    anyOwner = True

            if (anyOwner == True):
                self.cache.placeBlockInCache("01", str(address), 1)
                self.memory.UpdateDirectory(1, address, "01", False)

            else:
                self.cache.placeBlockInCache("11", str(address), 1)
                self.memory.UpdateDirectory(1, address, "11", True)

        elif (self.core == '2'):
            char_list = [x for x in self.memory.memory_Directory[address][2]]
            anyOwner = False

            for i in range(0, len(char_list)):
                if (char_list[i] == "1"):
                    anyOwner = True

            if (anyOwner == True):
                self.cache.placeBlockInCache("01", str(address), 1)
                self.memory.UpdateDirectory(2, address, "01", False)

            else:
                self.cache.placeBlockInCache("11", str(address), 1)
                self.memory.UpdateDirectory(2, address, "11", True)

        elif (self.core == '3'):
            char_list = [x for x in self.memory.memory_Directory[address][2]]
            anyOwner = False

            for i in range(0, len(char_list)):
                if (char_list[i] == "1"):
                    anyOwner = True

            if (anyOwner == True):
                self.cache.placeBlockInCache("01", str(address), 1)
                self.memory.UpdateDirectory(3, address, "01", False)

            else:
                self.cache.placeBlockInCache("11", str(address), 1)
                self.memory.UpdateDirectory(3, address, "11", True)

    def LM(self, address):

        address = int(address)

        if (self.core == '0'):
            self.cache.placeBlockInCache("00", str(address), 1)
            core1.cache.placeBlockInCache("10", str(address), 0)
            core2.cache.placeBlockInCache("10", str(address), 0)
            core3.cache.placeBlockInCache("10", str(address), 0)
            self.memory.UpdateDirectory(0, address, "00", True)

        elif (self.core == '1'):
            core0.cache.placeBlockInCache("10", str(address), 0)
            self.cache.placeBlockInCache("00", str(address), 1)
            core2.cache.placeBlockInCache("10", str(address), 0)
            core3.cache.placeBlockInCache("10", str(address), 0)
            self.memory.UpdateDirectory(1, address, "00", True)

        elif (self.core == '2'):
            core0.cache.placeBlockInCache("10", str(address), 0)
            core1.cache.placeBlockInCache("10", str(address), 0)
            self.cache.placeBlockInCache("00", str(address), 1)
            core3.cache.placeBlockInCache("10", str(address), 0)
            self.memory.UpdateDirectory(2, address, "00", True)

        elif (self.core == '3'):
            core0.cache.placeBlockInCache("10", str(address), 0)
            core1.cache.placeBlockInCache("10", str(address), 0)
            core2.cache.placeBlockInCache("10", str(address), 0)
            self.cache.placeBlockInCache("00", str(address), 1)
            self.memory.UpdateDirectory(3, address, "00", True)

    def IN(self, address):

        if self.core == '0':
            self.cache.placeBlockInCache("10", address, 0)
            self.memory.UpdateDirectory(0, address, "10", False)

        elif (self.core == '1'):
            self.cache.placeBlockInCache("10", address, 0)
            self.memory.UpdateDirectory(1, address, "10", False)

        elif (self.core == '2'):
            self.cache.placeBlockInCache("10", address, 0)
            self.memory.UpdateDirectory(2, address, "10", False)

        elif (self.core == '3'):
            self.cache.placeBlockInCache("10", address, 0)
            self.memory.UpdateDirectory(3, address, "10", False)

    def ADD(self, address, immediate):

        self.memory.Data[int(address)] = Core.intToBinary(
            int(self.memory.Data[int(address)], 2) + immediate)
        self.LM(address)


class ExecuteTransaction:
    executeIntstruction = 0
    coreNum = 0
    cache = 0
    memory = 0

    def __init__(self, cache, coreNum, memory):
        self.coreNum = coreNum
        self.cache = cache
        self.memory = memory
        self.executeInstruction = ExecuteInstruction(cache, coreNum, memory)

    def handleRequest(self, lines):
        if (lines.split()[1] == 'LS'):
            self.GetShared(lines)

        elif (lines.split()[1] == 'LM' or lines.split()[1] == 'ADD'):
            self.GetModified(lines)

        else:
            self.Put(lines)

    def GetShared(self, lines):
        self.executeInstruction.LS(lines.split()[2])

    def GetModified(self, lines):
        if (lines.split()[1] == 'LM'):
            self.executeInstruction.LM(lines.split()[2])

        else:
            self.executeInstruction.ADD(lines.split()
                                        [2], int(lines.split()[3][1::]))

    def Put(self, lines):
        self.executeInstruction.IN(lines.split()[2])


class CPU:
    test_case_start = False
    core0 = 0
    core1 = 0
    core2 = 0
    core3 = 0
    memory = 0

    def __init__(self, core0, core1, core2, core3, memory):
        self.core0 = core0
        self.core1 = core1
        self.core2 = core2
        self.core3 = core3
        self.memory = memory

        with open("input.txt") as file:
            j = 0
            test_no = 1
            for line in file:
                line = line.strip()

                if line.startswith("# Test"):
                    if (test_no > 1):
                        self.print_memory_directory_state(test_no)
                        Plot()

                    j = 0
                    test_no += 1
                    memory.clearMem()
                    core0.cache.clearCore()
                    core1.cache.clearCore()
                    core2.cache.clearCore()
                    core3.cache.clearCore()
                    self.memory = memory
                    self.core0 = core0
                    self.core1 = core1
                    self.core2 = core2
                    self.core3 = core3

                else:
                    if (line.split()[0] == "0"):
                        core0.execute(line)

                    elif (line.split()[0] == "1"):
                        core1.execute(line)

                    elif (line.split()[0] == "2"):
                        core2.execute(line)

                    elif (line.split()[0] == "3"):
                        core3.execute(line)

                    self.generate_log(j, test_no, line)
                    j += 1

            self.print_memory_directory_state(test_no)
            Plot()

    def print_memory_directory_state(self, test_no):
        print("\nTest Case: " + str(test_no-1) + "\n")
        print("+-----------+-------+-------+--------------+--------------+")
        print("|{:^11s}|{:^7s}|{:^7s}|{:^14s}|{:^14s}|".format(
            "Line No.", "State", "Owner", "Sharers List", "Memory Block"))
        print("+-----------+-------+-------+--------------+--------------+")

        for i in range(0, 64):
            print(
                f"|{i:^11d}|{self.memory.memory_Directory[i][0]:^7s}|{self.memory.memory_Directory[i][1]:^7s}|{self.memory.memory_Directory[i][2]:^14s}|{self.memory.Data[i]:^14s}|")

        print("+-----------+-------+-------+--------------+--------------+")

    def generate_log(self, i, test_no, line):
        global updateDirectoryCount
        global updateDirectoryList
        updateDirectoryList.append(updateDirectoryCount)
        updateDirectoryCount = 0

        with open("log.txt",  "a+") as file:
            seprator = "+-----------+-------+-------+--------------+"
            header = "|{:^11s}|{:^7s}|{:^7s}|{:^14s}|".format(
                "Line No.", "State", "Address", "Data")

            file.write("\nTest Case: " + str(test_no-1) + "\n")
            file.write("Instruction: " + str(i) + "\n")
            file.write("Core Request: " + str(line.split()[0]) + "\n")

            if (line.split()[1] == "LS"):
                file.write("Generated Transaction: GetShared" + "\n")
                file.write("Response: Execute LS")

            elif (line.split()[1] == "LM"):
                file.write("Generated Transaction: GetModified and Put" + "\n")
                file.write("Response: Execute LM for core request" + "\n")
                file.write("Response: Execute IN for rest of the core" + "\n")

            elif (line.split()[1] == "IN"):
                file.write("Generated Transaction: Put" + "\n")
                file.write("Response: Execute IN" + "\n")

            else:
                file.write("Generated Transaction: GetModified and Put" + "\n")
                file.write("Response: Execute ADD for core request" + "\n")
                file.write("Response: Execute IN for rest of the core" + "\n")

            file.write("\nCore 0\n")
            file.write(seprator + "\n")
            file.write(header + "\n")
            file.write(seprator + "\n")

            for i in range(4):
                file.write(
                    f"|{i:^11d}|{core0.cache.Directory[i][0]:^7s}|{str(core0.cache.Directory[i][1]):^7s}|{core0.cache.Data[i]:^14s}|\n")

            file.write(seprator + "\n")
            file.write("\nCore 1\n")
            file.write(seprator + "\n")
            file.write(header + "\n")
            file.write(seprator + "\n")

            for i in range(4):
                file.write(
                    f"|{i:^11d}|{core1.cache.Directory[i][0]:^7s}|{str(core1.cache.Directory[i][1]):^7s}|{core1.cache.Data[i]:^14s}|\n")

            file.write(seprator + "\n")
            file.write("\nCore 2\n")
            file.write(seprator + "\n")
            file.write(header + "\n")
            file.write(seprator + "\n")

            for i in range(4):
                file.write(
                    f"|{i:^11d}|{core2.cache.Directory[i][0]:^7s}|{str(core2.cache.Directory[i][1]):^7s}|{core2.cache.Data[i]:^14s}|\n")

            file.write(seprator + "\n")
            file.write("\nCore 3\n")
            file.write(seprator + "\n")
            file.write(header + "\n")
            file.write(seprator + "\n")

            for i in range(4):
                file.write(
                    f"|{i:^11d}|{core3.cache.Directory[i][0]:^7s}|{str(core3.cache.Directory[i][1]):^7s}|{core3.cache.Data[i]:^14s}|\n")

            file.write(seprator + "\n")


core0 = 0
core1 = 0
core2 = 0
core3 = 0

memory = Memory()
core0 = Core(0, memory)
core1 = Core(1, memory)
core2 = Core(2, memory)
core3 = Core(3, memory)
cpu = CPU(core0, core1, core2, core3, memory)
