import pickle
import os
from sys import exit

memory_file = 'memory_data.obj'
FILE = "FILE"
FOLDER = "FOLDER"
ROOT_BLOCK = 0

class INode:
    __attr = ["name", "_type", "blocks_numbers", "_block"]

    def __init__(self, name = None, _type = None, from_dict = None):
        self.name = None
        self._type = None
        self.blocks_numbers = []
        self._block = None
        if from_dict != None and type(from_dict) == dict:
            for arg in self.__attr:
                setattr(self, arg, from_dict[arg])
            self.blocks_numbers = eval(self.blocks_numbers)
        elif _type == FILE or _type == FOLDER:
            self.name = name
            self._type = _type
    
    def __repr__(self):
        return "{} - {}".format(self.name, self.blocks_numbers)

    def __str__(self):
        _str = "{"
        for attr in self.__attr:
            _str += "'{}': '{}', ".format(attr, getattr(self, attr))
        return _str[:-2] + "}"

class Memory:
    def __init__(self):     # Kbytes  Mbytes  bits
        self.n_bytes = 128 * 1024 * 1024 #* 8
                            #  Kbytes  bits
        self.block_bytes = 4 * 1024 #* 8
        self.n_blocks = int(self.n_bytes / self.block_bytes)
        self.blocks = [None] * self.n_blocks
        # self.inodes = []
        self.current_stack_inode = [INode(name="root", _type=FOLDER)]
        self.blocks[ROOT_BLOCK] = str(self.current_stack_inode[0])
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
                self.blocks = temp.blocks
                self.current_stack_inode = [INode(from_dict=eval(self.blocks[ROOT_BLOCK]))]
                # print("aa:",self.current_stack_inode)
                # exit()
                # f_size = os.path.getsize(f_path)
                # f_size = f_size
                # print("{:<20} - {:>10}B - {:>10}KB - {:>10}MB".format(f_path, f_size, f_size/1024, f_size/1024/1024))
    
    def store_data(self):
        self._update()
        arq = open(memory_file, 'wb') 
        pickle.dump(self, arq)
        arq.close()

    def list_files_folders(self, should_print = False):
        _str_files = ""
        _str_folders = ""
        filenames = []
        foldernames = []
        if len(self.current_stack_inode[-1].blocks_numbers) > 0:
            # print("jj", self.current_stack_inode[-1].blocks_numbers)
            for inode_block in self.current_stack_inode[-1].blocks_numbers:
                # print("gg",inode_block,self.blocks[inode_block])
                inode = INode(from_dict=eval(self.blocks[inode_block]))
                if inode._type == FILE:
                    filenames.append(inode.name)
                    _str_files += "{} - ".format(inode.name)
                elif inode._type == FOLDER:
                    foldernames.append(inode.name)
                    _str_folders += "{} - ".format(inode.name)
            _str_files = _str_files[:-3]
            _str_folders = _str_folders[:-3]
        if should_print: print("files  : {}".format(_str_files))
        if should_print: print("folders: {}".format(_str_folders))
        return filenames, foldernames
    
    def show_file(self, file_name):
        for inode_block in self.current_stack_inode[-1].blocks_numbers:
            aux_inode = INode(from_dict=eval(self.blocks[inode_block]))
            if aux_inode._type == FILE and aux_inode.name == file_name:
                for block_number in aux_inode.blocks_numbers:
                    _str += self.blocks[block_number]
                print("file: {} - {}".format(aux_inode.name, _str))
                return True
        print("arquivo nao encontrado")
        return False
    
    def show_files(self):
        for inode_block in self.current_stack_inode[-1].blocks_numbers:
            aux_inode = INode(from_dict=eval(self.blocks[inode_block]))
            if aux_inode._type == FILE:
                print(aux_inode)
                print()

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
        for i in range(1, len(self.blocks)):
            if self.blocks[i] == None:
                return i
        return None

    def make_file(self, name_of_file):
        filenames, foldernames = self.list_files_folders()
        if name_of_file not in filenames:
            aux_inode = INode(name = name_of_file, _type=FILE)
            self._store_inode(aux_inode)
        else:
            print("arquivo ja existe")
    
    def remove_file(self, file_name):
        found = False
        for i, inode_block in enumerate(self.current_stack_inode[-1].blocks_numbers):
            inode = INode(from_dict=eval(self.blocks[inode_block]))
            if inode._type == FILE and inode.name == file_name:
                for block_number in inode.blocks_numbers:
                    self.blocks[block_number] = None
                self.blocks[inode_block] = None
                found = True
                break
        if found:
            self.current_stack_inode[-1].blocks_numbers.pop(i)
            self._update()
        else:
            print("arquivo nao encontrado no diretório atual")
        return found

    def write_in_file(self, file_name, content):
        content = str(content)
        for i, inode_block in enumerate(self.current_stack_inode[-1].blocks_numbers):
            inode = INode(from_dict=eval(self.blocks[inode_block]))
            if inode._type == FILE and inode.name == file_name:
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
                self.blocks[inode_block] = str(inode)
                break

    def rename_file(self, old_name, new_name):
        for i, inode_block in enumerate(self.current_stack_inode[-1].blocks_numbers):
            inode = INode(from_dict=eval(self.blocks[inode_block]))
            if inode._type == FILE and inode.name == old_name:
                inode.name = new_name
                self.blocks[inode_block] = str(inode)
                return True
        print("arquivo não existe")
        return False

    def copy_file(self, filename, new_filename = None):
        for i, inode_block in enumerate(self.current_stack_inode[-1].blocks_numbers):
            inode = INode(from_dict=eval(self.blocks[inode_block]))
            if inode._type == FILE and inode.name == filename:
                if new_filename is None: new_filename = "{} {}".format(inode.name, "copy")
                self.make_file(new_filename)
                _str = ""
                for block_number in inode.blocks_numbers:
                    _str += self.blocks[block_number]
                self.write_in_file(new_filename, _str)
                return True
        print("arquivo não existe")
        return False

    def create_folder(self, name):
        aux_inode = INode(name=name, _type=FOLDER)
        self._store_inode(aux_inode)
    
    def _store_inode(self, inode):
        block_number = self.find_empty_block()
        if block_number != None:
            self.current_stack_inode[-1].blocks_numbers.append(block_number)
            self.blocks[block_number] = str(inode)
            self._update()
    
    def _update(self):
        self.blocks[ROOT_BLOCK] = str(self.current_stack_inode[0])
        if len(self.current_stack_inode) > 1:
            folder_inode_block = self.current_stack_inode[-1]._block
            self.blocks[folder_inode_block] = str(self.current_stack_inode[-1])
    
    def open_folder(self, path):
        path.split("/")
        for folder in path:
            if path == ".." and len(self.current_stack_inode) > 1:
                self.current_stack_inode.pop()
            else:
                for folder_inode_block in self.current_stack_inode[-1].blocks_numbers:
                    aux_inode = INode(from_dict=eval(self.blocks[folder_inode_block]))
                    if aux_inode._type == FOLDER and aux_inode.name == path:
                        aux_inode._block = folder_inode_block
                        self.current_stack_inode.append(aux_inode)
                        self._update()
                        return True
            return False

    def delete_folder(self, foldername):
        found = False
        for i, inode_block in enumerate(self.current_stack_inode[-1].blocks_numbers):
            inode = INode(from_dict=eval(self.blocks[inode_block]))
            if inode._type == FOLDER and inode.name == foldername and len(inode.blocks_numbers) == 0:
                self.blocks[inode_block] = None
                found = True
                break
        if found:
            self.current_stack_inode[-1].blocks_numbers.pop(i)
        else:
            print("arquivo nao encontrado no diretório atual")
        return found
