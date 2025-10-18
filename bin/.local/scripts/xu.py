import lldb
import re


def cmd_xu(debugger, command, result, _dict):
    command = command.strip()
    if not command:
        print("Usage: xu <expr>[<start>..<end>] — indices are by Unicode codepoints")
        return

    raw_addr_expr = command
    start_expr = "0"
    length_expr = None

    match = re.match(r"^(.*?)\[\s*(.*?)\s*\.\.\s*(.*?)\s*\]$", raw_addr_expr)
    if match:
        addr_expr = match.group(1).strip()
        start_str = match.group(2).strip()
        end_str = match.group(3).strip()
        start_expr = start_str if start_str else "0"
        if end_str:
            length_expr = f"({end_str} - ({start_expr}))"
    else:
        addr_expr = raw_addr_expr

    frame = (
        debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame()
    )
    process = frame.GetThread().GetProcess()
    target = debugger.GetSelectedTarget()

    val = frame.EvaluateExpression(addr_expr)
    if not val.IsValid():
        print(f"Invalid expression: {addr_expr}")
        return

    addr, elem_type, max_elems = get_data(val, target)
    if addr is None:
        print(f"Unsupported type for {addr_expr}")
        return
    if addr == 0:
        print(f"Null pointer for {addr_expr}")
        return

    elem_size = elem_type.GetByteSize() if elem_type.IsValid() else 0
    if elem_size == 1:
        encoding = "utf-8"
    elif elem_size == 2:
        encoding = "utf-16-le"
    elif elem_size == 4:
        encoding = "utf-32-le"
    else:
        print("Unknown element size")
        return

    start_val = frame.EvaluateExpression(start_expr)
    if not start_val.IsValid():
        print(f"Invalid start expression: {start_expr}")
        return
    start = start_val.GetValueAsUnsigned()

    end_offset = None
    if length_expr is not None:
        length_val = frame.EvaluateExpression(length_expr)
        if not length_val.IsValid():
            print(f"Invalid length expression: {length_expr}")
            return
        end_offset = length_val.GetValueAsUnsigned()
        if end_offset == 0:
            print("Length evaluated to zero")
            return

    # READ full slice without offset so we can slice by codepoints later
    max_bytes = max_elems * elem_size if max_elems is not None else None

    buffer = bytearray()
    offset = 0
    chunk_size = 1024
    max_read = 1 << 20  # 1MB cap

    while offset < max_read:
        to_read = chunk_size
        if max_bytes is not None:
            remaining = max_bytes - offset
            if remaining <= 0:
                break
            to_read = min(to_read, remaining)

        error = lldb.SBError()
        data = process.ReadMemory(addr + offset, to_read, error)
        if error.Fail() or len(data) == 0:
            break
        if isinstance(data, str):
            data = bytearray(ord(c) for c in data)
        buffer.extend(data)
        offset += len(data)
        if len(data) < to_read:
            break

    # stop at null terminator for any encoding
    null_pos = None
    if encoding == "utf-8":
        try:
            null_pos = buffer.index(0)
        except ValueError:
            pass
    elif encoding == "utf-16-le":
        for i in range(0, len(buffer) - 3, 2):
            # detect *double* null pair (= true end of sentinel)
            if (
                buffer[i] == 0
                and buffer[i + 1] == 0
                and buffer[i + 2] == 0
                and buffer[i + 3] == 0
            ):
                null_pos = i
                break
    elif encoding == "utf-32-le":
        for i in range(0, len(buffer) - 7, 4):
            if all(buffer[i + j] == 0 for j in range(8)):
                null_pos = i
                break

    if null_pos is not None:
        buffer = buffer[:null_pos]

    # decode safely (trim stray nulls at end to prevent “�”)
    while buffer and buffer[-1] == 0:
        buffer.pop()

    try:
        decoded_str = buffer.decode(encoding, errors="replace")
    except Exception:
        decoded_str = repr(buffer)

    # Slice by codepoint indices
    if end_offset is not None:
        decoded_str = decoded_str[start : start + end_offset]
    else:
        decoded_str = decoded_str[start:]

    print(decoded_str)


def get_data(val, target):
    val_type = val.GetType()
    type_name = val_type.GetName() or ""

    # 1. Zig slices (struct layout: ptr + len)
    ptr_val = val.GetChildMemberWithName("ptr")
    len_val = val.GetChildMemberWithName("len")
    if ptr_val.IsValid() and len_val.IsValid():
        ptr_type = ptr_val.GetType()
        if ptr_type.IsPointerType():
            elem_type = ptr_type.GetPointeeType()
            max_elems = len_val.GetValueAsUnsigned()
            addr = ptr_val.GetValueAsUnsigned()
            return addr, elem_type, max_elems

    # 2. Normal arrays
    if val_type.IsArrayType():
        elem_type = val_type.GetArrayElementType()
        max_elems = val_type.GetNumberOfElements()
        arr_addr = val.GetAddress()
        if arr_addr.IsValid():
            addr = arr_addr.GetLoadAddress(target)
            return addr, elem_type, max_elems
        return None, None, None

    # 3. Pointers or pointer-like
    if val_type.IsPointerType():
        pointee_type = val_type.GetPointeeType()
        elem_type = pointee_type
        return val.GetValueAsUnsigned(), elem_type, None

    # 4. Handle Zig synthetic slices (e.g. "[]u16", "[:0]u16", "[:sentinel]T", "[]align(2) u8")
    if (
        type_name.startswith("[]")
        or type_name.startswith("[:")
        or "u8" in type_name
        or "u16" in type_name
        or "u32" in type_name
    ):
        num_children = val.GetNumChildren()
        if num_children > 0:
            first_child = val.GetChildAtIndex(0)
            if first_child.IsValid():
                elem_type = first_child.GetType()
                # The first child's address — start of array
                first_addr = first_child.GetAddress()
                if not first_addr.IsValid():
                    return None, None, None
                addr = first_addr.GetLoadAddress(target)
                return addr, elem_type, num_children
        return None, None, None

    return None, None, None


def __lldb_init_module(debugger, _internal_dict):
    debugger.HandleCommand("command script add -f xu.cmd_xu xu")
    print('The "xu" command has been installed. Usage: xu my_str[0..]')
