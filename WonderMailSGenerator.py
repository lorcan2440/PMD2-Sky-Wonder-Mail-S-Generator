import math
import warnings
import random

from wmdata import *


def numToBits(num: int, outputSize: int):
    '''
    Converts a given decimal to outputSize-bit unsigned binary string.
    '''

    formatStr = '\"{0:0' + str(outputSize) + 'b}\"'
    return eval(r"f'{formatStr}'.format(num)").strip('\"')

def bitsToNum(bits: str):
    '''
    Convert a string of bits to a number.
    '''
    return int(bits, 2)

def getItemName(itemId):
    '''
    Returns the item name for a given item ID.
    '''
    return WMSkyItem.get(itemId, 'Unknown Item')

def getDungeonName(dungeonID):
    '''
    Returns the dungeon name for a given dungeon ID.
    '''
    return WMSkyDungeon.get(dungeonID, 'Unknown')

def getMonName(monId):
    '''
    Returns the monster name for a given monster ID.
    '''
    female = (monId > 600)
    if female:
        monId -= 600
    return WMSkyPoke.get(monId, 'Unknown')

def getTrueMonId(id, femaleChecked: bool):
    id = id % 600
    if id == WMSGenData['NIDORAN_MALE'] or id == WMSGenData['NIDORAN_FEMALE']:
        if femaleChecked:
            return WMSGenData['NIDORAN_FEMALE']
        else:
            return WMSGenData['NIDORAN_MALE']
    maleOnly = id in WMSGenData['maleOnly']
    femaleOnly = id in WMSGenData['femaleOnly']
    if (maleOnly or femaleOnly) and femaleChecked:
        print(f'Prevented {id} from being marked as female')
        return id
    elif femaleChecked:
        return id + 600
    else:
        return id