def initial_data_for_tests(memory):
    memory.make_file("teste1")
    memory.make_file("teste2")
    memory.make_file("teste3")
    memory.make_file("teste4")
    memory.remove_file("teste3")
    memory.list_files_folders(should_print=True)
    # show_initial_memory_blocks(memory)

def show_initial_memory_blocks(memory, n=10):
    print(">>>>>>>>><<<<<<<<<<")
    for i in range(n):
        print("->", i, memory.blocks[i])

# memory = Memory()
# initial_data_for_tests(memory)
# entrada = input("informe o conteudo: ")
# memory.write_in_file("teste1", entrada)
# memory.store_data()
# show_initial_memory_blocks(memory)

memory = Memory()
# show_initial_memory_blocks(memory)
memory.load_data()
# show_initial_memory_blocks(memory)
memory.create_folder("documentos")
memory.list_files_folders(should_print=True)
# memory.show_files()
memory.open_folder("documentos")
initial_data_for_tests(memory)
# show_initial_memory_blocks(memory)
print(memory.current_stack_inode)
memory.list_files_folders(should_print=True)
memory.open_folder("..")
print(memory.current_stack_inode)
memory.list_files_folders(should_print=True)
print(memory.current_stack_inode)
print("~~~~~~~~~~~~~~~~~~~~~~~~")

memory.create_folder("jogos")
memory.list_files_folders(should_print=True)
memory.open_folder("jogos")
initial_data_for_tests(memory)
print(memory.current_stack_inode)
print("~~~~~~~~~~~~~~~~~~~~~~~~")

memory.open_folder("..")
print(memory.current_stack_inode)
print("~~~~~~~~~~~~~~~~~~~~~~~~")

memory.create_folder("wallpapers")
memory.open_folder("wallpapers")
initial_data_for_tests(memory)
print(memory.current_stack_inode)
memory.list_files_folders(should_print=True)
print("~~~~~~~~~~~~~~~~~~~~~~~~")

memory.remove_file("teste1")
memory.list_files_folders(should_print=True)
memory.remove_file("teste2")
memory.list_files_folders(should_print=True)
memory.remove_file("teste4")
memory.list_files_folders(should_print=True)
print(memory.current_stack_inode)
memory.open_folder("..")
memory.delete_folder("wallpapers")
print(memory.current_stack_inode)
memory.list_files_folders(should_print=True)
print("~~~~~~~~~~~~~~~~~~~~~~~~")
# show_initial_memory_blocks(memory, n = 20)