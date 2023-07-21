import time
import serial
import serial.tools.list_ports
from array import array

"""Have a look into this! """
# MAX_PACKET_SIZE = 0xFE
STRUCT_FORMAT_LENGTHS = {'c': 1,
                         'b': 1,
                         'B': 1,
                         '?': 1,
                         'h': 2,
                         'H': 2,
                         'i': 4,
                         'I': 4,
                         'l': 4,
                         'L': 4,
                         'q': 8,
                         'Q': 8,
                         'e': 2,
                         'f': 4,
                         'd': 8}



class GetSerialDevice():

    def find_arduino(port=None):
        """Get the name of the port that is connected to Arduino."""
        if port is None:
            ports = serial.tools.list_ports.comports()
            for p in ports:
                if p.manufacturer is not None and "Arduino" in p.manufacturer:
                    port = p.device
        return port


class SerialTransfer(object):
    def __init__(self, port, baud=115200, restrict_ports=True,
         #debug=True, 
        #byte_format=BYTE_FORMATS['little-endian'], 
        timeout=0.05):
        '''
        Description:
        ------------
        Initialize transfer class and connect to the specified USB device

        :param port: int or str     - port, path the USB device is connected to
        :param baud: int            - baud (bits per sec) the device is configured for
        :param restrict_ports: bool - only allow port selection from auto detected list
        :param byte_format: str     - format for values packed/unpacked via the
                                      struct package as defined by
                                      https://docs.python.org/3/library/struct.html#struct-format-strings
        :param timeout: float       - timeout (in s) to set on pySerial for maximum wait for a read from the OS
                                      default 50ms marries up with DEFAULT_TIMEOUT in SerialTransfer
        :return: void
        '''
        
        self.txBuff = [0 for i in range(MAX_PACKET_SIZE - 1)]
        self.rxBuff = [0 for i in range(MAX_PACKET_SIZE - 1)]

        self.connection = serial.Serial()
        self.connection.port = port
        self.connection.baudrate = baud
        self.connection.timeout = timeout

    def open(self):
        '''
        Description:
        ------------
        Open serial port and connect to device if possible

        :return: bool - True if successful, else False
        '''

        if not self.connection.is_open:
            try:
                self.connection.open()
                return True
            except serial.SerialException as e:
                print(e)
                return False
        return True
    
    def close(self):
        '''
        Description:
        ------------
        Close serial port

        :return: void
        '''
        if self.connection.is_open:
            self.connection.close()
    
    def rx_obj(self, obj_type, start_pos=0, obj_byte_size=0, list_format=None, byte_format=''):
        '''
        Description:
        ------------
        Extract an arbitrary variable's value from the RX buffer starting at
        the specified index. If object_type is list, it is assumed that the
        list to be extracted has homogeneous element types where the common
        element type can neither be list, dict, nor string longer than a
        single char
        
        :param obj_type: type or str    - type of object to extract from the RX buffer or format string as defined 
                                          by https://docs.python.org/3/library/struct.html#format-characters
        :param start_pos: int           - index of TX buffer where the first byte of the value is to be stored in
        :param obj_byte_size: int       - number of bytes making up extracted object
        :param list_format: char        - array.array format char to represent the common list element type as defined
                                          by https://docs.python.org/3/library/array.html#module-array
        :param byte_format: str         - byte order, size and alignment according to
                                          https://docs.python.org/3/library/struct.html#struct-format-strings
        :return unpacked_response: obj  - object extracted from the RX buffer, None if operation failed
        '''

        # Look at the type of ojbect to extract - ojb_type
        if (obj_type == str) or (obj_type == dict):
            buff = bytes(self.rxBuff[start_pos:(start_pos + obj_byte_size)])
            format_str = '%ds' % len(buff)
        
        elif obj_type == float:
            format_str = 'f'
            buff = bytes(self.rxBuff[start_pos:(start_pos + STRUCT_FORMAT_LENGTHS[format_str])])   
        
        elif obj_type == int:
            format_str = 'i'
            buff = bytes(self.rxBuff[start_pos:(start_pos + STRUCT_FORMAT_LENGTHS[format_str])])
        
        elif obj_type == bool:
            format_str = '?'
            buff = bytes(self.rxBuff[start_pos:(start_pos + STRUCT_FORMAT_LENGTHS[format_str])])
        
        elif obj_type == list:
            buff = bytes(self.rxBuff[start_pos:(start_pos + obj_byte_size)])
            if list_format:
                arr = array(list_format, buff)
                return arr.tolist()
            else:
                return None
        
        else:
            return None

        # Look how to unpack ojbect - adjust byte_format
        if byte_format:
            unpacked_response = struct.unpack(byte_format + format_str, buff)[0]
            
        else:
            unpacked_response = struct.unpack(self.byte_format + format_str, buff)[0]
        
        if (obj_type == str) or (obj_type == dict):
            unpacked_response = unpacked_response.decode('utf-8')
        
        if obj_type == dict:
            unpacked_response = json.loads(unpacked_response)
        
        return unpacked_response
        
