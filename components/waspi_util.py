import arrow

def get_value_str(link, idx, size):
	data = link.rx_obj(str, obj_byte_size=size, start_pos=idx)
	idx += size
	return (idx, data)

def get_value_int(link, idx, size, fmt, fn):
	data = link.rx_obj(int, obj_byte_size=size, byte_format=fmt, start_pos=idx)
	idx += size
	if fn:
		return (idx, fn(data))
	return (idx, data)

def get_float(link, idx, fn = None):
	size = 4
	data = link.rx_obj(float, obj_byte_size=size, start_pos=idx)
	idx += size
	if fn:
		return (idx, fn(data))
	return (idx, data)

def get_uint16_t(link, start_pos, fn = None):
	return get_value_int(link, start_pos, 2, '<H', fn)

def get_int16_t(link, start_pos, fn = None):
	return get_value_int(link, start_pos, 2, '<h', fn)

def get_uint32_t(link, start_pos, fn = None):
	return get_value_int(link, start_pos, 4, '<I', fn)