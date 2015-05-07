# Linguistic steganography
## Overview
Steganography tool, that can embed secret message to raw text on the russian language
##Requirements
This tool is written using Python2.7
The necessary libraries are BeautifulSoup4 and pymorphy
##Example
The pack has some texts with news from lenta.ru for building table of synonyms  
To embed info first of all, you need to build table using command:  
```python main.py build_table```  
After you can embed random message.  
```python main.py embed```  
And extract it back
python main.py extract
##Help
###usage: 
```python main.py [-h] [-t texts-for-synonyms] [-s synonym-table-file] 
[-p pymorphy-file] [-c container] [-e outpute file] [-test] [-secret secret] 
action```

###Optional arguments:  
|Argument | Description |
| ------------- | ------------- |
|  action|embed, score, extract, build_table  
|-h, --help | show this help message and exit |
|-t texts-for-synonyms | change texts-for-synonyms file (default data/texts.json)  |
|-s synonym-table-file | change synonym_table file (default table.json)|
|-p pymorphy-file | change pymorphy file file (default data/ru.sqlite-json)|
|-c container | Container file secret (default: data/container.txt  |
|  -e outpute file | Container file secret (default: embeded.txt  |
|-test | Enable test mode - replaced word will be UPPERCASE |
|-secret secret | specify secret (default: None, will be generated |


