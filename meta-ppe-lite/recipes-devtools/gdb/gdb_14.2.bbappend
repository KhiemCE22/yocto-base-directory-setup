# Ép linker không bỏ thư viện và tránh LTO (chỉ cho gdb target)
TARGET_LDFLAGS:remove = "-Wl,--as-needed"
export LD_AS_NEEDED = "0"
TARGET_LDFLAGS:append = " -Wl,--no-as-needed"

INHIBIT_LTO = "1"

# Hỗ trợ resolve phụ thuộc vòng tròn giữa các static archives của GDB
TARGET_LDFLAGS:append = " -Wl,--start-group -Wl,--end-group"

# (Tùy chọn – chỉ dùng nếu link line vẫn chưa “ăn” các cờ trên)
# EXTRA_OEMAKE:append = " LDFLAGS='${LDFLAGS} -Wl,--no-as-needed -Wl,--start-group -Wl,--end-group'"
