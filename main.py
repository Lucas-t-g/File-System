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

    def current_dir(self):
        _str = "/"
        for inode in self.current_stack_inode:
            _str += inode.name+"/"
        return _str[:-1]
            

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
    
    def show_file(self, _args):
        file_name = _args[0]
        for inode_block in self.current_stack_inode[-1].blocks_numbers:
            aux_inode = INode(from_dict=eval(self.blocks[inode_block]))
            if aux_inode._type == FILE and aux_inode.name == file_name:
                _str = ""
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

    def make_file(self, _args):
        name_of_file = _args[0]
        filenames, foldernames = self.list_files_folders()
        name_of_file = name_of_file.replace(" ", "_")
        if name_of_file not in filenames:
            aux_inode = INode(name = name_of_file, _type=FILE)
            self._store_inode(aux_inode)
        else:
            print("arquivo ja existe")
    
    def remove_file(self, _args):
        file_name = _args[0]
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

    def write_in_file(self, _args):
        file_name = _args[0]
        content = _args[1]
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

    def rename(self, _args):
        old_name = _args[0]
        new_name = _args[1]
        for i, inode_block in enumerate(self.current_stack_inode[-1].blocks_numbers):
            inode = INode(from_dict=eval(self.blocks[inode_block]))
            if (inode._type == FILE or inode._type == FOLDER) and inode.name == old_name:
                inode.name = new_name
                self.blocks[inode_block] = str(inode)
                return True
        print("arquivo não existe")
        return False

    def copy_file(self, _args):
        filename = _args[0]
        new_filename = None if len(_args) == 1 else _args[1]
        # print(new_filename)
        for i, inode_block in enumerate(self.current_stack_inode[-1].blocks_numbers):
            inode = INode(from_dict=eval(self.blocks[inode_block]))
            if inode._type == FILE and inode.name == filename:
                if new_filename is None: new_filename = "{}_{}".format(inode.name, "copy")
                # print(new_filename)
                # show_initial_memory_blocks(self, n=15)
                self.make_file([new_filename])
                _str = ""
                for block_number in inode.blocks_numbers:
                    _str += self.blocks[block_number]
                self.write_in_file([new_filename, _str])
                return True
        print("arquivo não existe")
        return False

    def create_folder(self, _args):
        name = _args[0]
        name = name.replace(" ", "_")
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
    
    def open_folder(self, _args):
        path = _args[0].split("/")
        for folder in path:
            if folder == ".." and len(self.current_stack_inode) > 1:
                self.current_stack_inode.pop()
            else:
                for folder_inode_block in self.current_stack_inode[-1].blocks_numbers:
                    aux_inode = INode(from_dict=eval(self.blocks[folder_inode_block]))
                    if aux_inode._type == FOLDER and aux_inode.name == folder:
                        aux_inode._block = folder_inode_block
                        self.current_stack_inode.append(aux_inode)
                        self._update()

    def delete_folder(self, _args):
        foldername = _args[0]
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
    
    def action_map(self, command, _args):
        # print(command, "--", _args)
        action = {
            "ls" : lambda temp: self.list_files_folders(should_print=True),
            "touch" : lambda temp: self.make_file(_args),
            "rm" : lambda temp: self.remove_file(_args),
            "echo" : lambda temp: self.write_in_file(_args),
            "cat" : lambda temp: self.show_file(_args),
            "cp" : lambda temp: self.copy_file(_args),
            "mv" : lambda temp: self.rename(_args),
            "mkdir" : lambda temp: self.create_folder(_args),
            "rmdir" : lambda temp: self.delete_folder(_args),
            "cd" : lambda temp: self.open_folder(_args),
        }
        try:
            action[command](_args)
            return True
        except:
            print("comando '", command, "' nao reconhecido")
            return False

def initial_data_for_tests(memory):
    memory.make_file(["teste1"])
    memory.make_file(["teste2"])
    memory.make_file(["teste3"])
    memory.make_file(["teste4"])
    memory.remove_file(["teste3"])
    memory.list_files_folders(should_print=True)
    # show_initial_memory_blocks(memory)

def show_initial_memory_blocks(memory, n=10):
    print(">>>>>>>>><<<<<<<<<<")
    for i in range(n):
        print("->", i, memory.blocks[i])

def command_interpreter(command_line):
    space = False
    for i, _char in enumerate(command_line):
        if _char == " ":
            space = i
            break
    if space:
        command = command_line[:space]
        _args = command_line[space+1:]
        if command == "echo":
            count = 0
            index = False
            for i, _char in enumerate(_args):
                if _char == ">":
                    count += 1
                else:
                    count = 0
                if count == 2:
                    index = i
            if index:
                aux1 = _args[:index-1]
                aux2 = _args[index+1:]
                if aux1[-1] == " ": aux1 = aux1[:-1]
                if aux1[-1] == '"': aux1 = aux1[:-1]
                if aux1[0] == '"': aux1 = aux1[1:]
                if aux2[0] == " ": aux2 = aux2[1:]
                _args = [aux2, aux1]
        elif command == "cp" or command == "mv":
            _args = _args.split(" ")
        else:
            _args = [_args]
    else:
        command = command_line
        _args = []
    return command, _args

if __name__ == "__main__":
    memory = Memory()
    memory.load_data()
    command_line = ""
    while True:
        print(memory.current_dir(), end="")
        command_line = input(": ")
        if command_line == "exit":
            break
        command, _args = command_interpreter(command_line)
        memory.action_map(command, _args)
        print()
        memory.store_data()
        # show_initial_memory_blocks(memory)
    