class WMSParser:

    def __init__(self, printLog: bool = True):

        # Byte-swap patterns
	    # 07 1B 0D 1F 15 1A 06 01 17 1C 09 1E 0A 20 10 21 0F 08 1D 11 14 00 13 16 05 12 0E 04 03 18 02 0B 0C 19
	    # http://www.gamefaqs.com/boards/detail.php?board=955859&topic=51920426&message=571612360
        self.byteSwap = [
		    0x07, 0x1B, 0x0D, 0x1F, 0x15, 0x1A, 0x06, 0x01,
		    0x17, 0x1C, 0x09, 0x1E, 0x0A, 0x20, 0x10, 0x21,
		    0x0F, 0x08, 0x1D, 0x11, 0x14, 0x00, 0x13, 0x16,
		    0x05, 0x12, 0x0E, 0x04, 0x03, 0x18, 0x02, 0x0B,
		    0x0C, 0x19
	    ]

        self.byteSwapEU = [
		    0x0E, 0x04, 0x03, 0x18, 0x09, 0x1E, 0x0A, 0x20,
		    0x10, 0x21, 0x14, 0x00, 0x13, 0x16, 0x05, 0x12,
		    0x06, 0x01, 0x17, 0x1C, 0x07, 0x1B, 0x0D, 0x1F,
		    0x15, 0x1A, 0x02, 0x0B, 0x0C, 0x19, 0x0F, 0x08,
		    0x1D, 0x11
	    ]

        # Each WM byte maps to these bit values
	    # http://www.gamefaqs.com/boards/genmessage.php?board=938931&topic=42726909&page=9
        # http://www.gamefaqs.com/boards/genmessage.php?board=938931&topic=42949038
        self.bitValues = "&67NPR89F0+#STXY45MCHJ-K12=%3Q@W"

        # Encryption data from:
	    # http://docs.google.com/Doc?id=ddpvsk95_17fr7qpmgc
		# Listed vertical: first part of the 2-character hex code range
		# Listed horizontal: second part of the 2-character hex code
		#   0     1     2     3     4     5     6     7     8     9     A     B     C     D     E     F
        self.encryptionData = [
            0x2E, 0x75, 0x3F, 0x99, 0x09, 0x6C, 0xBC, 0x61, 0x7C, 0x2A, 0x96, 0x4A, 0xF4, 0x6D, 0x29, 0xFA, # 00-0F
		    0x90, 0x14, 0x9D, 0x33, 0x6F, 0xCB, 0x49, 0x3C, 0x48, 0x80, 0x7B, 0x46, 0x67, 0x01, 0x17, 0x59, # 10-1F
		    0xB8, 0xFA, 0x70, 0xC0, 0x44, 0x78, 0x48, 0xFB, 0x26, 0x80, 0x81, 0xFC, 0xFD, 0x61, 0x70, 0xC7, # 20-2F
		    0xFE, 0xA8, 0x70, 0x28, 0x6C, 0x9C, 0x07, 0xA4, 0xCB, 0x3F, 0x70, 0xA3, 0x8C, 0xD6, 0xFF, 0xB0, # 30-3F
		    0x7A, 0x3A, 0x35, 0x54, 0xE9, 0x9A, 0x3B, 0x61, 0x16, 0x41, 0xE9, 0xA3, 0x90, 0xA3, 0xE9, 0xEE, # 40-4F
		    0x0E, 0xFA, 0xDC, 0x9B, 0xD6, 0xFB, 0x24, 0xB5, 0x41, 0x9A, 0x20, 0xBA, 0xB3, 0x51, 0x7A, 0x36, # 50-5F
		    0x3E, 0x60, 0x0E, 0x3D, 0x02, 0xB0, 0x34, 0x57, 0x69, 0x81, 0xEB, 0x67, 0xF3, 0xEB, 0x8C, 0x47, # 60-6F
		    0x93, 0xCE, 0x2A, 0xAF, 0x35, 0xF4, 0x74, 0x87, 0x50, 0x2C, 0x39, 0x68, 0xBB, 0x47, 0x1A, 0x02, # 70-7F
		    0xA3, 0x93, 0x64, 0x2E, 0x8C, 0xAD, 0xB1, 0xC4, 0x61, 0x04, 0x5F, 0xBD, 0x59, 0x21, 0x1C, 0xE7, # 80-8F
		    0x0E, 0x29, 0x26, 0x97, 0x70, 0xA9, 0xCD, 0x18, 0xA3, 0x7B, 0x74, 0x70, 0x96, 0xDE, 0xA6, 0x72, # 90-9F
		    0xDD, 0x13, 0x93, 0xAA, 0x90, 0x6C, 0xA7, 0xB5, 0x76, 0x2F, 0xA8, 0x7A, 0xC8, 0x81, 0x06, 0xBB, # A0-AF
		    0x85, 0x75, 0x11, 0x0C, 0xD2, 0xD1, 0xC9, 0xF8, 0x81, 0x70, 0xEE, 0xC8, 0x71, 0x53, 0x3D, 0xAF, # B0-BF
		    0x76, 0xCB, 0x0D, 0xC1, 0x56, 0x28, 0xE8, 0x3C, 0x61, 0x64, 0x4B, 0xB8, 0xEF, 0x3B, 0x41, 0x09, # C0-CF
		    0x72, 0x07, 0x50, 0xAD, 0xF3, 0x2E, 0x5C, 0x43, 0xFF, 0xC3, 0xB3, 0x32, 0x7A, 0x3E, 0x9C, 0xA3, # D0-DF
		    0xC2, 0xAB, 0x10, 0x60, 0x99, 0xFB, 0x08, 0x8A, 0x90, 0x57, 0x8A, 0x7F, 0x61, 0x90, 0x21, 0x88, # E0-EF
		    0x55, 0xE8, 0xFC, 0x4B, 0x0D, 0x4A, 0x7A, 0x48, 0xC9, 0xB0, 0xC7, 0xA6, 0xD0, 0x04, 0x7E, 0x05  # F0-FF]
	    ]

        # Data used when calculating a checksum in Sky
        self.skyChecksumData = [None] * 256
        for i in range(256):
            entry = i
            for j in range(8):
                if bool((entry & 0x01) ^ 0x01):
                    entry = entry >> 1
                else:
                    entry = 0xEDB88320 ^ (entry >> 1)
                self.skyChecksumData[i] = entry

        self.printLog = printLog

    def sanitize(self, wmString):
        '''
        Sanitizes a WonderMail S string by removing all unknown characters.
        '''
        wmString = wmString.upper()
        outString = ''.join([char for char in wmString if char in self.bitValues])

        # check if the length is ok
        if len(outString) != 34:
            raise ValueError(f'Sanitized WMS code is {len(outString)} chars long, should be 34')
        return outString

    def prettyMailString(self, mailString, rows, middleColumnSize):
        '''
        Prettifies a mail string, given the amount of rows and the length of the middle column. Outer column
        width is automagically calculated.
        '''
        mailString = self.sanitize(mailString)
        outerColumnSize = int((len(mailString) - (rows * middleColumnSize)) / (rows * 2))
        prettyString = ''
        stringPtr = 0
        for _ in range(rows):
            if prettyString != '':
                prettyString += "\n"
            prettyString += mailString[stringPtr : stringPtr + outerColumnSize] + " "
            stringPtr += outerColumnSize
            prettyString += mailString[stringPtr : stringPtr + middleColumnSize] + " "
            stringPtr += middleColumnSize
            prettyString += mailString[stringPtr : stringPtr + outerColumnSize]
            stringPtr += outerColumnSize
        return prettyString

    def unscrambleString(self, wmString, swapArray):
        '''
        Unscrambles a scrambled WMS string.
        '''
        swapArray = [a | b for a, b in zip(swapArray, self.byteSwap)]
        outString = ''.join([wmString[source] for source in swapArray])
        return outString

    def scrambleString(self, wmString, swapArray):
        '''
        Scrambles a unscrambled WMS string.
        '''
        swapArray = [a | b for a, b in zip(swapArray, self.byteSwap)]
        outArray = [''] * len(swapArray)
        for i, target in enumerate(swapArray):
            outArray[target] += wmString[i]
        return ''.join(outArray)

    def getEncryptionEntries(self, checksum):
        '''
        Returns the encryption entries for a given checksum.
        '''
        amount = 17
        entries = []
        encPointer = checksum
        backwards = bool((checksum & 0x01) ^ 0x01)

        for _ in range(amount):
            entries.append(self.encryptionData[encPointer])
            if backwards:
                encPointer -= 1
                if encPointer < 0:
                    encPointer = len(self.encryptionData) - 1
            else:
                encPointer += 1
                if encPointer >= len(self.encryptionData):
                    encPointer = 0

        return entries

    def bytesToBits(self, wmIntString):
        '''
        Converts the unscrambled representation of a mail string to an encrypted bitstream.
        '''
        outString = ''
        for i in range(len(wmIntString) - 1, -1, -1):
            curChar = wmIntString[i]
            if curChar in self.bitValues:
                index = self.bitValues.index(curChar)
                outString += numToBits(index, 5)
            else:
                raise ValueError(f'Unknown character {curChar} at position {i}')
        return outString

    def bitsToBytes(self, bitStream):
        '''
        Converts an encrypted bitStream to an unscrambled mail.
        '''
        blocks = int(len(bitStream) / 5)
        outStr = ''
        for i in range(blocks):
            curChars = bitStream[(blocks - i - 1) * 5 : (blocks - i - 1) * 5 + 5]
            num = bitsToNum(curChars)
            if 0 <= num < 32:
                outStr += self.bitValues[num]
            else:
                raise ValueError(f'Could not find {curChars} in the reverse lookup table')
        return outStr

    def getResetByte(self, checksum):
        '''
        Returns the resetByte for a given checksum.
        '''
        checksumByte = checksum % 256
        resetByte = math.floor((checksumByte / 16) + 8 + (checksumByte % 16))
        return resetByte if resetByte < 17 else -1

    def decryptBitStream(self, curBitStream, encrypt=False):
        '''
        Decrypts or encrypts a bitstream according to the encryption data.
        '''
		# This will contain the 8-bit blocks as numbers (0-255), each representing one byte.
		# The checksum byte is NOT included in these blocks.
		# The first block in the array is the last block in the bitstream (we work backwards).
        bitPtr = 0
        blocks = []
        origBlocks = []
        # Checksum data
        checksumByte = 0
        checksumBits = ''
        skyChecksumBits = ''
        # Go 8 bits back from the end. We'll read the next 8 bits as our checksum.
        bitPtr = len(curBitStream) - 8
        checksumBits = curBitStream[bitPtr : bitPtr + 8]
        checksumByte = bitsToNum(checksumBits)
        # The Sky Checksum is 24 bits.
        bitPtr -= 24
        skyChecksumBits = curBitStream[bitPtr : bitPtr + 24]
        fullChecksum = bitsToNum(str(skyChecksumBits) + str(checksumBits))
		# http://www.gamefaqs.com/boards/genmessage.php?board=938931&topic=42949038&page=6
		# "At the moment, I figured out what the game is doing with the other half of the encryption. 
		# Apparently, if you have an even checksum, you go backwards through the encryption bytes.
		# With an odd checksum, you go forwards through the encryption bytes."
        backwards = bool((checksumByte & 0x01) ^ 0x01)
        if self.printLog:
            print(f'Checksum: {checksumByte}, encPtr goes backwards: {backwards}')

		# Parse everything into blocks.
		# Sky: 1 2-bit block + 16 8-bit blocks + 24-bit skyChecksum + 8-bit checksum.
        while bitPtr > 7:
            bitPtr -= 8
            data = bitsToNum(curBitStream[bitPtr : bitPtr + 8])
            blocks.append(data)
            origBlocks.append(data)

        # Handle the 2-bit block at the beginning (should always be 00?)
        twoBitsStart = curBitStream[:2]
        bitPtr -= 2
        # Get our encryption entries.
        entries = self.getEncryptionEntries(checksumByte)
        # Figure out the resetByte.
        resetByte = 255
        resetByte = self.getResetByte(fullChecksum)
        if self.printLog:
            print(f'resetByte used for this code: {resetByte}')

        # Do the decryption.
        tblPtr = 0
        encPtr = 0
        for i in range(len(blocks)):
            if encPtr == resetByte:
                remaining = len(blocks) - i
                if self.printLog:
                    print(f'Resetting at {encPtr}. {remaining} blocks remain for decryption.')
                encPtr = 0
            inputByte = blocks[tblPtr]
            # Add or subtract the number in the encryption entry from it.
            if encrypt:
                result = (inputByte + entries[encPtr]) & 0xFF
            else:
                result = (inputByte - entries[encPtr]) & 0xFF
            if self.printLog:
                print(f'pos {tblPtr}, value {inputByte} ({hex(inputByte)}), encbyte {entries[encPtr]}, result is {result}')
            # Update the data in the block.
            blocks[i] = result
            # Update blockPtr.
            tblPtr += 1
            encPtr += 1

        # String everything together. If we use twoBitsStart, that will be our base point.
        outString = twoBitsStart
		# We start at the end and work backwards; the last encryption block is
        # the first 8 bits in the bitstream. That's just how it works.
        for blockPtr in range(len(blocks) - 1, -1, -1):
            outString += numToBits(blocks[blockPtr], 8)
        # Re-add the checksums to the data.
        outString += skyChecksumBits + checksumBits
        return outString

    def encryptBitStream(self, curBitStream):
        '''
        Encrypts a bitstream according to the encryption data.
        '''
        return self.decryptBitStream(curBitStream, encrypt=True)

    def bitsToStructure(self, bitString):
        '''
        Converts a bit string to our internal structure.
        '''
        bitPtr = 0
        outputStruct = {}
        outputStructBit = {}
        for structPtr in range(len(WMSStruct)):
            structInfo = WMSStruct[structPtr]
            bitData = bitString[bitPtr : bitPtr + structInfo['size']]
            bitPtr += structInfo['size']
            numData = bitsToNum(bitData, 8)
            outputStruct[structInfo['name']] = numData
            outputStructBit[structInfo['name']] = bitData

        # We should be at the end now
        if bitPtr != len(bitString):
            warnings.warn('Not all available data was parsed into struct. '
            f'Final bitPtr is {bitPtr}, length is {len(bitString)}', RuntimeWarning)

        if self.printLog:
            print(f'outStruct: {outputStruct}, bitStruct: {outputStructBit}')
        return outputStruct

    def calculateChecksum(self, bitStream):
        '''
        Calculates the checksum for a given bitStream.
        '''
        if self.printLog:
            print(f'Sky Checksum calculation - bitStream of length {len(bitStream)}')
        if len(bitStream) == 170:
            if self.printLog:
                print('Truncating the 170-long bitStream for you. By golly, I\'m so nice.')
            bitStream = bitStream[2 : 138]
        if len(bitStream) != 136:
            warnings.warn(f'bitStream should be 136 bits long - currently {len(bitStream)}')

        checksum = 0xFFFFFFFF
        data = ''
        for i in range(16, -1, -1):
            bits = bitStream[i * 8 : i * 8 + 8]   
            num = bitsToNum(bits)
            data += chr(num).encode('utf-16', 'surrogatepass').decode('utf-16')
            entry = self.skyChecksumData[(checksum ^ num) & 0xFF]
            checksum = (checksum >> 8) ^ entry

        checksum = checksum ^ 0xFFFFFFFF
        if checksum < 0:
            checksum += 4294967296
        if self.printLog:
            print(f'Generated a Sky checksum of {checksum} ({hex(checksum)})')
        return checksum
        
    def structureToBits(self, inputStruct):
        '''
        Converts an object to an unencrypted bitstream.
        '''
        bitStream = ''
        totalSize = 0
        for i in range(len(WMSStruct)):
            key = WMSStruct[i]
            if key.get('noinclude', False):
                continue
            if key['name'] not in inputStruct:
                raise ValueError(f"The key {key['name']} was not defined in inputStruct {inputStruct}")

            data = inputStruct[key['name']]
            binData = numToBits(data, key['size'])
            bitStream += binData
            totalSize += key['size']

		# For Sky, our "null" byte is 8 bits in length. However, 2 of those bits aren't encrypted.
        # To make it easier on ourselves, we chop those two off here and re-add them later.
        # These will always be zero so it's ok.
        bitStream = bitStream[2:]
        if self.printLog:
            print(f'Generated a {len(bitStream)}-length bitStream: {bitStream}')
        checksum = self.calculateChecksum(bitStream)
        bitStream = "00" + bitStream + numToBits(checksum, 32)
        return bitStream


