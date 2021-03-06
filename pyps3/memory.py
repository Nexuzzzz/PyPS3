# ************************************************************ #
#       Library created by Nexus, on 22 August 2021.           #
# ************************************************************ #
# This program is free software: you can redistribute it and/or#
# modify it under the terms of the GNU General Public License  #
# as published by the Free Software Foundation, either version #
# 3 of the License, or (at your option) any later version.     #
#                                                              #
# This program is distributed in the hope that it will be      #
# usefull , but WITHOUT ANY WARRANTY; without even the implied #
# warrant yof MERCHANTABILITY or FITNESS FOR A PARTICULAR      #
# PURPOSE. See the GNU General Public License for more details.#
#                                                              #
# You should have received a copy of the GNU General Public    #
# License along with this program. If not, see                 #
# http://www.gnu.org/licenses/.                                #
#                                                              #
# (C) 2021-2022 PyPS3 by Nexus                                 #
# (C) 2010-2022 multiMAN/webMAN/sMAN/sLaunch/prepNTFS by DeanK #
#                                                              #
# THE SOFTWARE IS DISTRIBUTED "AS IS". NO WARRANTY OF ANY KIND #
# IS EXPRESSED OR IMPLIED. YOU USE AT YOUR OWN RISK. NEITHER   #
# THE AUTHOR, THE LICENSOR NOR THE AGENTS OF THE LICENSOR WILL #
# BE LIABLE FOR DATA LOSS, DAMAGES, LOSS OF PROFITS OR ANY     #
# OTHER KIND OF LOSS WHILE USING OR MISUSING THIS SOFTWARE OR  #
# ITS COMPONENTS. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT   #
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY  #
# , WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,       #
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR   #
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.                   #
# ************************************************************ #

'''
Submodule for writing/reading/poking the PS3 memory
'''

import requests, re
from pyps3.src.exceptions import *
from pyps3.src.core import Core
from pyps3.src.utils import Utils

