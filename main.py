import pickle
import os
from sys import exit

memory_file = 'memory_data.obj'
FILE = "FILE"
ARCHIVE = "ARCHIVE"

class INode:
    __args = ["name", "_type", "blocks_numbers"]
    name = None
    _type = None
    blocks_numbers = None
    def __init__(self, name = None, _type = None, blocks_numbers = [], from_dict = None):
        if from_dict != None and type(from_dict) == dict:
            for arg in self.__args:
                setattr(self, arg, from_dict[arg])
                
        elif _type == FILE or _type == ARCHIVE:
            self.name = name
            self._type = _type
            self.blocks_numbers = blocks_numbers
    
    def __repr__(self):
        return "{} - {}".format(self.name, self.blocks_numbers)

    def __str__(self):
        _str = "{"
        for arg in self.__args:
            _str += "'{}': '{}', ".format(arg, getattr(self, arg))
        return _str[:-2] + "}"

    def test(self):
        a = str(self)
        print(a)
        b = eval(a)
        print(b)
        for arg in self.__args:
            print(arg, b[arg])
        return a, b

class Memory:
    def __init__(self):     # Kbytes  Mbytes  bits
        self.n_bytes = 128 * 1024 * 1024 #* 8
                            #  Kbytes  bits
        self.block_bytes = 4 * 1024 #* 8
        self.n_blocks = int(self.n_bytes / self.block_bytes)
        self.blocks = [None] * self.n_blocks
        self.inodes = []
        #self.dir_inodes = INode()
    
    def __repr__(self):
        return "{} - {} - {}".format(self.n_bytes, self.block_bytes, self.n_blocks)

    def load_data(self):
        files = os.listdir()
        for f in files:
            f_path = os.path.join(f)
            if(os.path.isfile(f_path) and f_path == memory_file): # verificar se e ficheiro
                arq = open(memory_file, 'rb') 
                temp = pickle.load(arq)
                arq.close()
                self.inodes = temp.inodes
                self.blocks = temp.blocks
                # f_size = os.path.getsize(f_path)
                # f_size = f_size
                # print("{:<20} - {:>10}B - {:>10}KB - {:>10}MB".format(f_path, f_size, f_size/1024, f_size/1024/1024))
    
    def store_data(self):
        arq = open(memory_file, 'wb') 
        pickle.dump(self, arq)
        arq.close()

    def list_files(self, should_print = False):
        _str = ""
        filenames = []
        if len(self.inodes) > 0:
            for inode in self.inodes:
                _str += "{} - ".format(inode.name)
                filenames.append(inode.name)
            _str = _str[:-3]
        if should_print: print("files: {}".format(_str))
        return filenames
    
    def show_file(self, file_name):
        for inode in self.inodes:
            if inode.name == file_name:
                _str = ""
                for block_number in inode.blocks_numbers:
                    _str += self.blocks[block_number]
                print("file: {} - {}".format(inode.name, _str))

    def show_files(self):
        for file in self.inodes:
            self.show_file(file.name)

    def write_in_block(self, block_number, content):
        content = str(content)
        if self.blocks[block_number] == None:
            if len(content) <= self.block_bytes:
                self.blocks[block_number] = content
            else:
                print("conteudo maior que o tamanho do bloco")
                exit(1)
        else:
            print("bloco ocupado")
            exit(1)
    
    def find_empty_block(self):
        list_of_busy_blocks = []
        for inode in self.inodes:
            for block in inode.blocks_numbers:
                if block in list_of_busy_blocks:
                    print("algo inesperado aconteceu")
                    exit(1)
                else:
                    list_of_busy_blocks.append(block)
        for i in range(len(self.blocks)):
            if i not in list_of_busy_blocks:
                return i
        return None

    def make_file(self, name_of_file):
        filenames = self.list_files()
        if name_of_file not in filenames:
            block_number = self.find_empty_block()
            if block_number != None:
                self.blocks[block_number] = ""
                self.inodes.append(INode(name = name_of_file, _type=FILE, blocks_numbers=[block_number]))
            else:
                print("nenhum bloco vazio")
                exit(1)
        else:
            print("arquivo ja existe")
            exit(1)
    
    def remove_file(self, file_name):
        for inode in self.inodes:
            if inode.name == file_name:
                for block_number in inode.blocks_numbers:
                    self.blocks[block_number] = None
                self.inodes.remove(inode)
                return True
        return False
    
    def write_in_file(self, file_name, content):
        content = str(content)
        for inode in self.inodes:
            if inode.name == file_name:
                for block_number in inode.blocks_numbers:
                    self.blocks[block_number] = None #apaga o conteudo prévio do arquivo para sobrescrever os dados
                inode.blocks_numbers = []
                while len(content) > 0:
                    if len(content) > self.block_bytes:
                        _str = content[:self.block_bytes]
                        content = content[self.block_bytes:]
                    else:
                        _str = content
                        content = ""
                    
                    block_number = self.find_empty_block()
                    inode.blocks_numbers.append(block_number)
                    self.blocks[block_number] = _str

    def rename_file(self, old_name, new_name):
        for inode in self.inodes:
            if inode.name == old_name:
                inode.name = new_name
                return
        print("arquivo não existe")
        return False
    
    def copy_file(self, filename, new_filename = None):
        for inode in self.inodes:
            if inode.name == filename:
                if new_filename is None: new_filename = "{} {}".format(inode.name, "copy")
                self.make_file(new_filename)
                _str = ""
                for block_number in inode.blocks_numbers:
                    _str += self.blocks[block_number]
                self.write_in_file(new_filename, _str)
                return True
        print("arquivo não existe")
        return False

def initial_data_for_tests(memory):
    memory.make_file("teste1")
    memory.make_file("teste2")
    memory.make_file("teste3")
    memory.make_file("teste4")
    memory.remove_file("teste3")
    memory.list_files(should_print=True)

# memory = Memory()
# initial_data_for_tests(memory)
# memory.store_data()
# print(memory)

memory = Memory()
memory.load_data()

#entrada = input("informe o conteudo: ")
#memory.write_in_file("teste1", entrada)

memory.list_files(should_print=True)
memory.show_files()

i = INode(name = "lucas", _type = FILE)
a, b = i.test()