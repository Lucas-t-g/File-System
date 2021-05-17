basta executar com:
   python3 main.py

o arquivo onde é salvo os dados referente ao sistema
de arquivos se chama "memory_data.obj", caso ele seja deletado 
os dados do sistema de arquivos se perderao.
O arquivo precisa estar no memso direório de main.py

comandos aceitos:
   - 'exit' termina o programa;
   - 'ls' lista os arquivos e pastas no diretório atual

   Operações sobre arquivos:
      - Criar arquivo (touch arquivo)
      - Remover arquivo (rm arquivo)
      - Escrever no arquivo (echo "conteudo legal" >> arquivo)
      - Ler arquivo (cat arquivo)
      - Copiar arquivo (cp arquivo1 arquivo2)
         + caso nao passe o segundo nome de arquivo será
            criado um arquivo "arquivo1_copy"
      - Renomear arquivo (mv arquivo1 arquivo2)

   Operações sobre diretórios:
      - Criar diretório (mkdir diretorio)
      - Remover diretório (rmdir diretorio) - só funciona se diretório estiver vazio
      - Trocar de diretório (cd diretorio)
         + pode utilizar "/" entre o nome das pastas para especificar um caminho
         +sequencia de dois pontos ( ".." ) indica pra sair do diretório atual
      - Renomear diretorio (mv diretorio1 diretorio2)

Obs: pastas e arquivos nao podem ter espaços nos nomes
   se tentar criar uma pasta ou arquivo com os comandos mkdir e touchs
   com espaços em seus nomes, os espaços seram substituidos por "_"
   (isso funciona apenas com estes comandos)