class Memory():
    def __init__(self):
        pass
    
    def memWrite(self, process=None, patch_addr=None, hex_value=None) -> bool:
        '''
        Patches a specific address with a hex value
        
        :param process str: The process to write it to
        :param patch_addr str/list: The patch address (or addresses)
        :param hex_value str: The new hex value to patch
        :return bool: True, False
        '''

        if Core.ps3ip == None: raise ConsoleNotFound('Please connect first')
        elif process == None: raise ParamIsNone('Process can\'t be none!')
        elif patch_addr == None: raise ParamIsNone('Patch address can\'t be none!')
        elif hex_value == None: raise ParamIsNone('Hex value can\'t be none!')
        else:
            process = f'0x{process}' if not process.startswith('0x') else process
            hex_value = Utils().clean(hex_value)
            try:

                if type(patch_addr) == list:
                    for addr in patch_addr:
                        req = requests.get(f'http://{Core.ps3ip}/setmem.ps3mapi?proc={process}&addr={Utils().clean(addr)}&val={hex_value}')
                        if req.status_code == 200: continue
                        else: raise InvalidHTTPResponse( f'Got status code {str(req.status_code)} as response, which means "{self.HTTP_RESPONSE_CODES[req.status_code]}".')
                    return True
                else:
                    return Utils().get(f'http://{Core.ps3ip}/setmem.ps3mapi?proc={process}&addr={patch_addr}&val={hex_value}')

            except Exception:
                raise MemWriteException('Failed to write to console memory')
        
    def memWriteMultiple(self, process=None, patch_hex=None) -> bool:
        '''
        Patches a specific address with a hex value
        
        :param process str: The process to write it to
        :param patch_hex list: List with tuples in `(patch_addr, hex_value)` format
        :return bool: True, False
        '''

        if Core.ps3ip == None: raise ConsoleNotFound('Please connect first')
        elif process == None: raise ParamIsNone('Process can\'t be none!')
        elif patch_hex == None: raise ParamIsNone('Patch address can\'t be none!')
        else:
            process = f'0x{process}' if not process.startswith('0x') else process
            try:

                for addr, value in patch_hex:
                    req = requests.get(f'http://{Core.ps3ip}/setmem.ps3mapi?proc={process}&addr={Utils().clean(addr)}&val={Utils().clean(value)}')
                    if req.status_code == 200: continue
                    else: raise InvalidHTTPResponse( f'Got status code {str(req.status_code)} as response, which means "{self.HTTP_RESPONSE_CODES[req.status_code]}".')
                return True

            except Exception:
                raise MemWriteException('Failed to write to console memory')
    
    def memView(self, process=None, read_addr=None, pretty=False) -> str | list:
        '''
        Shows the process memory of the specified read address
        
        :param process str: The process to read from
        :param read_addr str: The patch address to read from
        :param pretty bool: Wether to show it really pretty, or return a raw list
        :return str/list: string if `pretty` has been set to True else list
        '''

        if Core.ps3ip == None: raise ConsoleNotFound('Please connect first')
        elif process == None: raise ParamIsNone('Process can\'t be none!')
        elif read_addr == None: raise ParamIsNone('Read address can\'t be none!')
        else:
            try:
                read_addr = Utils().clean(read_addr)
                process = f'0x{process}' if not process.startswith('0x') else process

                page = requests.get(f'http://{Core.ps3ip}/getmem.ps3mapi?proc={process}&addr={read_addr}&len=256')
                memview = re.findall(r'\<font color=\#ff0\>\<\/font\>\<hr\>(.*?)\<textarea id=\"output\"', page.text)[0].split('<br>') 

                return memview if not pretty \
                    else '\n'.join(memview)

            except Exception:
                raise MemReadException('Failed to read from console memory')
    
    def memRead(self, process=None, read_addr=None) -> str:
        '''
        Reads from a specific address
        
        :param process str: The process to read from
        :param read_addr str: The patch address to read from
        :return str: memory value
        '''

        if Core.ps3ip == None: raise ConsoleNotFound('Please connect first')
        elif process == None: raise ParamIsNone('Process can\'t be none!')
        elif read_addr == None: raise ParamIsNone('Read address can\'t be none!')
        else:
            try:
                process = f'0x{process}' if not process.startswith('0x') else process
                read_addr = Utils().clean(read_addr)
                
                page = requests.get(f'http://{Core.ps3ip}/getmem.ps3mapi?proc={process}&addr={read_addr}&len=256')
                memview = re.findall(r'\<textarea id=\"output\" style=\"display\:none\"\>(.*?)\<\/textarea\>', page.text)
                return memview[0]

            except Exception:
                raise MemReadException('Failed to read from console memory')
    
    def poke(self, address, value, lv=1) -> bool:
        '''
        Pokes into lv1 or lv2 memory

        :param address str: The address to poke
        :param value str: Hex or text value
        :param lv int: The lv memory (1 or 2)
        :return bool: True, False
        '''

        if Core.ps3ip == None: raise ConsoleNotFound('Please connect first')
        elif address == None: raise ParamIsNone('Address can\'t be none!')
        elif value == None: raise ParamIsNone('Value can\'t be none!')
        elif type(lv) != int or not lv in [1,2]: raise InvalidParam('Lv has to be integer, and either 1 or 2!')
        else:
            try:
                address = Utils().clean(address)
                value = Utils().clean(value)
                
                return Utils().get(f'http://{Core.ps3ip}/poke.lv{str(lv)}?{address}={value}')
            except Exception:
                raise PokeException(f'Failed to poke into lv{str(lv)} memory')
    
    def peek(self, address, lv=1, pretty=False) -> str | list:
        '''
        Peeks into lv1 or lv2 memory

        :param address str: The address to peek
        :param lv int: The lv memory (1 or 2)
        :param pretty bool: Wether to show it as a "pretty" string
        :return str/list: Returns the data
        '''

        if Core.ps3ip == None: raise ConsoleNotFound('Please connect first')
        elif address == None: raise ParamIsNone('Address can\'t be none!')
        elif type(lv) != int or not lv in [1,2]: raise InvalidParam('Lv has to be integer, and either 1 or 2!')
        else:
            try:
                address = Utils().clean(address)
                
                page = requests.get(f'http://{Core.ps3ip}/peek.lv{str(lv)}?{address}')
                peeked = re.findall(r'\<pre\>(.*?)\<br\>\<hr\>', page.text)[0].split('<br>')

                return peeked if not pretty \
                    else '\n'.join(peeked)

            except Exception:
                raise PeekException(f'Failed to peek into lv{str(lv)} memory')
    
    def dump(self, dmp_type='full') -> bytes:
        '''
        Dumps lv1, lv2, full, flash or rsx memory. This can take some time, especially for the full and rsx memory!

        :param type str: What to dump (lv1, lv2, full, flash or rsx)
        :return bytes: Data of the dump
        '''

        if Core.ps3ip == None: raise ConsoleNotFound('Please connect first')
        elif not dmp_type.lower() in ['lv1','lv2','full','flash','rsx']: raise InvalidParam('dmp_type has to be lv1, lv2, full or rsx')
        else:
            try:
                
                page = requests.get(f'http://{Core.ps3ip}/dump.ps3?{dmp_type}', timeout=(9999,9999))

                if page.status_code == 503: raise ConsoleIsBusy('Console is busy')
                page.raise_for_status()

                dump_path = re.findall(r'Dumped\: \<a class=\"f\" href=\"\/.*?\/\"\>\/.*?\<\/a\>\/\<a href=\"(.*?)"\>dump_'+dmp_type.lower()+r'\.bin\<\/a\>', page.text)
                if dump_path != None and dump_path != []:
                    path = dump_path[0]

                    data = requests.get(f'http://{Core.ps3ip}{path}', timeout=(9999,9999))
                    data.raise_for_status()

                    return data.content
                else:
                    raise DumpException('Failed to find location of dumped memory file')

            except Exception:
                raise DumpException(f'Failed to dump {dmp_type} memory')