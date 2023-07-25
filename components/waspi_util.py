import arrow

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