class WMSGen:
    '''
    Generator for a Wonder Mail S password.

    >>> wm = WMSGen(missionType='Rescue Client', missionSubType=None,
            dungeon='Beach Cave', floor=1, client='Bulbasaur',
            clientGender='Male', target='Bulbasaur', targetGender='Male',
            targetItem=None, rewardType='Item + ??? (Random)', rewardItem=None,
            isEuropean=False, advanced=False, flavorText=None, specialFloor=None,
            printLog=True)
    >>> print(wm.wonderMailPassword)

    See `data.json` for all possible inputs (item names, pokemon etc)
    '''

    def __init__(self, missionType='Rescue Client', missionSubType=None, dungeon='Beach Cave',
            floor=1, client='Bulbasaur', clientGender='Male', target='Bulbasaur',
            targetGender='Male', targetItem=None, rewardType='Item + ??? (Random)',
            rewardItem=None, isEuropean=False, advanced=False, flavorText=None, specialFloor=None, printLog=True):

        # set all user inputs and defaults
        self.missionType = missionType
        self.missionSubType = missionSubType
        self.dungeon = dungeon
        self.floor = floor
        self.client = client
        self.clientGender = clientGender
        self.target = target
        self.targetGender = targetGender
        self.targetItem = targetItem
        self.rewardType = rewardType
        self.rewardItem = rewardItem
        self.isEuropean = isEuropean
        self.advanced = advanced
        self.flavorText = flavorText
        self.specialFloor = specialFloor

        # convert user inputs to integer/boolean data
        clientFemale = (self.clientGender == ' Female')
        targetFemale = (self.targetGender == 'Female')
        typeData, typeNum, subTypeData, subTypeNum = self.getTypeData()
        rewardTypeNum = WMRewardType[rewardType]
        client = typeData.get('forceClient', getTrueMonId(WMSkyPoke[self.client], clientFemale))
        if typeData.get('clientIsTarget', False):
            target = typeData.get('forceTarget', client)
        else:
            target = getTrueMonId(WMSkyPoke[self.target], targetFemale)
        target2 = target if typeData.get('target2', False) else 0

        if typeData.get('noReward', False):
            rewardTypeNum = 1
            rewardNum = 109  # apple
        elif 1 <= rewardTypeNum <= 4:
            rewardNum = WMSkyItem[self.rewardItem]
        elif 5 <= rewardTypeNum <= 6:
            rewardNum = client
        else:
            rewardNum = 109

        if typeData.get('useTargetItem', False):
            targetItemNum = WMSkyItem[self.targetItem]
        else:
            targetItemNum = 109

        dungeonNum = WMSkyDungeon[self.dungeon]
        dungeonNum |= 1
        floor = self.floor if 1 <= self.floor <= 99 else 1

        if self.specialFloor is not None:
            specialFloor = self.specialFloor
        elif typeData.get('specialFloor', False):
            specialFloor = typeData['specialFloor']
        elif typeData.get('specialFloorFromList', False):
            listName = typeData['specialFloorFromList']
            if listName not in WMSGenData['staticLists']:
                raise ValueError(f'Static list {listName} not found.')
            specialFloor = random.choice(typeData['specialFloorFromList'][listName])
        else:
            specialFloor = 0

        struct = {
            'missionType': typeNum,
            'missionSpecial': subTypeNum,
            'nullBits': 0,
            'mailType': 4,
            'restriction': 0,
            'restrictionType': 0,
            'rewardType': rewardTypeNum,
            'reward': rewardNum,
            'targetItem': targetItemNum,
            'client': client,
            'target': target,
            'target2': target2,
            'dungeon': dungeonNum,
            'floor': floor,
            'specialFloor': specialFloor,
        }

        parser = WMSParser(printLog=printLog)

        if self.flavorText is not None:
            struct['flavorText'] = flavorText
            decBitStream = parser.structureToBits(struct)
        else:
            struct['flavorText'] = 300000 if self.advanced else random.randint(300000, 399999)
            decBitStream = parser.structureToBits(struct)
            checksum = bitsToNum(decBitStream[:138])
            resetByte = parser.getResetByte(checksum)
            if printLog:
                print(f'flavorText {flavorText}, checksum {checksum}, reset {resetByte}')

        encBitStream = parser.encryptBitStream(decBitStream)
        bitpacked = parser.bitsToBytes(encBitStream)
        byteSwap = parser.byteSwapEU if self.isEuropean else parser.byteSwap
        scrambled = parser.scrambleString(bitpacked, byteSwap)
        prettified = parser.prettyMailString(scrambled, 2, 7)
        if printLog:
            print(f'enc: {encBitStream}, packed: {bitpacked}, scrambled: {scrambled}, prettified: {prettified}')
        self.wonderMailPassword = prettified
        

    def getTypeData(self) -> tuple[dict, int, dict, int]:
        '''
        Converts the mission type string to data
        '''
        for mission in WMSGenData['missionTypes']:
            if mission['name'] == self.missionType:
                typeData = mission
                typeNum = mission['mainType']
                break
        else:
            return False, False

        if 'subTypes' in typeData:
            for subType in typeData['subTypes']:
                if subType['name'] == self.missionSubType:
                    subTypeNum = subType['specialType']
                    subTypeData = subType
                    break
            else:
                return typeData, typeNum, False, False
        else:
            return typeData, typeNum, False, False
        
        return typeData, typeNum, subTypeData, subTypeNum


    # dict reverse lookups - not used in generator. input = id number, output = string name
    @staticmethod
    def getRewardType(rewardType):
        from _original_data import _WMRewardType
        for key, value in _WMRewardType.items():
            if value == rewardType:
                return key
        else:
            return False

    @staticmethod
    def getMon(pokemonName):
        from _original_data import _WMSkyPoke
        for key, value in _WMSkyPoke.items():
            if value == pokemonName:
                return key
        else:
            return False

    @staticmethod
    def getItem(itemName):
        from _original_data import _WMSkyItem
        for key, value in _WMSkyItem.items():
            if value == itemName:
                return key
        else:
            return False

    @staticmethod
    def getDungeon(dungeonName):
        from _original_data import _WMSkyDungeon
        for key, value in _WMSkyDungeon.items():
            if value == dungeonName:
                return key
        else:
            return False


wm = WMSGen(
    missionType='Rescue client',
    dungeon='Waterfall Cave',
    floor=4,
    client='Squirtle',
    clientGender='Male',
    rewardType='Item + ??? (Random)',
    rewardItem='Lockon Specs',
    advanced=True,
    printLog=False)

print(wm.wonderMailPassword)
